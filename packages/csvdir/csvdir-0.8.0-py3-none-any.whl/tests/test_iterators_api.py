import csvdir

def test_iter_helpers_return_iterators_and_alias_with_names(tmp_path):
    (tmp_path / "x.csv").write_text("id,name\n1,A\n", encoding="utf-8")

    r = csvdir.read_dir(str(tmp_path))
    it_names = r.with_names()
    first_name = next(it_names)
    assert first_name[0] == "x" and isinstance(first_name[1], dict)

    it_paths = r.with_paths()
    first_path = next(it_paths)
    assert first_path[0].endswith("x.csv") and isinstance(first_path[1], dict)

    # chunked variants
    rc = csvdir.read_dir(str(tmp_path), chunksize=1)
    itc_names = rc.enumerate()
    name, chunk = next(itc_names)
    assert name == "x" and isinstance(chunk, list) and isinstance(chunk[0], dict)

    itc_paths = rc.with_paths()
    path, chunk2 = next(itc_paths)
    assert path.endswith("x.csv") and isinstance(chunk2, list)
