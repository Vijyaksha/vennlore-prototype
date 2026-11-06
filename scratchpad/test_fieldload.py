"""Tests for fieldload: phase-1 record mapping and cross-field row moves."""
import openpyxl
import pytest

import chemlib
import fieldload


# ---------- to_build_records ----------

def test_to_build_records_composes_why_listed():
    recs = fieldload.to_build_records([{
        'conference': 'AERA Annual Meeting',
        'society': 'American Educational Research Association',
        'country_or_region': 'US',
        'subfield': 'education research',
        'frequency_note': 'annual',
        'why_plausibly_900': 'largest education research meeting',
        'size_hint': '4,676 papers in Crossref 2025',
        'size_hint_url': 'https://example.org/hint',
        'source_url': 'https://www.aera.net/x',
        'boundary': False,
        'implied': False,
    }])
    assert len(recs) == 1
    r = recs[0]
    assert r['conference'] == 'AERA Annual Meeting'
    assert r['society'] == 'American Educational Research Association'
    assert r['country_or_region'] == 'US'
    assert r['subfield'] == 'education research'
    assert r['frequency_note'] == 'annual'
    assert r['source_url'] == 'https://www.aera.net/x'
    assert r['implied'] is False
    assert 'largest education research meeting' in r['why_listed']
    assert 'SIZE HINT: 4,676 papers in Crossref 2025 (https://example.org/hint)' in r['why_listed']
    assert 'BOUNDARY' not in r['why_listed']


def test_to_build_records_flags_boundary_and_survives_missing_fields():
    recs = fieldload.to_build_records([{
        'conference': 'X',
        'society': 'Y',
        'why_plausibly_900': 'reason',
        'boundary': True,
        'implied': True,
    }])
    r = recs[0]
    assert r['why_listed'].startswith('BOUNDARY (may belong to another field)')
    assert 'reason' in r['why_listed']
    assert 'SIZE HINT' not in r['why_listed']
    assert r['implied'] is True


# ---------- first_free_row / move_row ----------

NAMES_A = [{'conference': 'Conf A1', 'society': 'Soc A1'},
           {'conference': 'Conf A2', 'society': 'Soc A2'}]
NAMES_B = [{'conference': 'Conf B1', 'society': 'Soc B1'}]


@pytest.fixture
def wb_path(tmp_path):
    p = str(tmp_path / 'wb.xlsx')
    openpyxl.Workbook().save(p)
    chemlib.build_field(NAMES_A, [], 'FieldA', path=p)
    chemlib.build_field(NAMES_B, [], 'FieldB', path=p)
    # give FieldA row 5 a counted figure so the move carries real data
    wb = openpyxl.load_workbook(p)
    ws = wb['Census - FieldA']
    ws.cell(5, 6).value = 1
    ws.cell(5, 7).value = '2,976 contributed presentations (2025)'
    ws.cell(5, 8).value = 2025
    ws.cell(5, 14).value = 'VERIFIED'
    ws.cell(5, 20).value = 'RUNG 3 — counted'
    wb.save(p)
    return p


def test_first_free_row_is_after_last_name(wb_path):
    wb = openpyxl.load_workbook(wb_path)
    assert fieldload.first_free_row(wb['Census - FieldA']) == 7
    assert fieldload.first_free_row(wb['Census - FieldB']) == 6


def test_move_row_copies_data_blanks_source_and_lands_in_totals_range(wb_path):
    wb = openpyxl.load_workbook(wb_path)
    dst_row = fieldload.move_row(wb, 'Census - FieldA', 5, 'Census - FieldB', 'FieldB')
    assert dst_row == 6
    dst = wb['Census - FieldB']
    assert dst.cell(dst_row, 1).value == 'FieldB'          # field rewritten
    assert dst.cell(dst_row, 5).value == 'Conf A1'
    assert dst.cell(dst_row, 7).value == '2,976 contributed presentations (2025)'
    assert dst.cell(dst_row, 14).value == 'VERIFIED'
    assert dst.cell(dst_row, 20).value == 'RUNG 3 — counted'
    src = wb['Census - FieldA']
    assert all(src.cell(5, c).value is None for c in range(1, 26))  # blanked in place
    # inside the destination totals range
    end = fieldload.totals_range_end(dst)
    assert dst_row <= end


def test_move_row_refuses_row_outside_totals_range(wb_path):
    wb = openpyxl.load_workbook(wb_path)
    dst = wb['Census - FieldB']
    end = fieldload.totals_range_end(dst)
    # fill every row of the range so the next free row falls outside it
    for r in range(5, end + 1):
        dst.cell(r, 5).value = f'filler {r}'
    with pytest.raises(ValueError):
        fieldload.move_row(wb, 'Census - FieldA', 5, 'Census - FieldB', 'FieldB')


def test_totals_range_end_reads_formula(wb_path):
    wb = openpyxl.load_workbook(wb_path)
    # NAMES_B has 1 name -> last row 5, end = 5 + HEADROOM
    assert fieldload.totals_range_end(wb['Census - FieldB']) == 5 + chemlib.HEADROOM
