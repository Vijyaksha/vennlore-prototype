import json

import pytest


@pytest.fixture
def archive(tmp_path):
    """Mimics data/gps2026: events/, presentations/, locations/."""
    for sub in ("events", "presentations", "locations"):
        (tmp_path / sub).mkdir()
    (tmp_path / "locations" / "9001.json").write_text(json.dumps({
        "id": 9001, "external_id": None, "type": "PHYSICAL",
        "building": "Convention Center", "room": "Bluebird 3C"}))
    (tmp_path / "events" / "1.json").write_text(json.dumps({
        "id": 1, "type": "ORAL", "code": "MAR-B31", "title": "Organic Electronics &amp; Photonics",
        "sponsor_units": ["DPOLY"], "topics": ["Organic Electronics"],
        "presentation_ids": [10, 11, 12], "location_ids": [9001],
        "periods": [{"start": "2026-03-16T14:00:00.000Z", "end": "2026-03-16T16:24:00.000Z"}]}))
    base = {"is_invited": False, "is_withdrawn": False, "type": "Oral-In-person",
            "topics": ["Condensed Matter"], "author_ids": [101, 102], "presenter_ids": [101],
            "publication_reference": None, "funding_acknowledgement": "NSF",
            "team_acknowledgement": None, "presentation_location": None,
            "start": "2026-03-16T14:00:00.000Z", "end": "2026-03-16T14:12:00.000Z"}
    rows = [
        dict(base, id=10, external_id="SMT26-0000010", sort_order=1,
             title="Talk&nbsp;ten", abstract="<p>Abstract of ten.</p>"),
        dict(base, id=11, external_id="SMT26-0000011", sort_order=2,
             title="Talk eleven", abstract="Abstract of eleven.",
             author_ids=[102, 103], presenter_ids=[103]),
        dict(base, id=12, external_id="SMT26-0000012", sort_order=3,
             title="Withdrawn talk", abstract="Gone.", is_withdrawn=True),
    ]
    for r in rows:
        (tmp_path / "presentations" / f"{r['id']}.json").write_text(json.dumps(r))
    # a talk with no session at all
    (tmp_path / "presentations" / "13.json").write_text(json.dumps(
        dict(base, id=13, external_id="SMT26-0000013", sort_order=1,
             title="Orphan", abstract="No session.", author_ids=[104], presenter_ids=[104])))
    return tmp_path
