import os
from pathlib import Path

ROOT = Path(os.environ.get("DVWA_SOURCE_ROOT", Path(__file__).resolve().parents[1]))


def source(path):
    return (ROOT / path).read_text()


def test_api_credentials_and_signing_keys_are_deployment_managed():
    controller = source("vulnerabilities/api/src/LoginController.php")
    login = source("vulnerabilities/api/src/Login.php")
    setup = source("setup.php")
    assert "1471.dvwa.digi.ninja" not in controller
    assert "ABigLongSecret" not in controller
    assert "mrbennett" not in controller
    assert "becareful" not in controller
    assert "password_verify" in controller
    assert "random_bytes(32)" in login
    assert "Login::rotateSecrets()" in setup

def test_user_api_requires_a_token_and_never_serializes_passwords():
    router = source("vulnerabilities/api/public/index.php")
    user = source("vulnerabilities/api/src/User.php")

    assert 'HTTP/1.1 403 Forbidden' in router
    assert "Login::check_access_token" in router
    assert '"password" => $this->password' not in user
    assert '"name" => $this->name' in user  # legitimate records remain available

def test_user_administration_is_admin_only_and_parameterized():
    read = source("vulnerabilities/authbypass/get_user_data.php")
    update = source("vulnerabilities/authbypass/change_user_details.php")
    for endpoint in (read, update):
        assert "dvwaCurrentUser() !== 'admin'" in endpoint
        assert "http_response_code(403)" in endpoint
    assert "mysqli_prepare" in update
    assert "mysqli_stmt_bind_param" in update
    assert "UPDATE users SET first_name = '" not in update

def test_profile_access_uses_the_authenticated_user_id():
    low = source("vulnerabilities/bac/source/low.php")
    medium = source("vulnerabilities/bac/source/medium.php")
    assert "$id === $current_user_id" in low
    assert "$_COOKIE['user_id']" not in low
    assert "$id === (int) $current_user_id" in medium
    assert "$_GET['token'] == 'user_token'" not in medium
    assert "SELECT first_name, last_name" in low
    assert "SELECT first_name, last_name" in medium
