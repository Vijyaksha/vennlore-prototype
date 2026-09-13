# Pluggable Engine — Plan 2: Store, API, UI on the Contract

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the app side follow the contract so there is exactly one row shape from engine to screen: store tables derived from `@repo/contracts`, a presenter-based tRPC API in its own package, the Kindred UI reading it, the legacy seed path deleted.

**Architecture:** A new workspace package `packages/api` owns the data layer and the API: Drizzle schema + migrations + seed (moved out of `apps/web/db`), a `Repo` interface with a Drizzle implementation and an in-memory fake, and the tRPC router (`talk.get`, `presenter.picks`, `presenter.agenda`). `apps/web` becomes a pure UI consumer that mounts `@repo/api`. Seed input is `pipeline/out/app_seed.v2.json` (contract shape), validated with the zod schemas at seed time. Rows are tagged by `engine_id`; the server env `ENGINE_ID` selects which engine's rows the app serves.

**Tech Stack:** Turborepo npm workspaces, tRPC v11 + zod 4 + @tanstack/react-query, Drizzle ORM + postgres + drizzle-kit, shadcn/ui + Tailwind v4, next-intl, vitest + @testing-library/react, Playwright (e2e, deferred to the live step).

**Design decisions honoured (spec §3.4, §5, §10):** contract is binding; store schema derived from Talk (25) / Recommendation (13) / Run; `recommendations` PK `(engine_id, for_talk_id, candidate_id)`; `score` real 0–1; rubric sub-scores stay inside `evidence` jsonb; `runs` table keyed by `run_id`; `locations` unchanged; UI renders six fields of a recommendation plus the candidate Talk; multi-anchor presenters get one merged rail; deploy-time engine switch. **Single-tenant mapping:** today's app shows picks for the external porphyrin anchor (talk id 0, `presenter_ids: []`, no presenter). `presenter.picks` and `presenter.agenda` therefore take `{ presenterId } | { talkId }` (zod union). `apps/web` reads `NEXT_PUBLIC_PRESENTER_ID` if set, else `NEXT_PUBLIC_ANCHOR_TALK_ID` (default `0`). When a presenter can be resolved to talks the app is multi-tenant with no code change.

**Not in this plan:** Turborepo boundaries, CODEOWNERS, branch protection (Plan 3). A Supabase project already exists (`DATABASE_URL` in `apps/web/.env`, gitignored — never print it); running `db:migrate`/`db:seed` against it is the last, gated step.

**Rules for every task:** TDD (failing test, watch it fail, implement, green); surgical edits; relative imports inside `packages/api` are **extensionless** (see execution note below); never stage `docs/business/` or `scratchpad/`; commit trailers:

```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GyR4M6ie2tftRPoSLdJdxY
```

---

## Execution notes (2026-09-13)

- **Import style in `packages/api` (Task 1 deviation).** The plan text below shows `.js` suffixes on relative imports. Turbopack only rewrites `.js` → `.ts` when the consuming app's tsconfig uses `moduleResolution: nodenext`, which breaks `apps/web`. `packages/api` therefore uses extensionless relative imports with `module: ESNext` / `moduleResolution: Bundler`. When copying code from this plan into `packages/api`, drop the `.js` suffixes. `packages/contracts` keeps its `.js` style until the web app imports it directly, at which point it needs the same treatment.
- **Local `DATABASE_URL`.** `apps/web/.env` moved to `packages/api/.env`, so `npm run dev` in `apps/web` no longer sees `DATABASE_URL`. For Task 9 step 4, source `packages/api/.env` into the shell before starting the dev server. Vercel production is unaffected.

- **Task 4 deviation.** The pure upsert helpers (`excluded`, `batches`, `updateSet`) live in `packages/api/src/db/upsert.ts` with a test, because the repo requires TDD and `seed.ts` runs on import.
- **Seed follow-ups (review minors, not blocking).** The seed script does not run in a transaction. It exits without closing the postgres client. It never deletes an engine's stale recommendations on reseed, which does not matter for the first seed after migration 0001. `toSeedFile` does not reject duplicate keys, or a recommendation whose `run_id` has no matching run.

- **Task 5 review changes.** The presenter and author lookups use Drizzle `arrayContains` (`@>`), not raw `= ANY(...)`. `getMatches` orders by for_talk_id, rank, then candidate_id in both repos. The repo test fixtures are deliberately unsorted, so ordering and match filtering are really tested. Later: add a GIN index on `presenter_ids` and `author_ids` if the store grows well past GPS scale.

## File structure (end state)

```
packages/api/
  package.json  tsconfig.json  eslint.config.mjs  drizzle.config.ts  .env (gitignored, moved from apps/web)
  drizzle/0000_cooing_bishop.sql  drizzle/0001_<name>.sql  drizzle/meta/*        (moved + new)
  src/index.ts                       # public surface: appRouter, AppRouter, createContext, Repo, memoryRepo, dbRepo
  src/db/schema.ts  src/db/index.ts  src/db/transform.ts  src/db/seed.ts         (moved, then rewritten)
  src/repo.ts                        # Repo interface + memoryRepo (fake)
  src/repo.db.ts                     # dbRepo (Drizzle)
  src/walk.ts                        # moved from apps/web/lib/walk.ts, unchanged
  src/agenda.ts                      # pure: group timed talks by Denver day + transit
  src/trpc.ts  src/router.ts
  test/schema.test.ts  test/transform.test.ts  test/repo.test.ts  test/router.test.ts  test/walk.test.ts  test/agenda.test.ts
apps/web/
  app/api/trpc/[trpc]/route.ts       # mounts @repo/api
  lib/trpc.ts  lib/conference.ts     # AppRouter from @repo/api; SCORE_MAX removed; subject config
  app/page.tsx  app/calendar/page.tsx
  components/pick-card.tsx  pick-rail.tsx  agenda*.tsx
  messages/en.json
  test/components/*.test.tsx
  (deleted: db/, drizzle/, drizzle.config.ts, server/, lib/walk.ts, test/router.test.ts, test/transform.test.ts, test/walk.test.ts)
pipeline/
  src/gps_data/legacy_seed.py (deleted)  scripts/export_app_seed.py (v2 only)  tests/data/test_legacy_seed.py (deleted)
```

---

### Task 1: Create `packages/api` and move the data layer and router into it (no behaviour change)

