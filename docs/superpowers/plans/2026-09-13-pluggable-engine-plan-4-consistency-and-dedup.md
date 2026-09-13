# Pluggable Engine — Plan 4: Consistency and Deduplication

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the six important findings of the 2026-09-13 audit (`docs/superpowers/audits/2026-09-13-contract-enforcement-audit.md`) so the database, the read path and the guards all honour the contract exactly, then remove the camelCase middle layer so each contract field is spelled in three places (zod, Drizzle column, Python record) instead of six.

**Architecture:** Every task is one pull request through the CI gate on `main` (branch → PR → checks green → merge; no review requirement). Tasks 1–3 are database and read-path corrections that change column types and constraints to match the contract, never the contract itself. Task 4 closes two guard bypasses. Task 5 corrects the spec. Task 6 renames the Drizzle table properties to the contract's field names, which makes `$inferSelect` produce contract keys while the generated SQL stays byte-identical, and lands together with a fake-vs-real repository parity test that runs on the Postgres already in the e2e CI job. Task 7 trims dead surface and makes the seed transactional. Task 8 lets the UI components take contract types directly. Task 9 (gated) applies the new migrations to the live Supabase store.

**Tech Stack:** Drizzle ORM 0.45 + drizzle-kit migrations, zod 4, tRPC v11, vitest, ESLint flat config, GitHub Actions, `gh`.

**Rules for every task:** TDD (failing test first, watch it fail, implement, green). One branch per task named `plan4/task-N-<slug>` from `main`; open the PR with `gh pr create`; merge with `gh pr merge --merge` when the three checks are green; delete the branch. Extensionless relative imports in `packages/*`. Never stage `docs/business/`, `scratchpad/`, `pipeline/out/`, `__pycache__`, or any `.env`. Never connect to the live database except in Task 9. Commit trailer after a blank line:

```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
```

**Migrations note:** Tasks 1 and 2 each generate a migration with `cd packages/api && npx drizzle-kit generate --name <name>`. A second `npx drizzle-kit generate` must print "No schema changes". The e2e CI job applies every migration to an empty Postgres 16 before seeding, so a broken migration fails CI. The live Supabase store gets them in Task 9.

**Out of plan 4:** generated Python records (audit: not worth the loss of frozen dataclasses), GIN index and query projection (wait for the 1k-talk build), the Prettier check, Playwright browser cache.

---

## File structure (end state)

```
packages/api/
  src/db/schema.ts        # snake_case properties = column names; FKs; doublePrecision score; bigint person ids; runs declared before recommendations
  src/db/transform.ts     # toSeedFile with referential/uniqueness checks; toTalkInsert/toRunInsert = spread + Date; recommendation/location mappers deleted
  src/wire.ts             # toTalk/toRecommendation = spread + ISO/version; toPick unchanged
  src/repo.ts, src/repo.db.ts   # contract-named fields; contract_version filter; getTalks/authoredBy removed
  src/router.ts, src/agenda.ts  # contract-named fields
  src/db/seed.ts          # one transaction; deletes each engine's rows before inserting its recommendations
  src/index.ts            # exports appRouter, AppRouter, createContext only
  drizzle/0002_referential_integrity.sql, 0003_contract_types.sql (+ meta)
  test/{schema,transform,wire,repo,router,agenda,upsert,seed-path}.test.ts   # updated keys
  test/repo.parity.test.ts   # NEW, runs only when DATABASE_URL is set (CI e2e job)
packages/eslint-config/next.js   # no-restricted-syntax for dynamic driver imports
.github/workflows/ci.yml         # guard-comment grep; parity test step in e2e
apps/web/lib/query-errors.ts     # BAD_REQUEST is permanent
apps/web/components/pick-card.tsx, agenda-item.tsx, app/page.tsx, app/calendar/page.tsx   # take contract types (Task 8)
docs/superpowers/specs/2026-09-12-pluggable-engine-architecture-design.md   # four sentences corrected + rail/calendar sentence
```

