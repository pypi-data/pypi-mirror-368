import csvdir
import pytest

def test_strict_headers_uses_first_file_as_canonical(tmp_path, write_csv):
    write_csv("a.csv", ["id","name","age"], [["1","a","9"]])
    write_csv("b.csv", ["id","name","age"], [["2","b","10"]])
    r = csvdir.read_dir(str(tmp_path), strict_headers=True)
    assert len(list(r)) == 2  # no errors

def test_expected_headers_error_on_mismatch(tmp_path, write_csv):
    write_csv("a.csv", ["id","name","age"], [["1","a","9"]])
    write_csv("b.csv", ["id","name"], [["2","b"]])
    r = csvdir.read_dir(str(tmp_path), expected_headers=["id","name","age"], on_mismatch="error")
    with pytest.raises(ValueError):
        list(r)  # mismatch should raise

def test_expected_headers_skip_on_mismatch(tmp_path, write_csv):
    write_csv("a.csv", ["id","name","age"], [["1","a","9"]])
    write_csv("b.csv", ["id","name"], [["2","b"]])
    r = csvdir.read_dir(str(tmp_path), expected_headers=["id","name","age"], on_mismatch="skip")
    rows = list(r)
    # only rows from a.csv should be counted
    assert len(rows) == 1