**Files:**
- Create: `packages/api/package.json`, `tsconfig.json`, `eslint.config.mjs`, `src/index.ts`
- Move (git mv): `apps/web/db/{schema,index,transform,seed}.ts` → `packages/api/src/db/`; `apps/web/drizzle/**` → `packages/api/drizzle/`; `apps/web/drizzle.config.ts` → `packages/api/drizzle.config.ts`; `apps/web/server/{trpc,router,data}.ts` → `packages/api/src/{trpc,router,repo.db}.ts`; `apps/web/lib/walk.ts` → `packages/api/src/walk.ts`; `apps/web/test/{router,transform,walk}.test.ts` → `packages/api/test/`; `apps/web/.env` → `packages/api/.env`
- Modify: `apps/web/app/api/trpc/[trpc]/route.ts`, `apps/web/lib/trpc.ts`, `apps/web/package.json` (drop db scripts + drizzle/postgres/tsx deps, add `@repo/api`), `apps/web/components/walk-segment.tsx` and `agenda-item.tsx` only if they import `lib/walk` types (grep first)

- [x] **Step 1: Scaffold**

`packages/api/package.json`:

```json
{
  "name": "@repo/api",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "exports": { ".": "./src/index.ts" },
  "scripts": {
    "test": "vitest run",
    "check-types": "tsc --noEmit",
    "lint": "eslint . --max-warnings 0",
    "db:generate": "drizzle-kit generate",
    "db:migrate": "drizzle-kit migrate",
    "db:seed": "tsx src/db/seed.ts"
  },
  "dependencies": {
    "@repo/contracts": "*",
    "@trpc/server": "^11.18.0",
    "drizzle-orm": "^0.45.2",
    "postgres": "^3.4.9",
    "zod": "^4.4.3"
  },
  "devDependencies": {
    "@repo/eslint-config": "*",
    "@repo/typescript-config": "*",
    "@types/node": "26.3.0",
    "drizzle-kit": "^0.31.10",
    "eslint": "10.9.1",
    "tsx": "^4.23.13",
    "typescript": "~5.9.3",
    "vitest": "^4.1.11"
  }
}
```

`packages/api/tsconfig.json`: same shape as `packages/contracts/tsconfig.json` (extends base, `noEmit`, `types: ["node"]`, include `src/**/*.ts`, `test/**/*.ts`, `drizzle.config.ts`). `packages/api/eslint.config.mjs`: `import { config } from "@repo/eslint-config/base"; export default config;`.

- [x] **Step 2: Move with git and fix imports**

```bash
cd /Users/rupertlim/AI_Projects/ConferenceApp
mkdir -p packages/api/src/db packages/api/test
git mv apps/web/db/schema.ts packages/api/src/db/schema.ts
git mv apps/web/db/index.ts packages/api/src/db/index.ts
git mv apps/web/db/transform.ts packages/api/src/db/transform.ts
git mv apps/web/db/seed.ts packages/api/src/db/seed.ts
git mv apps/web/drizzle packages/api/drizzle
git mv apps/web/drizzle.config.ts packages/api/drizzle.config.ts
git mv apps/web/server/trpc.ts packages/api/src/trpc.ts
git mv apps/web/server/router.ts packages/api/src/router.ts
git mv apps/web/server/data.ts packages/api/src/repo.db.ts
git mv apps/web/lib/walk.ts packages/api/src/walk.ts
git mv apps/web/test/router.test.ts packages/api/test/router.test.ts
git mv apps/web/test/transform.test.ts packages/api/test/transform.test.ts
git mv apps/web/test/walk.test.ts packages/api/test/walk.test.ts
mv apps/web/.env packages/api/.env      # gitignored on both sides; never commit
```

Then, in the moved files, rewrite relative imports to their new locations WITH `.js` suffixes (`"../db"` → `"./db/index.js"`, `"../lib/walk"` → `"./walk.js"`, `"./schema"` → `"./schema.js"`, tests: `"../server/router"` → `"../src/router.js"`, etc.). In `drizzle.config.ts` set `schema: "./src/db/schema.ts"`. In `seed.ts` set `SEED_PATH` to `join(dirname(fileURLToPath(import.meta.url)), "../../../../pipeline/out/app_seed.json")` (four levels up from `packages/api/src/db/`).

`packages/api/src/index.ts`:

```ts
export { appRouter, type AppRouter } from "./router.js";
export { createCallerFactory } from "./trpc.js";
export { dbRepo, type Repo, type TalkRow, type RecRow } from "./repo.db.js";
export { walkMinutes, connection, type Connection, type Loc } from "./walk.js";
```

`apps/web/app/api/trpc/[trpc]/route.ts`: import `{ appRouter, dbRepo }` from `"@repo/api"`. `apps/web/lib/trpc.ts`: `import type { AppRouter } from "@repo/api"`. `apps/web/package.json`: add `"@repo/api": "*"`, remove `db:generate|db:migrate|db:seed` scripts and the `drizzle-orm`, `postgres`, `drizzle-kit`, `tsx` deps (they now live in `@repo/api`). Any web component importing `lib/walk` types switches to `@repo/api`.

- [x] **Step 3: Verify nothing changed**

Run: `npm install && npm run test --workspace=@repo/api && npm run test --workspace=web && npm run check-types && npm run lint && npm run build --workspace=web`
Expected: api 3 files pass (the moved router/transform/walk tests, same counts as before: 58 total across both workspaces), web builds. `cd packages/api && npx drizzle-kit generate` reports "No schema changes" (proves the moved journal is intact).

- [x] **Step 4: Commit**

```bash
git add packages/api apps/web package.json package-lock.json
git status --short | grep -v "^[MADR] " ; echo "(above must be only docs/business, scratchpad, and .env noise)"
git commit -m "refactor(api): move data layer, router and walking engine into packages/api"
```

---

### Task 2: Store schema derived from the contract + migration

**Files:**
- Modify: `packages/api/src/db/schema.ts`
- Create: `packages/api/drizzle/0001_*.sql` + `meta/0001_snapshot.json` (generated), `packages/api/test/schema.test.ts`

- [x] **Step 1: Failing test — column names equal contract keys**

`packages/api/test/schema.test.ts`:

```ts
import { getTableColumns } from "drizzle-orm";
import { describe, expect, test } from "vitest";

import { RecommendationSchema, RunSchema, TalkSchema } from "@repo/contracts";

import { recommendations, runs, talks } from "../src/db/schema.js";

const sqlNames = (table: Parameters<typeof getTableColumns>[0]) =>
  Object.values(getTableColumns(table)).map((c) => c.name).sort();

describe("store schema is derived from the contract", () => {
  test("talks has exactly the 25 Talk fields", () => {
    expect(sqlNames(talks)).toEqual(Object.keys(TalkSchema.shape).sort());
  });
  test("recommendations has exactly the 13 Recommendation fields", () => {
    expect(sqlNames(recommendations)).toEqual(Object.keys(RecommendationSchema.shape).sort());
  });
  test("runs has exactly the Run fields", () => {
    expect(sqlNames(runs)).toEqual(Object.keys(RunSchema.shape).sort());
  });
});
```

