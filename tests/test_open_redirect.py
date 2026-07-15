import contextlib
import socket
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest


DOCUMENT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def php_server():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]

    process = subprocess.Popen(
        ["php", "-S", f"127.0.0.1:{port}", "-t", str(DOCUMENT_ROOT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"

    try:
        for _ in range(50):
            try:
                with urllib.request.urlopen(base_url, timeout=0.1):
                    break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.05)
        else:
            pytest.fail("PHP test server did not become ready")

        yield base_url
    finally:
        process.terminate()
        with contextlib.suppress(subprocess.TimeoutExpired):
            process.wait(timeout=5)


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_redirect(base_url, mode, target):
    encoded_target = urllib.parse.quote(target, safe="")
    url = (
        f"{base_url}/vulnerabilities/open_redirect/source/{mode}.php"
        f"?redirect={encoded_target}"
    )
    opener = urllib.request.build_opener(NoRedirects)
    try:
        response = opener.open(url)
    except urllib.error.HTTPError as error:
        response = error
    return response.status, response.headers.get("Location")


@pytest.mark.parametrize(
    ("mode", "unapproved_target"),
    [
        ("low", "https://evil.example/phish"),
        ("medium", "//evil.example/phish"),
        ("high", "https://evil.example/info.php"),
    ],
)
def test_redirect_handlers_allow_only_approved_local_destinations(
    php_server, mode, unapproved_target
):
    control_status, control_location = request_redirect(
        php_server, mode, "info.php?id=1"
    )
    assert control_status == 302
    assert control_location == "info.php?id=1"

    attack_status, attack_location = request_redirect(
        php_server, mode, unapproved_target
    )
    assert not 300 <= attack_status < 400
    assert attack_location is None
