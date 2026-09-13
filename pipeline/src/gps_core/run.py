"""Drive any Engine through the two contract operations, record a manifest,
apply core filters, validate every row, and save results. Engines never
touch files outside their own artifact; core owns run.json and
recommendations.json."""
import functools
import hashlib
import importlib
import json
import os
import secrets
import subprocess
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from gps_core.checkpoint import content_key
from gps_core.contracts import ContractError, validate
from gps_core.filters import exclude_authored, ranked
from gps_core.protocol import Engine, IndexArtifact
from gps_core.records import Recommendation, RunManifest
from gps_data.talk import Talk, to_row


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def corpus_hash(corpus: list[Talk]) -> str:
    blob = json.dumps(sorted((t.id, t.title, t.abstract) for t in corpus)).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


@functools.lru_cache(maxsize=None)
def _git_short_hash(folder: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "log", "-1", "--format=%h", "--", folder],
            cwd=folder, text=True, stderr=subprocess.DEVNULL).strip() or "unknown"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def engine_version(engine: Engine) -> str:
    """Short git hash of the last commit touching the engine's package, or 'unknown'.
    Cached per folder so a batch of anchors does not fork git per anchor."""
    mod = importlib.import_module(type(engine).__module__)
    folder = Path(mod.__file__).resolve().parent
    return _git_short_hash(str(folder))


def new_run_id(engine_id: str, *salt) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = content_key(engine_id, stamp, os.getpid(), secrets.token_hex(3), *salt)
    return f"{engine_id}-{stamp}-{key[:6]}"


def run_index(engine: Engine, corpus: list[Talk], out: Path) -> tuple[IndexArtifact, RunManifest]:
    out.mkdir(parents=True, exist_ok=True)
    started = _now()
    artifact = engine.index(corpus, out)
    chash = corpus_hash(corpus)
    manifest = RunManifest(
        run_id=new_run_id(engine.id, "index", chash),
        engine_id=engine.id, kind="index", engine_version=engine_version(engine),
        models=dict(engine.models), corpus_hash=chash, anchor_ids=(),
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
    rows = ranked([replace(r, run_id=run_id, for_talk_id=anchor.id)
                   for r in exclude_authored(raw, authored_ids or set())])
    for r in rows:
        if r.engine_id != engine.id:
            raise ContractError(f"engine {engine.id!r} emitted a row tagged {r.engine_id!r}")
    saved = [r.to_row() for r in rows]
    for row in saved:
        validate("recommendation", row)
    manifest = RunManifest(
        run_id=run_id, engine_id=engine.id, kind="recommend",
        engine_version=engine_version(engine), models=dict(engine.models),
        corpus_hash=corpus_hash(corpus) if corpus is not None else "", anchor_ids=(anchor.id,),
        started_at=started, finished_at=_now(), index_path=str(index.path))
    mrow = manifest.to_row()
    validate("run", mrow)
    (out / "recommendations.json").write_text(json.dumps(saved, indent=1))
    (out / "run.json").write_text(json.dumps(mrow, indent=1))
    (out / "anchor.json").write_text(json.dumps(to_row(anchor), indent=1))
    return rows, manifest
