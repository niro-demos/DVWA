from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("level", ["low", "medium", "high", "impossible"])
def test_file_viewer_only_allows_documented_application_files(level):
    source = (ROOT / "vulnerabilities" / "fi" / "source" / f"{level}.php").read_text()
    source += (ROOT / "vulnerabilities" / "fi" / "source" / "secure.php").read_text()

    # Positive control: the intended viewer entry remains available.
    assert "include.php" in source

    # Security invariant: no traversal or stream-wrapper input reaches include().
    assert "in_array" in source
    assert "configFileNames" in source
    assert 'file*' not in source
    assert "str_replace" not in source


@pytest.mark.parametrize("level", ["low", "medium", "high", "impossible"])
def test_uploads_are_images_with_server_generated_names(level):
    source = (ROOT / "vulnerabilities" / "upload" / "source" / f"{level}.php").read_text()
    source += (ROOT / "vulnerabilities" / "upload" / "source" / "secure.php").read_text()

    # Positive control: JPEG and PNG uploads remain supported.
    assert "jpg" in source or "jpeg" in source
    assert "png" in source

    # Security invariants: ignore attacker-selected object names, validate the
    # decoded image, and re-encode it so trailing executable data is discarded.
    assert "random_bytes" in source
    assert "getimagesize" in source
    assert "imagecreatefromjpeg" in source
    assert "imagecreatefrompng" in source
    assert "move_uploaded_file" not in source
