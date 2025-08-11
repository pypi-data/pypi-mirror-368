import csvdir

def test_custom_delimiter_quote_and_encoding(tmp_path, write_csv):
    # pipe-delimited with single-quote quotechar
    write_csv("x.csv", ["id","name"], [["1","A|B"],["2","C'D"]], delimiter="|")
    r = csvdir.read_dir(str(tmp_path), delimiter="|", quotechar="'")
    rows = list(r)
    assert rows[0]["name"] == "A|B"

    # utf-16 encoded file
    write_csv("u.csv", ["col"], [["α"]], encoding="utf-16")
    r2 = csvdir.read_dir(str(tmp_path), encoding="utf-16")
    rows2 = list(r2)
    assert rows2[0]["col"] == "α"
