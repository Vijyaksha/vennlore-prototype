# Earth, environmental & agricultural sciences Phase 2 — wave brief (37 rows, one agent)

You are running **Phase 2 of the conference census** on a slice of 37 Earth, environmental & agricultural sciences conferences,
including rung 9 where the abstract ladder fails. This is a post-pilot wave: the field's routes
are already mapped — your job is throughput at the same evidence standard.

## Read first (this is the whole reading list)

1. `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/earth-sciences.md` — the field notes from this field's pilot: every route that worked with
   its URL pattern, every wall, the counting rules and traps. **These replace route discovery —
   try the matching route from the notes before anything else.**
2. The binding-rules digest below. Do not re-read documents between rows.

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


## BLIND RUN — do not read any prior research results

Every figure must come from your own primary-source research this session. Nothing under
`scratchpad/` except your queue, and never the workbook `docs/business/tam-sam-som-v3.xlsx` or any
`BACKUP_*.xlsx`. If you encounter such a file anyway, do not use it and say so. An honest
UNRESOLVED is worth far more than a copied figure.

## Pace — streamlined, not diluted

- Queue rows may carry `route_hint` (a known artefact or container for this meeting). Hints order
  the work and are NEVER evidence — open and count the artefact yourself.
- Batch a row's independent downloads into one command.
- **CRAWL BUDGET — defer bulk counts, never drop or guess them.** If counting an artefact would
need more than ~40 fetched pages (a 500-session programme, a paginated archive), do NOT crawl it
inline. Record outcome NEEDS_BULK_COUNT with the exact counting plan — the URL pattern, the page
range, the ID pattern to grep, the stated total if the site shows one — reproducible from your
text alone, then move to the next row. The orchestrator runs the bulk count in parallel. A capped
crawl you did run still gets its count written normally.

- **Soft timebox ~8 minutes of wall clock per row**: past it, write the trail (rungs tried, the
  named artefact, the exact next action) and move on — UNRESOLVED with a next action beats a
  stalled queue. Never trade the timebox for a lower-quality figure: a slow counted row beats a
  fast quoted one.

## Traps for this queue

