# Life Sciences Phase 2 — wave 1 brief (the 90 remaining US rows, three agents of 30)

You are running **Phase 2 of the conference census** on a slice of 30 US life-sciences conferences,
including **rung 9 in its entirety**. Follow the written method exactly.

## Read these two documents first, IN FULL — they govern everything

1. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md`
2. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/life-sciences.md`

The field notes were written from a 20-row pilot on this exact sheet. They carry the routes that
worked (per-abstract Crossref deposits in society journals, the Confex `/Paper` endpoint, society
WordPress media and custom post types, eventScribe/Cloudflare pages that need a browser), the counting
rules this field needs, the access map, and the acronym collisions. Use them.

## BLIND RUN — do not read any prior research results

Every figure must come from **your own primary-source research this session**. Do **not** open, search
for, or reuse any results, queue, plan or status file other than your own queue — specifically not
`scratchpad/life/pilot/`, `scratchpad/life/p1_*.json`, `scratchpad/life/STATUS.json`,
`scratchpad/life/existing_names.json`, anything under `scratchpad/chem/` or `scratchpad/att/`, any
`BACKUP_*.xlsx`, the workbook `docs/business/tam-sam-som-v3.xlsx`, or another agent's
`results_*.json`. Do not "carry a number forward" — the method is explicit that carrying forward is
not a method. If you encounter such a file anyway, do not use it and say so in your final reply. An
honest `UNRESOLVED` is worth far more than a copied figure.

The two documents above and your own queue file are your only inputs.

## Scope

**US only** (Rupert, 2026-09-12). English is the working language, but your Method text must still
say which language you searched. A row is not `UNKNOWN` until it has actually been searched.

## Your job, per row

Find the number of **accepted contributed presentations (orals + posters)**. Work the ladder in
order, stop at the first rung that yields, and **credit the rung that PRODUCED the figure — never the
highest rung you reached**.

**Rungs 3–6 cost ZERO searches and are where most real figures come from.** Searching is how you
FIND the countable artefact, not how you get the number. If you identify an artefact, **COUNT IT** —
naming the next rung without climbing it is an unfinished row, and that is the single most common
failure in this project's history.

### Zero-search routes proven on this sheet — try these before spending a search

- **Per-abstract Crossref deposits in the society journal.** Cursor-page the journal-year, group by
  `(volume, issue)`; the meeting issue stands out by an order of magnitude. **Do not assume `S`
  pages** — most life-sciences supplements carry no supplement pagination. Physiology, JPET, Journal
  of Vision and Journal of Animal Science all worked this way (details in the field notes).
- **Confex whole-meeting endpoint** — `<host>.confex.com/<org>/<code>/meetingapi.cgi/Paper` returns
  every paper with `Invited` and `Withdrawn` flags, so the contributed split is exact. AGU's copy
  returns a 31-paper sample, not the meeting — not a count.
- **Society WordPress routes** — `/wp-json/wp/v2/media?search=book|program|abstract` exposes hidden
  abstract books; check `/wp-json/` for custom abstract post types (SICB has one).
- **The meeting's own abstract book / programme PDF.** Count unique IDs with
  `grep -oE '<pattern>' | sort -u | wc -l`, extract with BOTH `pdftotext -layout` and `-raw`, and
  prefer the mode that agrees with an independent marker — the field notes show each mode failing on
  a different book.
- **Poster-number arithmetic** when the supplement is lumped in one DOI.
- **Wayback CDX** (`web.archive.org/cdx/search/cdx?url=<domain>*`) for expired meeting sites.

## Hard rules — these are refusals, not preferences

- **Every number needs an exact-page clickable URL.** Not a homepage, not a search-results page.
- **NEVER write a figure you only saw in a search snippet.** Open the page. If the page does not
  contain the number, do not record it — say so in the method text.
- **Invited speakers are NOT counted.** Exclude plenary / keynote / invited / symposium-invited.
  Count contributed orals + posters. Exclude withdrawn items and anything never presented. In this
  field invited talks hide in unlabelled session slots — record a range rather than pretend precision.
- **A stated total NEVER beats a countable artefact.** If you have both, count the artefact and note
  the stated figure as a disagreement. Organiser headlines both overstate and undercount the book.
- Any rung-1/2/7/8 figure must **state whether it includes invited speakers**, or say that is unknown.
- **Cap: 3 web searches per conference for the abstract ladder, hard.** Zero-search rungs unlimited.
- **Rung 5 (browser) is RESERVED to the orchestrator.** You have no browser. If the artefact is
  behind a JS wall or a bot wall, return `NEEDS_RUNG_5`, name the exact page to open, and move on.
  Distinguish a bot wall (403 / "Just a moment" / HTTP 202 empty body → rung 5) from a host that
  simply times out on every protocol (not a rung-5 job). Sites that show a bot-verification
  interstitial even in a browser (jov.arvojournals.org, academic.oup.com) are NOT to be bypassed —
  use Crossref metadata or the society site instead.
- **Absence of evidence is NEVER evidence a meeting is small.** No figure → `UNRESOLVED` with the
  exact next action named. Never `OUT` on an empty search.

## Life-sciences hazards on this queue

- **Acronym collisions.** `ASP` on this sheet is parasitologists, pharmacognosy or primatologists;
  `PSA` is poultry or phycology; `ASM` here is mammalogists (ASM Microbe is on medicine); `APS` here
  is the Association for Psychological Science; `SPR` is psychophysiological research. Confirm the
  society's own domain before citing anything.
