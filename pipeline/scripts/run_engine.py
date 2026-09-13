"""Run any registered engine. GATED: live LLM spend — only with Rupert's go.

  ENGINE=graph_v1 uv run python scripts/run_engine.py index  --ids datasets/sample-500.json --out out/graph_v1/sample500
  ENGINE=graph_v1 uv run python scripts/run_engine.py recommend --ids datasets/sample-500.json --anchor out/anchor-lodestar.json --index out/graph_v1/sample500
  ENGINE=graph_v1 uv run python scripts/run_engine.py recommend --ids datasets/sample-500.json --presenter 199897 --index out/graph_v1/sample500

`--ids` on recommend names the dataset that was indexed: it supplies the corpus
hash recorded in the manifest and resolves --presenter/--talk.
Progress: <out>/status.json. Reruns resume from content-keyed checkpoints."""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_core.checkpoint import content_key  # noqa: E402
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
    r.add_argument("--ids", required=True, help="the dataset that was indexed")
    src = r.add_mutually_exclusive_group(required=True)
    src.add_argument("--anchor")
    src.add_argument("--presenter", type=int)
    src.add_argument("--talk", type=int)
    a = ap.parse_args()
    engine = get_engine(os.environ.get("ENGINE", "graph_v1"))

    ids = corpus_ids(resolve(a.ids))
    talks = load_talks(ARCHIVE, only_ids=ids)
    missing = ids - set(talks)

    if a.cmd == "index":
        if missing:
            raise SystemExit(f"corpus ids missing from archive: {sorted(missing)}")
        run_index(engine, list(talks.values()), resolve(a.out))
        return

    index = IndexArtifact(path=resolve(a.index), engine_id=engine.id)
    corpus = list(talks.values())
    authored: set[int] = set()
    if a.anchor:
        spec = json.loads(resolve(a.anchor).read_text())
        anchors = [external_anchor(spec["title"], spec["abstract"], spec.get("units", []))]
    elif a.presenter is not None:
        anchors = anchors_for(talks, a.presenter)
        if not anchors:
            in_archive = anchors_for(load_talks(ARCHIVE), a.presenter)
            raise SystemExit(
                f"presenter {a.presenter} has no talk in the indexed corpus"
                if in_archive else f"presenter {a.presenter} not in archive")
        authored = authored_by(talks, a.presenter)
    else:
        anchor = talks.get(a.talk)
        if anchor is None:
            in_archive = a.talk in load_talks(ARCHIVE)
            raise SystemExit(f"talk {a.talk} is not in the indexed corpus"
                             if in_archive else f"talk {a.talk} not in archive")
        anchors = [anchor]
        # The talk's own indexed copy would come back as a paid self-match, so
        # exclude it — and everything its presenter authored.
        authored = {a.talk} | (authored_by(talks, anchor.presenter_ids[0])
                               if anchor.presenter_ids else set())
    for anchor in anchors:
        out = index.path / "queries" / content_key(anchor.id, anchor.title, anchor.abstract)
        rows, man = run_recommend(engine, anchor, index, out,
                                  authored_ids=authored, corpus=corpus)
        print(f"anchor {anchor.id}: {sum(r.match for r in rows)} matches / {len(rows)} judged; "
              f"run {man.run_id} -> {out}")


if __name__ == "__main__":
    main()
