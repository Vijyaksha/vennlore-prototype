"""Export a run's rows for the web app. Writes TWO files:
  out/app_seed.v2.json  — the contract shape (talks×25, recommendations×13, runs)
  out/app_seed.json     — LEGACY shape the current web app ingests; deleted in Plan 2.
Offline: reads the archive and a run directory. Usage:
  uv run python scripts/export_app_seed.py --query out/graph_v1/stage0/query --ids datasets/micro-corpus.json"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_core.records import Recommendation, RunManifest  # noqa: E402
from gps_core.store import write_seed  # noqa: E402
from gps_data.archive import load_talks  # noqa: E402
from gps_data.datasets import corpus_ids  # noqa: E402
from gps_data.legacy_seed import legacy_seed  # noqa: E402
from gps_data.talk import from_row  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "out"


def resolve(path: str) -> Path:
    """Accept a path relative to the cwd or to the repo root."""
    p = Path(path)
    if p.is_absolute() or p.exists():
        return p
    return ROOT / p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, help="run_recommend output dir")
    ap.add_argument("--ids", required=True, help="dataset json naming the corpus ids")
    a = ap.parse_args()
    q = resolve(a.query)
    ids = corpus_ids(resolve(a.ids))
    talks = load_talks(ROOT / "data" / "gps2026", only_ids=ids)
    anchor = from_row(json.loads((q / "anchor.json").read_text()))
    rows = []
    for r in json.loads((q / "recommendations.json").read_text()):
        r = {k: v for k, v in r.items() if k != "contract_version"}
        rows.append(Recommendation(**{**r, "shared_methods": tuple(r["shared_methods"])}))
    mrow = json.loads((q / "run.json").read_text())
    mrow.pop("contract_version")
    manifest = RunManifest(**{**mrow, "anchor_ids": tuple(mrow["anchor_ids"])})
    locations = [json.loads(f.read_text())
                 for f in sorted((ROOT / "data/gps2026/locations").glob("*.json"))]
    loc_rows = [{"id": l["id"], "building": l["building"], "room": l["room"]} for l in locations]
    all_talks = [anchor] + list(talks.values())
    write_seed(OUT / "app_seed.v2.json", all_talks, rows, [manifest], loc_rows)
    (OUT / "app_seed.json").write_text(json.dumps(legacy_seed(all_talks, rows, loc_rows), indent=1))
    print(f"wrote app_seed.v2.json ({len(all_talks)} talks, {len(rows)} recommendations) "
          f"and legacy app_seed.json")


if __name__ == "__main__":
    main()
