"""Life sciences wave 1 writeback: glue over the tested writers (writeback, attlib, dedupe).

Usage:  python3 apply_wave1.py --dry     # validate, print the plan, write write_plan.json, touch nothing
        python3 apply_wave1.py           # write the workbook

Rows the orchestrator overrides (spot-checks, rung-5 results, duplicates) are declared in the
EXTRA / DUPES / FORCE_TIER tables below so every deviation from a researcher verdict is on the record.
"""
import json, os, sys
sys.path.insert(0, "/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad")
import attlib, writeback, dedupe

W = "/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/life/wave1"
SHEET = "Census - Life Sciences"
attlib.SHEET = SHEET
attlib.CALL_DATE = attlib.TODAY = "2026-09-13"
attlib.RATIO_NOTE = ("life sciences wave 1 — ratio judged per conference by the researcher from the programme's "
                     "own wording (see the rationale above); no default or borrowed ratio")
TAG = "[life wave 1, 2026-09-13]"
SLICES = tuple(int(x) for x in os.environ.get("SLICES", "1,2,3").split(","))   # SLICES=1,3 for a partial dry run

DUPES = {75: "DUPLICATE / HELD INSIDE another census row: The Crustacean Society's recurring US meeting runs inside the SICB Annual Meeting (already on Census - Life Sciences); its only standalone meeting is an irregular non-US, institute-hosted event with no published programme (agent 2, wave 1). SICB is the surviving copy."}
EVENTS_OVERRIDE = {66: 0}   # Histochemical Society: no standalone meeting since 2011 (held inside EB, then TERMIS-AM) — researcher report, agent 1

# Orchestrator rung-5 results, one record per queue row, written as each page was worked
# (see r5_notes.json). A record with abstracts_numeric replaces the researcher's figure/tier;
# one with rung9=True sends the row through the rung-9 conversion; every note lands in Method.
R5 = {int(k): v for k, v in json.load(open(f"{W}/r5_notes.json")).items()}
EXTRA = {n: v["orchestrator_note"] for n, v in R5.items()}
FORCE_TIER = {n: v["tier"] for n, v in R5.items() if v.get("tier")}
RUNG9_ROWS = {n for n, v in R5.items() if v.get("rung9")}

recs = [x for i in SLICES for x in json.load(open(f"{W}/results_{i}.json"))]
queued = {x["conference"] for i in SLICES for x in json.load(open(f"{W}/queue_{i}.json"))}
missing = queued - {r["conference"] for r in recs}
assert not missing, f"{len(missing)} queued rows have no record: {sorted(missing)[:5]}"
assert len(recs) == len(queued), "duplicate or extra records"

for r in recs:   # normalise the shapes attlib renders
    r["alt_figures"] = [a if isinstance(a, dict) else {"value": a, "year": "see text", "basis": "UNSPECIFIED", "rung": "see text"}
                        for a in (r.get("alt_figures") or [])]
    if r.get("attendance") in (None, "") and r.get("attendance_numeric") is not None:
        r["attendance"] = f"{r['attendance_numeric']:,}"
    if not r.get("attendance_rung_name"):
        r["attendance_rung_name"] = "see Method column"
mapped = attlib.remap(recs)
assert len(mapped) == len(recs), "a conference name no longer matches the sheet"

VERDICT_TIER = {"VERIFIED": "VERIFIED", "BORDERLINE": "BORDERLINE", "OUT": "OUT",
                "UNRESOLVED": "BORDERLINE", "NEEDS_RUNG_5": "BORDERLINE"}


def is_rung9(r):
    return r.get("outcome") == "INFERRED" or r.get("rung") == 9 or r.get("_row_q") in RUNG9_ROWS


def tier(r, n):
    if n in FORCE_TIER:
        return FORCE_TIER[n]
    if is_rung9(r) and r.get("attendance_numeric"):
        return None          # decided by resolve_borderline below
    return VERDICT_TIER[r["verdict"]]


