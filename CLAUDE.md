# Database Project — rules for agents

- Every experiment or long-running shell must expose live progress the user can check at any time (progress lines and/or a probeable status file).
- Every experiment or long-running shell must checkpoint incrementally: if stopped at any point, all work completed up to that moment stays saved on disk and a rerun resumes rather than restarts.
- ALL code is written with the superpowers:test-driven-development skill (invoke it BEFORE writing any code): failing test first, watch it fail, minimal code to green, refactor. No production code without a failing test first — code written before its test gets deleted and rebuilt with the tests. Running the resulting tests is always allowed; running experiments/downloads still requires Rupert's go.
- Census work (conference market sizing) is governed by `docs/business/census-methodology.md` and the per-field notes in `docs/business/field-notes/`. Start by reading `docs/business/HANDOFF.md`, which says where the last session stopped.
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
