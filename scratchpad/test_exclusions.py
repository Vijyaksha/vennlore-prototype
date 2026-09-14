"""Tests for exclusions.py — the phase-1 exclusion list (every name already known)."""
import json
import openpyxl
import exclusions

HDR = ['Field', 'Umbrella', 'Society', 'Country', 'Conference', 'Events/yr',
       'Abstracts (exact, as published)', 'Abstr. yr', 'Abstracts source (click)', 'Attendance',
       'Attendance source (click)', 'Venue', 'Agent verdict', 'Tier']


def _wb(tmp_path):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    ws = wb.create_sheet('Census - X')
    ws.append(['Census — title']); ws.append(['blurb']); ws.append([])
    ws.append(HDR)
    ws.append(['X', 'CS / AI', 'Soc A', 'US', 'Conf A', 1, '1,234 papers', 2025, None, None, None, None, None, 'VERIFIED'])
    ws.append([None] * 4 + ['VERIFIED conferences >=1,500 abstracts — events/yr', 3.0])   # totals row
    ws.append(['X', 'CS / AI', None, 'JP', 'Conf B', None, None, None, None, None, None, None, None, 'NOT YET CENSUSED'])
    wd = wb.create_sheet('Deleted - X')
    wd.append(['Deleted - X']); wd.append(['blurb']); wd.append([])
    wd.append(HDR)
    wd.append(['X', 'eng', 'Soc C', 'DE', 'Conf C', None, '512', 2024, None, None, None, None, None, 'OUT'])
    ws2 = wb.create_sheet('Summary')
    ws2.append(['Conference']); ws2.append(['Not a census row'])
    p = tmp_path / 'wb.xlsx'
    wb.save(p)
    return p


def test_existing_names_lists_every_census_and_deleted_row_but_not_totals_or_other_sheets(tmp_path):
    rows = exclusions.existing_names(_wb(tmp_path))
    assert rows == [
        {'sheet': 'Census - X', 'society': 'Soc A', 'conference': 'Conf A', 'abstracts': '1,234 papers'},
        {'sheet': 'Census - X', 'society': None, 'conference': 'Conf B', 'abstracts': None},
        {'sheet': 'Deleted - X', 'society': 'Soc C', 'conference': 'Conf C', 'abstracts': '512'},
    ]


def test_crossref_titles_keeps_only_containers_at_or_above_the_floor_sorted_by_count(tmp_path):
    p = tmp_path / 'xr.json'
    p.write_text(json.dumps({'message': {'facets': {'container-title': {'values': {
        'Big Conf 2025': 950, 'Small Workshop': 120, 'Mid Conf': 300}}}}}))
    assert exclusions.crossref_titles(p, floor=300) == [('Big Conf 2025', 950), ('Mid Conf', 300)]