---

### Task 1: Referential integrity — foreign keys and seed cross-checks

**Files:**
- Modify: `packages/api/src/db/schema.ts`, `packages/api/src/db/transform.ts`, `packages/api/test/transform.test.ts`
- Generated: `packages/api/drizzle/0002_referential_integrity.sql` + `meta/`

- [ ] **Step 1: Failing tests** (append to `test/transform.test.ts`, inside a new `describe("toSeedFile referential checks")`; `fixture` and the valid `base` seed object from the existing tests are reused):

```ts
const base = () => ({
  contract_version: 1, talks: [fixture("talk")], locations: [],
  recommendations: [fixture("recommendation")], runs: [fixture("run")],
});
// fixture recommendation: for_talk_id 0, candidate_id 12772, run_id "graph_v1-20260912T120000Z-a1b2c3"; fixture talk id 2802.
const withTalks = (ids: number[]) => ({ ...base(), talks: ids.map((id) => ({ ...fixture("talk"), id })) });

test("rejects a recommendation whose candidate_id has no talk", () => {
  const seed = withTalks([0]); // candidate 12772 missing
  expect(() => toSeedFile(seed)).toThrow(/recommendations\[0\]\.candidate_id.*no talk 12772/);
});
test("rejects a recommendation whose for_talk_id has no talk", () => {
  const seed = withTalks([12772]); // anchor 0 missing
  expect(() => toSeedFile(seed)).toThrow(/recommendations\[0\]\.for_talk_id.*no talk 0/);
});
test("rejects a recommendation whose run_id has no run", () => {
  const seed = { ...withTalks([0, 12772]), runs: [{ ...fixture("run"), run_id: "other-run" }] };
  expect(() => toSeedFile(seed)).toThrow(/recommendations\[0\]\.run_id.*no run/);
});
test("rejects duplicate talk ids, run ids, location ids and recommendation keys", () => {
  const ok = withTalks([0, 12772]);
  expect(() => toSeedFile({ ...ok, talks: [...ok.talks, ok.talks[0]] })).toThrow(/talks\[2\]\.id.*duplicate/);
  expect(() => toSeedFile({ ...ok, runs: [ok.runs[0], ok.runs[0]] })).toThrow(/runs\[1\]\.run_id.*duplicate/);
  expect(() => toSeedFile({ ...ok, locations: [{ id: 1, building: "A", room: "1" }, { id: 1, building: "A", room: "2" }] })).toThrow(/locations\[1\]\.id.*duplicate/);
  expect(() => toSeedFile({ ...ok, recommendations: [ok.recommendations[0], ok.recommendations[0]] })).toThrow(/recommendations\[1\].*duplicate/);
});
test("accepts a seed whose references all resolve", () => {
  expect(toSeedFile(withTalks([0, 12772])).recommendations).toHaveLength(1);
});
```

Also update the existing "accepts a contract-shaped seed" test: its single fixture talk (2802) does not contain the recommendation's anchor 0 or candidate 12772, so change it to `withTalks([0, 12772])` (or add those talks). Run `npm run test --workspace=@repo/api -- test/transform.test.ts` → the new tests FAIL (nothing throws).

- [ ] **Step 2: Cross-checks in `transform.ts`**

Replace `const SeedFileSchema = z.strictObject({...})` with the same object followed by `.superRefine(checkReferences)`, and add above it:

```ts
type SeedShape = { talks: { id: number }[]; locations: { id: number }[]; runs: { run_id: string }[];
  recommendations: { for_talk_id: number; candidate_id: number; run_id: string; engine_id: string }[] };

/** Ids must be unique per table and every recommendation must point at a talk and a run in the same seed. */
function checkReferences(seed: SeedShape, ctx: z.RefinementCtx): void {
  const dup = <T>(rows: T[], key: (r: T) => string | number, path: (i: number) => (string | number)[], label: string) => {
    const seen = new Set<string | number>();
    rows.forEach((r, i) => {
      const k = key(r);
      if (seen.has(k)) ctx.addIssue({ code: "custom", path: path(i), message: `duplicate ${label} ${String(k)}` });
      seen.add(k);
    });
  };
  dup(seed.talks, (t) => t.id, (i) => ["talks", i, "id"], "talk id");
  dup(seed.locations, (l) => l.id, (i) => ["locations", i, "id"], "location id");
  dup(seed.runs, (r) => r.run_id, (i) => ["runs", i, "run_id"], "run id");
  dup(seed.recommendations, (r) => `${r.engine_id}/${r.for_talk_id}/${r.candidate_id}`, (i) => ["recommendations", i], "recommendation key");
  const talkIds = new Set(seed.talks.map((t) => t.id));
  const runIds = new Set(seed.runs.map((r) => r.run_id));
  seed.recommendations.forEach((r, i) => {
    if (!talkIds.has(r.for_talk_id)) ctx.addIssue({ code: "custom", path: ["recommendations", i, "for_talk_id"], message: `no talk ${r.for_talk_id} in this seed` });
    if (!talkIds.has(r.candidate_id)) ctx.addIssue({ code: "custom", path: ["recommendations", i, "candidate_id"], message: `no talk ${r.candidate_id} in this seed` });
    if (!runIds.has(r.run_id)) ctx.addIssue({ code: "custom", path: ["recommendations", i, "run_id"], message: `no run ${r.run_id} in this seed` });
  });
}
```

`toSeedFile` already formats the first issue's path as `recommendations[0].candidate_id`. Run the transform tests → green. Run `toSeedFile` once over the committed e2e fixture (`node`/`tsx` one-liner reading `apps/web/e2e/fixtures/app_seed.v2.json`) → must pass; if it does not, the live data has an orphan and Task 9 must be re-planned: STOP and report.

- [ ] **Step 3: Foreign keys in `schema.ts`**

Move the `runs` table definition above `recommendations` (it must be declared first to be referenced). Then:

```ts
    forTalkId: integer("for_talk_id").notNull().references(() => talks.id),
    candidateId: integer("candidate_id").notNull().references(() => talks.id),
    ...
    runId: text("run_id").notNull().references(() => runs.runId),
```

Run `cd packages/api && npx drizzle-kit generate --name referential_integrity` → `drizzle/0002_referential_integrity.sql` with three `ADD CONSTRAINT ... FOREIGN KEY` statements. Run it again → "No schema changes". Run `npm run test --workspace=@repo/api && npm run check-types --workspace=@repo/api && npm run lint --workspace=@repo/api` → green (schema.test still passes: column names unchanged).

- [ ] **Step 4: PR**

```bash
git checkout -b plan4/task-1-referential-integrity main
git add packages/api/src/db packages/api/test/transform.test.ts packages/api/drizzle
git commit -m "feat(api): foreign keys on recommendations; seed rejects orphan references and duplicate keys"
git push -u origin plan4/task-1-referential-integrity
gh pr create --fill --base main
gh pr checks --watch   # all three green (the e2e job applies 0002 to a fresh Postgres and seeds through the new checks)
gh pr merge --merge --delete-branch
```

---

### Task 2: Column types match the contract

**Files:**
- Modify: `packages/api/src/db/schema.ts`, `packages/api/test/schema.test.ts`
- Generated: `packages/api/drizzle/0003_contract_types.sql` + `meta/`

- [ ] **Step 1: Failing test** (append to `test/schema.test.ts`):

```ts
import { getTableColumns } from "drizzle-orm";
test("score is double precision and person ids are bigint, as the contract's number/int allow", () => {
  const rec = getTableColumns(recommendations);
  expect(rec.score.getSQLType()).toBe("double precision");
  const t = getTableColumns(talks);
  expect(t.authorIds.getSQLType()).toBe("bigint[]");
  expect(t.presenterIds.getSQLType()).toBe("bigint[]");
  expect(getTableColumns(runs).anchorIds.getSQLType()).toBe("bigint[]");
});
```

