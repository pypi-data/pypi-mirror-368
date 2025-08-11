import csvdir

def test_chunked_iteration(tmp_path, write_csv):
    write_csv("a.csv", ["id"], [["1"],["2"],["3"]])
    write_csv("b.csv", ["id"], [["4"],["5"]])
    rc = csvdir.read_dir(str(tmp_path), chunksize=2)

    chunks = list(rc)
    # chunks should be lists of dicts of size up to 2
    assert all(isinstance(c, list) for c in chunks)
    assert sum(len(c) for c in chunks) == 5

    # enumerate() on chunked
    en = list(rc.enumerate())
    assert all(isinstance(name, str) and isinstance(chunk, list) for name, chunk in en)

    # with_paths() on chunked
    wp = list(rc.with_paths())
    assert all(isinstance(path, str) and isinstance(chunk, list) for path, chunk in wp)
