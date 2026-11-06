# Earth, Environmental & Agricultural Sciences Phase 2 — wave 1 brief (30 rows, one agent — THE PILOT)

You are running **Phase 2 of the conference census** on a slice of 30 earth/environmental/
agricultural conferences, including **rung 9 in its entirety**. Follow the written method exactly.

**You are the pilot.** No `field-notes/earth-sciences.md` exists yet — the orchestrator will write
it from what you find. So your final report matters more than usual: every platform, index, URL
pattern, counting rule and trap you hit is what the later waves will run on.

## Read these documents first, IN FULL — they govern everything

1. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md`
2. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/engineering.md` — the
   closest recent pilot: society libraries, national platforms, J-STAGE/Confit, Chinese news pages.
3. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/chemistry.md` — how a
   field hides its counts; abstract books; invited/in-absentia exclusions.

## BLIND RUN — do not read any prior research results

Every figure must come from **your own primary-source research this session**. Do **not** open,
search for, or reuse any results, queue, plan, names or status file other than your own queue —
nothing under `scratchpad/` except `scratchpad/earth/wave1/queue_1.json`, and never the workbook
`docs/business/tam-sam-som-v3.xlsx` or any `BACKUP_*.xlsx`. If you encounter such a file anyway, do
not use it and say so. An honest `UNRESOLVED` is worth far more than a copied figure.

## Scope and language

Global, and this queue is local-language heavy: Japanese (大会/年会 + 講演件数/発表件数/要旨),
Chinese (学术年会 + 论文/报告数/参会人数), Portuguese (congresso + trabalhos/anais/resumos),
Spanish (congreso + resúmenes/actas), German (Jahrestagung + Beiträge), French (congrès +
communications). At least one query in the society's language before a row is `UNKNOWN`; Method
must name the language searched.

## Your job, per row

Find the number of **accepted contributed presentations (orals + posters)** in one edition —
invited/plenary/keynote excluded, exhibitor and sponsor sessions excluded, withdrawn excluded.
Work the ladder in order, stop at the first rung that yields, and **credit the rung that PRODUCED
the figure**.

**Rungs 3–6 cost ZERO searches and are where most real figures come from.** If you identify an
artefact, **COUNT IT** — naming the next rung without climbing it is an unfinished row.

### Zero-search routes to try FIRST in this field (mostly unproven — you are proving them)

- **Copernicus Meeting Organizer** (`meetingorganizer.copernicus.org/<MEETING><year>`) — runs EGU
  and hosts many European meetings (EMS annual meetings are on it). Plain HTML session programme;
  abstracts have countable IDs (`<MEETING>-<year>-NNNN`). Also `presentations.copernicus.org`.
- **USRA/LPI meeting archives** for planetary meetings: `www.hou.usra.edu/meetings/<meeting><yy>/`
  — programme PDFs and per-abstract pages, countable IDs; LPSC posts "abstracts submitted/accepted"
  in its program announcements.
- **Journal-supplement TOCs**: SSA publishes its meeting abstracts in *Seismological Research
  Letters* (technical program issue); soil/agro societies publish in society journals. Crossref
  page-prefix counting works exactly as the methodology describes.
- **ISHS Acta Horticulturae** (`actahort.org` / ISHS on Crossref): each IHC symposium becomes Acta
  volumes — sum the volumes of one congress for an exact paper count, zero searches.
- **Book-of-abstracts PDFs**: EAAP annual meeting books (Wageningen Academic, free PDFs, ~1,000+
  abstracts, ID-greppable); IUFRO congress abstract books; WCSS programme books; INQUA/IGC
  programme PDFs. Count unique IDs, extract with BOTH `pdftotext -layout` and `-raw`.
- **Confit** (`confit.atlas.jp`) hosts JpGU and most Japanese societies — it is a JS SPA:
  `NEEDS_RUNG_5`. BUT the societies' own news/stats pages state totals: JpGU posts "we received
  over N presentations" in English and Japanese (年会 開催報告); JSSSPN, Geological Society of
  Japan and the Meteorological Society publish 講演件数 in their kaiho/news PDFs.
- **Chinese society news pages** (cgs.org.cn, cms1924.org, csoe/CSES, cgu 年会 pages): the count
  appears in the post-meeting news item (论文/报告 N 篇, 参会 N 人) — Chinese query, open the page.
- **Brazilian anais**: SBG (CBG anais site per edition), SBCS (eventos), SBGf, CBMET — one
  proceedings/anais page or PDF per edition, trabalhos countable.
- **Society "by the numbers" / final reports**: SEG IMAGE technical program stats, ESA Living
  Planet Symposium programme page, AOGS annual meeting reports, congress circulars stating
  "N abstracts received" — open the page, never trust the snippet.

## Hard rules — these are refusals, not preferences

- **Every number needs an exact-page clickable URL.** Not a homepage, not a search-results page.
- **NEVER write a figure you only saw in a search snippet.** Open the page.
- **Invited speakers are NOT counted.** Contributed orals + posters only.
- **A stated total NEVER beats a countable artefact.** Count the artefact; note the stated figure
  as a disagreement.
- Any rung-1/2/7/8 figure must **state whether it includes invited talks**, or say unknown.
- **Cap: 3 web searches per conference for the abstract ladder, hard.** Zero-search rungs unlimited.
- **Rung 5 (browser) is RESERVED to the orchestrator.** Cloudflare/403/JS pages (Confit, Esri,
  Swapcard-type planners): return `NEEDS_RUNG_5`, name the exact page, move on. Try a browser
  user-agent with `curl` first.
- **Absence of evidence is NEVER evidence a meeting is small.** No figure → `UNRESOLVED` with the
  exact next action named. Never `OUT` on an empty search.
- **Attendance is not the unit.** PDAC's ~30,000 and Esri UC's ~18,000 are trade/vendor headcounts;
  the contributed-science count decides, and a giant expo with 300 papers is OUT.

## Traps specific to this queue

- **The IUGG family double-counts itself.** IUGG General Assembly (every 4 years) is the JOINT
  meeting of its associations (IASPEI, IAVCEI, IAGA, IACS/IAMAS/IAPSO…), which also hold their own
  assemblies between — sometimes jointly in pairs (IAGA-IASPEI 2025 is ONE meeting). Count each
  series once; a joint edition is one meeting; say in Method which editions you counted.
- **Joint editions in Latin America**: the Latin-American soil congress is periodically held WITH
  the Argentine national one — a joint year counts once; flag `duplicate_of` if your row's latest
  edition is a joint one.
- **Mergers**: SEG IMAGE (row 19) is the post-2021 merger of the SEG Annual Meeting and AAPG ACE —
  see the note on the queue row; set `duplicate_of` as instructed there.
- **Acronym collisions**: IGC = geological ≠ grassland ≠ geographical; ISC, ICG, IPC, ESC, IMS,
  IAC all collide with rows on other fields' sheets. **Confirm the society's own domain before
  citing any page.**
- **AGU, EGU and AMS (American Meteorological Society) are already counted on the physical-sciences
  sheet.** If a row turns out to be "held within AGU/EGU/AMS" or a section of them, flag
  `duplicate_of` rather than counting it.
- **Trade/policy events in the queue** (if reached): PDAC, Esri UC, INTERGEO, World Water Week are
  expected CURATED/trade — the abstracts bar and character judgement decide, not the headcount.

## Then rung 9 — run it in full on every row the abstract ladder did not settle

Rung 9 converts a **sourced attendance figure** into an approximate abstract count.

1. **Find attendance** on the A-ladder, first rung that yields with a basis: A1 exhibitor/sponsor
   prospectus (energy/geoscience expos publish these routinely) → A2 post-meeting report → A3
   press release / trade press → A4 venue / convention bureau → A5 programme-platform artefact
   (**browser-only: return `A5` with a null figure**) → A6 proxy arithmetic (flag it) → A7 prior
   year / sister meeting. **Cap: 2 searches per row, 3 for a hard one.**
2. **Tag the basis**: `DELEGATES` / `TOTAL_ONSITE` / `TOTAL_INC_VIRTUAL` / `UNSPECIFIED`. Discount
   only people who cannot submit at all (exhibitor staff, expo visitors) and say if you did.
3. **Judge the programme character**: `CONTRIBUTED` / `CURATED` / `HYBRID` / `UNKNOWN` — the
   strongest signal is an open call for abstracts.
4. **Judge the ratio for THIS conference** — no default ratio. `ratio` as a decimal,
   `ratio_rationale` explaining what about *this* meeting puts it there (a geoscience union meeting
   is mostly presenters; a mining investment convention is not). **A ratio without reasoning is
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
`VERIFIED`.

## Cadence

`Events/yr` is EMPTY for every row: return it (1 annual, 0.5 biennial, 0.33 triennial, 0.25
quadrennial — this queue is full of quadrennials: IGC, IUGG, INQUA, WCSS, IHC, IUFRO run 0.25–0.2)
with `cadence_evidence`. A world congress is very often not annual — verify every cadence.

## Output — checkpoint after EVERY row

Queue: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/earth/wave1/queue_1.json`.
Results: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/earth/wave1/results_1.json` — a
JSON list, **rewritten in full after every single row**. Also rewrite
`/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/earth/wave1/STATUS_1.json` as
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

## Finish by reporting — this report becomes `field-notes/earth-sciences.md`

1. A compact table (row / conference / abstracts / rung / verdict), total searches used.
2. **Every route that worked**, with the URL pattern and what it yields (Copernicus programmes,
   USRA/LPI archives, Acta Horticulturae sums, abstract books and their ID patterns, news pages in
   which language …).
3. **Every route that failed**, with the wall you hit (Cloudflare, JS, paywall, 202-empty).
4. **Counting rules this field needs** (union/association assembly families, joint editions,
   quadrennial cadences, per-volume Acta sums).
5. **Traps**: acronym collisions, expo-vs-congress headcounts, umbrella/union meetings.
6. Duplicate rows you spotted, and which rows you were least sure of.
