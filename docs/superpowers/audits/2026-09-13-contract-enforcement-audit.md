# Contract and Enforcement Audit — 2026-09-13

Scope: the contract layer (`packages/contracts` and its TypeScript and Python restatements), the
data path from engine output to screen (`packages/api`, `apps/web`), and the enforcement tooling
(Turborepo boundaries, ESLint guards, import-linter, CI, branch protection). Read-only; every
guard was exercised by planting a violation and reverting it; every measurement is from a probe on
the committed tree at `main` (`12feee8`). Three auditors' reports were cross-checked and the top
findings verified directly against the code.

**Verdict.** The framework is consistent. All copies of every contract field agree on name, order
and nullability, both validators give identical verdicts on all eleven fixtures, every write path
validates first, and every violation class the auditors could construct is caught in CI. Nothing
on `main` is serving bad data. The findings below are latent defects, duplication, and places
where the spec no longer describes reality. None of the recommended fixes changes the wire
contract; the ones that touch the database change column types to match the contract, not the
contract to match the columns.

---

## 1. Findings, ranked

### Critical

None.

### Important (correctness; contract-preserving)

**I1. A recommendation whose candidate talk is missing is dropped silently.**
`packages/api/src/repo.db.ts:41` inner-joins candidates; `repo.ts:36-39` mirrors it. No foreign
keys exist in either migration, and `toSeedFile` (`packages/api/src/db/transform.ts`) accepts a
recommendation whose `candidate_id` or `run_id` matches nothing, and duplicate talk ids. Probe:
all three accepted. Result: the rail is shorter than the engine's output and nothing logs it.
*Fix:* foreign keys `recommendations.candidate_id → talks.id`, `for_talk_id → talks.id`,
`run_id → runs.run_id` via a drizzle-kit migration (the seed already writes talks and runs first),
plus id cross-checks and duplicate-key rejection in `toSeedFile` with tests.

**I2. `score` is stored as `real` (float4); the value written is not the value read.**
`packages/api/src/db/schema.ts:61`. The contract is a float64 in [0, 1]; the seed holds
0.8666666666666667 and reads back as ~0.8666667. Nothing renders wrong (percent display), and
graph_v1 scores are 0.067 apart, but `memoryRepo` and `dbRepo` disagree on every non-dyadic score
and the agenda's kind rule uses strict `>`. A cosine-score engine could collide at float4.
*Fix:* `doublePrecision("score")`, one-column migration.

**I3. Id columns are int32 while the contract and the conference API allow larger values.**
`schema.ts` uses `integer` for talk ids and for `author_ids` / `presenter_ids`; the contract's
`z.int()` allows up to 2^53. The repo already knows the API exceeds int32 (`locations.id` is
`bigint` for exactly this reason). Current maxima are safe (author 224187, talk 15020). A row that
passes both validators would fail the insert with a range error.
*Fix:* `bigint` (mode number) for the person-id arrays at least; the talk id columns can follow
when the 1k-talk build lands.

**I4. `contract_version` is never filtered on read, so one stale row fails the whole request.**
`getMatches` filters on `engine_id` and `match` only. A version-2 row passes `wire.ts` (cast) and
then fails `.output(PicksResponseSchema)`, turning the entire picks response into a 500. Spec §6
says "the API serves only versions it understands"; today it serves none if any is wrong.
*Fix:* `eq(recommendations.contractVersion, CONTRACT_VERSION)` in `dbRepo.getMatches` and the
matching filter in `memoryRepo`, with a test.

**I5. Two guard bypasses in the app-side import rules.**
(a) A dynamic `await import("drizzle-orm")` passes both `turbo boundaries` and ESLint once the
driver is listed in the app's dependencies (`no-restricted-imports` ignores `ImportExpression`).
(b) One `// eslint-disable-next-line` silences the driver rules; nothing forbids disable comments.
Both are visible in a PR diff, neither fails CI.
*Fix:* a `no-restricted-syntax` rule on `ImportExpression` with the same source list, in
`packages/eslint-config/next.js`; and either `eslint-plugin-eslint-comments` (no-unlimited-disable,
no disables naming the two rules) or a one-line CI grep that fails on any disable naming
`no-restricted-imports` / `no-restricted-modules` or any `@boundaries-ignore`.

