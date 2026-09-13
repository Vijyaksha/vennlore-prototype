"""Stage-0 evaluation through the Engine protocol: index the 57-talk
micro-corpus, recommend for the external anchor, score against the labels.
GATED: live LLM spend — only with Rupert's go. Output: <out>/report.json."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_core.records import Recommendation  # noqa: E402
from gps_core.registry import engine_from_env  # noqa: E402
from gps_core.run import run_index, run_recommend  # noqa: E402
from gps_data.archive import load_talks  # noqa: E402
from gps_data.talk import external_anchor  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ANCHOR_ABSTRACT = (
    "The photoconductivity of nanorods self-assembled from "
    "meso-tetrakis(4-sulfonatophenyl)porphine is described. The "
    "nanorods are insulating in the dark. Upon illumination with "
    "488 nm light, the nanorods become photoconductive, exhibiting "
    "a rapid turn on/off (<100 ms) of the current when the light is "
    "turned on/off. This photoconductivity grows over hundreds of "
    "seconds with light exposure and decays slowly when the light "
    "is off. The nanorods can be trained via an applied bias to "
    "exhibit a short-circuit photocurrent (with corresponding "
    "open-circuit photovoltage) that flows in the direction "
    "opposite that of the training bias. A qualitative model is "
    "proposed, in which conduction occurs through the tightly "
    "coupled LUMOs of close-packed porphyrin molecules.")


def report(rows: list[Recommendation], positives: set[int], corpus_size: int) -> dict:
    judged = sorted(r.candidate_id for r in rows)
    matched = {r.candidate_id for r in rows if r.match}
    return {
        "corpus_size": corpus_size,
        "funnel_candidates": judged,
        "expected_positives": sorted(positives),
        "hit_positives": sorted(matched & positives),
        "missed_positives": sorted(positives - matched),
        "positives_not_in_funnel": sorted(positives - set(judged)),
        "false_positives": sorted(matched - positives),
        "matches": [r.to_row() for r in rows if r.match],
    }


def main() -> None:
    engine = engine_from_env()
    tag = os.environ.get("RUN_TAG", "stage0")   # keeps two configurations' outputs apart
    out = Path(__file__).resolve().parents[1] / "out" / engine.id / tag
    mc = json.loads((ROOT / "datasets" / "micro-corpus.json").read_text())
    neg = mc["negatives"]
    positives = {p["id"] for p in mc["positives"]}
    ids = positives | set(neg["random_unrelated"]) | set(neg["same_domain_different_method"])
    talks = load_talks(ROOT / "data" / "gps2026", only_ids=ids)
    missing = ids - set(talks)
    if missing:
        raise SystemExit(f"micro-corpus ids missing from archive: {sorted(missing)}")
    anchor = external_anchor(mc["anchor"]["title"], ANCHOR_ABSTRACT, ["DPOLY"])
    art, _ = run_index(engine, list(talks.values()), out / "index")
    rows, _ = run_recommend(engine, anchor, art, out / "query", corpus=list(talks.values()))
    rep = report(rows, positives, corpus_size=len(talks) + 1)
    (out / "report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: v for k, v in rep.items() if k != "matches"}, indent=1))


if __name__ == "__main__":
    main()
