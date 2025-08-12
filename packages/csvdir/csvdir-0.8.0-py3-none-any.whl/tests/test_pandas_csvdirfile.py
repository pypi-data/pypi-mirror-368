import io
import sys
import pytest

pandas = pytest.importorskip("pandas")

from csvdir import CsvDirFile


def _write_text(path, text, encoding="utf-8", newline="\n"):
    with open(path, "w", encoding=encoding, newline=newline) as f:
        f.write(text)


def test_pandas_reads_all_rows(tmp_path):
    _write_text(tmp_path / "a.csv", "id,name\n1,A\n2,B\n")
    _write_text(tmp_path / "b.csv", "id,name\n3,C\n")

    f = CsvDirFile(str(tmp_path))
    df = pandas.read_csv(f)
    assert list(df.columns) == ["id", "name"]
    assert len(df) == 3
    assert df.iloc[-1].to_dict() == {"id": 3, "name": "C"}


def test_pandas_with_custom_delimiter(tmp_path):
    _write_text(tmp_path / "x.csv", 'id|name\n1|"A|B"\n')
    _write_text(tmp_path / "y.csv", "id|name\n2|C'D\n")

    # pandas needs sep to match the file content
    f = CsvDirFile(str(tmp_path), delimiter="|", quotechar="'")
    df = pandas.read_csv(f, sep="|", quotechar='"')  # header parsing handled by CsvDirFile
    assert list(df.columns) == ["id", "name"]
    assert set(df["name"]) == {"A|B", "C'D"}


def test_pandas_chunksize_iteration(tmp_path):
    _write_text(tmp_path / "a.csv", "h\n1\n2\n")
    _write_text(tmp_path / "b.csv", "h\n3\n4\n")

    f = CsvDirFile(str(tmp_path))
    reader = pandas.read_csv(f, chunksize=2)
    total = 0
    for chunk in reader:
        total += len(chunk)
    assert total == 4


def test_pandas_skip_bad_header_on_mismatch_skip(tmp_path):
    _write_text(tmp_path / "good.csv", "id,name\n1,A\n")
    _write_text(tmp_path / "bad.csv", "name,id\nX,99\n")  # swapped

    f = CsvDirFile(str(tmp_path), strict_headers=True, on_mismatch="skip")
    df = pandas.read_csv(f)
    assert list(df.columns) == ["id", "name"]
    assert len(df) == 1
    assert df.iloc[0].to_dict() == {"id": 1, "name": "A"}


def test_pandas_mismatch_raises_when_error(tmp_path):
    _write_text(tmp_path / "good.csv", "id,name\n1,A\n")
    _write_text(tmp_path / "bad.csv", "name,id\nX,99\n")

    f = CsvDirFile(str(tmp_path), strict_headers=True, on_mismatch="error")
    with pytest.raises(ValueError):
        pandas.read_csv(f)


def test_pandas_mixed_encodings(tmp_path):
    # UTF-8 with BOM
    (tmp_path / "bom.csv").write_bytes(b"\xef\xbb\xbf" + b"id,name\n1,A\n")
    # UTF-16-LE without BOM
    _write_text(tmp_path / "u16le.csv", "id,name\n2,B\n", encoding="utf-16-le")

    f = CsvDirFile(str(tmp_path))
    df = pandas.read_csv(f)
    assert list(df.columns) == ["id", "name"]
    assert set(df["name"]) == {"A", "B"}


def test_pandas_recursive_and_hidden(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / ".hidden").mkdir()
    _write_text(tmp_path / "root.csv", "h\nr\n")
    _write_text(tmp_path / "sub" / "deep.csv", "h\nd\n")
    _write_text(tmp_path / ".hidden" / ".h.csv", "h\nhidden\n")

    # recurse but exclude hidden (default)
    f1 = CsvDirFile(str(tmp_path), recurse=True)
    df1 = pandas.read_csv(f1)
    assert set(df1["h"]) == {"r", "d"}

    # include hidden too
    f2 = CsvDirFile(str(tmp_path), recurse=True, include_hidden=True)
    df2 = pandas.read_csv(f2)
    assert set(df2["h"]) == {"r", "d", "hidden"}