Run → FAIL (`real`, `integer[]`).

- [ ] **Step 2: Schema**

```ts
import { bigint, boolean, doublePrecision, integer, jsonb, pgTable, primaryKey, text, timestamp } from "drizzle-orm/pg-core";
const bigintArray = (name: string) => bigint(name, { mode: "number" }).array().notNull().default(sql`'{}'::bigint[]`);
// talks: authorIds: bigintArray("author_ids"), presenterIds: bigintArray("presenter_ids")
// runs:  anchorIds: bigintArray("anchor_ids")
// recommendations: score: doublePrecision("score").notNull(),
```

Keep `intArray` only if something still uses it; otherwise delete it. `$inferSelect` types stay `number[]` and `number`, so nothing else changes. Run `npx drizzle-kit generate --name contract_types` → `0003_contract_types.sql` with `ALTER COLUMN ... SET DATA TYPE double precision` / `bigint[]` (with `USING` casts if drizzle emits them; if it does not and the SQL would fail on existing rows, add `USING "author_ids"::bigint[]` by hand and confirm a second generate still says no changes). Tests, types, lint → green.

- [ ] **Step 3: PR** as in Task 1 (`plan4/task-2-contract-types`, message "feat(api): score is double precision; person ids are bigint; columns honour the contract's ranges").

---

### Task 3: Only rows of the current contract version are served

**Files:**
- Modify: `packages/api/src/repo.ts`, `packages/api/src/repo.db.ts`, `packages/api/test/repo.test.ts`

- [ ] **Step 1: Failing test** (in `repo.test.ts`, add to the `recs` fixture `rec(10, 11, { rank: 9, contractVersion: 2 })` and this test):

```ts
test("getMatches ignores rows written under another contract version", async () => {
  expect((await repo.getMatches([10], "graph_v1")).map((r) => r.candidateId)).not.toContain(11);
});
```

Run → FAIL (11 is returned). (After Task 6 the key is `candidate_id`; write it for the current names now.)

- [ ] **Step 2: Implement.** `repo.ts` `getMatches` filter adds `&& r.contractVersion === CONTRACT_VERSION` (import `CONTRACT_VERSION` from `@repo/contracts`). `repo.db.ts` `where(and(...))` adds `eq(recommendations.contractVersion, CONTRACT_VERSION)`. Update the JSDoc on `Repo.getMatches`: "match=true rows of one engine written under the current contract version…". The router's `wire.ts` cast now has a filter behind it; update its comment to say so. Tests, types, lint → green.

- [ ] **Step 3: PR** (`plan4/task-3-version-filter`, "fix(api): serve only rows of the current contract version").

---

### Task 4: Close the two guard bypasses

**Files:**
- Modify: `packages/eslint-config/next.js`, `.github/workflows/ci.yml`

- [ ] **Step 1: Plant.** In `apps/web/lib/trpc.ts` add `const _m = await import("drizzle-orm");` won't parse at top level in a non-async module; instead add `export const _probe = () => import("drizzle-orm");`. Add `"drizzle-orm": "*"` to `apps/web/package.json` dependencies (no install). Run `npm run lint --workspace=web` → passes (the gap). Also add `// eslint-disable-next-line no-restricted-imports` above a planted `import "postgres";` → lint passes (the second gap). Record both.

- [ ] **Step 2: Rule.** In `packages/eslint-config/next.js`, in the same rules object as `no-restricted-imports`:

```js
      // no-restricted-imports ignores dynamic import(); this covers it.
      "no-restricted-syntax": [
        "error",
        {
          selector: "ImportExpression > Literal[value=/^(drizzle-orm|postgres)(\\/|$)|^@repo\\/api\\//]",
          message: "Database access lives in @repo/api.",
        },
      ],
```

- [ ] **Step 3: CI guard-comment check.** In `.github/workflows/ci.yml`, `web` job, after Lint:

