# CS & AI Phase 2 — wave 1 brief (the 30 second-pass rows, one agent)

You are running **Phase 2 of the conference census** on the 30 CS & AI conferences that the DBLP +
Crossref index pass could not see, including **rung 9 in its entirety**. Follow the written method
exactly.

## Read these two documents first, IN FULL — they govern everything

1. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md`
2. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/cs-ai.md` — interim notes:
   the unit, the overlap map, the zero-search routes (DBLP SPARQL, Crossref facets, OpenReview, ACL
   Anthology, J-STAGE, IPSJ digital library, CCF's list) and the field's traps (workshop inflation,
   umbrella double-counting, attendance over mostly-invited forums).

## BLIND RUN — do not read any prior research results

Every figure must come from **your own primary-source research this session**. Do **not** open,
search for, or reuse any results, queue, plan, names or status file other than your own queue —
specifically nothing under `scratchpad/` except `scratchpad/cs/wave1/queue.json`, and never the
workbook `docs/business/tam-sam-som-v3.xlsx` or any `BACKUP_*.xlsx`. Do not "carry a number forward".
If you encounter such a file anyway, do not use it and say so in your final reply. An honest
`UNRESOLVED` is worth far more than a copied figure.

## Scope and language

Global. **The local-language rule applies**: for a Japanese, Chinese, Korean, Spanish or Portuguese
society, at least one query in the society's language using the local term for the artefact
(年会/全国大会 + 発表件数/講演数; 年会/大会 + 论文/报告数; 학술대회 + 논문 편수; congreso + comunicaciones;
congresso + trabalhos). Your Method text must say which language you searched. A row is not
`UNKNOWN` until it has been searched in its own language.

## Your job, per row

Find the number of **accepted contributed presentations** — for this field, accepted main-track
papers plus posters, **workshop/companion volumes and invited talks excluded**. Work the ladder in
order, stop at the first rung that yields, and **credit the rung that PRODUCED the figure**.

**Rungs 3–6 cost ZERO searches and are where most real figures come from.** Searching is how you
FIND the countable artefact, not how you get the number. If you identify an artefact, **COUNT IT**.

### Zero-search routes for this field — try these before spending a search

- **DBLP SPARQL** (`https://sparql.dblp.org/sparql`, open to plain HTTP; the query is in the field
  notes). Every stream ≥300 papers was already counted, so a row on your queue is there only if
  DBLP lacks it or indexes it under a name the index pass did not match — check by acronym and by
  title words before concluding it is absent. The stream page `https://dblp.org/streams/<key>` is the
  citable URL (dblp.org HTML is behind an Anubis challenge: that is rung 5, say so).
- **Crossref** — `https://api.crossref.org/works?filter=type:proceedings-article,from-pub-date:<Y>-01-01,until-pub-date:<Y>-12-31&query.container-title=<title>&rows=0&facet=container-title:*`
  and read the facet for the exact container. National proceedings often carry DOIs even when
  DBLP ignores them (JSAI's are on J-STAGE with DOIs; IPSJ's are not).
- **J-STAGE** volume listings (`jstage.jst.go.jp/browse/pjsai/<vol>/0/_contents/-char/ja`) —
  one row per presentation, paginated; count the listing and cross-check the society's stated count.
- **The society's own post-meeting news page in its language** — JSAI states 発表件数; IPSJ's
  convention site states 講演件数; KIISE/KIPS state 논문 편수; CCF states forum and paper counts.
- **OpenReview API** for OpenReview-hosted venues (COLM): `api2.openreview.net/notes?content.venueid=<id>&limit=1` returns `count`.
- **Programme/abstract PDFs**: count unique IDs with `grep -oE '<pattern>' | sort -u | wc -l`,
  extract with BOTH `pdftotext -layout` and `-raw` and prefer the mode that agrees with an
  independent marker.
- **Wayback CDX** (`web.archive.org/cdx/search/cdx?url=<domain>*`) for expired meeting sites.

## Hard rules — these are refusals, not preferences

- **Every number needs an exact-page clickable URL.** Not a homepage, not a search-results page.
- **NEVER write a figure you only saw in a search snippet.** Open the page.
- **Invited speakers are NOT counted.** Plenary / keynote / invited forums are out. Count
  contributed papers + posters. Exclude workshops and withdrawn items.
- **A stated total NEVER beats a countable artefact.** Count the artefact; note the stated figure as
  a disagreement.
- Any rung-1/2/7/8 figure must **state whether it includes invited talks and workshops**, or say unknown.
- **Cap: 3 web searches per conference for the abstract ladder, hard.** Zero-search rungs unlimited.
- **Rung 5 (browser) is RESERVED to the orchestrator.** Confit (`confit.atlas.jp`, HTTP 202 + empty
  body), DBpia/KISS, dblp.org HTML (Anubis), any JS programme site: return `NEEDS_RUNG_5`, name the
  exact page, and move on.
- **Absence of evidence is NEVER evidence a meeting is small.** No figure → `UNRESOLVED` with the
  exact next action named. Never `OUT` on an empty search.
- **Umbrella rows** (FCRC, WCCI, SSCI, FLoC, IFIP WCC): if the meeting is the sum of tracks that are
  separately counted conferences (IJCNN, FUZZ-IEEE, CEC; STOC, PLDI …), return `duplicate_of` naming
  those tracks and the evidence, and do NOT return a summed figure as if it were one conference.
- **Industry/curated events** (GTC, RSA, FOSDEM, Grace Hopper): research like any row, judge on
  contributed papers; no open call for papers → `CURATED`, and say what the sessions are instead.

## Then rung 9 — run it in full on every row the abstract ladder did not settle

Rung 9 converts a **sourced attendance figure** into an approximate abstract count. Run it for any row
where rungs 1–8 produced no counted figure.

1. **Find attendance** on the A-ladder, first rung that yields with a basis: A1 exhibitor/sponsor
   prospectus → A2 post-meeting report → A3 society press release / trade press → A4 venue /
   convention bureau → A5 programme-platform artefact (**browser-only, orchestrator-reserved: return
   `A5` with a null figure**) → A6 proxy arithmetic (flag it) → A7 prior year / sister meeting (state
   the year). **Cap: 2 searches per row, 3 for a genuinely hard one.**
2. **Tag the basis**: `DELEGATES` / `TOTAL_ONSITE` / `TOTAL_INC_VIRTUAL` / `UNSPECIFIED`. Never guess.
3. **Judge the programme character**: `CONTRIBUTED` / `CURATED` / `HYBRID` / `UNKNOWN`. The strongest
   single signal is **whether an open call for papers/abstracts exists**.
4. **Judge the ratio for THIS conference** — what share of the people in the room presented? No
   default ratio. Give `ratio` as a decimal and `ratio_rationale` explaining what about *this*
   conference puts it there. **A ratio without reasoning is mechanically rejected.** In this field
   national CS congresses run high ratios (a Japanese 全国大会 is mostly student presenters); flagship
   forums like CNCC run very low (mostly invited).
5. **Record disagreement, never average.** Conflicting figures → headline = the more accountable rung,
   the rest in `alt_figures`.
6. Do **not** compute the final inferred figure or decide inclusion — the orchestrator does that.

**A figure a source STATES beats any ratio**: if a society says "1,186 presentations", return it as
`direct_abstracts` and say whether it counts submissions or accepted presentations.

**NON-NEGOTIABLE:** a rung-9 figure is an approximation. Mark it `~N INFERRED FROM ATTENDANCE, NOT
COUNTED`. Never present it as counted.

## The bar

≥1,500 counted = `VERIFIED`; 800–1,499 = `BORDERLINE` (the within-100 leeway around the ~900 floor
applies to counted AND inferred figures); below 800 **on positive evidence** = `OUT`; no evidence
either way = `BORDERLINE`, never `OUT`. An inferred or organiser-stated figure never reaches
`VERIFIED`.

## Cadence

`Events/yr` is EMPTY for every row: return it (1 annual, 0.5 biennial, 2 for spring+autumn) with
`cadence_evidence` naming the page.

## Output — checkpoint after EVERY row

Queue: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/cs/wave1/queue.json`.
Results: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/cs/wave1/results.json` — a JSON
list, **rewritten in full after every single row**. Also rewrite
`/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/cs/wave1/STATUS.json` as
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
duplicate_of (string|null — the sheet row or separately-counted tracks this meeting is the same as
  or is held inside, with the evidence; else null),
method (the exact page, the exact grep/count/query, what you excluded and why, which language you
  searched — reproducible from this text alone),
verdict (VERIFIED|BORDERLINE|OUT|UNRESOLVED|NEEDS_RUNG_5), confidence (exact|derived|dated|floor)
```

Queue rows carry the phase-1 `notes` (why listed, size hint if a page stated one). Hints are for
ordering only, never evidence. Echo `conference` verbatim; `row` is the workbook row at queue time.

## Downloads

Download every source yourself into a fresh directory that belongs to you alone (your session
scratchpad or a new `mktemp -d`), never into the shared `/tmp`. Never open, extract or count a file
already on disk. Check each download's HTTP status and size before counting it.

## Do not

- Do **not** write to any spreadsheet or `.xlsx` file. Do **not** modify any file outside your two
  output files. Do **not** ask anyone to change a permission or config setting. If the search budget
  runs out, stop and say so.

## Finish by reporting

A compact table (row / conference / abstracts / rung / verdict), total searches used, duplicate rows
spotted, and every new platform or API route you found that belongs in `field-notes/cs-ai.md`.
