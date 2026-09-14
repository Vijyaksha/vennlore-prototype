"""Tests for writeback — putting consolidated census results into the workbook.

Writes only to `Census - <Field>`, only the columns the method names, and never
destroys what a cell already held.
"""
import openpyxl
import pytest

import writeback


@pytest.fixture
def book(tmp_path):
    p = tmp_path / "wb.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Census - Chemistry"
    headers = ["Field", "Umbrella", "Society", "Country", "Conference", "Events/yr",
               "Abstracts (exact, as published)", "Abstr. yr", "Abstracts source (click)",
               "Attendance", "Attendance source (click)", "Venue", "Agent verdict", "Tier",
               "Include (1/0)", "SOM (1/0)", "US (1/0)", "Rev/yr @ $5k", "Notes",
               "Method", "Phase-2 priority", "Attendance basis", "Attendance rung + how",
               "Programme character", "Rupert's call"]
    for i, h in enumerate(headers, 1):
        ws.cell(4, i, h)
    ws.cell(5, 5, "Test Conference")
    ws.cell(5, 14, "NOT YET CENSUSED")
    wb.save(p)
    return p


def rec(**kw):
    base = dict(row=5, abstracts=1798, rung=3, year=2024,
                source_url="https://example.org/book", tier="VERIFIED",
                method="counted the abstract book", attendance=4000,
                attendance_source="https://example.org/news", character="CONTRIBUTED")
    base.update(kw)
    return base


def test_the_abstract_figure_and_its_year_and_source_are_written(book):
    writeback.apply([rec()], path=book)

    ws = openpyxl.load_workbook(book)["Census - Chemistry"]
    assert ws.cell(5, 7).value == 1798
    assert ws.cell(5, 8).value == 2024
    assert ws.cell(5, 9).value == "https://example.org/book"


def test_the_tier_replaces_not_yet_censused(book):
    writeback.apply([rec()], path=book)

    assert openpyxl.load_workbook(book)["Census - Chemistry"].cell(5, 14).value == "VERIFIED"


def test_the_method_names_the_rung_that_produced_the_figure(book):
    writeback.apply([rec()], path=book)

    method = openpyxl.load_workbook(book)["Census - Chemistry"].cell(5, 20).value
    assert "RUNG 3" in method
    assert "counted the abstract book" in method


def test_a_row_with_no_figure_says_no_rung_yielded(book):
    writeback.apply([rec(abstracts=None, rung=None, tier="BORDERLINE")], path=book)

    ws = openpyxl.load_workbook(book)["Census - Chemistry"]
    assert ws.cell(5, 7).value is None
    assert "NO RUNG YIELDED A FIGURE" in ws.cell(5, 20).value


def test_attendance_and_character_are_written(book):
    writeback.apply([rec()], path=book)

    ws = openpyxl.load_workbook(book)["Census - Chemistry"]
    assert ws.cell(5, 10).value == 4000
    assert ws.cell(5, 11).value == "https://example.org/news"
    assert ws.cell(5, 24).value == "CONTRIBUTED"


def test_existing_method_text_is_preserved_not_overwritten(book):
    wb = openpyxl.load_workbook(book)
    wb["Census - Chemistry"].cell(5, 20, "EARLIER NOTE")
    wb.save(book)

    writeback.apply([rec()], path=book)

    method = openpyxl.load_workbook(book)["Census - Chemistry"].cell(5, 20).value
    assert "EARLIER NOTE" in method


def test_a_disagreement_between_runs_is_recorded_in_the_method(book):
    writeback.apply([rec(disagreements=[{"run": "sliceB2", "abstracts_numeric": 318,
                                         "rung": 1}])], path=book)

    method = openpyxl.load_workbook(book)["Census - Chemistry"].cell(5, 20).value
    assert "DISAGREEMENT" in method and "318" in method


def test_a_figure_without_a_source_is_refused(book):
    with pytest.raises(ValueError, match="source"):
        writeback.apply([rec(source_url=None)], path=book)


def test_the_conference_name_is_verified_before_writing(book):
    """Row drift: agent row numbers go stale the instant a row moves."""
    with pytest.raises(ValueError, match="expected_name"):
        writeback.apply([rec(expected_name="A Different Conference")], path=book)


def test_a_matching_expected_name_writes_normally(book):
    writeback.apply([rec(expected_name="Test Conference")], path=book)

    assert openpyxl.load_workbook(book)["Census - Chemistry"].cell(5, 7).value == 1798


def test_events_per_yr_is_written_when_given(book):
    """Life sciences: the Events/yr column is blank on every row, so the writer must fill it."""
    writeback.apply([rec(events_per_yr=0.5)], path=book)

    assert openpyxl.load_workbook(book)["Census - Chemistry"].cell(5, 6).value == 0.5


def test_events_per_yr_is_left_alone_when_not_given(book):
    wb = openpyxl.load_workbook(book); wb["Census - Chemistry"].cell(5, 6, 1); wb.save(book)
    writeback.apply([rec()], path=book)

    assert openpyxl.load_workbook(book)["Census - Chemistry"].cell(5, 6).value == 1


# --- fill_blanks: add a missing figure without touching anything already written ---

def test_fill_blanks_writes_attendance_into_an_empty_cell(book):
    writeback.fill_blanks([dict(row=5, expected_name="Test Conference", attendance=15736,
                                attendance_source="https://example.org/a", note="restored")],
                          path=book)

    ws = openpyxl.load_workbook(book)["Census - Chemistry"]
    assert ws.cell(5, 10).value == 15736
    assert ws.cell(5, 11).value == "https://example.org/a"


def test_fill_blanks_never_overwrites_an_existing_value(book):
    wb = openpyxl.load_workbook(book)
    wb["Census - Chemistry"].cell(5, 10, 999)
    wb.save(book)

    writeback.fill_blanks([dict(row=5, expected_name="Test Conference", attendance=15736,
                                attendance_source="https://example.org/a", note="restored")],
                          path=book)

    assert openpyxl.load_workbook(book)["Census - Chemistry"].cell(5, 10).value == 999


def test_fill_blanks_refuses_a_figure_without_a_source(book):
    with pytest.raises(ValueError, match="source"):
        writeback.fill_blanks([dict(row=5, expected_name="Test Conference", attendance=15736,
                                    attendance_source=None, note="x")], path=book)


def test_fill_blanks_leaves_tier_untouched(book):
    writeback.fill_blanks([dict(row=5, expected_name="Test Conference", abstracts=12723, year=2025,
                                source_url="https://example.org/b", note="restored")], path=book)

    ws = openpyxl.load_workbook(book)["Census - Chemistry"]
    assert ws.cell(5, 7).value == 12723
    assert ws.cell(5, 14).value == "NOT YET CENSUSED"
