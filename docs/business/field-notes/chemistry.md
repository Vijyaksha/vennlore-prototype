# Field notes — chemistry

Companion to `census-methodology.md`, which stays general. This file holds only what is true of
**chemistry** and would be noise in the general method. Read both before working a chemistry row;
add what you learn here, not there.

Started 2026-09-12 from the phase 1 sweep and a 9-row phase 2 pilot.

## Scope, and where chemistry overlaps other censuses

Chemistry sits between two censuses that already exist, so **de-duplicate before trusting any
total**. These are already counted elsewhere and must not be added again:

| Conference | Already on |
|---|---|
| ACS Spring + Fall (one row) | `Census - Physical Sciences` — abstracts UNKNOWN there; the pilot has now counted them |
| MRS Spring/Fall, E-MRS Spring/Fall | `Census - Physical Sciences` |
| SciX (FACSS) | `Census - Physical Sciences` |
| ECS Meetings (Electrochemical Society) | `Census - Physical Sciences` |
| SOT Annual Meeting | `Census - Medicine & Health` (2,276 abstracts) |
| EUROTOX | `Deleted - Medicine & Health` (counted 1,075) |

Boundary calls to make once and apply consistently: materials chemistry, biochemistry and chemical
biology, pharmaceutical sciences, crystallography, and chemical engineering. The phase 1 sweep
over-included all of them deliberately.

## Where chemistry hides its counts

Chemistry publishes abstract counts more readily than medicine, but **almost never as a stated
total**. What it publishes is a countable artefact, and the two pilots found six kinds. Ranked by
how much they settle per unit of effort:

1. **National society paper-retrieval indexes — by far the highest-yield artefact in this field.**
   The Chinese Chemical Society runs one at `chemsoc.org.cn/library/papers/`, and it is the chemistry
   analogue of medicine's Crossref deposit index: 210 meetings, each with a 论文集 table listing one
   abstract volume (摘要集) per division, **each stating its own 论文数**. Crawling all 210 cost
   **zero searches** and produced **115,854 indexed abstracts**. See the section below.
2. **The society's own magazine.** C&EN's meeting programme PDF carries an itemised breakdown:
   ACS Spring 2025 = 12,723 accepted papers (6,736 in-person oral + 941 digital oral + 5,046
   posters, summing exactly). Look for `cen.acs.org/content/dam/cen/...meeting-program.pdf`.
3. **The congress's own abstract book, published as one download.** The Mendeleev Congress puts all
   seven volumes in a single zip on its own site (`mendeleevcongress.ru/media/sbornik-tezisov-*.zip`,
   195MB) — 1,798 contributed abstracts counted from it at one search. Russian and Central Asian
   congresses do this routinely; look for `сборник тезисов` before anything else.
4. **The president's business-meeting slide deck.** ASMS publishes a five-year table — abstracts
   submitted, orals, posters, attendance, membership — in one PDF presented at the annual meeting.
   One artefact, five years of history, for one search.
5. **Society news pages in the local language.** CSJ's 106th meeting states 3,604 academic-programme
   presentations and 6,000+ participants on its own Japanese news page; English queries return
   nothing usable.
6. **The umbrella body's annual activity report.** One PDF can resolve *dozens* of rows at once.
   RSEQ's `rseq.org/memorias-rseq/rseq_memorias_ge_2024.pdf` (76pp) carries a memoria for **every one
   of its specialised groups** — the real meeting name, the member count, and usually the attendance
   and communication counts. The CCS 2017 annual report does the same for China
   (`chemsoc.org.cn/about/annual/2017ANNUALREPORT.pdf`). **Always look for the federation's annual
   report before researching its member groups one at a time.**

### The CCS paper-retrieval system — the single most valuable page in the chemistry census

`https://www.chemsoc.org.cn/library/papers/` — 210 CCS meetings, 1998 to 2024, each with per-division
abstract counts. Crawled in full on 2026-09-12 (`scratchpad/ccs_crawl.py`, parser
`scratchpad/ccslib.py`, 9 tests; results in `scratchpad/chem/ccs/meetings.json`).

**How to fetch it.** A bare request 302s to `index.php` and returns nothing. It needs a **session
cookie plus a `Referer` of the index page**; with those, `meeting.php?id=<n>` returns plain HTML with
no JS. The index paginates at `?page=N`, 10 per page, 21 pages. `ccslib.py` encapsulates all of this.

