"""
Regression tests for view_source.php path traversal and XSS.

Covers two security invariants:
  1. The source-viewing page must not read and display arbitrary files
     from the server filesystem based on user-supplied path parameters.
  2. The source-viewing page must not reflect the user-supplied module
     identifier into HTML or JavaScript without encoding.

These tests drive the running DVWA instance over HTTP. They require the
TARGET_URL environment variable (defaults to http://127.0.0.1:4280).
"""

import os
import re

import requests

BASE_URL = os.environ.get("TARGET_URL", "http://127.0.0.1:4280")
USERNAME = os.environ.get("TARGET_USERNAME", "admin")
PASSWORD = os.environ.get("TARGET_PASSWORD", "password")


def _login_session():
    """Authenticate to DVWA and return a requests.Session with cookies set."""
    session = requests.Session()
    resp = session.get(f"{BASE_URL}/login.php", timeout=10)
    resp.raise_for_status()
    match = re.search(r"name='user_token'\s+value='([^']+)'", resp.text)
    assert match, "Could not extract user_token from login page"
    token = match.group(1)

    resp = session.post(
        f"{BASE_URL}/login.php",
        data={
            "username": USERNAME,
            "password": PASSWORD,
            "Login": "Login",
            "user_token": token,
        },
        timeout=10,
        allow_redirects=True,
    )
    resp.raise_for_status()
    session.cookies.set("security", "low", domain="127.0.0.1")
    return session


def test_path_traversal_blocked():
    """
    Path traversal via the ``id`` and ``security`` parameters must not
    allow reading arbitrary .php files such as config/config.inc.php.
    """
    session = _login_session()

    # Positive control: legitimate source view works
    resp = session.get(
        f"{BASE_URL}/vulnerabilities/view_source.php",
        params={"id": "sqli", "security": "low"},
        timeout=10,
    )
    assert resp.status_code == 200
    assert "vulnerabilities/sqli/source/low.php" in resp.text, (
        "Positive control failed: legitimate source view should work"
    )

    # Exploit attempt: path traversal to read config/config.inc.php
    resp = session.get(
        f"{BASE_URL}/vulnerabilities/view_source.php",
        params={"id": "fi", "security": "../../../config/config.inc"},
        timeout=10,
    )

    secrets = ["db_password", "recaptcha_private_key", "db_user", "DBMS"]
    leaked = [s for s in secrets if s in resp.text]

    assert not leaked, (
        f"Path traversal succeeded — config file contents leaked: {leaked}"
    )


def test_xss_in_module_id_blocked():
    """
    The user-supplied module id must not be reflected into HTML or
    JavaScript without encoding.
    """
    session = _login_session()

    # Positive control: legitimate module id works
    resp = session.get(
        f"{BASE_URL}/vulnerabilities/view_source.php",
        params={"id": "sqli", "security": "low"},
        timeout=10,
    )
    assert resp.status_code == 200
    assert "vulnerabilities/sqli/source/low.php" in resp.text, (
        "Positive control failed: legitimate source view should work"
    )

    # XSS attempt: crafted id with HTML metacharacters
    xss_payload = 'xss"><script>document.title="XSS_EXECUTED"</script>'
    resp = session.get(
        f"{BASE_URL}/vulnerabilities/view_source.php",
        params={"id": xss_payload, "security": "low"},
        timeout=10,
    )

    assert xss_payload not in resp.text, (
        "XSS invariant violated: raw payload reflected unescaped into HTML/JS"
    )

    onclick_payload = f"view_source_all.php?id={xss_payload}"
    assert onclick_payload not in resp.text, (
        "XSS invariant violated: raw payload in onclick attribute"
    )