Run: `npm run test --workspace=@repo/api -- test/schema.test.ts` → FAIL (`runs` not exported; talks has 9 columns).

- [x] **Step 2: Rewrite `schema.ts`**

```ts
import { sql } from "drizzle-orm";
import {
  bigint, boolean, integer, jsonb, pgTable, primaryKey, real, text, timestamp,
} from "drizzle-orm/pg-core";

const textArray = (name: string) => text(name).array().notNull().default(sql`'{}'::text[]`);
const intArray = (name: string) => integer(name).array().notNull().default(sql`'{}'::integer[]`);

/** One row per Talk contract field, same names. id 0 is the external anchor. */
export const talks = pgTable("talks", {
  id: integer("id").primaryKey(),
  externalId: text("external_id"),
  title: text("title").notNull(),
  abstract: text("abstract").notNull().default(""),
  units: textArray("units"),
  topics: textArray("topics"),
  type: text("type"),
  isInvited: boolean("is_invited").notNull().default(false),
  isWithdrawn: boolean("is_withdrawn").notNull().default(false),
  start: timestamp("start", { withTimezone: true }),
  end: timestamp("end", { withTimezone: true }),
  sortOrder: integer("sort_order"),
  presentationLocation: text("presentation_location"),
  authorIds: intArray("author_ids"),
  presenterIds: intArray("presenter_ids"),
  publicationReference: text("publication_reference"),
  fundingAcknowledgement: text("funding_acknowledgement"),
  teamAcknowledgement: text("team_acknowledgement"),
  sessionId: integer("session_id"),
  sessionTitle: text("session_title"),
  sessionCode: text("session_code"),
  sessionType: text("session_type"),
  sessionTopics: textArray("session_topics"),
  building: text("building"),
  room: text("room"),
});

/** One row per Recommendation contract field. Engine-specific detail stays in evidence. */
export const recommendations = pgTable(
  "recommendations",
  {
    engineId: text("engine_id").notNull(),
    forTalkId: integer("for_talk_id").notNull(),
    candidateId: integer("candidate_id").notNull(),
    score: real("score").notNull(),
    rank: integer("rank").notNull(),
    match: boolean("match").notNull(),
    crossDomain: boolean("cross_domain").notNull(),
    why: text("why").notNull().default(""),
    strongestParallel: text("strongest_parallel").notNull().default(""),
    sharedMethods: textArray("shared_methods"),
    evidence: jsonb("evidence").$type<Record<string, unknown>>().notNull().default({}),
    runId: text("run_id").notNull(),
    contractVersion: integer("contract_version").notNull(),
  },
  (t) => [primaryKey({ columns: [t.engineId, t.forTalkId, t.candidateId] })],
);

export const runs = pgTable("runs", {
  runId: text("run_id").primaryKey(),
  engineId: text("engine_id").notNull(),
  kind: text("kind").notNull(),
  engineVersion: text("engine_version").notNull(),
  models: jsonb("models").$type<Record<string, string>>().notNull().default({}),
  corpusHash: text("corpus_hash").notNull().default(""),
  anchorIds: intArray("anchor_ids"),
  startedAt: timestamp("started_at", { withTimezone: true }).notNull(),
  finishedAt: timestamp("finished_at", { withTimezone: true }).notNull(),
  indexPath: text("index_path"),
  contractVersion: integer("contract_version").notNull(),
});

// Location ids come from the conference API and exceed int32.
export const locations = pgTable("locations", {
  id: bigint("id", { mode: "number" }).primaryKey(),
  building: text("building").notNull(),
  room: text("room").notNull(),
});
```

Note the column rename `is_match` → `match` (contract name). The old `same_method/specificity/usage_parallel` columns are dropped; they live in `evidence`.

- [x] **Step 3: Generate the migration and run tests**

Run: `cd packages/api && npx drizzle-kit generate --name contract_v1` → writes `drizzle/0001_contract_v1.sql` and updates `meta/`. Open the SQL and confirm: `ALTER TABLE "talks" ADD COLUMN` ×16, `recommendations` drops the three sub-score columns, renames/recreates the PK to `(engine_id, for_talk_id, candidate_id)`, adds `rank`, `shared_methods`, `evidence`, `run_id`, `contract_version`, converts `score` to `real`; `CREATE TABLE "runs"`. If drizzle-kit asks interactively whether `is_match` was renamed to `match`, answer rename. (Data note: the live table holds only the 18 legacy rows for anchor 0; they will be reseeded from v2 in Task 9, so a destructive PK change is acceptable.)

Run: `npm run test --workspace=@repo/api` → schema tests pass; the OLD transform and router tests now FAIL to type-check (expected; fixed in Tasks 3 and 6). To keep the commit green, run only `-- test/schema.test.ts test/walk.test.ts` here and note the rest are red until Task 6.

- [x] **Step 4: Commit**

```bash
git add packages/api/src/db/schema.ts packages/api/drizzle packages/api/test/schema.test.ts
git commit -m "feat(api): store schema derived from the contract; migration 0001_contract_v1"
```

---

### Task 3: Seed transform for the v2 seed, validated by the contract

**Files:**
- Rewrite: `packages/api/src/db/transform.ts`, `packages/api/test/transform.test.ts`

- [x] **Step 1: Failing tests**

`packages/api/test/transform.test.ts`:

```ts
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { describe, expect, test } from "vitest";

import { toRecommendationInsert, toRunInsert, toSeedFile, toTalkInsert } from "../src/db/transform.js";

const req = createRequire(import.meta.url);
const fixture = (kind: string) =>
  JSON.parse(readFileSync(req.resolve(`@repo/contracts/fixtures/valid/${kind}.json`), "utf8"));

describe("toSeedFile", () => {
  test("accepts a contract-shaped seed and validates every row", () => {
    const seed = toSeedFile({
      contract_version: 1, talks: [fixture("talk")], locations: [],
      recommendations: [fixture("recommendation")], runs: [fixture("run")],
    });
    expect(seed.talks).toHaveLength(1);
  });
  test("rejects a row that breaks the contract, naming the row", () => {
    expect(() => toSeedFile({
      contract_version: 1, talks: [{ ...fixture("talk"), title: "" }], locations: [], recommendations: [], runs: [],
    })).toThrow(/talks\[0\]/);
  });
  test("rejects an unknown contract version", () => {
    expect(() => toSeedFile({ contract_version: 2, talks: [], locations: [], recommendations: [], runs: [] }))
      .toThrow(/contract_version/);
  });
});

describe("row transforms", () => {
  test("talk: snake_case → camelCase, ISO strings → Date, lists kept", () => {
    const row = toTalkInsert(fixture("talk"));
    expect(row.id).toBe(2802);
    expect(row.externalId).toBe("SMT26-3750532");
    expect(row.start).toEqual(new Date("2026-03-19T15:12:00.000Z"));
    expect(row.authorIds).toEqual([101, 102]);
    expect(row.sessionCode).toBe("MAR-B31");
    expect(Object.keys(row)).toHaveLength(25);
  });
  test("recommendation keeps evidence as-is and shared_methods as an array", () => {
    const row = toRecommendationInsert(fixture("recommendation"));
    expect(row.engineId).toBe("graph_v1");
    expect(row.score).toBe(0.8);
    expect(row.evidence).toEqual({ same_method: 4, specificity: 3, usage_parallel: 5, rubric_sum: 12 });
    expect(row.sharedMethods).toEqual(["transient photocurrent measurement"]);
    expect(row.contractVersion).toBe(1);
  });
  test("run converts timestamps", () => {
    const row = toRunInsert(fixture("run"));
    expect(row.startedAt).toEqual(new Date("2026-09-12T12:00:00Z"));
    expect(row.anchorIds).toEqual([0]);
  });
});
```

