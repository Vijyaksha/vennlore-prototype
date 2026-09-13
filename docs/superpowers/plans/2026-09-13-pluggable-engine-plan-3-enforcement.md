# Pluggable Engine — Plan 3: Enforcement

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the contract the enforced truth: every API request and response shape is declared in `packages/contracts` and validated at runtime, a change to the contract fails every non-conforming consumer in CI, no package can reach across the contract boundary, and `main` cannot take a change that skips those checks.

**Architecture:** Three layers of enforcement. (1) *Shape:* the API's inputs and responses become zod schemas in `@repo/contracts`, emitted to JSON Schema like the row schemas; the router attaches them as tRPC `.output()` validators and serves contract rows (snake_case, ISO timestamps), so one row shape really does flow from engine to screen. (2) *Reach:* Turborepo `boundaries` tags fix which workspace package may depend on which; an ESLint rule keeps database drivers out of the app; `import-linter` fixes the Python layering so an engine can never write to the store directly. (3) *Gate:* a GitHub Actions workflow runs all suites, the boundary checks, the schema-drift check and the Playwright e2e against a throwaway Postgres container on every push and PR; CODEOWNERS and branch protection on `main` require those checks to pass.

**Tech Stack:** Turborepo 2.10 (`turbo boundaries`, experimental), tRPC v11 `.output()`, zod 4 `z.toJSONSchema`, ESLint `no-restricted-imports`, import-linter (Python), GitHub Actions with `actions/setup-node@v4` (Node 24, per `engines`) and `astral-sh/setup-uv@v6`, `gh` CLI for branch protection.

**Design decisions honoured (spec §5.1, §6):** the contract is the source of truth and is additive here: no row field changes, so `contract_version` stays 1. Responses embed the existing `Talk` and `Recommendation` row schemas rather than a second camelCase shape, closing the gap plan 2 left (the API served Drizzle property names). Output validation failing is an `INTERNAL_SERVER_ERROR`, which `trpc.ts` already masks outside development. Python consumes only the three row schemas; the new schema files exist for other consumers and for the drift test, and the Python `KINDS` tuple is unchanged.

**Not in this plan:** the replay test, baseline engines, seed transactionality, the picks §5.2 evidence question (all still deferred), and merging `feat/stage0-engine` into `main` (use superpowers:finishing-a-development-branch after Task 7).

**Rules for every task:** TDD (failing test, watch it fail, implement, green). For configuration tasks (boundaries, lint rules, CI) the "failing test" is a deliberate violation that must be reported, then reverted. Surgical edits. Extensionless relative imports inside `packages/*`. Never stage `docs/business/`, `scratchpad/`, `pipeline/out/`, or any `.env`. Never connect to a database. Commit trailer, on its own line after a blank line:

```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
```

**Known environment facts:** local Node is v22.20 while `package.json` `engines` says `>=24`; CI uses 24 and Task 6 records the discrepancy. `main` is currently unprotected and the repo has no `.github/` directory. `gh` is authenticated as Rupertlim88. `turbo boundaries` exists in the installed 2.10.12.

---

## Execution notes (2026-09-13)

- **Task 1 review changes.** `Talk` carries `.meta({ id: "Talk" })`, so the emitted picks_response schema references one `$defs.Talk` instead of inlining it twice. `Recommendation` has the same id but still inlines inside `Pick`, because zod's `.extend()` builds a new object without the id; a test pins that. `AgendaDay` is titled and its `date` is `z.iso.date()`. Invalid fixtures exist for `subject` (both ids) and `picks_response` (missing candidate); the Python invalid-fixture test skips kinds outside its row `KINDS`, since Python validates rows only. Field-count guards: Pick 14, AgendaItem 10.

## File structure (end state)

```
packages/contracts/
  src/api.ts                     # NEW: SubjectSchema, EngineIdSchema, PickSchema, PicksResponseSchema,
                                 #      AgendaKindSchema, ConnectionSchema, AgendaItemSchema, AgendaDaySchema, AgendaResponseSchema
  src/schemas.ts                 # SCHEMAS gains subject, picks_response, agenda_response
  src/index.ts                   # re-exports api.ts
  schema/{subject,picks_response,agenda_response}.schema.json   # emitted, committed
  fixtures/valid/{subject,picks_response,agenda_response}.json  # NEW
  test/schemas.test.ts           # field-count tests for the new kinds
  turbo.json                     # NEW: tags ["contract"]
packages/api/
  src/wire.ts                    # NEW: toTalk, toRecommendation, toPick (Drizzle row -> contract row)
  src/router.ts                  # inputs/outputs from @repo/contracts; serves contract rows
  src/index.ts                   # exports wire helpers
  test/wire.test.ts              # NEW
  test/router.test.ts            # snake_case + ISO expectations
  turbo.json                     # NEW: tags ["data"]
packages/ui/turbo.json           # NEW: tags ["ui"]
packages/eslint-config/turbo.json, packages/typescript-config/turbo.json   # NEW: tags ["tooling"]
apps/web/
  turbo.json                     # NEW: tags ["app"]
  eslint.config.js               # no-restricted-imports for drivers and deep api paths
  package.json                   # + @repo/contracts (type import)
  lib/conference.ts              # Subject = contract Subject ({presenter_id}|{talk_id})
  app/page.tsx, app/calendar/page.tsx   # read contract rows
  test/lib/subject.test.ts       # snake_case expectations
  e2e/kindred.e2e.ts             # snake_case input/output
apps/docs/turbo.json             # NEW: tags ["app"]
turbo.json                       # boundaries.tags rules
package.json                     # "boundaries": "turbo boundaries"
pipeline/
  .importlinter                  # NEW
  pyproject.toml                 # dev group + import-linter
  README.md                      # lint-imports in Run
  tests/**                       # data-dependent tests skip without data/
apps/web/e2e/fixtures/app_seed.v2.json   # NEW: frozen seed for CI/local e2e
apps/web/playwright.config.ts    # webServer starts `next start` when no base URL
packages/api/src/db/seed-path.ts # NEW: SEED_PATH override
compose.yaml                     # NEW: local throwaway Postgres
.github/workflows/ci.yml         # NEW (jobs: web, pipeline, e2e)
.github/CODEOWNERS               # NEW
```

---

### Task 1: API request and response schemas in the contract

