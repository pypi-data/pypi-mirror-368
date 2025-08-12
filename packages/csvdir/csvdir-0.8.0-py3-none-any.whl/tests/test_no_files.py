import csvdir

def test_no_matching_files(tmp_path):
    r = csvdir.read_dir(str(tmp_path))
    assert r.names == []
    assert list(r) == []
    # chunked also yields nothing
    rc = csvdir.read_dir(str(tmp_path), chunksize=2)
    assert list(rc) == []
