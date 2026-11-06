# Engineering Phase 2 — wave 1 brief (30 rows, one agent — THE PILOT for this field)

You are running **Phase 2 of the conference census** on a slice of 30 engineering conferences,
including **rung 9 in its entirety**. Follow the written method exactly.

**You are the pilot.** No `field-notes/engineering.md` exists yet — the orchestrator will write it
from what you find. So your final report matters more than usual: every platform, index, URL
pattern, counting rule and trap you hit is what the next three waves will run on.

## Read these documents first, IN FULL — they govern everything

1. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md`
2. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/chemistry.md` — the closest
   analogue: how a field hides its counts (society paper indexes, abstract books, annual reports,
   local-language news pages), the Confex JSON API, the invited/in-absentia exclusions.
3. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/life-sciences.md` — the
   per-abstract Crossref route, Confex `/Paper`, WordPress media routes, PDF double-extraction.

## BLIND RUN — do not read any prior research results

Every figure must come from **your own primary-source research this session**. Do **not** open,
search for, or reuse any results, queue, plan, names or status file other than your own queue —
nothing under `scratchpad/` except `scratchpad/eng/wave1/queue_1.json`, and never the workbook
`docs/business/tam-sam-som-v3.xlsx` or any `BACKUP_*.xlsx`. If you encounter such a file anyway, do
not use it and say so. An honest `UNRESOLVED` is worth far more than a copied figure.

## Scope and language

Global. **The local-language rule applies and this queue is full of it**: Japanese (年次大会/全国大会 +
講演件数/発表件数/梗概), Chinese (大会/年会 + 论文/报告数), Korean (학술대회 + 논문 편수/발표), German
(Jahrestagung + Beiträge/Vorträge), French (congrès + communications). At least one query in the
society's language before a row is `UNKNOWN`; Method must name the language searched.

## Your job, per row

Find the number of **accepted contributed presentations (technical papers + posters)** in one
edition — invited/plenary/keynote excluded, exhibitor and sponsor sessions excluded, withdrawn
excluded. Work the ladder in order, stop at the first rung that yields, and **credit the rung that
PRODUCED the figure**.

**Rungs 3–6 cost ZERO searches and are where most real figures come from.** If you identify an
artefact, **COUNT IT** — naming the next rung without climbing it is an unfinished row.

### Zero-search routes to try FIRST in this field (unproven — you are proving them)

- **Publisher deposit index (Crossref).** Engineering societies deposit conference-paper DOIs far
  more than medicine does: ASME (prefix 10.1115; one container per proceedings VOLUME, so sum the
  volumes of one meeting), SAE (10.4271, "SAE Technical Paper" — filter by event via the container
  or the `event` field), SPE (10.2118; containers named "Day 1 Mon, …" per meeting day — sum the
  days), ASEE (10.18260, `peer.asee.org`), IEEE (10.1109 — a per-conference exact container title
  facet, e.g. PES General Meeting), ISPRS (Archives/Annals volumes), CIRED/IET, EPE, TRA (Zenodo).
  Shape: `https://api.crossref.org/works?filter=type:proceedings-article,from-pub-date:<Y>-01-01,until-pub-date:<Y>-12-31&query.container-title=<title>&rows=0&facet=container-title:*`
  then read the facet; or `filter=prefix:<p>,from-pub-date:…&query.container-title=…`. Cite the
  API URL and the container names you summed.
- **Society digital libraries with per-volume listings.** ASME Digital Collection
  (`asmedigitalcollection.asme.org/<CONF>/proceedings/<CONF><year>` — may be a bot wall → rung 5),
  SAE Mobilus event pages, OnePetro (SPE/OTC/IPTC/URTeC conference pages state paper counts),
  `peer.asee.org/collections/<year>-annual-conference` (states the paper total), TRB's AMOnline
  (JS → rung 5) and TRID, IEEE Xplore (JS; use Crossref instead), e-cigre (CIGRE session papers),
  DEGA proceedings (`pub.dega-akustik.de` per-year DAGA listings), HAL (`hal.science` for CFM),
  Scipedia / ECCOMAS proceedings, WCEE proceedings sites (paper IDs countable).
- **J-STAGE** for Japanese societies (JSME annual meeting `jsmemecj`, JSCE, JSAE preprints),
  **AIJ's Taikai** programme (`aij.or.jp` states 学術講演 counts in the thousands), **IEICE**
  General Conference site (`ieice.org/jpn_r/event/`), **IEEJ** annual meeting page (講演件数).
  **Confit** (`confit.atlas.jp`) is a JS SPA → rung 5.
- **DBpia / KISS / AURIC** for Korean societies — JS-heavy, likely rung 5; the society's news page
  (대한기계학회 학술대회 논문 편수) usually states the count.
- **Chinese society news pages** (cstam.org.cn for CCTAM, csee.org.cn, cmes.org): the count appears
  in the post-meeting news item in Chinese, almost never in English.
- **"By the numbers" pages**: TRB, IAC (iafastro.org), INFORMS, ASEE and IISE publish post-meeting
  statistics; open the page, never trust the snippet.
