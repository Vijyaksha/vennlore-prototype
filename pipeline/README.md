# pipeline — matching engines

Engines write Recommendation rows; the web app reads them. The row shape is fixed by
`packages/contracts` (see `docs/superpowers/specs/2026-09-12-pluggable-engine-architecture-design.md`)
and every row an engine emits is validated against it before it is written.

## Run

    uv sync
    uv run pytest -q                                            # always allowed
    ENGINE=graph_v1 uv run python scripts/eval_stage0.py        # LIVE LLM — needs Rupert's go
    ENGINE=graph_v1 uv run python scripts/run_engine.py index --ids datasets/sample-500.json --out out/graph_v1/sample500
    ENGINE=graph_v1 uv run python scripts/run_engine.py recommend --presenter 199897 --index out/graph_v1/sample500
    uv run python scripts/export_app_seed.py --query out/graph_v1/stage0/query --ids datasets/micro-corpus.json

Progress: `<out>/status.json`. Reruns resume from content-keyed checkpoints under `<out>/<stage>/`;
a prompt or model change produces new keys, so stale results are never reused.

## Layout

    src/gps_core/       Engine protocol, registry, records, contract validation, checkpoints,
                        progress, LLM clients, filters, run driver, seed writer
    src/gps_data/       25-field Talk record, archive loader, presenter resolution, dataset ids
    src/gps_engines/    one folder per engine (graph_v1 today)
    tests/{core,data,graph_v1}/

## Add an engine

1. Create `src/gps_engines/<name>/engine.py` with a class exposing `id`, `models`,
   `index(corpus, out) -> IndexArtifact`, `recommend(anchor, index) -> list[Recommendation]`,
   and a `build(**config)` factory.
2. Register it: one line in `src/gps_core/registry.py`. `ENGINE=<name>` then selects it.
3. Read only `id`, `title`, `abstract`, `units`, `topics` from a Talk.
4. Put anything engine-specific in `Recommendation.evidence`. Never add top-level fields;
   that is a contract change and goes through `packages/contracts` first.
5. Return rows with `rank=0` and `run_id=""`; core stamps both, excludes the presenter's own
   work, ranks, validates, and writes the files.
6. Tests with fakes under `tests/<name>/`; no live LLM calls in tests.
