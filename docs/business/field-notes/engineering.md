# Field notes — engineering

Companion to `census-methodology.md`, which stays general. This file holds only what is true of
**engineering** (everything except CS/AI) and would be noise in the general method. Read both before
working an engineering row; add what you learn here, not there.

Started 2026-09-14 from the 30-row phase-2 pilot (wave 1: 30 rows, 10 searches, 26 rows at zero
searches; 11 VERIFIED, 14 BORDERLINE, 5 OUT). The index pass of 2026-09-13 (DBLP + Crossref, 31 rows)
preceded it.

## The unit, and the bar

Accepted contributed presentations = **technical papers + posters presented at one edition**;
plenary / keynote / invited / 依頼 / 特別 / 기조 / 초청 talks excluded; exhibitor, sponsored and industrial
sessions excluded; withdrawn excluded. ≥1,500 counted = VERIFIED; 800–1,499 = BORDERLINE; below 800 on
positive evidence = OUT. A stated total never beats a countable artefact. A two-meetings-a-year
society (IEICE General + Society, JSAE spring + autumn, ASHRAE Annual + Winter) is one row per
meeting or `events_per_yr` = 2 with the per-edition figure — never a summed annual total.

## Scope, and where engineering overlaps other censuses

| Meeting | Counted on |
|---|---|
| AIAA forums, MRS/E-MRS, SPIE, Optica/CLEO/OFC, ASA, TMS | `Census - Physical Sciences` |
| AIChE, chemical engineering, ACHEMA | `Census - Chemistry` |
| BMES, biomedical engineering; EMBC (parked on `Deleted - Engineering`) | `Census - Medicine & Health` |
| ICRA, IROS, ICASSP, ICC, GLOBECOM, VTC, CDC, IECON, ISCAS, SMC, IGARSS and the Crossref series (CCC, CAC, CCDC, IEOM, ENEGEP, COBEM, AHFE, AP-S, ECCE, EuCAP, EAGE, ADIPEC, PIERS, ICOPS, IPEMC, ICMMT, COBRAMSEG, LACCEI, Forum Acusticum) | already on this sheet from the index pass |
| INFORMS | this sheet (Rupert, 2026-09-14); its CS & AI copy is parked as a duplicate |
| Sunbelt (social network analysis) | nowhere yet — waits for a social-sciences sheet |

## Where engineering publishes its counts — routes ranked by yield

