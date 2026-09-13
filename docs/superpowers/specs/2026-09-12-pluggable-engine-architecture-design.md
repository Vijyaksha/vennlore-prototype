# Pluggable Engine Architecture — Design

Date: 2026-09-12 · Status: draft for Rupert's review · Owner: Rupert

## 1. Purpose

Split the system into three components that meet only at written contracts, so that:

- several matching engines can exist side by side (`graph_v1`, `solvent_v2`, baselines) and
  switching between them is one config line;
- several UIs can exist side by side and switching between them is one config line;
- a person working on an engine needs to know only the engine's inputs and outputs, and a person
  working on a UI needs to know only the UI's inputs, and neither can break the other by accident.

The three components are the **data layer** (corpus loader + store + API), the **matching
engine** (offline batch producing recommendations), and the **UI**. The one rule:

> Engines write rows. UIs read rows. Neither imports the other. The row is defined in one place.

Everything else in this document is machinery to make that rule impossible to break by accident.

## 2. Component map

```
packages/contracts     the one shared truth: Talk, Recommendation, Run (zod → JSON Schema)
packages/api           tRPC router + repository; presenter-based; takes an engine_id
packages/ui            shadcn components (exists)
apps/web               UI v1 (Kindred)  ── each app mounts @repo/api and @repo/ui
apps/web-v2            UI v2            ─┘
pipeline/              uv workspace
  engine-core          Engine protocol, registry, checkpointing, progress, resume,
                       LLM clients, store writer, exclusion filter, eval harness
  engines/graph_v1     today's pipeline, assembled once
  engines/baseline_*   embedding kNN, embed+rubric, brute rubric, long-context
  engines/<next>       e.g. solvent_v2
  eval/                datasets, pooled labels, precision-at-K protocol
store                  Postgres (Supabase); recommendations keyed (engine_id, for_talk_id, candidate_id)
```

Data flow:

```
Data layer ──(Talk records)──▶ Engine ──(Recommendation rows)──▶ Data layer (store)
                                                                        │
UI ──(presenter_id; engine_id from config)─────────────────────────────▶│
UI ◀──(anchors: Talk[], recommendations: (Recommendation + candidate Talk)[])
```

The UI never calls the engine. The engine never sees the UI. The engine emits ids only; the data
layer joins the full Talk record back on when the UI asks.

## 3. Data layer

### 3.1 Talk record (24 fields)

Produced by one loader from the three archive files (`presentations/`, `events/`, `locations/`
under `data/gps2026`), and later served from the store in the same shape. Text fields are
tag-stripped then entity-decoded then whitespace-collapsed (existing `clean_text`).

| Field | Type | Source | Use |
|---|---|---|---|
| `id` | int | presentation | key; **0 is reserved for an external anchor** |
| `external_id` | string | presentation | APS submission number `SMT26-NNNNNNN`, unique; claim flow |
| `title` | string | presentation | cleaned |
| `abstract` | string | presentation | cleaned; 95 talks have an empty abstract |
| `units` | string[] | event.sponsor_units | cross_domain rule; empty when unknown |
| `topics` | string[] | presentation | 560 free tags; optional funnel signal, anchor sampling |
| `type` | string | presentation | `Oral-In-person`, `Invited-In-person`, `Poster-In-person`, `Oral-Virtual`, … |
| `is_invited` | bool | presentation | agenda display |
| `is_withdrawn` | bool | presentation | **excluded from the corpus at load time** (984 talks) |
| `start`, `end` | ISO datetime or null | presentation | agenda |
| `sort_order` | int | presentation | position within session; the only ordering for posters |
| `presentation_location` | string or null | presentation | poster board number |
| `author_ids` | int[] | presentation | exclusion filter, claim flow, co-author signal |
| `presenter_ids` | int[] | presentation | exactly one per non-withdrawn talk (18 have none) |
| `publication_reference` | string or null | presentation | citation string; route to the full paper |
| `funding_acknowledgement` | string or null | presentation | text |
| `team_acknowledgement` | string or null | presentation | collaboration name |
| `session_id` | int or null | event | join key |
| `session_title` | string or null | event | display |
| `session_code` | string or null | event | printed code, e.g. `MAR-U13` |
| `session_type` | string or null | event | `ORAL`, `FOCUS`, `INVITED`, `POSTER`, `PANEL`, … |
| `session_topics` | string[] | event | session-level tags |
| `building`, `room` | string or null | location via event.location_ids[0] | agenda and walking |

