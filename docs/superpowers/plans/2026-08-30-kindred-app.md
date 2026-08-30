# Kindred App (Stages 1–4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the two-page Kindred web app (picks card rail + day agenda with walking times) on the repo's mandated stack, runnable locally against seeded Stage-0 engine output, with Supabase/Vercel connection deferred to Stage 5 (blocked on credentials).

**Architecture:** Python pipeline exports a seed file (talks + locations + recommendations from the Stage-0 run) → Drizzle schema/migrations/seed in `apps/web` → tRPC router (search/picks/agenda + pure `walkMinutes`) → Next.js App Router UI porting the locked v6 mockup design into Tailwind v4 theme tokens + shadcn primitives. All times displayed America/Denver via next-intl.

**Tech Stack (per CLAUDE.md — no substitutions):** Turborepo npm workspaces, tRPC + zod + @tanstack/react-query, Drizzle ORM + postgres driver + drizzle-kit, shadcn/ui (Base UI, base-nova) + Tailwind v4 tokens, next-intl, vitest (new dev-dep, web workspace) for unit tests, Playwright (deferred e2e in Stage 5). TDD per superpowers:test-driven-development for every task.

**Design authority:** the locked v6 mockup (scratchpad `kindred-mockup.html`, artifact "Kindred Mockup"). Palette (dark-first): bg #0E0B10, surface #18121B, line #2C2233, ink #F2EDF3, muted #9C8FA3, faint #6B5F72, accent #E04A63 (light: #B02D44), surprise #E0A63C (light: #A56F13). Fonts: IBM Plex Sans / Mono / Serif. Light theme values as in the mockup file.

**Walking-time constants (Rupert-approved 2026-08-30):** same room 5 min; same cluster+floor 10; same building different wing/floor 15; between buildings (Convention Center ↔ Hyatt Regency) 22; offsite 60. Tight connection: slack = gap − walk < 15 min.

---

### Task 0: Merge main into feat/stage0-engine

**Files:** merge only (main has `CLAUDE.md`, app-stack wiring 49b8acc; branch has engine + docs).

- [ ] `git merge main` from repo root on `feat/stage0-engine`; resolve conflicts (expect at most `.gitignore`) preserving both sides.
- [ ] `npm install` at root; `npm run build` and `npm run check-types` green.
- [ ] Commit the merge.

### Task 1: Pipeline seed export (Stage 1)

**Files:**
- Create: `pipeline/scripts/export_app_seed.py`
- Create: `pipeline/src/gps_engine/app_export.py`
- Test: `pipeline/tests/test_app_export.py`

Build `build_seed(corpus_talks, locations, judgments, anchor) -> dict` (pure, offline, unit-tested with fixtures) producing:

```json
{
  "talks": [{"id": 2802, "title": "...", "session_title": "...", "units": ["DPOLY"],
              "start": "2026-03-19T15:12:00Z", "end": "...", "building": "Convention Center",
              "room": "Bluebird 3C", "abstract": "..."}],
  "locations": [{"id": 62045460, "building": "Convention Center", "room": "Bellco Theatre 1-2"}],
  "recommendations": [{"for_talk_id": 0, "candidate_id": 12772, "same_method": 4,
    "specificity": 3, "usage_parallel": 4, "score": 11, "match": true,
    "cross_domain": true, "why": "...", "strongest_parallel": "..."}]
}
```

- Talk rows join presentation JSON (title HTML-entity-decoded, start/end, abstract stripped of tags) + owning event (session_title, sponsor units) + location (building/room via event.location_ids[0]). Anchor = talk 0 with null times/room, abstract = the real Nano Letters abstract (from run_stage0.py).
- Include all 58 corpus talks; recommendations = every judgment in `out/stage0/judgments/` (match true and false — the app filters).
- Runner script writes `pipeline/out/app_seed.json`. TDD with small fixtures; runner itself smoke-run (offline, reads local archive only).
- [ ] failing tests → implement → green → commit.

### Task 2: Drizzle schema + migrations + seed script (Stage 2)

**Files:**
- Create: `apps/web/db/schema.ts`, `apps/web/db/index.ts` (lazy `getDb()` — no Proxy), `apps/web/drizzle.config.ts`
- Create: `apps/web/db/seed.ts` (reads `pipeline/out/app_seed.json`, upserts)
- Create: `apps/web/db/transform.ts` + Test: `apps/web/test/transform.test.ts` (vitest; pure seed-row → insert-row mapping incl. date parsing)
- Modify: `apps/web/package.json` (deps per CLAUDE.md install commands; scripts `db:generate`, `db:migrate`, `db:seed`, `test`)

