# pipeline — matching engines

Engines write Recommendation rows; the web app reads them. The row shape is fixed by
`packages/contracts` (see `docs/superpowers/specs/2026-09-12-pluggable-engine-architecture-design.md`)
and every row an engine emits is validated against it before it is written.

## Run

    uv sync
    uv run pytest -q                                            # always allowed
    uv run lint-imports                                         # layering: engines > core > data; engines never import store/run
    ENGINE=graph_v1 uv run python scripts/eval_stage0.py        # LIVE LLM — needs Rupert's go
    ENGINE=graph_v1 uv run python scripts/run_engine.py index --ids datasets/sample-500.json --out out/graph_v1/sample500
    ENGINE=graph_v1 uv run python scripts/run_engine.py recommend --presenter 199897 --index out/graph_v1/sample500
    uv run python scripts/export_app_seed.py --query out/graph_v1/stage0/query --ids datasets/micro-corpus.json
                                                                # writes out/app_seed.v2.json (contract shape)

Progress: `<out>/status.json`. Reruns resume from content-keyed checkpoints under `<out>/<stage>/`;
a prompt or model change produces new keys, so stale results are never reused.

## Layout

    src/gps_core/       Engine protocol, registry, records, contract validation, checkpoints,
                        progress, LLM clients, filters, run driver, seed writer
    src/gps_data/       25-field Talk record, archive loader, presenter resolution, dataset ids
    src/gps_engines/    one folder per engine: graph_v1, graphrag_v1
    tests/{core,data,graph_v1,graphrag_v1}/

The layering is enforced by `.importlinter`: `gps_engines` may import `gps_core` and
`gps_data`, `gps_core` may import `gps_data`, `gps_data` imports nothing internal, and no
engine may import `gps_core.store` or `gps_core.run`. `uv run lint-imports` checks it.

## graphrag_v1 (Vennlore GraphRAG) and free local LLMs

`graphrag_v1` builds a knowledge graph (talk, topic, LLM-extracted method, APS unit),
detects research themes (Louvain communities, LLM-named), and recommends by walking the
graph: 1 hop (shared concepts and wording) gives core picks; 3 hops (strong talk ->
shared method -> another division) gives unexpected picks. The LLM only explains the
retrieved picks. Graph path, theme and similarities go in `evidence`.

Both engines can run free on a local model: `provider="local"` uses `LocalLLM`, which talks
to LM Studio (`http://localhost:1234/v1`, Developer tab -> Start Server) or Ollama
(`LOCAL_LLM_URL=http://localhost:11434/v1`) and uses whichever model is loaded.

    # offline, no LLM (deterministic): wording + topics only, no unexpected picks expected
    ENGINE=graphrag_v1 ENGINE_CONFIG='{"provider": "none"}' uv run python scripts/add_engine_to_seed.py
    # free local LLM (LIVE LLM — needs Rupert's go)
    ENGINE=graphrag_v1 uv run python scripts/add_engine_to_seed.py
    ENGINE=graph_v1 ENGINE_CONFIG='{"provider": "local"}' uv run python scripts/run_engine.py ...

`add_engine_to_seed.py` runs an engine over the talks already in an app seed (default: the
web e2e fixture, so no crawled archive is needed) and writes `out/app_seed.v2.json` holding
every engine's rows. Load it with `npm run db:seed --workspace=@repo/api`; serve with
`ENGINE_ID=graphrag_v1` (or `graph_v1`) — the UI is unchanged.

### Papers: arXiv, bioRxiv, medRxiv

`scripts/fetch_preprints.py` (a download: Rupert's go) pulls recent papers from all three
archives as Talk rows (`type: preprint:<archive>`, `external_id: arXiv:<id> | doi:<doi>`,
no start time) into `out/preprints.json`. Pass it with `--extra out/preprints.json` to
`add_engine_to_seed.py` and every engine recommends papers next to talks. The web app shows
them as paper tiles: archive flag (`arXiv · unexpected`), posting date, and a Read paper link;
the calendar leaves them out because they have no slot.

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
