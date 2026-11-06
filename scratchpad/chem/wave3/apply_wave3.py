"""Wave 3 writeback: glue over the tested writers (writeback, attlib, dedupe). Writes a plan first."""
import json, sys
sys.path.insert(0, "/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad")
import attlib, writeback, dedupe

W = "/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/chem/wave3"
attlib.SHEET = "Census - Chemistry"
attlib.CALL_DATE = "2026-09-12"
attlib.TODAY = "2026-09-12"
attlib.RATIO_NOTE = ("chemistry wave 3 — ratio judged per conference by the researcher from the programme's own "
                     "wording (see the rationale above); no default or borrowed ratio")
TAG = "[chem wave 3, 2026-09-12]"

recs = [x for i in (1, 2, 3) for x in json.load(open(f"{W}/results_{i}.json"))]
queued = {x["conference"] for i in (1, 2, 3) for x in json.load(open(f"{W}/queue_{i}.json"))}
assert len(recs) == 91 and {r["conference"] for r in recs} == queued
for r in recs:   # some researchers returned alt_figures as plain strings; keep the text, in the shape attlib renders
    r["alt_figures"] = [a if isinstance(a, dict) else {"value": a, "year": "see text", "basis": "UNSPECIFIED", "rung": "see text"}
                        for a in (r.get("alt_figures") or [])]
    if r.get("attendance") in (None, "") and r.get("attendance_numeric") is not None:
        r["attendance"] = f"{r['attendance_numeric']:,}"
    if not r.get("attendance_rung_name"):
        r["attendance_rung_name"] = "see Method column"
mapped = attlib.remap(recs)
assert len(mapped) == 91, "a conference name no longer matches the sheet"

RUNG9 = {93, 135, 141, 64, 100, 101, 110, 119, 131, 134}
DUPES = {  # queue row -> (surviving row name, why)
    116: "DUPLICATE of 'ISFC - International Symposium on Fluorine Chemistry' — ISoFT's recent editions run inside ISFC (wave 3 evidence in Method)",
    137: "DUPLICATE of 'CRSI National Symposium in Chemistry (NSC)' — the RSC–CRSI Joint Symposium is held together with CRSI-NSC (wave 3 evidence in Method)",
    94: "DUPLICATE of 'COM — Conference of Metallurgy and Materials' — MetSoc Hydrometallurgy is a track inside COM, not a standalone meeting (wave 3 evidence in Method)",
    102: "DUPLICATE of 'IUPAC World Chemistry Congress' — the World Chemistry Leadership Meeting is an invited session inside the Congress (wave 3 evidence in Method)",
}
EXTRA = {
    105: ("ORCHESTRATOR SPOT-CHECK (decisive row, near the floor): re-downloaded the three Drive booklets "
          "(HTTP 200; 22,675,098 / 25,741,367 / 11,338,284 bytes) and counted grep -oE '\\b(OR|P)-[0-9]{2}-[0-9]{4}\\b' | sort -u "
          "= 1,070 in BOTH pdftotext -layout and -raw (918 OR + 152 P), vs the researcher's 1,071/1,072. Written figure uses 1,070 less ~35 keynotes = ~1,035."),
    79: ("ORCHESTRATOR RUNG 5 (Chrome, 2026-09-12): dechema.converia.de/frontend/index.php?folder_id=445 renders the ESCRE 2015 "
         "poster-list shell with an EMPTY table; the Congress Planner (page_id=296) Calendar, List (every day) and Persons views "
         "show only registration, coffee, lunch/poster and poster-party slots — the scientific sessions and author index have "
         "been removed from the archive. Nothing countable. No evidence either way, so BORDERLINE, never OUT (rule 1). "
         "NEXT ACTION: re-check when the ESCRE 2027 programme is published."),
    54: ("ORCHESTRATOR RUNG 5 (Chrome, 2026-09-12): https://www.otago.ac.nz/nzic2024/ now returns the University of Otago "
         "'Page Not Found' (a removed page, not a bot wall); https://nzic2026.eventsairsite.com/programme is still the 17 Aug 2026 "
         "PRELIMINARY programme; the Scribd copy (document 791005035) renders only ad placeholders without an account. Nothing "
         "countable. No evidence either way, so BORDERLINE, never OUT (rule 1). NEXT ACTION: the final NZIC 2026 programme after mid-Sept 2026."),
    141: ("ORCHESTRATOR NOTE: the rung-9 input is a 2004 society MEMBERSHIP figure, not an attendance count (membership != attendance); "
          "it is kept only as an upper proxy for a closed members' meeting, and the row is OUT on its closed, Gordon-style format."),
    64: ("ORCHESTRATOR NOTE: researcher verdict UNRESOLVED (first edition Oct 2027). Written as OUT: both predecessor meetings "
         "(ECBS, EFMC-ISCB) are single-track and the predecessor attendance converts to ~113, far below 800 even flexed."),
}

