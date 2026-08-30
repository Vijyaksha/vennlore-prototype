"""Export everything the web app needs into pipeline/out/app_seed.json.
Offline: pure file reading over data/gps2026, datasets/micro-corpus.json,
and the Stage-0 judgment checkpoints. Safe to rerun anytime."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_engine.app_export import build_seed  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "data" / "gps2026"
OUT = Path(__file__).resolve().parents[1] / "out" / "app_seed.json"

# The anchor is an external paper (Nano Lett. 2004, 4, 1261-1265), not a GPS
# talk; its row carries the real published abstract, same as run_stage0.
ANCHOR_ROW = {
    "id": 0,
    "title": "Photoconductivity of Self-Assembled Porphyrin Nanorods",
    "session_title": None,
    "units": ["DPOLY"],
    "start": None, "end": None,
    "building": None, "room": None,
    "abstract": (
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
        "coupled LUMOs of close-packed porphyrin molecules."),
}


def main() -> None:
    mc = json.loads((ROOT / "datasets" / "micro-corpus.json").read_text())
    neg = mc["negatives"]
    ids = ({p["id"] for p in mc["positives"]}
           | set(neg["random_unrelated"])
           | set(neg["same_domain_different_method"]))

    presentations = []
    for pid in sorted(ids):
        f = ARCHIVE / "presentations" / f"{pid}.json"
        if not f.exists():
            raise SystemExit(f"corpus id {pid} has no presentation file at {f}")
        presentations.append(json.loads(f.read_text()))

    events = [json.loads(f.read_text())
              for f in sorted((ARCHIVE / "events").glob("*.json"))]
    locations = [json.loads(f.read_text())
                 for f in sorted((ARCHIVE / "locations").glob("*.json"))]
    judgments = [json.loads(f.read_text())
                 for f in sorted((Path(__file__).resolve().parents[1]
                                  / "out" / "stage0" / "judgments").glob("*.json"))]

    seed = build_seed(presentations, events, locations, judgments, ANCHOR_ROW)
    OUT.write_text(json.dumps(seed, indent=1))
    print(f"wrote {OUT}: {len(seed['talks'])} talks, "
          f"{len(seed['locations'])} locations, "
          f"{len(seed['recommendations'])} recommendations")


if __name__ == "__main__":
    main()
