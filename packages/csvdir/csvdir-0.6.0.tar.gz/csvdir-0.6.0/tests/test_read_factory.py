from csvdir.dir_reader import CsvDir
from csvdir.chunks_dir import CsvChunksDir
from csvdir import read_dir
import csvdir


def test_read_dir_factory_returns_correct_type(tmp_path, write_csv):
    write_csv("a.csv", ["h"], [["1"]])

    r = read_dir(str(tmp_path))
    assert isinstance(r, CsvDir)

    rc = csvdir.read_dir(str(tmp_path), chunksize=2)
    assert isinstance(rc, CsvChunksDir)
