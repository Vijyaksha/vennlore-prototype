# Pluggable Engine — Plan 1: Contracts, Data Layer, Engine Core, graph_v1

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the binding contracts and the engine side of the architecture in `docs/superpowers/specs/2026-09-12-pluggable-engine-architecture-design.md`, so that today's graph pipeline runs as the first registered engine (`graph_v1`) through a two-function protocol and writes contract-valid Recommendation rows, reproducing the stage-0 result.

**Architecture:** `packages/contracts` holds the zod source of truth and emits committed JSON Schema. `pipeline/src/gps_core` provides the Engine protocol, registry, records, contract validation, checkpointing, progress, LLM clients, filters, and the run driver. `pipeline/src/gps_data` loads the 25-field Talk from the archive and resolves presenters. `pipeline/src/gps_engines/graph_v1` is the existing `gps_engine` package moved and assembled once into `index()` and `recommend()`. Three duplicated runner scripts are replaced by one engine runner, one stage-0 evaluator, and one exporter.

**Tech Stack:** TypeScript + zod 4 + vitest + tsx (contracts); Python 3.12 + uv + pytest + `jsonschema` (engine); existing DeepSeek/Anthropic clients; sentence-transformers and PhySH unchanged inside `graph_v1`.

**Out of scope for this plan (Plans 2 and 3):** Drizzle migrations, `packages/api`, UI changes, baseline engines, eval harness, Turborepo boundaries, CODEOWNERS, branch protection. The current web app keeps working from a legacy-shaped `app_seed.json` produced by an adapter that Plan 2 deletes.

**Rules that apply to every task:** TDD (failing test first, watch it fail, minimal code, green). Surgical edits. Never run a live LLM call without Rupert's go (Task 12 is the only gated step). Commit after every task with the attribution lines shown.

---

## File structure

```
packages/contracts/
  package.json  tsconfig.json
  src/index.ts  src/talk.ts  src/recommendation.ts  src/run.ts
  scripts/emit.ts                 # zod -> schema/*.json
  schema/talk.schema.json  schema/recommendation.schema.json  schema/run.schema.json   (committed)
  fixtures/valid/{talk,recommendation,run}.json
  fixtures/invalid/{recommendation-score-out-of-range,talk-missing-title,recommendation-unknown-key}.json
  test/schemas.test.ts

pipeline/
  pyproject.toml                  # +jsonschema; packages list updated
  src/gps_core/__init__.py contracts.py records.py checkpoint.py progress.py llm.py protocol.py registry.py filters.py run.py store.py
  src/gps_data/__init__.py talk.py archive.py legacy_seed.py
  src/gps_engines/__init__.py
  src/gps_engines/graph_v1/__init__.py engine.py + (moved) li_extraction.py claims.py filing.py cascade.py similarity.py graph.py funnel.py rubric.py recommend.py physh.py sampling.py
  tests/core/  tests/data/  tests/graph_v1/
  scripts/run_engine.py  scripts/eval_stage0.py  scripts/export_app_seed.py  (build_sample.py, select_negatives.py updated)
  DELETED: scripts/run_stage0.py scripts/run_stage1_index.py scripts/run_query.py src/gps_engine/corpus.py src/gps_engine/app_export.py
```

Commit trailer for every commit in this plan:

```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GyR4M6ie2tftRPoSLdJdxY
```

---

### Task 1: `packages/contracts` — zod schemas, JSON Schema emit, fixtures, drift test

**Files:**
- Create: `packages/contracts/package.json`, `packages/contracts/tsconfig.json`
- Create: `packages/contracts/src/talk.ts`, `src/recommendation.ts`, `src/run.ts`, `src/index.ts`
- Create: `packages/contracts/scripts/emit.ts`
- Create: `packages/contracts/fixtures/valid/talk.json`, `recommendation.json`, `run.json`
- Create: `packages/contracts/fixtures/invalid/recommendation-score-out-of-range.json`, `talk-missing-title.json`, `recommendation-unknown-key.json`
- Test: `packages/contracts/test/schemas.test.ts`

- [ ] **Step 1: Scaffold the package**

`packages/contracts/package.json`:

```json
{
  "name": "@repo/contracts",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "exports": {
    ".": "./src/index.ts",
    "./schema/*": "./schema/*.json"
  },
  "scripts": {
    "test": "vitest run",
    "emit": "tsx scripts/emit.ts",
    "check-types": "tsc --noEmit",
    "lint": "eslint . --max-warnings 0"
  },
  "dependencies": {
    "zod": "^4.4.3"
  },
  "devDependencies": {
    "@repo/eslint-config": "*",
    "@repo/typescript-config": "*",
    "@types/node": "26.3.0",
    "eslint": "10.9.1",
    "tsx": "^4.23.13",
    "typescript": "~5.9.3",
    "vitest": "^4.1.11"
  }
}
```

`packages/contracts/tsconfig.json`:

```json
{
  "extends": "@repo/typescript-config/base.json",
  "compilerOptions": { "noEmit": true, "types": ["node"] },
  "include": ["src/**/*.ts", "scripts/**/*.ts", "test/**/*.ts"],
  "exclude": ["node_modules"]
}
```

`packages/contracts/eslint.config.mjs`:

```js
import { config } from "@repo/eslint-config/base";
export default config;
```

Run: `cd /Users/rupertlim/AI_Projects/ConferenceApp && npm install`
Expected: completes; `node_modules/@repo/contracts` is a symlink to `packages/contracts`.

- [ ] **Step 2: Write the failing test**

`packages/contracts/test/schemas.test.ts`:

```ts
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";

import { RecommendationSchema, RunSchema, TalkSchema } from "../src/index";
import { emitAll } from "../scripts/emit";

const ROOT = join(import.meta.dirname, "..");
const read = (p: string) => JSON.parse(readFileSync(join(ROOT, p), "utf8"));

const BY_KIND = {
  talk: TalkSchema,
  recommendation: RecommendationSchema,
  run: RunSchema,
} as const;

describe("valid fixtures parse", () => {
  for (const kind of Object.keys(BY_KIND) as (keyof typeof BY_KIND)[]) {
    test(kind, () => {
      const row = read(`fixtures/valid/${kind}.json`);
      expect(BY_KIND[kind].safeParse(row).success).toBe(true);
    });
  }
});

describe("invalid fixtures are rejected", () => {
  for (const file of readdirSync(join(ROOT, "fixtures/invalid"))) {
    test(file, () => {
      const kind = file.split("-")[0] as keyof typeof BY_KIND;
      const row = read(`fixtures/invalid/${file}`);
      expect(BY_KIND[kind].safeParse(row).success).toBe(false);
    });
  }
});

describe("committed JSON Schema matches the zod source", () => {
  for (const [kind, schema] of Object.entries(emitAll())) {
    test(kind, () => {
      expect(read(`schema/${kind}.schema.json`)).toEqual(schema);
    });
  }
});

test("talk has exactly 25 fields", () => {
  expect(Object.keys(TalkSchema.shape)).toHaveLength(25);
});

test("recommendation has exactly 13 fields", () => {
  expect(Object.keys(RecommendationSchema.shape)).toHaveLength(13);
});
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `npm run test --workspace=@repo/contracts`
Expected: FAIL, "Cannot find module '../src/index'".

- [ ] **Step 4: Write the schemas**

`packages/contracts/src/talk.ts`:

```ts
import { z } from "zod";

const nullableString = z.string().nullable();
const nullableDatetime = z.iso.datetime().nullable();

/** One talk, as loaded from the APS feed. id 0 is reserved for an external anchor. */
export const TalkSchema = z
  .strictObject({
    id: z.int().min(0),
    external_id: nullableString,
    title: z.string().min(1),
    abstract: z.string(),
    units: z.array(z.string()),
    topics: z.array(z.string()),
    type: nullableString,
    is_invited: z.boolean(),
    is_withdrawn: z.boolean(),
    start: nullableDatetime,
    end: nullableDatetime,
    sort_order: z.int().nullable(),
    presentation_location: nullableString,
    author_ids: z.array(z.int()),
    presenter_ids: z.array(z.int()),
    publication_reference: nullableString,
    funding_acknowledgement: nullableString,
    team_acknowledgement: nullableString,
    session_id: z.int().nullable(),
    session_title: nullableString,
    session_code: nullableString,
    session_type: nullableString,
    session_topics: z.array(z.string()),
    building: nullableString,
    room: nullableString,
  })
  .meta({ title: "Talk" });

export type Talk = z.infer<typeof TalkSchema>;
```

`packages/contracts/src/recommendation.ts`:

```ts
import { z } from "zod";

export const CONTRACT_VERSION = 1;

/** One engine judgment: anchor talk -> candidate talk. Ids only; the data layer joins Talk fields. */
export const RecommendationSchema = z
  .strictObject({
    for_talk_id: z.int().min(0),
    candidate_id: z.int().min(1),
    score: z.number().min(0).max(1),
    rank: z.int().min(1),
    match: z.boolean(),
    cross_domain: z.boolean(),
    why: z.string(),
    strongest_parallel: z.string(),
    shared_methods: z.array(z.string()),
    evidence: z.record(z.string(), z.unknown()),
    engine_id: z.string().regex(/^[a-z0-9_]+$/),
    run_id: z.string().min(1),
    contract_version: z.literal(CONTRACT_VERSION),
  })
  .meta({ title: "Recommendation" });

export type Recommendation = z.infer<typeof RecommendationSchema>;
```

`packages/contracts/src/run.ts`:

```ts
import { z } from "zod";

import { CONTRACT_VERSION } from "./recommendation";

/** Provenance for one index build or one recommend batch. */
export const RunSchema = z
  .strictObject({
    run_id: z.string().min(1),
    engine_id: z.string().regex(/^[a-z0-9_]+$/),
    kind: z.enum(["index", "recommend"]),
    engine_version: z.string(),
    models: z.record(z.string(), z.string()),
    corpus_hash: z.string(),
    anchor_ids: z.array(z.int()),
    started_at: z.iso.datetime(),
    finished_at: z.iso.datetime(),
    index_path: z.string().nullable(),
    contract_version: z.literal(CONTRACT_VERSION),
  })
  .meta({ title: "Run" });

export type Run = z.infer<typeof RunSchema>;
```

`packages/contracts/src/index.ts`:

```ts
export { TalkSchema, type Talk } from "./talk";
export { RecommendationSchema, CONTRACT_VERSION, type Recommendation } from "./recommendation";
export { RunSchema, type Run } from "./run";
```

`packages/contracts/scripts/emit.ts`:

```ts
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { z } from "zod";

import { RecommendationSchema, RunSchema, TalkSchema } from "../src/index";

export function emitAll(): Record<string, Record<string, unknown>> {
  const opts = { target: "draft-2020-12" as const };
  return {
    talk: z.toJSONSchema(TalkSchema, opts),
    recommendation: z.toJSONSchema(RecommendationSchema, opts),
    run: z.toJSONSchema(RunSchema, opts),
  };
}