(Add `"./fixtures/*": "./fixtures/*"` to `packages/contracts/package.json` `exports` so the fixtures resolve; that is an additive contract-package change and is allowed.)

Run → FAIL (`toRunInsert` missing; `toSeedFile` shape differs).

- [x] **Step 2: Rewrite `transform.ts`**

```ts
import { z } from "zod";

import {
  CONTRACT_VERSION, RecommendationSchema, RunSchema, TalkSchema,
  type Recommendation, type Run, type Talk,
} from "@repo/contracts";

import type { locations, recommendations, runs, talks } from "./schema.js";

export type TalkInsert = typeof talks.$inferInsert;
export type RecommendationInsert = typeof recommendations.$inferInsert;
export type RunInsert = typeof runs.$inferInsert;
export type LocationInsert = typeof locations.$inferInsert;

const LocationSchema = z.strictObject({ id: z.int(), building: z.string().min(1), room: z.string().min(1) });

const SeedFileSchema = z.strictObject({
  contract_version: z.literal(CONTRACT_VERSION),
  talks: z.array(TalkSchema),
  locations: z.array(LocationSchema),
  recommendations: z.array(RecommendationSchema),
  runs: z.array(RunSchema),
});
export type SeedFile = z.infer<typeof SeedFileSchema>;

/** Validates the whole seed against the contract; errors name the offending row. */
export function toSeedFile(value: unknown): SeedFile {
  const result = SeedFileSchema.safeParse(value);
  if (!result.success) {
    const issue = result.error.issues[0]!;
    const where = issue.path.map((p, i) => (typeof p === "number" ? `[${p}]` : i ? `.${p}` : String(p))).join("");
    throw new Error(`seed file: ${where || "<root>"}: ${issue.message}`);
  }
  return result.data;
}

const date = (v: string | null) => (v === null ? null : new Date(v));

export function toTalkInsert(t: Talk): TalkInsert {
  return {
    id: t.id, externalId: t.external_id, title: t.title, abstract: t.abstract,
    units: t.units, topics: t.topics, type: t.type, isInvited: t.is_invited,
    isWithdrawn: t.is_withdrawn, start: date(t.start), end: date(t.end),
    sortOrder: t.sort_order, presentationLocation: t.presentation_location,
    authorIds: t.author_ids, presenterIds: t.presenter_ids,
    publicationReference: t.publication_reference,
    fundingAcknowledgement: t.funding_acknowledgement,
    teamAcknowledgement: t.team_acknowledgement, sessionId: t.session_id,
    sessionTitle: t.session_title, sessionCode: t.session_code,
    sessionType: t.session_type, sessionTopics: t.session_topics,
    building: t.building, room: t.room,
  };
}

export function toRecommendationInsert(r: Recommendation): RecommendationInsert {
  return {
    engineId: r.engine_id, forTalkId: r.for_talk_id, candidateId: r.candidate_id,
    score: r.score, rank: r.rank, match: r.match, crossDomain: r.cross_domain,
    why: r.why, strongestParallel: r.strongest_parallel, sharedMethods: r.shared_methods,
    evidence: r.evidence, runId: r.run_id, contractVersion: r.contract_version,
  };
}

export function toRunInsert(m: Run): RunInsert {
  return {
    runId: m.run_id, engineId: m.engine_id, kind: m.kind, engineVersion: m.engine_version,
    models: m.models, corpusHash: m.corpus_hash, anchorIds: m.anchor_ids,
    startedAt: new Date(m.started_at), finishedAt: new Date(m.finished_at),
    indexPath: m.index_path, contractVersion: m.contract_version,
  };
}

export function toLocationInsert(l: z.infer<typeof LocationSchema>): LocationInsert {
  return { id: l.id, building: l.building, room: l.room };
}
```

Run: `npm run test --workspace=@repo/api -- test/transform.test.ts test/schema.test.ts` → all pass.

- [x] **Step 3: Commit**

```bash
git add packages/api/src/db/transform.ts packages/api/test/transform.test.ts packages/contracts/package.json
git commit -m "feat(api): seed transform reads the v2 contract seed and validates every row"
```

---

### Task 4: Seed script for the v2 seed

**Files:**
- Rewrite: `packages/api/src/db/seed.ts`

- [x] **Step 1: Rewrite** (no unit test: it touches the DB; verified by the friendly-failure check and by Task 9)

Keep the `batches`/`excluded` helpers. Change `SEED_PATH` to `.../pipeline/out/app_seed.v2.json`; parse with `toSeedFile`; upsert in this order: `talks` (`onConflictDoUpdate` target `talks.id`, `set` every non-id column via `excluded("<sql name>")`), `locations` (as before), `runs` (target `runs.runId`), `recommendations` (target `[recommendations.engineId, recommendations.forTalkId, recommendations.candidateId]`, set score, rank, match, cross_domain, why, strongest_parallel, shared_methods, evidence, run_id, contract_version). Log four counts. Generate the `set` maps from the schema's column list rather than hand-typing 25 names:

```ts
import { getTableColumns } from "drizzle-orm";
function updateSet<T extends Parameters<typeof getTableColumns>[0]>(table: T, skip: string[]) {
  return Object.fromEntries(
    Object.values(getTableColumns(table)).filter((c) => !skip.includes(c.name)).map((c) => [c.name, excluded(c.name)]),
  ) as Record<string, ReturnType<typeof excluded>>;
}
```