**Files:**
- Create: `packages/contracts/src/api.ts`, `packages/contracts/fixtures/valid/subject.json`, `packages/contracts/fixtures/valid/picks_response.json`, `packages/contracts/fixtures/valid/agenda_response.json`
- Modify: `packages/contracts/src/schemas.ts`, `packages/contracts/src/index.ts`, `packages/contracts/test/schemas.test.ts`
- Generated: `packages/contracts/schema/{subject,picks_response,agenda_response}.schema.json`

- [x] **Step 1: Failing tests**

Append to `packages/contracts/test/schemas.test.ts`:

```ts
import { AgendaResponseSchema, PicksResponseSchema, SubjectSchema } from "../src/index";

describe("api schemas", () => {
  test("subject accepts exactly one of presenter_id or talk_id", () => {
    expect(SubjectSchema.safeParse({ presenter_id: 7 }).success).toBe(true);
    expect(SubjectSchema.safeParse({ talk_id: 0 }).success).toBe(true);
    expect(SubjectSchema.safeParse({ talk_id: 0, engine_id: "other" }).success).toBe(true);
    expect(SubjectSchema.safeParse({ presenter_id: 7, talk_id: 0 }).success).toBe(false);
    expect(SubjectSchema.safeParse({ presenter_id: 0 }).success).toBe(false);
    expect(SubjectSchema.safeParse({ talk_id: 0, engine_id: "DROP TABLE" }).success).toBe(false);
    expect(SubjectSchema.safeParse({ talk_id: 0, engine_id: "a".repeat(65) }).success).toBe(false);
  });
  test("picks response embeds contract rows and a candidate per recommendation", () => {
    const row = read("fixtures/valid/picks_response.json");
    expect(PicksResponseSchema.safeParse(row).success).toBe(true);
    const bad = { ...row, recommendations: [{ ...row.recommendations[0], candidate: undefined }] };
    expect(PicksResponseSchema.safeParse(bad).success).toBe(false);
  });
  test("agenda response items carry kind, units and transit", () => {
    const row = read("fixtures/valid/agenda_response.json");
    expect(AgendaResponseSchema.safeParse(row).success).toBe(true);
    const bad = structuredClone(row);
    bad.days[0].items[0].kind = "later";
    expect(AgendaResponseSchema.safeParse(bad).success).toBe(false);
  });
});
```

The existing loops ("valid fixtures parse", "committed JSON Schema matches the zod source", "every committed schema file has an emitter entry") pick the new kinds up automatically once they are in `SCHEMAS`.

Create the three fixtures. `fixtures/valid/subject.json`:

```json
{ "talk_id": 0 }
```

`fixtures/valid/picks_response.json` embeds the existing talk and recommendation fixtures verbatim. Generate it rather than retyping 40 lines:

```bash
cd packages/contracts && node -e '
const fs = require("node:fs");
const talk = JSON.parse(fs.readFileSync("fixtures/valid/talk.json", "utf8"));
const rec = JSON.parse(fs.readFileSync("fixtures/valid/recommendation.json", "utf8"));
const out = { presenter_id: null, anchors: [talk], recommendations: [{ ...rec, candidate: talk }] };
fs.writeFileSync("fixtures/valid/picks_response.json", JSON.stringify(out, null, 2) + "\n");
'
```

`fixtures/valid/agenda_response.json`:

```json
{
  "presenter_id": 7,
  "days": [
    {
      "date": "2026-03-19",
      "items": [
        {
          "id": 10, "title": "My first talk", "session_title": null,
          "start": "2026-03-19T14:00:00.000Z", "end": "2026-03-19T14:12:00.000Z",
          "building": "Convention Center", "room": "Bluebird 2A",
          "units": [], "kind": "mine", "transit": null
        },
        {
          "id": 2802, "title": "Bluebird talk", "session_title": "Organic Electronics & Photonics",
          "start": "2026-03-19T15:12:00.000Z", "end": "2026-03-19T15:24:00.000Z",
          "building": "Convention Center", "room": "Bluebird 3C",
          "units": ["DPOLY"], "kind": "core", "transit": { "walk": 15, "slack": 45, "tight": false }
        }
      ]
    }
  ]
}
```

- [x] **Step 2: Run to verify failure**

Run: `npm run test --workspace=@repo/contracts`
Expected: FAIL. The new `describe("api schemas")` fails on missing exports; "valid fixtures parse" does not yet see the new kinds.

- [x] **Step 3: Implement `src/api.ts`**

```ts
import { z } from "zod";

import { RecommendationSchema } from "./recommendation";
import { TalkSchema } from "./talk";

/** Engine ids follow the row rule; the API also caps the length a client may send. */
export const EngineIdSchema = RecommendationSchema.shape.engine_id.max(64);

/** Who the picks are for: a presenter (every talk they present is an anchor) or one talk.
 *  Strict on both branches so a request naming both is rejected, not silently resolved. */
export const SubjectSchema = z
  .union([
    z.strictObject({ presenter_id: z.int().min(1), engine_id: EngineIdSchema.optional() }),
    z.strictObject({ talk_id: z.int().min(0), engine_id: EngineIdSchema.optional() }),
  ])
  .meta({ title: "Subject" });
export type Subject = z.infer<typeof SubjectSchema>;

/** A matched recommendation joined with its candidate talk. */
export const PickSchema = RecommendationSchema.extend({ candidate: TalkSchema }).meta({ title: "Pick" });
export type Pick = z.infer<typeof PickSchema>;

export const PicksResponseSchema = z
  .strictObject({
    presenter_id: z.int().min(1).nullable(),
    anchors: z.array(TalkSchema),
    /** match=true rows for the anchors, ordered by for_talk_id, rank, candidate_id. */
    recommendations: z.array(PickSchema),
  })
  .meta({ title: "PicksResponse" });
export type PicksResponse = z.infer<typeof PicksResponseSchema>;

export const AgendaKindSchema = z.enum(["mine", "core", "surprise"]);
export type AgendaKind = z.infer<typeof AgendaKindSchema>;

/** Walking connection from the previous item on the same day. */
export const ConnectionSchema = z.strictObject({
  walk: z.int().min(0),
  slack: z.number(),
  tight: z.boolean(),
});
export type Connection = z.infer<typeof ConnectionSchema>;

/** The slim agenda item the calendar renders: not the whole Talk. Only timed talks appear, so start is non-null. */
export const AgendaItemSchema = z
  .strictObject({
    id: z.int().min(0),
    title: z.string().min(1),
    session_title: z.string().nullable(),
    start: z.iso.datetime(),
    end: z.iso.datetime().nullable(),
    building: z.string().nullable(),
    room: z.string().nullable(),
    units: z.array(z.string()),
    kind: AgendaKindSchema,
    transit: ConnectionSchema.nullable(),
  })
  .meta({ title: "AgendaItem" });
export type AgendaItem = z.infer<typeof AgendaItemSchema>;

export const AgendaDaySchema = z.strictObject({
  /** Conference-local (America/Denver) date, YYYY-MM-DD. */
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  items: z.array(AgendaItemSchema),
});

export const AgendaResponseSchema = z
  .strictObject({
    presenter_id: z.int().min(1).nullable(),
    days: z.array(AgendaDaySchema),
  })
  .meta({ title: "AgendaResponse" });
export type AgendaResponse = z.infer<typeof AgendaResponseSchema>;
```