1. **Crossref, with the discriminator named per publisher.** Engineering societies deposit
   conference-paper DOIs far more than medicine does; this settled eleven pilot rows at zero
   searches. The thing you group on differs every time:
   - **ASME** (prefix `10.1115`): one container per proceedings **volume**, so a meeting is the SUM
     over its `Volume N: …` containers. The DOI carries the meeting slug (`10.1115/imece2024-…`,
     `gt2024-…`, `omae…`, `detc…`, `pvp…`, `fedsm…`), which is the cleaner key: cursor-page
     `filter=type:proceedings-article,prefix:10.1115,from-pub-date:…&rows=1000&select=DOI,container-title,event&cursor=*`
     and group on `^([a-z-]+[0-9]{4})-` of the DOI suffix. Thirty ASME meetings share the prefix.
     IMECE 2024 = 723 published papers (organiser states ~2,400 papers + presentations + posters — the
     deposit is a FLOOR; presentation-only slots are not deposited); Turbo Expo 2024 = 1,201.
   - **SAE** (`10.4271`): records carry a populated `event` field — filter on `event.name`
     (WCX: 2022 625, 2023 709, 2024 776, 2025 677). The DOI series is NOT a discriminator:
     `2025-01-*` holds 1,481 items of which only 677 are WCX. ~200 oral-only WCX presentations per
     edition are not deposited (floor).
   - **SPE** (`10.2118`): one container per meeting now, not the historic `Day 1 Mon, …` per-day
     containers — check the facet before assuming a sum. Filter on `event.name`. ATCE 2023–2025 =
     330–333 (OUT); ADIPEC alone is 2,039; twenty-plus SPE meetings share the prefix.
   - **IEEE** (`10.1109`): use `&rows=0&facet=container-title:1000` for the year and read the EXACT
     container. Two traps, both hit: `query.container-title` does NOT filter, it only reorders, so
     `total-results` stays the whole prefix (~40,000 in 2025 — using it overstates a row fiftyfold);
     and facet keys are **double** HTML-escaped (`Power &amp;amp; Energy`), so unescape twice before
     matching. PES GM 2024 = 777 conference papers (Transactions-paper track and student posters
     not deposited — floor). Acronym substring matching is fatal: `EPE` matches eight unrelated
     containers; only the exact title is safe.
   - **ASHRAE**: findable only through the member registry, `api.crossref.org/members?query=ASHRAE`
     (member 49508, prefix `10.63044`, 1,094 DOIs in total) — the member record alone settles the
     row: no ASHRAE edition can approach the floor (Winter 2026 = 174).
   - **Copernicus/ISPRS**: deposits every item. Archives ISSN `2194-9034`, **Annals ISSN
     `2194-9050`** (the obvious guess 2194-9042 returns zero and reads like "no deposits" — find
     ISSNs via `api.crossref.org/journals?query=…`). Group on `volume` and filter by volume PATTERN
     (`^XLIII-B\d` Archives, `^V-\d` Annals), never by date: the same years hold dozens of workshop
     volumes. ISPRS Congress 2022 = 2,306 (quadrennial).
   - **IET/CIRED** (`10.1049`): named per-conference containers only up to ~2015 (CIRED 2013 = 742);
     from 2015 IET lumps everything into one `IET Conference Proceedings` container — useless for
     recent editions.
   - **JSME** (`10.1299`): group the DOI suffix on `^([a-z]+)\.([0-9]{4})\.`; `jsmemecj` is the
     national 年次大会; thirty other codes are divisional/regional meetings.
   - **ASEE** (`10.18260`) deposits only its journals, NOT conference papers — the deposit rung is
     inapplicable; use `peer.asee.org` (below). **IISE** and **INFORMS** deposit nothing.
2. **Society statistics pages that itemise by presentation type** — the best artefacts in the
   field, because the organiser makes the invited exclusion for you:
   - **IEICE** 大会実施報告: `ieice.org/jpn_r/activities/taikai/{general|society}/<year>/report_<year>.html`
     (index `…/report.html`, every year since 2006). The 公募セッション table gives 一般 / 公募シンポジウム /
     公募ポスター / 学生・ジュニアポスター counts by society; the 企画セッション table above it counts
     invited SESSIONS and is excluded. General 2025 = 1,784; Society 2025 = 1,111 (47 not 80
     symposium talks — 33 are double-listed across co-hosting societies). **AWS WAF challenge**:
     `curl` gets HTTP 202 with an empty body; a browser clears it (rung 5).
   - **KIEE** `conf.kiee.or.kr/pages/submission_statistics.vm` — a 46-row 논문제출현황 table summing
     exactly to 1,435 (Summer 2025). Recorded as submissions; a members' meeting with no evident
     rejection stage.
   - **CSTAM** (China) news page itemises 9 plenary + 340 invited + 2,000余 contributed thematic
     talks for CCTAM 2025 — reachable only through the Wayback Machine (`web.archive.org/web/2025id_/<url>`)
     because `cstam.org.cn` 403s every path.
   - **FEMS EUROMAT**: the host society's highlights page carries a statistics panel whose numbers
     are JavaScript count-up animations — the values live in `data-` attributes, invisible to text
     extraction but readable in the raw HTML. 1,446 contributed (2025), 9 plenaries + 189
     highlights excluded.