**I6. The binding spec is stale in four places.**
`docs/superpowers/specs/2026-09-12-pluggable-engine-architecture-design.md`:
§6 says CODEOWNERS requires review on `packages/contracts` (no review requirement exists, by
Rupert's decision; CI is the only gate); §5.2 says the UI "never sees" `evidence`, `engine_id`,
`run_id`, `contract_version` (it receives them and never *renders* them: `PickSchema` has 14
fields); §5.1 writes the picks input as `{ presenterId }` (it is the strict `Subject` union with
`presenter_id` / `talk_id`); §6 says the emitter writes three schema files (it writes six).
*Fix:* edit the four sentences. Documentation only.

### Minor

- **M1. Seed script.** Not transactional; never deletes an engine's stale rows on reseed (wrong the
  first time a rerun drops a candidate); duplicate keys within one batch raise, across batches
  last-write-wins. Wrap the four loops in `db.transaction` and delete the engine's rows inside it;
  reject duplicates in `toSeedFile` (I1). `process.exit(0)` is fine.
- **M2. The rail caps at 2 core + 3 unexpected; the agenda lists every match.** A candidate ranked
  6th appears on the calendar as "core" with no card on the rail. Product decision needed: if the
  two surfaces should agree, the cap belongs on the server. The merge and tie rules themselves are
  identical on both sides (verified).
- **M3. `retryUnlessNotFound` retries `BAD_REQUEST`**, which can never succeed. One-line fix.
- **M4. `Location` is a contract shape defined outside the contracts package**
  (`transform.ts:15`), with no column-parity test, and a bare `z.int()` id. Move it or document it.
- **M5. Two legal timestamp spellings coexist in one seed** (talks with `.000Z`, run manifest
  without). Both valid; a string comparison would see a false difference. Normalise in the loader
  if it ever matters.
- **M6. e2e seed fixture is kept in sync with the pipeline export by hand.** Byte-identical today;
  nothing checks it later. Add a comment naming the regenerating command, or a pytest that
  compares the exporter's output against the fixture.
- **M7. Formatting is claimed but never checked.** `npm run format` exists; CI never runs
  `prettier --check`; 44 files (mostly generated shadcn) differ. Format once and add the check, or
  drop the script.
- **M8. Python cannot validate the three API schemas** (`KINDS` lists rows only). Deliberate and
  documented; drift in those files has no Python-side check. Acceptable.
- **M9. Hygiene.** `data.dependents.allow: ["web"]` is a package name, not a tag (works, stricter
  than the tag form; add a comment). Root README "Apps and Packages" is stock starter text and
  omits `@repo/api` and `@repo/contracts`. No `.nvmrc` / `engine-strict` while `engines` is
  `>=24` and local Node is 22. zod is a caret range in three packages (lockfile pins 4.4.3; CI uses
  `npm ci`; pin exactly to remove the nuisance).
- **M10. Five of seven barrel exports in `packages/api/src/index.ts` have no consumer**; `getTalks`
  and `authoredBy` are dead in the request path (author exclusion happens in Python). Trim, or
  note why they stay.

---

## 2. Duplication inventory

| Where | What is restated | What removes it | Lines | Risk |
|---|---|---|---|---|
| `packages/api/src/db/transform.ts` (4 mappers) | every field, contract → Drizzle camelCase | rename Drizzle table properties to the contract's snake_case names; mappers become spread + two Date conversions | ~27 | Low |
| `packages/api/src/wire.ts` (3 mappers) | every field, Drizzle camelCase → contract | same rename; `toTalk` = spread + `iso()` twice, `toRecommendation` = spread + the version cast | ~19 | Low |
| `packages/api/src/db/schema.ts` | 52 explicit SQL name strings | same rename; property name becomes the column name | 0 lines, 52 strings | Low |
| `packages/api/src/router.ts:76-80` | 10 AgendaItem fields cut from a row | shrinks to a destructure | ~3 | Low |
| `apps/web/app/page.tsx`, `calendar/page.tsx` | 10 + 9 fields remapped into the UI's own view types | components take `Pick` / `AgendaItem` from `@repo/contracts` | ~28 | Medium (component test fixtures) |
| `pipeline/src/gps_data/talk.py`, `gps_core/records.py` | 25 + 13 + 11 fields as hand-written records | `datamodel-code-generator` from the JSON Schema | ~56 | High: generated models lose the frozen, hashable dataclasses the pipeline relies on and add construction-time validation. Already protected by tests that push full instances through `validate`. **Do not do.** |

The enabling change is one rename, verified by probe against drizzle-orm 0.45.2: naming the
properties `external_id` etc. makes `$inferSelect` produce contract keys while the generated SQL
is byte-identical, so **no migration and no wire change**. Total safely removable: about 46 lines
in `packages/api`, optionally 28 more in `apps/web`. The safety net that must stay is
`packages/api/test/schema.test.ts`, which asserts each table has exactly the contract's field
names; after the rename a stray column would reach the strict output validator at runtime instead
of failing at compile time, and that test is what catches it first.

