"""Attendance writeback for the medicine census.

Rung 9 is NON-DECIDING: nothing here ever sets a Tier or touches the abstracts
columns. It records attendance, what the number counts, how it was obtained, and
the contributed-vs-curated character signal. Rupert decides.
"""
import re
import openpyxl

WB = '/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/tam-sam-som-v3.xlsx'
SHEET = 'Census - Medicine & Health'
NEW_COLS = {22: 'Attendance basis', 23: 'Attendance rung + how',
            24: 'Programme character', 25: "Rupert's call"}
ATT, SRC = 10, 11
TODAY = '2026-09-11'


def _ws(wb):
    return wb[SHEET]


def _ensure_cols(ws):
    for c, name in NEW_COLS.items():
        ws.cell(4, c).value = name


def _fmt(n):
    return f'{n:,}' if isinstance(n, (int, float)) else str(n)


def method_text(r):
    """Credit the rung that PRODUCED the figure, never the highest rung reached."""
    rung, name = r.get('attendance_rung'), r.get('attendance_rung_name') or ''
    if r.get('attendance_numeric') is not None and rung:
        head = f"RUNG {rung} PRODUCED THIS FIGURE — {name}."
    elif rung == 'A5':
        head = ("NO FIGURE YET — needs rung A5 (programme-platform count), reserved to the "
                "orchestrator's browser.")
    else:
        head = ("NO RUNG YIELDED A FIGURE — attendance remains UNKNOWN. Absence of evidence is "
                "NOT evidence the meeting is small.")
    parts = [head, r.get('attendance_method') or '']
    alts = r.get('alt_figures') or []
    if alts:
        rendered = '; '.join(
            f"{_fmt(a.get('value'))} ({a.get('year','?')}, basis {a.get('basis','UNSPECIFIED')}, "
            f"rung {a.get('rung','?')}) {a.get('url','')}".strip() for a in alts)
        parts.append(f"DISAGREEMENT — other figures found, recorded NOT averaged: {rendered}")
    if r.get('character_evidence'):
        parts.append(f"CHARACTER EVIDENCE: {r['character_evidence']}")
    parts.append(f"[attendance pass {TODAY}; {r.get('searches_used', 0)} searches; "
                 f"confidence={r.get('confidence')}]")
    return ' '.join(p for p in parts if p)


def remap(recs, path=WB):
    """Row numbers go stale the instant any row moves. Re-anchor by conference name."""
    wb = openpyxl.load_workbook(path)
    ws = _ws(wb)
    index = {}
    for row in range(5, ws.max_row + 1):
        name = ws.cell(row, 5).value
        if name:
            index.setdefault(str(name).strip(), row)
    out = []
    for r in recs:
        row = index.get(str(r.get('conference', '')).strip())
        if row is None:
            continue
        r = dict(r)
        r['row'] = row
        out.append(r)
    return out


def apply(recs, path=WB):
    wb = openpyxl.load_workbook(path)
    ws = _ws(wb)
    _ensure_cols(ws)
    written = []
    for r in recs:
        row = r['row']
        if r.get('attendance_numeric') is not None:
            year = r.get('attendance_year')
            ws.cell(row, ATT).value = (f"{r.get('attendance')} ({year})" if year
                                       else r.get('attendance'))
            ws.cell(row, SRC).value = r.get('attendance_source_url')
            ws.cell(row, 22).value = r.get('attendance_basis') or 'UNSPECIFIED'
        else:
            ws.cell(row, ATT).value = 'UNKNOWN'
            ws.cell(row, 22).value = ''
        ws.cell(row, 23).value = method_text(r)
        ws.cell(row, 24).value = r.get('character') or 'UNKNOWN'
        written.append(row)
    wb.save(path)
    return written


def apply_character(recs, path=WB):
    """Character-only write. Touches columns 23/24 and NOTHING else."""
    wb = openpyxl.load_workbook(path)
    ws = _ws(wb)
    _ensure_cols(ws)
    for r in recs:
        row = r['row']
        ws.cell(row, 24).value = r.get('character') or 'UNKNOWN'
        prior = ws.cell(row, 23).value or ''
        note = (f"CHARACTER: {r.get('character')} — {r.get('character_evidence','')} "
                f"[character pass {TODAY}, no search required]")
        ws.cell(row, 23).value = (prior + ' ' + note).strip() if prior else note
    wb.save(path)
    return [r['row'] for r in recs]


def _counted(text):
    """A real counted abstract figure, or None."""
    t = str(text or '')
    if not t or 'UNKNOWN' in t.upper():
        return None
    m = re.search(r'([\d][\d,]{2,})', t)
    return int(m.group(1).replace(',', '')) if m else None


def character_from_abstracts(path=WB):
    """A counted abstract figure IS the evidence of an open call for abstracts.
    Rows whose abstracts are UNKNOWN are omitted — those need actual research."""
    wb = openpyxl.load_workbook(path)
    ws = _ws(wb)
    out = []
    for row in range(5, ws.max_row + 1):
        if ws.cell(row, 14).value not in ('VERIFIED', 'BORDERLINE', 'NOT YET CENSUSED'):
            continue
        n = _counted(ws.cell(row, 7).value)
        if n is None:
            continue
        out.append({'row': row, 'conference': ws.cell(row, 5).value, 'character': 'CONTRIBUTED',
                    'character_evidence': f'{n:,} abstracts actually counted for this meeting — '
                                          f'an open call for abstracts necessarily produced them. '
                                          f'Source: {ws.cell(row, 9).value or "see abstracts source"}'})
    return out
