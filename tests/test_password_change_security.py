from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def source(relative_path):
    return (ROOT / relative_path).read_text()


def test_low_csrf_password_change_requires_post_token_and_current_password():
    handler = source("vulnerabilities/csrf/source/low.php")
    page = source("vulnerabilities/csrf/index.php")

    assert "$_POST[ 'Change' ]" in handler
    assert "checkToken(" in handler
    assert "password_current" in handler
    assert "SELECT password FROM users" in handler
    assert 'method=\\"POST\\"' in page
    assert "tokenField()" in page


def test_medium_csrf_password_change_requires_server_issued_token():
    handler = source("vulnerabilities/csrf/source/medium.php")
    page = source("vulnerabilities/csrf/index.php")

    assert "checkToken(" in handler
    assert "HTTP_REFERER" not in handler
    assert "tokenField()" in page


def test_low_captcha_confirmation_requires_single_use_session_authorization():
    handler = source("vulnerabilities/captcha/source/low.php")

    assert "$_SESSION[ 'captcha_passed' ]" in handler
    assert "unset( $_SESSION[ 'captcha_passed' ] )" in handler
    assert "dvwaCurrentUser()" in handler


def test_high_captcha_accepts_only_provider_verified_response():
    handler = source("vulnerabilities/captcha/source/high.php")

    assert "hidd3n_valu3" not in handler
    assert "HTTP_USER_AGENT" not in handler
    assert "recaptcha_private_key" in handler
    assert "Password Changed." in handler
