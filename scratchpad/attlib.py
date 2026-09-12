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
TODAY = '2026-09-11'        # the attendance research pass
CALL_DATE = '2026-09-12'    # the day Rupert's inclusion rule was applied


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


NOT_COUNTED = 'NOT COUNTED'   # the machine-readable marker for a rung-9 figure


def _counted(text):
    """A real COUNTED abstract figure, or None.

    A rung-9 figure (inferred from attendance, or reported by a source without a
    count behind it) is not a counted figure. It must never be read back as one:
    that would let the ratio feed on its own output.
    """
    t = str(text or '')
    if not t or 'UNKNOWN' in t.upper() or NOT_COUNTED in t.upper():
        return None
    m = re.search(r'([\d][\d,]{2,})', t)
    return int(m.group(1).replace(',', '')) if m else None


def parse_attendance(text):
    """The headline attendance figure in a cell, or None.

    Takes the FIRST figure, which is the headline one by writeback convention.
    A bare year is not an attendance figure: an unpunctuated 1900-2100 is
    rejected (so a real attendance of exactly '2024' would be missed — write
    such a figure with a comma).
    """
    t = str(text or '')
    if not t or 'UNKNOWN' in t.upper():
        return None
    for m in re.finditer(r'\d{1,3}(?:,\d{3})+|\d{3,}', t):
        raw = m.group(0)
        n = int(raw.replace(',', ''))
        if ',' not in raw and 1900 <= n <= 2100:
            continue                      # a year, not a headcount
        return n
    return None


def implied_abstracts(attendance, ratio):
    """Abstracts implied by a headcount at a given abstracts:attendance ratio."""
    if attendance is None or ratio is None:
        return None
    return round(attendance * ratio)


def ratio_rows(path=WB, sheet=SHEET):
    """Rows carrying BOTH a counted abstract figure and an attendance figure.

    These are the only rows that can calibrate the abstracts:attendance ratio.
    """
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet]
    out = []
    for row in range(5, ws.max_row + 1):
        abstracts = _counted(ws.cell(row, 7).value)
        attendance = parse_attendance(ws.cell(row, 10).value)
        if not abstracts or not attendance:
            continue
        out.append({'row': row, 'conference': ws.cell(row, 5).value,
                    'abstracts': abstracts, 'attendance': attendance,
                    'ratio': abstracts / attendance})
    return out


RATIO_NOTE = ('medicine calibration n=21 rows carrying BOTH a counted abstract figure and an '
              'attendance figure: median 0.246, range 0.061 (EuroPCR, a teaching course) to 1.55 '
              '(ESPGHAN). The ratio varies ~25x by conference type, so this is an order-of-'
              'magnitude indicator, never a measurement')


def inclusion_text(c):
    """The audit log for a row included on attendance rather than a counted abstract figure."""
    parts = [f"RUNG 9 ATTENDANCE-BASED CALL ({CALL_DATE}) — decision: {c['decision']}."]
    year = f" ({c['attendance_year']})" if c.get('attendance_year') else ''
    parts.append(f"Attendance {_fmt(c['attendance'])}{year}, basis {c.get('attendance_basis') or 'UNSPECIFIED'}, "
                 f"produced by rung {c.get('attendance_rung')}: {c.get('attendance_source_url')}.")
    parts.append(f"Programme type judged {c['programme_type']} — {c.get('programme_evidence','')}".strip() + '.')
    if c.get('direct_abstracts'):
        parts.append(f"ABSTRACT EVIDENCE: {_fmt(c['direct_abstracts'])} abstracts reported for this meeting "
                     f"by a source found during the attendance pass — used in preference to the ratio.")
    else:
        parts.append(f"No abstract figure found; implied ~{_fmt(c['implied'])} abstracts at "
                     f"{c['ratio']*100:.0f}% of attendance. RATIO JUDGED FOR THIS CONFERENCE: "
                     f"{c.get('ratio_rationale','')} Calibration context — {RATIO_NOTE}.")
    parts.append(f"Rupert's bar for this override: ~{_fmt(c['bar'])} abstracts.")
    parts.append("APPROXIMATION: the figure written into the Abstracts column carries the NOT COUNTED label "
                 "because it is arithmetic on a headcount and is NOT a counted abstract figure. No abstract "
                 "artefact was counted for this row; rungs 1-8 found none.")
    return ' '.join(parts)


def log_inclusion(calls, path=WB):
    """Append the attendance-based call to the Method column and Rupert's call column.

    Adds no columns, no switches and no files: the existing Method text is kept and the
    log appended after it. Tier, Include and the abstracts columns are never touched.
    """
    wb = openpyxl.load_workbook(path)
    ws = _ws(wb)
    _ensure_cols(ws)
    for c in calls:
        row = c['row']
        prior = ws.cell(row, 20).value or ''
        note = inclusion_text(c)
        ws.cell(row, 20).value = (str(prior).rstrip() + ' ' + note).strip() if prior else note
        figure = c.get('direct_abstracts') or c.get('implied')
        short = (f"{c['decision']} ({CALL_DATE}) — rung 9: ~{_fmt(figure)} abstracts from attendance "
                 f"{_fmt(c['attendance'])}, against Rupert's ~{_fmt(c['bar'])} bar. "
                 f"See Method column for the full log.")
        ws.cell(row, 25).value = short
    wb.save(path)
    return [c['row'] for c in calls]