`src/schemas.ts`: add the three kinds.

```ts
import { z } from "zod";
import { AgendaResponseSchema, PicksResponseSchema, SubjectSchema } from "./api";
import { RecommendationSchema } from "./recommendation";
import { RunSchema } from "./run";
import { TalkSchema } from "./talk";

export const SCHEMAS = {
  talk: TalkSchema,
  recommendation: RecommendationSchema,
  run: RunSchema,
  subject: SubjectSchema,
  picks_response: PicksResponseSchema,
  agenda_response: AgendaResponseSchema,
} as const;
```

(`emitAll` is unchanged.) `src/index.ts`: append

```ts
export {
  EngineIdSchema, SubjectSchema, PickSchema, PicksResponseSchema, AgendaKindSchema,
  ConnectionSchema, AgendaItemSchema, AgendaDaySchema, AgendaResponseSchema,
  type Subject, type Pick, type PicksResponse, type AgendaKind, type Connection,
  type AgendaItem, type AgendaResponse,
} from "./api";
```

- [x] **Step 4: Emit, run tests, lint, types**

Run: `npm run emit --workspace=@repo/contracts` → prints `emitted talk, recommendation, run, subject, picks_response, agenda_response` (update the `console.log` in `scripts/emit.ts` to print `Object.keys(emitAll()).join(", ")` instead of the hardcoded list). Open `schema/subject.schema.json` and confirm it is an `anyOf` of two objects with `additionalProperties: false`. Open `schema/picks_response.schema.json` and confirm the recommendation item has 14 required keys (13 + `candidate`).

Run: `npm run test --workspace=@repo/contracts && npm run check-types --workspace=@repo/contracts && npm run lint --workspace=@repo/contracts`
Expected: all green; test count rises from 12 to 12 + 3 (api) + 3 (valid fixtures) + 3 (drift) = 21.

Run: `cd pipeline && uv run pytest -q tests/core/test_contracts.py` → still 7 passed (Python `KINDS` is unchanged and ignores the new files).

- [x] **Step 5: Commit**

```bash
git add packages/contracts
git commit -m "feat(contracts): Subject, PicksResponse and AgendaResponse schemas; emitted JSON Schema and fixtures"
```

---

### Task 2: The API serves contract rows and validates every output

**Files:**
- Create: `packages/api/src/wire.ts`, `packages/api/test/wire.test.ts`
- Modify: `packages/api/src/router.ts`, `packages/api/src/index.ts`, `packages/api/test/router.test.ts`

- [ ] **Step 1: Failing wire tests**

`packages/api/test/wire.test.ts`:

```ts
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { describe, expect, test } from "vitest";

import { PickSchema, RecommendationSchema, TalkSchema } from "@repo/contracts";

import { toRecommendationInsert, toTalkInsert } from "../src/db/transform";
import type { RecRow, TalkRow } from "../src/repo";
import { toPick, toRecommendation, toTalk } from "../src/wire";

const req = createRequire(import.meta.url);
const fixture = (kind: string) =>
  JSON.parse(readFileSync(req.resolve(`@repo/contracts/fixtures/valid/${kind}.json`), "utf8"));

// toTalkInsert / toRecommendationInsert set every column, so the insert shape is a full row.
const talkRow = () => toTalkInsert(TalkSchema.parse(fixture("talk"))) as TalkRow;
const recRow = () => toRecommendationInsert(RecommendationSchema.parse(fixture("recommendation"))) as RecRow;

describe("wire: Drizzle row -> contract row", () => {
  test("toTalk round-trips the talk fixture exactly", () => {
    expect(toTalk(talkRow())).toEqual(fixture("talk"));
  });
  test("toTalk emits ISO timestamps and nulls, and validates", () => {
    const t = toTalk({ ...talkRow(), start: null, end: new Date("2026-03-19T15:24:00Z") });
    expect(t.start).toBeNull();
    expect(t.end).toBe("2026-03-19T15:24:00.000Z");
    expect(TalkSchema.safeParse(t).success).toBe(true);
  });
  test("toRecommendation round-trips the recommendation fixture exactly", () => {
    expect(toRecommendation(recRow())).toEqual(fixture("recommendation"));
  });
  test("toPick joins the candidate and validates against PickSchema", () => {
    const pick = toPick({ ...recRow(), candidate: talkRow() });
    expect(pick.candidate.id).toBe(2802);
    expect(PickSchema.safeParse(pick).success).toBe(true);
    expect(Object.keys(pick)).toHaveLength(14);
  });
});
```

Run: `npm run test --workspace=@repo/api -- test/wire.test.ts` → FAIL, cannot find `../src/wire`.

- [ ] **Step 2: Implement `src/wire.ts`**

```ts
import type { Pick, Recommendation, Talk } from "@repo/contracts";

import type { MatchRow, RecRow, TalkRow } from "./repo";

const iso = (d: Date | null) => (d === null ? null : d.toISOString());

/** The inverse of transform.toTalkInsert: Drizzle property names -> contract field names, Date -> ISO. */
export function toTalk(r: TalkRow): Talk {
  return {
    id: r.id, external_id: r.externalId, title: r.title, abstract: r.abstract,
    units: r.units, topics: r.topics, type: r.type, is_invited: r.isInvited,
    is_withdrawn: r.isWithdrawn, start: iso(r.start), end: iso(r.end),
    sort_order: r.sortOrder, presentation_location: r.presentationLocation,
    author_ids: r.authorIds, presenter_ids: r.presenterIds,
    publication_reference: r.publicationReference,
    funding_acknowledgement: r.fundingAcknowledgement,
    team_acknowledgement: r.teamAcknowledgement, session_id: r.sessionId,
    session_title: r.sessionTitle, session_code: r.sessionCode,
    session_type: r.sessionType, session_topics: r.sessionTopics,
    building: r.building, room: r.room,
  };
}

export function toRecommendation(r: RecRow): Recommendation {
  return {
    for_talk_id: r.forTalkId, candidate_id: r.candidateId, score: r.score, rank: r.rank,
    match: r.match, cross_domain: r.crossDomain, why: r.why,
    strongest_parallel: r.strongestParallel, shared_methods: r.sharedMethods,
    evidence: r.evidence, engine_id: r.engineId, run_id: r.runId,
    contract_version: r.contractVersion as Recommendation["contract_version"],
  };
}

export function toPick(m: MatchRow): Pick {
  return { ...toRecommendation(m), candidate: toTalk(m.candidate) };
}
```