```yaml
      - name: Guard comments (no disabling the import guards)
        run: |
          if grep -rnE 'eslint-disable[^\n]*no-restricted-(imports|modules|syntax)|@boundaries-ignore' apps packages --include='*.ts' --include='*.tsx' --include='*.js' --include='*.mjs' --exclude-dir=node_modules --exclude-dir=.next; then
            echo "::error::a comment disables an import guard"; exit 1; fi
```

Run the grep locally with the planted disable → matches; lint with the planted dynamic import → fails on `no-restricted-syntax`. Revert both plants and the package.json edit; `git status` clean; root lint 5/5.

- [ ] **Step 4: PR** (`plan4/task-4-guard-bypasses`, "build: forbid dynamic driver imports and guard-disabling comments").

---

### Task 5: Spec corrections

**Files:** `docs/superpowers/specs/2026-09-12-pluggable-engine-architecture-design.md`

- [ ] **Step 1:** Edit these sentences (exact search strings):
  - §5.1: `presenter.picks({ presenterId })` → `presenter.picks(Subject)` where Subject is the strict union `{ presenter_id } | { talk_id }`, optional `engine_id`; the response is `{ presenter_id, anchors: Talk[], recommendations: Pick[] }` with `Pick = Recommendation & { candidate: Talk }`. Same for `presenter.agenda`. Add: "Request and response shapes are zod schemas in `packages/contracts` (`api.ts`), emitted to JSON Schema like the rows, and attached as tRPC output validators."
  - §5.2: "It never sees `evidence`, `engine_id`, `run_id` or `contract_version`." → "It receives the full Recommendation but renders none of `evidence`, `engine_id`, `run_id` or `contract_version`." Append: "The picks rail shows at most 2 core and 3 unexpected picks; the calendar lists every match. The rail is the highlight, the calendar is the complete plan; the two are not meant to agree in count."
  - §6 JSON Schema bullet: "emits `talk.schema.json`, `recommendation.schema.json`, `run.schema.json`" → add "and the API shapes (`subject`, `picks_response`, `agenda_response`)".
  - §6 Enforcement, CODEOWNERS bullet → "`CODEOWNERS` lists the collaborators as a notification list. Branch protection on `main` requires the three CI checks (web, pipeline, e2e) and nothing else: no review requirement, by decision (plan 3, task 7). CI is the only gate."
- [ ] **Step 2: PR** (`plan4/task-5-spec`, "docs(spec): API shapes, wire vs render, six schema files, CI-only gate").

---

### Task 6: The rename — Drizzle properties take the contract's field names, with a parity test

**Files:**
- Modify: `packages/api/src/db/schema.ts`, `src/db/transform.ts`, `src/db/seed.ts`, `src/db/upsert.ts` (doc only), `src/wire.ts`, `src/repo.ts`, `src/repo.db.ts`, `src/router.ts`, `src/agenda.ts`, and every test under `packages/api/test/`
- Create: `packages/api/test/repo.parity.test.ts`
- Modify: `.github/workflows/ci.yml` (parity step in the e2e job)

- [ ] **Step 1: The failing parity test** (written first; it skips without `DATABASE_URL`, so "watch it fail" is done in CI on the PR, and locally by confirming it is skipped):

