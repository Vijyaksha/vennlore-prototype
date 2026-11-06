"""Tests for priority.order — putting likely-large unresearched rows first."""
import priority


def row(r, tier, score=None):
    return {"row": r, "tier": tier, "score": score}


def test_unresearched_rows_come_before_researched_rows():
    out = priority.order([row(1, "VERIFIED"), row(2, "NOT YET CENSUSED", 1)])

    assert [x["row"] for x in out] == [2, 1]


def test_unresearched_rows_are_sorted_most_likely_large_first():
    out = priority.order([row(1, "NOT YET CENSUSED", 2), row(2, "NOT YET CENSUSED", 5),
                          row(3, "NOT YET CENSUSED", 3)])

    assert [x["row"] for x in out] == [2, 3, 1]


def test_ties_keep_their_original_order():
    out = priority.order([row(7, "NOT YET CENSUSED", 4), row(3, "NOT YET CENSUSED", 4)])

    assert [x["row"] for x in out] == [7, 3]


def test_researched_rows_are_grouped_verified_then_borderline_then_out():
    out = priority.order([row(1, "OUT"), row(2, "BORDERLINE"), row(3, "VERIFIED")])

    assert [x["row"] for x in out] == [3, 2, 1]


def test_order_loses_no_rows():
    rows = [row(i, t, 3) for i, t in enumerate(["OUT", "NOT YET CENSUSED", "VERIFIED", "BORDERLINE"])]

    assert len(priority.order(rows)) == 4
