"""Propose ~50 negatives for the micro-corpus: 40 seeded-random unrelated talks
+ a shortlist of same-domain (organic-electronics-adjacent) talks from which
~10 different-method negatives will be hand-picked. Prints for review."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_data.archive import load_talks  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
POSITIVES = {p["id"] for p in json.loads(
    (ROOT / "datasets" / "micro-corpus.json").read_text())["positives"]}
ANCHOR_METHOD_WORDS = ("self-assembl", "photoconduct", "photocurrent", "memrist",
                       "neuromorphic", "synaptic", "resistive switching",
                       "nanowire", "nanorod", "charge transport")

talks = load_talks(ROOT / "data" / "gps2026")
eligible = [t for t in talks.values()
            if t.id not in POSITIVES
            and not any(w in (t.title + " " + t.abstract).lower()
                        for w in ANCHOR_METHOD_WORDS)]

rng = random.Random(2026)
print("== 40 random unrelated (auto-approved unless struck) ==")
for t in sorted(rng.sample(eligible, 40), key=lambda t: t.id):
    print(f"{t.id}\t[{','.join(t.units)}]\t{t.title[:100]}")

print("\n== same-domain shortlist (pick ~10 with NONE of the anchor's methods) ==")
same_domain = [t for t in eligible
               if "organic electronic" in t.session_title.lower()
               or "molecular electronic" in t.session_title.lower()
               or ("DPOLY" in t.units and "electro" in t.session_title.lower())]
for t in same_domain[:25]:
    print(f"{t.id}\t[{','.join(t.units)}]\t{t.title[:80]}  <<{t.session_title[:50]}>>")
