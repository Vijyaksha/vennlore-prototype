"""Tests for restore.py — bring a parked row back from `Deleted - <field>` into a cleared census row, in place."""
import openpyxl
import pytest
import chemlib
import dedupe
import restore


def _wb(tmp_path):
    p = tmp_path / 'wb.xlsx'
    openpyxl.Workbook().save(p)
    chemlib.build_field([{'conference': 'Keep', 'subfield': 'x', 'society': 's', 'country_or_region': 'US'},
                         {'conference': 'Parked', 'subfield': 'mech', 'society': 'JSME', 'country_or_region': 'Japan'},
                         {'conference': 'Also keep', 'subfield': 'x', 'society': 's', 'country_or_region': 'US'}],
                        [], 'Engineering', path=p)
    wb = openpyxl.load_workbook(p)
    ws = wb['Census - Engineering']
    ws['G6'].value, ws['N6'].value, ws['T6'].value = '741 papers', 'OUT', 'RUNG 4 — j-stage count'
    wb.save(p)
    dedupe.move_to_deleted([dict(row=6, expected_name='Parked', why='OUT on positive evidence: 741')], path=p,
                           today='2026-09-14', census='Census - Engineering', deleted='Deleted - Engineering')
    return p


def test_restore_copies_the_row_back_into_the_cleared_census_row_and_blanks_the_deleted_row(tmp_path):
    p = _wb(tmp_path)
    out = restore.restore_row(p, 'Census - Engineering', 'Deleted - Engineering', 'Parked', dest_row=6,
                              tier='BORDERLINE', note='RESTORED: Confit shows 1,252', today='2026-09-14')
    assert out == {'from_deleted_row': 5, 'to_census_row': 6}
    wb = openpyxl.load_workbook(p)
    ws, wd = wb['Census - Engineering'], wb['Deleted - Engineering']
    assert [ws.cell(6, c).value for c in (1, 2, 3, 4, 5)] == ['Engineering', 'mech', 'JSME', 'Japan', 'Parked']
    assert ws['N6'].value == 'BORDERLINE' and ws['G6'].value == '741 papers'
    assert ws['T6'].value.startswith('RESTORED FROM THE REMOVED LIST (2026-09-14)') and 'Confit shows 1,252' in ws['T6'].value \
        and 'j-stage count' in ws['T6'].value and 'OUT on positive evidence: 741' in ws['T6'].value
    assert all(wd.cell(5, c).value is None for c in range(1, wd.max_column + 1))     # blanked in place, not deleted
    assert ws['E5'].value == 'Keep' and ws['E7'].value == 'Also keep'                  # nothing shifted


def test_restore_refuses_an_occupied_destination_or_a_missing_parked_row(tmp_path):
    p = _wb(tmp_path)
    with pytest.raises(ValueError, match='occupied'):
        restore.restore_row(p, 'Census - Engineering', 'Deleted - Engineering', 'Parked', dest_row=5,
                            tier='BORDERLINE', note='x', today='2026-09-14')
    with pytest.raises(ValueError, match='not on'):
        restore.restore_row(p, 'Census - Engineering', 'Deleted - Engineering', 'Nope', dest_row=6,
                            tier='BORDERLINE', note='x', today='2026-09-14')
