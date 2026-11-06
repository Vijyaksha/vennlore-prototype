"""Write consolidated census results into `Census - <Field>`.

Writes only the columns the method names, never destroys existing cell text, and
refuses anything the method forbids: a figure with no exact-page URL (rule 2), or
a row whose conference name no longer matches (row drift — agent row numbers go
stale the instant a row moves).
"""
import openpyxl

import attlib

SHEET = "Census - Chemistry"

COL = {"events": 6, "abstracts": 7, "year": 8, "source": 9, "attendance": 10,
       "attendance_source": 11, "tier": 14, "method": 20, "character": 24}


def _method_text(r):
    parts = []
    if r.get("abstracts") is not None:
        parts.append(f"RUNG {r['rung']} — {r.get('method') or ''}".strip())
    else:
        reached = r.get("rung") or "n"
        parts.append(f"NO RUNG YIELDED A FIGURE — highest rung reached: {reached}. "
                     f"{r.get('method') or ''}".strip())
    for d in r.get("disagreements") or []:
        parts.append(
            f"DISAGREEMENT — run '{d.get('run')}' returned {d.get('abstracts_numeric')} "
            f"at rung {d.get('rung')}; the counted figure above was preferred per the "
            f"method (a counted artefact outranks a stated total, and stated totals "
            f"routinely include invited speakers). Both are recorded, neither averaged."
        )
    return "  ".join(p for p in parts if p)


def apply(records, path=None, sheet=SHEET):
    path = path or attlib.WB
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet]

    for r in records:
        if r.get("abstracts") is not None and not r.get("source_url"):
            raise ValueError(f"a figure needs a source URL: row {r.get('row')}")
        row = r["row"]
        expected = r.get("expected_name")
        if expected is not None and (ws.cell(row, 5).value or "").strip() != expected.strip():
            raise ValueError(
                f"expected_name mismatch at row {row}: sheet says "
                f"{ws.cell(row, 5).value!r}, record says {expected!r}")

        if r.get("abstracts") is not None:
            ws.cell(row, COL["abstracts"], r["abstracts"])
            if r.get("year"):
                ws.cell(row, COL["year"], r["year"])
            ws.cell(row, COL["source"], r["source_url"])
        if r.get("attendance") is not None:
            ws.cell(row, COL["attendance"], r["attendance"])
            if r.get("attendance_source"):
                ws.cell(row, COL["attendance_source"], r["attendance_source"])
        if r.get("tier"):
            ws.cell(row, COL["tier"], r["tier"])
        if r.get("events_per_yr") is not None:
            ws.cell(row, COL["events"], r["events_per_yr"])
        if r.get("character"):
            ws.cell(row, COL["character"], r["character"])

        prior = ws.cell(row, COL["method"]).value
        text = _method_text(r)
        ws.cell(row, COL["method"], f"{prior}  ||  {text}" if prior else text)

    wb.save(path)
    return len(records)


def fill_blanks(records, path=None, sheet=SHEET):
    """Add a missing abstracts or attendance figure into EMPTY cells only.

    Never overwrites a value, never changes a tier. Each figure needs its source URL,
    and the row's conference name is checked first. A short note is appended to the
    Method column so the late addition is auditable.
    """
    path = path or attlib.WB
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet]
    for r in records:                                    # validate the batch first
        if r.get("abstracts") is not None and not r.get("source_url"):
            raise ValueError(f"an abstracts figure needs a source URL: row {r['row']}")
        if r.get("attendance") is not None and not r.get("attendance_source"):
            raise ValueError(f"an attendance figure needs a source URL: row {r['row']}")
        actual = str(ws.cell(r["row"], 5).value or "").strip()
        if actual != str(r["expected_name"] or "").strip():
            raise ValueError(f"expected_name mismatch at row {r['row']}")

    def empty(c):
        return ws.cell(row, c).value in (None, "")

    method_col = next(c for c in range(1, ws.max_column + 1)
                      if str(ws.cell(4, c).value or "").startswith("Method"))
    for r in records:
        row, added = r["row"], []
        if r.get("abstracts") is not None and empty(COL["abstracts"]):
            ws.cell(row, COL["abstracts"], r["abstracts"])
            if r.get("year") and empty(COL["year"]):
                ws.cell(row, COL["year"], r["year"])
            ws.cell(row, COL["source"], r["source_url"])
            added.append("abstracts")
        if r.get("attendance") is not None and empty(COL["attendance"]):
            ws.cell(row, COL["attendance"], r["attendance"])
            ws.cell(row, COL["attendance_source"], r["attendance_source"])
            added.append("attendance")
        if added:
            prior = ws.cell(row, method_col).value
            text = f"FILLED BLANK ({', '.join(added)}): {r.get('note') or ''}".strip()
            ws.cell(row, method_col, f"{prior}  ||  {text}" if prior else text)
    wb.save(path)
    return len(records)