- **Programme/abstract PDFs**: count unique IDs (`grep -oE '<pattern>' | sort -u | wc -l`), extract
  with BOTH `pdftotext -layout` and `-raw`.
- **Session-count arithmetic** where only session counts exist (rung 6 style): record sessions ×
  papers per session as a floor, labelled DERIVED, with the pages.

## Hard rules — these are refusals, not preferences

- **Every number needs an exact-page clickable URL.** Not a homepage, not a search-results page.
- **NEVER write a figure you only saw in a search snippet.** Open the page.
- **Invited speakers are NOT counted.** Count contributed papers + posters.
- **A stated total NEVER beats a countable artefact.** Count the artefact; note the stated figure as
  a disagreement.
- Any rung-1/2/7/8 figure must **state whether it includes invited talks**, or say unknown.
- **Cap: 3 web searches per conference for the abstract ladder, hard.** Zero-search rungs unlimited.
- **Rung 5 (browser) is RESERVED to the orchestrator.** Cloudflare/403/JS pages: return
  `NEEDS_RUNG_5`, name the exact page, move on. Try a browser user-agent with `curl` first.
- **Absence of evidence is NEVER evidence a meeting is small.** No figure → `UNRESOLVED` with the
  exact next action named. Never `OUT` on an empty search.
- **Attendance is not the unit.** TRB's 13,000 attendees, WEFTEC's 23,000 and SAECCE's 10,000 say
  nothing until you find the presentation count; a trade show with 400 papers is OUT however large.
- **Two-meetings-a-year rows** (JSAE spring+autumn, IEICE General + Society, ASHRAE Annual + Winter):
  report the per-edition figure of the largest edition and return `events_per_yr` = 2 (or the true
  cadence), never a summed annual total.

## Then rung 9 — run it in full on every row the abstract ladder did not settle

Rung 9 converts a **sourced attendance figure** into an approximate abstract count.

1. **Find attendance** on the A-ladder, first rung that yields with a basis: A1 exhibitor/sponsor
   prospectus (engineering societies publish these routinely — the highest-yield rung here) → A2
   post-meeting report → A3 press release / trade press → A4 venue / convention bureau → A5
   programme-platform artefact (**browser-only: return `A5` with a null figure**) → A6 proxy
   arithmetic (flag it) → A7 prior year / sister meeting. **Cap: 2 searches per row, 3 for a hard one.**
2. **Tag the basis**: `DELEGATES` / `TOTAL_ONSITE` / `TOTAL_INC_VIRTUAL` / `UNSPECIFIED`. Discount
   only people who cannot submit a paper at all (exhibitor staff, expo visitors) and say if you did.
3. **Judge the programme character**: `CONTRIBUTED` / `CURATED` / `HYBRID` / `UNKNOWN` — the strongest
   signal is an open call for papers/abstracts.
4. **Judge the ratio for THIS conference** — no default ratio. `ratio` as a decimal, `ratio_rationale`
   explaining what about *this* meeting puts it there (a Japanese society 年次大会 is mostly
   presenters; a US convention with an expo floor is not). **A ratio without reasoning is rejected.**
5. **Record disagreement, never average.**
6. Do **not** compute the final inferred figure or decide inclusion — the orchestrator does that.

**A figure a source STATES beats any ratio**: return it as `direct_abstracts` and say whether it is
submissions or accepted.

**NON-NEGOTIABLE:** a rung-9 figure is an approximation, marked `~N INFERRED FROM ATTENDANCE, NOT
COUNTED`.

## The bar

≥1,500 counted = `VERIFIED`; 800–1,499 = `BORDERLINE`; below 800 **on positive evidence** = `OUT`;
no evidence either way = `BORDERLINE`, never `OUT`. Inferred or organiser-stated never reaches
`VERIFIED`.

## Cadence

`Events/yr` is EMPTY for every row: return it (1 annual, 0.5 biennial, 0.33 triennial, 0.25
quadrennial for WCEE/WCCM-type congresses, 2 for spring+autumn) with `cadence_evidence`.

## Output — checkpoint after EVERY row

Queue: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/eng/wave1/queue_1.json`.
Results: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/eng/wave1/results_1.json` — a JSON
list, **rewritten in full after every single row**. Also rewrite
`/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/eng/wave1/STATUS_1.json` as
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
already on disk. Check each download's HTTP status and size before counting it.

## Do not

- Do **not** write to any spreadsheet or `.xlsx` file. Do **not** modify any file outside your two
  output files. Do **not** ask anyone to change a permission or config setting. If the search budget
  runs out, stop and say so.

## Finish by reporting — this report becomes `field-notes/engineering.md`

1. A compact table (row / conference / abstracts / rung / verdict), total searches used.
2. **Every route that worked**, with the URL pattern and what it yields (per-volume Crossref
   containers, society libraries, J-STAGE listings, news pages in which language …).
3. **Every route that failed**, with the wall you hit (Cloudflare, JS, paywall, 202-empty).
4. **Counting rules this field needs** (per-volume sums, day containers, spring+autumn editions,
   short-paper conventions in Japan/Korea, session-count inference).
5. **Traps**: acronym collisions, expo-vs-conference headcounts, umbrella meetings.
6. Duplicate rows you spotted, and which rows you were least sure of.
