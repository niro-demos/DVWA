import subprocess
import time
import uuid

import pytest
import requests


@pytest.fixture(scope="module")
def deployed_app():
    image = f"dvwa-deployment-test:{uuid.uuid4().hex}"
    container = f"dvwa-deployment-test-{uuid.uuid4().hex}"
    database = f"dvwa-deployment-db-{uuid.uuid4().hex}"
    network = f"dvwa-deployment-network-{uuid.uuid4().hex}"

    subprocess.run(
        ["docker", "build", "--tag", image, "."],
        check=True,
        text=True,
    )
    subprocess.run(["docker", "network", "create", network], check=True)
    subprocess.run(
        [
            "docker",
            "run",
            "--detach",
            "--name",
            database,
            "--network",
            network,
            "--network-alias",
            "db",
            "--env",
            "MARIADB_ROOT_PASSWORD=dvwa",
            "--env",
            "MARIADB_DATABASE=dvwa",
            "--env",
            "MARIADB_USER=dvwa",
            "--env",
            "MARIADB_PASSWORD=p@ssw0rd",
            "mariadb:10",
        ],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    subprocess.run(
        [
            "docker",
            "run",
            "--detach",
            "--name",
            container,
            "--network",
            network,
            "--env",
            "DB_SERVER=db",
            "--publish",
            "127.0.0.1::80",
            image,
        ],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )

    try:
        port_output = subprocess.run(
            ["docker", "port", container, "80/tcp"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        port = int(port_output.rsplit(":", 1)[1])
        base_url = f"http://127.0.0.1:{port}"

        deadline = time.monotonic() + 30
        while True:
            try:
                response = requests.get(f"{base_url}/login.php", timeout=2)
                if response.status_code == 200 and "Login" in response.text:
                    break
            except (requests.ConnectionError, requests.Timeout):
                pass
            if time.monotonic() >= deadline:
                raise RuntimeError("DVWA container did not become ready")
            time.sleep(0.25)

        yield base_url
    finally:
        subprocess.run(["docker", "rm", "--force", container], check=False)
        subprocess.run(["docker", "rm", "--force", database], check=False)
        subprocess.run(["docker", "network", "rm", network], check=False)
        subprocess.run(["docker", "image", "rm", "--force", image], check=False)


def assert_not_published(base_url, path, sensitive_markers=()):
    response = requests.get(f"{base_url}{path}", timeout=5, allow_redirects=False)
    assert response.status_code in (403, 404), (
        f"{path} is public (HTTP {response.status_code}, {len(response.content)} bytes)"
    )
    for marker in sensitive_markers:
        assert marker not in response.content


def test_public_page_control(deployed_app):
    response = requests.get(f"{deployed_app}/favicon.ico", timeout=5)
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("image/")
    assert len(response.content) > 1000


@pytest.mark.parametrize(
    ("path", "markers"),
    [
        ("/config/config.inc.php.dist", (b"db_password", b"DISABLE_AUTHENTICATION")),
        ("/php.ini", (b"allow_url_fopen", b"allow_url_include")),
        ("/database/sqli.db", (b"SQLite format 3",)),
        ("/database/sqli.db.dist", (b"SQLite format 3",)),
        ("/database/create_sqlite_db.sql", (b"INSERT INTO users",)),
    ],
)
def test_deployment_assets_are_not_public(deployed_app, path, markers):
    assert_not_published(deployed_app, path, markers)


def test_anonymous_instructions_are_not_public(deployed_app):
    response = requests.get(
        f"{deployed_app}/instructions.php", timeout=5, allow_redirects=False
    )
    protected = response.status_code in (302, 303, 307, 308, 401, 403, 404)
    assert protected or (
        "Default username" not in response.text
        and "Default password" not in response.text
    )


def test_include_only_command_handler_is_not_public(deployed_app):
    response = requests.post(
        f"{deployed_app}/vulnerabilities/exec/source/low.php",
        data={"Submit": "Submit", "ip": "badhost"},
        timeout=5,
        allow_redirects=False,
    )
    assert response.status_code in (302, 303, 307, 308, 401, 403, 404)