and pass `updateSet(talks, ["id"])` etc. (Drizzle's `set` accepts SQL fragments keyed by column property; if it requires property keys rather than SQL names, key by the object property instead — check the type error and pick the one that compiles.)

- [x] **Step 2: Verify the gate**

Run: `cd packages/api && env -u DATABASE_URL npx tsx src/db/seed.ts`
Expected: exits 1 with `DATABASE_URL is not set — connect Supabase first` (or the "Seed file not found" message if `app_seed.v2.json` is absent, which is also fine — the point is no DB is touched).

- [x] **Step 3: Commit**

```bash
git add packages/api/src/db/seed.ts
git commit -m "feat(api): seed talks, locations, runs and recommendations from app_seed.v2.json"
```

---

### Task 5: Repository interface, in-memory fake, Drizzle implementation

**Files:**
- Create: `packages/api/src/repo.ts`, `packages/api/test/repo.test.ts`
- Rewrite: `packages/api/src/repo.db.ts`

- [x] **Step 1: Failing tests (against the fake; the Drizzle repo is type-checked only, per the no-live-DB rule)**

`packages/api/test/repo.test.ts`:

```ts
import { describe, expect, test } from "vitest";

import { memoryRepo, type RecRow, type TalkRow } from "../src/repo.js";

const talk = (o: Partial<TalkRow> & { id: number }): TalkRow => ({
  externalId: null, title: `Talk ${o.id}`, abstract: "", units: [], topics: [], type: null,
  isInvited: false, isWithdrawn: false, start: null, end: null, sortOrder: null,
  presentationLocation: null, authorIds: [], presenterIds: [], publicationReference: null,
  fundingAcknowledgement: null, teamAcknowledgement: null, sessionId: null, sessionTitle: null,
  sessionCode: null, sessionType: null, sessionTopics: [], building: null, room: null, ...o,
});
const rec = (forTalkId: number, candidateId: number, o: Partial<RecRow> = {}): RecRow => ({
  engineId: "graph_v1", forTalkId, candidateId, score: 0.5, rank: 1, match: true,
  crossDomain: false, why: "", strongestParallel: "", sharedMethods: [], evidence: {},
  runId: "r", contractVersion: 1, ...o,
});

const talks = [
  talk({ id: 0 }),
  talk({ id: 10, presenterIds: [7], authorIds: [7, 8] }),
  talk({ id: 11, presenterIds: [7], authorIds: [7] }),
  talk({ id: 12, presenterIds: [9], authorIds: [8, 9] }),
  talk({ id: 13 }),
];
const recs = [
  rec(10, 13, { rank: 1, score: 0.9 }), rec(10, 12, { rank: 2, score: 0.6 }),
  rec(11, 13, { rank: 1 }), rec(10, 13, { engineId: "other", rank: 1 }),
  rec(0, 13, { match: false }),
];
const repo = memoryRepo(talks, recs);

describe("memoryRepo", () => {
  test("getTalk / getTalks", async () => {
    expect((await repo.getTalk(10))?.id).toBe(10);
    expect(await repo.getTalk(999)).toBeNull();
    expect((await repo.getTalks([13, 10])).map((t) => t.id)).toEqual([10, 13]);
  });
  test("anchorsFor returns the presenter's talks in id order", async () => {
    expect((await repo.anchorsFor(7)).map((t) => t.id)).toEqual([10, 11]);
    expect(await repo.anchorsFor(404)).toEqual([]);
  });
  test("authoredBy returns every talk the person authored", async () => {
    expect(await repo.authoredBy(8)).toEqual(new Set([10, 12]));
  });
  test("getMatches filters by engine and match, orders by anchor then rank, joins the candidate", async () => {
    const rows = await repo.getMatches([10, 11], "graph_v1");
    expect(rows.map((r) => [r.forTalkId, r.candidateId, r.rank])).toEqual([[10, 13, 1], [10, 12, 2], [11, 13, 1]]);
    expect(rows[0]?.candidate.id).toBe(13);
  });
  test("getMatches for another engine sees only its rows", async () => {
    expect((await repo.getMatches([10], "other")).map((r) => r.candidateId)).toEqual([13]);
  });
});
```

Run → FAIL (`memoryRepo` missing).

- [x] **Step 2: Implement `repo.ts`**

```ts
import type { recommendations, talks } from "./db/schema.js";

export type TalkRow = typeof talks.$inferSelect;
export type RecRow = typeof recommendations.$inferSelect;
export type MatchRow = RecRow & { candidate: TalkRow };

/** Everything the router needs from the store. dbRepo implements it over
 *  Drizzle; memoryRepo implements it over arrays for tests. */
export interface Repo {
  getTalk(id: number): Promise<TalkRow | null>;
  getTalks(ids: number[]): Promise<TalkRow[]>;
  anchorsFor(presenterId: number): Promise<TalkRow[]>;
  authoredBy(presenterId: number): Promise<Set<number>>;
  /** match=true rows of one engine for the given anchors, ordered by for_talk_id then rank. */
  getMatches(forTalkIds: number[], engineId: string): Promise<MatchRow[]>;
}

export function memoryRepo(talkRows: TalkRow[], recRows: RecRow[]): Repo {
  const byId = new Map(talkRows.map((t) => [t.id, t]));
  return {
    getTalk: async (id) => byId.get(id) ?? null,
    getTalks: async (ids) => ids.map((id) => byId.get(id)).filter((t): t is TalkRow => t !== undefined).sort((a, b) => a.id - b.id),
    anchorsFor: async (presenterId) =>
      talkRows.filter((t) => t.presenterIds.includes(presenterId)).sort((a, b) => a.id - b.id),
    authoredBy: async (presenterId) => new Set(talkRows.filter((t) => t.authorIds.includes(presenterId)).map((t) => t.id)),
    getMatches: async (forTalkIds, engineId) =>
      recRows
        .filter((r) => r.engineId === engineId && r.match && forTalkIds.includes(r.forTalkId))
        .sort((a, b) => a.forTalkId - b.forTalkId || a.rank - b.rank)
        .flatMap((r) => { const c = byId.get(r.candidateId); return c ? [{ ...r, candidate: c }] : []; }),
  };
}
```

- [x] **Step 3: Rewrite `repo.db.ts`** with the same five methods over Drizzle: `getTalks` → `inArray(talks.id, ids)` ordered by id; `anchorsFor` → `sql\`${presenterId} = ANY(${talks.presenterIds})\`` ordered by id; `authoredBy` → same with `authorIds`, returns `new Set(rows.map(r => r.id))`; `getMatches` → `select().from(recommendations).innerJoin(talks, eq(recommendations.candidateId, talks.id)).where(and(eq(recommendations.engineId, engineId), eq(recommendations.match, true), inArray(recommendations.forTalkId, forTalkIds))).orderBy(asc(recommendations.forTalkId), asc(recommendations.rank))`, mapped to `{ ...row.recommendations, candidate: row.talks }`. Export `dbRepo: Repo`. Update `src/index.ts` to export `memoryRepo`, `type MatchRow` from `./repo.js` and `dbRepo` from `./repo.db.js`.

Run: `npm run test --workspace=@repo/api -- test/repo.test.ts` → 5 pass; `npm run check-types --workspace=@repo/api` still fails on the old router (next task).

- [x] **Step 4: Commit**

```bash
git add packages/api/src/repo.ts packages/api/src/repo.db.ts packages/api/src/index.ts packages/api/test/repo.test.ts
git commit -m "feat(api): Repo interface with in-memory fake and Drizzle implementation on the contract schema"
```

---

### Task 6: Router — `talk.get`, `presenter.picks`, `presenter.agenda`

**Files:**
- Create: `packages/api/src/agenda.ts`, `packages/api/test/agenda.test.ts`
- Rewrite: `packages/api/src/trpc.ts` (context gains `engineId`), `packages/api/src/router.ts`, `packages/api/test/router.test.ts`

- [ ] **Step 1: Failing tests**

`packages/api/test/agenda.test.ts` (pure grouping, lifted from the old agenda procedure):

```ts
import { describe, expect, test } from "vitest";
import { groupByDenverDay } from "../src/agenda.js";

const item = (id: number, start: string | null, end: string | null, building = "Convention Center", room = "Bluebird 3C") =>
  ({ id, title: `T${id}`, sessionTitle: null, start: start ? new Date(start) : null, end: end ? new Date(end) : null, building, room });

describe("groupByDenverDay", () => {
  test("groups by Denver date, sorts by start, annotates transit after the first item", () => {
    const days = groupByDenverDay([
      item(2, "2026-03-19T16:00:00Z", "2026-03-19T16:12:00Z", "Convention Center", "Exhibit Hall D, E & F, Level 2"),
      item(1, "2026-03-19T15:12:00Z", "2026-03-19T15:24:00Z"),
      item(3, "2026-03-19T05:30:00Z", "2026-03-19T05:42:00Z", "Hyatt Regency", "Capitol 1"),
      item(4, null, null),
    ]);
    expect(days.map((d) => d.date)).toEqual(["2026-03-18", "2026-03-19"]);
    expect(days[1]?.items.map((i) => i.id)).toEqual([1, 2]);
    expect(days[1]?.items[0]?.transit).toBeNull();
    expect(days[1]?.items[1]?.transit).toEqual({ walk: 15, slack: 21, tight: false });
  });
});
```

`packages/api/test/router.test.ts` (replace the old file):

```ts
import { describe, expect, test } from "vitest";
import { appRouter } from "../src/router.js";
import { createCallerFactory } from "../src/trpc.js";
import { memoryRepo, type RecRow, type TalkRow } from "../src/repo.js";

const talk = (o: Partial<TalkRow> & { id: number }): TalkRow => ({ /* same 25-field factory as repo.test.ts */ } as TalkRow);
const rec = (forTalkId: number, candidateId: number, o: Partial<RecRow> = {}): RecRow => ({ /* same as repo.test.ts */ } as RecRow);

const anchor = talk({ id: 0, title: "Porphyrin nanorods" });
const mine1 = talk({ id: 10, title: "My first talk", presenterIds: [7], authorIds: [7], start: new Date("2026-03-19T14:00:00Z"), end: new Date("2026-03-19T14:12:00Z"), building: "Convention Center", room: "Bluebird 2A" });
const mine2 = talk({ id: 11, title: "My second talk", presenterIds: [7], authorIds: [7] });
const bluebird = talk({ id: 2802, title: "Bluebird talk", units: ["DPOLY"], start: new Date("2026-03-19T15:12:00Z"), end: new Date("2026-03-19T15:24:00Z"), building: "Convention Center", room: "Bluebird 3C" });
const hall = talk({ id: 12342, title: "Hall talk", units: ["FIAP"], start: new Date("2026-03-19T16:00:00Z"), end: new Date("2026-03-19T16:12:00Z"), building: "Convention Center", room: "Exhibit Hall D, E & F, Level 2" });
const repo = memoryRepo([anchor, mine1, mine2, bluebird, hall], [
  rec(0, 2802, { rank: 1, score: 0.8 }), rec(0, 12342, { rank: 2, score: 0.4, crossDomain: true }),
  rec(10, 2802, { rank: 1, score: 0.9 }), rec(11, 12342, { rank: 1, score: 0.7, crossDomain: true }),
  rec(10, 12342, { rank: 2, score: 0.3, match: false }),
  rec(0, 2802, { engineId: "other", rank: 1, score: 0.1 }),
]);
const call = (engineId = "graph_v1") => createCallerFactory(appRouter)({ repo, engineId });

describe("talk.get", () => {
  test("returns the talk or NOT_FOUND", async () => {
    expect((await call().talk.get({ id: 2802 })).title).toBe("Bluebird talk");
    await expect(call().talk.get({ id: 1 })).rejects.toThrow(/not found/i);
  });
});

describe("presenter.picks", () => {
  test("by talkId (single-tenant anchor): anchors = [talk], matched rows of the configured engine only", async () => {
    const r = await call().presenter.picks({ talkId: 0 });
    expect(r.anchors.map((t) => t.id)).toEqual([0]);
    expect(r.recommendations.map((x) => [x.candidateId, x.rank, x.score])).toEqual([[2802, 1, 0.8], [12342, 2, 0.4]]);
    expect(r.recommendations[0]?.candidate.title).toBe("Bluebird talk");
  });
  test("by presenterId: union across the presenter's anchors, per anchor order", async () => {
    const r = await call().presenter.picks({ presenterId: 7 });
    expect(r.presenterId).toBe(7);
    expect(r.anchors.map((t) => t.id)).toEqual([10, 11]);
    expect(r.recommendations.map((x) => [x.forTalkId, x.candidateId])).toEqual([[10, 2802], [11, 12342]]);
  });
  test("engineId override selects another engine's rows", async () => {
    const r = await call().presenter.picks({ talkId: 0, engineId: "other" });
    expect(r.recommendations.map((x) => x.score)).toEqual([0.1]);
  });
  test("unknown presenter → NOT_FOUND", async () => {
    await expect(call().presenter.picks({ presenterId: 404 })).rejects.toThrow(/not found/i);
  });
});

describe("presenter.agenda", () => {
  test("own timed talks plus matched candidates, grouped by Denver day with transit", async () => {
    const r = await call().presenter.agenda({ presenterId: 7 });
    expect(r.days.map((d) => d.date)).toEqual(["2026-03-19"]);
    expect(r.days[0]?.items.map((i) => [i.id, i.kind])).toEqual([[10, "mine"], [2802, "core"], [12342, "surprise"]]);
    expect(r.days[0]?.items[1]?.transit).toEqual({ walk: 15, slack: 45, tight: false });
  });
  test("by talkId works for the untimed anchor: only candidates appear", async () => {
    const r = await call().presenter.agenda({ talkId: 0 });
    expect(r.days.flatMap((d) => d.items.map((i) => i.id))).toEqual([2802, 12342]);
  });
});
```

Run → FAIL.

- [ ] **Step 2: Implement**

`packages/api/src/agenda.ts`:

```ts
import { connection, walkMinutes, type Connection } from "./walk.js";

export interface AgendaInput { id: number; title: string; sessionTitle: string | null; start: Date | null; end: Date | null; building: string | null; room: string | null }
export interface AgendaItem extends Omit<AgendaInput, "start"> { start: Date; transit: Connection | null }

const denverDate = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Denver", year: "numeric", month: "2-digit", day: "2-digit" });

export function groupByDenverDay(items: AgendaInput[]): { date: string; items: AgendaItem[] }[] {
  const timed = items.filter((t): t is AgendaInput & { start: Date } => t.start !== null)
    .sort((a, b) => a.start.getTime() - b.start.getTime());
  const byDate = new Map<string, AgendaItem[]>();
  for (const t of timed) {
    const date = denverDate.format(t.start);
    const list = byDate.get(date) ?? [];
    const prev = list.at(-1);
    let transit: Connection | null = null;
    if (prev) {
      const gap = (t.start.getTime() - (prev.end ?? prev.start).getTime()) / 60_000;
      transit = connection(gap, walkMinutes(prev, t));
    }
    list.push({ ...t, transit });
    byDate.set(date, list);
  }
  return [...byDate.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([date, items]) => ({ date, items }));
}
```

`packages/api/src/trpc.ts`: `export interface Context { repo: Repo; engineId: string }`; add `export function createContext(): Context { return { repo: dbRepo, engineId: process.env.ENGINE_ID ?? "graph_v1" }; }` (import `dbRepo` from `./repo.db.js`).

`packages/api/src/router.ts`:

```ts
import { TRPCError } from "@trpc/server";
import { z } from "zod";
import { groupByDenverDay } from "./agenda.js";
import type { MatchRow, Repo, TalkRow } from "./repo.js";
import { publicProcedure, router } from "./trpc.js";

const Subject = z.union([
  z.object({ presenterId: z.int().min(1), engineId: z.string().optional() }),
  z.object({ talkId: z.int().min(0), engineId: z.string().optional() }),
]);

async function resolveAnchors(repo: Repo, input: z.infer<typeof Subject>) {
  if ("presenterId" in input) {
    const anchors = await repo.anchorsFor(input.presenterId);
    if (anchors.length === 0) throw new TRPCError({ code: "NOT_FOUND", message: `presenter ${input.presenterId} not found` });
    return { presenterId: input.presenterId, anchors };
  }
  const talk = await repo.getTalk(input.talkId);
  if (talk === null) throw new TRPCError({ code: "NOT_FOUND", message: `talk ${input.talkId} not found` });
  return { presenterId: null, anchors: [talk] };
}

export const appRouter = router({
  talk: router({
    get: publicProcedure.input(z.object({ id: z.int().min(0) })).query(async ({ ctx, input }) => {
      const talk = await ctx.repo.getTalk(input.id);
      if (talk === null) throw new TRPCError({ code: "NOT_FOUND", message: `talk ${input.id} not found` });
      return talk;
    }),
  }),
  presenter: router({
    picks: publicProcedure.input(Subject).query(async ({ ctx, input }) => {
      const { presenterId, anchors } = await resolveAnchors(ctx.repo, input);
      const recommendations: MatchRow[] = await ctx.repo.getMatches(anchors.map((a) => a.id), input.engineId ?? ctx.engineId);
      return { presenterId, anchors, recommendations };
    }),
    agenda: publicProcedure.input(Subject).query(async ({ ctx, input }) => {
      const { presenterId, anchors } = await resolveAnchors(ctx.repo, input);
      const matches = await ctx.repo.getMatches(anchors.map((a) => a.id), input.engineId ?? ctx.engineId);
      const kind = new Map<number, "mine" | "core" | "surprise">();
      for (const m of matches) kind.set(m.candidateId, m.crossDomain ? "surprise" : "core");
      for (const a of anchors) kind.set(a.id, "mine");
      const seen = new Set<number>();
      const pool: TalkRow[] = [...anchors, ...matches.map((m) => m.candidate)].filter((t) => !seen.has(t.id) && seen.add(t.id));
      const days = groupByDenverDay(pool).map((d) => ({
        date: d.date,
        items: d.items.map((i) => ({ ...i, kind: kind.get(i.id) ?? "surprise", units: pool.find((t) => t.id === i.id)?.units ?? [] })),
      }));
      return { presenterId, days };
    }),
  }),
});
export type AppRouter = typeof appRouter;
```

Update `src/index.ts` to export `createContext` and `groupByDenverDay`.

Run: `npm run test --workspace=@repo/api && npm run check-types --workspace=@repo/api && npm run lint --workspace=@repo/api` → all green (`apps/web` is now red until Task 7).

- [ ] **Step 3: Commit**

```bash
git add packages/api/src packages/api/test
git commit -m "feat(api): presenter-based picks and agenda over the contract store; talk.get"
```

---

### Task 7: Kindred UI on the new API

**Files:**
- Modify: `apps/web/app/api/trpc/[trpc]/route.ts` (use `createContext` from `@repo/api`), `apps/web/lib/conference.ts` (replace `ANCHOR_TALK_ID`/`SCORE_MAX` with `SUBJECT`), `apps/web/app/page.tsx`, `apps/web/app/calendar/page.tsx`, `apps/web/components/pick-card.tsx`, `apps/web/components/pick-rail.tsx`, `apps/web/messages/en.json`, `apps/web/test/components/pick-rail.test.tsx`, `apps/web/e2e/kindred.e2e.ts`, `apps/web/.env.example` (new, documents `NEXT_PUBLIC_PRESENTER_ID`, `NEXT_PUBLIC_ANCHOR_TALK_ID`, `ENGINE_ID`, `DATABASE_URL`)

- [ ] **Step 1: Failing component tests** (edit `pick-rail.test.tsx`):
  - score renders as a percentage: a pick with `score: 0.8` shows `80%` (message `"score": "{score, number, percent}"`); the `11/15` assertion goes away.
  - shared-method chips: a pick with `sharedMethods: ["transient photocurrent", "self-assembly"]` renders both as chips (`getByText("transient photocurrent")`).
  - anchor chip only for multi-anchor presenters: with `anchors` of length 2, each card shows `for your talk on …` (message `"forTalk": "for your talk on {title}"`) truncated title; with one anchor no chip.
  - merged rail keeps the best score per candidate when the same candidate appears under two anchors.
  - existing caps (2 core / 3 unexpected), empty slots, dots and Denver time tests remain.

- [ ] **Step 2: Implement**
  - `lib/conference.ts`: `export const SUBJECT = process.env.NEXT_PUBLIC_PRESENTER_ID ? { presenterId: Number(process.env.NEXT_PUBLIC_PRESENTER_ID) } : { talkId: Number(process.env.NEXT_PUBLIC_ANCHOR_TALK_ID ?? "0") };` Remove `ANCHOR_TALK_ID` and `SCORE_MAX`.
  - `Pick` type: `candidateId, forTalkId, title, sessionTitle, units, start, score (0–1), crossDomain, why, sharedMethods: string[]`. `PickRail` props: `{ anchors: { id: number; title: string }[]; recommendations: Pick[] }`; it dedupes by `candidateId` keeping max score, splits core/unexpected by `crossDomain`, applies the caps, sorts by score desc then id, shows the honest empty slot rule as today. `PickCard` renders the percent score, chips (`Badge` variant outline, `font-mono text-[10.5px]`), and the anchor chip when `anchors.length > 1` (title from the anchors array by `forTalkId`).
  - `app/page.tsx`: `trpc.presenter.picks.useQuery(SUBJECT)`; heading = anchors' titles joined by " · " when several; pass `anchors` and `recommendations` to the rail.
  - `app/calendar/page.tsx`: `trpc.presenter.agenda.useQuery(SUBJECT)`; items already carry `kind` and `units`, so the local `kinds` map disappears.
  - `messages/en.json`: `picks.score` → `"{score, number, percent}"`, add `picks.forTalk`, `picks.sharedMethods` (aria label for the chip group).
  - `e2e/kindred.e2e.ts`: `/\/15/` → `/%/`; the agenda API test calls `presenter.agenda` with `{ talkId: 0 }`.

Run: `npm run test --workspace=web && npm run check-types && npm run lint && npm run build --workspace=web` → green.

- [ ] **Step 3: Commit**

```bash
git add apps/web
git commit -m "feat(web): Kindred reads presenter.picks/agenda; percent score, shared-method chips, merged rail"
```

---

### Task 8: Delete the legacy seed path

**Files:**
- Modify: `pipeline/scripts/export_app_seed.py` (write only `app_seed.v2.json`; update docstring), `pipeline/README.md`
- Delete: `pipeline/src/gps_data/legacy_seed.py`, `pipeline/tests/data/test_legacy_seed.py`
- Modify: `pipeline/tests/data/test_datasets.py` only if it imported from legacy_seed (it should not)

- [ ] **Step 1:** `grep -rn "legacy_seed\|app_seed.json\b" pipeline/ apps/ packages/` → list every reference; remove them. `git rm` the two files. In `export_app_seed.py` drop the legacy write and the import.
- [ ] **Step 2:** `cd pipeline && uv run pytest -q` → green (count drops by the deleted tests). `grep -rn "build_talk_row\|build_seed" pipeline` → nothing.
- [ ] **Step 3:** Commit: `git add -A pipeline/src/gps_data pipeline/tests/data pipeline/scripts/export_app_seed.py pipeline/README.md && git commit -m "chore(pipeline): remove the legacy seed shape; the contract seed is the only output"`

---

### Task 9: GATED — migrate and reseed the live store, then smoke the app

**Requires Rupert's explicit go. Touches the Supabase database (`DATABASE_URL` in `packages/api/.env`).**

- [ ] **Step 1:** Ask: "Task 9 runs migration 0001 against the live Supabase Postgres (drops the three sub-score columns and recreates the recommendations PK; existing 18 legacy rows are replaced) and reseeds from `app_seed.v2.json`. Proceed?"
- [ ] **Step 2:** `cd pipeline && uv run python scripts/export_app_seed.py --query out/graph_v1/stage0-chat/query --ids datasets/micro-corpus.json` (offline; uses the run from Plan 1 Task 12).
- [ ] **Step 3:** `cd packages/api && set -a && . ./.env && set +a && npm run db:migrate && npm run db:seed` → "Seeded 58 talks / 118 locations / 1 runs / 19 recommendations".
- [ ] **Step 4:** `cd apps/web && ENGINE_ID=graph_v1 npm run dev` and, in a browser or via Playwright, confirm `/` shows the porphyrin heading, cards with percent scores and chips, and `/calendar` renders days; then `npm run e2e` against the dev server (set `PLAYWRIGHT_BASE_URL`).
- [ ] **Step 5:** Commit nothing (outputs are gitignored); append one line to this plan under this task: `Migrated + seeded on <date>; e2e N passed`, and commit that line.

---

## Self-review

- **Spec coverage.** §3.4 store: Task 2 (tables), Task 3/4 (seed). §3.3 presenter resolution on the app side: Task 5 (`anchorsFor`, `authoredBy`) and Task 6. §3.5 what the data layer serves: Task 5/6. §5.1 API surface: Task 6 (the `{talkId}` alternative is the documented single-tenant mapping; a per-request `engineId` exists but the UI never passes it). §5.2 what the UI renders: Task 7 (six recommendation fields + candidate Talk; percent score; chips; merged rail). §5.3 one app mounting `@repo/api`: Tasks 1 and 7. §8 steps 5–7: Tasks 2–7. Legacy adapter deletion: Task 8. §6 enforcement (boundaries, CODEOWNERS): deliberately Plan 3.
- **Placeholders.** None; the two "same factory as repo.test.ts" comments in Task 6 refer to code fully given in Task 5 and must be copied, not abbreviated, when implementing.
- **Type consistency.** `Repo` methods: `getTalk`, `getTalks`, `anchorsFor`, `authoredBy`, `getMatches` (Tasks 5, 6). Row types `TalkRow`, `RecRow`, `MatchRow` (Task 5) used by Task 6/7. Context `{ repo, engineId }` (Task 6) used by `createContext` and the web route (Task 7). Seed transforms `toSeedFile`, `toTalkInsert`, `toRecommendationInsert`, `toRunInsert`, `toLocationInsert` (Tasks 3, 4). `groupByDenverDay` (Task 6). `SUBJECT` (Task 7). Column `match` replaces `is_match` everywhere (Tasks 2, 4, 5).
- **Known follow-up not in scope:** `authoredBy` is available in the repo but the router does not yet exclude a presenter's co-authored talks from *picks* (core already excluded them at engine time); a later plan may add a server-side guard.
