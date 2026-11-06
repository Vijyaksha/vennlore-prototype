# Engineering Phase 2 — wave 2 brief (29 rows, one agent)

You are running **Phase 2 of the conference census** on a slice of 29 engineering conferences,
including **rung 9 in its entirety**. Follow the written method exactly.

## Read these documents first, IN FULL — they govern everything

1. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md`
2. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/engineering.md` — written
   from the 30-row pilot that ran hours ago on this exact sheet. It carries the routes that worked
   (Crossref with the per-publisher discriminator, society statistics pages, static programme
   hosts, Wayback CDX enumeration, J-STAGE API), the walls each host hits and what to do about
   them, the counting rules (per-volume sums, deposit floors, range arithmetic, short-paper
   conventions) and the traps (acronym collisions, expo headcounts, series breaks). **Use them —
   most of your rows are the same societies, platforms and publishers.**

## BLIND RUN — do not read any prior research results

Every figure must come from **your own primary-source research this session**. Do **not** open,
search for, or reuse any results, queue, plan, names or status file other than your own queue —
nothing under `scratchpad/` except `scratchpad/eng/wave2/queue_1.json`, and never the workbook
`docs/business/tam-sam-som-v3.xlsx` or any `BACKUP_*.xlsx`. If you encounter such a file anyway, do
not use it and say so. An honest `UNRESOLVED` is worth far more than a copied figure.

## Scope and language

Global. **The local-language rule applies**: Japanese (年次大会/全国大会 + 講演件数/発表件数/梗概), Chinese
(大会/年会 + 论文/报告数), Korean (학술대회 + 논문 편수/발표), German (Jahrestagung + Beiträge/Vorträge), French
(congrès + communications). At least one query in the society's language before a row is `UNKNOWN`;
Method must name the language searched.

## Your job, per row

Find the number of **accepted contributed presentations (technical papers + posters)** in one
edition — invited/plenary/keynote excluded, exhibitor and sponsor sessions excluded, withdrawn
excluded. Work the ladder in order, stop at the first rung that yields, and **credit the rung that
PRODUCED the figure**.

**Rungs 3–6 cost ZERO searches and are where most real figures come from** — the pilot resolved 26
of 30 rows without a search. If you identify an artefact, **COUNT IT**.

### Start every row here (zero searches), in this order

1. **Crossref with the right discriminator** (field notes §"routes", item 1): ASME slug in the DOI
   (`omae`, `detc`, `pvp`, `fedsm` …), SAE `event.name`, SPE `event.name`, IEEE exact container from
   the year facet (double-unescape the keys; `query.container-title` does not filter), member
   registry lookup (`api.crossref.org/members?query=<society>`) for anyone whose prefix you do not
   know, ISSN lookup via `api.crossref.org/journals?query=`.
2. **The society's own statistics or programme host** (§"routes", items 2–3): IEICE/KIEE-style
   statistics pages, gakkai-web.net, J-STAGE API (`cdjournal`), KSME-style ASP proceedings sites,
   DEGA, IAF, IAEE, CIMNE archives, DSpace REST, `peer.asee.org` via Wayback.
3. **Wayback CDX enumeration** of the society's file server for programme PDFs.
4. **Programme/abstract PDFs**: count unique IDs, extract with BOTH `pdftotext -layout` and `-raw`,
   check content-type and size before counting.

Then, and only then, the search rungs (1, 2, 7, 8), cap 3 per row.

## Hard rules — these are refusals, not preferences

- **Every number needs an exact-page clickable URL.** Not a homepage, not a search-results page.
- **NEVER write a figure you only saw in a search snippet.** Open the page.
- **Invited speakers are NOT counted.** Count contributed papers + posters.
- **A stated total NEVER beats a countable artefact.** Count the artefact; note the stated figure as
  a disagreement. A deposit index that misses presentation-only slots is a FLOOR — say so
  (`confidence: floor`) and keep the stated total in the disagreement, never as the figure.
- Any rung-1/2/7/8 figure must **state whether it includes invited talks**, or say unknown.
- **Cap: 3 web searches per conference for the abstract ladder, hard.** Zero-search rungs unlimited.
- **Rung 5 (browser) is RESERVED to the orchestrator.** AWS WAF (HTTP 202 empty body), Cloudflare
  403 "Just a moment", Vue/Angular shells: first try the field notes' workarounds (sibling host,
  Wayback `id_` copy, the REST/ajax endpoint the page's own JS names); if none applies, return
  `NEEDS_RUNG_5`, name the exact page, move on. A **credential wall** (member/attendee login) is
  NOT rung 5 — find an older open edition or another artefact.
- **Absence of evidence is NEVER evidence a meeting is small.** No figure → `UNRESOLVED` with the
  exact next action named. Never `OUT` on an empty search.
- **Repository collections are not proceedings** (HAL, Zenodo, Scipedia): never count them as a
  congress.
