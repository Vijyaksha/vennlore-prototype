from dataclasses import fields

from gps_core.contracts import validate
from gps_data.talk import Talk, external_anchor, from_row, to_row


def test_talk_has_25_fields():
    assert len(fields(Talk)) == 25


def test_external_anchor_is_contract_valid():
    a = external_anchor("Porphyrin nanorods", "Photoconductivity is described.", ["DPOLY"])
    assert a.id == 0 and a.external_id is None and a.units == ("DPOLY",)
    validate("talk", to_row(a))


def test_to_row_uses_lists_not_tuples():
    a = external_anchor("T", "A", ["DPOLY"])
    row = to_row(a)
    assert row["units"] == ["DPOLY"] and row["author_ids"] == []


def test_from_row_round_trips_to_row():
    a = external_anchor("T", "A", ["DPOLY"])
    assert from_row(to_row(a)) == a