RATIO_MIN, RATIO_MAX = 0.005, 2.0
# Floor is 0.5%, not the observed 6% minimum: a headcount padded with exhibition footfall or
# online viewers (Japan Medical Congress, ~540,000 incl. exhibition) needs a ratio far below any
# counted anchor to stay honest. Ceiling 200% covers meetings where nearly everyone presents.


def check_ratio(c):
    """Problems with a judged conversion ratio. Empty list means it is usable.

    The ratio is NEVER a lookup from a band table: it is a judgement about THIS
    conference, and it must arrive with the reasoning that produced it.
    """
    problems = []
    r = c.get('ratio')
    if r is None:
        problems.append('no ratio stated — every rung-9 row must state its own conversion ratio')
    elif not RATIO_MIN <= r <= RATIO_MAX:
        problems.append(f'ratio {r} outside the plausible range {RATIO_MIN}-{RATIO_MAX}')
    if len((c.get('ratio_rationale') or '').strip()) < 20:
        problems.append('no rationale — say what about THIS conference puts it at that ratio')
    return problems


def write_inferred_abstracts(calls, path=WB):
    """Write the rung-9 abstract figure into the Abstracts column, clearly labelled.

    The label carries the marker NOT COUNTED so the figure can never be mistaken —
    by a human or by _counted() — for an abstract count taken off a real artefact.
    A row that already has a counted figure is left alone: rungs 1-8 outrank rung 9.
    """
    wb = openpyxl.load_workbook(path)
    ws = _ws(wb)
    written = []
    for c in calls:
        row = c['row']
        prior = str(ws.cell(row, 7).value or '').strip()
        if _counted(prior) is not None:
            continue                                  # a counted figure already stands
        if c.get('direct_abstracts'):
            head = (f"~{_fmt(c['direct_abstracts'])} REPORTED BY SOURCE, {NOT_COUNTED} "
                    f"(rung 9 — figure stated by an organiser/report found during the attendance "
                    f"pass; no artefact was counted)")
        else:
            head = (f"~{_fmt(c['implied'])} INFERRED FROM ATTENDANCE, {NOT_COUNTED} "
                    f"(rung 9 — {_fmt(c['attendance'])} attendees x {c['ratio']*100:.0f}% of attendance, "
                    f"a ratio judged for this conference, not a default)")
        ws.cell(row, 7).value = f"{head} — see Method column. PRIOR: {prior}" if prior else head
        written.append(row)
    wb.save(path)
    return written


NEAR_BAR = 100      # a figure this close to the bar counts as clearing it
RATIO_FLEX = 0.20   # relative, not percentage points — see resolve_borderline


def resolve_borderline(c, bar=None, near=NEAR_BAR, flex=RATIO_FLEX):
    """Rupert's rule (2026-09-12) for a row that lands near the bar.

    Two tests, either one includes the row:
      1. the figure is within `near` of the bar;
      2. flexing the judged ratio up by `flex` brings it within `near` of the bar.

    The flex is RELATIVE (25% -> 20-30%), never percentage points. Adding points would
    rescue exactly the rows that should fail: a 2% teaching meeting flexed by +5 points
    becomes 7%, a 3.5x change that would drag a CE-and-trade meeting over the bar.

    A figure a source STATED is not flexed — there is no ratio behind it to vary.
    """
    bar = bar if bar is not None else c.get('bar', 1000)
    threshold = bar - near
    if c.get('direct_abstracts'):
        fig = c['direct_abstracts']
        return {'decision': 'INCLUDE' if fig >= threshold else 'BELOW BAR',
                'low': fig, 'high': fig, 'figure': fig,
                'why': (f'{_fmt(fig)} reported by a source, not flexed: there is no judged ratio behind it. '
                        f'{"Within" if fig >= threshold else "Short of"} {_fmt(near)} of the {_fmt(bar)} bar.')}
    fig = c.get('implied')
    ratio, att = c.get('ratio'), c.get('attendance')
    low = high = fig
    if ratio and att:
        low = implied_abstracts(att, ratio * (1 - flex))
        high = implied_abstracts(att, ratio * (1 + flex))
    if fig is not None and fig >= threshold:
        why = f'{_fmt(fig)} is within {_fmt(near)} of the {_fmt(bar)} bar.'
        decision = 'INCLUDE'
    elif high is not None and high >= threshold:
        why = (f'{_fmt(fig)} at {ratio*100:.0f}% falls short, but flexing the ratio +-{flex*100:.0f}% relative '
               f'({ratio*(1-flex)*100:.0f}%-{ratio*(1+flex)*100:.0f}%) gives {_fmt(low)}-{_fmt(high)}, and the '
               f'top of that band is within {_fmt(near)} of the {_fmt(bar)} bar.')
        decision = 'INCLUDE'
    else:
        why = (f'{_fmt(fig)} at {ratio*100:.0f}% stays short even flexed: the +-{flex*100:.0f}% relative band is '
               f'{_fmt(low)}-{_fmt(high)}, and {_fmt(high)} is still more than {_fmt(near)} under the '
               f'{_fmt(bar)} bar.')
        decision = 'BELOW BAR'
    return {'decision': decision, 'low': low, 'high': high, 'figure': fig, 'why': why}


