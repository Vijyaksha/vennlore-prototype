"""Bring a parked row back from `Deleted - <field>` into a cleared row of `Census - <field>`, IN PLACE.

Rule 5 in reverse: nothing is inserted or deleted (openpyxl re-points no formulas), the census
row is filled where it was cleared, the deleted row is blanked, and the history travels in Method.
"""
import openpyxl

SHARED = 19            # census A-S map straight across to deleted A-S
CEN_METHOD = 20


def _headers(ws):
    return [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]


def _col_starting(headers, prefix):
    for i, h in enumerate(headers, 1):
        if h is not None and str(h).startswith(prefix):
            return i
    raise ValueError(f'no column header starting with {prefix!r}')


def restore_row(path, census, deleted, conference, dest_row, tier, note, today):
    wb = openpyxl.load_workbook(path)
    ws, wd = wb[census], wb[deleted]
    if ws.cell(dest_row, 5).value not in (None, ''):
        raise ValueError(f'census row {dest_row} is occupied by {ws.cell(dest_row, 5).value!r}')
    src = next((r for r in range(5, wd.max_row + 1)
                if str(wd.cell(r, 5).value or '').strip() == conference.strip()), None)
    if src is None:
        raise ValueError(f'{conference!r} is not on {deleted}')
    dh, ch = _headers(wd), _headers(ws)
    d_method, d_on, d_why = _col_starting(dh, 'Method'), dh.index('Deleted on') + 1, dh.index('Why deleted') + 1
    for c in range(1, SHARED + 1):
        ws.cell(dest_row, c).value = wd.cell(src, c).value
    for c, h in enumerate(dh, 1):                       # census-only columns parked as extras
        if c > SHARED and h and h in ch and not str(h).startswith('Method') and h not in ('Deleted on', 'Why deleted'):
            ws.cell(dest_row, ch.index(h) + 1).value = wd.cell(src, c).value
    ws.cell(dest_row, 14).value = tier
    ws.cell(dest_row, CEN_METHOD).value = (
        f"RESTORED FROM THE REMOVED LIST ({today}): {note}  ||  Previously deleted on {wd.cell(src, d_on).value} "
        f"because: {wd.cell(src, d_why).value}  ||  Prior method text follows.  ||  {wd.cell(src, d_method).value or ''}")
    for c in range(1, wd.max_column + 1):
        wd.cell(src, c).value = None
    wb.save(path)
    return {'from_deleted_row': src, 'to_census_row': dest_row}
