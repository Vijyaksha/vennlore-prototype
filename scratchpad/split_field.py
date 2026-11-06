"""Split one `Census - <field>` / `Deleted - <field>` sheet pair into two pairs by a row rule.

Rows are NOT moved: each new sheet is a full copy of the source with the other group's rows
blanked, so every totals formula (fixed ranges, e.g. N5:N469) still covers exactly the rows it
did before and nothing shifts. openpyxl re-points no formulas — this is the only safe way.
"""
import openpyxl

HEADER_ROW = 4
COL_FIELD, COL_UMBRELLA, COL_CONF = 1, 2, 5


def _data_rows(ws):
    """(row_index, umbrella) for every candidate row — totals rows carry only Conference + figure."""
    out = []
    for r in range(HEADER_ROW + 1, ws.max_row + 1):
        if ws.cell(r, COL_CONF).value is None:
            continue
        others = [ws.cell(r, c).value for c in range(1, ws.max_column + 1) if c not in (COL_CONF, COL_CONF + 1)]
        if all(v is None for v in others):
            continue
        out.append((r, ws.cell(r, COL_UMBRELLA).value))
    return out


def split_field(path, src_field, rule, field_a, field_b):
    """rule(umbrella) -> True keeps the row on `field_a`, False on `field_b`.

    Returns {field: {'census': n, 'deleted': n}}. Refuses (ValueError, file untouched) when
    either side would receive no census rows.
    """
    wb = openpyxl.load_workbook(path)
    plan = {}
    for kind in ('Census', 'Deleted'):
        src = wb[f'{kind} - {src_field}']
        plan[kind] = [(r, bool(rule(u))) for r, u in _data_rows(src)]
    for side, field in ((True, field_a), (False, field_b)):
        if not any(s == side for _, s in plan['Census']):
            raise ValueError(f'rule sends no census rows to {field}; refusing to split')

    counts = {field_a: {'census': 0, 'deleted': 0}, field_b: {'census': 0, 'deleted': 0}}
    for kind in ('Census', 'Deleted'):
        src = wb[f'{kind} - {src_field}']
        for side, field in ((True, field_a), (False, field_b)):
            ws = wb.copy_worksheet(src)
            ws.title = f'{kind} - {field}'
            ws['A1'].value = str(src['A1'].value or '').replace(src_field, field)
            for r, s in plan[kind]:
                if s == side:
                    ws.cell(r, COL_FIELD).value = field
                    counts[field][kind.lower()] += 1
                else:
                    for c in range(1, ws.max_column + 1):
                        ws.cell(r, c).value = None
        del wb[src.title]
    wb.save(path)
    return counts
