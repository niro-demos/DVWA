from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text()


def test_supported_security_levels_remain_available():
    page = source("dvwa/includes/dvwaPage.inc.php")
    for level in ("low", "medium", "high", "impossible"):
        assert f"'{level}'" in page


def test_authenticated_session_cookies_are_always_httponly():
    page = source("dvwa/includes/dvwaPage.inc.php")
    session_function = page.split("function dvwa_start_session()", 1)[1].split("\n}", 1)[0]
    assert "$httponly = false" not in session_function
    assert "$httponly = true" in session_function


def test_session_identifiers_are_rotated_and_predecessors_deleted():
    page = source("dvwa/includes/dvwaPage.inc.php")
    login_function = page.split("function dvwaLogin", 1)[1].split("\n}", 1)[0]
    assert "session_regenerate_id( true )" in login_function
    assert "session_regenerate_id(true)" in page


def test_login_sessions_are_bound_to_the_users_authentication_version():
    page = source("dvwa/includes/dvwaPage.inc.php")
    assert "session_version" in page
    assert "dvwaSessionVersionRefresh" in page
    assert "dvwaSessionVersionIsCurrent" in page


def test_every_password_change_rotates_the_authentication_version():
    for level in ("low", "medium", "high", "impossible"):
        implementation = source(f"vulnerabilities/csrf/source/{level}.php")
        assert "dvwaSessionVersionRotate" in implementation


def test_database_recreation_revokes_all_application_sessions():
    setup = source("setup.php")
    assert "dvwaRevokeAllSessions" in source("dvwa/includes/DBMS/MySQL.php")
    assert "successful initializer revokes all DVWA sessions" in setup


def test_active_user_schema_includes_an_authentication_version():
    assert "session_version" in source("dvwa/includes/DBMS/MySQL.php")
