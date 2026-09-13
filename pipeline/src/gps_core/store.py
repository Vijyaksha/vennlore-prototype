"""Store writer. While Supabase is offline the store is a seed file the web
app ingests; the shape is the contract (talks, recommendations, runs)."""
import json
from pathlib import Path

from gps_core.contracts import validate
from gps_core.records import CONTRACT_VERSION, Recommendation, RunManifest
from gps_data.talk import Talk, to_row


def write_seed(path: Path, talks: list[Talk], rows: list[Recommendation],
               runs: list[RunManifest], locations: list[dict] | None = None) -> dict:
    talk_rows = [to_row(t) for t in sorted(talks, key=lambda t: t.id)]
    rec_rows = [r.to_row() for r in rows]
    run_rows = [m.to_row() for m in runs]
    for t in talk_rows:
        validate("talk", t)
    for r in rec_rows:
        validate("recommendation", r)
    for m in run_rows:
        validate("run", m)
    seed = {"contract_version": CONTRACT_VERSION, "talks": talk_rows,
            "locations": locations or [], "recommendations": rec_rows, "runs": run_rows}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(seed, indent=1))
    return seed
