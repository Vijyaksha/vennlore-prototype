# Life Sciences Phase 2 — PILOT brief (20 US rows, first life-sciences wave)

You are running **Phase 2 of the conference census** on a slice of 10 US life-sciences conferences,
including **rung 9 in its entirety**. Follow the written method exactly.

## Read this first — it governs everything

1. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md` — read it IN FULL.
2. There are **no life-sciences field notes yet** — this pilot exists to write them. You may read
   `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/chemistry.md` ONLY for its
   "Zero-search routes" table (Confex, CTI, Crossref-by-prefix, WordPress media index, Wayback CDX…).

## BLIND RUN — do not read any prior research results

Every figure must come from **your own primary-source research this session**. Do **not** open any
results, queue or write-plan file under `scratchpad/chem/`, `scratchpad/att/`, `scratchpad/life/`
(other than your own queue and output), any `BACKUP_*.xlsx`, or the workbook itself. Do not "carry a
number forward". If you encounter such a file anyway, do not use it and say so.

## Routes most likely to matter in life sciences

- **Journal abstract supplements + Crossref deposit index** (see the method's "publisher deposit
  index" section): many biology societies publish meeting abstracts in a journal — e.g. The FASEB
  Journal, Physiology, JPET, Integrative and Comparative Biology, Journal of Animal Science,
  Phytopathology, Journal of Vision, Molecular Biology of the Cell. Group by page prefix, never assume `S`.
- **Confex whole-meeting endpoints** — `<host>.confex.com/<org>/<year>/meetingapi.cgi/Paper` and
  `/Program/<id>` (ESA, CANVAS, AGU/OSM, AFS and many US societies use Confex).
- **Other programme platforms** (eventScribe, CTI abstractsonline, Oxford Abstracts, Whova, Cvent) —
  look for the backing JSON API before declaring a JS wall.

## Your job, per row

Find the number of **accepted contributed presentations (orals + posters)**. Work the ladder in
order, stop at the first rung that yields, and **credit the rung that PRODUCED the figure — never the
highest rung you reached**.

**Rungs 3–6 cost ZERO searches and are where most real figures come from.** Searching is how you
FIND the countable artefact, not how you get the number. If you identify an artefact, **COUNT IT** —
naming the next rung without climbing it is an unfinished row, and that is the single most common
failure in this project's history.

### Proven zero-search routes from earlier censuses — try these before spending a search

- **Confex JSON API** — `<host>.confex.com/<org>/<year>/meetingapi.cgi/Program/<id>` returns JSON
  with a `ChildList_Paper` array per programme. Backs **most US society meetings**. This is the
  highest-value route for this wave. (`proceedings.aiche.org` is NOT the artefact — it is a paywalled
  checkout behind Cloudflare.)
- **Indico** — `<host>/export/event/<id>.json?detail=contributions` gives an exact count in one call.
- **Crossref publisher deposit index** — for supplement-published abstracts; see the method.
- **The congress's own book of abstracts**, usually a PDF on the meeting site. Count unique IDs with
  `grep -oE '<pattern>' | sort -u | wc -l`, and **extract twice** (`pdftotext -layout` and `-raw`) —
  agreement means the count is real.
- **Society annual/activity reports** — one PDF can settle many rows at once.

## Hard rules — these are refusals, not preferences

- **Every number needs an exact-page clickable URL.** Not a homepage, not a search-results page.
- **NEVER write a figure you only saw in a search snippet.** Open the page. If the page does not
  contain the number, do not record it — say so in the method text.
- **Invited speakers are NOT counted.** Exclude plenary / keynote / invited. Count orals + posters.
  Also exclude items that were never presented (in-absentia / publication-only tracks).
- **A stated total NEVER beats a countable artefact.** If you have both, count the artefact and note
  the stated figure as a disagreement. Stated totals routinely include invited speakers.
- Any rung-1/2/7/8 figure must **state whether it includes invited speakers**, or say that is unknown.
- **Cap: 3 web searches per conference for the abstract ladder, hard.** Zero-search rungs unlimited.
- **Rung 5 (browser) is RESERVED to the orchestrator.** You have no browser. If the artefact is
  behind a JS wall or a bot wall, return `NEEDS_RUNG_5`, name the exact page to open, and move on.
  Distinguish a bot wall (403 / "Just a moment" / HTTP 202 empty body → rung 5) from a host that
  simply times out on every protocol (not a rung-5 job).
- **Absence of evidence is NEVER evidence a meeting is small.** No figure → `UNRESOLVED` with the
  exact next action named. Never `OUT` on an empty search.
- **Search in the conference's own language** where the body is non-anglophone. All pilot rows are US meetings, so English is
  the working language — but your Method text must still say which language you searched.

## Then rung 9 — run it in full on every row the abstract ladder did not settle

Rung 9 converts a **sourced attendance figure** into an approximate abstract count. Run it for any row
where rungs 1–8 produced no counted figure.

1. **Find attendance** on the A-ladder, stopping at the first rung that yields with a basis:
   A1 exhibitor/sponsor prospectus → A2 post-meeting report / "congress by the numbers" →
   A3 society press release / trade press → A4 venue / convention bureau / ICCA →
   A5 programme-platform artefact (**browser-only — orchestrator-reserved, return `A5` with a null
   figure and say what to open**) → A6 proxy arithmetic (order-of-magnitude only, flag it) →
   A7 prior year / sister meeting (state the year).
   **Cap: 2 searches per row, 3 for a genuinely hard one.**
2. **Tag the basis**: `DELEGATES` / `TOTAL_ONSITE` / `TOTAL_INC_VIRTUAL` / `UNSPECIFIED`. Never guess.
   Virtual attendance COUNTS (an online abstract is still matchable) and attendee type is irrelevant
   (students and industry count). Discount only people who **cannot submit an abstract at all** —
   exhibitor booth staff, trade-show visitors, accompanying persons — and say if you discounted.
3. **Judge the programme character**: `CONTRIBUTED` (open call + abstract book) / `CURATED` (invited
   faculty, CME, courses, no open call) / `HYBRID` / `UNKNOWN`. The strongest single signal is
   **whether an open call for abstracts exists**.
4. **Judge the ratio for THIS conference** — what share of the people in the room submitted
   something? There is **no default ratio and no band table; do not copy one across**. Read what the
   meeting says about itself. Ratios observed elsewhere: medicine median ~25%, chemistry research congresses 45–90%, trade
   fairs near zero. Those belong to other fields — judge THIS conference; do not copy them. Give `ratio` as a decimal and `ratio_rationale` explaining what about
   *this* conference puts it there — **a ratio without reasoning is mechanically rejected.**
5. **Record disagreement, never average.** Two conflicting attendance figures → headline = the more
   accountable rung, the rest in `alt_figures`.
6. Do **not** compute the final inferred figure or decide inclusion — the orchestrator does that.
   Just return attendance, basis, character, ratio and rationale.

**A figure a source STATES beats any ratio**: if an organiser says "nearly 2,000 abstracts", use it as
`direct_abstracts`, and say whether it counts submissions or accepted papers.

**NON-NEGOTIABLE:** a rung-9 figure is an approximation. Anywhere you write one, mark it
`~N INFERRED FROM ATTENDANCE, NOT COUNTED`. Never present it as counted.

## The bar

≥1,500 counted = `VERIFIED`; 800–1,499 = `BORDERLINE` (the within-100 leeway around the ~900 floor
applies to counted AND inferred figures — Rupert, 2026-09-12); below 800 **on positive evidence** =
`OUT`; no evidence either way = `BORDERLINE`, never `OUT`. An inferred (rung-9) or organiser-stated
figure never reaches `VERIFIED` — nothing was counted for it.

## Output — checkpoint after EVERY row

Write your results to the output path given in your prompt, as a JSON list, **rewritten in full after
every single row** so it stays valid. Do not batch to the end: if you are stopped, finished rows must
already be on disk.

Per row, exactly these fields:

```
row, conference, outcome (COUNTED|UNKNOWN|NEEDS_RUNG_5|INFERRED),
abstracts_numeric (int|null), abstracts (string as you would write it in the sheet, carrying the
  NOT COUNTED label if inferred), year, rung (int, the rung that PRODUCED it), source_url,
