import io
import os
import sys
import pytest

from csvdir import CsvDirFile


def _write_text(path, text, encoding="utf-8", newline="\n"):
    # Force consistent newlines in files we create
    with open(path, "w", encoding=encoding, newline=newline) as f:
        f.write(text)


def test_basic_concatenation_header_once(tmp_path):
    # Two matching CSVs -> header should appear once, then all data lines
    _write_text(tmp_path / "a.csv", "id,name\n1,A\n2,B\n")
    _write_text(tmp_path / "b.csv", "id,name\n3,C\n",)

    f = CsvDirFile(str(tmp_path))
    lines = list(f)
    assert lines[0] == "id,name\n"
    assert lines[1:] == ["1,A\n", "2,B\n", "3,C\n"]


def test_skips_header_on_matching_only(tmp_path):
    # Second file has mismatched header -> skip when on_mismatch='skip'
    _write_text(tmp_path / "good.csv", "id,name\n1,A\n")
    _write_text(tmp_path / "bad.csv", "name,id\nX,99\n")

    f = CsvDirFile(str(tmp_path), on_mismatch="skip", strict_headers=True)
    lines = list(f)
    # Only the first file should be present
    assert lines == ["id,name\n", "1,A\n"]


def test_mismatch_raises_when_error(tmp_path):
    _write_text(tmp_path / "good.csv", "id,name\n1,A\n")
    _write_text(tmp_path / "bad.csv", "name,id\nX,99\n")

    f = CsvDirFile(str(tmp_path), on_mismatch="error", strict_headers=True)
    with pytest.raises(ValueError):
        _ = list(f)


def test_utf8_bom_and_utf16le_headers(tmp_path):
    # UTF-8 with BOM
    (tmp_path / "bom.csv").write_bytes(b"\xef\xbb\xbf" + b"id,name\n1,A\n")

    # UTF-16-LE without BOM
    _write_text(tmp_path / "u16le.csv", "id,name\n2,B\n", encoding="utf-16-le")

    f = CsvDirFile(str(tmp_path))
    data = f.read()
    # Header should be emitted once, with no BOM visible
    assert data.startswith("id,name\n")
    # Both rows present
    assert "1,A\n" in data and "2,B\n" in data


def test_readline_and_read_methods(tmp_path):
    _write_text(tmp_path / "a.csv", "h\n1\n2\n")
    _write_text(tmp_path / "b.csv", "h\n3\n")

    f = CsvDirFile(str(tmp_path))
    # readline() returns header
    assert f.readline() == "h\n"
    # then one by one
    assert f.readline() == "1\n"
    assert f.readline() == "2\n"
    # read() returns the rest (not strictly size-aware yet)
    rest = f.read()
    assert rest == "3\n"
    # EOF
    assert f.readline() == ""


def test_readlines(tmp_path):
    _write_text(tmp_path / "a.csv", "h\nx\n")
    _write_text(tmp_path / "b.csv", "h\ny\n")

    with CsvDirFile(str(tmp_path)) as f:
        lines = f.readlines()
    assert lines == ["h\n", "x\n", "y\n"]


def test_empty_directory_yields_nothing(tmp_path):
    f = CsvDirFile(str(tmp_path))
    assert list(f) == []
    assert f.read() == ""


def test_recursive_and_hidden(tmp_path):
    # Hidden file & nested file
    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()
    _write_text(hidden_dir / ".h.csv", "h\nhidden\n")
    sub = tmp_path / "sub"
    sub.mkdir()
    _write_text(sub / "d.csv", "h\nd\n")
    _write_text(tmp_path / "root.csv", "h\nr\n")

    # Default: no recurse, no hidden -> only root
    f0 = CsvDirFile(str(tmp_path))
    assert f0.read() == "h\nr\n"

    # Recurse but still exclude hidden
    f1 = CsvDirFile(str(tmp_path), recurse=True)
    out1 = f1.read()
    assert out1.startswith("h\n")
    assert "r\n" in out1 and "d\n" in out1 and "hidden\n" not in out1

    # Include hidden + recurse
    f2 = CsvDirFile(str(tmp_path), recurse=True, include_hidden=True)
    out2 = f2.read()
    assert "hidden\n" in out2


def test_quotechar_detection_and_delimiter(tmp_path):
    # Pipe-delimited; first file quotes a field with double quotes,
    # second file contains a single quote in content
    _write_text(tmp_path / "a.csv", 'id|name\n1|"A|B"\n')
    _write_text(tmp_path / "b.csv", "id|name\n2|C'D\n")

    # Even if user passes the "wrong" quotechar, header detection should work
    f = CsvDirFile(str(tmp_path), delimiter="|", quotechar="'")
    lines = list(f)
    # Header once
    assert lines[0] == "id|name\n"
    # Content preserved and fully concatenated
    assert lines[1:] == ['1|"A|B"\n', "2|C'D\n"]


def test_context_manager_closes(tmp_path):
    _write_text(tmp_path / "x.csv", "h\n1\n")
    with CsvDirFile(str(tmp_path)) as f:
        assert f.readable()
        data = f.read()
        assert data == "h\n1\n"
    # After context, should be closed
    with pytest.raises(ValueError):
        _ = list(f)