plan, wb_recs, calls, moves, problems = [], [], [], [], []
for r in mapped:
    q = next(x for x in recs if x["conference"] == r["conference"])
    n = q["row"]
    r["_row_q"] = n
    if n in EVENTS_OVERRIDE:
        r["events_per_yr"] = EVENTS_OVERRIDE[n]
    if n in R5 and R5[n].get("abstracts_numeric") is not None:   # orchestrator's rung-5 count wins
        for k in ("abstracts_numeric", "abstracts", "year", "rung", "source_url", "confidence"):
            r[k] = R5[n][k]
        r["outcome"] = "COUNTED"
    counted = (not is_rung9(r)) and r.get("abstracts_numeric") is not None
    abstracts = r["abstracts"] if counted else None
    if counted and not r.get("source_url"):
        problems.append((n, "counted figure with no source_url"))
    if r.get("events_per_yr") is None:
        problems.append((n, "no events_per_yr"))

    t = tier(r, n)
    call = None
    if is_rung9(r) and r.get("attendance_numeric"):
        call = dict(r, attendance=r["attendance_numeric"], bar=900,
                    implied=attlib.implied_abstracts(r["attendance_numeric"], r["ratio"]))
        probs = attlib.check_ratio(call)
        if probs:
            problems.append((n, f"ratio rejected: {probs}"))
        call.update(attlib.resolve_borderline(call))
        if t is None:
            t = "OUT" if call["decision"] == "BELOW BAR" else "BORDERLINE"
        calls.append(call)
    elif t is None:
        t = "BORDERLINE"    # rung-9 row with no attendance figure: no evidence either way (rule 1)

    method = r["method"]
    if abstracts is None and not is_rung9(r) and r.get("abstracts"):
        method = f"ROW SUMMARY: {r['abstracts']}  ||  {method}"
    if r.get("cadence_evidence"):
        method = f"{method}  ||  CADENCE: {r['events_per_yr']}/yr — {r['cadence_evidence']}"
    if r.get("duplicate_of"):
        method = f"{method}  ||  DUPLICATE?: {r['duplicate_of']}"
    if n in EXTRA:
        method = f"{method}  ||  {EXTRA[n]}"
    method = (f"{method}  ||  VERDICT {t} (researcher verdict {r['verdict']}, confidence {r.get('confidence')}, "
              f"{r.get('searches_used')} searches) {TAG}")
    wb_recs.append(dict(row=r["row"], expected_name=r["conference"], abstracts=abstracts,
                        year=r.get("year") if abstracts else None, source_url=r.get("source_url"),
                        rung=r.get("rung") if abstracts else (r.get("rung") or "n"),
                        tier=t, character=r.get("character"), method=method,
                        events_per_yr=r.get("events_per_yr")))
    if n in DUPES:
        moves.append(dict(row=r["row"], expected_name=r["conference"], why=DUPES[n]))
    elif t == "OUT":
        moves.append(dict(row=r["row"], expected_name=r["conference"],
                          why=f"OUT on positive evidence: {r.get('abstracts') or (call and call.get('implied'))} — see Method {TAG}"))
    plan.append(dict(row=r["row"], conference=r["conference"], tier=t, abstracts=abstracts,
                     events_per_yr=r.get("events_per_yr"), rung9=is_rung9(r),
                     implied=call["implied"] if call else None, decision=call["decision"] if call else None,
                     move=DUPES.get(n) or (t == "OUT")))

json.dump(plan, open(f"{W}/write_plan.json", "w"), ensure_ascii=False, indent=1)
import collections
print(len(wb_recs), "rows;", len(calls), "rung-9 calls;", len(moves), "moves;",
      dict(collections.Counter(p["tier"] for p in plan)))
if problems:
    print("PROBLEMS — fix before writing:")
    for p in problems: print("  ", p)
if "--dry" in sys.argv or problems:
    sys.exit(1 if problems else 0)

writeback.apply(wb_recs, sheet=SHEET)    # figures, year, source, tier, events/yr, character, Method log
attlib.apply(mapped)                     # attendance, source, basis, rung+how, character
attlib.write_inferred_abstracts(calls)   # labelled NOT COUNTED rung-9 figures
attlib.log_inclusion(calls)              # rung-9 audit log + Rupert's call column
dedupe.move_to_deleted(moves, today="2026-09-13", census=SHEET, deleted="Deleted - Life Sciences")
print("written", len(wb_recs), "rung9", len(calls), "moved", len(moves))
