# Conference Talk Recommender — MVP Design

Date: 2026-08-26 · Status: approved in discussion, pending spec review · Owner: Rupert

## 1. Product concept

Large conferences (APS Global Physics Summit: ~14,000 attendees, ~12,000 presentations) make it impossible to know which talks are relevant to you. Keyword search finds your own field; the real value is **non-obvious connections: talks in *other* domains that use methods similar to yours**. The MVP recommends individual talks to a presenter based on their own submitted abstract, with cross-domain "surprise" picks as the signature feature.

**Success bar:** recommendation quality, judged by physicists on real GPS 2026 data — with a real (possibly disposable) web UI, not a terminal demo.

## 2. Data

- **Source:** the public, unauthenticated JSON feed behind the official GPS 2026 schedule site: `https://makoshark-data.aps.org/441/` (`meeting.json` → 1,303 `event/{id}.json` sessions → 12,233 `presentation/{id}.json` talks with full abstracts, topic tags, authors, times; `individual/{id}.json` and location records available, not yet crawled).
- **Archived:** full session + presentation crawl completed 2026-08-26 into `data/gps2026/` (gitignored) via `data/crawl_gps2026.py` (checkpointed per-file, resumable, probeable `status.json`). The feed may go dark when the 2027 cycle starts; the local archive is the system of record.
- **Granularity: talks only.** Sessions are display context (title, room, time), never a recommendation unit.

### 2.1 Stage-0 ground-truth micro-corpus (the TDD harness)

`datasets/micro-corpus.json` (committed). Anchor: Rupert's porphyrin nanorod paper (Nano Letters 2004), method axes: self-assembly · photoconductivity transients · molecular/1D charge transport · bias-training/memory.

- **10 approved positives** (2 same-domain controls + 8 cross-domain surprises spanning DBIO, DCOMP, DMP, DCMP, DLS, DSNP, FIAP/superconductivity), hand-verified by reading abstracts.
- **~50 negatives** (to be selected): ~10 same-domain-different-method + ~40 random unrelated. Expected result for every negative: **no match**.
- These are executable expectations: pipeline tests assert the engine connects anchor↔positives and stays silent on negatives, before any scale-up.

### 2.2 Stage-1 test corpus (~800–1,200 talks)

Union of: (a) all talks in 4 anchor Level-2 sorting categories — Data Science, Complex Structured Materials, Semiconductor/Insulators/Dielectrics, Soft Condensed Matter; (b) corpus-wide tag sweeps TAG_SET_ML and TAG_SET_NANO (Level-3 tags discovered from the crawled tag vocabulary via seed match + LLM adjacency pass, approved by Rupert); (c) ~100 random background talks. Trim overshoot by capping the largest category block. Full 11k+ indexing is a config change later.

## 3. Matching engine

Principle: **the LLM makes every similarity judgment; storage structures make its knowledge persistent and queryable.** No hard-coded normalization rules, no domain axis in the graph.

1. **Graph build (offline, per corpus):** schema-constrained extraction via **LlamaIndex** (`SchemaLLMPathExtractor` under `PropertyGraphIndex` machinery, Anthropic LLM) — entities = `METHOD`, relation = `USES_METHOD` only, strict schema. (Decision 2026-08-29: Rupert reversed the earlier Path-B/no-framework choice; LlamaIndex is the graph builder of record.) Output: bipartite talk→method graph in our `MethodGraph`. Identical strings collapse mechanically; nothing else does.
2. **Method-similarity pass (LLM):** over the distinct method list, pairwise on plausible pairs only (embedding-near names / shared context — never all-pairs), verdicts: **same** (merge nodes) / **related** (add `RELATED_TO` edge) / unrelated. This subsumes normalization.
3. **Storage:** graph lands in Supabase Postgres tables (`talks`, `methods`, `talk_methods`, `method_edges`) — the interface between pipeline and app.
4. **Recommendation (GraphRAG funnel + rubric):** candidate funnel = graph traversal (talks sharing/related-to the user's talk's method nodes; division metadata identifies cross-domain candidates). Then an **LLM interrogation rubric** judges each candidate pair against the user's abstract along fixed lines of inquiry (shared methods incl. differently-named equivalents; transferability; analogous phenomena), producing per-axis scores + a written justification.
5. **Output contract: thresholds, not top-k.** Up to **5 picks: 1–2 core + 2–3 unexpected** (core:unexpected weighting per Rupert: unexpected picks dominate), each slot filled only if the candidate clears a confidence bar; empty slots are honest, first-class results.