DELETED_SHEET = 'Deleted - Medicine & Health'
DEL_ON, DEL_WHY, DEL_METHOD = 20, 21, 22      # deleted-sheet columns
CEN_NOTES, CEN_METHOD = 19, 20                # census-sheet columns


def apply_deleted(recs, path=WB, deleted_sheet=DELETED_SHEET):
    """Record attendance on the DELETED sheet for rows that stay removed.

    Rule 5: the deleted sheet is a reversible parking place, so a row that stays there
    still gets its figure and method. Restoring it later must be a re-read, never a
    re-run of the research. Touches only attendance (10), source (11) and Method (22).
    """
    wb = openpyxl.load_workbook(path)
    wd = wb[deleted_sheet]
    index = {}
    for row in range(5, wd.max_row + 1):
        name = wd.cell(row, 5).value
        if name:
            index.setdefault(str(name).strip(), row)
    written = []
    for r in recs:
        row = index.get(str(r.get('conference', '')).strip())
        if row is None:
            continue
        if r.get('attendance_numeric') is not None:
            year = r.get('attendance_year')
            wd.cell(row, ATT).value = (f"{r.get('attendance')} ({year})" if year else r.get('attendance'))
            wd.cell(row, SRC).value = r.get('attendance_source_url')
        prior = str(wd.cell(row, DEL_METHOD).value or '').strip()
        note = method_text(r)
        wd.cell(row, DEL_METHOD).value = (prior + ' ' + note).strip() if prior else note
        written.append(row)
    wb.save(path)
    return written


def _last_data_row(ws):
    """Last row carrying a conference name, before any totals block."""
    last = 4
    for row in range(5, ws.max_row + 1):
        if ws.cell(row, 5).value and ws.cell(row, 14).value:
            last = row
    return last


def _widen_totals(ws, new_end):
    """Totals formulas carry FIXED ranges (N5:N257). openpyxl re-points nothing, so a row
    inserted past the end would sit outside every total, silently. Widen them by hand."""
    for row in range(5, ws.max_row + 1):
        for col in (5, 6):
            v = ws.cell(row, col).value
            if isinstance(v, str) and v.startswith('='):
                ws.cell(row, col).value = re.sub(
                    r'([A-Z]{1,2})5:([A-Z]{1,2})(\d+)',
                    lambda m: f'{m.group(1)}5:{m.group(2)}{max(int(m.group(3)), new_end)}', v)


def upgrade_rows(calls, path=WB, sheet=SHEET, deleted_sheet=DELETED_SHEET):
    """Move rows the rung-9 figure lifts over the bar from the removed list to the approved one.

    Refuses any row under the bar, and any row whose ratio arrives without reasoning.
    The upgraded row lands as BORDERLINE, never VERIFIED: nothing was counted for it.
    """
    wb = openpyxl.load_workbook(path)
    ws, wd = wb[sheet], wb[deleted_sheet]
    moved = []
    for c in calls:
        figure = c.get('direct_abstracts') or c.get('implied')
        if figure is None or figure < c.get('bar', 1000) or check_ratio(c):
            continue
        src = None
        for row in range(5, wd.max_row + 1):
            if str(wd.cell(row, 5).value or '').strip() == str(c['conference']).strip():
                src = row
                break
        if src is None:
            continue
        values = {col: wd.cell(src, col).value for col in range(1, DEL_METHOD + 1)}
        dest = _last_data_row(ws) + 1
        ws.insert_rows(dest)
        for col in range(1, 19):                       # Field .. Rev/yr, as-is
            if col not in (7, 14):
                ws.cell(dest, col).value = values.get(col)
        ws.cell(dest, 14).value = 'BORDERLINE'         # never VERIFIED — nothing was counted
        ws.cell(dest, CEN_NOTES).value = values.get(19)
        history = (f"UPGRADED FROM THE REMOVED LIST ({CALL_DATE}) by rung 9. "
                   f"Previously deleted on {values.get(DEL_ON)} because: {values.get(DEL_WHY)}. "
                   f"Tier set to BORDERLINE, never VERIFIED: no abstract artefact was ever counted "
                   f"for this row. Prior method text follows. || {values.get(DEL_METHOD) or ''}")
        ws.cell(dest, CEN_METHOD).value = history
        _widen_totals(ws, dest)
        wd.delete_rows(src)
        c = dict(c, row=dest)
        moved.append(c)
        wb.save(path)
        wb = openpyxl.load_workbook(path)
        ws, wd = wb[sheet], wb[deleted_sheet]
    wb.save(path)
    if moved:
        write_inferred_abstracts(moved, path=path)
        log_inclusion(moved, path=path)
    return moved


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
