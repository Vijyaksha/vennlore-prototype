from gps_engine.app_export import build_seed, build_talk_row, clean_text


def test_clean_text_decodes_entities_strips_tags_collapses_whitespace():
    assert clean_text("Memristive&nbsp;Properties") == "Memristive Properties"
    assert clean_text("H<sub>2</sub>O and CO<sub>2</sub>") == "H2O and CO2"
    assert clean_text("Organic Electronics &amp; Photonics") == "Organic Electronics & Photonics"
    assert clean_text("  spaced\n\n  out\ttext  ") == "spaced out text"
    assert clean_text("&lt;not a tag&gt;") == "<not a tag>"


PRES = {"id": 2802, "title": "Memristive&nbsp;Properties", "abstract": "<p>Body&nbsp;text.</p>",
        "start": "2026-03-19T15:12:00.000Z", "end": "2026-03-19T15:24:00.000Z"}
EVENT = {"id": 245, "title": "Organic Electronics &amp; Photonics", "sponsor_units": ["DPOLY"],
         "presentation_ids": [2802], "location_ids": [1368547704]}
LOC = {"id": 1368547704, "building": "Convention Center", "room": "Bluebird 3C"}


def test_build_talk_row_joins_event_and_location():
    row = build_talk_row(PRES, EVENT, LOC)
    assert row == {
        "id": 2802, "title": "Memristive Properties",
        "session_title": "Organic Electronics & Photonics", "units": ["DPOLY"],
        "start": "2026-03-19T15:12:00.000Z", "end": "2026-03-19T15:24:00.000Z",
        "building": "Convention Center", "room": "Bluebird 3C",
        "abstract": "Body text.",
    }


def test_build_talk_row_without_event_or_location():
    row = build_talk_row(PRES, None, None)
    assert row["session_title"] is None
    assert row["units"] == []
    assert row["building"] is None
    assert row["room"] is None


def test_build_talk_row_keeps_null_times():
    pres = dict(PRES, start=None, end=None)
    row = build_talk_row(pres, EVENT, LOC)
    assert row["start"] is None and row["end"] is None


ANCHOR = {"id": 0, "title": "Photoconductivity of Self-Assembled Porphyrin Nanorods",
          "session_title": None, "units": ["DPOLY"], "start": None, "end": None,
          "building": None, "room": None, "abstract": "The photoconductivity..."}


def test_build_seed_assembles_and_sorts():
    pres_b = {"id": 99, "title": "B", "abstract": "b", "start": None, "end": None}
    judgment = {"candidate_id": 2802, "same_method": 4, "specificity": 3,
                "usage_parallel": 4, "match": True, "cross_domain": True,
                "why": "same readout"}
    seed = build_seed([pres_b, PRES], [EVENT], [LOC], [judgment], ANCHOR)

    assert [t["id"] for t in seed["talks"]] == [0, 99, 2802]
    assert seed["talks"][0] == ANCHOR
    assert seed["talks"][1]["session_title"] is None  # 99 belongs to no event
    assert seed["talks"][2]["room"] == "Bluebird 3C"
    assert seed["locations"] == [LOC]

    rec = seed["recommendations"][0]
    assert rec == {"for_talk_id": 0, "candidate_id": 2802,
                   "same_method": 4, "specificity": 3, "usage_parallel": 4,
                   "score": 11, "match": True, "cross_domain": True,
                   "why": "same readout", "strongest_parallel": ""}


def test_build_seed_keeps_strongest_parallel_when_present():
    judgment = {"candidate_id": 7, "same_method": 1, "specificity": 2,
                "usage_parallel": 3, "match": False, "cross_domain": False,
                "why": "w", "strongest_parallel": "both measure X"}
    seed = build_seed([], [], [], [judgment], ANCHOR)
    rec = seed["recommendations"][0]
    assert rec["score"] == 6
    assert rec["strongest_parallel"] == "both measure X"


def test_build_seed_projects_location_rows():
    raw = dict(LOC, external_id=None, type="PHYSICAL")
    seed = build_seed([], [], [raw], [], ANCHOR)
    assert seed["locations"] == [LOC]


def test_build_seed_sorts_recommendations_by_candidate_id():
    js = [{"candidate_id": c, "same_method": 1, "specificity": 1,
           "usage_parallel": 1, "match": False, "cross_domain": False, "why": ""}
          for c in (30, 10, 20)]
    seed = build_seed([], [], [], js, ANCHOR)
    assert [r["candidate_id"] for r in seed["recommendations"]] == [10, 20, 30]