**Fake vs real repository parity.** `memoryRepo` and `dbRepo` agree on 18 of 20 behaviours
checked by reading; the two disagreements are I2 (float4) and the fake's ability to hold duplicate
`(engine, anchor, candidate)` rows the primary key forbids. Nothing executes `dbRepo` in any test.
Cheapest parity test: a `describe.skipIf(!process.env.DATABASE_URL)` vitest file that seeds the
same fixture rows and asserts deep-equal results from both repos for all five methods, run in the
existing e2e CI job, which already stands up Postgres 16. No new dependency; pglite (25 MB) is
feasible via Drizzle's first-party driver but not worth it.

---

## 3. Performance (no change recommended)

| Operation | Cost |
|---|---|
| `TalkSchema.parse`, one row | 1.9 µs |
| `PicksResponseSchema.parse`, 3 anchors × 60 picks, realistic abstracts | 0.17 ms |
| `JSON.stringify` of that same response, for scale | 0.23 ms |
| `toSeedFile` on the 195 KB seed | 0.18 ms |
| Python `validate("talk", row)`, cached validator | 140 µs |
| `turbo boundaries` / `lint-imports` / full TS tests / pytest | 0.3 s / 0.2 s / 1.9 s / 2.7 s |
| CI jobs web / pipeline / e2e | ~80 s / ~50 s warm / ~105 s |

Output validation costs less than serialising the response. Picks and agenda each make exactly two
queries, with no N+1. A Talk that is both anchor and candidate is validated twice (0.003 ms).
Python validates each recommendation twice (run driver, then seed writer); under a second even at
1,000 talks, and the second pass is what guarantees the seed file. `getMatches` selects all 25
Talk columns including `abstract` for every candidate; the agenda needs 8. Unmeasurable at 58
talks; revisit with the 1k build together with a GIN index on `presenter_ids` (today a sequential
scan). The slowest CI step is the Playwright browser download; cacheable, saves ~30 s, optional.
`fastjsonschema` would make Python validation 10–50× faster from the same schema files if ever
needed.

---

## 4. Coverage map (what catches what)

| Violation | Guard | Runs in |
|---|---|---|
| Engine writes a bad row | `validate()` against the committed JSON Schema | pipeline tests, CI |
| Seed writes a bad row | strict `toSeedFile` | api tests, CI e2e |
| DB column drifts from contract | `schema.test.ts` | CI web |
| Emitted schema drifts / new schema uncommitted | drift test + re-emit with `git add -N` + diff | CI web |
| App imports a driver (ESM / CommonJS / deep path) | ESLint rules + `turbo boundaries` | CI web |
| App imports a driver (dynamic `import()`) | boundaries only while undeclared | **gap (I5)** |
| Wrong package dependency | boundaries tags | CI web |
| Engine imports store / run / registry; data imports core | import-linter | CI pipeline |
| API returns a non-contract row | tRPC `.output()` from contract schemas | runtime + tests |
| Direct push / red merge to `main` | branch protection, admins included | GitHub |
| Contract change without a second reader | none, by decision | — |

---

## 5. Recommended sequencing

1. **Correctness, one PR each, all migrations:** I2 (`doublePrecision`), I3 (`bigint` person ids),
   I1 (foreign keys + seed cross-checks), I4 (version filter). Each is small and independently
   shippable through the CI gate.
2. **Guards and docs, one PR:** I5 (dynamic-import rule, disable-comment guard), I6 (spec edits),
   M9 comment and README, M3.
3. **Deduplication (plan 4):** the Drizzle property rename with the parity test landing in the same
   change, since the rename is exactly the kind of mechanical edit a parity test protects. Then
   trim the barrel (M10) and decide M2.
4. **Later:** seed transaction and stale-row delete (M1) before the first reseed of a rerun; GIN
   index and projection with the 1k build.

---

## 6. Verified consistent (so the reader knows what was checked)

Field counts Talk 25 / Recommendation 13 / Run 11 / Pick 14 / AgendaItem 10, asserted in both
languages. Drizzle column names equal contract keys for all three tables. All 11 fixtures give the
same verdict under zod and jsonschema, loaded from the same files; Python resolves `$defs.Talk`.
`emitAll` deterministic; drift caught by deep-equal in vitest and by bytes in CI. Every write path
validates first (four TS inserts downstream of `toSeedFile`; six Python `validate` calls). Error
masking holds over HTTP; no Drizzle message escapes; `NOT_FOUND` carries only the requested id.
Rail and agenda merge rules identical (max score, first on ties, strict `>`). Boundaries, ESLint
ESM/CommonJS rules, import-linter, branch protection, and CI contexts all verified firing and
mutually consistent; `globalEnv` matches the variables actually read.
