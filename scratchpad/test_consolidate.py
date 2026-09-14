"""Tests for consolidate — picking the best result per conference across runs.

Seven runs researched the same 49 conferences from different angles. Where they
disagree the method decides, not recency and not the model that produced it:
a COUNTED artefact (rungs 3-6) outranks a STATED figure (rungs 1, 2, 7, 8), which
outranks an INFERRED one (rung 9). Within the same class, prefer the later edition.
"""
import consolidate


def r(**kw):
    base = dict(conference="X", abstracts_numeric=None, rung=None, year=None,
                source_url=None, verdict=None, method="", run="test")
    base.update(kw)
    return base


def test_a_counted_figure_beats_a_stated_one_even_if_the_stated_one_is_newer():
    counted = r(abstracts_numeric=291, rung=3, year=2025, source_url="https://a")
    stated = r(abstracts_numeric=318, rung=1, year=2025, source_url="https://b")

    assert consolidate.best([stated, counted])["abstracts_numeric"] == 291


def test_a_stated_figure_beats_an_inferred_one():
    stated = r(abstracts_numeric=800, rung=8, source_url="https://a")
    inferred = r(abstracts_numeric=1050, rung=9, source_url="https://b")

    assert consolidate.best([inferred, stated])["abstracts_numeric"] == 800


def test_among_two_counted_figures_the_later_edition_wins():
    old = r(abstracts_numeric=1107, rung=4, year=2012, source_url="https://a")
    new = r(abstracts_numeric=1482, rung=4, year=2015, source_url="https://b")

    assert consolidate.best([old, new])["abstracts_numeric"] == 1482


def test_a_figure_always_beats_no_figure():
    empty = r(verdict="UNRESOLVED")
    figure = r(abstracts_numeric=612, rung=5, source_url="https://a")

    assert consolidate.best([empty, figure])["abstracts_numeric"] == 612


def test_a_figure_with_no_source_url_is_never_chosen():
    """Rule 2 — an unsourced number must not reach the workbook."""
    unsourced = r(abstracts_numeric=9999, rung=3, source_url=None)
    sourced = r(abstracts_numeric=612, rung=5, source_url="https://a")

    assert consolidate.best([unsourced, sourced])["abstracts_numeric"] == 612


def test_when_every_candidate_is_unresolved_the_richest_record_is_kept():
    """A NEEDS_RUNG_5 row naming its artefact is more useful than a bare UNKNOWN."""
    bare = r(verdict="UNRESOLVED", method="nothing found")
    named = r(verdict="NEEDS_RUNG_5", method="artefact is at X; NEXT: open in Playwright")

    assert consolidate.best([bare, named])["verdict"] == "NEEDS_RUNG_5"


def test_the_winning_record_records_which_run_produced_it():
    a = r(abstracts_numeric=291, rung=3, source_url="https://a", run="pilot2")

    assert consolidate.best([a])["run"] == "pilot2"


def test_disagreements_between_runs_are_reported_not_silently_dropped():
    counted = r(abstracts_numeric=291, rung=3, source_url="https://a", run="pilot2")
    stated = r(abstracts_numeric=318, rung=1, source_url="https://b", run="sliceB2")

    w = consolidate.best([stated, counted])

    assert w["disagreements"] == [{"run": "sliceB2", "abstracts_numeric": 318, "rung": 1}]


def test_agreeing_runs_are_not_listed_as_disagreements():
    a = r(abstracts_numeric=291, rung=3, source_url="https://a", run="pilot2")
    b = r(abstracts_numeric=291, rung=3, source_url="https://b", run="sliceB2")

    assert consolidate.best([a, b])["disagreements"] == []


def test_tier_follows_the_bar_and_the_900_floor():
    assert consolidate.tier(8719) == "VERIFIED"
    assert consolidate.tier(1500) == "VERIFIED"
    assert consolidate.tier(1482) == "BORDERLINE"
    assert consolidate.tier(900) == "BORDERLINE"
    assert consolidate.tier(291) == "OUT"


def test_a_row_with_no_figure_is_never_tiered_out():
    """Rule 1 — absence of evidence is never evidence of a small meeting."""
    assert consolidate.tier(None) == "BORDERLINE"


def test_an_inferred_figure_never_reaches_verified():
    """Rung 9 figures are BORDERLINE at best — nothing was counted for them."""
    assert consolidate.tier(2000, rung=9) == "BORDERLINE"


# --- Rupert, 2026-09-12: the within-100 leeway applies to COUNTED figures too ---

def test_a_counted_figure_within_100_of_the_floor_is_borderline():
    assert consolidate.tier(855, rung=3) == "BORDERLINE"   # EUROCORR
    assert consolidate.tier(801, rung=3) == "BORDERLINE"   # MACRO 2024


def test_a_counted_figure_exactly_800_is_borderline():
    assert consolidate.tier(800, rung=4) == "BORDERLINE"


def test_a_counted_figure_below_800_is_out():
    assert consolidate.tier(789, rung=3) == "OUT"          # WATOC 2025


def test_an_inferred_figure_within_100_is_also_borderline():
    assert consolidate.tier(850, rung=9) == "BORDERLINE"
