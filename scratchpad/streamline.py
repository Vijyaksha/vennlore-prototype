"""STREAMLINE — how post-pilot census waves run faster WITHOUT lowering the evidence bar.

Rupert, 2026-09-14: "I don't want to sacrifice performance, but find ways to streamline."
Measured on the social/earth pilots: agents spent minutes reading ~50-60k tokens of documents
before row 1 (full methodology + two analogue field-notes files) and then carried that context
on every turn; one row (ASSA) crawled a ~500-page programme inline while 19 rows waited.

The five measures, none of which touches what counts as evidence:

1. READING DIET. A wave agent reads its OWN field notes (which replace route discovery) plus the
   BINDING_DIGEST below, instead of the full methodology + two analogue files. The methodology
   stays authoritative and available — the digest tells the agent to open the relevant section
   for anything unusual. Pilots for NEW fields still read in full; this diet is post-pilot only.
2. ROUTE HINTS IN THE QUEUE. The orchestrator pre-annotates queue rows with any known artefact
   (phase-1 crossref_seen.json container names, field-notes URL patterns). Hints order the work;
   the agent still opens and counts the artefact itself — hints are never evidence.
3. CRAWL BUDGET (CRAWL_RULE below). Inline counting is capped at ~40 fetched pages per row; a
   bigger artefact is checkpointed with an exact counting plan (NEEDS_BULK_COUNT) and the
   orchestrator runs the bulk count while the agent works other rows. Deferred, never dropped.
4. BATCH THE CHEAP FETCHES. Independent downloads for one row go in one command (curl multiple
   PDFs at once); never re-read documents between rows.
5. SOFT TIMEBOX. ~8 minutes of wall clock per row: past that, write the trail (rungs tried, the
   named artefact, the exact next action) and move on — the row comes back UNRESOLVED with its
   next action, which the methodology already prefers over a stalled queue. Never trade the
   timebox for a lower-quality figure: a slow COUNTED row beats a fast quoted one.

`build_wave_brief()` emits a wave brief implementing all of this; the orchestrator writes it to
the wave dir as BRIEF.md. Model choice is unchanged: census agents run on Opus (settled A/B).
"""

BINDING_DIGEST = """\
## The binding rules (digest — the methodology file is authoritative; open
`docs/business/census-methodology.md` at the relevant section for any situation this digest
does not settle, and follow the file where they differ)

- **Unit**: accepted contributed presentations (orals + posters; each paper inside a panel counts
  as one). **Invited speakers are NOT counted.** Withdrawn excluded.
- **Every number needs an exact-page clickable URL** plus its year — the page the number is ON.
- **NEVER write a figure you only saw in a search snippet.** Open the page. No figure without a
  source: mark UNKNOWN, never estimate (rung 9 is the one labelled exception).
- **A stated total NEVER beats a countable artefact** — count the artefact, record the stated
  figure as a disagreement. Any rung-1/2/7/8 figure must state whether it includes invited talks.
- **Work the ladder in order, stop at the first rung that yields, credit the rung that PRODUCED
  the figure** (never the highest reached). Rungs 3-6 cost zero searches — if you identify an
  artefact, COUNT IT. Sanity-check counts against the artefact's own stated total, or extract
  twice (`pdftotext -layout` and `-raw`) and compare.
- **Cap: 3 web searches per conference** on the abstract ladder (hard); 2-3 on rung 9. Zero-search
  rungs unlimited. Local-language rule: a row is not UNKNOWN until searched in the society's own
  language, and Method names the language.
- **Absence of evidence is NEVER evidence a meeting is small**: no figure means UNRESOLVED with
  the exact next action, never OUT. OUT needs positive evidence under the bar.
- **Bar**: >=1,500 counted = VERIFIED; 800-1,499 = BORDERLINE; below 800 on positive evidence =
  OUT; no evidence = BORDERLINE. Inferred or organiser-stated never reaches VERIFIED.
- **Rung 5 (browser) is the orchestrator's**: 403/Cloudflare/JS pages come back as NEEDS_RUNG_5
  with the exact page (try a browser user-agent with curl first).
- **Rung 9** (only after rungs 1-8): sourced attendance x a ratio judged for THIS conference with
  written reasoning; basis tag (DELEGATES/TOTAL_ONSITE/TOTAL_INC_VIRTUAL/UNSPECIFIED); programme
  character with evidence; the figure is an approximation carrying **NOT COUNTED** wherever it
  appears; the orchestrator computes the final number, not you. A figure a source states is
  `direct_abstracts`, labelled, and beats any ratio. Record disagreement, never average.
- **Cadence**: return events_per_yr with evidence (many world congresses are 0.5/0.33/0.25).
- **Checkpoint**: results and STATUS files **rewritten in full after every single row**.
- If the search budget runs out: stop and say so. Never substitute a degraded method.
"""