if (process.argv[1]?.endsWith("emit.ts")) {
  const dir = join(import.meta.dirname, "..", "schema");
  mkdirSync(dir, { recursive: true });
  for (const [kind, schema] of Object.entries(emitAll())) {
    writeFileSync(join(dir, `${kind}.schema.json`), JSON.stringify(schema, null, 2) + "\n");
  }
  console.log("emitted talk, recommendation, run");
}
```

- [ ] **Step 5: Write the fixtures**

`packages/contracts/fixtures/valid/talk.json`:

```json
{
  "id": 2802,
  "external_id": "SMT26-3750532",
  "title": "Memristive Properties of Ni-DNA Thin-Film Devices",
  "abstract": "DNA is a natural one-dimensional nanowire.",
  "units": ["DPOLY"],
  "topics": ["Organic Electronics"],
  "type": "Oral-In-person",
  "is_invited": false,
  "is_withdrawn": false,
  "start": "2026-03-19T15:12:00.000Z",
  "end": "2026-03-19T15:24:00.000Z",
  "sort_order": 4,
  "presentation_location": null,
  "author_ids": [101, 102],
  "presenter_ids": [101],
  "publication_reference": null,
  "funding_acknowledgement": "NSF",
  "team_acknowledgement": null,
  "session_id": 245,
  "session_title": "Organic Electronics & Photonics",
  "session_code": "MAR-B31",
  "session_type": "ORAL",
  "session_topics": ["Organic Electronics"],
  "building": "Convention Center",
  "room": "Bluebird 3C"
}
```

`packages/contracts/fixtures/valid/recommendation.json`:

```json
{
  "for_talk_id": 0,
  "candidate_id": 12772,
  "score": 0.8,
  "rank": 1,
  "match": true,
  "cross_domain": true,
  "why": "Both read carrier dynamics from the photocurrent transient.",
  "strongest_parallel": "Time-resolved photocurrent as the readout of carrier dynamics.",
  "shared_methods": ["transient photocurrent measurement"],
  "evidence": { "same_method": 4, "specificity": 3, "usage_parallel": 5, "rubric_sum": 12 },
  "engine_id": "graph_v1",
  "run_id": "graph_v1-20260912T120000Z-a1b2c3",
  "contract_version": 1
}
```

`packages/contracts/fixtures/valid/run.json`:

```json
{
  "run_id": "graph_v1-20260912T120000Z-a1b2c3",
  "engine_id": "graph_v1",
  "kind": "recommend",
  "engine_version": "8a53eac",
  "models": { "extract": "deepseek-chat", "pair_judge": "deepseek-chat", "rubric": "deepseek-reasoner" },
  "corpus_hash": "3f9c1e2b7d4a5c6e",
  "anchor_ids": [0],
  "started_at": "2026-09-12T12:00:00Z",
  "finished_at": "2026-09-12T12:00:34Z",
  "index_path": "out/graph_v1/stage0/index",
  "contract_version": 1
}
```

`packages/contracts/fixtures/invalid/recommendation-score-out-of-range.json`: copy of the valid recommendation with `"score": 12`.

`packages/contracts/fixtures/invalid/recommendation-unknown-key.json`: copy of the valid recommendation plus `"same_method": 4` at top level.

`packages/contracts/fixtures/invalid/talk-missing-title.json`: copy of the valid talk with the `title` key removed.

- [ ] **Step 6: Emit the schema files and run the tests**

Run: `npm run emit --workspace=@repo/contracts && npm run test --workspace=@repo/contracts`
Expected: "emitted talk, recommendation, run"; all tests PASS (3 valid, 3 invalid, 3 drift, 2 counts).

- [ ] **Step 7: Type-check and commit**

Run: `npm run check-types --workspace=@repo/contracts`
Expected: no errors.

```bash
git add packages/contracts package-lock.json
git commit -m "feat(contracts): zod source of truth for Talk, Recommendation, Run with committed JSON Schema"
```

---

### Task 2: Python contract validation against the committed JSON Schema

**Files:**
- Modify: `pipeline/pyproject.toml`
- Create: `pipeline/src/gps_core/__init__.py`, `pipeline/src/gps_core/contracts.py`
- Test: `pipeline/tests/core/__init__.py` (empty), `pipeline/tests/core/test_contracts.py`

- [ ] **Step 1: Add the dependency and the new package to the build**

In `pipeline/pyproject.toml` change the `dependencies` list to add `"jsonschema>=4.23",` and change the wheel packages line to:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/gps_engine", "src/gps_core", "src/gps_data", "src/gps_engines"]
```

Run: `cd /Users/rupertlim/AI_Projects/ConferenceApp/pipeline && uv sync`
Expected: jsonschema installed.

- [ ] **Step 2: Write the failing test**

`pipeline/tests/core/test_contracts.py`:

```python
import json
from pathlib import Path

import pytest

from gps_core.contracts import ContractError, FIXTURES, validate

VALID = FIXTURES / "valid"
INVALID = FIXTURES / "invalid"


@pytest.mark.parametrize("kind", ["talk", "recommendation", "run"])
def test_valid_fixture_passes(kind):
    validate(kind, json.loads((VALID / f"{kind}.json").read_text()))


@pytest.mark.parametrize("path", sorted(INVALID.glob("*.json")), ids=lambda p: p.stem)
def test_invalid_fixture_fails(path: Path):
    kind = path.stem.split("-")[0]
    with pytest.raises(ContractError):
        validate(kind, json.loads(path.read_text()))


def test_unknown_kind():
    with pytest.raises(KeyError):
        validate("nope", {})
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `uv run pytest tests/core/test_contracts.py -q`
Expected: FAIL, "No module named 'gps_core'".

- [ ] **Step 4: Implement**

`pipeline/src/gps_core/__init__.py`:

```python
__version__ = "0.1.0"
```

`pipeline/src/gps_core/contracts.py`:

```python
"""Validate rows against the committed JSON Schema in packages/contracts.
The zod source in packages/contracts/src is the truth; the JSON files are
generated from it and a TypeScript test keeps them in sync."""
import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[3]
SCHEMA_DIR = REPO / "packages" / "contracts" / "schema"
FIXTURES = REPO / "packages" / "contracts" / "fixtures"
KINDS = ("talk", "recommendation", "run")


class ContractError(ValueError):
    """A row does not conform to its contract."""


@lru_cache(maxsize=None)
def validator(kind: str) -> Draft202012Validator:
    if kind not in KINDS:
        raise KeyError(kind)
    schema = json.loads((SCHEMA_DIR / f"{kind}.schema.json").read_text())
    return Draft202012Validator(schema)


