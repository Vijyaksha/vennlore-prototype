# HANDOFF — conference census

State of play for the next session. The method lives in `census-methodology.md` (general, all
fields) and `field-notes/<field>.md` (field-specific). This file is only where we stopped.

## Where we stopped — 2026-09-12 (second session)

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
