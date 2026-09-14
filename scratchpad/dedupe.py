"""Move duplicate rows from `Census - <Field>` to `Deleted - <Field>`.

Rule 5: a removed row is parked, never erased. Its evidence travels with it, the
date and reason are recorded, and the census row is cleared in place (never deleted,
so no formula range shifts). The batch is all-or-nothing: every record's name is
checked against the sheet before anything is written.
"""
import openpyxl

import attlib

CENSUS = "Census - Chemistry"
DELETED = "Deleted - Chemistry"
N_CENSUS_COLS = 26
SHARED = 19            # census A-S map straight across to deleted A-S


def _headers(ws):
    return [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]


def _col_starting(headers, prefix):
    """1-based index of the first header starting with `prefix` (live headers are long)."""
    for i, h in enumerate(headers, 1):
        if h is not None and str(h).startswith(prefix):
            return i
    raise ValueError(f"no column header starting with {prefix!r}")


def _next_free_row(ws):
    last = 4
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 5).value not in (None, ""):
            last = r
    return last + 1


def move_to_deleted(records, path=None, today=None, census=CENSUS, deleted=DELETED):
    path = path or attlib.WB
    wb = openpyxl.load_workbook(path)
    cs, ds = wb[census], wb[deleted]

    for rec in records:                                   # validate the whole batch first
        actual = (cs.cell(rec["row"], 5).value or "").strip()
        if actual != (rec["expected_name"] or "").strip():
            raise ValueError(f"expected_name mismatch at row {rec['row']}: "
                             f"sheet {actual!r} vs record {rec['expected_name']!r}")

    census_h = [cs.cell(4, c).value for c in range(1, N_CENSUS_COLS + 1)]
    deleted_h = _headers(ds)
    method_col = _col_starting(deleted_h, "Method")
    census_method = _col_starting(census_h, "Method")
    extra = {}                                            # census-only columns -> deleted column
    for c, h in enumerate(census_h, 1):
        if c <= SHARED or h is None or str(h).startswith("Method"):
            continue
        if h not in deleted_h:
            deleted_h.append(h)
            ds.cell(4, len(deleted_h), h)
        extra[c] = deleted_h.index(h) + 1

    out = _next_free_row(ds)
    for rec in records:
        r = rec["row"]
        vals = [cs.cell(r, c).value for c in range(1, N_CENSUS_COLS + 1)]
        for c in range(1, SHARED + 1):
            ds.cell(out, c, vals[c - 1])
        ds.cell(out, 20, today)
        ds.cell(out, 21, rec["why"])
        ds.cell(out, method_col, vals[census_method - 1])
        for c, dc in extra.items():
            ds.cell(out, dc, vals[c - 1])
        for c in range(1, N_CENSUS_COLS + 1):
            cs.cell(r, c).value = None
        out += 1

    wb.save(path)
    return len(records)