If `contract_version` needs the cast because the row type is `number` and the contract is the literal `1`, keep the cast and add a one-line comment; the `.output()` validator in Step 4 rejects any other value at runtime.

Run: `npm run test --workspace=@repo/api -- test/wire.test.ts` → 4 pass.

- [ ] **Step 3: Failing router tests**

Rewrite the expectations in `packages/api/test/router.test.ts` to the contract shape. The fixtures, factories and the HTTP/createContext tests stay; change only inputs and asserted keys:

- Every `{ talkId: N }` input becomes `{ talk_id: N }`; every `{ presenterId: N }` becomes `{ presenter_id: N }`; `engineId:` in inputs becomes `engine_id:`.
- Picks assertions: `r.presenterId` → `r.presenter_id`; `x.candidateId` → `x.candidate_id`; `x.forTalkId` → `x.for_talk_id`; `x.candidate.title` unchanged.
- Agenda assertions: `i.kind` unchanged; the transit assertion unchanged; add to the first agenda test: `expect(r.days[0]?.items[0]?.start).toBe("2026-03-19T14:00:00.000Z")` and `expect(r.days[0]?.items[1]?.session_title).toBeNull()`.
- The "rejects an input naming both" test sends `{ presenter_id: 7, talk_id: 0 }`; the engine rule test sends `{ talk_id: 0, engine_id: "DROP TABLE" }`.
- Add one test at the end of `describe("presenter.picks")`:

```ts
  test("responses validate against the contract response schemas", async () => {
    const { PicksResponseSchema, AgendaResponseSchema } = await import("@repo/contracts");
    expect(PicksResponseSchema.safeParse(await call().presenter.picks({ talk_id: 0 })).success).toBe(true);
    expect(AgendaResponseSchema.safeParse(await call().presenter.agenda({ presenter_id: 7 })).success).toBe(true);
  });
```

- Add one test proving output validation is live, in a new `describe("output validation")`:

```ts
describe("output validation", () => {
  test("a repo returning a malformed row is an INTERNAL_SERVER_ERROR, not a leaked row", async () => {
    const broken: Repo = { ...repo, getTalk: async () => ({ ...anchor, title: "" }) };
    const caller = createCallerFactory(appRouter)({ repo: broken, engineId: "graph_v1" });
    await expect(caller.talk.get({ id: 0 })).rejects.toMatchObject({ code: "INTERNAL_SERVER_ERROR" });
  });
});
```

Run: `npm run test --workspace=@repo/api -- test/router.test.ts` → FAIL (inputs rejected by the old camelCase Subject; keys missing).

- [ ] **Step 4: Rewrite `src/router.ts`**

```ts
import { TRPCError } from "@trpc/server";
import {
  AgendaResponseSchema, PicksResponseSchema, SubjectSchema, TalkSchema,
  type AgendaItem, type AgendaKind, type Subject,
} from "@repo/contracts";
import { z } from "zod";

import { groupByDenverDay } from "./agenda";
import type { MatchRow, Repo, TalkRow } from "./repo";
import { publicProcedure, router } from "./trpc";
import { toPick, toTalk } from "./wire";

async function resolveAnchors(repo: Repo, input: Subject): Promise<{ presenterId: number | null; anchors: TalkRow[] }> {
  if ("presenter_id" in input) {
    const anchors = await repo.anchorsFor(input.presenter_id);
    if (anchors.length === 0) {
      throw new TRPCError({ code: "NOT_FOUND", message: `presenter ${input.presenter_id} not found` });
    }
    return { presenterId: input.presenter_id, anchors };
  }
  const talk = await repo.getTalk(input.talk_id);
  if (talk === null) throw new TRPCError({ code: "NOT_FOUND", message: `talk ${input.talk_id} not found` });
  return { presenterId: null, anchors: [talk] };
}

/** In-process agenda entry: Date fields so groupByDenverDay can sort and compute transit. */
function agendaEntry(t: TalkRow, kind: AgendaKind) {
  return {
    id: t.id, title: t.title, sessionTitle: t.sessionTitle, start: t.start, end: t.end,
    building: t.building, room: t.room, units: t.units, kind,
  };
}

export const appRouter = router({
  talk: router({
    get: publicProcedure
      .input(z.object({ id: z.int().min(0) }))
      .output(TalkSchema)
      .query(async ({ ctx, input }) => {
        const talk = await ctx.repo.getTalk(input.id);
        if (talk === null) throw new TRPCError({ code: "NOT_FOUND", message: `talk ${input.id} not found` });
        return toTalk(talk);
      }),
  }),
  presenter: router({
    picks: publicProcedure
      .input(SubjectSchema)
      .output(PicksResponseSchema)
      .query(async ({ ctx, input }) => {
        const { presenterId, anchors } = await resolveAnchors(ctx.repo, input);
        const matches: MatchRow[] = await ctx.repo.getMatches(
          anchors.map((a) => a.id),
          input.engine_id ?? ctx.engineId,
        );
        return { presenter_id: presenterId, anchors: anchors.map(toTalk), recommendations: matches.map(toPick) };
      }),
    agenda: publicProcedure
      .input(SubjectSchema)
      .output(AgendaResponseSchema)
      .query(async ({ ctx, input }) => {
        const { presenterId, anchors } = await resolveAnchors(ctx.repo, input);
        const matches = await ctx.repo.getMatches(anchors.map((a) => a.id), input.engine_id ?? ctx.engineId);
        // A candidate matched under several anchors takes its kind from its
        // best-scoring match (first in getMatches order on ties), agreeing with the
        // merged picks rail; a presenter's own talk is always "mine".
        const best = new Map<number, MatchRow>();
        for (const m of matches) {
          const prev = best.get(m.candidateId);
          if (prev === undefined || m.score > prev.score) best.set(m.candidateId, m);
        }
        const entries = new Map<number, ReturnType<typeof agendaEntry>>();
        for (const m of best.values()) entries.set(m.candidateId, agendaEntry(m.candidate, m.crossDomain ? "surprise" : "core"));
        for (const a of anchors) entries.set(a.id, agendaEntry(a, "mine"));
        const mineFirst = (a: { kind: AgendaKind }, b: { kind: AgendaKind }) =>
          Number(b.kind === "mine") - Number(a.kind === "mine");
        const days = groupByDenverDay([...entries.values()], mineFirst).map((d) => ({
          date: d.date,
          items: d.items.map((i): AgendaItem => ({
            id: i.id, title: i.title, session_title: i.sessionTitle,
            start: i.start.toISOString(), end: i.end === null ? null : i.end.toISOString(),
            building: i.building, room: i.room, units: i.units, kind: i.kind, transit: i.transit,
          })),
        }));
        return { presenter_id: presenterId, days };
      }),
  }),
});

export type AppRouter = typeof appRouter;
```

