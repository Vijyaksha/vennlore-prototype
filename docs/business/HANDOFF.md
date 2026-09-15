# HANDOFF — conference census

State of play for the next session. The method lives in `census-methodology.md` (general, all
fields) and `field-notes/<field>.md` (field-specific). This file is only where we stopped.

## Where we stopped — 2026-09-14 evening (social sciences + earth sciences PILOTS RUNNING)

**Rupert gave the phase-2 go for both new fields this session.** The plan he set, then AMENDED
mid-session: pilot wave of 30+30 (RUNNING as of 16:04), then a 4-agent wave of 120 and a 7:30 pm
scheduled run for the rest — **both of those follow-ons were CANCELLED by Rupert ("cancel it —
the follow-on"). No cron exists.** After the pilots: orchestrator does rung-5/bulk counts,
intake-validates, writes back, writes both field-notes files, reports, and STOPS. The remaining
rows stay `NOT YET CENSUSED` for a future session. His other calls this session: **move APA/APS
from life to social** (done), census agents ALWAYS on Opus, and **streamline the process without
lowering the evidence bar** (see `scratchpad/streamline.py`).

### FINAL STATE (2026-09-14 ~20:45) — both pilots COMPLETE and WRITTEN BACK

- **Both pilots finished 30/30** (a usage-limit pause 18:35–19:42 cost nothing — per-row
  checkpoints held and both resumed by mailbox message). Social: 10 searches; earth: 11.
- **Workbook written and committed** (earth f7aa26a, social 6810257): social sheet 18 VERIFIED
  (16.25 ev/yr) + 13 BORDERLINE (10.25) + 166 NOT YET CENSUSED; earth sheet 7 VERIFIED (4.2) +
  14 BORDERLINE (9.24) + 95 NOT YET CENSUSED. Totals recomputed from cells.
- **Orchestrator rung 5, all cleared**: ICA 3,541 (ICA25 Abstract Program PDF); DGPs 1,686
  (Converia day pages, double-extraction exact); EEA-ESEM 1,093 contributed (Cloudflare-cleared
  pager, 353 session pages); JpGU 5,412 platform count via `pub.confit.atlas.jp/en/event/<slug>/
  search?f=&t=presentation` (route unlocks every Confit meeting); NCTM is login-walled → resolved
  on the agent's rung-9 attendance.
- **Intake decisions on record**: Chinese Geophysical Society parked as duplicate of CGU (same
  co-organised meeting, identical 3,922); IUGG raised to VERIFIED for consistency with CGU (both
  itemised published counts, KCS precedent) — **Rupert may demote both together if VERIFIED must
  mean strict artefact counts**; implied APSA (Asia-Pacific Sociological) parked on non-existence.
- **RATIFIED BY RUPERT (2026-09-15, "for all of the decisions, you can just keep them")** — all
  four open flags are now settled as written, do not re-open: (1) IUGG and CGU STAY VERIFIED on
  itemised published counts (the KCS precedent stands as tier policy); (2) SEG IMAGE (earth,
  BORDERLINE) and engineering r188 (AAPG ACE, DATED 2019) BOTH stay — Rupert accepts the known
  merger overlap; (3) NCTM stays BORDERLINE on the rung-9 ~840; (4) JSM, AAR and CONIC stay on
  Census - Social Sciences where the pilot placed them.
- **Both field-notes files are published** (pilot report + orchestrator addenda):
  `field-notes/earth-sciences.md` and `field-notes/social-sciences.md`. The soc pilot could not
  write files (subagent harness guard), so its report travelled as 16 chunked messages and was
  reassembled verbatim into `scratchpad/soc/wave1/REPORT.md`; the field-notes copy carries three
  marked verdict corrections (EEA-ESEM BORDERLINE; ICA and DGPs VERIFIED at rung 5).
- **Deferred retry queue (no verdict changes)**: PAA's 981 unlisted posters, JPA Confit cross-check,
  KPA oral tracks, ICME via Wayback (Archive down all run). Boundary rows for deliberate assignment:
  JSM, AAR, CONIC. New phase-1 lead: Pacific Sociological Association (pacificsoc.org).

### What this session did before launching (all committed)

1. **Sheets built and loaded** (commit cd8fb18): `Census/Deleted - Social Sciences` (197 live + 3
   parked dupes) and `Census/Deleted - Earth Sciences` from the two phase-1 names.json files via
   `chemlib.build_field` + new `scratchpad/fieldload.py` (tested). APA Convention (VERIFIED 2,976)
   and APS Convention (BORDERLINE 1,350) MOVED from life rows 91/92 to social rows 202/203; move
   verified neutral by recomputing totals from cells (life 7.0/40.25 → 6.0/38.25).
2. **Dedupe sweep, Rupert-ordered** (commit ec5bdcf): fuzzy scan (tokens+acronyms+society) within
   and across ALL sheets. Parked as already-counted: ASHA (med r234), TRB (eng r79), ECSS sport
   (med r157), IAGG (med r148), and on earth IGC-geography + AAG (geography counted once, on
   social r92/r14). ~25 acronym lookalikes checked by society and KEPT (ASA×4, ISA×2, APA×3,
   ICA×3, IGC×3, ISC×3, AAS, BPS, ESA, SRA…). Live rows after: **social 196, earth 125** to census.
3. **`scratchpad/streamline.py`** (commit 29fa781, tested): post-pilot protocol — reading diet
   (own field notes + BINDING_DIGEST instead of ~55k tokens of docs), route hints in queues
   (hints ≠ evidence), crawl budget (>~40 pages → `NEEDS_BULK_COUNT` + exact counting plan,
   orchestrator bulk-counts), batched downloads, soft ~8-min/row timebox (trail + UNRESOLVED,
   never a lower-grade figure). `build_wave_brief()` generates slim wave briefs. Both pilots got
   measures 1–4 (sans reading diet) by mid-run message at ~15:40 — pace went from ~10 to ~2-3
   min/row. Cost note (Rupert asked): downloads/grep counts are nearly free (bash-side); the
   compute sinks are context size and per-row tool round-trips; next levers if wanted =
   index-scripting whole slices (DBLP/CCS pattern) and ~15-20-row agent slices.

### Orchestrator TODO once pilots return (the stopping work of THIS session)

1. **Rung-5 + bulk-count queues** (browser is orchestrator-only): the NEEDS_RUNG_5 /
   NEEDS_BULK_COUNT rows, each carrying the exact page or counting plan.
2. **Intake flags already spotted**: (a) Chinese Geoscience Union AND Chinese Geophysical Society
   both returned 3,922 — CGU's meeting is co-organised by the Geophysical Society, almost
   certainly ONE meeting on two rows; adjudicate before writing. (b) SEG IMAGE 611 BORDERLINE —
   check whether that is a floor/partial count; IMAGE is the post-2021 SEG+AAPG-ACE merger and
   **engineering r188 holds ACE's DATED 2019 count (914) — Rupert decides whether r188 retires**.
   (c) Verify no rung-2 stated total got VERIFIED.
3. **Writeback** through `scratchpad/apply_wave.py` (wavelib.plan + tested writers), one run per
   field (`--sheet "Census - Social Sciences" --deleted "Deleted - Social Sciences"`, same for
   Earth); r5_notes.json / dupes.json / events_override.json per wave dir; totals recomputed from
   cells; commit before and after.
4. **Field notes**: write `docs/business/field-notes/social-sciences.md` and `earth-sciences.md`
   from the pilots' six-section reports (report is the body, orchestrator adds addenda).
5. Update the methodology status table + this file, then STOP (no wave 2, no cron — cancelled).

**Remaining after the pilots: social 166, earth 95 `NOT YET CENSUSED`.** Budget: cap 1000
confirmed live; ~12 searches used by this session so far. Tests: 117 green (`test_fieldload.py`,
`test_streamline.py` new). The 2026-09-14-afternoon section below is superseded by this one.

## Where we stopped — 2026-09-13 (life sciences)

**Rupert's direction this session: "We're going to the life sciences now."** Chemistry phase 2 is
parked mid-way (see the 2026-09-12 section below, which is still accurate for chemistry, medicine and
physical sciences except where this section says otherwise).

### THE NEXT SESSION DOES THESE, IN ORDER (Rupert, end of 2026-09-13)

**What this session did, in one paragraph.** Finished the US life-sciences census (90 rows, three
agents, rung 5 by the orchestrator; 7 VERIFIED / 38 BORDERLINE / 101 deleted). Ran a global
English-language life-sciences phase 1 (732 names, not loaded; a 74-row shortlist is on disk).
Compared the 900 floor against a 500 floor across the whole workbook; Rupert kept the bar
(VERIFIED ≥1,500, floor ~900 with the 800 leeway). Built `Census - CS & Engineering` from DBLP's
SPARQL endpoint plus Crossref's proceedings index — 62 live rows (18 VERIFIED, 44 BORDERLINE) and 4
deleted — with tested code (`scratchpad/dblplib.py`, `scratchpad/cs/build_cs_sheet.py`). Workbook-wide
there are now **367 conferences at or above 800 abstracts (197 at or above 1,500)** across five
fields; medicine is just under half. All of it is UNCOMMITTED.

**UPDATE 2026-09-14 — steps A and B below are DONE; the sheet was split; phase 2 is next.**
Committed (9ee4309). Rupert then split the field: `Census - CS & Engineering` became
`Census - CS & AI` (31 rows: 13 VERIFIED, 18 BORDERLINE; 1 deleted) and `Census - Engineering`
(31 rows: 5 VERIFIED, 26 BORDERLINE; 3 deleted) via `scratchpad/split_field.py` (rows blanked in
place, totals ranges untouched, totals reconcile). Two Opus phase-1 agents ran in parallel,
English-language, no target count ("return what you can stand behind"), clean input dirs:
- **CS & AI** — `scratchpad/cs/p1_csai/` (BRIEF, `names.json` 31 names, REPORT). 46 searches, all
  sweeps saturated. DBLP exhausts the field; the journal-first vein is empty. Strongest: JSAI
  (1,186 presentations 2025), IPSJ National Convention (~1,200), SIAM CSE, IC2S2. Weakest: CSI
  India (implied), CNCC/CCIG (forums mostly invited), FCRC/WCCI (sum of tracks already counted —
  drop). INFORMS and Sunbelt fell between fields — Rupert to assign (suggest INFORMS → Engineering).
- **Engineering** — `scratchpad/eng/p1/` (BRIEF, `names.json` 136 names, 81 boundary, 9 implied,
  REPORT). 49 searches, saturated in English. Most confident: TRB, AIJ, JSCE (3,000+ papers), IEEJ,
  IEICE, ASME IMECE (~2,400), IAC (~6,400 abstracts), INFORMS, WCEE, CCTAM, WCCM, ECCOMAS, ISPRS
  (1,500+), KSME (1,400+), KIEE, ASEE, CIGRE, CIRED, JIM, EUROMAT. Take last: NASCC, ACI, ISARC,
  ASCE ICTD, SAE COMVEC, FEDSM, PCIM, OTC, URTeC, IPTC, PES GM (~800 papers), WEFTEC. China is the
  big local-language gap (societies run technical-committee meetings, not one congress; CAST's 118
  forums is the door); Confit (JP), DBpia and AURIC (KR) index society volumes and would give exact
  counts. Rupert's prior: engineering ends near 200 at the bar; orchestrator's: 100–150.
- **OVERNIGHT 2026-09-14 (Rupert asleep; his instruction: CS phase 2 + engineering waves 1–2 now,
  a 5 am Eastern wakeup finishes the remaining engineering rows across three agents).** Both lists
  were loaded as `NOT YET CENSUSED` (CS & AI rows 68–97, 30 rows — Sunbelt not loaded; Engineering
  rows 70–205, 136 rows) with `scratchpad/append_names.py`. Writeback for every wave runs through
  `scratchpad/apply_wave.py` over `wavelib.plan` (tested) + the tested writers; per-wave override
  files `r5_notes.json` / `dupes.json` / `events_override.json` sit in each wave dir.
  - **CS & AI phase 2 — DONE** (`scratchpad/cs/wave1/`, 30 rows, 4 searches). Sheet now 14 VERIFIED
    (12.5 ev/yr) + 25 BORDERLINE (22.74); deleted 22 OUT + INFORMS parked (it is on Engineering).
    New: IPSJ National Convention 1,608 VERIFIED; JSAI 1,174, SIAM CSE 1,433, FOSDEM 989, COLM 856,
    KCC 854, FCRC 856 (one federated week, 0.25/yr — Rupert's call) BORDERLINE; CSI India UNRESOLVED.
    ANLP Japan OUT by 3 (797) — restorable. WCCI parked as a sum of IJCNN + CEC + FUZZ. Field notes
    `field-notes/cs-ai.md` carry a dozen new zero-search routes. **CS & AI is closed** at the
    English + JP/CN/KR level.
  - **Engineering wave 1 — DONE** (`scratchpad/eng/wave1/`, 30 rows, 10 searches; pilot report in
    `REPORT.md`, now the body of `field-notes/engineering.md`). Wave 2 — DONE (`eng/wave2/`, 29
    rows, 5 searches). Sheet now **18 VERIFIED (14.33 ev/yr) + 58 BORDERLINE (50.99 ev/yr) + 76
    NOT YET CENSUSED**; `Deleted - Engineering` 18 rows. Rung 5 by the orchestrator (Playwright):
    IEICE General 1,784 / Society 1,111, JSME 1,252 (Confit; restored after an OUT on the J-STAGE
    floor — `scratchpad/restore.py`), JIM ≤1,161, EWRI 516 (OUT). Biggest finds: AIJ 6,645, INFORMS
    5,122 (2018), JSCE 4,188, IAC 4,008, WCEE 3,163, WCCM 2,800, ASEE 2,466, ECCOMAS 2,368, ISPRS
    2,306, IFAC 1,908, POMS 1,560, CIGRE 1,552.
  - **Wave 3 — DONE by the 5 am job** (`scratchpad/eng/wave3/`, 76 rows, three agents, 40 searches,
    nothing interrupted — the 4:30 am usage-limit reset held). 0 VERIFIED, 19 BORDERLINE, 57 OUT.
    Rung 5 by the orchestrator: ICTD 711 ceiling (OUT), CAST ruled OUT on programme character (990
    invited forum talks, the CNCC shape); WEFTEC left BORDERLINE (Swapcard planner needs a long
    browser session). **ENGINEERING PHASE 2 IS COMPLETE at the English + local-page level: 18
    VERIFIED (14.33 ev/yr) + 77 BORDERLINE (66.99 ev/yr) = 95 passing, 81.3 ev/yr; `Deleted -
    Engineering` 75 rows. Two kept rows rest on rung-9 inference (CFM, WM Symposia); every other
    pass is a counted figure.** The implied Chinese societies all resolved and all fell under the
    bar — the Chinese layer runs through technical-committee meetings and invited forums, so the
    deferred local-language pass is expected to add BORDERLINE rows only.
  - **Both fields together: 32 VERIFIED + 102 BORDERLINE = 134 passing, 116.6 ev/yr.** Rupert's
    prior of ~200 for engineering alone was not reached (95); the tail ran one pass in four.
  - **Searches used for the whole CS/engineering effort**: 95 (phase 1) + 59 (phase 2) ≈ 154 of 1,000.
  - **Rows for Rupert's eye** (all recorded in Method): FCRC as one meeting; ANLP 797, ISOPE 794,
    CBA 797, SHASE 775 (rising), SOFT 757 and IPTC 713 OUT by a handful of papers on exact counts;
    EU PVSEC 802 in by two; CAST ruled OUT on character (~990/yr if invited forum talks were ever
    admitted); ICTD ceiling; WEFTEC, ICASP/ICOSSAR, Indian Engineering Congress and CSI India kept
    BORDERLINE with no figure; INFORMS counting rule 6 (sponsored sessions
    counted; strict reading ~580 + posters); TRB 981 posters-only from 2017 (lectern track uncounted
    — AMOnline needs a browser login); IMECE deposit floor 723 vs ~2,400 stated; ICA 2025 was the
    joint ASA/ICA meeting (ASA is on physical sciences — count a joint year once); WCCM and ECCOMAS
    merge in alternate cycles (2026 joint); KSCE 1,053 (2024) vs 719 (2025); FEMS EUROMAT 1,446
    stated (1,635 if highlight talks count).
  - **Searches used tonight**: ~19 across four agents (phase 2) + 95 (phase 1) — of 1,000.

**2026-09-14 afternoon — two new fields discovered, NOT loaded, phase 2 awaits Rupert's go.**
Rupert chose the next two high-yield fields; one Opus phase-1 agent each, English-language, clean
input dirs with the 1,688-name exclusion list:
- **Social sciences & education** — `scratchpad/soc/p1/` (BRIEF, `names.json` **200 names**, 40
  searches, all sweeps saturated; 16 boundary, 5 implied). Confirmed giants from Crossref: AERA
  4,676, ICERI 1,756, EDULEARN 1,739, INTED 1,312, CONIC 1,125. The US flagships (AAG, APSA, ASA,
  AAA, ASC, ICA, NCA, PAA, SRCD, SPSP, ASSA …) and European mirrors are the expected VERIFIED rows;
  practitioner conventions (NCTM, NCTE, NAEYC, ISTE, ALA, NSTA) and the mid-size European societies
  are the doubtful tail. Business & management deliberately left for its own field. APA and APS
  (life sheet, boundary) should move here at load time. Japan/China/Korea seen only through English
  (Chinese Sociological Association: 100 forums, 3,700 participants; Chinese education bodies meet
  per branch).
- **Earth, environmental & agricultural sciences** — `scratchpad/earth/p1/` (BRIEF, `names.json`
  **127 names**, 58 searches, saturated; 105 boundary, 10 implied). Strongest: JpGU (4,600+
  presentations stated), AOGS (~4,000 participants), Chinese Geoscience Union, ESA Living Planet
  Symposium (6,500+ participants), ICUC (1,000+ abstracts), ESC General Assembly (~1,000), Congreso
  Geológico Chileno (900+). Trade/policy events (World Water Week, Esri UC, INTERGEO, PDAC) flagged
  for a contributed-share check; four checked near-misses kept as records (DBG 508, SBAgro 678, SGEM
  532, SBGf 712); a list of searched negatives is in the agent's report.
- **State right now**: phase 1 is FINISHED for both fields and nothing has been loaded onto the
  workbook — the 327 names (200 + 127) live only in the two `names.json` files. Rupert explicitly
  withheld the phase-2 go on 2026-09-14 ("no go-ahead for phase 2, just finish phase 1"); do not
  build sheets or launch agents until he gives it.

**THE PLAN FOR THESE ~300 NAMES (Rupert, 2026-09-14) — run it in this order when he says go:**

1. **Two domains, two sheet pairs.** `Census - Social Sciences` / `Deleted - Social Sciences` and
   `Census - Earth Sciences` / `Deleted - Earth Sciences`, built with `chemlib.build_field(names,
   duplicates, field)` (400 spare rows inside the totals ranges), every name loaded as
   `NOT YET CENSUSED`. At load: park APA Convention and APS Convention on the social deleted sheet as
   "already counted on Census - Life Sciences" (or move them across — Rupert's call), and set
   `why_listed` from each record's `why_plausibly_900` + `size_hint` + `boundary` flag.
2. **Pilot wave: ONE census-researcher agent per domain, 30 rows each**, phase 2 under
   `census-methodology.md` exactly as the engineering pilot ran (`scratchpad/eng/wave1/BRIEF.md` is
   the template: blind run, clean input dir holding only the queue, zero-search rungs first, cap 3
   searches per row, rung 5 back to the orchestrator, per-row checkpointing, the six-section report
   at the end because it becomes the field notes). Pick the 30 as a representative mix, not the 30
   easiest — US flagships, European mirrors, Asia/LatAm, world congresses, a few boundary rows — so
   the notes learn the field's routes. Writeback through `scratchpad/apply_wave.py`
   (`wavelib.plan` + the tested writers), totals recomputed from cells, commit before and after.
3. **Field notes from the pilot**: write `docs/business/field-notes/social-sciences.md` and
   `docs/business/field-notes/earth-sciences.md` in the chemistry/engineering pattern — scope and
   overlap table, the unit, routes that worked with verbatim URL patterns and grouping keys, routes
   that failed with the wall hit, counting rules, traps, rows for Rupert's eye. The pilot agent's
   report is the body; the orchestrator adds the addenda.
4. **The remaining ~260 names run as STAGGERED SCHEDULED phase-2 runs**, each wave carrying its
   domain's field notes in the brief. Rupert will explain the staggering (cadence, wave size, how
   many agents per run) to the chat agent when he starts it; the mechanics are the overnight
   pattern already proven on engineering — a session cron (`CronCreate`, one-shot, local time)
   that first checks every earlier wave for interruptions (compare each queue to its results file,
   resume on the same brief and output path if short), then launches the next wave, writes back,
   commits, and updates the field notes, this file and the status table. Pre-build the wave queues
   (`scratchpad/<field>/wave<N>/queue_<k>.json`) from the sheet's remaining `NOT YET CENSUSED` rows
   so each launch is one command. Keep the Mac awake (`caffeinate -i -s`) for the duration.

Expected yield, for calibration only: social sciences 80–150 passing (the US flagships and
European mirrors are the VERIFIED candidates; practitioner conventions and mid-size European
societies the doubtful tail); earth sciences 60–100 (105 of its 127 names are flagged boundary, so
expect one pass in three or four, as engineering's tail ran).

**CURRENT PLAN — Rupert's last instruction, supersedes the numbered order below where they differ:**

- **Step A. Commit** (step 0 below, unchanged).
- **Step B. CS & Engineering phase 1, second pass — Rupert suspects the 62 are not all of it.**
  DBLP and Crossref only see conferences whose proceedings are indexed; large engineering meetings
  that publish through society presses or not at all are invisible to both (ASME IMECE and
  Turbo Expo, ASCE, SAE WCX, TRB Annual Meeting, SPE ATCE/OTC, ASHRAE, IEEE PES General Meeting,
  ISSCC/IMS/IEDM if under-indexed, the national CS/engineering societies IEICE, IPSJ, JSAI, CCF,
  KIISE, VDI/VDE, IET, Engineers Australia, plus the big Chinese/Indian IEEE-section conferences).
  Run ONE Opus phase-1 agent (discovery is a saturation judgement — do not split it), **English-
  language searching**, target **60–70 new candidate names** that plausibly clear ~900 accepted
  presentations. Inputs it gets: the field-agnostic phase-1 rules in `census-methodology.md`, the
  chemistry phase-1 brief as a template (`scratchpad/chem/p1-BRIEF.md`), and an exclusion list of
  everything already known — the 66 rows on the two CS & Engineering sheets, every name on the
  other sheets (regenerate `existing_names.json` from the workbook), and the Crossref ≥300
  container list in `scratchpad/cs/dblp_probe/crossref_proc_2025.json` (already checked). Names only,
  over-include, `implied` allowed, ~60 searches. Output `scratchpad/cs/p1/names.json` + `STATUS.json`,
  written after every sweep.
- **Step C. Phase 2 on those 60–70 names**, cheapest rung first: for each name try DBLP SPARQL and
  the Crossref facet by exact title FIRST (zero searches; `dblplib` has the row builders), then the
  ordinary ladder for the rest (society proceedings, programme PDFs, Confex/eventScribe), rung 5 to
  the orchestrator, rung 9 last. Append the names to `Census - CS & Engineering` as
  `NOT YET CENSUSED` inside the totals range before writing figures; OUT rows to the deleted sheet.
- **Step D (later).** The 74-row life-sciences shortlist (step 1 below) and the engineering-society
  local-language sweep; Rupert has not scheduled these.

0. **Commit first.** This session's census work — the workbook, this file, `census-methodology.md`,
   `field-notes/life-sciences.md` — is in the working tree UNCOMMITTED. The "revert a bad write with
   `git checkout`" safety net does not exist until it is committed. Run the 75+ tests
   (`cd scratchpad && python3 -m pytest test_attlib.py test_chemlib.py test_pilotlib.py test_ccslib.py test_writeback.py test_dedupe.py -q`,
   99 green on 2026-09-13), then commit as `feat(census): life sciences US phase 2 wave 1 + global phase 1 list`.
   Also confirm `echo $CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` is ~1000 and spend one throwaway search.

1. **Close life sciences with a cheap positives-only pass, NOT a full census of the 732 names.**
   Rupert's read (agreed): the field's big meetings were already caught by medicine, the hit rate has
   fallen to ~5% of names, and the 434 implied placeholders will resolve small like RSEQ did. So:
   - Queue: `scratchpad/life/p1_global/shortlist.json` — **74 named meetings** picked by the
     orchestrator as the only plausible ≥900s (federation flagships such as FENS, FEBS/EMBO, ISME,
     ESEB, ICN, ESHG, HUPO, ICP; large national societies — MBSJ, JBS, Japan Neuroscience, JSI,
     JSPP, ESJ, CSCB, CSBMB, KSBMB, KSMCB, SBPC, SBBq, BES, VAAM, Microbiology Society UK …). Each
     record carries `shortlist_reason`. The other 658 names stay in `names.json`, unloaded.
   - Run: **one or two Opus `census-researcher` agents**, wave-1 brief pattern
     (`scratchpad/life/wave1/BRIEF.md`) with three changes: scope is GLOBAL and the local-language
     rule APPLIES (JP/CN/KR/PT rows — terms are in `p1_global/REPORT.md`); rule 1 is in force
     (positives only, `UNRESOLVED` after 2 searches is fine, never `OUT` on an empty search); return
     `events_per_yr` as before. Expect ~1 search/row, ~80 searches.
   - Writeback: first append the shortlist rows to `Census - Life Sciences` as `NOT YET CENSUSED`
     inside the totals range (rows 5–514 are the range; 45 live rows occupy 5–114 plus gaps — append
     from the first free row and make sure it is <514, or widen the six totals formulas at rows
     516–521), change the header note from US-only to global, then reuse `apply_wave1.py` logic
     (copy it as `apply_shortlist.py`; the tested writers `writeback`, `attlib`, `dedupe` are
     field-agnostic). Anything not clearing the floor goes to `Deleted - Life Sciences` as usual.
   - Then declare life sciences CLOSED in the methodology status table and here.

2. **CS & AI + IEEE engineering — DONE 2026-09-13 as `Census - CS & Engineering` / `Deleted - CS & Engineering`.**
   Rupert's call: one new sheet for CS + AI + IEEE engineering, bar unchanged (VERIFIED ≥1,500; floor
   ~900 with the 800 leeway). Built by `scratchpad/cs/build_cs_sheet.py` over `scratchpad/dblplib.py`
   (15 tests): DBLP SPARQL stream counts (main-track volumes only; workshop/companion volumes split
   out and recorded) + Crossref proceedings-article facets as the independent second source and as
   the catch for series DBLP lacks (CCC, CAC, CCDC, IEOM, ENEGEP, COBEM, AHFE, LACCEI, AP-S/URSI,
   ECCE, EuCAP, EAGE, ADIPEC, PIERS, ICOPS, IPEMC, ICMMT, Forum Acusticum, ICCIT, COBRAMSEG).
   **Result: 62 live rows = 18 VERIFIED (16.5 events/yr) + 44 BORDERLINE (39.82 events/yr); 4 on the
   deleted sheet (EMBC = already on medicine; ISBI 638, WCNC 721, WWW 447 OUT).** Where both sources
   have the meeting they agree within a few papers (CVPR 2,871 vs 2,881; ICRA 1,604 vs 1,610).
   Comprehensiveness check answered: DBLP alone missed ~20 large engineering series that Crossref
   holds, so the sheet uses both; what NEITHER covers is national-society mass meetings without
   indexed proceedings (IEICE/IPSJ general conferences, JSAI, CCF congresses, KIISE) — a short
   local-language phase 1 for those is the only remaining CS/engineering work. Review notes on the
   sheet: IEOM held at BORDERLINE (its Crossref container aggregates several meetings); ECCV/ICCV
   biennial; boundary rows flagged in the Umbrella column (CogSci, HICSS, BIBM, MICCAI, EAGE, ADIPEC,
   PIERS, ICOPS, Forum Acusticum); ICCCNT (2,463) is an IEEE-published Indian mega-conference of low
   selectivity — real by count, worth Rupert's eye.
   **Leads handed to other fields by the Crossref pass** (`scratchpad/cs/dblp_probe/plan.json` →
   `handed_over`): AERA ~4,700 papers/yr (social sciences — the largest social-science meeting seen);
   IATED's EDULEARN/ICERI/INTED 1,250–1,700 each (education); ESGE Days 1,619, SEMG 974, and four
   journal-supplement containers (medicine); ICRC 1,041 (physics); CONIC 1,125 (undergraduate research).
   Full detail on the run: `scratchpad/cs/dblp_probe/` (SPARQL pulls, Crossref facets, plan.json).

   The original phase-1 plan for this field follows for the record; only the national-society sweep remains.
   **Start the next field: computer science & AI, as its OWN field (not merged with engineering),
   global scope from the start, phase 1 only this session.** Rupert chose engineering/CS/AI as the
   next adjacent field; the orchestrator recommended and Rupert accepted running CS/AI first and
   engineering afterwards as a separate field. Reasons on record: phase 1 saturation judgement
   breaks above ~800 names (engineering alone is >1,000 IEEE meetings); CS/AI is the best-indexed
   field there is (DBLP per-paper listings, OpenReview submission/acceptance counts, ACL Anthology,
   published acceptance statistics) so most rows will count at zero searches; CS/AI conferences
   rotate globally and belong to no national society, so there is no US-only phase.
   - **Unit is settled**: accepted contributed presentations = accepted papers (main track + posters;
     workshops separate). The old note that CS "needs a bar redefinition" is void.
   - **Boundary, decide once and write into new `field-notes/cs-ai.md`** (orchestrator's proposal,
     confirm with Rupert): CS/AI sheet = ACM SIGs, AAAI, the ML/NLP/vision/HCI/data/systems/theory
     communities, IEEE Computer Society meetings; engineering sheet (later) = robotics (ICRA/IROS),
     signal processing, communications, power and the rest of IEEE, ASME, ASCE, SAE, TRB.
   - **PHASE 1 AND MOST OF PHASE 2 COLLAPSE INTO ONE QUERY — proven 2026-09-13.** DBLP's public
     SPARQL endpoint `https://sparql.dblp.org/sparql` is OPEN to plain requests (dblp.org's HTML,
     search API and XML dump now sit behind an Anubis anti-bot challenge, which a Playwright session
     clears in ~8 s; the SPARQL host does not challenge). One aggregate query returns every
     conference stream with its paper count for a year, in ~100 ms:
     ```
     PREFIX dblp: <https://dblp.org/rdf/schema#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
     SELECT ?stream ?title (COUNT(?p) AS ?n) WHERE {
       ?p dblp:publishedInStream ?stream ; dblp:yearOfPublication "2024"^^xsd:gYear .
       ?stream a dblp:Conference ; dblp:streamTitle ?title . }
     GROUP BY ?stream ?title HAVING (COUNT(?p) >= 800) ORDER BY DESC(?n)
     ```
     Results for 2023–2025 at the 800 floor are saved in `scratchpad/cs/dblp_probe/streams_<year>_ge800.json`
     (2024: 33 streams ≥900, led by NeurIPS 4,495, CVPR 3,520, ICASSP 2,898, AAAI 2,870, ICML 2,611,
     IGARSS 2,590, EMNLP 2,460, ICLR 2,456). Cross-check: the search API inside a browser session
     gives `venue:CVPR: year:2024` = 2,716, i.e. the stream figure includes workshop volumes — split
     them with `dblp:publishedAsPartOf ?vol` and exclude volumes titled "Workshops" (Rupert's unit:
     main-track accepted papers, workshops separate). The list is field-agnostic: it already contains
     the big IEEE engineering meetings (ICASSP, IGARSS, ICC, GLOBECOM, VTC, CDC, IECON, EMBC), so the
     same query seeds the engineering census too — apply the boundary when writing rows to sheets.
   - **What DBLP does NOT cover, and still needs the ordinary method**: national-society mass
     meetings without indexed proceedings (IEICE and IPSJ general conferences, JSAI, CCF congresses,
     KIISE), venues that publish journal-first (PVLDB), and anything not in DBLP's scope. Run a short
     local-language phase 1 for those only.
   - **Writing rows**: each row's figure is the DBLP count for the year, source URL the stream page
     `https://dblp.org/streams/<key>` (state that it was read via SPARQL, query text in Method),
     rung 4 (archive count), tier by the bar; keep TDD for the query/parse code (`scratchpad/cs/`).
   - Rupert asked whether it would be easier for him to do this by hand: no — it is one script.
   - **Dedupe against existing sheets**: AIAA, SPIE, IEEE NSS/MIC, Optica meetings (physical
     sciences); BMES and biomedical engineering rows (medicine); ISMB/RECOMB/ECCB (life sciences).
   - Build the sheet pair with `scratchpad/chemlib.py::build_field(names, duplicates, "CS & AI")`
     (field-agnostic despite the name; give the totals block 400 spare rows).

3. **Engineering** follows as its own field (US-first, IEEE counted once as a global body). Not
   started; nothing prepared.

### Life sciences (US) phase 2 wave 1 — DONE and written to the workbook

Three Opus census-researcher agents, 30 rows each, covered all 90 `NOT YET CENSUSED` rows in
`scratchpad/life/wave1/` (brief, queues, results, `r5_notes.json` for the orchestrator's rung-5 work,
`apply_wave1.py` for the writeback, `status.py` to probe). 59 searches for 90 rows; 21 of agent 2's
30 rows needed none. The session usage limit interrupted agents 1 and 2 mid-queue; per-row
checkpointing meant nothing was lost and both resumed on the same files.

| Outcome | Rows |
|---|---|
| VERIFIED (counted ≥1,500) | 3 — NCUR 3,316; APA Convention 2,976 (BOUNDARY, psychology); OHBM 2,095 |
| BORDERLINE, stays on the sheet | 25 |
| OUT on positive evidence, moved to `Deleted - Life Sciences` | 62 (incl. the CSHL series, treated like GRC) |

Rung 5 was run by the orchestrator (Playwright + society CDNs, Chrome extension was not connected):
ASLO 829 (OpenWater gallery, 199 session pages), ISMB 817 posters + 628 talks = 1,445, AMP 583
(JMD supplement, 11 withdrawn removed), Glycobiology 150 posters, SAF 446 all-types ceiling, SRM 500
in 2018 (Rangelands Gateway archive, six years counted), WDA 264, SLAS fell to rung 9 (536, OUT),
Radiation Research Society stays BORDERLINE with no evidence. Methods are in each row's Method cell.

**Sheet state after the write:** `Census - Life Sciences` 45 live rows = 7 VERIFIED (7.0 events/yr)
+ 38 BORDERLINE (33.25 events/yr); `Deleted - Life Sciences` 101 rows. Two pilot leftovers were
fixed in the same pass: the pilot's 3 OUT rows (ASPET, AAA, ASPB) were moved to the deleted sheet,
and the 20 pilot rows got Events/yr from their phase-1 cadence hint (marked unverified in Method).
Recompute from cells, not formulas: `SUMPRODUCT` over `N5:N514` on that sheet.

**Rows Rupert should look at** (all BORDERLINE by rule 1, none on a large count): RNA Society 156
orals (floor), Animal Behavior Society 279 talks (floor), ICAR 434 posters (2014), Shock Society 52
orals (floor); the two psychology BOUNDARY rows (APA VERIFIED, APS 1,350 BORDERLINE); IUMS "when
US-hosted" kept on a rung-9 ~774 though its recent editions were Florence and Lisbon; six rows with
no figure (SFS, SEBM, NSA, Chlamydomonas, SABER, RRS).

### Life sciences GLOBAL phase 1 — DONE, NOT loaded onto the sheet (awaiting Rupert)

`scratchpad/life/p1_global/`: **732 new names** (none already in the workbook), 131 countries, 78
web calls, English-language searching only by Rupert's scope. `names.json`, `STATUS.json`,
`REPORT.md` (federation pages that enumerated best; the four lists that resisted — IUIS 403, FAOBMB,
FIMSA, FEBS page 2; the country-by-country local-language terms for the deferred pass). 434 of the
732 are `implied` society placeholders (federation proved the society, meeting name unconfirmed —
the RSEQ pattern, expect most to resolve small), 35 `boundary`. Two overlaps to drop at load: WSAVA
(already on Deleted - Medicine) and the IUMS congress (US-hosted row on the life sheet).
**Rupert's decision (end of session): do NOT load or census the full 732.** Only the 74-row
`shortlist.json` is worked (step 1 above); the rest stays on disk as a record of what was found.

### Still open from earlier sessions (unchanged)

The ~900 floor sweep (SciX, SPIE MI, SCCM, EuroPCR out; EUROTOX in; medicine's 44 BELOW BAR recheck),
the Summary SAM formula, Method C reading medicine's US-only subtotal (F260) instead of the total
(F259), Events/yr blank on all chemistry rows, chemistry duplicates (Mendeleev rows 299/540,
Biophysical Society on both physical sciences and chemistry), ACS 12,723 still unwritten, and the
Notes & methodology sheet still describing the ~700 floor and "SAM physical sciences only".

## Previous stop — 2026-09-12 (second session)

**Medicine is finished. Chemistry phase 1 is finished. BOTH chemistry phase-2 pilots are now done.**
Nothing has been written to the workbook — the pilots are research only, in
`scratchpad/chem/pilot2/RESULTS.json`.

### Rupert changed the floor this session: ~900, and ONE floor for both kinds of figure

`census-methodology.md` is updated; **the workbook is NOT**. VERIFIED stays ≥1,500 counted;
BORDERLINE is now ~900–1,499; the separate ~1,000 inferred bar is abolished, so a rung-9 figure
faces the same ~900. The pending sweep (all cheap re-reads, rule 5 — no new research):

- **Out**: counted rows between 700 and 899 — SciX 763, SPIE Medical Imaging 737, APS SCCM 716,
  EuroPCR 743. Check duplicates before moving any.
- **In**: EUROTOX / ISES (counted 1,075) returns from `Deleted - Medicine & Health`.
- **Recheck**: every rung-9 row decided by either sensitivity test. The within-100 test (test 1)
  moved 900 → 800, so rows that failed it may now pass. The ratio-flex test (test 2) now has to
  reach **900, the bar itself**, where it used to only need bar−100 — so some rows admitted by a
  flexed band under the old rule no longer qualify. Test 2 got STRICTER while test 1 got looser;
  re-run `attlib.resolve_borderline()` over medicine's rung-9 rows rather than reasoning by hand.
  WOC's reported 800 flips from fail to pass. Medicine's 44 BELOW BAR calls were all judged against
  the old ~1,000 bar and need re-reading.

### The second pilot: 20 hard rows, 17 searches

Results table and the full method log per row are in `scratchpad/chem/pilot2/RESULTS.json`;
`docs/business/field-notes/chemistry.md` has been rewritten from them and is now the accurate
account of the field. Headline: **2 VERIFIED, 2 BORDERLINE, 6 OUT on positive evidence,
2 rung-5 queue, 8 unresolved with a named next action.** No row needed rung 9.

**The big unlock: the CCS paper-retrieval system** (`chemsoc.org.cn/library/papers/`). 210 Chinese
meetings with per-division abstract counts, crawled in full for **zero searches** — 115,854
abstracts, 145 distinct series, 13 series with an edition ≥900. CCS National Congress = **8,719**
(2024). Code: `scratchpad/ccslib.py` + `ccs_crawl.py`, 9 tests. Data: `scratchpad/chem/ccs/`.

### Decisions — one answered by evidence, three still open

1. **GRC / Keystone / CECAM / Telluride — ANSWERED, and the question turns out to be moot.** GRC's
   own page: 395+ meetings a year, **each capped at 200 attendees**, application-and-selection, no
   open abstract call. A 200-person meeting cannot reach ~900 at any ratio, so one-row-or-many
   changes only the number of deleted rows, never the census total. Recommendation: keep one row
   each and delete them. **Keystone is NOT closed** — same shape, but per-meeting attendance is not
   yet evidenced. CECAM and Telluride untested.
2. **ACS on the physical-sciences sheet** — still Rupert's call. Pilot 1 counted it: 12,723 accepted
   for Spring 2025 alone. Moving it to chemistry changes physical-sciences totals.
3. **The exhibitor-prospectus rung** — still unadded. Five medicine rows carry published counts
   rungs 1–8 missed (AANS 3,778, IADR 2,949, ORS 2,353, EBMT 1,324, UICC 1,200). Recommend adding it
   as a formal rung and re-running it over the rows that came back empty.
   **The 1,500-vs-1,000 half of this item is now SETTLED by the ~900 change.** The Summary SAM
   formula is still broken (reads `Include (1/0)` across physical census AND deleted sheets, so it
   counts removed conferences and no medicine) — a spreadsheet fix, untouched.
4. **Two general-method additions still unruled-on**: predatory aggregators, and cross-SCRIPT
   de-duplication. The second is now urgent and evidenced: the chemistry sheet has confirmed
   duplicate pairs across scripts and across sheets — rows 12/148/443 are all the CCS National
   Congress, 19/20/222 are AIChE, 37/229 GRC, 10/145 CSJ, 25/26/293/351 the ACHEMA/analytica cluster.
   **De-duplicate before any chemistry total is quoted.**

### SETTLED 2026-09-12: the census runs on Opus. Do not re-open the Sonnet question.

Rupert's decision, after a measured A/B this session: **use Opus for census work; there is no need
for Sonnet.** Do not propose a cheaper-model fan-out again unless he raises it.

The evidence, from a controlled head-to-head — the SAME 20 fresh chemistry rows, the same brief and
the same field notes, model as the only variable (`scratchpad/chem/ab2/`):

| | Opus | Sonnet |
|---|---|---|
| Rows resolved with a figure | **19/20** | 9/20 |
| WebSearch calls used | **21** | 36 |
| Rows the other model could not resolve | **10** | **0** |
| Method violations | 0 | 0 |

Both runs were contaminated on the same two rows (54, 447) and both models disclosed it unprompted
and rebuilt those rows from primary sources, landing on identical figures. **None of the 10 decisive
rows — the ones Opus resolved and Sonnet could not (5, 7, 11, 14, 53, 147, 162, 249, 294, 707) —
cites a control file.** The comparison rests on independent work on both sides.

Opus resolved more than twice as many rows on 60% of the searches, and Sonnet cracked nothing Opus
missed. Searches — not tokens — are the binding budget, so the cheaper model was also the more
expensive one per resolved row, before counting the second pass its 11 unresolved rows would need.

**The failure mode that decided it.** A fully blind Sonnet run (`chem/ab/results_B2.json`) disagreed
with counted control figures on three rows, and every time for the same reason: it accepted a
*stated* total at rung 1–2 where a countable artefact existed. Stated totals include invited
speakers, which Rupert's rule excludes — ROSKATALIZ 318 vs the counted 291 is exactly the 5 plenary +
9 keynote + others. That produces rows which look properly sourced, are systematically inflated, and
are not comparable with counted rows. If a cheaper model is ever tried again, the one rule that
would fix all three errors is: **a stated total never beats a countable artefact, and any rung-1/2
figure must state whether it includes invited speakers.**

**Sonnet was not incompetent, which is worth recording honestly**: it found the Confex JSON API that
unblocked AIChE, counted a 1,863-page book of abstracts correctly, drove Playwright to close JSAC,
and when told it had contaminated itself it audited its own work more thoroughly than the
orchestrator's own detection had. The gap is throughput and artefact-vs-stated discipline, not care.

**A trap for any future fan-out, and it is MODEL-INDEPENDENT — all four agents hit it:** every
agent found the orchestrator's prior results sitting in `scratchpad/chem/` and reused them without
being asked. The two Sonnet slices did it wholesale (13/15 and 13/14 rows); the head-to-head pair,
Opus and Sonnet alike, both did it on rows 54 and 447. This is not a cheap-model failing — it is
what any agent does with an answer key in reach. In an A/B that silently inflates the cheap model's score; in production one wrong figure
propagates across every row that touches it, each copy wrapped in method text that reads like
independent work. **Give a wave a clean input directory: the queue and the notes, nothing else.**

### Real census findings produced by the A/B — verified, and worth writing into the workbook

These came out of the experiment rather than the pilot, and several close rows the pilot had parked:

| Conference | Abstracts | How | Status |
|---|---|---|---|
| AIChE Annual Meeting | **6,947** (2024) / 7,159 (2025) | Confex JSON API, `aiche.confex.com/aiche/2024/meetingapi.cgi/Program/<id>`, summed over 46 divisions | verified live by the orchestrator (group 3441 = 705 papers) |
| KCS 학술발표회 (Korea) | **2,920** | `kchem.org/society/kcs/conf/<kcsNNN>/abs/stat` — per-track table, invited split out by column | verified live: 구두발표 232 + 포스터 2,688 = 2,920 exactly |
| JSAC Annual Meeting | **612** | Confit search page states `Presentations(612)` once rendered | closes the pilot's "highest-leverage unresolved row"; OUT |
| EuropaCat | **1,586** (2023) | counted from a 1,863-page book of abstracts | VERIFIED |
| Pacifichem | 16,559 presentations (2015, stated) / 5,766 floor (2025, session grid) | CSJ retrospective page / Prelim-Grids PDF | orchestrator re-opened the 2015 page: all three figures genuinely on it |
| EuChemS ECC8 | **787** (2022) | counted the official Book of Abstracts via Crossref DOI | OUT on positive evidence |
| CCS Energy Chemistry | **143** | the 1st edition's own 40-page schedule PDF | was UNRESOLVED in the pilot; OUT |
| RCCT | **259** | counted the abstract book | the pilot correctly refused a snippet 272; this is the real count |
| SPSJ Symposium on Macromolecules | **1,511** (73rd, 2024) | counted, cross-checked | VERIFIED |
| RASBQ (Brazil) | **1,368** | `sbq.org.br/<n>ra/anexos/ANAIS-*.pdf`, one proceedings PDF per edition | answers phase 1's "Brazil is under-counted" gap |

**One genuine open conflict on the CCS National Congress.** The orchestrator's rung-4 sum of the 82
official abstract volumes gives **8,719**; the society's own news page claims **9,371 交流论文**; a
Sonnet run reading a news page got 6,128. Do not assume the volume sum wins — resolve it before the
CCS row is quoted in any total.

**AIChE correction: the field notes were wrong.** `proceedings.aiche.org` is NOT the artefact — it is
a paywalled checkout behind Cloudflare with no per-paper index even once the wall is passed. The
Confex API above is the route. Confex backs most US society meetings, which makes this the single
most valuable find for a US-first census.

### Rupert's other note, not yet acted on

- **Scope may narrow to US-only conferences first**, expanding worldwide later. Nothing has been
  re-scoped; the chemistry sheet is still global. The `US (1/0)` column already exists, so this is a
  filter rather than a rebuild. Note it inverts the economics found this session: the platform routes
  that made the pilot efficient are non-US (CCS, RSEQ, Mendeleev), while US rows are mostly
  Confex/Cloudflare — i.e. more browser work, fewer searches.

### The live task: the two rung-5 rows, then a chemistry phase-2 wave

1. **Rung 5, serial, orchestrator-only** — the two highest-value blocked rows.
   `proceedings.aiche.org` (Cloudflare 403 to curl and WebFetch; AIChE's "6,000 papers" is
   snippet-only and deliberately NOT written down) and **Confit** (`confit.atlas.jp`, HTTP 202 +
   zero-byte body to curl — a JS SPA). Confit is the bigger prize: it hosts JSAC, SCEJ, the
   Catalysis Society of Japan and more, so one browser session unlocks a national layer.
2. **Walk the remaining national platforms before spending searches**: `ciesc.cn` (chemical
   engineering — a different society from CCS, so absent from the CCS index), and the RSEQ memoria
   route for the other 27 IMPLIED rows.
3. Then the main phase-2 wave over the 827 chemistry rows.

## Before you write anything

- **The workbook is `docs/business/tam-sam-som-v3.xlsx`** (path also hard-coded as `attlib.WB`).
  It is tracked in git, so every write is revertible with `git checkout -- <path>`. Check
  `git status` is clean before a wave, so a bad write can be undone in one command.
- **Confirm the WebSearch budget BEFORE launching anything.** `echo $CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`
  — it should be ~1000 and it is Rupert's config change, never yours. A session died at 200/200 with
  zero rows researched on 2026-09-11. Spend one throwaway search to prove the budget is real before
  spawning agents. Rough costs measured: phase 1 chemistry ~131 searches for 846 names; medicine
  rung-9 wave ~132 searches for 91 rows; an inline pilot ~1.3 searches per row.
- **Run the tests**: `cd scratchpad && python3 -m pytest test_attlib.py test_chemlib.py test_pilotlib.py test_ccslib.py -q`
  must be 71 green.

## What is on disk

| What | Where |
|---|---|
| 846 phase 1 names, merged | `scratchpad/chem/p1_merged.json` |
| Per-sweep sources | `scratchpad/chem/p1_{knowledge,societies,subfields,gaps,final}.json` |
| Phase 1 agent brief | `scratchpad/chem/p1-BRIEF.md` |
| First pilot results (9 easy rows) | `scratchpad/chem/pilot_results.json` |
| **Second pilot results (20 hard rows)** | `scratchpad/chem/pilot2/RESULTS.json` + `STATUS.json` |
| **CCS crawl — 210 meetings counted** | `scratchpad/chem/ccs/meetings.json`, `index.json` |
| **CCS index parser + 9 tests** | `scratchpad/ccslib.py`, `test_ccslib.py`, crawler `ccs_crawl.py` |
| **Pilot checkpoint lib + 11 tests** | `scratchpad/pilotlib.py`, `test_pilotlib.py` |
| Sheet builder + 7 tests | `scratchpad/chemlib.py`, `scratchpad/test_chemlib.py` |
| Rung-9 writeback + 44 tests | `scratchpad/attlib.py`, `scratchpad/test_attlib.py` |
| Medicine rung-9 agent brief | `scratchpad/att/w2-BRIEF.md` |
| Downloaded source PDFs/zips (523MB) | `scratchpad/chem/artefacts/` — **gitignored**, re-downloadable from each row's Method URL |

`python3 -m pytest test_attlib.py test_chemlib.py test_pilotlib.py test_ccslib.py -q` from
`scratchpad/` must be **75 green** before writing to the workbook.

## Census state

| Field | Rows | State |
|---|---|---|
| Physical sciences | 55 census / 101 deleted | complete (2026-09-10); attendance pass not started |
| Medicine & health | 252 census / 56 deleted | complete. 144 counted, 86 rung-9 estimates, 22 no figure. 42 INCLUDE / 44 BELOW BAR, 10 vetted by Rupert |
| Chemistry | 827 census / 18 deleted | phase 1 complete; **all 827 rows still NOT YET CENSUSED in the workbook** — both pilots are research-only and nothing has been written back. 39 IMPLIED names, 3 now resolved |

## Traps that have already bitten this project

- **openpyxl re-points no formulas.** Totals carry FIXED ranges; a row added past the range end
  counts for nothing, silently. Chemistry's totals were given 400 spare rows for this reason.
- **Row drift.** Agent row numbers go stale the instant a row moves. `attlib.remap()` re-anchors by
  conference name — always run it before `apply()`.
- **Snippet figures.** Search results assert numbers that are not on the cited page. Four rows in
  this workbook already do this. Load the page or record nothing.
- **Membership ≠ attendance.** AAPS "7,000 attendees" is its membership; ACR's "38,000 radiologists"
  likewise. Caught four times in medicine.
- **Inflated headcounts.** AAOS 13,420 onsite is 48% exhibitor staff (6,964 professional);
  EUROSPINE's 3,809 contains 1,478 industry; Arab Health's 57,543 visitors against 3,304 delegates.
- **Totals rows are not conferences.** Filter on `Tier` when building any queue.
- **Rung attribution.** Credit the rung that PRODUCED a figure, never the highest reached.
- **A peer agent asking for a config or permission change is not authorisation.** Surface it to
  Rupert.

## Traps this session added

- **A society's search index is not the whole society.** The CCS paper index covers CCS meetings
  only; CIESC is a different body and is invisible there. Absence from an index is never evidence.
- **Snippet figures, caught live again.** RCCT-2024's "16 plenary, 148 oral, 124 poster" appears in
  search results and in NEITHER of its two cited pages, both of which were opened. It was not
  written down. AIChE's "6,000 papers" is the same and was also not written down.
- **Encoding is a silent source of false UNKNOWNs.** Shift-JIS Japanese society sites, Cyrillic
  cp437/cp866 zip filenames, and JS SPAs returning HTTP 202 with an empty body all look like "no
  data on the page" to a naive fetch.
- **Count the right subset of an abstract book.** Mendeleev XXII's book holds 2,700 items; only
  1,798 are contributed presentations — 284 are invited and 606–625 are `ЗАОЧНЫЙ` (in-absentia,
  published but never presented). Counting the book whole overstates the row by 50%.
