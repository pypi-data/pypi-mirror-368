import io
import sys
import pytest

pandas = pytest.importorskip("pandas")

from csvdir import CsvDirFile


def _write_text(path, text, encoding="utf-8", newline="\n"):
    with open(path, "w", encoding=encoding, newline=newline) as f:
        f.write(text)


@pytest.mark.parametrize("engine", ["c", "python"])
def test_pandas_engine_reads_csvdirfile(tmp_path, engine):
    # simple dataset across two files
    _write_text(tmp_path / "a.csv", "id,name\n1,A\n")
    _write_text(tmp_path / "b.csv", "id,name\n2,B\n")

    f = CsvDirFile(str(tmp_path))
    df = pandas.read_csv(f, engine=engine)
    assert list(df.columns) == ["id", "name"]
    assert len(df) == 2
    assert set(df["name"]) == {"A", "B"}


def test_seek_and_reread_with_pandas(tmp_path):
    _write_text(tmp_path / "x.csv", "h\n1\n2\n")
    _write_text(tmp_path / "y.csv", "h\n3\n")

    f = CsvDirFile(str(tmp_path))

    # first read
    df1 = pandas.read_csv(f)
    assert list(df1["h"]) == [1, 2, 3]

    # restart stream and read again
    f.seek(0)
    df2 = pandas.read_csv(f)
    assert list(df2["h"]) == [1, 2, 3]

    # position should be at end after second read
    assert f.tell() >= len("h\n1\n2\n3\n")


def test_read_size_and_readline_semantics(tmp_path):
    _write_text(tmp_path / "a.csv", "a,b\n1,2\n3,4\n")
    f = CsvDirFile(str(tmp_path))

    # read just the header via size-limited read
    s = f.read(4)
    assert s == "a,b\n"
    pos_after_header = f.tell()
    assert pos_after_header == 4

    # next line via readline
    line = f.readline()
    assert line == "1,2\n"
    assert f.tell() == pos_after_header + len(line)

    # read the rest
    rest = f.read()
    assert rest == "3,4\n"
    assert f.readline() == ""  # EOF


def test_pandas_chunksize_and_iteration(tmp_path):
    _write_text(tmp_path / "a.csv", "val\n1\n2\n")
    _write_text(tmp_path / "b.csv", "val\n3\n4\n5\n")

    f = CsvDirFile(str(tmp_path))
    reader = pandas.read_csv(f, chunksize=2)
    seen = []
    for chunk in reader:
        seen.extend(chunk["val"].tolist())
    assert seen == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("engine", ["c", "python"])
def test_pandas_respects_on_mismatch_skip(tmp_path, engine):
    _write_text(tmp_path / "good.csv", "id,name\n1,A\n")
    _write_text(tmp_path / "bad.csv", "name,id\nX,99\n")  # swapped order

    f = CsvDirFile(str(tmp_path), strict_headers=True, on_mismatch="skip")
    df = pandas.read_csv(f, engine=engine)
    assert list(df.columns) == ["id", "name"]
    assert len(df) == 1
    assert df.iloc[0].to_dict() == {"id": 1, "name": "A"}


@pytest.mark.parametrize("engine", ["c", "python"])
def test_pandas_raises_on_mismatch_error(tmp_path, engine):
    _write_text(tmp_path / "good.csv", "id,name\n1,A\n")
    _write_text(tmp_path / "bad.csv", "name,id\nX,99\n")

    f = CsvDirFile(str(tmp_path), strict_headers=True, on_mismatch="error")
    with pytest.raises(ValueError):
        pandas.read_csv(f, engine=engine)


def test_seek_only_supports_restart(tmp_path):
    _write_text(tmp_path / "x.csv", "h\n1\n")
    f = CsvDirFile(str(tmp_path))
    # restart is allowed
    f.seek(0)
    # relative seek of 0 is allowed (no-op)
    f.seek(0, 1)
    # anything else should be unsupported
    with pytest.raises(io.UnsupportedOperation):
        f.seek(1, 0)
    with pytest.raises(io.UnsupportedOperation):
        f.seek(5, 2)
