import csvdir
import csv
from pathlib import Path

def write(tmp_path: Path, name: str, header, rows, delimiter=","):
    p = tmp_path / name
    with open(p, "w", newline="") as f:
        w = csv.writer(f, delimiter=delimiter)
        w.writerow(header)
        w.writerows(rows)
    return p

def test_iterpath_column_chunks(tmp_path):
    write(tmp_path, "a.csv", ["id","name"], [[1,"A"],[2,"B"],[3,"C"]])
    r = csvdir.read_dir(str(tmp_path), chunksize=2).with_paths()
    got = list(r.iter_column_chunks("name"))
    assert got == [
        (str(tmp_path / "a.csv"), ["A","B"]),
        (str(tmp_path / "a.csv"), ["C"]),
    ]

def test_iterenum_column_chunks(tmp_path):
    write(tmp_path, "a.csv", ["id","name"], [[1,"A"],[2,"B"],[3,"C"]])
    r = csvdir.read_dir(str(tmp_path), chunksize=2).enumerate()
    got = list(r.iter_column_chunks("name"))
    assert got == [
        ("a.csv", ["A","B"]),
        ("a.csv", ["C"]),
    ]

def test_iterpath_select_columns_chunks(tmp_path):
    write(tmp_path, "a.csv", ["id","name","age"], [[1,"A",10],[2,"B",20],[3,"C",30]])
    r = csvdir.read_dir(str(tmp_path), chunksize=2).with_paths()
    got = list(r.select_columns_chunks(["name","age"]))
    assert got == [
        (str(tmp_path / "a.csv"), [{"name":"A","age":"10"},{"name":"B","age":"20"}]),
        (str(tmp_path / "a.csv"), [{"name":"C","age":"30"}]),
    ]

def test_iterenum_select_columns_chunks(tmp_path):
    write(tmp_path, "a.csv", ["id","name","age"], [[1,"A",10],[2,"B",20]])
    r = csvdir.read_dir(str(tmp_path), chunksize=2).enumerate()
    got = list(r.select_columns_chunks(["name","age"]))
    assert got == [
        ("a.csv", [{"name":"A","age":"10"},{"name":"B","age":"20"}]),
    ]