```ts
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";

import { resolveSeedPath } from "../src/db/seed-path";
import { toSeedFile, toTalkInsert } from "../src/db/transform";
import { memoryRepo, type RecRow, type TalkRow } from "../src/repo";
import { dbRepo } from "../src/repo.db";

// Runs only where a seeded Postgres exists (the e2e CI job). Read-only.
const url = process.env.DATABASE_URL;
const seedPath = resolveSeedPath(process.env, "");
describe.skipIf(!url || !seedPath)("memoryRepo and dbRepo agree on the seeded store", () => {
  const seed = toSeedFile(JSON.parse(readFileSync(seedPath, "utf8")));
  const fake = memoryRepo(seed.talks.map(toTalkInsert) as TalkRow[], seed.recommendations as RecRow[]);
  const talkIds = seed.talks.map((t) => t.id);
  const presenterIds = [...new Set(seed.talks.flatMap((t) => t.presenter_ids))];
  const anchors = [...new Set(seed.recommendations.map((r) => r.for_talk_id))];
  const engines = [...new Set(seed.recommendations.map((r) => r.engine_id))];

  test("getTalk", async () => {
    for (const id of [...talkIds, 999_999]) expect(await dbRepo.getTalk(id)).toEqual(await fake.getTalk(id));
  });
  test("anchorsFor", async () => {
    for (const p of [...presenterIds, 404]) expect(await dbRepo.anchorsFor(p)).toEqual(await fake.anchorsFor(p));
  });
  test("getMatches: same rows, same order, same candidates", async () => {
    for (const e of [...engines, "other"]) expect(await dbRepo.getMatches(anchors, e)).toEqual(await fake.getMatches(anchors, e));
    expect(await dbRepo.getMatches([], engines[0]!)).toEqual([]);
  });
});
```

(`toEqual` compares `Date` objects by value; after Task 2 scores are float64 on both sides, so no tolerance is needed. `toTalkInsert` sets every column, hence the `as TalkRow`.) Locally: `npm run test --workspace=@repo/api -- test/repo.parity.test.ts` → 1 skipped.

- [ ] **Step 2: Rename the schema properties.** In `schema.ts`, every property becomes its column name and the explicit name string is dropped: `external_id: text()`, `is_invited: boolean().notNull().default(false)`, `start: timestamp({ withTimezone: true })`, `author_ids: bigintArray()`, … for all 25 talk columns, 13 recommendation columns (`for_talk_id`, `candidate_id`, `cross_domain`, `strongest_parallel`, `shared_methods`, `engine_id`, `run_id`, `contract_version`), 11 run columns (`run_id`, `engine_id`, `engine_version`, `corpus_hash`, `anchor_ids`, `started_at`, `finished_at`, `index_path`, `contract_version`) and `locations`. Helpers become `const textArray = () => text().array()...`. Run `cd packages/api && npx drizzle-kit generate` → **must print "No schema changes"**; if it emits anything, a name string was dropped wrongly. `schema.test.ts` passes unchanged (it compares column `name`).

- [ ] **Step 3: Collapse the mappers.** `transform.ts`:

```ts
const date = (v: string | null) => (v === null ? null : new Date(v));
export function toTalkInsert(t: Talk): TalkInsert { return { ...t, start: date(t.start), end: date(t.end) }; }
export function toRunInsert(m: Run): RunInsert { return { ...m, started_at: new Date(m.started_at), finished_at: new Date(m.finished_at) }; }
// toRecommendationInsert and toLocationInsert are deleted; seed.ts inserts seed.recommendations and seed.locations directly.
```

`wire.ts`:

```ts
const iso = (d: Date | null) => (d === null ? null : d.toISOString());
export function toTalk(r: TalkRow): Talk { return { ...r, start: iso(r.start), end: iso(r.end) }; }
export function toRecommendation(r: RecRow): Recommendation {
  // The column is a plain integer; getMatches filters on CONTRACT_VERSION, and .output() rejects anything else.
  return { ...r, contract_version: r.contract_version as Recommendation["contract_version"] };
}
export function toPick(m: MatchRow): Pick { const { candidate, ...rec } = m; return { ...toRecommendation(rec), candidate: toTalk(candidate) }; }
```