Selective grounding (the extractor may consult external sources for unfamiliar terms) is a fast-follow, not MVP; frontier-model knowledge suffices for mainstream physics vocabulary.

### Runtime envelope (estimates, not commitments)

Every LLM stage is embarrassingly parallel. Corpus indexing: minutes-to-an-hour wall clock, tens of dollars at 11k scale, trivial at Stage-1 scale; checkpointed and resumable per repo rules. Per-user path: funnel is a DB query; rubric over ~100 candidates parallelized ≈ 10–30 s, or precomputed offline for in-corpus presenters. Design invariant: **never all-pairs; always funnel, then judge.**

## 4. Product surface

Hosted on Vercel; Supabase Postgres; **no login** — onboarding is "find/claim your talk" (search the program, pick your submission); results at a shareable unguessable URL. Non-presenters: out of MVP (paste-in profile is a fast-follow).

Two pages:

1. **Recommendations page** — card layout (shadcn), top 3–5 recommended talks: title, speaker, session/time/room context, and the rubric's one-line "why" (for unexpected picks: which shared/related method, and that it crosses divisions).
2. **Calendar page** — user enters attendance dates; system fills available windows with recommended talks under constraints: no overlaps + **travel-time feasibility** between rooms (hand-built venue map with coarse transition estimates: same room ≈ 0, same building ≈ 5 min, cross-venue ≈ 15 min). Weighted interval scheduling with setup times; talks from the same session naturally cluster into stay-in-room blocks.

## 5. Architecture & stack

- **Pipeline (Python, `pipeline/`):** crawler → LlamaIndex graph extraction → method-similarity pass → Postgres. Batch, offline, checkpointed, live-progress per repo rules. (Requires a future CLAUDE.md amendment for Python tooling: uv, pytest-based TDD.)
- **App (TypeScript, existing Turborepo):** Next.js on Vercel, tRPC procedures for talk search / recommendations / calendar, Drizzle over Supabase Postgres, shadcn/Tailwind UI in `packages/ui`, next-intl available. Better Auth installed but dormant in MVP.
- Interface between the two worlds is **only** the Postgres schema.

## 6. Testing & evaluation

- **TDD throughout** (repo rule): micro-corpus expectations become the pipeline's test suite before pipeline code exists; app code test-first per superpowers:test-driven-development.
- **Stage 0:** engine must connect anchor↔10 positives (with sensible justifications), reject ~50 negatives. Empty-result correctness is explicitly tested.
- **Stage 1:** on the ~1k corpus — baseline comparison (pure embedding similarity must *fail* to surface the cross-domain positives that the graph+rubric path finds, demonstrating the engine earns its complexity); spot-check discovery quality by physicist judgment (Rupert; proxy-claiming talks in familiar areas).
- **Scheduler:** property tests — no overlaps, no infeasible transitions, monotone under added availability.

## 7. Open items (deferred, not blocking)

- Negative-set selection (~50) for the micro-corpus — mechanical, next implementation step.
- TAG_SET_ML / TAG_SET_NANO discovery + Rupert's approval (post-crawl vocabulary exists now).
- Venue/room map for travel estimates (location records crawl + hand labeling).
- CLAUDE.md Python amendment; model choice per stage (cheap model for extraction, stronger for rubric) — empirical.
