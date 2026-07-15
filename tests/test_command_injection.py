import json
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def run_device_ping_handler(security_level, target):
    source = ROOT / "vulnerabilities" / "exec" / "source" / f"{security_level}.php"
    script = f"""
    define('DVWA_WEB_PAGE_TO_ROOT', {json.dumps(str(ROOT) + '/')});
    $_POST = ['Submit' => 'Submit'];
    $_REQUEST = ['ip' => {json.dumps(target)}];
    $html = '';
    include {json.dumps(str(source))};
    echo $html;
    """
    return subprocess.run(
        ["php", "-r", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
        check=True,
    ).stdout


@pytest.mark.parametrize(
    ("security_level", "operator"),
    [("low", ";"), ("medium", "|"), ("high", "|")],
)
def test_device_ping_accepts_ip_but_rejects_shell_syntax(security_level, operator):
    control = run_device_ping_handler(security_level, "127.0.0.1")
    assert "127.0.0.1" in control

    marker = f"DVWA_COMMAND_INJECTION_{security_level.upper()}"
    attack = run_device_ping_handler(
        security_level, f"127.0.0.1{operator}printf {marker}"
    )

    assert marker not in attack
    assert "Invalid IP address" in attack


def unused_tcp_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def post_target(url, target):
    request = urllib.request.Request(
        url,
        data=json.dumps({"target": target}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    try:
        response = urllib.request.urlopen(request, timeout=15)
    except urllib.error.HTTPError as error:
        response = error
    return response.status, json.loads(response.read()), time.monotonic() - started


def test_connectivity_api_accepts_ip_but_rejects_shell_syntax():
    port = unused_tcp_port()
    router = ROOT / "tests" / "fixtures" / "health_connectivity_router.php"
    server = subprocess.Popen(
        ["php", "-S", f"127.0.0.1:{port}", str(router)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    url = f"http://127.0.0.1:{port}/vulnerabilities/api/v2/health/connectivity"
    try:
        for _ in range(50):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1):
                    pass
            except urllib.error.HTTPError:
                break
            except urllib.error.URLError:
                time.sleep(0.05)
        else:
            pytest.fail(f"PHP test server did not start: {server.stderr.read()}")

        control_status, control_body, _ = post_target(url, "127.0.0.1")
        assert control_status == 200
        assert control_body == {"status": "OK"}

        attack_status, attack_body, elapsed = post_target(url, "127.0.0.1; sleep 2")
        assert attack_status == 400
        assert attack_body == {"status": "Invalid target"}
        assert elapsed < 1
    finally:
        server.terminate()
        server.wait(timeout=5)
