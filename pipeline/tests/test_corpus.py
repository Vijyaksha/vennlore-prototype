from gps_engine.corpus import load_talks


def test_load_talks_joins_session_metadata(archive):
    talks = load_talks(archive)
    t = talks[10]
    assert t.title == "Talk ten"
    assert t.units == ("DCMP",)
    assert t.session_title == "Session A"


def test_load_talks_skips_withdrawn(archive):
    import json
    p = archive / "presentations" / "10.json"
    rec = json.loads(p.read_text()); rec["is_withdrawn"] = True
    p.write_text(json.dumps(rec))
    assert 10 not in load_talks(archive)


def test_load_talks_subset(archive):
    talks = load_talks(archive, only_ids={11})
    assert set(talks) == {11}
