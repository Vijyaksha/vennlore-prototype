"""Drive any Engine through the two contract operations, record a manifest,
apply core filters, validate every row, and save results. Engines never
touch files outside their own artifact; core owns run.json and
recommendations.json."""
import hashlib
import importlib
import json
import subprocess
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from gps_core.checkpoint import content_key
from gps_core.contracts import validate
from gps_core.filters import exclude_authored, ranked
from gps_core.protocol import Engine, IndexArtifact
from gps_core.records import Recommendation, RunManifest
from gps_data.talk import Talk, to_row


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def corpus_hash(corpus: list[Talk]) -> str:
    blob = json.dumps(sorted((t.id, t.title, t.abstract) for t in corpus)).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def engine_version(engine: Engine) -> str:
    """Short git hash of the last commit touching the engine's package, or 'unknown'."""
    mod = importlib.import_module(type(engine).__module__)
    folder = Path(mod.__file__).resolve().parent
    try:
        return subprocess.check_output(
            ["git", "log", "-1", "--format=%h", "--", str(folder)],
            cwd=folder, text=True, stderr=subprocess.DEVNULL).strip() or "unknown"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def new_run_id(engine_id: str, *salt) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{engine_id}-{stamp}-{content_key(engine_id, stamp, *salt)[:6]}"


def run_index(engine: Engine, corpus: list[Talk], out: Path) -> tuple[IndexArtifact, RunManifest]:
    out.mkdir(parents=True, exist_ok=True)
    started = _now()
    artifact = engine.index(corpus, out)
    manifest = RunManifest(
        run_id=new_run_id(engine.id, "index", corpus_hash(corpus)),
        engine_id=engine.id, kind="index", engine_version=engine_version(engine),
        models=dict(engine.models), corpus_hash=corpus_hash(corpus), anchor_ids=(),
        started_at=started, finished_at=_now(), index_path=str(artifact.path))
    row = manifest.to_row()
    validate("run", row)
    (out / "run.json").write_text(json.dumps(row, indent=1))
    return artifact, manifest


def run_recommend(engine: Engine, anchor: Talk, index: IndexArtifact, out: Path,
                  authored_ids: set[int] | None = None,
                  corpus: list[Talk] | None = None) -> tuple[list[Recommendation], RunManifest]:
    out.mkdir(parents=True, exist_ok=True)
    started = _now()
    run_id = new_run_id(engine.id, "recommend", anchor.id)
    raw = engine.recommend(anchor, index)
    rows = ranked(exclude_authored(raw, authored_ids or set()))
    rows = [replace(r, run_id=run_id, for_talk_id=anchor.id) for r in rows]
    saved = [r.to_row() for r in rows]
    for row in saved:
        validate("recommendation", row)
    manifest = RunManifest(
        run_id=run_id, engine_id=engine.id, kind="recommend",
        engine_version=engine_version(engine), models=dict(engine.models),
        corpus_hash=corpus_hash(corpus) if corpus else "", anchor_ids=(anchor.id,),
        started_at=started, finished_at=_now(), index_path=str(index.path))
    mrow = manifest.to_row()
    validate("run", mrow)
    (out / "recommendations.json").write_text(json.dumps(saved, indent=1))
    (out / "run.json").write_text(json.dumps(mrow, indent=1))
    (out / "anchor.json").write_text(json.dumps(to_row(anchor), indent=1))
    return rows, manifest