Remove the local `EngineId`, `Subject` and `AgendaKind` definitions (they now come from the contract). `src/index.ts`: add `export { toTalk, toRecommendation, toPick } from "./wire";` and drop the `AgendaKind` export if it was re-exported from the router (the contract exports it).

- [ ] **Step 5: Green**

Run: `npm run test --workspace=@repo/api && npm run check-types --workspace=@repo/api && npm run lint --workspace=@repo/api`
Expected: all green. `apps/web` is red until Task 3 (expected).

- [ ] **Step 6: Commit**

```bash
git add packages/api/src packages/api/test
git commit -m "feat(api): procedures take the contract Subject and serve validated contract rows"
```

---

### Task 3: The web app reads contract rows

**Files:**
- Modify: `apps/web/package.json` (add `"@repo/contracts": "*"` to dependencies), `apps/web/lib/conference.ts`, `apps/web/app/page.tsx`, `apps/web/app/calendar/page.tsx`, `apps/web/test/lib/subject.test.ts`, `apps/web/e2e/kindred.e2e.ts`

- [ ] **Step 1: Failing subject tests**

In `apps/web/test/lib/subject.test.ts` replace every expected `{ talkId: N }` with `{ talk_id: N }` and every `{ presenterId: N }` with `{ presenter_id: N }`. Add one test:

```ts
  test("returns a contract Subject with exactly one key", () => {
    expect(Object.keys(subjectFromEnv({}))).toEqual(["talk_id"]);
    expect(Object.keys(subjectFromEnv({ presenterId: "5" }))).toEqual(["presenter_id"]);
  });
```

Run: `npm run test --workspace=web -- test/lib/subject.test.ts` → FAIL on key names.

- [ ] **Step 2: Implement**

`apps/web/lib/conference.ts`: replace the local `Subject` type with the contract's, and the two return shapes.

```ts
import type { Subject } from "@repo/contracts";
export type { Subject };

// The claimed anchor talk (the porphyrin-nanorod photoconductivity paper),
// seeded as talk id 0. Used when no subject is configured.
const DEFAULT_SUBJECT: Subject = { talk_id: 0 };
```

