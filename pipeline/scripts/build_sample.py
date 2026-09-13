# pipeline/scripts/build_sample.py
"""Build the stratified Stage-1 sample (offline, deterministic, no LLM).
Writes datasets/sample-500.json: talk ids stratified sqrt-proportionally
across primary sponsor units, micro-corpus talks forced in."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_engines.graph_v1.sampling import stratified_sample  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
TOTAL = 500
SEED = 2026
MIN_ABSTRACT = 200


def main() -> None:
    arch = ROOT / "data" / "gps2026"
    sess_units: dict[int, tuple] = {}
    for f in (arch / "events").glob("*.json"):
        e = json.loads(f.read_text())
        for pid in e.get("presentation_ids", []):
            sess_units[pid] = tuple(e.get("sponsor_units") or [])

    by_unit: dict[str, list[int]] = {}
    for f in (arch / "presentations").glob("*.json"):
        p = json.loads(f.read_text())
        if p.get("is_withdrawn") or len(p.get("abstract") or "") < MIN_ABSTRACT:
            continue
        us = sess_units.get(p["id"], ())
        by_unit.setdefault(us[0] if us else "(none)", []).append(p["id"])

    mc = json.loads((ROOT / "datasets" / "micro-corpus.json").read_text())
    forced = ({p["id"] for p in mc["positives"]}
              | set(mc["negatives"]["random_unrelated"])
              | set(mc["negatives"]["same_domain_different_method"]))

    ids = stratified_sample(by_unit, TOTAL, SEED, must_include=forced)
    unit_of = {t: u for u, ts in by_unit.items() for t in ts}
    summary: dict[str, int] = {}
    for t in ids:
        summary[unit_of[t]] = summary.get(unit_of[t], 0) + 1

    out = {"seed": SEED, "total": len(ids),
           "micro_corpus_included": sorted(forced & set(ids)),
           "per_unit": dict(sorted(summary.items(), key=lambda kv: -kv[1])),
           "ids": ids}
    path = ROOT / "datasets" / "sample-500.json"
    path.write_text(json.dumps(out, indent=1))
    print(f"{len(ids)} talks across {len(summary)} units -> {path}")
    print(json.dumps(out["per_unit"], indent=1))


if __name__ == "__main__":
    main()
