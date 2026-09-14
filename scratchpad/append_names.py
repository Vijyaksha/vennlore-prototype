"""Append phase-1 candidate names to an EXISTING `Census - <field>` sheet as NOT YET CENSUSED.

Rows land after the last used Conference cell, inside the totals range (parsed from the first
totals formula, e.g. N5:N469), so the fixed-range formulas keep counting them. openpyxl re-points
nothing: a row past the range end would count for nothing, silently — so that is refused.
"""
import re
import openpyxl

COL_CONF, COL_TIER, COL_INCLUDE, COL_SOM, COL_US, COL_NOTES = 5, 14, 15, 16, 17, 19
US_LABELS = ('US', 'USA', 'United States')


def _range_end(ws):
    for r in range(5, ws.max_row + 1):
        v = ws.cell(r, 6).value
        if isinstance(v, str) and v.startswith('=SUMPRODUCT'):
            return int(re.search(r'N5:N(\d+)', v).group(1))
    raise ValueError('no totals formula found on the sheet')


def _note(n, today):
    parts = []
    if n.get('implied'):
        parts.append('IMPLIED NAME — the society or group is confirmed but this meeting title was never '
                     'verified. Phase 2 must resolve it to a real name or drop the row.')
    if n.get('boundary'):
        parts.append('BOUNDARY — flagged by phase 1 as sitting between fields; judge on contributed science.')
    for k in ('frequency_note', 'why_plausibly_900', 'why_listed'):
        if n.get(k):
            parts.append(str(n[k]))
    if n.get('size_hint'):
        parts.append(f"Phase-1 size hint (page opened, not a figure): {n['size_hint']} — {n.get('size_hint_url') or 'no URL'}")
    if n.get('source_url'):
        parts.append(f"Phase 1 source: {n['source_url']}")
    parts.append(f'Phase 1 second pass, loaded {today}')
    return ' | '.join(parts)


def append_names(path, sheet, field, names, today):
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet]
    end = _range_end(ws)
    existing = {str(ws.cell(r, COL_CONF).value).strip() for r in range(5, end + 1) if ws.cell(r, COL_CONF).value}
    last = max((r for r in range(5, end + 1) if ws.cell(r, COL_CONF).value), default=4)
    todo = [n for n in names if n['conference'].strip() not in existing]
    skipped = [n['conference'] for n in names if n['conference'].strip() in existing]
    if last + len(todo) > end:
        raise ValueError(f'{len(todo)} rows from row {last + 1} would pass the totals range end ({end}); widen the totals first')
    row = last + 1
    for n in todo:
        ws.cell(row, 1).value = field
        ws.cell(row, 2).value = n.get('subfield')
        ws.cell(row, 3).value = n.get('society')
        ws.cell(row, 4).value = n.get('country_or_region')
        ws.cell(row, COL_CONF).value = n['conference']
        ws.cell(row, COL_TIER).value = 'NOT YET CENSUSED'
        ws.cell(row, COL_INCLUDE).value = 0
        ws.cell(row, COL_SOM).value = 0
        ws.cell(row, COL_US).value = 1 if str(n.get('country_or_region') or '').strip() in US_LABELS else 0
        ws.cell(row, COL_NOTES).value = _note(n, today)
        row += 1
    wb.save(path)
    return {'first_row': last + 1, 'last_row': row - 1, 'appended': len(todo), 'skipped': skipped}
