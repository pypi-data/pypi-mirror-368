import csvdir
import pytest

def test_chunked_strict_headers_uses_first_file_as_canonical(tmp_path, write_csv):
    write_csv("a.csv", ["id","name","age"], [["1","a","9"], ["2","b","10"]])
    write_csv("b.csv", ["id","name","age"], [["3","c","11"]])
    rc = csvdir.read_dir(str(tmp_path), chunksize=2, strict_headers=True)
    # Should not raise; should yield all rows across both files in chunks
    chunks = list(rc)
    total = sum(len(c) for c in chunks)
    assert total == 3

def test_chunked_expected_headers_error_on_mismatch(tmp_path, write_csv):
    write_csv("a.csv", ["id","name","age"], [["1","a","9"]])
    write_csv("b.csv", ["id","name"], [["2","b"]])
    rc = csvdir.read_dir(
        str(tmp_path),
        chunksize=2,
        expected_headers=["id","name","age"],
        on_mismatch="error",
    )
    with pytest.raises(ValueError):
        list(rc)  # mismatch should raise

def test_chunked_expected_headers_skip_on_mismatch(tmp_path, write_csv):
    write_csv("a.csv", ["id","name","age"], [["1","a","9"], ["2","b","10"]])
    write_csv("b.csv", ["id","name"], [["3","c"]])  # missing 'age'
    rc = csvdir.read_dir(
        str(tmp_path),
        chunksize=2,
        expected_headers=["id","name","age"],
        on_mismatch="skip",
    )
    # Should only read rows from a.csv, b.csv is skipped entirely
    chunks = list(rc)
    total = sum(len(c) for c in chunks)
    assert total == 2

def test_chunked_enumerate_and_with_paths_obey_header_checks(tmp_path, write_csv):
    write_csv("good.csv", ["id","name"], [["1","a"],["2","b"]])
    write_csv("bad.csv", ["id"], [["3"]])  # missing 'name'
    # enumerate(): skip bad file
    rc_enum = csvdir.read_dir(
        str(tmp_path),
        chunksize=1,
        expected_headers=["id","name"],
        on_mismatch="skip",
    ).enumerate()
    items = list(rc_enum)
    # All chunks should be from "good"
    assert all(name == "good" for name, _ in items)
    # with_paths(): skip bad file too
    rc_paths = csvdir.read_dir(
        str(tmp_path),
        chunksize=1,
        expected_headers=["id","name"],
        on_mismatch="skip",
    ).with_paths()
    items_p = list(rc_paths)
    assert all(p.endswith("good.csv") for p, _ in items_p)