CRAWL_RULE = """\
**CRAWL BUDGET — defer bulk counts, never drop or guess them.** If counting an artefact would
need more than ~40 fetched pages (a 500-session programme, a paginated archive), do NOT crawl it
inline. Record outcome NEEDS_BULK_COUNT with the exact counting plan — the URL pattern, the page
range, the ID pattern to grep, the stated total if the site shows one — reproducible from your
text alone, then move to the next row. The orchestrator runs the bulk count in parallel. A capped
crawl you did run still gets its count written normally.
"""

OUTPUT_CONTRACT = """\
Per row, exactly these fields:

```
row, conference, outcome (COUNTED|UNKNOWN|NEEDS_RUNG_5|NEEDS_BULK_COUNT|INFERRED),
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
"""

REPO = '/Users/rupertlim/AI_Projects/ConferenceApp'


def build_wave_brief(field, field_notes, queue, results, status, n_rows, extra_traps=''):
    """Slim post-pilot wave brief: field notes + digest, route hints, crawl budget, timebox."""
    return f"""# {field} Phase 2 — wave brief ({n_rows} rows, one agent)

You are running **Phase 2 of the conference census** on a slice of {n_rows} {field} conferences,
including rung 9 where the abstract ladder fails. This is a post-pilot wave: the field's routes
are already mapped — your job is throughput at the same evidence standard.

## Read first (this is the whole reading list)

1. `{REPO}/{field_notes}` — the field notes from this field's pilot: every route that worked with
   its URL pattern, every wall, the counting rules and traps. **These replace route discovery —
   try the matching route from the notes before anything else.**
2. The binding-rules digest below. Do not re-read documents between rows.

{BINDING_DIGEST}

## BLIND RUN — do not read any prior research results

Every figure must come from your own primary-source research this session. Nothing under
`scratchpad/` except your queue, and never the workbook `docs/business/tam-sam-som-v3.xlsx` or any
`BACKUP_*.xlsx`. If you encounter such a file anyway, do not use it and say so. An honest
UNRESOLVED is worth far more than a copied figure.

## Pace — streamlined, not diluted

- Queue rows may carry `route_hint` (a known artefact or container for this meeting). Hints order
  the work and are NEVER evidence — open and count the artefact yourself.
- Batch a row's independent downloads into one command.
- {CRAWL_RULE}
- **Soft timebox ~8 minutes of wall clock per row**: past it, write the trail (rungs tried, the
  named artefact, the exact next action) and move on — UNRESOLVED with a next action beats a
  stalled queue. Never trade the timebox for a lower-quality figure: a slow counted row beats a
  fast quoted one.

## Traps for this queue

{extra_traps}

## Output — checkpoint after EVERY row

Queue: `{REPO}/{queue}`.
Results: `{REPO}/{results}` — a JSON list, rewritten in full after every single row. Also rewrite
`{REPO}/{status}` as
{{ "rows_done": n, "rows_total": {n_rows}, "searches_used": n, "in_flight": "<conference>" }}
after every row.

{OUTPUT_CONTRACT}

Queue rows carry phase-1 `notes` and possibly `route_hint`. Echo `conference` verbatim; `row` is
the workbook row at queue time.

## Downloads

Download every source yourself into a fresh directory of your own (your session scratchpad or a
new `mktemp -d`), never the shared `/tmp`. Check each download's HTTP status and size before
counting it.

## Do not

Do not write to any spreadsheet or `.xlsx`. Do not modify any file outside your two output files.
Do not ask anyone to change a permission or config setting. If the search budget runs out, stop
and say so.

## Finish by reporting

A compact table (row / conference / abstracts / rung / verdict), total searches used; any NEW
route, wall or trap not already in the field notes (additions only — do not restate the notes);
duplicate rows spotted; rows you were least sure of.
"""
