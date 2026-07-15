from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


IDENTIFIER_HANDLERS = [
    "vulnerabilities/sqli/source/low.php",
    "vulnerabilities/sqli/source/medium.php",
    "vulnerabilities/sqli/source/high.php",
    "vulnerabilities/sqli_blind/source/low.php",
    "vulnerabilities/sqli_blind/source/medium.php",
    "vulnerabilities/sqli_blind/source/high.php",
]


@pytest.mark.parametrize("relative_path", IDENTIFIER_HANDLERS)
def test_identifier_queries_validate_and_bind_integer_input(relative_path):
    source = (ROOT / relative_path).read_text()
    query_helper = (ROOT / "dvwa/includes/dvwaQuery.inc.php").read_text()

    # A normal integer remains queryable, but SQL syntax can never become part
    # of the statement: every handler validates and integer-binds the value.
    assert "dvwaUserById" in source
    assert "WHERE user_id = '$id'" not in source
    assert "WHERE user_id = $id" not in source
    assert "FILTER_VALIDATE_INT" in query_helper
    assert "prepare(" in query_helper
    assert "PDO::PARAM_INT" in query_helper
    assert "SQLITE3_INTEGER" in query_helper


def test_low_security_login_binds_credentials_and_returns_generic_failure():
    source = (ROOT / "vulnerabilities/brute/source/low.php").read_text()

    assert "WHERE user = '$user'" not in source
    assert "prepare(" in source
    assert "PARAM_STR" in source
    assert "Username and/or password incorrect." in source
    assert "mysqli_error" not in source
