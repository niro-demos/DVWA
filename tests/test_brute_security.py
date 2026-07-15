from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text()


def test_brute_challenge_never_accepts_credentials_in_a_get_url():
    index = source("vulnerabilities/brute/index.php")
    assert "$method            = 'POST';" in index

    for level in ("low", "medium", "high", "impossible"):
        handler = source(f"vulnerabilities/brute/source/{level}.php")
        assert "$_GET[ 'password' ]" not in handler
        assert "$_GET[ 'username' ]" not in handler


def test_every_brute_level_uses_the_shared_bounded_verifier():
    for level in ("low", "medium", "high", "impossible"):
        handler = source(f"vulnerabilities/brute/source/{level}.php")
        assert "dvwaPasswordChallenge" in handler
        assert "SELECT * FROM `users`" not in handler
        assert "md5(" not in handler.lower()


def test_shared_verifier_binds_the_authenticated_principal_and_does_not_extend_lockout():
    helper = source("dvwa/includes/dvwaPage.inc.php")
    function = helper[helper.index("function dvwaPasswordChallenge"):]

    assert "$user = dvwaCurrentUser();" in function
    assert "password_verify(" in function
    assert "failed_login >=" in function
    assert "return false;" in function
    assert function.index("failed_login >=") < function.index("failed_login = (failed_login + 1)")


def test_account_login_uses_parameterized_lookup_and_password_verify():
    login = source("login.php")
    assert "password_verify(" in login
    assert "WHERE user='$user' AND password='$pass'" not in login
    assert "md5( $pass )" not in login


def test_seeded_passwords_use_password_hash_and_columns_allow_modern_hashes():
    mysql = source("dvwa/includes/DBMS/MySQL.php")
    assert "password varchar(255)" in mysql.lower()
    assert "password_hash(" in mysql
    assert "MD5('" not in mysql

    for path in ("database/create_mssql_db.sql", "database/create_postgresql_db.sql"):
        schema = source(path)
        assert "VARCHAR(255)" in schema.upper()
        assert "MD5(" not in schema.upper()
        assert "HASHBYTES('MD5'" not in schema.upper()
