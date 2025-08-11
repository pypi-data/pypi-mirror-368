import csvdir
import pytest

def test_hidden_and_recurse_toggles(tmp_path):
    # Hidden files and nested structure
    (tmp_path / ".hidden").mkdir()
    (tmp_path / ".hidden" / ".h.csv").write_text("h\nx\n", encoding="utf-8")
    (tmp_path / "visible.csv").write_text("h\nv\n", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "deep.csv").write_text("h\nd\n", encoding="utf-8")

    # Default: no recurse, exclude hidden
    r0 = csvdir.read_dir(str(tmp_path))
    assert set(r0.names) == {"visible"}

    # Recurse but still exclude hidden
    r1 = csvdir.read_dir(str(tmp_path), recurse=True)
    assert set(r1.names) == {"visible", "deep"}

    # Include hidden + recurse
    r2 = csvdir.read_dir(str(tmp_path), recurse=True, include_hidden=True)
    assert set(r2.names) == {"visible", "deep", ".h"}

def test_escapechar_and_newlines(tmp_path):
    # Use backslash escape to keep delimiter literal
    (tmp_path / "esc.csv").write_text("h\nA\\,B\n", encoding="utf-8")
    rows = list(csvdir.read_dir(str(tmp_path), delimiter=",", escapechar="\\"))
    assert rows[0]["h"] == "A,B"

def test_empty_file_and_only_header(tmp_path):
    (tmp_path / "empty.csv").write_text("", encoding="utf-8")
    (tmp_path / "header_only.csv").write_text("h\n", encoding="utf-8")
    r = csvdir.read_dir(str(tmp_path))
    # empty.csv -> no rows; header_only -> no data rows
    assert list(r) == []

def test_case_sensitive_extension(tmp_path, monkeypatch):
    # Create uppercase extension
    (tmp_path / "DATA.CSV").write_text("h\n1\n", encoding="utf-8")
    # Turn off case-insensitive matching
    r = csvdir.read_dir(str(tmp_path), case_insensitive=False)
    assert r.names == []  # should ignore DATA.CSV
    # With case-insensitive on (default), it appears
    r2 = csvdir.read_dir(str(tmp_path))
    assert r2.names == ["DATA"]
