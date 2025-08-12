import csvdir
from pathlib import Path

def test_mixed_encodings_autopick(tmp_path):
    # UTF-8 with BOM
    p1 = tmp_path / "bom.csv"
    p1.write_bytes(b'\xef\xbb\xbf' + "h\n1\n".encode("utf-8"))

    # UTF-16-LE without BOM
    p2 = tmp_path / "u16le.csv"
    p2.write_bytes("h\n2\n".encode("utf-16-le"))

    # Normal UTF-8
    p3 = tmp_path / "u8.csv"
    p3.write_text("h\n3\n", encoding="utf-8")

    it = csvdir.read_dir(str(tmp_path))
    vals = [row["h"] for row in it]
    assert set(vals) == {"1", "2", "3"}
