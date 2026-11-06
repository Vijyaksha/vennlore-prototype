# Social Sciences & Education Phase 2 — wave 1 brief (30 rows, one agent — THE PILOT for this field)

You are running **Phase 2 of the conference census** on a slice of 30 social-science and education
conferences, including **rung 9 in its entirety**. Follow the written method exactly.

**You are the pilot.** No `field-notes/social-sciences.md` exists yet — the orchestrator will write
it from what you find. So your final report matters more than usual: every platform, index, URL
pattern, counting rule and trap you hit is what the later waves will run on.

## Read these documents first, IN FULL — they govern everything

1. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md`
2. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/engineering.md` — the
   closest recent pilot: how zero-search routes carry a field, society libraries, national platforms.
3. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/life-sciences.md` — the
   per-abstract Crossref route, Confex `/Paper` API, PDF double-extraction.

## BLIND RUN — do not read any prior research results

Every figure must come from **your own primary-source research this session**. Do **not** open,
search for, or reuse any results, queue, plan, names or status file other than your own queue —
nothing under `scratchpad/` except `scratchpad/soc/wave1/queue_1.json`, and never the workbook
`docs/business/tam-sam-som-v3.xlsx` or any `BACKUP_*.xlsx`. If you encounter such a file anyway, do
not use it and say so. An honest `UNRESOLVED` is worth far more than a copied figure.

## Scope and language

Global. **The local-language rule applies**: Japanese (大会/総会 + 発表件数/演題数/プログラム),
Chinese (学术年会 + 论文/报告数/参会), Korean (연차학술대회 + 논문/발표), German (Kongress/Tagung +
Beiträge/Vorträge), French (congrès + communications), Spanish/Portuguese (congreso/congresso +
comunicaciones/trabalhos/anais/resúmenes). At least one query in the society's language before a
row is `UNKNOWN`; Method must name the language searched.

## Your job, per row

Find the number of **accepted contributed presentations** in one edition — invited/plenary/keynote
excluded, exhibitor and sponsor sessions excluded, withdrawn excluded. Work the ladder in order,
stop at the first rung that yields, and **credit the rung that PRODUCED the figure**.

**THE PANEL RULE (Rupert, settled 2026-09-12, decisive in THIS field):** social-science programmes
are built from panels/organised sessions, not posters. **Each paper inside a panel or session
counts as ONE presentation** — a panel carrying five papers counts as five, not one. Count papers,
not sessions; roundtables and author-meets-critics with no submitted papers are not contributed
presentations.

**Rungs 3–6 cost ZERO searches and are where most real figures come from.** If you identify an
artefact, **COUNT IT** — naming the next rung without climbing it is an unfinished row.

### Zero-search routes to try FIRST in this field (mostly unproven — you are proving them)

- **Crossref proceedings containers.** AERA deposits its whole programme ("Proceedings of the 2025
  AERA Annual Meeting" — a phase-1 hint says 4,676 items); IATED deposits ICERI/EDULEARN/INTED
  (proven order-of-magnitude 1,250–1,700 each). Shape:
  `https://api.crossref.org/works?filter=type:proceedings-article,from-pub-date:<Y>-01-01,until-pub-date:<Y>-12-31&query.container-title=<title>&rows=0&facet=container-title:*`
  — read the facet, cite the API URL and the container names you summed.
- **All Academic** (`convention2.allacademic.com/one/<org>/<org><yy>/`) backs AERA, ASA sociology,
  ICA, NCA, AEJMC, ASC, MPSA, ISA int'l studies, APSA and more. The public "browse by session type /
  index" pages are plain HTML and countable; per-unit ID patterns grep well. If it 403s, that is
  rung 5 — say so.
- **Confex** backs some US societies here too: try
  `<society>.confex.com/<society>/<meeting>/meetingapi.cgi/Program` (JSON; sum `ChildList_Paper`).
- **Society programme/abstract PDFs** (JPA 日本心理学会, DGPs, DGS, ECPR, EEA-ESEM): download, count
  unique IDs (`grep -oE '<pattern>' | sort -u | wc -l`), extract with BOTH `pdftotext -layout` and
  `-raw`, record the ID pattern.
- **ConfTool instances** (`conftool.com`/`conftool.pro` subdomains — ECER, ECPR, many European
  congresses): the public "browse contributions" listing paginates and counts.
- **Brazilian anais platforms**: Realize Eventos (`editorarealize.com.br` — CONEDU anais list every
  trabalho), ANPEd/ANPOCS/SBS post trabalhos-aprovados lists per GT (working group) — sum the GTs.
- **"By the numbers" / post-congress press releases**, often in the society's own language
  (中国心理学会 news pages state 参会/报告 counts; 한국심리학회 뉴스).