Tables: `talks` (id pk, title, session_title, units text[], start/end timestamptz null, building, room, abstract), `recommendations` (for_talk_id, candidate_id, scores ints, score int, match bool, cross_domain bool, why text, strongest_parallel text, pk (for_talk_id, candidate_id)), `locations` (id pk, building, room).
- `drizzle-kit generate` produces SQL migration committed to repo. Running migrate/seed against a live DB is DEFERRED (no DATABASE_URL yet) — scripts must fail with a clear "set DATABASE_URL" message.
- [ ] vitest wired in web workspace; transform tests TDD; commit.

### Task 3: Walking engine + tRPC router (Stage 3)

**Files:**
- Create: `apps/web/lib/walk.ts` + Test: `apps/web/test/walk.test.ts`
- Create: `apps/web/server/trpc.ts`, `apps/web/server/router.ts`, `apps/web/app/api/trpc/[trpc]/route.ts`
- Create: `apps/web/server/data.ts` (repository interface over Drizzle with an in-memory fake for tests)
- Test: `apps/web/test/router.test.ts`

`walkMinutes(a: {building, room}, b): number` — constants above; cluster = leading word-group of room ("Bluebird", "Meeting Room", "Capitol", "Exhibit Hall", "Bellco", "Mile High", ...); floor = first digit of trailing number ("Bluebird 2C" → 2; "Meeting Room 708/710" → 7; rooms without digits → cluster-only). Same building+cluster+floor → 10; same building otherwise → 15; different buildings, neither Offsite → 22; any Offsite → 60; identical room → 5. TDD against real GPS room names (Bluebird 2A↔2C=10, Bluebird 3C↔Exhibit Hall D,E&F Level 2=15, Convention Center↔Hyatt Capitol 1=22, ↔Denver Museum=60).

tRPC procedures (zod inputs):
- `searchTalks({query})` → up to 20 talks by ILIKE title match.
- `picks({talkId})` → recommendations where match=true ordered score desc, joined with candidate talk rows, split {core, unexpected} (cross_domain flag), capped 2/3 in the client contract (return all matched; UI slices).
- `agenda({talkId})` → matched picks + the claimed talk itself, grouped by conference day (America/Denver), each consecutive pair annotated {walkMinutes, slackMinutes, tight} via `walkMinutes`.
Router tests use the in-memory repository fake (no DB).
- [ ] TDD; commit.

### Task 4: UI (Stage 4)

**Files:**
- Modify: `apps/web/app/globals.css` (Kindred token values into the Tailwind v4 theme, dark-first + light)
- Create: `apps/web/app/layout.tsx` update (IBM Plex via next/font/google, next-intl provider, tRPC/react-query provider `apps/web/app/providers.tsx`)
- Create: `apps/web/messages/en.json` (ALL UI strings), `apps/web/i18n.ts`
- Create: `apps/web/app/page.tsx` (claim-your-talk search), `apps/web/app/talk/[id]/page.tsx` (picks rail), `apps/web/app/talk/[id]/calendar/page.tsx` (day agenda)
- Create: components in `apps/web/components/`: `pick-card.tsx`, `pick-rail.tsx`, `day-strip.tsx`, `agenda.tsx`, `walk-segment.tsx`, `bottom-nav.tsx` (compose shadcn primitives — Card, Badge, Button, Input — restyled with tokens; never ad-hoc hex)
- Test: `apps/web/test/agenda-view.test.tsx` (vitest + @testing-library/react: walk segment renders tight state; empty-day honesty; rail renders n cards + honest empty core slot)

Port the locked v6 design faithfully: portrait card rail (scroll-snap), serif-italic why with accent rule, day agenda with left time axis + dotted walk segments (amber tight state), bottom nav pills, honest empty states. All strings through next-intl; all times formatted America/Denver. Data flows only through tRPC hooks.
- [ ] TDD components; `npm run build` + `npm run check-types` + lint green; commit.

### Deferred to Stage 5 (blocked on credentials)
Supabase provisioning + migrate + seed; Vercel link/deploy; Playwright e2e against preview; live smoke of tRPC against real DB.

## Verification per task
Spec review + code quality review (subagent) after each task; suite green; pre-commit checklist from user CLAUDE.md (tests pass, no secrets, gitignore intact, plan alignment).