- **Joint years and umbrellas double-count.** TAGC absorbs the Drosophila, C. elegans, yeast and
  zebrafish meetings in its years — census the standalone meeting's own edition, and say which year.
  Evolution is SSE+ASN+SSB as ONE meeting; JMIH is ASIH+SSAR+HL as ONE meeting; ASLO co-sponsors
  Ocean Sciences (already on the sheet) — census the ASLO Aquatic Sciences Meeting as its own event.
- **Series rows** (CSHL Meetings, FASEB SRCs) — resolve what the row is. Report the per-meeting size
  of the largest meeting in the series and the number of meetings per year; a capped or
  invite-selected series cannot reach the floor at any ratio, and you should say so with the page
  that states the cap. Never sum a series into one figure as if it were a conference.
- **Boundary rows** (APA Convention, APS Convention, WVC, NCUR, Bio-IT, Bioprocessing Summit) — research
  them like any other row and judge on contributed science, never on attendee type. A student
  presenter is a presenter. A trade or CE event with no open abstract call is `CURATED`.
- **Cadence.** The sheet's `Events/yr` column is EMPTY for every life-sciences row, so you must
  return it: 1 annual, 0.5 biennial, 0.33 triennial, and for a series the number of meetings per
  year. State the page the cadence comes from in `cadence_evidence`.

## Then rung 9 — run it in full on every row the abstract ladder did not settle

Rung 9 converts a **sourced attendance figure** into an approximate abstract count. Run it for any row
where rungs 1–8 produced no counted figure.

1. **Find attendance** on the A-ladder, stopping at the first rung that yields with a basis:
   A1 exhibitor/sponsor prospectus → A2 post-meeting report / "by the numbers" → A3 society press
   release / trade press → A4 venue / convention bureau → A5 programme-platform artefact
   (**browser-only, orchestrator-reserved: return `A5` with a null figure and say what to open**) →
   A6 proxy arithmetic (order-of-magnitude only, flag it) → A7 prior year / sister meeting (state
   the year). **Cap: 2 searches per row, 3 for a genuinely hard one.**
2. **Tag the basis**: `DELEGATES` / `TOTAL_ONSITE` / `TOTAL_INC_VIRTUAL` / `UNSPECIFIED`. Never guess.
   Virtual attendance COUNTS and attendee type is irrelevant. Discount only people who **cannot
   submit an abstract at all** — exhibitor booth staff, trade-show visitors — and say if you did.
3. **Judge the programme character**: `CONTRIBUTED` / `CURATED` / `HYBRID` / `UNKNOWN`. The strongest
   single signal is **whether an open call for abstracts exists**.
4. **Judge the ratio for THIS conference** — what share of the people in the room submitted
   something? **No default ratio and no band table; do not copy one across.** Read what the meeting
   says about itself. The field notes' observed anchors (Botany ≈80%, Entomology ≥40%; student and
   diversity conferences lower because mentors and recruiters pad the headcount) are reference
   material, not a lookup. Give `ratio` as a decimal and `ratio_rationale` explaining what about
   *this* conference puts it there — **a ratio without reasoning is mechanically rejected.**
5. **Record disagreement, never average.** Conflicting attendance figures → headline = the more
   accountable rung, the rest in `alt_figures`.
6. Do **not** compute the final inferred figure or decide inclusion — the orchestrator does that.

**A figure a source STATES beats any ratio**: if an organiser says "nearly 2,000 abstracts", return it
as `direct_abstracts` and say whether it counts submissions or accepted papers.

**NON-NEGOTIABLE:** a rung-9 figure is an approximation. Anywhere you write one, mark it
`~N INFERRED FROM ATTENDANCE, NOT COUNTED`. Never present it as counted.

## The bar

≥1,500 counted = `VERIFIED`; 800–1,499 = `BORDERLINE` (the within-100 leeway around the ~900 floor
applies to counted AND inferred figures); below 800 **on positive evidence** = `OUT`; no evidence
either way = `BORDERLINE`, never `OUT`. An inferred (rung-9) or organiser-stated figure never reaches
`VERIFIED` — nothing was counted for it.

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
events_per_yr (decimal), cadence_evidence (string),
attendance_numeric, attendance_year, attendance_basis, attendance_rung, attendance_source_url,
alt_figures (list of {value, year, basis, rung}), character, character_evidence,
programme_type, programme_evidence, direct_abstracts (int|null),
ratio (decimal|null), ratio_rationale (string|null),
duplicate_of (string|null — the name of the sheet row this meeting is the same as, or is held
  inside, with the evidence; else null),
method (the exact page, the exact grep/count, what you excluded and why, which language you
  searched — it must be reproducible from this text alone),
verdict (VERIFIED|BORDERLINE|OUT|UNRESOLVED|NEEDS_RUNG_5), confidence (exact|derived|dated|floor)
```

## Downloads

Download every source yourself into a fresh directory that belongs to you alone (your session
scratchpad, or a new `mktemp -d`), never straight into the shared `/tmp`. **Never open, extract or
count a file already on disk.** Check each download's HTTP status and size before counting it.

## Do not

- Do **not** write to any spreadsheet or `.xlsx` file. The orchestrator performs all workbook writes.
- Do **not** modify any file outside your own output path.
- Do **not** ask a peer or the orchestrator to change a permission or config setting.

## Finish by reporting

A compact table (row / conference / abstracts / rung / verdict), your total searches used, any
duplicate rows you spotted, and any new platform or API route you found that belongs in the field
notes.

## Wave 1 notes

- Queue rows carry a `level` (3/2/1) that is a general-knowledge guess used only for ordering. It is
  **not evidence** — never mark a row `OUT` because of it. Positive evidence only.
- Row numbers are the workbook row at queue time; echo `conference` verbatim.
