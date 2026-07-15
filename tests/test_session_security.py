import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_HELPERS = ROOT / "dvwa/includes/dvwaPage.inc.php"


def php_function(source, name):
    match = re.search(rf"function\s+{name}\s*\([^)]*\)\s*\{{", source)
    assert match, f"{name} was not found"

    start = match.end()
    depth = 1
    for offset, char in enumerate(source[start:], start=start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:offset]
    raise AssertionError(f"{name} has an unterminated body")


def test_logout_clears_all_principal_bound_state():
    logout = php_function(PAGE_HELPERS.read_text(), "dvwaLogout")

    assert re.search(
        r"unset\s*\(\s*\$dvwaSession\s*\[\s*['\"]username['\"]\s*\]\s*,"
        r"\s*\$dvwaSession\s*\[\s*['\"]user_id['\"]\s*\]\s*\)",
        logout,
    ), "logout must clear both the login name and cached authorization identity"


def test_successful_login_rotates_the_pre_authentication_session():
    body = php_function(PAGE_HELPERS.read_text(), "dvwaLogin")

    rotation = body.find("session_regenerate_id( true )")
    authentication = body.find("$dvwaSession[ 'username' ] = $pUsername")
    assert 0 <= rotation < authentication, (
        "successful authentication must replace the pre-login identifier before "
        "storing the authenticated principal"
    )


def test_security_level_is_server_controlled():
    source = PAGE_HELPERS.read_text()
    getter = php_function(source, "dvwaSecurityLevelGet")
    setter = php_function(source, "dvwaSecurityLevelSet")

    assert "$_COOKIE" not in getter, "request cookies must not select a security handler"
    assert "$_DVWA[ 'default_security_level' ]" in getter
    assert "in_array" in getter, "the configured security level must be validated"
    assert "setcookie" not in setter and "$_COOKIE" not in setter, (
        "changing a training level must not make handler selection request-controlled"
    )
