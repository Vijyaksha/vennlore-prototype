"""Load a phase-1 field onto the workbook and move rows between field sheets.

`to_build_records` shapes phase-1 names.json records for chemlib.build_field
(why_listed composed from why_plausibly_900 + size_hint + boundary, per HANDOFF).
`move_row` moves one census row to another field's census sheet: cell copy of
cols 1-25 with Field rewritten, source row blanked IN PLACE (never deleted —
openpyxl re-points no formulas), destination row kept inside the totals range.
"""
import re

N_COLS = 25


def to_build_records(p1_records):
    out = []
    for n in p1_records:
        parts = []
        if n.get('boundary'):
            parts.append('BOUNDARY (may belong to another field)')
        if n.get('why_plausibly_900'):
            parts.append(str(n['why_plausibly_900']))
        if n.get('size_hint'):
            hint = f"SIZE HINT: {n['size_hint']}"
            if n.get('size_hint_url'):
                hint += f" ({n['size_hint_url']})"
            parts.append(hint)
        out.append({
            'conference': n.get('conference'),
            'society': n.get('society'),
            'country_or_region': n.get('country_or_region'),
            'subfield': n.get('subfield'),
            'frequency_note': n.get('frequency_note'),
            'source_url': n.get('source_url'),
            'implied': bool(n.get('implied')),
            'why_listed': ' | '.join(parts),
        })
    return out


def first_free_row(ws):
    r = 5
    while ws.cell(r, 5).value is not None:
        r += 1
    return r


def totals_range_end(ws):
    """Read the fixed range end out of the totals block's own formula."""
    r = first_free_row(ws)
    while r <= ws.max_row + 2:
        v = ws.cell(r, 6).value
        if isinstance(v, str) and v.startswith('='):
            m = re.search(r'N5:N(\d+)', v)
            if m:
                return int(m.group(1))
        r += 1
    raise ValueError('no totals formula found')


def move_row(wb, src_sheet, src_row, dst_sheet, dst_field):
    src, dst = wb[src_sheet], wb[dst_sheet]
    dst_row = first_free_row(dst)
    if dst_row > totals_range_end(dst):
        raise ValueError(f'{dst_sheet}: row {dst_row} falls outside the totals range')
    for c in range(1, N_COLS + 1):
        dst.cell(dst_row, c).value = src.cell(src_row, c).value
    dst.cell(dst_row, 1).value = dst_field
    for c in range(1, N_COLS + 1):
        src.cell(src_row, c).value = None
    return dst_row