`repo.ts` / `repo.db.ts` / `router.ts` / `agenda.ts`: replace every camelCase row property with its contract name (`presenterIds`→`presenter_ids`, `authorIds`→`author_ids`, `engineId`→`engine_id`, `forTalkId`→`for_talk_id`, `candidateId`→`candidate_id`, `crossDomain`→`cross_domain`, `sessionTitle`→`session_title`, `contractVersion`→`contract_version`, …). `AgendaInput` in `agenda.ts` drops `sessionTitle` (unused by the grouping; extra fields are carried through generically). `seed.ts`: `updateSet(talks, ["id"])` unchanged (skip lists were already SQL names); `upsert.ts` doc comment: property name and column name are now the same string. Then update every test's fixtures and assertions to the contract names (`repo.test.ts`, `router.test.ts`, `wire.test.ts`, `transform.test.ts`, `upsert.test.ts` expects keys like `external_id`, `agenda.test.ts`). Do not weaken any assertion; the router tests' inputs/outputs were already contract-shaped after plan 3.

Run `npm run test --workspace=@repo/api && npm run check-types && npm run lint && env -u DATABASE_URL npm run build --workspace=web` → green. `apps/web` needs no change (it reads contract-shaped responses already).

- [ ] **Step 4: CI parity step.** In `ci.yml`, `e2e` job, after "Migrate and seed the throwaway database":

```yaml
      - name: Repository parity (memoryRepo vs dbRepo on the seeded store)
        run: npm run test --workspace=@repo/api -- test/repo.parity.test.ts
```

- [ ] **Step 5: PR** (`plan4/task-6-rename`, "refactor(api): Drizzle properties are the contract's field names; mappers collapse; parity test on the seeded store"). Watch the e2e job: the parity step must run (not skip) and pass. If it fails, the rename changed behaviour: fix the code, never the test.

---

### Task 7: Trim, retry rule, transactional seed

**Files:**
- Modify: `packages/api/src/index.ts`, `src/repo.ts`, `src/repo.db.ts`, `test/repo.test.ts`, `src/db/seed.ts`, `apps/web/lib/query-errors.ts`, `apps/web/test/lib/query-errors.test.ts`