**Engine-readable subset.** An engine may read only `id`, `title`, `abstract`, `units`, `topics`.
It must not depend on any other field. The remaining fields exist for the UI, the agenda, the
exclusion filter and future features.

Deliberately left out until needed: the event `tags` dictionary (Attendance Mode, Audience, …),
`presiders`, `periods`, and the uncrawled `individual/{id}` endpoint (author names and
affiliations). Adding any of these later does not touch the engine.

### 3.2 Anchor

An anchor is either a corpus talk (by id) or an **external anchor**: a Talk record with `id = 0`,
`title`, `abstract`, `units`, and every other field null or empty. Rupert's porphyrin paper is an
external anchor.

### 3.3 Presenter resolution

The data layer, not the engine, resolves a person to talks:

- **anchors(presenter_id)** = non-withdrawn talks where `presenter_id ∈ presenter_ids`.
  10,582 presenters: 9,962 have one talk, 620 have two to six.
- **authored(presenter_id)** = talks where `presenter_id ∈ author_ids`. Used by the exclusion
  filter (§4.4). Authors appear on up to 175 talks.

### 3.4 Store

Postgres via Drizzle. Migrations through `drizzle-kit`, never ad-hoc DDL.

- `talks`: the 24 fields above. Adds 15 columns to today's table.
- `recommendations`: the Recommendation record (§4.2). Primary key
  `(engine_id, for_talk_id, candidate_id)`. Adds `engine_id`, `run_id`, `contract_version`,
  `rank`, `shared_methods`, `evidence`; `score` becomes a float; the three rubric sub-scores move
  into `evidence`.
- `runs`: the Run manifest (§4.3), keyed by `run_id`.
- `locations`: unchanged.

### 3.5 What the data layer can serve

One talk by id; any set of talks; the anchors for a presenter; the recommendations for a
presenter under a given `engine_id`, each joined to its candidate Talk. Always in the 24-field
shape.

## 4. Matching engine

### 4.1 Protocol

Two functions. Everything else is the engine's private business.

```python
class Engine(Protocol):
    id: str                                   # e.g. "graph_v1"
    def index(self, corpus: list[Talk], out: Path) -> IndexArtifact: ...
    def recommend(self, anchor: Talk, index: IndexArtifact) -> list[Recommendation]: ...
```

- `index` is the expensive offline build, run once per engine version per corpus.
- `recommend` is the query: one anchor in, rows out. It may report candidates with
  `match = false`; the evaluation harness wants them.
- `IndexArtifact` is opaque and engine-owned. Core stores its path in the run manifest.

### 4.2 Recommendation record (13 fields)

| Field | Type | Meaning |
|---|---|---|
| `for_talk_id` | int | the anchor this recommendation is for |
| `candidate_id` | int | the recommended talk; must exist in the corpus |
| `score` | float 0–1 | engine confidence, higher is better; ordering key |
| `rank` | int | position within this anchor's list, 1 is best |
| `match` | bool | the engine's decision that the candidate clears its bar; UI shows only `true` |
| `cross_domain` | bool | anchor and candidate share no sponsor unit (core default; an engine may override with its own rule and must say so in `evidence`) |
| `why` | string | one paragraph for the card; may be empty |
| `strongest_parallel` | string | one sentence naming the shared usage; may be empty |
| `shared_methods` | string[] | method names the match rests on, for chips; may be empty |
| `evidence` | object | engine-specific, opaque to the UI (rubric sub-scores, graph path, cosine, …) |
| `engine_id` | string | producing engine |
| `run_id` | string | points to the Run manifest |
| `contract_version` | int | shape version; starts at 1 |

The engine emits ids only. It never re-emits Talk fields.

`score` is 0–1 so that an embedding baseline or a SOLVENT-style engine can fill it honestly. For
`graph_v1` it is the rubric sum divided by 15, and the three sub-scores are kept in `evidence`.
The card's "score out of 15" display therefore becomes a percentage or a bar (UI-only change).

### 4.3 Run manifest

Written by core for every `index` and every `recommend` batch:
`run_id`, `engine_id`, engine code version (git hash of the engine folder), models used per stage,
corpus hash, anchor ids, started/finished timestamps, index artifact path, `contract_version`.
This is what makes a result reproducible and what the eval harness records.

### 4.4 engine-core responsibilities

An engine author fills in the two functions and inherits all of this:

- **Registry and switch.** Engines register under a name via Python entry points
  (`[project.entry-points."gps.engines"]`). One setting, `ENGINE=<id>`, selects the engine for a
  run; the same setting on the app side selects which rows the API serves. Switching is that one
  line plus a re-run of the export.
- **Checkpointing, progress, resume.** Per-artifact skip-if-exists checkpoints, a probeable
  `status.json`, and resumable reruns (repo rules). Checkpoints are keyed by content hash of the
  input plus the engine id, not by talk id alone, so a prompt or model change does not silently
  reuse stale results (a trap in today's scripts).
- **LLM clients.** The existing `LLMClient` seam (`FakeLLM`, `AnthropicLLM`, `DeepSeekLLM`),
  refusal handling, JSON parsing.
- **Exclusion filter.** After `recommend`, drop any candidate the presenter authored
  (`authored(presenter_id)`, §3.3). Fixed in core so no engine can recommend someone their own
  poster.
- **Default `cross_domain`.** Computed from units unless the engine overrides.
- **Validation.** Every row is validated against the committed JSON Schema before it is written.
  A non-conforming row fails the run.
- **Store writer.** Writes rows and the manifest to the store (or to `app_seed.json` while the
  store is offline), tagged with `engine_id` and `run_id`.
- **Eval harness.** Runs any engine over a labelled dataset and reports the shared protocol
  (§7). Lives beside the engines, not inside any of them.

### 4.5 Folder layout

```
pipeline/
  pyproject.toml            uv workspace root
  engine-core/              gps_core: protocol, registry, checkpoint, progress, llm, store, eval
  engines/
    graph_v1/               gps_engine_graph_v1: today's extraction→filing→cascade→graph→funnel→rubric
    baseline_embed/         cosine kNN over abstracts, no LLM
    baseline_embed_rubric/  embedding top-k → rubric
    baseline_brute_rubric/  rubric over every talk (quality ceiling)
    baseline_longctx/       one long-context call
  eval/
    datasets/               micro-corpus, held-out anchors, pooled labels, SOLVENT gold (sanity)
    protocol.py             precision@K%, hit/miss/FP per anchor, cross-domain recall
```

`graph_v1` is the current `gps_engine` package assembled **once**: the orchestration that is
currently pasted across `run_stage0.py`, `run_stage1_index.py` and `run_query.py` becomes one
`index` and one `recommend`. The library modules (`li_extraction`, `claims`, `filing`, `cascade`,
`similarity`, `graph`, `funnel`, `rubric`, `recommend`) move under the engine folder unchanged.

## 5. UI

### 5.1 API surface (`packages/api`)

Presenter-based. Every procedure takes `engine_id` from server config; a per-request override is
allowed for evaluation sessions but never exposed in the product UI.

- `presenter.picks({ presenterId })` →
  `{ presenterId, anchors: Talk[], recommendations: (Recommendation & { candidate: Talk })[] }`.
  Only rows with `match = true` for the configured engine, ordered by `for_talk_id` then `rank`.
- `presenter.agenda({ presenterId })` → matched candidate Talks plus the presenter's own talks,
  grouped by conference day (America/Denver), consecutive pairs annotated with the existing
  walking-time connection. No engine fields.
- `talk.get({ id })` → one Talk.
- External anchors are served the same way once a live query path exists (§9); the response
  shape does not change.

### 5.2 What a UI receives and renders

From a recommendation the UI renders six of the thirteen fields: `score`, `cross_domain`,
`why`, `strongest_parallel`, `shared_methods`, and `for_talk_id` (to group by anchor). From the
candidate Talk it renders title, session title/code, type, start/end, building/room, units. It
never sees `evidence`, `engine_id`, `run_id` or `contract_version`.

Presenters with several talks: rows stay per anchor; the default UI shows one merged rail with a
"for your talk on …" chip per card and keeps the best score per candidate. A per-talk rail is a
UI-only choice.

### 5.3 UI packaging

Each UI is an app under `apps/` that mounts `@repo/api` and `@repo/ui`. A new UI is a new app;
each app deploys as its own Vercel project from the same repo. UIs depend on `@repo/contracts`
and `@repo/api` only. All strings through next-intl; all times America/Denver.

## 6. Contracts (`packages/contracts`)

- **Source of truth:** zod schemas for `Talk`, `Recommendation`, `Run`, and the API response
  shapes. TypeScript consumers import them directly; no generation step.
- **JSON Schema:** a build script emits `talk.schema.json`, `recommendation.schema.json`,
  `run.schema.json` via `z.toJSONSchema()` (zod 4). The files are committed. A test fails if the
  committed copy drifts from the zod source.
- **Python side:** `engine-core` validates every row against the committed JSON Schema with
  `jsonschema`. Typed models, if wanted, are generated from the same files with
  `datamodel-code-generator`.
- **Golden fixtures:** `packages/contracts/fixtures/` holds valid example rows and deliberately
  invalid ones. Both the TypeScript and the Python suites load the same files.
- **Versioning:** additive change (new optional field) → no bump. Breaking change (rename, type
  change, removal) → `contract_version` bump. Rows keep the version they were written under; the
  API serves only versions it understands.
- **Enforcement:**
  - CI runs both suites whenever `packages/contracts` changes.
  - Turborepo `boundaries` fails the build if an app imports from the database or engine
    packages.
  - `CODEOWNERS`: `packages/contracts` requires Rupert's review; engine and UI folders are owned
    by their teams.

The four situations this covers: an engine records something new (goes in `evidence`, no
contract change); a UI needs a field the engine does not produce (PR to contracts, Python tests
fail until resolved); additive change (no bump); breaking change (bump, old rows stay readable).

## 7. Evaluation (shared protocol)

The harness takes any engine and a dataset of labelled pairs and reports, per anchor: precision
at top K% of ranked candidates (SOLVENT protocol), hits/misses against labelled positives, false
positives, and cross-domain recall. The current micro-corpus is a **tuning set**; held-out anchors
and pooled blind labels are a separate spec. The SOLVENT gold set (50 abstracts, 259 pairs) is
kept under `eval/datasets/solvent/` as a pipeline sanity check only, not as physics ground truth.

## 8. Migration from today's code

Each step is test-first (repo rule) and independently shippable.

1. **Contracts.** Create `packages/contracts` with the three zod schemas, JSON Schema emit, drift
   test, golden fixtures. TS + Python contract tests green.
2. **Data layer loader.** `load_talks` produces the 24-field Talk, excludes withdrawn talks,
   joins session and location. Drizzle migration adds the new `talks` columns.
3. **engine-core.** Protocol, registry, checkpoint/progress/resume (lifted from the scripts,
   content-hash keyed), LLM clients (moved), validation, exclusion filter, store writer,
   manifest. Unit tests with `FakeLLM`.
4. **graph_v1.** Move `gps_engine` under `engines/graph_v1`; implement `index` and `recommend`
   once; delete the three scripts. Re-run stage 0 with `ENGINE=graph_v1` and confirm the report
   reproduces the DeepSeek result (8/10, 0 FP) before anything else changes.
5. **Store + export.** Drizzle migration for `recommendations` (new key, new columns, float
   score) and `runs`. Export reads rows from any engine. Fix the exporter's hard-coded
   `out/stage0/` (Anthropic tree) to read the selected engine's run.
6. **API.** `packages/api` with presenter-based procedures; `apps/web` mounts it; router tests
   on the in-memory repo fake.
7. **UI.** Score display becomes percentage/bar; `shared_methods` chips; merged rail with anchor
   chip for multi-talk presenters. Component tests.
8. **Baselines.** The four baseline engines against the harness.
9. **Enforcement.** Turborepo boundaries, CI matrix, CODEOWNERS, branch protection on `main`.

## 9. Out of scope (deferred)

- Live query path for external anchors (needs a job queue, a Python worker and a run-status
  table; the response shape is already fixed so the UI does not change).
- Crawl of `individual/{id}` (author names and affiliations; needed before claim-by-name).
- A runtime engine/UI picker in the product. Switching is config; coexistence in the store is
  what makes a later picker cheap.
- Pluggable data layer. The contract already isolates it; no work planned.
- Stage-level swapping inside the graph-engine family (extractor / matcher / judge). Add when
  two engines share most of their stages; Hydra is the likely mechanism then.

## 10. Decisions recorded

- Whole-engine swap at the boundary (option A), not stage-level (option B).
- Switching is deploy-time config, not a runtime picker.
- `score` is 0–1; rubric sub-scores live in `evidence`.
- Presenter resolution and the exclusion filter belong to the data layer / core, not the engine.
- Zod is the single source of truth; JSON Schema is generated and committed; no Protobuf,
  OpenAPI or Pact.
- `is_withdrawn` talks are excluded at load time.
- The SOLVENT annotation scheme (Background / Purpose / Mechanism / Findings) and the
  SOLVENT-style extraction are a **future engine** (`solvent_v2`), not part of this refactor.
