"""Turn a phase-2 wave's researcher records into workbook writes, rung-9 calls and moves.

Pure planning, no workbook I/O: `plan()` takes records already re-anchored by attlib.remap()
and returns what the tested writers (writeback, attlib, dedupe) should be given. Extracted from
scratchpad/life/wave1/apply_wave1.py so every wave — and the overnight runs — share one logic.
"""
import attlib

VERDICT_TIER = {'VERIFIED': 'VERIFIED', 'BORDERLINE': 'BORDERLINE', 'OUT': 'OUT',
                'UNRESOLVED': 'BORDERLINE', 'NEEDS_RUNG_5': 'BORDERLINE'}


def normalise(r):
    """Shapes attlib renders: alt_figures as dicts, attendance text, a rung name."""
    r = dict(r)
    r['alt_figures'] = [a if isinstance(a, dict) else {'value': a, 'year': 'see text', 'basis': 'UNSPECIFIED', 'rung': 'see text'}
                        for a in (r.get('alt_figures') or [])]
    if r.get('attendance') in (None, '') and r.get('attendance_numeric') is not None:
        r['attendance'] = f"{r['attendance_numeric']:,}"
    if not r.get('attendance_rung_name'):
        r['attendance_rung_name'] = 'see Method column'
    return r


def is_rung9(r, rung9_rows=()):
    return r.get('outcome') == 'INFERRED' or r.get('rung') == 9 or r.get('_row_q') in rung9_rows


def plan(recs, tag, r5=None, dupes=None, events_override=None, bar=900):
    """r5: {row: {abstracts_numeric, abstracts, year, rung, source_url, confidence, orchestrator_note, tier?, rung9?}}
    dupes: {row: why}   events_override: {row: events_per_yr}
    Returns dict(plan, wb_recs, calls, moves, problems). Row keys are the queue-time row numbers
    carried in each record (`row`), which the caller has already remapped by name."""
    r5, dupes, events_override = r5 or {}, dupes or {}, events_override or {}
    rung9_rows = {n for n, v in r5.items() if v.get('rung9')}
    out = dict(plan=[], wb_recs=[], calls=[], moves=[], problems=[])
    for raw in recs:
        r = normalise(raw)
        n = r['_row_q'] = r.get('_row_q', r['row'])
        if n in events_override:
            r['events_per_yr'] = events_override[n]
        if n in r5 and r5[n].get('abstracts_numeric') is not None:      # orchestrator's rung-5 count wins
            for k in ('abstracts_numeric', 'abstracts', 'year', 'rung', 'source_url', 'confidence'):
                r[k] = r5[n][k]
            r['outcome'] = 'COUNTED'
        r9 = is_rung9(r, rung9_rows)
        counted = (not r9) and r.get('abstracts_numeric') is not None
        abstracts = r['abstracts'] if counted else None
        if counted and not r.get('source_url'):
            out['problems'].append((n, 'counted figure with no source_url'))
        if r.get('events_per_yr') is None:
            out['problems'].append((n, 'no events_per_yr'))

        t = r5[n]['tier'] if n in r5 and r5[n].get('tier') else None
        call = None
        if r9 and r.get('attendance_numeric'):
            call = dict(r, attendance=r['attendance_numeric'], bar=bar,
                        implied=attlib.implied_abstracts(r['attendance_numeric'], r['ratio']))
            probs = attlib.check_ratio(call)
            if probs:
                out['problems'].append((n, f'ratio rejected: {probs}'))
            call.update(attlib.resolve_borderline(call))
            if t is None:
                t = 'OUT' if call['decision'] == 'BELOW BAR' else 'BORDERLINE'
            out['calls'].append(call)
        elif t is None:
            t = 'BORDERLINE' if r9 else VERDICT_TIER[r['verdict']]   # rung-9 with no attendance: no evidence either way

        method = r.get('method') or ''
        if abstracts is None and not r9 and r.get('abstracts'):
            method = f"ROW SUMMARY: {r['abstracts']}  ||  {method}"
        if r.get('cadence_evidence'):
            method = f"{method}  ||  CADENCE: {r.get('events_per_yr')}/yr — {r['cadence_evidence']}"
        if r.get('duplicate_of'):
            method = f"{method}  ||  DUPLICATE?: {r['duplicate_of']}"
        if n in r5 and r5[n].get('orchestrator_note'):
            method = f"{method}  ||  {r5[n]['orchestrator_note']}"
        method = (f"{method}  ||  VERDICT {t} (researcher verdict {r.get('verdict')}, confidence {r.get('confidence')}, "
                  f"{r.get('searches_used')} searches) {tag}")
        out['wb_recs'].append(dict(row=r['row'], expected_name=r['conference'], abstracts=abstracts,
                                   year=r.get('year') if abstracts else None, source_url=r.get('source_url'),
                                   rung=r.get('rung') if abstracts else (r.get('rung') or 'n'),
                                   tier=t, character=r.get('character'), method=method,
                                   events_per_yr=r.get('events_per_yr')))
        if n in dupes:
            out['moves'].append(dict(row=r['row'], expected_name=r['conference'], why=dupes[n]))
        elif t == 'OUT':
            fig = r.get('abstracts') or (call and call.get('implied'))
            out['moves'].append(dict(row=r['row'], expected_name=r['conference'],
                                     why=f'OUT on positive evidence: {fig} — see Method {tag}'))
        out['plan'].append(dict(row=r['row'], conference=r['conference'], tier=t, abstracts=abstracts,
                                events_per_yr=r.get('events_per_yr'), rung9=r9,
                                implied=call['implied'] if call else None,
                                decision=call['decision'] if call else None,
                                move=dupes.get(n) or (t == 'OUT')))
    return out