…and in `subjectFromEnv`: `return { presenter_id: presenterId };` and `return talkId !== null ? { talk_id: talkId } : DEFAULT_SUBJECT;`. Nothing else in the function changes; the env variable names stay `NEXT_PUBLIC_PRESENTER_ID` / `NEXT_PUBLIC_ANCHOR_TALK_ID` and the parameter object keeps `presenterId` / `anchorTalkId` (those are the builder's own inputs, not wire fields).

Run `npm install` after editing `apps/web/package.json` so the workspace link exists.

`apps/web/app/page.tsx`: the rail mapping reads contract fields.

```ts
  const { anchors, recommendations } = picks.data;
  const rail: Pick[] = recommendations.map((rec) => ({
    candidateId: rec.candidate_id,
    forTalkId: rec.for_talk_id,
    title: rec.candidate.title,
    sessionTitle: rec.candidate.session_title,
    units: rec.candidate.units,
    start: rec.candidate.start,
    score: rec.score,
    crossDomain: rec.cross_domain,
    why: rec.why,
    sharedMethods: rec.shared_methods,
  }));
```

(`Pick` in `components/pick-card.tsx` is the UI's own view model and stays camelCase; the mapping is the seam.)

`apps/web/app/calendar/page.tsx`: map contract agenda items to the component's `AgendaEntry`.

```ts
  const byDate = new Map(
    agenda.data.days.map((day) => [
      day.date,
      day.items.map(
        (item): AgendaEntry => ({
          id: item.id, title: item.title, sessionTitle: item.session_title,
          start: item.start, end: item.end, room: item.room,
          transit: item.transit, kind: item.kind, units: item.units,
        }),
      ),
    ]),
  );
```

`apps/web/e2e/kindred.e2e.ts`: both `JSON.stringify({ talkId: 0 })` become `JSON.stringify({ talk_id: 0 })`; the picks cast becomes `{ candidate_id: number }[]` and `.map((r) => r.candidate_id)`.

- [ ] **Step 3: Green, and the build**

Run: `npm run test --workspace=web && npm run check-types && npm run lint && env -u DATABASE_URL npm run build --workspace=web`
Expected: web 62 tests pass (count unchanged plus the one new subject test = 63); root check-types and lint 5/5; build compiles, `/` and `/calendar` static.

Run: `grep -rn "talkId\|presenterId\|candidateId\|crossDomain\|sharedMethods" apps/web/app apps/web/e2e` → only `presenterId`/`anchorTalkId` as `subjectFromEnv` parameter names in `lib/conference.ts`; nothing in `app/` or `e2e/` (the `Pick` view model keys live in `components/`, which is fine).

- [ ] **Step 4: Commit**

```bash
git add apps/web package-lock.json
git commit -m "feat(web): pages read the contract picks and agenda responses; Subject is the contract type"
```

---

### Task 4: Turborepo boundaries and the app-side import rule

**Files:**
- Create: `apps/web/turbo.json`, `apps/docs/turbo.json`, `packages/api/turbo.json`, `packages/contracts/turbo.json`, `packages/ui/turbo.json`, `packages/eslint-config/turbo.json`, `packages/typescript-config/turbo.json`
- Modify: `turbo.json` (root), `package.json` (root), `apps/web/eslint.config.js`

- [ ] **Step 1: The "failing test": a deliberate violation**

Add to the top of `apps/web/lib/trpc.ts`: `import "drizzle-orm";` and to `apps/web/app/page.tsx`: `import { dbRepo } from "@repo/api";` (unused). Run `npx turbo boundaries`. Expected: a dependency violation for `drizzle-orm` (not declared in `apps/web/package.json`). Run `npm run lint --workspace=web`. Expected: only an unused-import warning at most; nothing forbids the driver by name yet. Note both outputs, then keep the violations in place for Step 3.

- [ ] **Step 2: Tags and rules**

Each per-package `turbo.json` (same content, different tag):

```json
{ "$schema": "https://turborepo.dev/schema.json", "extends": ["//"], "tags": ["app"] }
```

Tags: `apps/web` and `apps/docs` → `"app"`; `packages/api` → `"data"`; `packages/contracts` → `"contract"`; `packages/ui` → `"ui"`; `packages/eslint-config` and `packages/typescript-config` → `"tooling"`.

Root `turbo.json`: add after `globalEnv`:

```json
  "boundaries": {
    "tags": {
      "contract": { "dependencies": { "allow": ["tooling"] } },
      "ui":       { "dependencies": { "allow": ["tooling"] } },
      "data":     { "dependencies": { "allow": ["contract", "tooling"] },
                    "dependents":   { "allow": ["app"] } },
      "app":      { "dependencies": { "allow": ["data", "ui", "contract", "tooling"] } }
    }
  }
```

Meaning: the contract depends on nothing internal; UI primitives depend on nothing internal; the data/API package may use only the contract, and only apps may mount it; apps may use the data package, UI, contract and tooling, never each other. Root `package.json` scripts: add `"boundaries": "turbo boundaries"`.

`apps/web/eslint.config.js`:

```js
import { nextJsConfig } from "@repo/eslint-config/next-js";

/** @type {import("eslint").Linter.Config[]} */
export default [
  ...nextJsConfig,
  {
    rules: {
      // The app meets the data layer only through @repo/api's public surface.
      "no-restricted-imports": [
        "error",
        {
          paths: [
            { name: "drizzle-orm", message: "Database access lives in @repo/api." },
            { name: "postgres", message: "Database access lives in @repo/api." },
          ],
          patterns: [
            { group: ["drizzle-orm/*"], message: "Database access lives in @repo/api." },
            { group: ["@repo/api/*"], message: "Import from the @repo/api barrel only." },
          ],
        },
      ],
    },
  },
];
```

- [ ] **Step 3: Verify the violations are caught, then revert them**

Run: `npm run boundaries` → FAIL, reporting the `drizzle-orm` dependency violation in `apps/web/lib/trpc.ts`. Run: `npm run lint --workspace=web` → FAIL on `no-restricted-imports` for `drizzle-orm`. Now also prove a tag rule bites, on the rule that protects the data package: temporarily add `"@repo/api": "*"` to `packages/ui/package.json` dependencies (do not run `npm install`), run `npm run boundaries`, expected: a rule violation because `ui` may only depend on `tooling`. Revert `packages/ui/package.json` and the two temporary imports. Run `npm run boundaries` → passes; `npm run lint` (root) → 5/5.

If `turbo boundaries` reports devDependencies on `@repo/eslint-config`/`@repo/typescript-config` as violations even with `tooling` allowed, that is why `tooling` is in every allow list; if it instead ignores devDependencies, leave the allow lists as written (harmless). If it complains about `apps/docs` importing something not covered, add the missing tag rather than loosening `app`. Report which case applied.

- [ ] **Step 4: Commit**

```bash
git add turbo.json package.json apps/web/turbo.json apps/docs/turbo.json packages/*/turbo.json apps/web/eslint.config.js
git commit -m "build: Turborepo boundaries tags and rules; apps cannot import database drivers"
```

---

### Task 5: Python layering with import-linter

**Files:**
- Create: `pipeline/.importlinter`
- Modify: `pipeline/pyproject.toml`, `pipeline/README.md`

- [ ] **Step 1: The "failing test": a deliberate violation**

Add `from gps_core.store import write_seed  # noqa: F401` near the top of `pipeline/src/gps_engines/graph_v1/engine.py` (check the actual exported name in `gps_core/store.py`; any symbol works). Keep it for Step 3.

- [ ] **Step 2: Configure**

`cd pipeline && uv add --group dev import-linter` (adds to the `dev` group in `pyproject.toml` and the lockfile).

`pipeline/.importlinter`:

```ini
[importlinter]
root_packages =
    gps_engines
    gps_core
    gps_data

; Engines sit on core, core sits on the data layer. Lower layers never import higher ones.
; The registry reaches engines by importlib string, not by import, so core stays below engines.
[importlinter:contract:layers]
name = engines > core > data
type = layers
layers =
    gps_engines
    gps_core
    gps_data

; An engine returns rows; only core's run driver validates and writes them.
[importlinter:contract:no-store-from-engines]
name = engines never write the store or drive runs
type = forbidden
source_modules =
    gps_engines
forbidden_modules =
    gps_core.store
    gps_core.run
```

`pipeline/README.md`, in the Run block after the pytest line:

```
    uv run lint-imports                                         # layering: engines > core > data; engines never import store/run
```

- [ ] **Step 3: Verify, revert, verify**

Run: `cd pipeline && uv run lint-imports` → FAIL: "engines never write the store or drive runs" broken by `gps_engines.graph_v1.engine -> gps_core.store`. Remove the temporary import. Run again → both contracts KEPT. Run `uv run pytest -q` → 145 passed.

If the layers contract reports a real import of `gps_core` from `gps_data`, or of `gps_engines` from `gps_core`, stop and report it: that is an existing layering bug, and the fix (moving the symbol) needs a decision, not a loosened rule.

- [ ] **Step 4: Commit**

```bash
git add pipeline/.importlinter pipeline/pyproject.toml pipeline/uv.lock pipeline/README.md
git commit -m "build(pipeline): import-linter enforces engines > core > data; engines never touch the store"
```

---

### Task 6: CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: any `pipeline/tests/**` file that needs the local `data/` archive (skip cleanly when absent)

- [ ] **Step 1: Find tests that need the gitignored archive**

`data/` is local-only. Simulate a CI checkout: `git worktree add /tmp/ci-sim HEAD && cd /tmp/ci-sim/pipeline && uv sync && uv run pytest -q; cd - && git worktree remove /tmp/ci-sim`. Expected: some tests under `tests/data/` fail or error on a missing `data/gps2026` path. List them.

- [ ] **Step 2: Skip them without the archive (the failing-first is Step 1's red run)**

In `pipeline/tests/data/conftest.py` add a module-level guard and apply it to the archive-reading fixtures:

```python
import pytest
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parents[3] / "data" / "gps2026"  # tests/data -> tests -> pipeline -> repo root
requires_archive = pytest.mark.skipif(not ARCHIVE.exists(), reason="local data/ archive not present (CI)")
```

Decorate each test module or function that reads the archive with `@requires_archive` (import it from `conftest` via `from .conftest import requires_archive` or, cleaner, apply `pytestmark = requires_archive` at the top of each affected module). Re-run the worktree simulation: expected `N passed, M skipped`, zero failures. Run the normal `uv run pytest -q` locally: still 145 passed, 0 skipped.

- [ ] **Step 3: Workflow**

`.github/workflows/ci.yml`:

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

env:
  TURBO_TELEMETRY_DISABLED: "1"
  DO_NOT_TRACK: "1"

jobs:
  web:
    name: web
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 24
          cache: npm
      - run: npm ci
      - name: Boundaries (package graph)
        run: npm run boundaries
      - name: Lint
        run: npm run lint
      - name: Types
        run: npm run check-types
      - name: Tests
        run: npm run test
      - name: Contract schema drift
        run: |
          npm run emit --workspace=@repo/contracts
          git diff --exit-code -- packages/contracts/schema
      - name: Build web (no database needed)
        run: npm run build --workspace=web

  pipeline:
    name: pipeline
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: pipeline
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
          cache-dependency-glob: pipeline/uv.lock
      - run: uv python install 3.12
      - run: uv sync --locked
      - name: Layering
        run: uv run lint-imports
      - name: Tests (offline; archive-dependent tests skip)
        run: uv run pytest -q
```

Notes for the implementer: the pipeline job installs `sentence-transformers` and its torch dependency, so the first run takes several minutes; the uv cache makes later runs fast. `NEXT_PUBLIC_*` are unset in CI, so the build resolves the default subject.

- [ ] **Step 3b: Frozen e2e seed and a `SEED_PATH` override**

The seed script reads `pipeline/out/app_seed.v2.json`, which is run output and gitignored. CI needs a committed copy. Copy the current export (58 talks, 118 locations, 1 run, 19 recommendations; public programme data, 195 KB) to `apps/web/e2e/fixtures/app_seed.v2.json`:

```bash
cp pipeline/out/app_seed.v2.json apps/web/e2e/fixtures/app_seed.v2.json
```

Failing test first: `packages/api/test/seed-path.test.ts`

```ts
import { describe, expect, test } from "vitest";
import { resolveSeedPath } from "../src/db/seed-path";

describe("resolveSeedPath", () => {
  test("uses SEED_PATH when set", () => {
    expect(resolveSeedPath({ SEED_PATH: "/tmp/x.json" }, "/default.json")).toBe("/tmp/x.json");
  });
  test("falls back to the default when unset or blank", () => {
    expect(resolveSeedPath({}, "/default.json")).toBe("/default.json");
    expect(resolveSeedPath({ SEED_PATH: "  " }, "/default.json")).toBe("/default.json");
  });
});
```

Run: `npm run test --workspace=@repo/api -- test/seed-path.test.ts` → FAIL (module missing). Then `packages/api/src/db/seed-path.ts`:

```ts
/** The seed file to load: SEED_PATH when set and non-blank, else the pipeline's default export. */
export function resolveSeedPath(env: { SEED_PATH?: string }, defaultPath: string): string {
  const value = env.SEED_PATH?.trim() ?? "";
  return value === "" ? defaultPath : value;
}
```

In `seed.ts`, replace the `SEED_PATH` constant's use with `const SEED_PATH = resolveSeedPath(process.env, DEFAULT_SEED_PATH);` where `DEFAULT_SEED_PATH` is the existing four-levels-up join. Add `SEED_PATH` to `turbo.json` `globalEnv`. Run the test → green.

- [ ] **Step 3c: Playwright starts the built app itself when no base URL is given**

`apps/web/playwright.config.ts`:

```ts
import { defineConfig } from "@playwright/test";

// E2E targets:
//   PLAYWRIGHT_BASE_URL=https://<deployment> npm run e2e --workspace=web   (a deployed instance)
//   npm run e2e --workspace=web   (starts `next start` on :3000 against DATABASE_URL; CI and local Docker)
const baseURL = process.env.PLAYWRIGHT_BASE_URL;
export default defineConfig({
  testDir: "./e2e",
  testMatch: "**/*.e2e.ts",
  use: { baseURL: baseURL ?? "http://localhost:3000", trace: "retain-on-failure" },
  reporter: [["list"]],
  webServer: baseURL
    ? undefined
    : {
        command: "npm run start -- --port 3000",
        url: "http://localhost:3000",
        reuseExistingServer: !process.env.CI,
        timeout: 60_000,
      },
});
```

- [ ] **Step 3d: The e2e CI job** (append to `.github/workflows/ci.yml` under `jobs:`)

```yaml
  e2e:
    name: e2e
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: kindred
          POSTGRES_PASSWORD: kindred
          POSTGRES_DB: kindred
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U kindred"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      DATABASE_URL: postgres://kindred:kindred@localhost:5432/kindred
      ENGINE_ID: graph_v1
      SEED_PATH: ${{ github.workspace }}/apps/web/e2e/fixtures/app_seed.v2.json
      CI: "1"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 24
          cache: npm
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - name: Migrate and seed the throwaway database
        run: |
          npm run db:migrate --workspace=@repo/api
          npm run db:seed --workspace=@repo/api
      - name: Build
        run: npm run build --workspace=web
      - name: End-to-end
        run: npm run e2e --workspace=web
      - if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-traces
          path: apps/web/test-results/
```

The database is a container GitHub starts for this job and destroys afterwards; the connection string is a fixed localhost address, so no secret exists. Supabase is never touched by CI. The seed step is also the only place the migration and seed scripts run from an empty database, so a broken migration fails here.

- [ ] **Step 3e: Local equivalent** (documented; Docker is not installed on Rupert's machine, so this is verified in CI only)

Root `compose.yaml`:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: kindred
      POSTGRES_PASSWORD: kindred
      POSTGRES_DB: kindred
    ports: ["5432:5432"]
```

Append to `apps/web/.env.example` a commented block:

```
# Local e2e against a throwaway Postgres (needs Docker):
#   docker compose up -d postgres
#   DATABASE_URL=postgres://kindred:kindred@localhost:5432/kindred SEED_PATH=$PWD/apps/web/e2e/fixtures/app_seed.v2.json \
#     npm run db:migrate --workspace=@repo/api && npm run db:seed --workspace=@repo/api
#   DATABASE_URL=postgres://kindred:kindred@localhost:5432/kindred npm run build --workspace=web && npm run e2e --workspace=web
```

- [ ] **Step 4: Run it**

Commit and push the branch (`git push origin feat/stage0-engine`), then `gh run watch --exit-status` (or `gh run list --branch feat/stage0-engine` and `gh run view <id> --log-failed`). Expected: all three jobs (`web`, `pipeline`, `e2e`) green. If `web` fails on Node 24 where local Node 22 passed, fix the incompatibility rather than lowering the version: `engines` already declares `>=24`. Record the local/CI Node mismatch in this plan's execution notes.

- [ ] **Step 5: Commit** (if Step 4 needed fixes, amend nothing; add a follow-up commit)

```bash
git add .github/workflows/ci.yml pipeline/tests apps/web/e2e/fixtures apps/web/playwright.config.ts apps/web/.env.example packages/api/src/db packages/api/test/seed-path.test.ts turbo.json compose.yaml
git commit -m "ci: boundaries, lint, types, tests, schema drift, web build, pipeline layering; e2e against a throwaway Postgres"
```

---

### Task 7: GATED — CODEOWNERS and branch protection on `main`

**Requires Rupert's explicit go. Changes GitHub repository settings.**

The repo has three human collaborators with push access: Rupertlim88 (admin), ryudayo and ryut-glitch. Rupert's decision (2026-09-13): every merge into `main` needs one approving review from a human, and any of the three may give it; AI sessions author commits under Rupert's account but never approve. Listing all three as code owners means a contract change can be approved by whichever owner did not write it.

**Files:**
- Create: `.github/CODEOWNERS`

- [ ] **Step 1: CODEOWNERS** (commit this part without the gate; it is inert until protection is on)

```
# Any one of the three humans below may approve a pull request. Contract and spec
# changes are listed explicitly so GitHub requests owner review on them by name.
*                                   @Rupertlim88 @ryudayo @ryut-glitch
/packages/contracts/                @Rupertlim88 @ryudayo @ryut-glitch
/docs/superpowers/specs/            @Rupertlim88 @ryudayo @ryut-glitch
```

```bash
git add .github/CODEOWNERS
git commit -m "chore: CODEOWNERS — the three collaborators own the contract and specs"
git push origin feat/stage0-engine
```

- [ ] **Step 2: Ask.** "Task 7 step 3 turns on branch protection for `main`: required status checks `web`, `pipeline` and `e2e`, one approving review from a code owner (any of the three collaborators, never the author), stale approvals dismissed on new pushes, force-pushes and deletion blocked, and the rules apply to admins too. Proceed?"

- [ ] **Step 3: Protect `main`** (after the go)

```bash
gh api -X PUT repos/Rupertlim88/ConferenceApp/branches/main/protection \
  --input - <<'JSON'
{
  "required_status_checks": { "strict": true, "contexts": ["web", "pipeline", "e2e"] },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "require_code_owner_reviews": true,
    "dismiss_stale_reviews": true,
    "require_last_push_approval": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true
}
JSON
gh api repos/Rupertlim88/ConferenceApp/branches/main/protection --jq '{checks: .required_status_checks.contexts, approvals: .required_pull_request_reviews.required_approving_review_count, owners: .required_pull_request_reviews.require_code_owner_reviews, admins: .enforce_admins.enabled, force: .allow_force_pushes.enabled}'
```

Expected: `{"checks":["web","pipeline","e2e"],"approvals":1,"owners":true,"admins":true,"force":false}`. `require_last_push_approval` means the person who pushed the latest commit cannot be the one whose approval counts, so an AI session pushing under Rupert's account still needs another human's approval.

- [ ] **Step 4: Prove it** (read-only check): open a throwaway pull request from a branch with a one-line README change, confirm GitHub shows "Review required" and "Code owner review required" and that the author's own approve button is absent, then close the PR without merging and delete the branch.

- [ ] **Step 5: Record**

Append under this task: `Protected main on <date>: checks web+pipeline+e2e required, 1 code-owner approval from any of three collaborators, admins included.` Commit that line.

---

## Self-review

- **Spec coverage.** §6 "CI runs both suites whenever packages/contracts changes": Task 6 runs both suites on every push and PR, which is a superset, plus the schema-drift check. §6 "Turborepo boundaries fails the build if an app imports from the database or engine packages": Task 4 (package graph via tags; the driver-level rule via ESLint because the database lives inside `@repo/api`); Python engines cannot reach the store: Task 5. §6 CODEOWNERS: Task 7 (all three collaborators own the contract and specs; one human approval required, never the author). §8 step 9 branch protection: Task 7. §6 "zod schemas for … the API response shapes": Tasks 1 and 2 (`.output()` makes them enforced, not just declared). Plan 2's open goal "one row shape from engine to screen": Task 2 serves `Talk`/`Recommendation` rows; Task 3 makes the UI read them.
- **Placeholders.** The picks fixture in Task 1 says "paste the contents of" the two existing fixtures rather than repeating 40 lines; that is a copy instruction, not a TBD. Task 6 Step 2 names the mechanism (`pytestmark = requires_archive`) but the affected module list comes from Step 1's red run.
- **Type consistency.** `SubjectSchema`/`Subject` (`presenter_id` | `talk_id`, optional `engine_id`) used in Tasks 1, 2, 3. `PickSchema` = Recommendation + `candidate: Talk` (Task 1) produced by `toPick` (Task 2), read as `rec.candidate_id`/`rec.candidate.title` (Task 3). `AgendaItem` fields `session_title`, `start` (ISO), `transit`, `kind`, `units` (Task 1) built in the router (Task 2) and mapped to the UI's `AgendaEntry` (Task 3). Tags `app`, `data`, `contract`, `ui`, `tooling` (Task 4) match the rule table. CI job names `web`, `pipeline` and `e2e` (Task 6) are the status-check contexts in Task 7. `SEED_PATH` (Task 6 step 3b) is read by `seed.ts` and set by the e2e job.
- **Contract versioning.** Only additive schemas; `contract_version` stays 1; Python `KINDS` unchanged; emitted files for the three row kinds are untouched (Task 1 Step 4 re-emits and the drift test proves it).