3. **Society programme hosts serving static HTML** (count session codes or ID ranges):
   - **gakkai-web.net** — IEEJ's whole 全国大会 programme at
     `gakkai-web.net/iee/program/<year>/data/html/general/general_l.html` (分野別一覧 prints a
     lecture-number RANGE per session, `1-001〜1-010`; expand the ranges). The parent directory
     `/gakkai/iee/` 403s but the programme path serves. Does NOT host IEICE. IEEJ 2026 = 1,263.
   - **AIJ** 大会学術講演梗概集目次検索: the form on `aij.or.jp/scripts/annual/annual.htm` posts to a
     SEPARATE host, `scripts.aij.or.jp/scr/annual/annual.asp`, which is not behind the AWS WAF wall
     that blocks `www.aij.or.jp` (recover the form HTML from Wayback). AIJ 2024 = 6,645.
   - **JSCE** 学術論文等公開ページ `jsce.or.jp/library/open/proc/maglist2/00035/<year>/mg01.htm` — per-year,
     per-section tables with one PDF per paper (IDs `I-…` to `VII-…`, `CS…`). **2023 is the newest
     open edition**; 2024+ redirect to a member-login `.asp` (credential wall, not rung 5). 2023 = 4,188.
   - **KSME** `ksme.or.kr/Proceedings/<year>a/` (classic ASP, cp949): `TrackList.asp?ST_TYPE=<0 oral|1 poster>&ST_DATE=<YYYYMMDD>`
     lists sessions, `SessionPaperList.asp?code=<n>` lists papers. 2024 = 1,350.
   - **DEGA** `pub.dega-akustik.de/<edition>/konferenz.html?sessions=all` — one directory per DAGA
     since 2014, session pages with time-slot markers. DAGA 2025 = 617 (OUT).
   - **IAF** `iafastro.directory/iac/archive/browse/IAC-<yy>/` — a three-level plain-HTML paper
     archive (symposium → session → paper). **The host returns empty pages intermittently: retry on
     empty and sanity-check that no symposium reports zero** (first crawl 3,150, retried 4,008).
   - **IAEE** `proceedings-wcee.org` — every WCEE since 1954; the DataTables grid renders nothing to
     curl, but the page's initialiser names an ajax URL; call it with empty filters and read
     `recordsTotal` (conference=18 → 3,163; 17 → 2,807; 16 → 2,129).
   - **CIRED repository** is DSpace 7: the Angular shell is empty, but the REST API
     `cired-repository.org/server/api/discover/search/objects?dsoType=item&scope=<collection>`
     counts items. Holds only 2019 and the 2018 workshop (DATED).
   - **peer.asee.org** is Cloudflare-blocked; the Wayback copy of
     `peer.asee.org/collections/<year>-asee-annual-conference-exposition` counts. 2025 = 2,466.
   - **CIGRE** Special Reports: 16 free rapporteur PDFs (one per Study Committee) under
     `session.cigre.org/fileadmin/…/Special_reports/` cover every accepted paper; IDs are five
     digits starting with 1, but the sixteen reports use sixteen citation styles — a `Paper NNNNN`
     literal returns 0 for seven committees. 2026 = 1,552 (biennial).
   - **congressarchive.cimne.com** — durable host for ECCOMAS/IACM programme PDFs
     (`eccomas_2024/assets/eccomas-2024.pdf`, 220 pp; restrict the count to the programme section).
   - **USACM Google Sites mirror** for WCCM 2024 (`wccm2024.usacm.org`) links the full book of
     abstracts on Google Cloud Storage; the congress's own domains are dead.
   - **TRA** publishes a single open "digital booklet" PDF; count `Presenter:` lines (971).
4. **Wayback CDX to enumerate a society's file server** when directory listing is forbidden:
   `web.archive.org/cdx/search/cdx?url=<host>/<path>*&output=text&collapse=urlkey&filter=statuscode:200[&filter=mimetype:application/pdf]`
   found TRB's final programme, IISE's onsite brochure and INFORMS' 2018 abstract book. **Check
   content-type**: `onlinepubs.trb.org` serves an HTML error page with HTTP 200 where a PDF is
   expected; the `id_` Wayback copy is the real file.
