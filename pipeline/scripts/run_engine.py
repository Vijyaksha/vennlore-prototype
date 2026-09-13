"""Run any registered engine. GATED: live LLM spend — only with Rupert's go.

  ENGINE=graph_v1 uv run python scripts/run_engine.py index  --ids datasets/sample-500.json --out out/graph_v1/sample500
  ENGINE=graph_v1 uv run python scripts/run_engine.py recommend --anchor out/anchor-lodestar.json --index out/graph_v1/sample500
  ENGINE=graph_v1 uv run python scripts/run_engine.py recommend --presenter 199897 --index out/graph_v1/sample500

Progress: <out>/status.json. Reruns resume from content-keyed checkpoints."""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_core.protocol import IndexArtifact  # noqa: E402
from gps_core.registry import get_engine  # noqa: E402
from gps_core.run import run_index, run_recommend  # noqa: E402
from gps_data.archive import anchors_for, authored_by, load_talks  # noqa: E402
from gps_data.datasets import corpus_ids  # noqa: E402
from gps_data.talk import external_anchor  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "data" / "gps2026"


def resolve(path: str) -> Path:
    """Accept a path relative to the cwd or to the repo root."""
    p = Path(path)
    if p.is_absolute() or p.exists():
        return p
    return ROOT / p


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("index")
    i.add_argument("--ids", required=True)
    i.add_argument("--out", required=True)
    r = sub.add_parser("recommend")
    r.add_argument("--index", required=True)
    src = r.add_mutually_exclusive_group(required=True)
    src.add_argument("--anchor")
    src.add_argument("--presenter", type=int)
    src.add_argument("--talk", type=int)
    a = ap.parse_args()
    engine = get_engine(os.environ.get("ENGINE", "graph_v1"))

    if a.cmd == "index":
        ids = corpus_ids(resolve(a.ids))
        talks = load_talks(ARCHIVE, only_ids=ids)
        run_index(engine, list(talks.values()), resolve(a.out))
        return

    index = IndexArtifact(path=resolve(a.index), engine_id=engine.id)
    talks = load_talks(ARCHIVE)
    if a.anchor:
        spec = json.loads(resolve(a.anchor).read_text())
        anchors = [external_anchor(spec["title"], spec["abstract"], spec.get("units", []))]
        authored: set[int] = set()
    elif a.presenter is not None:
        anchors, authored = anchors_for(talks, a.presenter), authored_by(talks, a.presenter)
    else:
        anchors, authored = [talks[a.talk]], set()
    for anchor in anchors:
        rows, man = run_recommend(engine, anchor, index, index.path / "queries" / str(anchor.id),
                                  authored_ids=authored)
        print(f"anchor {anchor.id}: {sum(r.match for r in rows)} matches / {len(rows)} judged; run {man.run_id}")


if __name__ == "__main__":
    main()
