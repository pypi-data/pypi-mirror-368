import csvdir
from pathlib import Path

def test_recurse_and_include_hidden_and_case_insensitive(tmp_path, write_csv):
    # Create nested dirs and hidden entries
    sub = tmp_path / "sub"
    sub.mkdir()
    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()

    write_csv("root.csv", ["h"], [["1"]])
    (tmp_path / "ROOT.CSV").write_text("h\n2\n", encoding="utf-8")  # uppercase extension

    # nested
    with (sub / "nested.csv").open("w", encoding="utf-8", newline="") as f:
        f.write("h\n3\n")
    # hidden file
    with (hidden_dir / ".dot.csv").open("w", encoding="utf-8", newline="") as f:
        f.write("h\n4\n")

    # default (no recurse, no hidden, case-insensitive True by default)
    r = csvdir.read_dir(str(tmp_path))
    names = set(r.names)
    assert "root" in names
    # uppercase picked up due to case_insensitive=True
    assert any(n.lower() == "root" for n in names)

    # recurse but exclude hidden (default)
    rr = csvdir.read_dir(str(tmp_path), recurse=True)
    names_r = set(rr.names)
    assert "nested" in names_r
    assert ".dot" not in names_r

    # include hidden
    rh = csvdir.read_dir(str(tmp_path), recurse=True, include_hidden=True)
    names_h = set(rh.names)
    assert ".dot" in names_h