5. **WordPress REST on society meeting sites**: `meetings.informs.org/wordpress/<meeting>/wp-json/wp/v2/media?search=prospectus`
   surfaces the exhibitor prospectus (attendance); `/wp-json/` route list shows whether a custom
   abstract post type exists (INFORMS: no).
6. **J-STAGE search API** `api.jstage.jst.go.jp/searchapi/do?service=3&cdjournal=<code>&pubyearfrom=<Y>&pubyearto=<Y>&count=1`
   → `opensearch:totalResults`. `service=3` needs `cdjournal` or `issn`; `material=<Japanese
   title>` returns `ERR_001` even for titles that exist — never read ERR_001 as "does not deposit".

## Routes that failed, and the wall each hit

| Host | Wall | What to do |
|---|---|---|
| `www.ieice.org`, `www.aij.or.jp` | AWS WAF JavaScript challenge: HTTP 202, empty body (`awsWafCookieDomainList`, `gokuProps`) | Browser (rung 5); or the unwalled sibling host (AIJ `scripts.aij.or.jp`) |
| `cstam.org.cn`, `peer.asee.org`, `fcrc.acm.org`, `www.siam.org` | HTTP 403 (Cloudflare / bot wall) | Wayback `id_` copy; DSpace/REST endpoints; legacy hosts |
| `cctam2025.cstam.org.cn` | Vue SPA shell (逸云智会 / `vip.yiyum.com`) — the Chinese Confit | Browser only; prefer the society news page |
| `iise.org/ConferenceArchives`, JSCE 2024+, INFORMS searchable programme, ASME/SAE digital libraries | **Credential walls** (member/attendee login) — NOT rung 5 | Older open editions via Wayback CDX; the deposit index |
| `wccm2024.org`, `wccm-panacm2024.org`, `wccm-apcom2022.org` | domains dead | USACM mirror |
| Zenodo for TRA, HAL for CFM, Scipedia for ECCOMAS/WCCM | **Voluntary author deposits, not proceedings** (HAL CFM2025 = 132 of 850+; counting them understates several-fold) | Never use a repository collection as a congress count |
| `gakkai-web.net/ieice/` | 403 — the host does not carry IEICE | IEICE's own report pages |

## Counting rules this field needs

- **Per-volume and per-container sums** (ASME volumes, ISPRS volumes, SPE historic day containers).
- **Deposit indexes are floors** where presentation-only slots exist (IMECE 723 deposited vs ~2,400
  stated; SAE WCX +~200 oral-only; PES GM +Transactions track). Record `confidence = floor` and
  keep the organiser's statement as a disagreement, never as the figure.
- **Range arithmetic**: IEEJ prints lecture-number ranges per session; TRB prints poster-board
  ranges per day (`-raw` 981 vs `-layout` 1,053 — the two extractions DISAGREE, the lower was
  recorded as a floor). Expand ranges, dedupe IDs.
- **Two-column PDFs** (INFORMS abstract book) defeat `-layout`; anchor on session codes instead.
- **Double-listed co-hosted sessions** (IEICE: 80 symposium talks listed, 47 actual) — read the
  footnote.
- **Short-paper conventions in Japan and Korea**: a 講演 / 논문 is 2–6 pages and the counts run high
  (AIJ 6,645, JSCE 4,188, IEICE 1,784, KIEE 1,435). They clear the bar on volume; consistent with
  how the chemistry census treated CSJ.
- **Cadence**: WCEE and ISPRS quadrennial (0.25); WCCM, ECCOMAS, CIGRE, EUROMAT, CIRED, TRA, CFM,
  CCTAM biennial (0.5); IEICE and JSAE two meetings a year, one row each; KIEE Summer is its own
  numbered series (1/yr) although KIEE also runs an autumn conference.
- **Session counts are not presentation counts** (WEFTEC "125+ technical sessions"): treat as
  sessions × papers-per-session, labelled DERIVED, or go to rung 9.

## Traps

- **Acronym collisions in Crossref**: `EPE` (eight IEEE containers), `SPE` (shares prefix with
  ADIPEC etc.), `-01` SAE series. Exact container title or `event.name` only.
