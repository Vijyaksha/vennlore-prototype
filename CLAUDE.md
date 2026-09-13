# Database Project — rules for agents

- Every experiment or long-running shell must expose live progress the user can check at any time (progress lines and/or a probeable status file).
- Every experiment or long-running shell must checkpoint incrementally: if stopped at any point, all work completed up to that moment stays saved on disk and a rerun resumes rather than restarts.
- ALL code is written with the superpowers:test-driven-development skill (invoke it BEFORE writing any code): failing test first, watch it fail, minimal code to green, refactor. No production code without a failing test first — code written before its test gets deleted and rebuilt with the tests. Running the resulting tests is always allowed; running experiments/downloads still requires Rupert's go.
- Census work (conference market sizing) is governed by `docs/business/census-methodology.md` and the per-field notes in `docs/business/field-notes/`. Start by reading `docs/business/HANDOFF.md`, which says where the last session stopped.
- Only when the model is Fable 5.1: when it will not affect the end result, surgically edit a file (targeted Edit of the changed lines) rather than rewriting the entire file.
- **The contracts are binding.** The data layer, matching engines and UIs meet only at the contracts in `packages/contracts` (Talk, Recommendation, Run — see `docs/superpowers/specs/2026-09-12-pluggable-engine-architecture-design.md`). All code must respect them: engines write rows in that shape, UIs read rows in that shape, neither imports the other. Changing how data flows means changing the contract there first, with both the TypeScript and Python contract tests green; never work around a contract locally.
- **Three swappable parts.** The system is a data layer (`packages/api` and the store), matching engines, and UIs, meeting only at the contract. Engines live one per folder under `pipeline/src/gps_engines/`, are registered by id in `pipeline/src/gps_core/registry.py`, are selected by `ENGINE` when run and `ENGINE_ID` when served, and several may coexist in the store, each tagging its rows with its id. UIs are the apps under `apps/`; the one that depends on `@repo/api` is the one serving picks. The data layer has a single implementation. Equipping a different engine is config, not code; adding one is a new folder plus a registry line; a new UI is a new app that reads the contract through `@repo/api`.
- **Open every session by stating what is loaded.** A SessionStart hook runs `scripts/loaded-parts.mjs` (also `npm run status`), which reports the active engine, UI and data layer and every registered alternative. Repeat that report to the user in the first reply, and say plainly when only one option exists. Never write current implementation names into this file; the script reads them.
- **The contract is a tool, not a law.** Do not treat the contract, its schemas, or the enforcement scaffolding as fixed facts. If you think the contract is wrong, or a field should be named, typed, stored or shaped differently, say so and propose the change: ask the user, and once they agree, change the contract first and then the code to match, through the normal checks. Never work around a known-wrong contract silently, and never keep one because it is "the contract". The contract exists to keep the code ordered, not to freeze it; expect to change it often.
- This file contains only these rules and nothing else. Never add experiment progress, project status, or notes to it.

## Required stack — agents MUST use these tools

This repo is a Turborepo monorepo (npm workspaces: `apps/web`, `apps/docs`, `packages/ui`). The tools below are the chosen stack. Do not substitute alternatives (no REST route handlers instead of tRPC, no other ORM, no other component/auth/i18n library) without Rupert's explicit approval. If a package is missing, install it with the command shown — always into the workspace, never globally (Turborepo CLI is the one global tool).

- **Turborepo** — task runner/cache. Run tasks from the repo root: `npm run build|dev|lint`, or `turbo run <task> --filter=web`. Tasks are defined in `turbo.json`.
  Install if missing: `npm install turbo --global` (CLI) — the repo itself already depends on it.

- **tRPC** (`@trpc/server`, `@trpc/client`, `@trpc/react-query`, `@tanstack/react-query`, `zod`) — ALL client–server communication. Define procedures in tRPC routers with `zod`-validated inputs; the client calls them through the typed hooks. Never hand-write REST endpoints or raw `fetch` calls to our own backend.
  Install if missing: `npm install @trpc/server @trpc/client @trpc/react-query @tanstack/react-query zod --workspace=web`

- **Drizzle ORM** (`drizzle-orm`, `postgres` driver, `drizzle-kit` dev-dep) — ALL database access. Schema is defined in TypeScript; schema changes go through `drizzle-kit` migrations, never ad-hoc SQL DDL. No raw SQL in application code unless Drizzle genuinely cannot express the query.
  Install if missing: `npm install drizzle-orm postgres --workspace=web && npm install -D drizzle-kit --workspace=web`

- **Supabase** (`@supabase/supabase-js`, `@supabase/ssr`) — the hosted Postgres database (plus storage/realtime if needed). Drizzle connects to it via the `postgres` driver and `DATABASE_URL`. Auth is NOT Supabase Auth — see Better Auth below. No Supabase project exists yet; creating one requires Rupert's go.
  Install if missing: `npm install @supabase/supabase-js @supabase/ssr --workspace=web`

- **shadcn/ui** (Base UI primitives, base-nova style) + **Tailwind v4** — ALL UI. Shared components live in `packages/ui/src/components`; import as `@repo/ui/components/<name>`, `cn` from `@repo/ui/lib/utils`. Add missing primitives with the CLI from the repo root: `npx shadcn@latest add <name> -c apps/web` (alias config routes them into `packages/ui`). Never hand-roll a primitive shadcn provides and never add another component library. Style with Tailwind theme tokens (`bg-background`, `text-muted-foreground`, …), not ad-hoc hex values. Theme tokens live in `apps/web/app/globals.css`; `packages/ui/src/styles/globals.css` carries the `@source` directive and must stay imported.

- **Better Auth** (`better-auth`) — ALL authentication (sign-up, sessions, OAuth), using its Drizzle adapter for storage. Do not use Supabase Auth or roll custom auth.
  Install if missing: `npm install better-auth --workspace=web`

- **next-intl** (`next-intl`) — ALL user-facing strings and locale-aware date/time/number formatting. No hardcoded UI strings once i18n is wired; conference times must be formatted locale/timezone-aware through it.
  Install if missing: `npm install next-intl --workspace=web`

Not yet wired (packages installed, no config/code): tRPC router + provider, Drizzle schema/config, Better Auth config, next-intl setup. Wiring any of these should follow the official current docs (check via Context7), and database-dependent steps are blocked until the Supabase project exists.
