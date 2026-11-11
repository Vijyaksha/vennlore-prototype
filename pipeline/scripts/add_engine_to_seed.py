"""Add an engine's picks to an existing app seed, keeping every other engine's rows.

Runs the engine over the seed's own talks (no crawled archive needed): the
seed's recommend-run anchors are the anchors, every other talk is the corpus.
Output is a seed holding both engines, so the web app switches with ENGINE_ID.

  ENGINE=graphrag_v1 uv run python scripts/add_engine_to_seed.py
  ENGINE=graphrag_v1 ENGINE_CONFIG='{"provider": "none"}' uv run python scripts/add_engine_to_seed.py

Add papers: --extra out/preprints.json (from scripts/fetch_preprints.py).
Defaults: --seed apps/web/e2e/fixtures/app_seed.v2.json, --out pipeline/out/app_seed.v2.json
(the path `npm run db:seed` loads). Progress: <work>/index/status.json. Reruns resume
from the engine's checkpoints and replace (never duplicate) its rows.
With a live LLM this is an experiment: free with provider 'local', still Rupert's go."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_core.checkpoint import content_key  # noqa: E402
from gps_core.protocol import Engine  # noqa: E402
from gps_core.records import Recommendation, RunManifest  # noqa: E402
from gps_core.registry import engine_from_env  # noqa: E402
from gps_core.run import run_index, run_recommend  # noqa: E402
from gps_core.store import write_seed  # noqa: E402
from gps_data.talk import from_row  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED = ROOT / "apps/web/e2e/fixtures/app_seed.v2.json"
DEFAULT_OUT = ROOT / "pipeline/out/app_seed.v2.json"


def _rec(row: dict) -> Recommendation:
    row = {k: v for k, v in row.items() if k != "contract_version"}
    return Recommendation(**{**row, "shared_methods": tuple(row["shared_methods"])})


def _run(row: dict) -> RunManifest:
    row = {k: v for k, v in row.items() if k != "contract_version"}
    return RunManifest(**{**row, "anchor_ids": tuple(row["anchor_ids"])})


def add_engine(engine: Engine, seed_path: Path, work: Path, out: Path,
               extra: list[Path] = ()) -> dict:
    """extra: files of {"talks": [...]} rows (e.g. out/preprints.json) offered as
    candidates too; they are written into the seed so the app can show them."""
    seed = json.loads(Path(seed_path).read_text())
    talks = {t["id"]: from_row(t) for t in seed["talks"]}
    for path in extra:
        for row in json.loads(Path(path).read_text(encoding="utf-8"))["talks"]:
            talks.setdefault(row["id"], from_row(row))
    anchor_ids = sorted({a for r in seed["runs"] if r["kind"] == "recommend"
                         for a in r["anchor_ids"]}) or [min(talks)]
    corpus = [t for i, t in sorted(talks.items()) if i not in anchor_ids]

    index, _ = run_index(engine, corpus, work / "index")
    new_rows, new_runs = [], []
    for a in anchor_ids:
        anchor = talks[a]
        q = work / "queries" / content_key(anchor.id, anchor.title, anchor.abstract)
        rows, manifest = run_recommend(engine, anchor, index, q, corpus=corpus)
        new_rows += rows
        new_runs.append(manifest)
        print(f"anchor {a}: {sum(r.match for r in rows)} picks / {len(rows)} rows "
              f"({engine.id})", flush=True)

    kept_rows = [_rec(r) for r in seed["recommendations"] if r["engine_id"] != engine.id]
    kept_runs = [_run(m) for m in seed["runs"] if m["engine_id"] != engine.id]
    return write_seed(out, list(talks.values()), kept_rows + new_rows,
                      kept_runs + new_runs, seed.get("locations", []))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default=str(DEFAULT_SEED))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--work", default=None, help="engine work dir (default out/<engine>/seed)")
    ap.add_argument("--extra", action="append", default=[],
                    help="extra candidates, e.g. out/preprints.json (repeatable)")
    a = ap.parse_args()
    engine = engine_from_env()
    work = Path(a.work) if a.work else ROOT / "pipeline/out" / engine.id / "seed"
    seed = add_engine(engine, Path(a.seed), work, Path(a.out), [Path(x) for x in a.extra])
    engines = sorted({r["engine_id"] for r in seed["recommendations"]})
    print(f"wrote {a.out}: {len(seed['talks'])} talks, {len(seed['recommendations'])} "
          f"recommendations from {', '.join(engines)}")


if __name__ == "__main__":
    main()
