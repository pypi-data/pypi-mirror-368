import csvdir
from pathlib import Path

def test_basic_iteration(tmp_path, write_csv):
    d = tmp_path / "data"
    d.mkdir()
    write_csv("people.csv", ["id","name","age"], [["1","Odos","38"],["2","Kayla","39"]])
    write_csv("people2.csv", ["id","name","age"], [["3","Meda","27"],["4","Oli","5"],["5","Una","11"]])

    r = csvdir.read_dir(str(tmp_path))
    # names are derived from discovered paths
    assert sorted(r.names) == ["people","people2"]
    # collect all rows across files
    rows = list(r)
    assert len(rows) == 5
    assert rows[0]["name"] == "Odos"

    # enumerate() yields (name, row)
    en = list(r.enumerate())
    assert en[0][0] in ("people","people2")
    assert isinstance(en[0][1], dict)

    # with_paths() yields (path, row)
    wp = list(r.with_paths())
    assert Path(wp[0][0]).suffix == ".csv"
    assert isinstance(wp[0][1], dict)
