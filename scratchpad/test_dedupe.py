"""Tests for dedupe.move_to_deleted — moving duplicate rows off a census sheet.

Rule 5: a removed row is parked on `Deleted - <Field>`, never erased, with its
evidence intact and the reason recorded, so it can be restored by re-reading.
"""
import openpyxl
import pytest

import dedupe

CENSUS_HEADERS = ["Field", "Umbrella", "Society", "Country", "Conference", "Events/yr",
                  "Abstracts (exact, as published)", "Abstr. yr", "Abstracts source (click)",
                  "Attendance", "Attendance source (click)", "Venue", "Agent verdict", "Tier",
                  "Include (1/0)", "SOM (1/0)", "US (1/0)", "Rev/yr @ $5k", "Notes", "Method",
                  "Phase-2 priority", "Attendance basis", "Attendance rung + how",
                  "Programme character", "Rupert's call", "Language group"]
DELETED_HEADERS = CENSUS_HEADERS[:19] + ["Deleted on", "Why deleted", "Method"]


@pytest.fixture
def book(tmp_path):
    p = tmp_path / "wb.xlsx"
    wb = openpyxl.Workbook()
    cs = wb.active
    cs.title = "Census - Chemistry"
    ds = wb.create_sheet("Deleted - Chemistry")
    for i, h in enumerate(CENSUS_HEADERS, 1):
        cs.cell(4, i, h)
    for i, h in enumerate(DELETED_HEADERS, 1):
        ds.cell(4, i, h)
    ds.cell(5, 5, "Already deleted conference")
    for r, name in ((6, "EUROCORR"), (7, "EUROCORR — European Corrosion Congress")):
        cs.cell(r, 5, name)
        cs.cell(r, 7, 855)
        cs.cell(r, 14, "BORDERLINE")
        cs.cell(r, 20, "RUNG 3 — counted the programme")
        cs.cell(r, 24, "CONTRIBUTED")
        cs.cell(r, 26, "ENGLISH")
    wb.save(p)
    return p


def test_a_moved_row_is_appended_below_the_existing_deleted_rows(book):
    dedupe.move_to_deleted([{"row": 7, "expected_name": "EUROCORR — European Corrosion Congress",
                             "why": "duplicate of row 6"}], path=book, today="2026-09-12")

    ds = openpyxl.load_workbook(book)["Deleted - Chemistry"]
    assert ds.cell(5, 5).value == "Already deleted conference"
    assert ds.cell(6, 5).value == "EUROCORR — European Corrosion Congress"


def test_the_evidence_travels_with_the_row(book):
    dedupe.move_to_deleted([{"row": 7, "expected_name": "EUROCORR — European Corrosion Congress",
                             "why": "duplicate of row 6"}], path=book, today="2026-09-12")

    ds = openpyxl.load_workbook(book)["Deleted - Chemistry"]
    assert ds.cell(6, 7).value == 855
    assert ds.cell(6, 14).value == "BORDERLINE"
    assert ds.cell(6, 22).value == "RUNG 3 — counted the programme"   # census T -> deleted V


def test_the_deletion_date_and_reason_are_recorded(book):
    dedupe.move_to_deleted([{"row": 7, "expected_name": "EUROCORR — European Corrosion Congress",
                             "why": "duplicate of row 6"}], path=book, today="2026-09-12")

    ds = openpyxl.load_workbook(book)["Deleted - Chemistry"]
    assert ds.cell(6, 20).value == "2026-09-12"
    assert ds.cell(6, 21).value == "duplicate of row 6"


def test_census_only_columns_are_kept_after_the_deleted_columns(book):
    dedupe.move_to_deleted([{"row": 7, "expected_name": "EUROCORR — European Corrosion Congress",
                             "why": "duplicate of row 6"}], path=book, today="2026-09-12")

    ds = openpyxl.load_workbook(book)["Deleted - Chemistry"]
    headers = [ds.cell(4, c).value for c in range(1, ds.max_column + 1)]
    col = headers.index("Programme character") + 1
    assert ds.cell(6, col).value == "CONTRIBUTED"


def test_the_census_row_is_cleared(book):
    dedupe.move_to_deleted([{"row": 7, "expected_name": "EUROCORR — European Corrosion Congress",
                             "why": "duplicate of row 6"}], path=book, today="2026-09-12")

    cs = openpyxl.load_workbook(book)["Census - Chemistry"]
    assert all(cs.cell(7, c).value is None for c in range(1, 27))
    assert cs.cell(6, 5).value == "EUROCORR"          # the survivor is untouched


def test_a_row_whose_name_has_drifted_is_refused(book):
    with pytest.raises(ValueError, match="expected_name"):
        dedupe.move_to_deleted([{"row": 7, "expected_name": "Something Else", "why": "x"}],
                               path=book, today="2026-09-12")


def test_a_refused_batch_changes_nothing(book):
    """All-or-nothing: a bad record must not leave half the batch applied."""
    with pytest.raises(ValueError):
        dedupe.move_to_deleted([
            {"row": 6, "expected_name": "EUROCORR", "why": "x"},
            {"row": 7, "expected_name": "Wrong name", "why": "y"},
        ], path=book, today="2026-09-12")

    cs = openpyxl.load_workbook(book)["Census - Chemistry"]
    assert cs.cell(6, 5).value == "EUROCORR"


def test_the_real_long_method_header_is_recognised(tmp_path):
    """The live sheets title the column 'Method — which escalation-ladder rung ...'."""
    long_h = "Method — which escalation-ladder rung produced the number, and exactly how"
    p = tmp_path / "wb.xlsx"
    wb = openpyxl.Workbook()
    cs = wb.active
    cs.title = "Census - Chemistry"
    ds = wb.create_sheet("Deleted - Chemistry")
    for i, h in enumerate([long_h if h == "Method" else h for h in CENSUS_HEADERS], 1):
        cs.cell(4, i, h)
    for i, h in enumerate([long_h if h == "Method" else h for h in DELETED_HEADERS], 1):
        ds.cell(4, i, h)
    cs.cell(5, 5, "X")
    cs.cell(5, 20, "RUNG 4 — the evidence")
    wb.save(p)

    dedupe.move_to_deleted([{"row": 5, "expected_name": "X", "why": "dup"}], path=p, today="2026-09-12")

    assert openpyxl.load_workbook(p)["Deleted - Chemistry"].cell(5, 22).value == "RUNG 4 — the evidence"