def validate(kind: str, row: dict) -> None:
    errors = sorted(validator(kind).iter_errors(row), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        where = "/".join(str(p) for p in first.path) or "<root>"
        raise ContractError(f"{kind} row invalid at {where}: {first.message}")
```

- [ ] **Step 5: Run the tests**

Run: `uv run pytest tests/core/test_contracts.py -q`
Expected: 7 passed.

- [ ] **Step 6: Commit**

```bash
git add pipeline/pyproject.toml pipeline/uv.lock pipeline/src/gps_core pipeline/tests/core
git commit -m "feat(core): validate rows against the committed contract JSON Schema"
```

---

### Task 3: `gps_data` — the 25-field Talk and the archive loader

**Files:**
- Create: `pipeline/src/gps_data/__init__.py`, `pipeline/src/gps_data/talk.py`, `pipeline/src/gps_data/archive.py`
- Test: `pipeline/tests/data/__init__.py` (empty), `pipeline/tests/data/conftest.py`, `pipeline/tests/data/test_talk.py`, `pipeline/tests/data/test_archive.py`

- [ ] **Step 1: Write the failing tests**

`pipeline/tests/data/conftest.py`:

```python
import json

import pytest


@pytest.fixture
def archive(tmp_path):
    """Mimics data/gps2026: events/, presentations/, locations/."""
    for sub in ("events", "presentations", "locations"):
        (tmp_path / sub).mkdir()
    (tmp_path / "locations" / "9001.json").write_text(json.dumps({
        "id": 9001, "external_id": None, "type": "PHYSICAL",
        "building": "Convention Center", "room": "Bluebird 3C"}))
    (tmp_path / "events" / "1.json").write_text(json.dumps({
        "id": 1, "type": "ORAL", "code": "MAR-B31", "title": "Organic Electronics &amp; Photonics",
        "sponsor_units": ["DPOLY"], "topics": ["Organic Electronics"],
        "presentation_ids": [10, 11, 12], "location_ids": [9001],
        "periods": [{"start": "2026-03-16T14:00:00.000Z", "end": "2026-03-16T16:24:00.000Z"}]}))
    base = {"is_invited": False, "is_withdrawn": False, "type": "Oral-In-person",
            "topics": ["Condensed Matter"], "author_ids": [101, 102], "presenter_ids": [101],
            "publication_reference": None, "funding_acknowledgement": "NSF",
            "team_acknowledgement": None, "presentation_location": None,
            "start": "2026-03-16T14:00:00.000Z", "end": "2026-03-16T14:12:00.000Z"}
    rows = [
        dict(base, id=10, external_id="SMT26-0000010", sort_order=1,
             title="Talk&nbsp;ten", abstract="<p>Abstract of ten.</p>"),
        dict(base, id=11, external_id="SMT26-0000011", sort_order=2,
             title="Talk eleven", abstract="Abstract of eleven.",
             author_ids=[102, 103], presenter_ids=[103]),
        dict(base, id=12, external_id="SMT26-0000012", sort_order=3,
             title="Withdrawn talk", abstract="Gone.", is_withdrawn=True),
    ]
    for r in rows:
        (tmp_path / "presentations" / f"{r['id']}.json").write_text(json.dumps(r))
    # a talk with no session at all
    (tmp_path / "presentations" / "13.json").write_text(json.dumps(
        dict(base, id=13, external_id="SMT26-0000013", sort_order=1,
             title="Orphan", abstract="No session.", author_ids=[104], presenter_ids=[104])))
    return tmp_path
```

`pipeline/tests/data/test_talk.py`:

```python
from dataclasses import fields

from gps_core.contracts import validate
from gps_data.talk import Talk, external_anchor, to_row


def test_talk_has_25_fields():
    assert len(fields(Talk)) == 25


def test_external_anchor_is_contract_valid():
    a = external_anchor("Porphyrin nanorods", "Photoconductivity is described.", ["DPOLY"])
    assert a.id == 0 and a.external_id is None and a.units == ("DPOLY",)
    validate("talk", to_row(a))


def test_to_row_uses_lists_not_tuples():
    a = external_anchor("T", "A", ["DPOLY"])
    row = to_row(a)
    assert row["units"] == ["DPOLY"] and row["author_ids"] == []
```

`pipeline/tests/data/test_archive.py`:

```python
from gps_core.contracts import validate
from gps_data.archive import anchors_for, authored_by, clean_text, load_talks
from gps_data.talk import to_row


def test_clean_text():
    assert clean_text("Talk&nbsp;ten") == "Talk ten"
    assert clean_text("<p>H<sub>2</sub>O</p>") == "H2O"
    assert clean_text("&lt;not a tag&gt;") == "<not a tag>"


def test_load_joins_session_and_location_and_excludes_withdrawn(archive):
    talks = load_talks(archive)
    assert set(talks) == {10, 11, 13}
    t = talks[10]
    assert t.title == "Talk ten" and t.abstract == "Abstract of ten."
    assert t.units == ("DPOLY",) and t.session_title == "Organic Electronics & Photonics"
    assert t.session_id == 1 and t.session_code == "MAR-B31" and t.session_type == "ORAL"
    assert t.session_topics == ("Organic Electronics",)
    assert t.building == "Convention Center" and t.room == "Bluebird 3C"
    assert t.external_id == "SMT26-0000010" and t.sort_order == 1
    assert t.author_ids == (101, 102) and t.presenter_ids == (101,)


def test_orphan_talk_has_null_session_fields(archive):
    t = load_talks(archive)[13]
    assert t.session_id is None and t.session_title is None and t.units == ()
    assert t.building is None and t.room is None


def test_every_loaded_talk_is_contract_valid(archive):
    for t in load_talks(archive).values():
        validate("talk", to_row(t))


def test_only_ids_filter(archive):
    assert set(load_talks(archive, only_ids={11})) == {11}


def test_presenter_helpers(archive):
    talks = load_talks(archive)
    assert [t.id for t in anchors_for(talks, 101)] == [10]
    assert authored_by(talks, 102) == {10, 11}
    assert anchors_for(talks, 999) == [] and authored_by(talks, 999) == set()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/data -q`
Expected: FAIL, "No module named 'gps_data'".

- [ ] **Step 3: Implement the Talk record**

`pipeline/src/gps_data/__init__.py`:

```python
from gps_data.talk import Talk, external_anchor, to_row  # noqa: F401
from gps_data.archive import load_talks, anchors_for, authored_by, clean_text  # noqa: F401
```

`pipeline/src/gps_data/talk.py`:

```python
"""The 25-field Talk record: the data layer's output and the engine's input.
Shape is fixed by packages/contracts (talk.schema.json). Engines may read
only id, title, abstract, units, topics."""
from dataclasses import asdict, dataclass, fields


@dataclass(frozen=True)
class Talk:
    id: int
    external_id: str | None
    title: str
    abstract: str
    units: tuple[str, ...]
    topics: tuple[str, ...]
    type: str | None
    is_invited: bool
    is_withdrawn: bool
    start: str | None
    end: str | None
    sort_order: int | None
    presentation_location: str | None
    author_ids: tuple[int, ...]
    presenter_ids: tuple[int, ...]
    publication_reference: str | None
    funding_acknowledgement: str | None
    team_acknowledgement: str | None
    session_id: int | None
    session_title: str | None
    session_code: str | None
    session_type: str | None
    session_topics: tuple[str, ...]
    building: str | None
    room: str | None


_LIST_FIELDS = {"units", "topics", "author_ids", "presenter_ids", "session_topics"}


def to_row(t: Talk) -> dict:
    row = asdict(t)
    for k in _LIST_FIELDS:
        row[k] = list(row[k])
    return row


def from_row(row: dict) -> Talk:
    kw = {f.name: row[f.name] for f in fields(Talk)}
    for k in _LIST_FIELDS:
        kw[k] = tuple(kw[k])
    return Talk(**kw)


def external_anchor(title: str, abstract: str, units: list[str]) -> Talk:
    """A paper that is not in the programme: id 0, text and units only."""
    return Talk(
        id=0, external_id=None, title=title, abstract=abstract,
        units=tuple(units), topics=(), type=None, is_invited=False,
        is_withdrawn=False, start=None, end=None, sort_order=None,
        presentation_location=None, author_ids=(), presenter_ids=(),
        publication_reference=None, funding_acknowledgement=None,
        team_acknowledgement=None, session_id=None, session_title=None,
        session_code=None, session_type=None, session_topics=(),
        building=None, room=None,
    )
```

- [ ] **Step 4: Implement the loader**

`pipeline/src/gps_data/archive.py`:

```python
"""Load Talk records from the crawled GPS archive (data/gps2026): join each
presentation to its event (session) and the event's first location. Withdrawn
talks are excluded here, once, for everyone."""
import html
import json
import re
from pathlib import Path

from gps_data.talk import Talk

_TAG = re.compile(r"<[^>]+>")


def clean_text(s: str | None) -> str:
    # Tags first, entities second: escaped angle brackets (&lt;) stay text.
    s = _TAG.sub("", s or "")
    s = html.unescape(s)
    return " ".join(s.split())


def _opt(s) -> str | None:
    s = clean_text(s) if isinstance(s, str) else s
    return s or None


def _read_dir(d: Path) -> list[dict]:
    return [json.loads(f.read_text()) for f in sorted(d.glob("*.json"))]


def load_talks(archive: Path, only_ids: set[int] | None = None) -> dict[int, Talk]:
    events = _read_dir(archive / "events")
    locations = {l["id"]: l for l in _read_dir(archive / "locations")} \
        if (archive / "locations").exists() else {}
    event_by_pid = {pid: e for e in events for pid in e.get("presentation_ids") or []}
    talks: dict[int, Talk] = {}
    for p in _read_dir(archive / "presentations"):
        pid = p["id"]
        if p.get("is_withdrawn") or (only_ids is not None and pid not in only_ids):
            continue
        e = event_by_pid.get(pid)
        loc = None
        if e and e.get("location_ids"):
            loc = locations.get(e["location_ids"][0])
        talks[pid] = Talk(
            id=pid,
            external_id=p.get("external_id") or None,
            title=clean_text(p.get("title")),
            abstract=clean_text(p.get("abstract")),
            units=tuple((e or {}).get("sponsor_units") or []),
            topics=tuple(p.get("topics") or []),
            type=p.get("type") or None,
            is_invited=bool(p.get("is_invited")),
            is_withdrawn=bool(p.get("is_withdrawn")),
            start=p.get("start"), end=p.get("end"),
            sort_order=p.get("sort_order"),
            presentation_location=_opt(p.get("presentation_location")),
            author_ids=tuple(p.get("author_ids") or []),
            presenter_ids=tuple(p.get("presenter_ids") or []),
            publication_reference=_opt(p.get("publication_reference")),
            funding_acknowledgement=_opt(p.get("funding_acknowledgement")),
            team_acknowledgement=_opt(p.get("team_acknowledgement")),
            session_id=e["id"] if e else None,
            session_title=_opt(e.get("title")) if e else None,
            session_code=(e.get("code") or None) if e else None,
            session_type=(e.get("type") or None) if e else None,
            session_topics=tuple((e or {}).get("topics") or []),
            building=(loc or {}).get("building") or None,
            room=(loc or {}).get("room") or None,
        )
    return talks


def anchors_for(talks: dict[int, Talk], presenter_id: int) -> list[Talk]:
    """The talks a presenter presents, in id order."""
    return sorted((t for t in talks.values() if presenter_id in t.presenter_ids),
                  key=lambda t: t.id)


def authored_by(talks: dict[int, Talk], presenter_id: int) -> set[int]:
    """Every talk the person is an author on — the exclusion set."""
    return {t.id for t in talks.values() if presenter_id in t.author_ids}
```

- [ ] **Step 5: Run the tests**

Run: `uv run pytest tests/data -q`
Expected: 9 passed.

- [ ] **Step 6: Commit**

```bash
git add pipeline/src/gps_data pipeline/tests/data
git commit -m "feat(data): 25-field Talk record, archive loader, presenter resolution"
```

---

### Task 4: `gps_core.records` — Recommendation and RunManifest

**Files:**
- Create: `pipeline/src/gps_core/records.py`
- Test: `pipeline/tests/core/test_records.py`

- [ ] **Step 1: Write the failing test**

`pipeline/tests/core/test_records.py`:

```python
import pytest

from gps_core.contracts import ContractError, validate
from gps_core.records import CONTRACT_VERSION, Recommendation, RunManifest


def rec(**kw):
    base = dict(for_talk_id=0, candidate_id=12772, score=0.8, rank=1, match=True,
                cross_domain=True, why="w", strongest_parallel="p",
                shared_methods=("transient photocurrent",),
                evidence={"rubric_sum": 12}, engine_id="graph_v1", run_id="r1")
    return Recommendation(**{**base, **kw})


def test_recommendation_row_is_contract_valid():
    validate("recommendation", rec().to_row())


def test_recommendation_row_carries_contract_version():
    assert rec().to_row()["contract_version"] == CONTRACT_VERSION == 1


def test_recommendation_score_out_of_range_is_rejected_by_contract():
    with pytest.raises(ContractError):
        validate("recommendation", rec(score=1.5).to_row())


def test_manifest_row_is_contract_valid():
    m = RunManifest(run_id="r1", engine_id="graph_v1", kind="recommend",
                    engine_version="abc1234", models={"rubric": "deepseek-reasoner"},
                    corpus_hash="deadbeef", anchor_ids=(0,),
                    started_at="2026-09-12T12:00:00Z", finished_at="2026-09-12T12:00:34Z",
                    index_path="out/x")
    validate("run", m.to_row())
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/core/test_records.py -q`
Expected: FAIL, "No module named 'gps_core.records'".

- [ ] **Step 3: Implement**

`pipeline/src/gps_core/records.py`:

```python
"""The engine's output records. Shapes are fixed by packages/contracts."""
from dataclasses import asdict, dataclass, field

CONTRACT_VERSION = 1


@dataclass(frozen=True)
class Recommendation:
    for_talk_id: int
    candidate_id: int
    score: float                 # 0..1, higher is better
    rank: int                    # 1 is best within for_talk_id
    match: bool
    cross_domain: bool
    why: str
    strongest_parallel: str
    shared_methods: tuple[str, ...]
    evidence: dict
    engine_id: str
    run_id: str

    def to_row(self) -> dict:
        row = asdict(self)
        row["shared_methods"] = list(self.shared_methods)
        row["contract_version"] = CONTRACT_VERSION
        return row


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    engine_id: str
    kind: str                    # "index" | "recommend"
    engine_version: str
    models: dict
    corpus_hash: str
    anchor_ids: tuple[int, ...]
    started_at: str
    finished_at: str
    index_path: str | None = None
    extra: dict = field(default_factory=dict)   # not in the contract; kept out of to_row

    def to_row(self) -> dict:
        row = asdict(self)
        row.pop("extra")
        row["anchor_ids"] = list(self.anchor_ids)
        row["contract_version"] = CONTRACT_VERSION
        return row
```

- [ ] **Step 4: Run the tests, then commit**

Run: `uv run pytest tests/core -q`
Expected: 11 passed.

```bash
git add pipeline/src/gps_core/records.py pipeline/tests/core/test_records.py
git commit -m "feat(core): Recommendation and RunManifest records"
```

---

### Task 5: `gps_core.checkpoint` and `gps_core.progress` (lifted from the scripts)

**Files:**
- Create: `pipeline/src/gps_core/checkpoint.py`, `pipeline/src/gps_core/progress.py`
- Test: `pipeline/tests/core/test_checkpoint.py`, `pipeline/tests/core/test_progress.py`

- [ ] **Step 1: Write the failing tests**

`pipeline/tests/core/test_checkpoint.py`:

```python
import json

from gps_core.checkpoint import checkpointed, content_key


def test_content_key_is_stable_and_order_independent_for_dicts():
    a = content_key("graph_v1", "methods", {"id": 1, "title": "t"})
    b = content_key("graph_v1", "methods", {"title": "t", "id": 1})
    assert a == b and len(a) == 24


def test_content_key_changes_when_any_part_changes():
    base = content_key("graph_v1", "methods", {"id": 1})
    assert content_key("graph_v2", "methods", {"id": 1}) != base
    assert content_key("graph_v1", "claims", {"id": 1}) != base
    assert content_key("graph_v1", "methods", {"id": 2}) != base


def test_checkpointed_runs_once_and_resumes(tmp_path):
    calls = []
    p = tmp_path / "x.json"
    assert checkpointed(p, lambda: calls.append(1) or {"v": 1}) == {"v": 1}
    assert checkpointed(p, lambda: calls.append(1) or {"v": 2}) == {"v": 1}
    assert calls == [1]
    assert json.loads(p.read_text()) == {"v": 1}
    assert not p.with_suffix(".tmp").exists()
```

`pipeline/tests/core/test_progress.py`:

```python
import json

from gps_core.progress import Status, parallel


def test_status_writes_probeable_file(tmp_path, capsys):
    s = Status(tmp_path)
    s.set("extraction 3/10")
    d = json.loads((tmp_path / "status.json").read_text())
    assert d["phase"] == "extraction 3/10" and isinstance(d["elapsed_s"], int)
    assert "extraction 3/10" in capsys.readouterr().out


def test_parallel_preserves_order_and_reports(tmp_path):
    s = Status(tmp_path)
    out = parallel("sq", [3, 1, 2], lambda x: x * x, workers=2, status=s)
    assert out == [9, 1, 4]
    assert json.loads((tmp_path / "status.json").read_text())["phase"] == "sq 3/3"
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/core/test_checkpoint.py tests/core/test_progress.py -q`
Expected: FAIL, modules not found.

- [ ] **Step 3: Implement**

`pipeline/src/gps_core/checkpoint.py`:

```python
"""Skip-if-exists checkpoints so a stopped run resumes instead of restarting.
Keys are CONTENT hashes (engine id + stage + inputs), so a prompt, model or
input change can never silently reuse a stale result."""
import hashlib
import json
from pathlib import Path
from typing import Callable


def content_key(*parts) -> str:
    blob = json.dumps(parts, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:24]


def checkpointed(path: Path, fn: Callable[[], object]):
    if path.exists():
        return json.loads(path.read_text())
    result = fn()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(result))
    tmp.rename(path)
    return result