- **ASSA/AEA**: the preliminary program (`aeaweb.org/conference/`) lists every session with papers —
  countable; state sessions × mean papers only as a DERIVED floor if a full count is impractical.

## Hard rules — these are refusals, not preferences

- **Every number needs an exact-page clickable URL.** Not a homepage, not a search-results page.
- **NEVER write a figure you only saw in a search snippet.** Open the page.
- **Invited speakers are NOT counted.** Contributed papers + posters only. The panel rule above.
- **A stated total NEVER beats a countable artefact.** Count the artefact; note the stated figure
  as a disagreement.
- Any rung-1/2/7/8 figure must **state whether it includes invited talks**, or say unknown.
- **Cap: 3 web searches per conference for the abstract ladder, hard.** Zero-search rungs unlimited.
- **Rung 5 (browser) is RESERVED to the orchestrator.** Cloudflare/403/JS pages: return
  `NEEDS_RUNG_5`, name the exact page, move on. Try a browser user-agent with `curl` first.
- **Absence of evidence is NEVER evidence a meeting is small.** No figure → `UNRESOLVED` with the
  exact next action named. Never `OUT` on an empty search.
- **Attendance is not the unit.** AERA's 14,000 attendees say nothing until the paper count is
  found; a practitioner convention with 400 contributed papers is OUT however huge its expo.

## Traps specific to this queue

- **Acronym collisions are worse here than in any other field.** ASA = sociology, NOT anesthesiology
  / acoustics / agronomy / American Studies; ISA = int'l studies AND sociology (two different
  societies, both real); APA = psychological, NOT psychiatric (medicine) nor Asian Population; AAS,
  SRA, ICA, ESA, BPS, AHA, ECE, ECP, IEA all collide with rows on other fields' sheets. **Confirm
  the society's own domain before citing any page.**
- **Practitioner conventions** (NCTM-type) are often CURATED/workshop-built: check whether an open
  research call exists and how big the contributed share is — the character judgement decides.
- **Same society, different meetings**: ISA World Congress vs ISA Forum (both quadrennial, offset);
  IATED's ICERI/EDULEARN/INTED are three separate meetings a year. Never merge them; never
  double-count one as the other.
- **JSM and ASSA are umbrella meetings** of many associations — the umbrella figure is the row's
  figure, but flag it as an umbrella in the notes.

## Then rung 9 — run it in full on every row the abstract ladder did not settle

Rung 9 converts a **sourced attendance figure** into an approximate abstract count.

1. **Find attendance** on the A-ladder, first rung that yields with a basis: A1 exhibitor/sponsor
   prospectus (US education/psychology conventions publish these routinely) → A2 post-meeting
   report → A3 press release / trade press → A4 venue / convention bureau → A5 programme-platform
   artefact (**browser-only: return `A5` with a null figure**) → A6 proxy arithmetic (flag it) →
   A7 prior year / sister meeting. **Cap: 2 searches per row, 3 for a hard one.**
2. **Tag the basis**: `DELEGATES` / `TOTAL_ONSITE` / `TOTAL_INC_VIRTUAL` / `UNSPECIFIED`. Discount
   only people who cannot submit at all (exhibitor staff, expo visitors) and say if you did.
3. **Judge the programme character**: `CONTRIBUTED` / `CURATED` / `HYBRID` / `UNKNOWN` — the
   strongest signal is an open call for papers/abstracts.
4. **Judge the ratio for THIS conference** — no default ratio. `ratio` as a decimal,
   `ratio_rationale` explaining what about *this* meeting puts it there (an academic congress built
   on submitted panels is majority-presenter; a teachers' convention with an expo floor is not).
   **A ratio without reasoning is rejected.**
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
quadrennial for the world congresses; SRCD/EARLI-type biennials are 0.5) with `cadence_evidence`.

## Output — checkpoint after EVERY row

Queue: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/soc/wave1/queue_1.json`.
Results: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/soc/wave1/results_1.json` — a JSON
list, **rewritten in full after every single row**. Also rewrite
`/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/soc/wave1/STATUS_1.json` as
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

## Finish by reporting — this report becomes `field-notes/social-sciences.md`

1. A compact table (row / conference / abstracts / rung / verdict), total searches used.
2. **Every route that worked**, with the URL pattern and what it yields (All Academic browse pages,
   Crossref containers, ConfTool listings, anais platforms, programme PDFs and their ID patterns …).
3. **Every route that failed**, with the wall you hit (Cloudflare, JS, paywall, 202-empty).
4. **Counting rules this field needs** (the panel rule in practice, GT/working-group sums,
   umbrella meetings, biennial world congresses).
5. **Traps**: acronym collisions, practitioner-convention character, same-society sister meetings.
6. Duplicate rows you spotted, and which rows you were least sure of.