- **Field notes are your first stop**: `pub.confit.atlas.jp/en/event/<slug>/search?f=&t=presentation` (Japanese meetings — note: curl gets 202/zero bytes, so it is NEEDS_RUNG_5 unless a mirror exists; J-STAGE volume totals work with curl), Copernicus static per-abstract pages, IUGG annual reports, Crossref container facets, society WordPress media APIs (`/wp-json/wp/v2/media?search=program`), government mirrors for Chinese societies.
- **IUGG family**: rows 9/10/11/58/61/62 are association assemblies. IUGG GA (row 8) is already counted. Count each association's own series once; a joint assembly (IAGA-IASPEI 2025, IACS-IAMAS-IAPSO 2025) is ONE meeting.
- **Already counted elsewhere — flag `duplicate_of`, do not count**: AGU, EGU, AMS (physical sciences); AAPG ACE / SEG IMAGE (engineering r188 / earth r19); Aquaculture America & WAS Triennial (row 100); EPSC-DPS joint years count once (rows 22/23).
- **IMPLIED NAME rows** (Chinese/Korean societies): first resolve the real meeting name; if no real recurring meeting exists, say so (outcome UNKNOWN, verdict UNRESOLVED, method explains) — never invent one.
- **Acronym collisions**: IGC = geological ≠ grassland ≠ geographical; ISC, ICG, IPC, ESC, IMS, IAC, SEG, CGS, CBG all collide. Confirm the society's own domain before citing.
- **Trade/policy events** (WFC, ASSW, Adaptation Futures, World Water Congress): the abstracts bar and programme character decide, never the headcount.
- **Cadence**: Events/yr is EMPTY on every row — return it with evidence. Many rows are 0.25 (quadrennial), 0.33, 0.5, 0.2 (IUFRO-style five-yearly), ~0.1 (WCRP decadal), 2 (twice-yearly Japanese societies: report the larger edition, events_per_yr=2).
- **Rung-9 anchors for this field** (from counted wave-1 rows, presentations per attendee): IUGG 89%, AOGS 106%, INQUA 89%, IUFRO ~80%, CBCS 65%, IGC 46%, Aquaculture ~33% (trade hybrid), ICUC 111%. Judge THIS conference's ratio from its own programme wording; name the anchor you reasoned from in `ratio_rationale`; never copy a ratio across.
- Wayback may be offline; DNS failures are not rung 5; password-protected PDFs are not rung 5; credential walls (C-IN portals) are not rung 5.
## Routes and traps learned tonight (wave A, 2026-09-15) — additions to the field notes
- **Dype Soluções platform** runs many Brazilian society congresses (CFP, ANPUH, ANPOCS, RBA, SBS): `/atividade/programacao` (whole programme) and `/atividade/hub/<track>`; papers are `<p class="m-4">` on consolidated pages — but consolidated pages can PAD (ANPOCS 423 vs 357 on detail pages): verify on detail pages.
- **Realize Eventos** (CONEDU, ENDIPE): schedule table carries `data-ajax-url=".../base/api/divulgacoes/trabalhosAlocados"` returning every session with its works (open JSON).
- **Confex is alive** for SSWR, MLA, ISA (`<host>/<meeting>/meetingapi.cgi/Paper`, `--compressed`) — probe the host before assuming a society left it.
- **All Academic**: APPAM's instance issues a guest session and browse pages render to curl; AEJMC/APSA/ASA/ASC/MPSA still serve the reCAPTCHA stub. AEJMC publishes accepted abstracts as an .xlsx on its Higher Logic S3 bucket.
- **WebFetch clears some Cloudflare walls curl cannot** (federationhss.ca, igc2024dublin.org) — try it before declaring rung 5; it did not help on SBL/ACSP/plantprotection.org.
- **Oxford Abstracts**: `/event/<id>/titles` states the total submissions; `apigw.oxfordabstracts.com/services/program-pdf?event_id=<id>` serves the programme PDF unauthenticated (sessions only).
- **C-IN portals** (czech-in.org cmPortalV15): the guest 'Abstract List' states the total (browser only).
- **MiraSmart** (AAS/DPS): two-step cookie handshake (fetch Itinerary/ with a jar, then EventsAAG.aspx with the jar) yields the full server-rendered programme.
- **WAS abstract books**: `wasblobstorage.blob.core.windows.net/meeting-abstracts/<CODE>AbstractBook.pdf` — HEAD tells you which editions exist.
- **Unwalled WordPress mirrors** of Cloudflare-blocked societies exist (mineralogy-ima-wordpress.website); WordPress REST APIs may live at `/api/` instead of `/wp-json/` (IAVCEI). Media API `?search=` works where `mime_type=` returns 400.
- **Programme data as a JS literal** (`EMBEDDED={...}`, ESC 2026) — a text extractor sees an empty page; grep the HTML for JSON.
- **Google Drive public folders** list via `drive.google.com/embeddedfolderview?id=<id>#list`; files via `drive.usercontent.google.com/download?id=<id>&export=download&confirm=t` (content-type octet-stream).
- **Crossref**: member+year faceting beats container filters (comma in a container title breaks the filter; `container-title` arrays double-count SGEM). Container filters need the exact string.
- **Copernicus title discriminator varies**: EPSC2026/EPSC-DPS2025 title `Abstract <SLUG>-<n>`; EPSC2022/ICG2022 title every page `CO Meeting Organizer <SLUG>` and the discriminator is HTTP 200 vs 302. Test a known-good and known-absent id first.
- **Dead domains that return HTTP 200**: Wayback-downloader demo stubs (suelossantacruz2025.com), domain-broker sale pages (ippcathens2024.gr, sociedadgeologicamexicana.org.mx), gambling squatters (sbagro.org→olxbaut.com, icme15.org), empty documents (cbagro2025.com.br content-length 0). Check the body, never the status.
- **Credential walls are not rung 5**: Ex Ordo event spaces 'restricted to registered delegates' (RGS-IBG), eventi.unibo.it (IAG), IPSA library. **reCAPTCHA v2 is a human wall** (ABAI).
- **Wayback / Internet Archive** was HTTP 503 all night — do not build a route on it.


## Output — checkpoint after EVERY row

Queue: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/earth/wave4/queue.json`.
Results: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/earth/wave4/results.json` — a JSON list, rewritten in full after every single row. Also rewrite
`/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/earth/wave4/STATUS.json` as
{ "rows_done": n, "rows_total": 37, "searches_used": n, "in_flight": "<conference>" }
after every row.

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