```

`pipeline/src/gps_core/progress.py`:

```python
"""Live progress the user can probe at any time: out/status.json plus a
printed line. parallel() runs fn over items on a thread pool, preserves
input order, and reports every few completions."""
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class Status:
    def __init__(self, out: Path):
        self.out = out
        self.t0 = time.time()
        out.mkdir(parents=True, exist_ok=True)

    def set(self, msg: str) -> None:
        elapsed = round(time.time() - self.t0)
        (self.out / "status.json").write_text(json.dumps(
            {"phase": msg, "elapsed_s": elapsed}))
        print(f"[{elapsed}s] {msg}", flush=True)


def parallel(label: str, items: Iterable[T], fn: Callable[[T], R],
             workers: int = 8, status: Status | None = None,
             every: int = 10) -> list[R]:
    items = list(items)
    done = 0
    lock = threading.Lock()

    def wrapped(item: T) -> R:
        nonlocal done
        r = fn(item)
        with lock:
            done += 1
            if status and (done % every == 0 or done == len(items)):
                status.set(f"{label} {done}/{len(items)}")
        return r

    if not items:
        return []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(wrapped, items))
```

- [ ] **Step 4: Run the tests, then commit**

Run: `uv run pytest tests/core -q`
Expected: 16 passed.

```bash
git add pipeline/src/gps_core/checkpoint.py pipeline/src/gps_core/progress.py pipeline/tests/core
git commit -m "feat(core): content-keyed checkpoints and probeable progress"
```

---

### Task 6: Move the LLM seam into core; add the Engine protocol and registry

**Files:**
- Move: `pipeline/src/gps_engine/llm.py` → `pipeline/src/gps_core/llm.py`; `pipeline/tests/test_llm.py` → `pipeline/tests/core/test_llm.py`
- Create: `pipeline/src/gps_core/protocol.py`, `pipeline/src/gps_core/registry.py`
- Modify: every `from gps_engine.llm import` in `pipeline/src/gps_engine/*.py`, `pipeline/tests/*.py`, `pipeline/scripts/*.py`
- Test: `pipeline/tests/core/test_registry.py`

- [ ] **Step 1: Move the LLM module and fix imports**

```bash
cd /Users/rupertlim/AI_Projects/ConferenceApp/pipeline
git mv src/gps_engine/llm.py src/gps_core/llm.py
git mv tests/test_llm.py tests/core/test_llm.py
grep -rl "gps_engine.llm" src tests scripts | xargs sed -i '' 's/gps_engine\.llm/gps_core.llm/g'
uv run pytest -q
```

Expected: 113 passed (97 existing + 16 core), zero import errors.

- [ ] **Step 2: Write the failing registry test**

`pipeline/tests/core/test_registry.py`:

```python
import pytest

from gps_core import registry
from gps_core.protocol import Engine, IndexArtifact


class DummyEngine:
    id = "dummy"
    models = {}

    def index(self, corpus, out):
        return IndexArtifact(path=out, engine_id=self.id)

    def recommend(self, anchor, index):
        return []


def build_dummy(**kw):
    return DummyEngine()


def test_get_engine_by_name(monkeypatch):
    monkeypatch.setitem(registry.ENGINES, "dummy", f"{__name__}:build_dummy")
    e = registry.get_engine("dummy")
    assert isinstance(e, Engine) and e.id == "dummy"


def test_unknown_engine_lists_known_names():
    with pytest.raises(KeyError, match="graph_v1"):
        registry.get_engine("nope")


def test_graph_v1_is_registered():
    assert "graph_v1" in registry.ENGINES
```

- [ ] **Step 3: Run to verify it fails**

Run: `uv run pytest tests/core/test_registry.py -q`
Expected: FAIL, "No module named 'gps_core.registry'".

- [ ] **Step 4: Implement**

`pipeline/src/gps_core/protocol.py`:

```python
"""The engine contract: two functions. Everything else is the engine's own."""
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from gps_core.records import Recommendation
from gps_data.talk import Talk


@dataclass(frozen=True)
class IndexArtifact:
    """Opaque, engine-owned. Core only records its path in the manifest."""
    path: Path
    engine_id: str


@runtime_checkable
class Engine(Protocol):
    id: str
    models: dict            # stage -> model name, recorded in the manifest

    def index(self, corpus: list[Talk], out: Path) -> IndexArtifact: ...

    def recommend(self, anchor: Talk, index: IndexArtifact) -> list[Recommendation]: ...
```

`pipeline/src/gps_core/registry.py`:

```python
"""One line per engine. ENGINE=<name> selects it. Value is "module:factory";
the factory takes keyword config and returns an Engine."""
import importlib

from gps_core.protocol import Engine

ENGINES: dict[str, str] = {
    "graph_v1": "gps_engines.graph_v1.engine:build",
}


def get_engine(name: str, **config) -> Engine:
    try:
        target = ENGINES[name]
    except KeyError:
        raise KeyError(f"unknown engine {name!r}; known: {sorted(ENGINES)}") from None
    module, factory = target.split(":")
    return getattr(importlib.import_module(module), factory)(**config)
```

- [ ] **Step 5: Run the tests, then commit**

Run: `uv run pytest tests/core -q`
Expected: all pass (the `test_graph_v1_is_registered` test passes because the name is in the dict; the module itself is created in Task 9).

```bash
git add -A pipeline/src/gps_core pipeline/src/gps_engine pipeline/tests pipeline/scripts
git commit -m "refactor(core): LLM seam moves to gps_core; Engine protocol and registry"
```

---

### Task 7: `gps_core.filters`, `gps_core.run`, `gps_core.store`

**Files:**
- Create: `pipeline/src/gps_core/filters.py`, `pipeline/src/gps_core/run.py`, `pipeline/src/gps_core/store.py`
- Test: `pipeline/tests/core/test_filters.py`, `pipeline/tests/core/test_run.py`

- [ ] **Step 1: Write the failing tests**

`pipeline/tests/core/test_filters.py`:

```python
from gps_core.filters import default_cross_domain, exclude_authored, ranked
from gps_core.records import Recommendation
from gps_data.talk import external_anchor


def rec(cid, score, for_talk=0):
    return Recommendation(for_talk_id=for_talk, candidate_id=cid, score=score, rank=0,
                          match=True, cross_domain=False, why="", strongest_parallel="",
                          shared_methods=(), evidence={}, engine_id="e", run_id="r")


def test_cross_domain_requires_affirmative_evidence():
    a = external_anchor("a", "x", ["DPOLY"])
    assert default_cross_domain(a, external_anchor("b", "x", ["DBIO"])) is True
    assert default_cross_domain(a, external_anchor("b", "x", ["DPOLY", "DBIO"])) is False
    assert default_cross_domain(a, external_anchor("b", "x", [])) is False
    assert default_cross_domain(external_anchor("a", "x", []), a) is False


def test_exclude_authored_drops_own_work():
    rows = [rec(1, 0.9), rec(2, 0.8), rec(3, 0.7)]
    assert [r.candidate_id for r in exclude_authored(rows, {2})] == [1, 3]


def test_ranked_orders_by_score_then_id_within_each_anchor():
    rows = [rec(5, 0.5), rec(3, 0.9), rec(4, 0.9), rec(9, 1.0, for_talk=7)]
    out = ranked(rows)
    assert [(r.for_talk_id, r.candidate_id, r.rank) for r in out] == [
        (0, 3, 1), (0, 4, 2), (0, 5, 3), (7, 9, 1)]
```

`pipeline/tests/core/test_run.py`:

```python
import json
from dataclasses import replace
from pathlib import Path

from gps_core.contracts import validate
from gps_core.protocol import IndexArtifact
from gps_core.records import Recommendation
from gps_core.run import corpus_hash, run_index, run_recommend
from gps_core.store import write_seed
from gps_data.talk import external_anchor


class StubEngine:
    id = "stub"
    models = {"judge": "none"}

    def index(self, corpus, out):
        (out / "index.json").write_text(json.dumps(sorted(t.id for t in corpus)))
        return IndexArtifact(path=out, engine_id=self.id)

    def recommend(self, anchor, index):
        return [Recommendation(for_talk_id=anchor.id, candidate_id=cid, score=s, rank=0,
                               match=s >= 0.5, cross_domain=False, why="w",
                               strongest_parallel="", shared_methods=(),
                               evidence={}, engine_id=self.id, run_id="")
                for cid, s in ((11, 0.9), (10, 0.9), (12, 0.2))]


def corpus():
    return [replace(external_anchor(f"t{i}", "a", ["DPOLY"]), id=i) for i in (10, 11, 12)]


def test_corpus_hash_is_order_independent():
    c = corpus()
    assert corpus_hash(c) == corpus_hash(list(reversed(c)))


def test_run_index_writes_manifest(tmp_path):
    art, man = run_index(StubEngine(), corpus(), tmp_path / "idx")
    assert art.path == tmp_path / "idx" and man.kind == "index"
    validate("run", json.loads((tmp_path / "idx" / "run.json").read_text()))


def test_run_recommend_ranks_filters_validates_and_writes(tmp_path):
    e = StubEngine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    anchor = external_anchor("mine", "a", ["DPOLY"])
    rows, man = run_recommend(e, anchor, art, tmp_path / "q", authored_ids={12})
    assert [(r.candidate_id, r.rank) for r in rows] == [(10, 1), (11, 2)]
    assert all(r.run_id == man.run_id for r in rows)
    saved = json.loads((tmp_path / "q" / "recommendations.json").read_text())
    for row in saved:
        validate("recommendation", row)
    validate("run", json.loads((tmp_path / "q" / "run.json").read_text()))
    assert man.index_path == str(art.path) and man.anchor_ids == (0,)


def test_write_seed_is_contract_valid(tmp_path):
    e = StubEngine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    rows, man = run_recommend(e, external_anchor("m", "a", []), art, tmp_path / "q")
    seed = write_seed(tmp_path / "seed.json", corpus(), rows, [man])
    d = json.loads((tmp_path / "seed.json").read_text())
    assert d["contract_version"] == 1 and len(d["talks"]) == 3 and len(d["runs"]) == 1
    for t in d["talks"]:
        validate("talk", t)
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/core/test_filters.py tests/core/test_run.py -q`
Expected: FAIL, modules not found.

- [ ] **Step 3: Implement**

`pipeline/src/gps_core/filters.py`:

```python
"""Rules every engine inherits: the default cross-domain test, the
own-work exclusion, and deterministic ranking."""
from dataclasses import replace

from gps_core.records import Recommendation
from gps_data.talk import Talk


def default_cross_domain(anchor: Talk, cand: Talk) -> bool:
    """Unknown units never count as cross-domain: a surprise pick needs
    affirmative evidence that the two talks live in different divisions."""
    return bool(anchor.units) and bool(cand.units) and not (set(anchor.units) & set(cand.units))


def exclude_authored(rows: list[Recommendation], authored_ids: set[int]) -> list[Recommendation]:
    return [r for r in rows if r.candidate_id not in authored_ids]


def ranked(rows: list[Recommendation]) -> list[Recommendation]:
    """rank = 1..n within each for_talk_id, by score desc then candidate_id asc."""
    out: list[Recommendation] = []
    by_anchor: dict[int, list[Recommendation]] = {}
    for r in rows:
        by_anchor.setdefault(r.for_talk_id, []).append(r)
    for anchor_id in sorted(by_anchor):
        rs = sorted(by_anchor[anchor_id], key=lambda r: (-r.score, r.candidate_id))
        out.extend(replace(r, rank=i + 1) for i, r in enumerate(rs))
    return out
```

`pipeline/src/gps_core/run.py`:

```python
"""Drive any Engine through the two contract operations, record a manifest,
apply core filters, validate every row, and save results. Engines never
touch files outside their own artifact; core owns run.json and
recommendations.json."""
import hashlib
import json
import subprocess
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
    import importlib
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
    rows = [Recommendation(**{**r.__dict__, "run_id": run_id, "for_talk_id": anchor.id})
            for r in rows]
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
```

`pipeline/src/gps_core/store.py`:

```python
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
```

- [ ] **Step 4: Run the tests, then commit**

Run: `uv run pytest tests/core -q`
Expected: all pass.

```bash
git add pipeline/src/gps_core pipeline/tests/core
git commit -m "feat(core): filters, run driver with manifests and validation, seed writer"
```

---

### Task 8: Move `gps_engine` → `gps_engines/graph_v1`; Talk comes from `gps_data`

**Files:**
- Move: `pipeline/src/gps_engine/{li_extraction,claims,filing,cascade,similarity,graph,funnel,rubric,recommend,physh,sampling}.py` → `pipeline/src/gps_engines/graph_v1/`
- Move: `pipeline/src/gps_engine/app_export.py` → `pipeline/src/gps_data/legacy_seed.py`
- Delete: `pipeline/src/gps_engine/corpus.py`, `pipeline/src/gps_engine/__init__.py`
- Move tests: `pipeline/tests/test_{claims,funnel,graph,li_extraction,physh_cascade,recommend,rubric,sampling,similarity}.py` → `pipeline/tests/graph_v1/`; `tests/test_app_export.py` → `tests/data/test_legacy_seed.py`; `tests/test_corpus.py` deleted (covered by Task 3); `tests/test_scaffold.py` updated
- Modify: `pipeline/pyproject.toml` packages list; `pipeline/scripts/build_sample.py`, `pipeline/scripts/select_negatives.py` imports

- [ ] **Step 1: Move files with git**

```bash
cd /Users/rupertlim/AI_Projects/ConferenceApp/pipeline
mkdir -p src/gps_engines/graph_v1 tests/graph_v1
touch src/gps_engines/__init__.py tests/graph_v1/__init__.py
for m in li_extraction claims filing cascade similarity graph funnel rubric recommend physh sampling; do
  git mv src/gps_engine/$m.py src/gps_engines/graph_v1/$m.py
done
git mv src/gps_engine/app_export.py src/gps_data/legacy_seed.py
git rm -q src/gps_engine/corpus.py src/gps_engine/__init__.py tests/test_corpus.py
for t in claims funnel graph li_extraction physh_cascade recommend rubric sampling similarity; do
  git mv tests/test_$t.py tests/graph_v1/test_$t.py
done
git mv tests/test_app_export.py tests/data/test_legacy_seed.py
git mv tests/conftest.py tests/graph_v1/conftest.py
printf '"""graph_v1: methods-only graph + PhySH cascade + rubric. See engine.py."""\n' > src/gps_engines/graph_v1/__init__.py
```

- [ ] **Step 2: Rewrite imports**

```bash
grep -rl "gps_engine\." src tests scripts | xargs sed -i '' \
  -e 's/from gps_engine\.corpus import Talk, load_talks/from gps_data.talk import Talk\nfrom gps_data.archive import load_talks/' \
  -e 's/from gps_engine\.corpus import Talk/from gps_data.talk import Talk/' \
  -e 's/from gps_engine\.corpus import load_talks/from gps_data.archive import load_talks/' \
  -e 's/gps_engine\.app_export/gps_data.legacy_seed/g' \
  -e 's/gps_engine\./gps_engines.graph_v1./g'
grep -rn "gps_engine\b" src tests scripts || echo "no stale gps_engine imports"
```

Then in `pipeline/pyproject.toml` set:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/gps_core", "src/gps_data", "src/gps_engines"]
```

And replace `tests/test_scaffold.py` with:

```python
def test_packages_import():
    import gps_core, gps_data, gps_engines.graph_v1  # noqa: F401
    assert gps_core.__version__ == "0.1.0"
```

- [ ] **Step 3: Fix the `physh.py` resource path**

`load_physh` locates `resources/physh.json.gz` via `Path(__file__).resolve().parents[2]`; the file is now one level deeper. Change that line in `src/gps_engines/graph_v1/physh.py` to `parents[3]`.

- [ ] **Step 4: Adapt tests that construct `Talk` positionally or with the old field set**

Any test that builds `Talk(id=..., title=..., abstract=..., topics=(), units=(), session_title="", start=None, end=None)` must now build it via `gps_data.talk.external_anchor(title, abstract, units)` and `dataclasses.replace(..., id=<id>)`. Add this helper at the top of each affected test module (`tests/graph_v1/test_rubric.py`, `tests/graph_v1/test_li_extraction.py`, `tests/graph_v1/test_claims.py`, and any other that fails in Step 5):

```python
from dataclasses import replace
from gps_data.talk import external_anchor

def mk_talk(id, title, abstract, units=()):
    return replace(external_anchor(title, abstract, list(units)), id=id)
```

and replace the old constructor calls with `mk_talk(...)`.

- [ ] **Step 5: Run the whole suite**

Run: `uv sync && uv run pytest -q`
Expected: all previously passing tests pass under their new paths (count = old 97 − 2 corpus tests + 30 new core/data tests, give or take the Task 8 helper edits); zero import errors. Fix any residual import until green.

- [ ] **Step 6: Commit**

```bash
git add -A pipeline
git commit -m "refactor: gps_engine becomes gps_engines/graph_v1; Talk lives in gps_data"
```

---

### Task 9: `GraphV1Engine` — `index()` and `recommend()` assembled once

**Files:**
- Create: `pipeline/src/gps_engines/graph_v1/engine.py`
- Test: `pipeline/tests/graph_v1/fakes.py`, `pipeline/tests/graph_v1/test_engine.py`

- [ ] **Step 1: Write the routing fake and the failing test**

`pipeline/tests/graph_v1/fakes.py`:

```python
"""Deterministic stand-ins: an LLM that answers by prompt type, an embedder
that answers by keyword, and a 6-node PhySH tree."""
from gps_engines.graph_v1.physh import PhySH


class RoutingFakeLLM:
    """Routes on the prompt text so call ORDER does not matter (the engine
    runs stages on a thread pool)."""

    def __init__(self, methods_by_title: dict[str, list[str]],
                 rubric_by_title: dict[str, dict]):
        self.methods_by_title = methods_by_title
        self.rubric_by_title = rubric_by_title
        self.prompts: list[str] = []

    def _title_in(self, prompt: str, table: dict):
        for title, val in table.items():
            if title in prompt:
                return val
        return None

    def complete_json(self, prompt: str, schema_hint: str) -> dict:
        self.prompts.append(prompt)
        if "List every method" in prompt:                       # extraction
            return {"methods": self._title_in(prompt, self.methods_by_title) or []}
        if "missed_methods" in prompt:                          # glean + describe
            ms = self._title_in(prompt, self.methods_by_title) or []
            return {"missed_methods": [], "descriptions": {m: f"uses {m}" for m in ms}}
        if "factual claims" in prompt:                          # claims
            return {"claims": []}
        if "File the method onto" in prompt:                    # PhySH filing
            return {"assignments": []}
        if "Two research-method names" in prompt:               # pair judge
            return {"verdict": "related", "strength": 7, "why": "kin"}
        if "METHOD-related" in prompt:                          # rubric
            r = self._title_in(prompt, self.rubric_by_title)
            return r or {"strongest_parallel": "none", "same_method": 0,
                         "specificity": 0, "usage_parallel": 0, "match": False, "why": "no"}
        raise AssertionError(f"unrouted prompt: {prompt[:80]!r}")


def keyword_embedder(texts: list[str]) -> list[list[float]]:
    out = []
    for t in texts:
        t = t.lower()
        if "photocurrent" in t:
            out.append([1.0, 0.0, 0.0])
        elif "self-assembl" in t:
            out.append([0.0, 1.0, 0.0])
        else:
            out.append([0.0, 0.0, 1.0])
    return out


def tiny_physh() -> PhySH:
    label = {"opt": "Optical techniques", "pl": "Photoluminescence",
             "pc": "Photocurrent", "sp": "Sample preparation",
             "sa": "Self-assembly", "lb": "Langmuir-Blodgett deposition"}
    broader = {"pl": ["opt"], "pc": ["opt"], "sa": ["sp"], "lb": ["sa"], "opt": [], "sp": []}
    facet = {k: "Experimental Techniques" for k in label}
    return PhySH(label, {k: [] for k in label}, broader, facet)
```

`pipeline/tests/graph_v1/test_engine.py`:

```python
import json
from dataclasses import replace

from gps_core.contracts import validate
from gps_core.protocol import Engine
from gps_core.run import run_index, run_recommend
from gps_data.talk import external_anchor
from gps_engines.graph_v1.engine import GraphV1Engine, build

from .fakes import RoutingFakeLLM, keyword_embedder, tiny_physh

ANCHOR_T = "Photoconductivity of Self-Assembled Porphyrin Nanorods"
PEROV_T = "Ultrafast transient photocurrent in hybrid lead halide perovskites"
GEMS_T = "Raman spectroscopy, a definitive tool for eliminating Diamond simulants"


def corpus():
    return [replace(external_anchor(PEROV_T, "We performed transient photocurrent measurements.", ["DLS"]), id=12772),
            replace(external_anchor(GEMS_T, "We compare Raman signatures.", ["GIMS"]), id=9856)]


def make_engine():
    llm = RoutingFakeLLM(
        methods_by_title={ANCHOR_T: ["photocurrent measurement", "self-assembly"],
                          PEROV_T: ["transient photocurrent"],
                          GEMS_T: ["raman spectroscopy"]},
        rubric_by_title={PEROV_T: {"strongest_parallel": "time-resolved photocurrent",
                                   "same_method": 4, "specificity": 3, "usage_parallel": 5,
                                   "match": True, "why": "same readout"}})
    return GraphV1Engine(extract_llm=llm, pair_llm=llm, rubric_llm=llm,
                         embed=keyword_embedder, physh=tiny_physh(), workers=1,
                         models={"extract": "fake", "pair_judge": "fake", "rubric": "fake"}), llm


def test_build_returns_an_engine_with_models():
    e = build(provider="deepseek", embed=keyword_embedder, physh=tiny_physh(), llm_factory=lambda m: None)
    assert isinstance(e, Engine) and e.id == "graph_v1" and e.models["rubric"] == "deepseek-reasoner"


def test_index_writes_graph_and_context(tmp_path):
    e, _ = make_engine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    assert (art.path / "graph.json").exists() and (art.path / "name_context.json").exists()
    g = json.loads((art.path / "graph.json").read_text())
    assert set(g["canon"]) == {"transient photocurrent", "raman spectroscopy"}


def test_index_is_resumable(tmp_path):
    e, llm = make_engine()
    run_index(e, corpus(), tmp_path / "idx")
    n = len(llm.prompts)
    run_index(e, corpus(), tmp_path / "idx")
    assert len(llm.prompts) == n           # every stage hit its checkpoint


def test_recommend_scores_from_rubric_and_names_shared_methods(tmp_path):
    e, _ = make_engine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    anchor = external_anchor(ANCHOR_T, "Nanorods self-assembled; photocurrent measured.", ["DPOLY"])
    rows, _ = run_recommend(e, anchor, art, tmp_path / "q")
    assert [r.candidate_id for r in rows] == [12772]          # gems never funneled
    r = rows[0]
    assert r.score == (4 + 3 + 5) / 15 and r.match is True and r.rank == 1
    assert r.cross_domain is True
    assert r.evidence == {"same_method": 4, "specificity": 3, "usage_parallel": 5,
                          "rubric_sum": 12, "match_min_score": 5}
    assert r.shared_methods == ("photocurrent measurement ~ transient photocurrent",)
    validate("recommendation", r.to_row())


def test_recommend_below_threshold_is_reported_not_matched(tmp_path):
    e, llm = make_engine()
    llm.rubric_by_title[PEROV_T] = {"strongest_parallel": "weak", "same_method": 2,
                                    "specificity": 1, "usage_parallel": 1, "match": True, "why": "w"}
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    rows, _ = run_recommend(e, external_anchor(ANCHOR_T, "x", ["DPOLY"]), art, tmp_path / "q")
    assert rows[0].match is False and rows[0].score == 4 / 15
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/graph_v1/test_engine.py -q`
Expected: FAIL, "No module named 'gps_engines.graph_v1.engine'".

- [ ] **Step 3: Implement the engine**

`pipeline/src/gps_engines/graph_v1/engine.py`:

```python
"""graph_v1 assembled once. index(): extraction → gleaning → claims → PhySH
filing → edge cascade → pair verdicts → graph.json. recommend(): anchor
extraction → filing → bipartite cascade → verdicts → funnel → rubric → rows.
Replaces run_stage0.py / run_stage1_index.py / run_query.py."""
import json
from dataclasses import replace
from pathlib import Path
from typing import Callable

from gps_core.checkpoint import checkpointed, content_key
from gps_core.filters import default_cross_domain
from gps_core.llm import AnthropicLLM, DeepSeekLLM, LLMClient, LLMRefusal
from gps_core.progress import Status, parallel
from gps_core.protocol import IndexArtifact
from gps_core.records import Recommendation
from gps_data.talk import Talk
from gps_engines.graph_v1.cascade import Decision, decide_pairs_bulk, decide_pairs_cross
from gps_engines.graph_v1.claims import claims_digest, extract_claims
from gps_engines.graph_v1.filing import candidate_shortlist, embed_targets, file_method
from gps_engines.graph_v1.funnel import candidates
from gps_engines.graph_v1.graph import MethodGraph
from gps_engines.graph_v1.li_extraction import extract_methods_json, glean_and_describe
from gps_engines.graph_v1.physh import PhySH, load_physh
from gps_engines.graph_v1.rubric import judge_candidate
from gps_engines.graph_v1.similarity import apply_verdicts, judge_pair, sbert_embedder

ENGINE_ID = "graph_v1"
MATCH_MIN_SCORE = 5       # calibrated on the 10+47 ground truth (2026-08-30)
RUBRIC_MAX = 15
ANCHOR_KEY = 0

PROVIDERS = {
    "deepseek": {"extract": "deepseek-chat", "pair_judge": "deepseek-chat",
                 "rubric": "deepseek-reasoner", "client": DeepSeekLLM},
    "anthropic": {"extract": "claude-haiku-4-5-20251001", "pair_judge": "claude-sonnet-5",
                  "rubric": "claude-sonnet-5", "client": AnthropicLLM},
}


def _norm(name: str) -> str:
    return " ".join(str(name).casefold().split())


class GraphV1Engine:
    id = ENGINE_ID

    def __init__(self, extract_llm: LLMClient, pair_llm: LLMClient, rubric_llm: LLMClient,
                 embed: Callable, physh: PhySH, models: dict, workers: int = 8):
        self.extract_llm, self.pair_llm, self.rubric_llm = extract_llm, pair_llm, rubric_llm
        self.embed, self.physh, self.models, self.workers = embed, physh, models, workers
        self._targets = None

    # ---- shared stages -------------------------------------------------

    def _targets_vecs(self):
        if self._targets is None:
            self._targets = embed_targets(self.physh, self.embed)
        return self._targets

    def _ck(self, out: Path, stage: str, *inputs) -> Path:
        return out / stage / f"{content_key(self.id, stage, self.models, *inputs)}.json"

    def _extract(self, out: Path, t: Talk) -> tuple[list[str], dict, list]:
        key = (t.id, t.title, t.abstract)
        ms = checkpointed(self._ck(out, "methods", key),
                          lambda: extract_methods_json(t, self.extract_llm))
        enriched = checkpointed(self._ck(out, "enrich", key, ms),
                                lambda: list(glean_and_describe(t, ms, self.extract_llm)))
        claims = checkpointed(self._ck(out, "claims", key),
                              lambda: extract_claims(t, self.extract_llm))
        return enriched[0], enriched[1], claims

    def _file(self, out: Path, name: str, ctx: str) -> list[dict]:
        return checkpointed(
            self._ck(out, "filings", name, ctx),
            lambda: file_method(name, ctx, candidate_shortlist(
                name, ctx, self.physh, self.embed, self._targets_vecs()), self.physh, self.extract_llm))

    def _judge_pair(self, out: Path, d: Decision, name_context: dict) -> dict:
        def judge():
            try:
                return judge_pair(d.a, d.b, self.pair_llm,
                                  context_a=name_context.get(_norm(d.a), ""),
                                  context_b=name_context.get(_norm(d.b), ""),
                                  evidence=d.evidence)
            except LLMRefusal:
                return {"verdict": "unrelated",
                        "why": "API REFUSAL; defaulted to no-edge, not a real judgment"}
        return checkpointed(self._ck(out, "verdicts", d.a, d.b, d.evidence), judge)

    @staticmethod
    def _verdicts(decisions: list[Decision], judged: dict) -> list[tuple[str, str, dict]]:
        vs = []
        for d in decisions:
            if d.action == "judge":
                vs.append((d.a, d.b, judged[(d.a, d.b)]))
            elif d.action in ("auto-same", "auto-related"):
                vs.append((d.a, d.b, {"verdict": "same" if d.action == "auto-same" else "related",
                                      "strength": d.strength, "why": d.why,
                                      "provenance": d.provenance}))
        return vs

    # ---- contract operations -------------------------------------------

    def index(self, corpus: list[Talk], out: Path) -> IndexArtifact:
        status = Status(out)
        status.set("extraction")
        ordered = sorted(corpus, key=lambda t: t.id)
        extracted = parallel("extraction", ordered, lambda t: (t, *self._extract(out, t)),
                             workers=self.workers, status=status)
        g = MethodGraph()
        name_context: dict[str, str] = {}
        for t, ms, descs, _claims in extracted:
            for m in ms:
                g.link_talk(t.id, m)
                key = _norm(m)
                if key not in name_context:
                    d = descs.get(m) or descs.get(key) or ""
                    name_context[key] = (f'in "{t.title[:70]}": {d}' if d
                                         else f'used in "{t.title[:70]}"')
        status.set("filing")
        names = sorted({n for nid in g.nodes() for n in g.names_of(nid)})
        filed = parallel("filing", names,
                         lambda n: self._file(out, n, name_context.get(_norm(n), "")),
                         workers=self.workers, status=status)
        filings = dict(zip(names, filed))
        status.set("cascade")
        texts = {n: f"{n}: {name_context.get(_norm(n), '')}" for n in names}
        kept, n_dropped = decide_pairs_bulk(names, filings, self.physh, self.embed, texts)
        to_judge = [d for d in kept if d.action == "judge"]
        status.set(f"cascade: {len(kept) - len(to_judge)} auto, {len(to_judge)} to judge, {n_dropped} dropped")
        judged = dict(zip([(d.a, d.b) for d in to_judge],
                          parallel("verdicts", to_judge,
                                   lambda d: self._judge_pair(out, d, name_context),
                                   workers=self.workers, status=status)))
        apply_verdicts(g, self._verdicts(kept, judged))
        g.save(out / "graph.json")
        (out / "name_context.json").write_text(json.dumps(name_context))
        (out / "filings.json").write_text(json.dumps(filings))
        (out / "talks.json").write_text(json.dumps({t.id: {"title": t.title, "abstract": t.abstract,
                                                             "units": list(t.units)} for t in ordered}))
        status.set(f"done — {len(names)} methods, {len(ordered)} talks")
        return IndexArtifact(path=out, engine_id=self.id)

    def recommend(self, anchor: Talk, index: IndexArtifact) -> list[Recommendation]:
        idx = index.path
        out = idx / "queries" / str(anchor.id)
        status = Status(out)
        g = MethodGraph.load(idx / "graph.json")
        name_context = json.loads((idx / "name_context.json").read_text())
        filings = json.loads((idx / "filings.json").read_text())
        talks = {int(k): v for k, v in json.loads((idx / "talks.json").read_text()).items()}

        status.set("anchor extraction")
        ms, descs, anchor_claims = self._extract(idx, anchor)
        existing = sorted({n for nid in g.nodes() for n in g.names_of(nid)})
        for m in ms:
            g.link_talk(ANCHOR_KEY, m)
            key = _norm(m)
            if key not in name_context:
                d = descs.get(m) or descs.get(key) or ""
                name_context[key] = (f'in "{anchor.title[:70]}": {d}' if d
                                     else f'used in "{anchor.title[:70]}"')
        for n in ms:
            if n not in filings:
                filings[n] = self._file(idx, n, name_context.get(_norm(n), ""))

        status.set("bipartite cascade")
        texts = {n: f"{n}: {name_context.get(_norm(n), '')}" for n in set(existing) | set(ms)}
        ds = decide_pairs_cross(ms, existing, filings, self.physh, self.embed, texts)
        to_judge = [d for d in ds if d.action == "judge"]
        judged = dict(zip([(d.a, d.b) for d in to_judge],
                          parallel("verdicts", to_judge,
                                   lambda d: self._judge_pair(idx, d, name_context),
                                   workers=self.workers, status=status)))
        apply_verdicts(g, self._verdicts(ds, judged))

        cands = sorted(candidates(g, talk_id=ANCHOR_KEY, min_strength=0))
        status.set(f"rubric: {len(cands)} candidates")
        anchor_digest = claims_digest(anchor_claims)

        def rubric_one(cid: int) -> dict:
            cand = replace(anchor, id=cid, title=talks[cid]["title"],
                           abstract=talks[cid]["abstract"], units=tuple(talks[cid]["units"]))
            _ms, _d, cand_claims = self._extract(idx, cand)

            def judge():
                try:
                    j = judge_candidate(anchor, cand, self.rubric_llm,
                                        mine_claims=anchor_digest,
                                        cand_claims=claims_digest(cand_claims))
                    return {"same_method": j.same_method, "specificity": j.specificity,
                            "usage_parallel": j.usage_parallel, "why": j.why,
                            "strongest_parallel": j.strongest_parallel}
                except LLMRefusal:
                    return {"same_method": 0, "specificity": 0, "usage_parallel": 0,
                            "strongest_parallel": "",
                            "why": "API REFUSAL; defaulted to no-match, not a real judgment"}
            return checkpointed(self._ck(idx, "judgments", anchor.id, anchor.abstract, cid,
                                         cand.abstract), judge)

        judgments = parallel("rubric", cands, rubric_one, workers=self.workers, status=status)
        rows = []
        for cid, j in zip(cands, judgments):
            total = j["same_method"] + j["specificity"] + j["usage_parallel"]
            cand_units = tuple(talks[cid]["units"])
            rows.append(Recommendation(
                for_talk_id=anchor.id, candidate_id=cid, score=total / RUBRIC_MAX, rank=0,
                match=total >= MATCH_MIN_SCORE,
                cross_domain=default_cross_domain(anchor, replace(anchor, units=cand_units)),
                why=j["why"], strongest_parallel=j["strongest_parallel"],
                shared_methods=tuple(self._shared_methods(g, cid)),
                evidence={"same_method": j["same_method"], "specificity": j["specificity"],
                          "usage_parallel": j["usage_parallel"], "rubric_sum": total,
                          "match_min_score": MATCH_MIN_SCORE},
                engine_id=self.id, run_id=""))
        status.set(f"done — {sum(r.match for r in rows)} matches of {len(rows)} candidates")
        return rows

    @staticmethod
    def _shared_methods(g: MethodGraph, cid: int) -> list[str]:
        """Node names that connect the anchor to the candidate: a shared node
        gives one name; a RELATED_TO hop gives 'anchor-name ~ candidate-name'."""
        out: set[str] = set()
        for n in g.nodes():
            if ANCHOR_KEY not in g.talks_using(n):
                continue
            n_name = sorted(g.names_of(n))[0]
            if cid in g.talks_using(n):
                out.add(n_name)
            for r in g.related_to(n):
                if cid in g.talks_using(r):
                    out.add(f"{n_name} ~ {sorted(g.names_of(r))[0]}")
        return sorted(out)


def build(provider: str = "deepseek", workers: int = 8, embed=None, physh=None,
          llm_factory=None) -> GraphV1Engine:
    """Registry factory. Live clients by default; tests inject fakes."""
    cfg = PROVIDERS[provider]
    make = llm_factory or cfg["client"]
    return GraphV1Engine(
        extract_llm=make(cfg["extract"]), pair_llm=make(cfg["pair_judge"]),
        rubric_llm=make(cfg["rubric"]), embed=embed or sbert_embedder(),
        physh=physh or load_physh(), workers=workers,
        models={"extract": cfg["extract"], "pair_judge": cfg["pair_judge"], "rubric": cfg["rubric"]})
```

- [ ] **Step 4: Run the engine tests**

Run: `uv run pytest tests/graph_v1/test_engine.py -q`
Expected: 5 passed. If `test_recommend_scores_from_rubric_and_names_shared_methods` fails on `shared_methods`, print `g.names_of` for the anchor's nodes: the pair judge returns `related`, so the expected form is `"photocurrent measurement ~ transient photocurrent"`; if the cascade dropped the pair instead of judging it, check that `keyword_embedder` maps both names to the same vector (cosine 1.0 ≥ `SIM_UNFILED` 0.50).

- [ ] **Step 5: Run everything, then commit**

Run: `uv run pytest -q`
Expected: all green.

```bash
git add pipeline/src/gps_engines/graph_v1/engine.py pipeline/tests/graph_v1
git commit -m "feat(graph_v1): index() and recommend() assembled once behind the Engine protocol"
```

---

### Task 10: One runner, one stage-0 evaluator, one exporter; delete the three scripts

**Files:**
- Create: `pipeline/scripts/run_engine.py`, `pipeline/scripts/eval_stage0.py`
- Rewrite: `pipeline/scripts/export_app_seed.py`
- Delete: `pipeline/scripts/run_stage0.py`, `pipeline/scripts/run_stage1_index.py`, `pipeline/scripts/run_query.py`
- Test: `pipeline/tests/core/test_eval_stage0.py`

- [ ] **Step 1: Write the failing test for the report logic**

`pipeline/tests/core/test_eval_stage0.py`:

```python
import importlib.util
from pathlib import Path

from gps_core.records import Recommendation

spec = importlib.util.spec_from_file_location(
    "eval_stage0", Path(__file__).resolve().parents[2] / "scripts" / "eval_stage0.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def rec(cid, match):
    return Recommendation(for_talk_id=0, candidate_id=cid, score=0.5, rank=1, match=match,
                          cross_domain=False, why="", strongest_parallel="", shared_methods=(),
                          evidence={}, engine_id="e", run_id="r")


def test_report_counts_hits_misses_fps_and_funnel_gaps():
    rows = [rec(1, True), rec(2, False), rec(9, True)]
    r = mod.report(rows, positives={1, 2, 3}, corpus_size=58)
    assert r["hit_positives"] == [1] and r["missed_positives"] == [2, 3]
    assert r["false_positives"] == [9] and r["positives_not_in_funnel"] == [3]
    assert r["funnel_candidates"] == [1, 2, 9] and r["corpus_size"] == 58
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/core/test_eval_stage0.py -q`
Expected: FAIL, file not found.

- [ ] **Step 3: Write the scripts**

`pipeline/scripts/run_engine.py`:

```python
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
from gps_data.talk import external_anchor  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "data" / "gps2026"


def corpus_ids(path: Path) -> set[int]:
    d = json.loads(path.read_text())
    if "ids" in d:
        return set(d["ids"])
    neg = d["negatives"]
    return ({p["id"] for p in d["positives"]} | set(neg["random_unrelated"])
            | set(neg["same_domain_different_method"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("index"); i.add_argument("--ids", required=True); i.add_argument("--out", required=True)
    r = sub.add_parser("recommend"); r.add_argument("--index", required=True)
    r.add_argument("--anchor"); r.add_argument("--presenter", type=int); r.add_argument("--talk", type=int)
    a = ap.parse_args()
    engine = get_engine(os.environ.get("ENGINE", "graph_v1"))

    if a.cmd == "index":
        ids = corpus_ids(ROOT / a.ids)
        talks = load_talks(ARCHIVE, only_ids=ids)
        run_index(engine, list(talks.values()), Path(a.out))
        return

    index = IndexArtifact(path=Path(a.index), engine_id=engine.id)
    talks = load_talks(ARCHIVE)
    if a.anchor:
        spec = json.loads(Path(a.anchor).read_text())
        anchors, authored = [external_anchor(spec["title"], spec["abstract"], spec.get("units", []))], set()
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
```

`pipeline/scripts/eval_stage0.py`:

```python
"""Stage-0 evaluation through the Engine protocol: index the 57-talk
micro-corpus, recommend for the external anchor, score against the labels.
GATED: live LLM spend — only with Rupert's go. Output: <out>/report.json."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_core.records import Recommendation  # noqa: E402
from gps_core.registry import get_engine  # noqa: E402
from gps_core.run import run_index, run_recommend  # noqa: E402
from gps_data.archive import load_talks  # noqa: E402
from gps_data.talk import external_anchor  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ANCHOR_ABSTRACT = (
    "The photoconductivity of nanorods self-assembled from "
    "meso-tetrakis(4-sulfonatophenyl)porphine is described. The "
    "nanorods are insulating in the dark. Upon illumination with "
    "488 nm light, the nanorods become photoconductive, exhibiting "
    "a rapid turn on/off (<100 ms) of the current when the light is "
    "turned on/off. This photoconductivity grows over hundreds of "
    "seconds with light exposure and decays slowly when the light "
    "is off. The nanorods can be trained via an applied bias to "
    "exhibit a short-circuit photocurrent (with corresponding "
    "open-circuit photovoltage) that flows in the direction "
    "opposite that of the training bias. A qualitative model is "
    "proposed, in which conduction occurs through the tightly "
    "coupled LUMOs of close-packed porphyrin molecules.")


def report(rows: list[Recommendation], positives: set[int], corpus_size: int) -> dict:
    judged = sorted(r.candidate_id for r in rows)
    matched = {r.candidate_id for r in rows if r.match}
    return {
        "corpus_size": corpus_size,
        "funnel_candidates": judged,
        "expected_positives": sorted(positives),
        "hit_positives": sorted(matched & positives),
        "missed_positives": sorted(positives - matched),
        "positives_not_in_funnel": sorted(positives - set(judged)),
        "false_positives": sorted(matched - positives),
        "matches": [r.to_row() for r in rows if r.match],
    }


def main() -> None:
    engine = get_engine(os.environ.get("ENGINE", "graph_v1"))
    out = Path(__file__).resolve().parents[1] / "out" / engine.id / "stage0"
    mc = json.loads((ROOT / "datasets" / "micro-corpus.json").read_text())
    neg = mc["negatives"]
    positives = {p["id"] for p in mc["positives"]}
    ids = positives | set(neg["random_unrelated"]) | set(neg["same_domain_different_method"])
    talks = load_talks(ROOT / "data" / "gps2026", only_ids=ids)
    missing = ids - set(talks)
    if missing:
        raise SystemExit(f"micro-corpus ids missing from archive: {sorted(missing)}")
    anchor = external_anchor(mc["anchor"]["title"], ANCHOR_ABSTRACT, ["DPOLY"])
    art, _ = run_index(engine, list(talks.values()), out / "index")
    rows, _ = run_recommend(engine, anchor, art, out / "query", corpus=list(talks.values()))
    rep = report(rows, positives, corpus_size=len(talks) + 1)
    (out / "report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: v for k, v in rep.items() if k != "matches"}, indent=1))


if __name__ == "__main__":
    main()
```

`pipeline/scripts/export_app_seed.py` (rewrite in full):

```python
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
from gps_data.legacy_seed import legacy_seed  # noqa: E402
from gps_data.talk import from_row  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "out"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, help="run_recommend output dir")
    ap.add_argument("--ids", required=True, help="dataset json naming the corpus ids")
    a = ap.parse_args()
    q = Path(a.query)
    d = json.loads((ROOT / a.ids).read_text())
    ids = set(d["ids"]) if "ids" in d else (
        {p["id"] for p in d["positives"]} | set(d["negatives"]["random_unrelated"])
        | set(d["negatives"]["same_domain_different_method"]))
    talks = load_talks(ROOT / "data" / "gps2026", only_ids=ids)
    anchor = from_row(json.loads((q / "anchor.json").read_text()))
    rows = []
    for r in json.loads((q / "recommendations.json").read_text()):
        r = {k: v for k, v in r.items() if k != "contract_version"}
        rows.append(Recommendation(**{**r, "shared_methods": tuple(r["shared_methods"])}))
    mrow = json.loads((q / "run.json").read_text())
    mrow.pop("contract_version")
    manifest = RunManifest(**{**mrow, "anchor_ids": tuple(mrow["anchor_ids"])})
    locations = [json.loads(f.read_text()) for f in sorted((ROOT / "data/gps2026/locations").glob("*.json"))]
    loc_rows = [{"id": l["id"], "building": l["building"], "room": l["room"]} for l in locations]
    all_talks = [anchor] + list(talks.values())
    write_seed(OUT / "app_seed.v2.json", all_talks, rows, [manifest], loc_rows)
    (OUT / "app_seed.json").write_text(json.dumps(legacy_seed(all_talks, rows, loc_rows), indent=1))
    print(f"wrote app_seed.v2.json ({len(all_talks)} talks, {len(rows)} recommendations) and legacy app_seed.json")


if __name__ == "__main__":
    main()
```

Add to `pipeline/src/gps_data/legacy_seed.py` (keep the existing `clean_text`, `build_talk_row`, `build_seed` untouched; append):

```python
def legacy_seed(talks, rows, locations) -> dict:
    """The pre-contract shape the current web app seeds from. Plan 2 deletes this."""
    talk_rows = [{
        "id": t.id, "title": t.title, "session_title": t.session_title,
        "units": list(t.units), "start": t.start, "end": t.end,
        "building": t.building, "room": t.room, "abstract": t.abstract,
    } for t in sorted(talks, key=lambda t: t.id)]
    rec_rows = [{
        "for_talk_id": r.for_talk_id, "candidate_id": r.candidate_id,
        "same_method": r.evidence.get("same_method", 0),
        "specificity": r.evidence.get("specificity", 0),
        "usage_parallel": r.evidence.get("usage_parallel", 0),
        "score": r.evidence.get("rubric_sum", round(r.score * 15)),
        "match": r.match, "cross_domain": r.cross_domain,
        "why": r.why, "strongest_parallel": r.strongest_parallel,
    } for r in sorted(rows, key=lambda r: r.candidate_id)]
    return {"talks": talk_rows, "locations": locations, "recommendations": rec_rows}
```

And a test appended to `pipeline/tests/data/test_legacy_seed.py`:

```python
from gps_core.records import Recommendation
from gps_data.legacy_seed import legacy_seed
from gps_data.talk import external_anchor


def test_legacy_seed_recovers_rubric_scores_from_evidence():
    r = Recommendation(for_talk_id=0, candidate_id=5, score=0.8, rank=1, match=True,
                       cross_domain=True, why="w", strongest_parallel="p", shared_methods=(),
                       evidence={"same_method": 4, "specificity": 3, "usage_parallel": 5, "rubric_sum": 12},
                       engine_id="graph_v1", run_id="r")
    seed = legacy_seed([external_anchor("t", "a", ["DPOLY"])], [r], [])
    rec = seed["recommendations"][0]
    assert rec["score"] == 12 and rec["same_method"] == 4 and rec["match"] is True
    assert set(seed["talks"][0]) == {"id", "title", "session_title", "units", "start", "end",
                                     "building", "room", "abstract"}
```

- [ ] **Step 4: Delete the three old scripts and fix the two survivors**

```bash
cd /Users/rupertlim/AI_Projects/ConferenceApp/pipeline
git rm -q scripts/run_stage0.py scripts/run_stage1_index.py scripts/run_query.py
grep -n "gps_engine\|corpus import" scripts/build_sample.py scripts/select_negatives.py
```

Both survivors import `load_talks`; ensure the line reads `from gps_data.archive import load_talks`.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest -q`
Expected: all green, including `test_eval_stage0.py` and the legacy-seed test.

- [ ] **Step 6: Smoke the runner offline**

Run: `uv run python scripts/run_engine.py --help && uv run python scripts/eval_stage0.py --help 2>&1 | head -3`
Expected: argparse help for the runner; the evaluator prints nothing harmful (it has no `--help`, so it will begin building the engine and fail on a missing `DEEPSEEK_API_KEY` if `.env` is not loaded — that is the gate working; do not proceed to a live run here).

- [ ] **Step 7: Commit**

```bash
git add -A pipeline/scripts pipeline/src/gps_data/legacy_seed.py pipeline/tests
git commit -m "feat(pipeline): single engine runner, stage-0 evaluator and exporter; delete the three stage scripts"
```

---

### Task 11: Docs — how to add an engine

**Files:**
- Create: `pipeline/README.md`

- [ ] **Step 1: Write it**

```markdown
# pipeline — matching engines

Engines write Recommendation rows; the web app reads them. The row shape is fixed by
`packages/contracts` (see `docs/superpowers/specs/2026-09-12-pluggable-engine-architecture-design.md`).

## Run
    uv sync
    uv run pytest -q                                   # always allowed
    ENGINE=graph_v1 uv run python scripts/eval_stage0.py           # LIVE LLM — needs Rupert's go
    ENGINE=graph_v1 uv run python scripts/run_engine.py index --ids datasets/sample-500.json --out out/graph_v1/sample500
    uv run python scripts/export_app_seed.py --query out/graph_v1/stage0/query --ids datasets/micro-corpus.json

Progress: `<out>/status.json`. Reruns resume from content-keyed checkpoints under `<out>/<stage>/`.

## Add an engine
1. Create `src/gps_engines/<name>/engine.py` with a class exposing `id`, `models`,
   `index(corpus, out) -> IndexArtifact`, `recommend(anchor, index) -> list[Recommendation]`,
   and a `build(**config)` factory.
2. Register it: one line in `src/gps_core/registry.py`.
3. Read only `id`, `title`, `abstract`, `units`, `topics` from a Talk.
4. Put anything engine-specific in `Recommendation.evidence`. Never add top-level fields;
   that is a contract change and goes through `packages/contracts` first.
5. Tests with fakes under `tests/<name>/`; `gps_core.run` validates every row you emit.
```

- [ ] **Step 2: Commit**

```bash
git add pipeline/README.md
git commit -m "docs(pipeline): how to run and how to add an engine"
```

---

### Task 12: GATED — reproduce stage 0 through the new engine and export

**This task spends live DeepSeek calls (≈ a few cents). Do not start it without Rupert's explicit go in the session.**

**Files:** none created in the repo (`pipeline/out/` is gitignored).

- [ ] **Step 1: Ask Rupert for the go.** State: "Task 12 runs `eval_stage0.py` live on DeepSeek, ~58 extractions, ~100 pair verdicts, ~12 rubric calls. Proceed?"

- [ ] **Step 2: Run the evaluator**

Run: `cd /Users/rupertlim/AI_Projects/ConferenceApp/pipeline && set -a && . ./.env && set +a && ENGINE=graph_v1 uv run python scripts/eval_stage0.py`
Expected: progress lines; final JSON with `hit_positives`, `missed_positives`, `false_positives`, `positives_not_in_funnel`.

- [ ] **Step 3: Compare with the DeepSeek baseline**

The reference (from `out/stage0-deepseek/report.json`) is hits `[2802, 3100, 5432, 8500, 9437, 11810, 12292, 12772]`, misses `[5389, 12342]`, no false positives, funnel recall 10/10.

- If the new run matches: record the run id in the commit message of Step 5.
- If it differs: **stop and report the two lists side by side to Rupert.** The likely cause is the query-time bipartite cascade replacing the old all-pairs cascade at stage 0; that is a real behavioural difference and Rupert decides whether it is acceptable. Do not tune anything.

- [ ] **Step 4: Export both seed shapes and validate**

Run: `uv run python scripts/export_app_seed.py --query out/graph_v1/stage0/query --ids datasets/micro-corpus.json`
Expected: "wrote app_seed.v2.json (58 talks, N recommendations) and legacy app_seed.json". Then:

Run: `cd ../apps/web && npx vitest run test/transform.test.ts`
Expected: PASS (the legacy seed still satisfies the current web transform).

- [ ] **Step 5: Commit the docs note**

No generated files are committed. Append one line to the plan's own file under this task: `Reproduced on <date>: run_id <id>, hits 8/10, FP 0` and commit:

```bash
git add docs/superpowers/plans/2026-09-12-pluggable-engine-plan-1-contracts-core-graph-v1.md
git commit -m "docs(plan): stage-0 reproduced through graph_v1 engine"
```

---

## Self-review against the spec

- §3.1 Talk record: Task 3 (25 fields, withdrawn excluded, session and location joined). §3.2 external anchor: Task 3. §3.3 presenter resolution: Task 3 (`anchors_for`, `authored_by`). §3.4 store: deferred to Plan 2; the seed writer in Task 7 carries the contract shape meanwhile.
- §4.1 protocol: Task 6. §4.2 record: Task 4. §4.3 manifest: Tasks 4 and 7. §4.4 core responsibilities: registry (6), checkpoint/progress (5), LLM (6), exclusion + cross_domain default (7), validation (2, 7), store writer (7). Eval harness: only the stage-0 report here; the general protocol is Plan 3. §4.5 layout: Task 8.
- §6 contracts: Task 1 (zod, emit, drift test, fixtures), Task 2 (Python validation). Versioning field: Tasks 1 and 4. Enforcement (CI, boundaries, CODEOWNERS): Plan 3.
- §8 migration steps 1–5 are covered here; 6–9 are Plans 2 and 3.
- Names used consistently: `Talk`, `to_row`, `from_row`, `external_anchor`, `load_talks`, `anchors_for`, `authored_by`, `Recommendation`, `RunManifest`, `IndexArtifact`, `Engine`, `get_engine`, `ENGINES`, `run_index`, `run_recommend`, `write_seed`, `validate`, `ContractError`, `checkpointed`, `content_key`, `Status`, `parallel`, `default_cross_domain`, `exclude_authored`, `ranked`, `GraphV1Engine`, `build`, `MATCH_MIN_SCORE`.
