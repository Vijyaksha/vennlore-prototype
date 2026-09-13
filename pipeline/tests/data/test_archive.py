from gps_core.contracts import validate
from gps_data.archive import anchors_for, authored_by, clean_text, load_talks
from gps_data.talk import to_row


def test_clean_text():
    assert clean_text("Talk&nbsp;ten") == "Talk ten"
    assert clean_text("<p>H<sub>2</sub>O</p>") == "H2O"
    assert clean_text("&lt;not a tag&gt;") == "<not a tag>"


def test_load_joins_session_and_location_and_excludes_withdrawn(archive):
    talks = load_talks(archive)
    assert set(talks) == {10, 11, 13}
    t = talks[10]
    assert t.title == "Talk ten" and t.abstract == "Abstract of ten."
    assert t.units == ("DPOLY",) and t.session_title == "Organic Electronics & Photonics"
    assert t.session_id == 1 and t.session_code == "MAR-B31" and t.session_type == "ORAL"
    assert t.session_topics == ("Organic Electronics",)
    assert t.building == "Convention Center" and t.room == "Bluebird 3C"
    assert t.external_id == "SMT26-0000010" and t.sort_order == 1
    assert t.author_ids == (101, 102) and t.presenter_ids == (101,)


def test_orphan_talk_has_null_session_fields(archive):
    t = load_talks(archive)[13]
    assert t.session_id is None and t.session_title is None and t.units == ()
    assert t.building is None and t.room is None


def test_every_loaded_talk_is_contract_valid(archive):
    for t in load_talks(archive).values():
        validate("talk", to_row(t))


def test_only_ids_filter(archive):
    assert set(load_talks(archive, only_ids={11})) == {11}


def test_presenter_helpers(archive):
    talks = load_talks(archive)
    assert [t.id for t in anchors_for(talks, 101)] == [10]
    assert authored_by(talks, 102) == {10, 11}
    assert anchors_for(talks, 999) == [] and authored_by(talks, 999) == set()
