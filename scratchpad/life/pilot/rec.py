"""Append one inline pilot record: python3 rec.py '<json>'"""
import sys, json
sys.path.insert(0, "/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad")
import pilotlib
r = json.loads(sys.argv[1])
base = dict(outcome=None, abstracts_numeric=None, abstracts=None, year=None, rung=None, source_url=None, spot_checks=[],
            searches_used=0, attendance_numeric=None, attendance_year=None, attendance_basis=None, attendance_rung=None,
            attendance_source_url=None, alt_figures=[], character=None, character_evidence=None, programme_type=None,
            programme_evidence=None, direct_abstracts=None, ratio=None, ratio_rationale=None, method=None, verdict=None,
            confidence=None, learned=None)
base.update(r)
run = pilotlib.Run("/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/life/pilot")
q = {x["row"]: x["conference"] for x in run.queue()}
assert q[base["row"]] == base["conference"], "name mismatch"
run.record(base)
print(json.load(open(run.dir / "STATUS.json"))["done"], "done")