def tier(r):
    v = r["verdict"]
    if v in ("VERIFIED", "BORDERLINE", "OUT"): return v
    if v == "NEEDS_RUNG_5": return "BORDERLINE"
    if r["row_q"] == 64: return "OUT"
    return "BORDERLINE"   # duplicates: tier irrelevant, row moves to Deleted

plan, wb_recs, calls, moves = [], [], [], []
for r in mapped:
    q = next(x for x in recs if x["conference"] == r["conference"])
    r["row_q"] = q["row"]
    n = r["row_q"]
    abstracts = None
    if n not in RUNG9 and r.get("abstracts_numeric") is not None:
        abstracts = r["abstracts"]
    if n == 105:
        abstracts = ("~1,035 (SICC-12, 2024: 1,070 unique abstract IDs in the 3-part e-booklet = 918 oral OR- + 152 poster P-, "
                     "re-derived by the orchestrator in both extraction modes; less ~35 keynote presentations. The share of the "
                     "20-min orals that were invited is UNKNOWN, so the true contributed figure is lower by an unknown amount)")
    method = r["method"]
    if abstracts is None and n not in RUNG9 and r.get("abstracts"):
        method = f"ROW SUMMARY: {r['abstracts']}  ||  {method}"
    if n in EXTRA:
        method = f"{method}  ||  {EXTRA[n]}"
    method = (f"{method}  ||  VERDICT {tier(r)} (researcher verdict {r['verdict']}, confidence {r.get('confidence')}, "
              f"{r.get('searches_used')} searches) {TAG}")
    wb_recs.append(dict(row=r["row"], expected_name=r["conference"], abstracts=abstracts,
                        year=r.get("year") if abstracts else None, source_url=r.get("source_url"),
                        rung=r.get("rung") if abstracts else (r.get("rung") or "n"),
                        tier=tier(r), character=r.get("character"), method=method))
    if n in RUNG9 and r.get("attendance_numeric"):
        c = dict(r, attendance=r["attendance_numeric"], bar=900,
                 implied=attlib.implied_abstracts(r["attendance_numeric"], r["ratio"]))
        probs = attlib.check_ratio(c)
        assert not probs, (n, probs)
        c.update(attlib.resolve_borderline(c))
        assert c["decision"] == "BELOW BAR", (n, c["decision"])
        calls.append(c)
    if n in DUPES:
        moves.append(dict(row=r["row"], expected_name=r["conference"], why=DUPES[n]))
    plan.append(dict(row=r["row"], conference=r["conference"], tier=tier(r), abstracts=abstracts,
                     rung9=n in RUNG9, implied=(calls[-1]["implied"] if calls and calls[-1]["row"] == r["row"] else None),
                     move=DUPES.get(n)))

json.dump(plan, open(f"{W}/write_plan.json", "w"), ensure_ascii=False, indent=1)
if "--dry" in sys.argv:
    print(len(wb_recs), "rows;", len(calls), "rung-9 calls;", len(moves), "moves"); sys.exit()

writeback.apply(wb_recs)                 # figures, year, source, tier, character, Method log
attlib.apply(mapped)                     # attendance, source, basis, rung+how, character
attlib.write_inferred_abstracts(calls)   # labelled NOT COUNTED rung-9 figures
attlib.log_inclusion(calls)              # rung-9 audit log + Rupert's call column
dedupe.move_to_deleted(moves, today="2026-09-12")
print("written", len(wb_recs), "rung9", len(calls), "moved", len(moves))