- **Expo headcounts**: TRB 13,000, WEFTEC 23,000, SAECCE 10,000 and IAC's "nearly 6,400 abstracts"
  (submissions; 4,008 presented) say nothing until the presentation count is found. IEICE's 延べ
  参加人数 is cumulative daily attendance, not unique delegates.
- **Post-COVID series breaks**: JSME 年次大会 ran 1,089–1,662 to 2020, then 528 / 612 / 741
  (2023–2025). The current edition decides the tier; the series is recorded for Rupert.
- **Two J-STAGE titles for one society** (JSME): pick the national meeting's code.
- **A 403 on a parent directory is not a wall on the child path** (gakkai-web.net).
- **HTTP 200 is not a file**: check content-type and size before counting a "PDF".

## Wave 1 results (2026-09-14) — the pilot

| Row | Conference | Figure | Rung | Tier |
|---|---|---|---|---|
| 104 | AIJ Taikai | 6,645 (2024) | 4 | VERIFIED |
| 88 | INFORMS Annual Meeting | 5,122 (2018, DATED) | 3 | VERIFIED |
| 105 | JSCE Annual Meeting | 4,188 (2023) | 4 | VERIFIED |
| 139 | IAC | 4,008 (2024) | 4 | VERIFIED |
| 133 | WCEE | 3,163 (2024) | 4 | VERIFIED (0.25/yr) |
| 135 | WCCM | 2,800 (2024) | 3 | VERIFIED (0.5) |
| 93 | ASEE | 2,466 (2025) | 4 | VERIFIED |
| 136 | ECCOMAS | 2,368 (2024) | 3 | VERIFIED (0.5) |
| 165 | ISPRS Congress | 2,306 (2022) | 4 | VERIFIED (0.25) |
| 108 | IEICE General Conference | 1,784 (2025) | 5 | VERIFIED |
| 154 | CIGRE Session | 1,552 (2026) | 3 | VERIFIED (0.5) |
| 199 | CCTAM | ~2,000 stated | 2 | BORDERLINE (0.5) |
| 166 | FEMS EUROMAT | 1,446 | 2 | BORDERLINE (0.5) |
| 124 | KIEE Summer | 1,435 | 4 | BORDERLINE |
| 122 | KSME | 1,350 | 3 | BORDERLINE |
| 107 | IEEJ | 1,263 | 3 | BORDERLINE |
| 71 | ASME Turbo Expo | 1,201 | 4 | BORDERLINE |
| 109 | IEICE Society Conference | 1,111 (2025) | 5 | BORDERLINE |
| 87 | IISE | 1,025 (2013, DATED) | 3 | BORDERLINE |
| 79 | TRB Annual Meeting | 981 posters only (2017, floor) | 6 | BORDERLINE |
| 174 | TRA | 971 | 3 | BORDERLINE (0.5) |
| 155 | CIRED | 820 (2019, DATED) | 4 | BORDERLINE (0.5) |
| 99 | IEEE PES GM | 777 floor | 4 | BORDERLINE |
| 80 | SAE WCX | 776 + ~200 oral-only | 4 | BORDERLINE |
| 70 | ASME IMECE | 723 floor / ~2,400 stated | 4 | BORDERLINE |
| 181 | CFM | none; 850 delegates × 0.9 | 9 | BORDERLINE |
| 106 | JSME 年次大会 | 741 (2025) | 4 | OUT (orchestrator; series break) |
| 182 | DAGA | 617 | 3 | OUT |
| 156 | EPE ECCE Europe | 518 | 4 | OUT |
| 82 | SPE ATCE | 330 | 4 | OUT |
| 86 | ASHRAE | 174 | 4 | OUT |

Rows for Rupert's eye: JSME (OUT on 741 against a pre-COVID 1,200+ series); TRB (posters only,
2017 — the lectern count would likely lift it to VERIFIED, needs the AMOnline programme in a
browser); IMECE (deposit floor 723 vs 2,400 stated); INFORMS and IISE dated figures.
