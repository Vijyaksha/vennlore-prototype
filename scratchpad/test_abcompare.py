"""Tests for abcompare — grading one census run against another.

Agreement rate alone is misleading: most rows correctly yield no figure, so two runs
can agree on nothing useful. What matters are the failure modes that corrupt a census:
a figure with no source, a figure credited to no rung, an artefact named but never
counted, and an unsourced OUT (absence of evidence recorded as evidence).
"""
import abcompare

CONTROL = [
    {"row": 1, "conference": "A", "abstracts_numeric": 8719, "rung": 4,
     "source_url": "https://x/1", "verdict": "VERIFIED", "method": "counted"},
    {"row": 2, "conference": "B", "abstracts_numeric": None, "rung": None,
     "source_url": None, "verdict": "UNRESOLVED", "method": "nothing found"},
    {"row": 3, "conference": "C", "abstracts_numeric": 291, "rung": 3,
     "source_url": "https://x/3", "verdict": "OUT", "method": "counted"},
]


def test_a_row_both_runs_resolved_to_the_same_figure_is_an_agreement():
    other = [dict(CONTROL[0])]

    d = abcompare.compare(CONTROL, other)

    assert d["rows"][0]["agreement"] == "SAME_FIGURE"


def test_figures_that_differ_are_flagged_with_both_values():
    other = [dict(CONTROL[0], abstracts_numeric=6000)]

    row = abcompare.compare(CONTROL, other)["rows"][0]

    assert row["agreement"] == "DIFFERENT_FIGURE"
    assert row["control"] == 8719 and row["candidate"] == 6000


def test_a_figure_the_control_missed_is_credited_not_penalised():
    other = [dict(CONTROL[1], abstracts_numeric=1200, rung=4,
                  source_url="https://x/2", verdict="BORDERLINE")]

    row = abcompare.compare([CONTROL[1]], other)["rows"][0]

    assert row["agreement"] == "CANDIDATE_ONLY"


def test_a_row_the_candidate_never_returned_is_reported_as_missing():
    d = abcompare.compare(CONTROL, [dict(CONTROL[0])])

    assert d["missing"] == [2, 3]


def test_a_figure_without_a_source_url_is_a_violation():
    other = [dict(CONTROL[0], source_url=None)]

    v = abcompare.violations(other)

    assert any(x["kind"] == "FIGURE_WITHOUT_SOURCE" for x in v)


def test_a_figure_without_a_rung_is_a_violation():
    other = [dict(CONTROL[0], rung=None)]

    v = abcompare.violations(other)

    assert any(x["kind"] == "FIGURE_WITHOUT_RUNG" for x in v)


def test_an_out_verdict_with_no_figure_is_a_violation():
    """Absence of evidence recorded as evidence — the method forbids this."""
    other = [{"row": 9, "conference": "D", "abstracts_numeric": None, "rung": None,
              "source_url": None, "verdict": "OUT", "method": "found nothing"}]

    v = abcompare.violations(other)

    assert any(x["kind"] == "UNSOURCED_OUT" for x in v)


def test_naming_an_artefact_then_returning_unknown_is_a_violation():
    other = [{"row": 9, "conference": "D", "abstracts_numeric": None, "rung": None,
              "source_url": None, "verdict": "UNRESOLVED",
              "method": "The abstract book PDF is at example.org/book.pdf. NEXT: count it."}]

    v = abcompare.violations(other)

    assert any(x["kind"] == "ARTEFACT_NOT_COUNTED" for x in v)


def test_a_clean_run_produces_no_violations():
    assert abcompare.violations(CONTROL) == []


def test_summary_counts_resolved_rows_in_each_run():
    other = [dict(CONTROL[0]), dict(CONTROL[1]), dict(CONTROL[2], abstracts_numeric=None,
                                                      rung=None, source_url=None,
                                                      verdict="UNRESOLVED")]

    s = abcompare.compare(CONTROL, other)["summary"]

    assert s["control_resolved"] == 2
    assert s["candidate_resolved"] == 1


def test_an_out_justified_by_a_sourced_attendance_ceiling_is_not_a_violation():
    """A 127-attendee meeting cannot reach 900 at any ratio — that IS positive
    evidence of size, and the control run uses exactly this reasoning for GEADS."""
    run = [{"row": 707, "conference": "Winter School", "abstracts_numeric": None,
            "rung": None, "source_url": None, "verdict": "OUT",
            "attendance_numeric": 127,
            "attendance_source_url": "https://x/707",
            "method": "127 attendees, far below any ratio that reaches the floor"}]

    assert abcompare.violations(run) == []


def test_an_out_with_neither_a_figure_nor_a_sourced_attendance_is_still_a_violation():
    run = [{"row": 9, "conference": "D", "abstracts_numeric": None, "rung": None,
            "source_url": None, "verdict": "OUT", "attendance_numeric": None,
            "method": "found nothing"}]

    v = abcompare.violations(run)

    assert any(x["kind"] == "UNSOURCED_OUT" for x in v)


def test_an_attendance_ceiling_without_a_source_url_is_still_a_violation():
    run = [{"row": 9, "conference": "D", "abstracts_numeric": None, "rung": None,
            "source_url": None, "verdict": "OUT", "attendance_numeric": 127,
            "attendance_source_url": None, "method": "127 attendees"}]

    v = abcompare.violations(run)

    assert any(x["kind"] == "UNSOURCED_OUT" for x in v)


def test_an_artefact_blocked_by_a_wall_is_not_an_uncounted_artefact():
    """NEEDS_RUNG_5 is the correct outcome for a bot-walled artefact, not a failure."""
    run = [{"row": 20, "conference": "AIChE", "abstracts_numeric": None, "rung": None,
            "source_url": None, "verdict": "NEEDS_RUNG_5", "attendance_numeric": None,
            "method": "proceedings.aiche.org lists every paper but returns 403 behind a "
                      "Cloudflare wall. NEXT: open it in Playwright and count."}]

    assert not any(x["kind"] == "ARTEFACT_NOT_COUNTED" for x in abcompare.violations(run))
