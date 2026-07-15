import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = '<img src=x onerror="document.title=\'xss\'">'


def php(code: str) -> str:
    result = subprocess.run(
        ["php", "-r", code], cwd=ROOT, text=True, capture_output=True, check=True
    )
    return result.stdout


def test_reflected_names_are_encoded_at_every_security_level():
    for level in ("low", "medium", "high"):
        output = php(
            f'$_GET["name"]={PAYLOAD!r}; $html=""; '
            f'include "vulnerabilities/xss_r/source/{level}.php"; echo $html;'
        )
        assert "Hello" in output  # legitimate rendering remains healthy
        assert PAYLOAD not in output
        assert "&lt;img" in output


def test_profile_fields_are_encoded_at_each_profile_sink():
    for level in ("low", "medium"):
        source = (ROOT / f"vulnerabilities/bac/source/{level}.php").read_text()
        for field in ("user_id", "first_name", "last_name", "avatar"):
            assert re.search(
                rf"htmlspecialchars\(\s*\$row\[['\"]{field}['\"]\]",
                source,
            ), f"{field} is not encoded in {level} profile output"


def test_source_viewer_separates_lookup_values_from_encoded_display_values():
    source = (ROOT / "vulnerabilities/view_source.php").read_text()
    assert "htmlspecialchars( $id, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8' )" in source
    assert "htmlspecialchars( $security, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8' )" in source
    assert 'onclick="window.location.href=' not in source
    assert "rawurlencode( $id )" in source


def test_guestbook_always_encodes_stored_name_and_comment():
    source = (ROOT / "dvwa/includes/dvwaPage.inc.php").read_text()
    function = source[source.index("function dvwaGuestbook()") :]
    assert re.search(r"\$name\s*=\s*htmlspecialchars\(\s*\$row\[0\]", function)
    assert re.search(r"\$comment\s*=\s*htmlspecialchars\(\s*\$row\[1\]", function)
    assert "if( dvwaSecurityLevelGet() == 'impossible' )" not in function


def test_language_selector_uses_query_value_and_safe_dom_apis():
    source = (ROOT / "vulnerabilities/xss_d/index.php").read_text()
    assert "document.write" not in source
    assert ".searchParams.get('default')" in source
    assert ".textContent" in source
    assert ".appendChild" in source