- [ ] **Step 1: Failing tests.** `query-errors.test.ts`: `retryUnlessNotFound(0, { data: { code: "BAD_REQUEST" } })` is `false`. `repo.test.ts`: delete the `getTalks`/`authoredBy` tests (dead in the request path; author exclusion is Python's). Run → the retry test FAILS.
- [ ] **Step 2: Implement.** `query-errors.ts`: permanent codes are `NOT_FOUND` and `BAD_REQUEST`. `Repo` interface loses `getTalks` and `authoredBy`; remove both implementations. `index.ts` exports only `appRouter`, `type AppRouter`, `createContext` (tests import from `../src/*` directly; confirm with grep that nothing else imports the removed names). `seed.ts`: wrap the four loops in `await db.transaction(async (tx) => { ... })` using `tx` for every insert, and before the recommendations loop: `await tx.delete(recommendations).where(inArray(recommendations.engine_id, [...new Set(seed.recommendations.map((r) => r.engine_id))]))` so a reseed replaces each engine's rows completely (stale rows gone). Keep the counts log. Gate check: `cd packages/api && env -u DATABASE_URL SEED_PATH=../../apps/web/e2e/fixtures/app_seed.v2.json npx tsx src/db/seed.ts` → exits 1 on the DATABASE_URL message.
- [ ] **Step 3: PR** (`plan4/task-7-trim`, "refactor(api): trim the barrel and dead repo methods; transactional seed replaces each engine's rows; web does not retry BAD_REQUEST"). The e2e job runs the seed inside the transaction against a fresh database.

---

### Task 8: UI components take contract types

**Files:**
- Modify: `apps/web/components/pick-card.tsx`, `pick-rail.tsx`, `agenda-item.tsx`, `agenda.tsx`, `app/page.tsx`, `app/calendar/page.tsx`, `test/components/pick-rail.test.tsx`, `test/components/agenda.test.tsx`

- [ ] **Step 1: Failing tests.** Rewrite the component test fixtures to contract shapes: rail tests build `Pick` objects from `@repo/contracts` (`candidate_id`, `for_talk_id`, `cross_domain`, `shared_methods`, `candidate: { title, session_title, units, start, … }`); agenda tests build `AgendaItem` objects (`session_title`, `kind`, `units`, `transit`). Keep every assertion (percent score, chips, anchor chip, caps, empty slots, dots, Denver time). Run → FAIL on the old prop names.
- [ ] **Step 2: Implement.** `PickRail` props: `{ anchors: { id: number; title: string }[]; recommendations: Pick[] }`; `PickCard` takes `pick: Pick` and reads `pick.candidate.title`, `pick.candidate.session_title`, `pick.candidate.start`, `pick.shared_methods`, `pick.cross_domain`, `pick.for_talk_id`, `pick.candidate_id`. `AgendaEntry` is replaced by `AgendaItem` from the contract (`session_title`, `start: string`, `end: string | null`). `app/page.tsx` passes `picks.data.recommendations` straight through; `app/calendar/page.tsx` passes `day.items` straight through. Delete the local `Pick` and `AgendaEntry` interfaces. Web tests, root types, lint, build → green.
- [ ] **Step 3: PR** (`plan4/task-8-ui-contract-types`, "refactor(web): components render the contract Pick and AgendaItem directly").

---

### Task 9: GATED — apply migrations 0002 and 0003 to the live store

**Requires Rupert's explicit go. Touches the Supabase database (`DATABASE_URL` in `packages/api/.env`).**

- [ ] **Step 1: Ask.** "Task 9 applies two migrations to the live Supabase Postgres: foreign keys on recommendations (fails if any existing row points at a missing talk or run; the seeded data was checked in Task 1 and resolves) and column type changes (score to double precision, person id arrays to bigint). Then it reseeds so scores regain full precision. Proceed?"
- [ ] **Step 2:** `cd packages/api && set -a && . ./.env && set +a && npm run db:migrate && npm run db:seed` → migrations 0002, 0003 applied; "Seeded 58 talks / 118 locations / 1 runs / 19 recommendations".
- [ ] **Step 3:** Smoke: with `DATABASE_URL` sourced, `npm run test --workspace=@repo/api -- test/repo.parity.test.ts` with `SEED_PATH` pointing at `apps/web/e2e/fixtures/app_seed.v2.json` → passes against the live store (read-only). Then the Playwright suite against a dev server as in plan 2 Task 9.
- [ ] **Step 4:** Append `Migrated live on <date>; parity and e2e green.` under this task; commit through a PR.

---

## Self-review

- **Audit coverage.** I1 → Task 1. I2, I3 → Task 2. I4 → Task 3. I5 → Task 4. I6 and M2 sentence → Task 5. Duplication rows for transform/wire/schema/router → Task 6; web rows → Task 8; barrel and dead methods (M10) → Task 7; M1 seed transaction and stale rows → Task 7; M3 retry → Task 7. Parity test → Task 6. Not in scope, by decision: Python codegen, GIN index, projection, Prettier, browser cache, M4 Location schema, M5 timestamp spellings, M9 hygiene.
- **Placeholders.** None. Task 6 Step 2 lists the rename rule rather than all 49 lines; the invariant that proves it ("drizzle-kit generate prints No schema changes") is stated.
- **Type consistency.** After Task 6, `TalkRow`/`RecRow` keys are the contract's; `toTalkInsert`/`toRunInsert` return spreads; `toRecommendationInsert`/`toLocationInsert` are gone and `seed.ts` inserts `seed.recommendations`/`seed.locations` directly; Task 7 then wraps those inserts in a transaction. Task 3's test is written with pre-rename keys and must be renamed in Task 6 with the rest. `CONTRACT_VERSION` comes from `@repo/contracts` in Tasks 3 and 6. CI step names added in Tasks 4 and 6 are inside existing jobs, so the branch-protection contexts are unchanged.
- **Order dependencies.** Task 2 before Task 6 (parity test needs float64 scores). Task 1 before Task 9. Tasks 4, 5, 7, 8 are independent of the others except that 7 and 8 assume 6's field names.
