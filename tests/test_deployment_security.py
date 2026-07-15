from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def test_deployment_excludes_sensitive_web_artifacts():
    """The image stays useful while sensitive endpoints and data stay private."""
    dockerignore = (ROOT / ".dockerignore").read_text()
    dockerfile = (ROOT / "Dockerfile").read_text()

    assert "database/*.db" in dockerignore
    assert "phpinfo.php" in dockerignore
    assert "DVWA_SQLITE_DB_PATH=/var/lib/dvwa/sqli.db" in dockerfile
    assert "/var/lib/dvwa" in dockerfile

    # Positive control: the normal login route remains part of the image context.
    assert not any(line.strip() == "login.php" for line in dockerignore.splitlines())


def test_setup_is_opt_in_and_never_publishes_admin_credentials():
    setup = (ROOT / "setup.php").read_text()
    mysql_setup = (ROOT / "dvwa/includes/DBMS/MySQL.php").read_text()

    assert "DVWA_ENABLE_SETUP" in setup
    assert "admin</em> // <em>password" not in setup
    assert "DVWA_ADMIN_PASSWORD" in mysql_setup
    assert "'admin',MD5('password')" not in mysql_setup

    # Positive control: opting into setup still retains database provisioning.
    assert "create_db" in setup
    assert "CREATE TABLE users" in mysql_setup


def test_successful_provisioning_revokes_browser_and_api_tokens_before_redirect():
    setup = (ROOT / "setup.php").read_text()
    mysql_setup = (ROOT / "dvwa/includes/DBMS/MySQL.php").read_text()

    assert "Login::rotateSecrets()" not in setup
    assert "Login::rotateSecrets()" in mysql_setup
    assert mysql_setup.index("Login::rotateSecrets()") < mysql_setup.index("dvwaRevokeAllSessions()")
    assert mysql_setup.index("dvwaRevokeAllSessions()") < mysql_setup.rindex("dvwaPageReload()")


def test_source_viewer_only_resolves_enumerated_sources():
    script = r'''
require $argv[1];
$valid = dvwaSourceFile('brute', 'low', 'php');
if ($valid === null || !str_ends_with($valid, '/vulnerabilities/brute/source/low.php')) {
    fwrite(STDERR, "legitimate source selection failed\n");
    exit(2);
}
if (dvwaSourceFile('brute', '../../../config/config.inc', 'php') !== null) {
    fwrite(STDERR, "traversal escaped the approved source set\n");
    exit(1);
}
'''
    result = subprocess.run(
        ["php", "-r", script, str(ROOT / "dvwa/includes/source_viewer.php")],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