**What it yielded**, counting contributed abstracts only (the parser reports the
`大会特邀报告` plenary-invited volume separately so it can be excluded per Rupert's invited rule):

| | |
|---|---|
| Meetings indexed | 210, all parsed, zero errors |
| Total abstracts indexed | 115,854 |
| Distinct series (editions collapsed) | 145 |
| Series with an edition ≥900 contributed | **13** |
| Individual editions ≥900 | 24 |
| Editions under 300 | 143 |

The CCS National Congress dominates and is growing steadily: **27th 3,085 → 28th 4,008 → 29th 5,156
→ 30th 7,124 → 31st 7,552 → 32nd 8,442 → 34th 8,716 → 33rd 9,519**. The other series that clear the
floor are 全国高分子学术论文报告会 (2,183), 全国催化学术会议 (1,901), 全国环境化学大会 (1,814),
全国电化学大会 (1,757), 全国分析化学年会 (1,482), 全国有机化学学术会议 (1,343),
全国无机化学学术会议 (1,110) and 全国配位化学会议 (1,077).

**Three cautions on this index, all hit for real:**

- **It is patchy and its coverage skews old.** Many series' most recent indexed edition is 2013–2015.
  A figure from it is often `DATED`, and for a growing series that means it is a *floor*, not a
  current count.
- **Absence from the index is not evidence of a small meeting.** 全国理论与计算化学会议 and the main
  全国能源化学学术会议 are both missing entirely. Those rows stay `BORDERLINE`.
- **Only CCS meetings are in it.** CIESC (中国化工学会, chemical engineering) is a *different
  society*; its meetings will never appear here and need `ciesc.cn` walked separately.

### Name collisions in Chinese series — check before merging any two rows

Chinese series names differ by one or two characters and denote genuinely different meetings of very
different size. Three found in twenty rows:

| Looks like | Actually | Sizes |
|---|---|---|
| 全国**分析**化学年会 | vs 全国**电分析**化学学术会议 | 1,482 vs 630 |
| 全国能源化学**学术会议** | vs 全国能源化学**青年论坛** (youth forum) | unknown vs 197 |
| 中国**化学**会 (CCS) | vs 中国**化工**学会 (CIESC) | different societies entirely |

## The conversion ratio, and what the pilot changed about it

Chemistry converts **far** higher than medicine. Anchors observed so far:

- CCS National Congress: 8,719 abstracts against 11,000+ attendees = **79%**
- Mendeleev Congress: 1,798 contributed against 4,000+ participants = **45%**

Do not maintain a static anchor list here — generate the current one with
`attlib.ratio_rows(sheet='Census - Chemistry')`, and record in each row's Method cell the specific
anchors you actually reasoned from. The no-shortcuts rule in the general method still applies.

Why the ratio is high at research congresses: chemistry meetings are built on divisional programmes
where nearly every attendee presents, and the poster hall is the main event. **The exceptions are
the trade fairs, where it collapses to near zero — see below.**

**The pilot needed rung 9 for none of the twenty rows.** Every row that resolved did so at rungs 2–4
off a countable artefact. That is the opposite of medicine, where rung 9 carried 86 of 252 rows.
Plan chemistry waves around *finding artefacts*, not around attendance conversion.

## Field-specific traps

- **Predatory aggregators are worse here than in medicine.** WASET, conferenceseries.com (OMICS),
  conferenceindex.org, Magnus Group, Peers Alley, United Scientific Group and lookalikes dominate
  result pages for every subfield, and they manufacture plausible names ("International Conference
  on Analytical and Bioanalytical Chemistry, Istanbul"). All three phase 1 agents hit them
  independently. **A real meeting traces to a society, a university, or a series with past
  editions.** Nanochemistry is the worst-infested area.
- **ACS is many meetings, not one.** Two national meetings a year plus eight regional meetings
  (MARM, NERM, SERMACS, MWRM, SWRM, NORM, WRM, CERM), each with its own abstract call. Events/yr
  must reflect that.
- **Trade fairs wear conference clothing, and their programme numbers are vendor talks.** Pittcon,
  ACHEMA, analytica, JASIS, ARABLAB, K and CHINAPLAS all carry technical programmes of very different
  weight. Judge them on contributed science, not on the exhibition. **JASIS is the worked example and
  the sharpest trap in the field**: search returns `2024年の発表件数は312件`, which reads exactly like
  an abstract count. JAIMA's own post-show report shows those 312 are
  新技術説明会（出展社による最新機器・技術の紹介） — **92 exhibitors presenting product talks**. There is
  no call for abstracts anywhere in the programme: contributed abstracts = **0**, against 21,918
  visitors. ARABLAB is the same shape (350 "expert speakers", no abstract call). ACHEMA is the one
  genuine borderline: 106,001 participants and 30,000+ congress listeners, but its programme total of
  "over 900 lectures, discussion panels and workshops" is an *upper bound* that lumps contributed
  lectures with panels and workshops, so contributed science sits just under the ~900 floor.
- **Russian national congresses are small by abstract count, even the flagship ones.** ROSKATALIZ,
  the Russian national catalysis congress, has a 919-page abstract book containing **291** contributed
  presentations (154 oral + 137 poster). Do not let a thick abstract book or a grand title imply
  scale — Russian abstracts run ~3 pages each, against ~1 page at the Mendeleev Congress. The
  Mendeleev Congress itself is the only Russian chemistry meeting found so far that clears the bar.
- **Russian abstract books label every item by type, which makes the invited split exact.** Grep for
  `(ПЛЕНАРНЫЙ|КЛЮЧЕВОЙ|ПРИГЛАШЕННЫЙ|УСТНЫЙ|ПОСТЕРНЫЙ|ЗАОЧНЫЙ) ДОКЛАД`. Two of those are exclusions:
  `ПРИГЛАШЕННЫЙ`/`КЛЮЧЕВОЙ`/`ПЛЕНАРНЫЙ` are invited (284 of them at Mendeleev XXII), and **`ЗАОЧНЫЙ`
  is in-absentia** — accepted and published but never presented, 606–625 at Mendeleev XXII, and
  excluded from the counted figure. Counting the whole book would have overstated that row by 50%.
- **Cyrillic zip filenames break `unzip`.** The Mendeleev collection unpacks only if names are
  decoded `cp437` → `cp866`. Use Python's `zipfile`, not the shell.
- **Shift-JIS Japanese society sites decode to mojibake.** `main.spsj.or.jp` and similar older
  Japanese society pages are Shift-JIS; a naive UTF-8 fetch looks like an empty or broken page and
  invites a wrong `UNKNOWN`. Force `shift_jis`/`cp932`.
- **Confit is a JS SPA and returns HTTP 202 with a zero-byte body to `curl`.** That is a rung-5 job,
  not a dead end. Confit hosts JSAC, SCEJ, the Catalysis Society of Japan and others, so solving it
  once in a browser unlocks a whole national layer — it is the highest-leverage unresolved item in
  the chemistry census.
- **Index-page societies hide dozens of meetings behind one row.** RSEQ (Spain) has 30 specialised
  groups each running a recurring reunión; SCI (Italy) has 11 divisional congresses; the Chinese
  Chemical Society runs division congresses on one index. One fetch of the index yields 20–30 names.
- **The 39 IMPLIED placeholders resolve in one PDF, and they resolve SMALL.** The RSEQ memoria
  (above) names each group's real meeting. Two patterns, and both matter:
  the placeholder may be *renamed* (GEADS → "Reunión Ibérica de Adsorción", ~100 researchers) or
  *wrong* (GCTbA runs no meeting of its own; its congress is **NyNA**, the International Congress on
  Analytical Nanoscience and Nanotechnology). **Rename the row before deleting it** — the meetings are
  real, just small, and a deleted row must keep a name a later session can find.
  Measured sizes: GEE-RSEQ electrochemistry 180 contributed (100 oral + 80 poster) against 200+
  attendees; GEADS ~100 attendees against 85 group members. Spanish specialised-group meetings run
  50–200 people. **None of the 30 RSEQ rows will clear the ~900 floor**; work them as a single
  batch off the memoria rather than one search at a time.
- **Invite-led series — the one-row-or-many question is MOOT for the bar.** GRC's own About page
  states it: **"GRC organizes over 395 Gordon Research Conferences (GRCs) and Gordon Research
  Seminars (GRSs) per year"**, **"Each conference is limited to 200 attendees"**, and attendance is by
  application and chair selection, not an open call for abstracts. A 200-person cap means no
  individual GRC can reach the ~900 floor **at any conversion ratio**, so whether GRC is carried as
  one row or exploded into 395 changes only how many deleted rows exist — never the census total.
  Character is `CURATED`. Keystone (50–60 meetings/yr) is the same shape and its abstracts are
  distributed only through a private registrant app, but **its per-meeting attendance is not yet
  evidenced**, so it is not closed. CECAM and Telluride remain untested.

## Phase 1 state — COMPLETE (2026-09-12)

**846 unique conference names**, merged from five sweeps for ~131 searches: a knowledge-first list,
societies/geography, subfields/techniques, a gap sweep, and a final index-expansion and
local-language sweep.

**The local-language sweep is the reason this list is credible.** Before it, the list was deep where
societies publish in English and blind everywhere else. After it:

| Region | Before | After |
|---|---|---|
| China | 15 | 96 |
| Russia | 4 | 61 |
| Spain | 6 | 35 |
| India | 9 | 24 |
| South Korea | 2 | 14 |
| Portugal | 0 | 14 |
| Iran | 0 | 11 |
| Central Asia & Caucasus | 0 | 15 |

An English-only census would have undercounted the world's largest chemistry community roughly
sixfold. Treat that as the standing argument for the mandatory local-language rule.

Known weaknesses to resolve in phase 2:

- **42 entries are society-implied placeholders** (`"implied": true`) — a federation or group list
  proves the body exists, but the meeting's real title was never confirmed. Honest placeholders,
  not inventions. Each needs one confirmation fetch to resolve to a real name, or be dropped.
  Concentrated in the 30 RSEQ groups, 6 SCI divisions, and small FACS/FASC member societies.
- **Azerbaijan** — the one country that defeated the sweep. ANAS and the Nagiyev Institute clearly
  run chemistry meetings; every angle returned the institute itself or predatory aggregators.
  Nothing was listed rather than invent a name.
- **Brazil** — 6 entries only, because its national index died (see above). Certainly under-counted.
- **CCS depth** — the meetings index was crawled to page 6 of 22; the rest are older editions of
  series already captured, but a full crawl would catch dormant ones.
- **Kyrgyzstan** — nothing found; may genuinely have no standalone chemistry congress.

## Zero-search routes found in wave 1 (2026-09-12, 100 English rows, 45 searches)

Each of these settled a row without a search. Try them before searching.

| Route | How | Settled |
|---|---|---|
| **Confex whole-meeting endpoint** | `<host>/<org>/<year>/meetingapi.cgi/Paper` returns every paper with its type and a withdrawn flag, no programme ID needed. Keeps working after the web programme is taken down | Goldschmidt 2025 = 3,072 |
| **CTI abstractsonline** | Looks browser-only but isn't: POST the public guest credentials shipped in its own JS to `/oe3/Backpack/create`, search `/oe3/Program/<id>/Search/new/presentation` with `{"Phrase":"*"}` (an empty phrase returns 0), read each presentation's `Activity` to separate abstracts from invited speakers. CTI hosts many society meetings | ICMAT 2025 = 968 |
| **DGM programme widget API** | The conference page carries `<schedule-extended domain="dgm.inventum.de" id=".." hash="..">`; `GET https://dgm.inventum.de/api/customer/widget/<id>/<hash>?lang=en` returns the whole programme as typed JSON (Lecture / Keynote / Plenary / Company presentation + posters). Without `lang=en` it returns 503. Covers every DGM-run meeting | EWCPS 2025 |
| **Documedias planner** | `<event>.planner.documedias.systems/api/settings` links the full programme PDF at `/api/documents/pdf-program` | EAFS 2025 |
| **WordPress media index** | `<site>/wp-json/wp/v2/media` lists uploaded PDFs, finding abstract books the page itself hides. Worked on 5 sites | Dioxin, IUFoST, ICOS, CRSI, RMRM |
| **Crossref by publisher prefix** | `api.crossref.org/prefixes/<prefix>/works?rows=1000&cursor=*`, split by container title. PSE Press `10.69997` (ESCAPE 35 = 424, ESCAPE 36 = 338); AMPP/NACE `10.5006` | ESCAPE, AMPP |
| **Crossref by abstract title** | JBC holds ASBMB abstracts per item but with no supplement page numbers, so the S-page filter finds nothing; filter on titles starting "Abstract NNNN" | ASBMB 2026 = 1,516 |
| **Acta Cryst A page prefixes** | One journal volume holds three meetings: `e` = ECM, `a` = ACA, `C` = IUCr Congress | ECM |
| **Institutional Indico** | FZ Jülich: `iffindico.fz-juelich.de/export/event/<id>.json?detail=contributions` (types Talk / Invited talk / Poster). An Indico export can come back **empty** — PSI's ICRP did — so count the attached abstract book instead | POLYSOLVAT-16 |
| **ACS MAPS programme tables** | ACS regional meetings post programme tables with a paper-number column, grouped by session type. `acs.confex.com` no longer exists and `acs.org` blocks curl (Incapsula) | SERMACS, WRM |
| **GoeShow** | `s7.goeshow.com/<org>/annual/<year>/program.cfm` is plain HTML; a `getDetails` POST expands each session | EAS 2025 |
| **Server-rendered programmes** | EventsAir agenda detail pages and inviteo programme pages both work with plain curl | Chemeca, ICC Lyon |
| **Wayback CDX API** | `web.archive.org/cdx/search/cdx?url=<domain>*` recovers programme PDFs from expired meeting domains. For old RSC pages, `web.archive.org/web/<year>id_/<url>` works where WebFetch is blocked | OMCOS-22, IP'24 |
| **Organiser history pages** | `organicdivision.org/noshistory/` (NOS attendees and posters since the 1980s); `watoc.net/watoc.congress.html` (every WATOC); `eu-openscreen.eu/resources/ecbs.html` (ECBS) | NOS, WATOC, ECBS |
| **Free proceedings archives** | AAFS: `aafs.org/research/annual-conference-proceedings`, 2002–2026, IDs are a section letter + number, withdrawn items marked | AAFS 2026 = 961 presented |
| **Google Drive abstract books** | `drive.usercontent.google.com/download?id=<id>&confirm=t` | ICCE/ECRICE 2026 |
| **Poster floorplan images** | Board numbers are countable (rung 6) when the abstract book needs a login | EFMC-ISMC |

### Traps found in wave 1

- **Stated totals overstate counts, again.** ICC Lyon said "1,500 posters"; the count was 1,371. Count the artefact whenever one exists.
- **"Invited Communications" can be contributed.** WATOC labels its orals that way, but its submission page says all 150 were selected from submitted abstracts — count them. Read the submission page before excluding a label.
- **Withdrawn abstracts are not presented.** AAFS 2026: 1,071 accepted, 110 withdrawn, 961 presented.
- **Trade fairs, again**: CPHI (62,000 attendees) and AFPM have no call for abstracts at all — 0 contributed.
- **Lapsed congress domains now serve spam** — `esoc2025.com`, `esoc2023.org`, `ecis2025.eu`, and SERMACS 2024's domain return casino or lottery pages. Never cite one.
- **Access quirks**: `euroanalysis2023.ch` 406s to a browser user-agent (use `-A curl/8.0`); `euroanalysis2025.com` 500s on its home page but still serves its PDFs; `medchemfrontiers.org` has a broken TLS chain (`curl -k`); a Dioxin programme PDF carries a real user password, which no browser beats — that is not a rung-5 job.
- **Phase-1 URLs are sometimes not the meeting.** The listed ACS NERM source is ACS's organiser resource portal, not NERM.
- **Duplicates were endemic.** 37 English rows were the same meeting as another row — acronym vs full name, a joint-meeting name, or an aggregate row covering meetings already listed. De-duplicate before any total.

## Pilot results

**Pilot 1** — `scratchpad/chem/pilot_results.json`, 9 easy rows, ~12 searches. Three counted outright
(ACS, CSJ, ASMS), one stated forward figure (Pittcon), five UNKNOWN with a named next step.

**Pilot 2** — `scratchpad/chem/pilot2/RESULTS.json`, **20 deliberately HARD rows, 17 searches**
(0.85 per row, against 1.3 in pilot 1). Run inline on 2026-09-12 against the categories pilot 1 never
touched: Chinese numbered series, Russian съезд series, IMPLIED placeholders, Confit-hosted Japanese
meetings, AIChE, trade fairs and the invite-led series.

| Outcome | Rows |
|---|---|
| `VERIFIED` (counted ≥1,500) | 2 — CCS National Congress **8,719**, Mendeleev Congress **1,798** |
| `BORDERLINE` | 2 — CCS Analytical Chemistry 1,482 (dated), ACHEMA (<900 upper bound) |
| `OUT` on positive evidence | 6 — ROSKATALIZ 291, GEE-RSEQ 180, GEADS ~100, JASIS 0, ARABLAB 0, GRC |
| `NEEDS_RUNG_5` (artefact found, bot-walled) | 2 — AIChE, JSAC/Confit |
| `UNRESOLVED`, next action named | 8 |

**What the hard rows cost: less than the easy ones, not more.** The reason is that the hard
categories are national layers, and national layers have platforms: one crawl settled 210 Chinese
meetings, one PDF settled the whole RSEQ group layer. Budget chemistry waves by *platform*, not by row.

**Ten of twenty rows did not yield a figure.** That is the honest rate on the hard end, and every one
carries a named next action rather than a bare `UNKNOWN`. The two rung-5 rows (AIChE's
`proceedings.aiche.org`, behind Cloudflare; JSAC on Confit) are the highest-value unblocked work left.