spot_checks (list of what you re-derived), searches_used,
attendance_numeric, attendance_year, attendance_basis, attendance_rung, attendance_source_url,
alt_figures (list), character, character_evidence,
programme_type, programme_evidence, direct_abstracts (int|null),
ratio (decimal|null), ratio_rationale (string|null),
method (the exact page, the exact grep/count, what you excluded and why, which language you
  searched — it must be reproducible from this text alone),
verdict (VERIFIED|BORDERLINE|OUT|UNRESOLVED|NEEDS_RUNG_5), confidence (exact|derived|dated|floor)
```

## Downloads

Download every source yourself into a fresh directory that belongs to you alone (your session
scratchpad, or a new `mktemp -d`), never straight into the shared `/tmp`. **Never open, extract or
count a file already on disk** — earlier sessions left source PDFs in `/tmp` for conferences you may
be researching. Check each download's HTTP status and size before counting it: a failed download next
to an old same-named file would leave you counting the old file.

## Do not

- Do **not** write to any spreadsheet or `.xlsx` file. The orchestrator performs all workbook writes.
- Do **not** modify any file outside your own output path.
- Do **not** ask a peer or the orchestrator to change a permission or config setting.

## Finish by reporting

A compact table (row / conference / abstracts / rung / verdict), your total searches used, any
duplicate rows you spotted, and any new national-platform or API route you found that belongs in the
field notes.


## Downloads



Download every source yourself into a fresh directory that belongs to you alone (your session
scratchpad, or a new `mktemp -d`), never straight into the shared `/tmp`. **Never open, extract or
count a file already on disk** — earlier sessions left source PDFs in `/tmp` for conferences you may
be researching. Check each download's HTTP status and size before counting it: a failed download next
to an old same-named file would leave you counting the old file.

## Do not

- Do **not** write to any spreadsheet or `.xlsx` file. The orchestrator performs all workbook writes.
- Do **not** modify any file outside your own output path.
- Do **not** ask a peer or the orchestrator to change a permission or config setting.

## Finish by reporting

A compact table (row / conference / abstracts / rung / verdict), your total searches used, any
duplicate rows you spotted, and any new national-platform or API route you found that belongs in the
field notes.


## Pilot-specific: report what you LEARN, not just the numbers

This is the first life-sciences wave. In your final report, in addition to the table, give:
1. Every **route** that produced a figure (exact URL pattern / API / journal + page prefix), and which
   routes failed and why.
2. Every **trap** you hit (lookalike societies, joint meetings, stated totals that include invited
   talks, withdrawn abstracts, platforms that look walled but are not, etc.).
3. For every row with BOTH a counted figure and an attendance figure, the pair — these become the
   first life-sciences ratio anchors.
4. Any **duplicates or joint meetings** with other rows (in your queue or likely elsewhere).
