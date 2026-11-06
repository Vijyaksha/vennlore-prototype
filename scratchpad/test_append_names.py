"""Tests for append_names.py — load phase-1 names onto an existing census sheet as NOT YET CENSUSED."""
import openpyxl
import pytest
import chemlib
import append_names

NAMES = [
    {'conference': 'TRB Annual Meeting', 'society': 'Transportation Research Board', 'country_or_region': 'US',
     'subfield': 'transportation', 'frequency_note': 'annual', 'why_plausibly_900': 'thousands of presentations',
     'size_hint': 'over 5,000 presentations', 'size_hint_url': 'https://trb.org/x', 'source_url': 'https://trb.org/'},
    {'conference': 'JSCE Annual Meeting', 'society': 'JSCE', 'country_or_region': 'Japan', 'subfield': 'civil',
     'implied': True, 'boundary': True, 'source_url': 'https://jsce.or.jp/'},
]


def _wb(tmp_path, headroom=400):
    p = tmp_path / 'wb.xlsx'
    openpyxl.Workbook().save(p)
    chemlib.HEADROOM = headroom
    chemlib.build_field([{'conference': 'Existing Conf', 'subfield': 'x', 'society': 's', 'country_or_region': 'US'}],
                        [], 'Engineering', path=p)
    return p


def test_append_writes_names_after_the_last_row_with_tier_us_flag_and_notes(tmp_path):
    p = _wb(tmp_path)
    out = append_names.append_names(p, 'Census - Engineering', 'Engineering', NAMES, today='2026-09-14')
    assert out == {'first_row': 6, 'last_row': 7, 'appended': 2, 'skipped': []}
    ws = openpyxl.load_workbook(p)['Census - Engineering']
    r6 = [ws.cell(6, c).value for c in range(1, 20)]
    assert r6[:5] == ['Engineering', 'transportation', 'Transportation Research Board', 'US', 'TRB Annual Meeting']
    assert r6[13] == 'NOT YET CENSUSED' and (r6[14], r6[15], r6[16]) == (0, 0, 1)
    assert 'over 5,000 presentations' in r6[18] and 'https://trb.org/x' in r6[18] and '2026-09-14' in r6[18]
    r7 = [ws.cell(7, c).value for c in range(1, 20)]
    assert r7[4] == 'JSCE Annual Meeting' and r7[16] == 0
    assert r7[18].startswith('IMPLIED NAME') and 'BOUNDARY' in r7[18]
    assert ws.cell(8, 5).value is None


def test_append_skips_names_already_on_the_sheet(tmp_path):
    p = _wb(tmp_path)
    out = append_names.append_names(p, 'Census - Engineering', 'Engineering',
                                    [{'conference': 'Existing Conf'}] + NAMES[:1], today='2026-09-14')
    assert out['appended'] == 1 and out['skipped'] == ['Existing Conf']


def test_append_refuses_to_run_past_the_totals_range(tmp_path):
    p = _wb(tmp_path, headroom=1)          # totals range ends at row 6; three names would reach row 8
    before = openpyxl.load_workbook(p)['Census - Engineering'].cell(6, 5).value
    with pytest.raises(ValueError, match='totals range'):
        append_names.append_names(p, 'Census - Engineering', 'Engineering', NAMES + [{'conference': 'Third'}], today='2026-09-14')
    assert openpyxl.load_workbook(p)['Census - Engineering'].cell(6, 5).value == before
