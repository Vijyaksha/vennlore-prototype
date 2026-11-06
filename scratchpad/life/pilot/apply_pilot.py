"""Life-sciences pilot writeback: glue over the tested writers (writeback, attlib)."""
import json, sys
sys.path.insert(0, "/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad")
import attlib, writeback

SHEET = "Census - Life Sciences"
attlib.SHEET = SHEET
attlib.CALL_DATE = attlib.TODAY = "2026-09-12"
attlib.RATIO_NOTE = ("life sciences pilot — no counted life-sciences anchor existed yet; ratio judged from this "
                     "conference's own programme description (see rationale)")
TAG = "[life sciences pilot, 2026-09-12, inline]"
recs = json.load(open("/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/life/pilot/RESULTS.json"))
assert len(recs) == 20
for r in recs:
    if r.get("attendance_numeric") is not None:
        r["attendance"] = f"{r['attendance_numeric']:,}"
    r["attendance_rung_name"] = r.get("attendance_rung_name") or "see Method column"
    r["alt_figures"] = [a if isinstance(a, dict) else {"value": a} for a in (r.get("alt_figures") or [])]
mapped = attlib.remap(recs)
assert len(mapped) == 20, "a conference name no longer matches the sheet"

TIER = {"VERIFIED": "VERIFIED", "BORDERLINE": "BORDERLINE", "OUT": "OUT", "UNRESOLVED": "BORDERLINE"}
wb_recs, calls = [], []
for r in mapped:
    rung9 = r.get("rung") == 9
    abstracts = None if rung9 else (r["abstracts"] if r.get("abstracts_numeric") is not None else None)
    method = r["method"] if abstracts is not None or rung9 else f"ROW SUMMARY: {r['abstracts']}  ||  {r['method']}"
    method += (f"  ||  VERDICT {TIER[r['verdict']]} (pilot verdict {r['verdict']}, confidence {r.get('confidence')}, "
               f"{r.get('searches_used')} searches) {TAG}")
    wb_recs.append(dict(row=r["row"], expected_name=r["conference"], abstracts=abstracts,
                        year=r.get("year") if abstracts else None, source_url=r.get("source_url"),
                        rung=r.get("rung") or "n", tier=TIER[r["verdict"]], character=r.get("character"), method=method))
    if rung9:
        c = dict(r, attendance=r["attendance_numeric"], bar=900, implied=attlib.implied_abstracts(r["attendance_numeric"], r["ratio"]))
        assert not attlib.check_ratio(c), attlib.check_ratio(c)
        c.update(attlib.resolve_borderline(c))
        calls.append(c)
if "--dry" in sys.argv:
    print(len(wb_recs), "rows;", [(c["conference"][:25], c["implied"], c["decision"]) for c in calls]); sys.exit()
writeback.apply(wb_recs, sheet=SHEET)
attlib.apply(mapped)
attlib.write_inferred_abstracts(calls)
attlib.log_inclusion(calls)
print("written", len(wb_recs), "rung9", len(calls))
