"""Live progress for life wave 1: python3 status.py"""
import json, os, collections
here = os.path.dirname(os.path.abspath(__file__))
tot = done = 0
v = collections.Counter()
for i in (1, 2, 3):
    q = len(json.load(open(f"{here}/queue_{i}.json")))
    p = f"{here}/results_{i}.json"
    try:
        r = json.load(open(p))
    except (FileNotFoundError, json.JSONDecodeError):
        r = []
    v.update(x.get("verdict") for x in r)
    print(f"agent {i}: {len(r)}/{q} rows, {sum(x.get('searches_used') or 0 for x in r)} searches")
    tot += q; done += len(r)
print(f"TOTAL {done}/{tot}", dict(v))
