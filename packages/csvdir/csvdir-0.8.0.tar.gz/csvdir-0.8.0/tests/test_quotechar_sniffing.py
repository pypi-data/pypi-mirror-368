import csvdir

def test_quotechar_detection_when_user_passes_wrong_value(tmp_path):
    # Real quoting uses double quotes around field containing delimiter
    (tmp_path / "a.csv").write_text('id|name\n1|"A|B"\n', encoding="utf-8")
    # Single quote appears in content but not as quoting
    (tmp_path / "b.csv").write_text("id|name\n2|C'D\n", encoding="utf-8")

    r = csvdir.read_dir(str(tmp_path), delimiter="|", quotechar="'")  # wrong on purpose
    rows = list(r)
    assert rows[0]["name"] == "A|B"
    assert rows[1]["name"] == "C'D"