- **Attendance is not the unit.** Find the presentation count; a trade show with 400 papers is OUT
  however large.
- **Two-meetings-a-year rows** (JSAE spring+autumn, KSAS spring+fall, KICS winter+summer, ISIJ/JIM
  spring+autumn): report the per-edition figure of the largest edition and `events_per_yr` = 2,
  never a summed annual total.
- **Umbrella / multi-conference rows**: if the meeting is the sum of separately counted
  conferences already on a sheet, return `duplicate_of` with the evidence rather than a summed
  figure.

## Then rung 9 — run it in full on every row the abstract ladder did not settle

1. **Find attendance** on the A-ladder, first rung that yields with a basis: A1 exhibitor/sponsor
   prospectus → A2 post-meeting report → A3 press release / trade press → A4 venue / convention
   bureau → A5 programme-platform artefact (**browser-only: return `A5` with a null figure**) → A6
   proxy arithmetic (flag it) → A7 prior year / sister meeting. **Cap: 2 searches per row, 3 for a
   hard one.**
2. **Tag the basis**: `DELEGATES` / `TOTAL_ONSITE` / `TOTAL_INC_VIRTUAL` / `UNSPECIFIED`. Japanese
   延べ参加人数 is cumulative daily attendance — tag it and say so.
3. **Judge the programme character**: `CONTRIBUTED` / `CURATED` / `HYBRID` / `UNKNOWN`.
4. **Judge the ratio for THIS conference** — no default ratio; `ratio` as a decimal,
   `ratio_rationale` naming what about *this* meeting puts it there. **A ratio without reasoning is
   rejected.**
5. **Record disagreement, never average.**
6. Do **not** compute the final inferred figure or decide inclusion — the orchestrator does that.

**A figure a source STATES beats any ratio**: return it as `direct_abstracts` and say whether it is
submissions or accepted.

**NON-NEGOTIABLE:** a rung-9 figure is an approximation, marked `~N INFERRED FROM ATTENDANCE, NOT
COUNTED`.

## The bar

≥1,500 counted = `VERIFIED`; 800–1,499 = `BORDERLINE`; below 800 **on positive evidence** = `OUT`;
no evidence either way = `BORDERLINE`, never `OUT`. Inferred or organiser-stated never reaches
`VERIFIED`. A counted figure below 800 is OUT even when the series used to be larger — record the
series in Method for Rupert.

## Cadence

`Events/yr` is EMPTY for every row: return it (1 annual, 0.5 biennial, 0.33 triennial, 0.25
quadrennial, 2 for spring+autumn) with `cadence_evidence`.

## Output — checkpoint after EVERY row

Queue: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/eng/wave2/queue_1.json`.
Results: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/eng/wave2/results_1.json` — a JSON
list, **rewritten in full after every single row**. Also rewrite
`/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/eng/wave2/STATUS_1.json` as
`{ "rows_done": n, "rows_total": n, "searches_used": n, "in_flight": "<conference>" }` after every row.

Per row, exactly these fields:

```
row, conference, outcome (COUNTED|UNKNOWN|NEEDS_RUNG_5|INFERRED),
abstracts_numeric (int|null), abstracts (string as you would write it in the sheet, carrying the
  NOT COUNTED label if inferred), year, rung (int, the rung that PRODUCED it), source_url,
spot_checks (list of what you re-derived), searches_used,
events_per_yr (decimal), cadence_evidence (string),
attendance_numeric, attendance_year, attendance_basis, attendance_rung, attendance_source_url,
alt_figures (list of {value, year, basis, rung}), character, character_evidence,
programme_type, programme_evidence, direct_abstracts (int|null),
ratio (decimal|null), ratio_rationale (string|null),
duplicate_of (string|null — the sheet row this meeting is the same as or is held inside, with
  the evidence; else null),
method (the exact page, the exact grep/count/query, what you excluded and why, which language you
  searched — reproducible from this text alone),
verdict (VERIFIED|BORDERLINE|OUT|UNRESOLVED|NEEDS_RUNG_5), confidence (exact|derived|dated|floor)
```

Queue rows carry the phase-1 `notes` (why listed, a size hint if a page stated one). Hints are for
ordering only, never evidence. Echo `conference` verbatim; `row` is the workbook row at queue time.

## Downloads

Download every source yourself into a fresh directory that belongs to you alone (your session
scratchpad or a new `mktemp -d`), never into the shared `/tmp`. Never open, extract or count a file
already on disk. Check each download's HTTP status, content-type and size before counting it.

## Do not

- Do **not** write to any spreadsheet or `.xlsx` file. Do **not** modify any file outside your two
  output files. Do **not** ask anyone to change a permission or config setting. If the search budget
  runs out, stop and say so.

## Finish by reporting

A compact table (row / conference / abstracts / rung / verdict), total searches used, duplicate rows
spotted, rows you were least sure of, and **every route, wall, counting rule or trap NOT already in
`field-notes/engineering.md`** — those get added to it for wave 3.
