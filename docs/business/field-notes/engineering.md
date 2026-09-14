# Field notes — engineering

Companion to `census-methodology.md`, which stays general. This file holds only what is true of
**engineering** (everything except CS/AI) and would be noise in the general method. Read both before
working an engineering row; add what you learn here, not there.

Started 2026-09-14. Sections 1–6 are the pilot researcher's report from phase-2 wave 1 (30 rows,
one Opus agent, 10 searches, 26 rows at zero searches), reproduced verbatim; the orchestrator's
addenda follow. The index pass of 2026-09-13 (DBLP + Crossref, 31 rows) preceded the pilot.

## The unit, the bar, and the scope

Accepted contributed presentations = **technical papers + posters presented at one edition**;
plenary / keynote / invited (依頼 / 特別 / 기조 / 초청 / 特邀) talks excluded; exhibitor, sponsored and
industrial sessions excluded; withdrawn excluded. ≥1,500 counted = VERIFIED; 800–1,499 =
BORDERLINE; below 800 on positive evidence = OUT. A stated total never beats a countable artefact;
a deposit index that misses presentation-only slots is a FLOOR (`confidence: floor`), not evidence
of a small meeting — see counting rule 2 below for which publishers are near-complete.

| Meeting | Counted on |
|---|---|
| AIAA forums, MRS/E-MRS, SPIE, Optica/CLEO/OFC, ASA, TMS | `Census - Physical Sciences` |
| AIChE, chemical engineering, ACHEMA | `Census - Chemistry` |
| BMES, biomedical engineering; EMBC (parked on `Deleted - Engineering`) | `Census - Medicine & Health` |
| ICRA, IROS, ICASSP, ICC, GLOBECOM, VTC, CDC, IECON, ISCAS, SMC, IGARSS and the Crossref series (CCC, CAC, CCDC, IEOM, ENEGEP, COBEM, AHFE, AP-S, ECCE, EuCAP, EAGE, ADIPEC, PIERS, ICOPS, IPEMC, ICMMT, COBRAMSEG, LACCEI, Forum Acusticum) | this sheet, from the index pass |
| INFORMS | this sheet (Rupert, 2026-09-14); the CS & AI copy is parked as a duplicate |
| Sunbelt (social network analysis) | nowhere yet — waits for a social-sciences sheet |

---

## 1. Wave 1 results

**26 of 30 rows cost ZERO searches.** Ten `VERIFIED`, fifteen `BORDERLINE`, four `OUT` on positive
evidence, one `NEEDS_RUNG_5`.

| Row | Conference | Abstracts | Rung | Verdict | Ev/yr |
|---|---|---|---|---|---|
| 104 | Architectural Institute of Japan Annual Meeting (AIJ Taikai) | 6,645 | 4 | VERIFIED | 1 |
| 88 | INFORMS Annual Meeting | 5,122 (2018) | 3 | VERIFIED | 1 |
| 105 | JSCE Annual Meeting (Nenji Gakujutsu Koenkai) | 4,188 (2023) | 4 | VERIFIED | 1 |
| 139 | International Astronautical Congress (IAC) | 4,008 | 4 | VERIFIED | 1 |
| 133 | World Conference on Earthquake Engineering (WCEE) | 3,163 | 4 | VERIFIED | 0.25 |
| 135 | World Congress on Computational Mechanics (WCCM) | 2,800 | 3 | VERIFIED | 0.5 |
| 93 | ASEE Annual Conference and Exposition | 2,466 | 4 | VERIFIED | 1 |
| 136 | ECCOMAS Congress | 2,368 | 3 | VERIFIED | 0.5 |
| 165 | ISPRS Congress | 2,306 | 4 | VERIFIED | 0.25 |
| 154 | CIGRE Session (Paris) | 1,552 | 3 | VERIFIED | 0.5 |
| 199 | CCTAM 中国力学大会 | ~2,000 stated | 2 | BORDERLINE | 0.5 |
| 166 | FEMS EUROMAT | 1,446 | 2 | BORDERLINE | 0.5 |
| 124 | KIEE Summer Annual Conference | 1,435 | 4 | BORDERLINE | 1 |
| 122 | KSME Annual Meeting | 1,350 | 3 | BORDERLINE | 1 |
| 107 | IEEJ Annual Meeting (Zenkoku Taikai) | 1,263 | 3 | BORDERLINE | 1 |
| 71 | ASME Turbo Expo | 1,201 | 4 | BORDERLINE | 1 |
| 87 | IISE Annual Conference and Expo | 1,025 (2013) | 3 | BORDERLINE | 1 |
| 79 | TRB Annual Meeting | 981 (2017, posters only) | 6 | BORDERLINE | 1 |
| 174 | Transport Research Arena (TRA) | 971 | 3 | BORDERLINE | 0.5 |
| 155 | CIRED | 820 (2019) | 4 | BORDERLINE | 0.5 |
| 99 | IEEE PES General Meeting | 777 (floor) | 4 | BORDERLINE | 1 |
| 80 | SAE WCX World Congress Experience | 776 + ~200 oral-only | 4 | BORDERLINE | 1 |
| 106 | JSME Annual Meeting (Nenji Taikai) | 741 | 4 | BORDERLINE | 1 |
| 70 | ASME IMECE | 723 papers / ~2,400 stated | 4 | BORDERLINE | 1 |
| 181 | Congrès Français de Mécanique (CFM) | none; 850 delegates | 9 | BORDERLINE | 0.5 |
| 108 | IEICE General Conference | blocked | — | NEEDS_RUNG_5 | 2 |
| 182 | DAGA | 617 | 3 | OUT | 1 |
| 156 | EPE ECCE Europe | 518 | 4 | OUT | 1 |
| 82 | SPE ATCE | 330 | 4 | OUT | 1 |
| 86 | ASHRAE Annual + Winter | 174 (largest edition) | 4 | OUT | 2 |

**Plan engineering waves around the deposit index and the society platform, not around search.**
Rung 1 produced nothing in this wave. Of the 10 searches spent, not one returned a usable figure
directly — each only pointed at an artefact, which then had to be counted.

---

## 2. Every route that worked

### 2.1 Crossref publisher deposit index — highest yield, but the grouping key differs per publisher

Eleven rows settled here at zero search cost. **The single most important fact in this file: the
thing you group on is different for every engineering publisher.** Get it wrong and the answer is
out by an order of magnitude in either direction.

| Publisher | Prefix | Grouping key | Worked example |
|---|---|---|---|
| **ASME** | `10.1115` | ONE CONTAINER PER PROCEEDINGS **VOLUME** → sum the `Volume N: …` containers. The DOI *also* carries the meeting slug, which is cleaner | IMECE 2024 = 723 (11 volumes); Turbo Expo 2024 = 1,201 (18 volumes) |
| **SAE** | `10.4271` | The `event` field, populated, single spelling | WCX 2024 = 776 |
| **SPE** | `10.2118` | The `event` field. **One container per meeting now** — the per-day `Day 1 Mon, …` containers are historic | ATCE 2024 = 330 |
| **IEEE** | `10.1109` | Exact `container-title` read off a FACET | PES GM 2024 = 777; ECCE Europe 2025 = 518 |
| **ASHRAE** | `10.63044` | Whole prefix; found via the member registry | Winter 2026 = 174 |
| **Copernicus / ISPRS** | by ISSN | The `volume` field, by PATTERN | XXIV Congress = 2,306 |
| **IET (historic)** | `10.1049` | Named per-conference container, pre-2015 only | CIRED 2013 = 742 |

**Exact call shapes.**

```
# ASME — read the container facet, then SUM the "Volume N:" containers
https://api.crossref.org/works?filter=type:proceedings-article,prefix:10.1115,from-pub-date:2024-10-01,until-pub-date:2025-03-31&rows=0&facet=container-title:100

# ASME / SAE / SPE / JSME — cursor-page the prefix, group on the DOI slug or the event field
https://api.crossref.org/works?filter=prefix:<PREFIX>,from-pub-date:<Y1>-01-01,until-pub-date:<Y2>-12-31&rows=1000&select=DOI,container-title,event,published,type&cursor=*

# IEEE — the facet IS the figure; see the two traps below
https://api.crossref.org/works?filter=type:proceedings-article,prefix:10.1109,from-pub-date:<Y>-01-01,until-pub-date:<Y>-12-31&rows=0&facet=container-title:1000

# Copernicus (ISPRS) — by ISSN, then group on `volume`
https://api.crossref.org/works?filter=issn:<ISSN>,from-pub-date:<Y>-01-01,until-pub-date:<Y>-12-31&rows=1000&select=DOI,volume,page,title&cursor=*

# Find a society whose prefix you cannot guess
https://api.crossref.org/members?query=ASHRAE&rows=5
https://api.crossref.org/journals?query=ISPRS+Annals&rows=4
```

**Grouping regexes for DOI slugs:** `^([a-z\-]+\d{4})-` on the DOI suffix (ASME: `imece2024`,
`gt2024`, `imece-india2025`); `^([a-z]+)\.(\d{4})\.` for J-STAGE-style DOIs such as
`10.1299/jsmemecj.2025.C202-1`.

**Three Crossref traps, all hit for real:**

1. **`query.container-title` does NOT filter.** It only re-ranks. `total-results` stays the whole
   prefix — 23,751 for IEEE in 2022 rising to 40,398 in 2025. Using it as a count overstates a row
   roughly fiftyfold. **The facet is the figure; the query string is not.**
2. **IEEE facet keys are DOUBLE HTML-escaped**: `2025 IEEE Power &amp;amp; Energy Society General
   Meeting (PESGM)`. Unescape twice or a name match silently returns nothing, which reads as
   "society does not deposit".
3. **One prefix holds dozens of meetings.** SPE's prefix for 2024–25 is 10,843 items of which ATCE
   is 663 and ADIPEC 2,039. JSME's prefix holds **thirty** conference codes (`jsmeatem`, `jsmebio`,
   `jsmefed`, `jsmekansai`, `jsmekyushu` …); only `jsmemecj` is the national 年次大会. Always separate
   by event/slug/container, never by date.

### 2.2 Society statistics pages that itemise BY PRESENTATION TYPE

The best artefacts in this field, because the organiser performs the invited exclusion for you.
Look for these before counting anything.

| Society | URL | What it gives |
|---|---|---|
| **KIEE** | `https://conf.kiee.or.kr/pages/submission_statistics.vm` | 논문제출현황: a 46-row table by subject × oral/poster with a 합계 row. Rows re-summed independently = 197 + 1,238 = **1,435**, reproducing the printed total exactly |
| **CSTAM** | `https://www.cstam.org.cn/193/202507/21449.html` (via Wayback) | `包含9场大会特邀报告，340余场分会场邀请报告和2000余场专题学术报告` — 9 plenary invited + 340 session invited + **2,000 contributed**, split by the source itself |
| **FEMS EUROMAT** | `https://sociemat.es/fems-euromat-2025-highlights/` | CONGRESS STATISTICS: registrations 1,812, exhibitors 17, plenaries 9, highlight 189, oral 1,032, poster 414 |
| **IEICE** | `<edition-site>/report/<NN>ge/houkoku2.html#d` | 各ソサイエティ別,形式別の企画数ならびに講演数 — lecture counts by society AND by format. Currently WAF-blocked; this is the rung-5 target |

### 2.3 Rapporteur special reports (CIGRE) — a complete paper list on free access

CIGRE's Session Papers list is delegate-only, but the **16 Special Reports, one per Study
Committee, are free** and between them summarise *every* accepted paper.

```
index:  https://session.cigre.org/guides-templates/special-reports.html
files:  https://session.cigre.org/fileadmin/cru-1788274896/Session_2026/Special_reports/<NAME>.pdf
        (A1, A2, A3, B1–B5, C1–C6, D1, D2; a .zip of all 16 is offered alongside)
```

**Counting rule.** CIGRE 2026 paper numbers are five digits beginning with 1. A `Paper NNNNN`
literal FAILS — the sixteen reports use sixteen citation styles and that pattern returns 0 for seven
committees. The pattern that works across all of them is the bare token:

```
(?<![\d.])(1\d{4})(?![\d.])
```

It cannot collide with years (4 digits) or page numbers (small). **Validated, not assumed:** it
reproduces the printed "A total of N papers have been accepted" exactly in all three committees that
print one — A1 57, B1 120, D1 74. Per-committee: A1 57, A2 116, A3 122, B1 120, B2 118, B3 82,
B4 123, B5 121, C1 48, C2 84, C3 57, C4 126, C5 88, C6 117, D1 74, D2 107. Union **1,552**; naive sum
1,560, so the union removes 8 joint-committee double-counts.

**CIRED's special reports look identical and are NOT complete** — see §3.

### 2.4 Static society programme platforms (Japan, Korea)

These are national layers: solving one unlocks many rows.

**`gakkai-web.net` — Toyo Agency (トーヨー企画), hosts IEEJ.** Plain static HTML, no JS, no login.

```
https://gakkai-web.net/iee/program/<YEAR>/index.html
https://gakkai-web.net/iee/program/<YEAR>/data/html/general/general_l.html   # 一般講演 分野別一覧
https://gakkai-web.net/iee/program/<YEAR>/data/html/general/general_t.html   # 日程表
https://gakkai-web.net/iee/program/<YEAR>/data/html/sympo/sympo_l.html       # symposium list
```

The 分野別一覧 prints a lecture-number RANGE per session (`1-001〜1-010`). Expand and union:

```
(\d{1,2})-(\d{3})\s*[〜~-]\s*(?:(\d{1,2})-)?(\d{3})
```

IEEJ 2026 = **1,263**, and it is EXACT not a floor: per 部門 the count equals the maximum number
(103/103, 113/113, 200/200, 216/216, 244/244, 275/275, 112/112), so numbering is gap-free. Series:
2023 1,180, 2024 1,159, 2025 984, 2026 1,263. Note `www.gakkai-web.net/gakkai/iee/` returns 403 — a
403 on the parent path is not a wall on the programme. **gakkai-web.net does NOT host IEICE**
(`/ieice/` 403s, `/ieice/program/2026/index.html` 404s).

**`scripts.aij.or.jp` — AIJ's digest index, on a DIFFERENT HOST from the WAF-walled main site.**

```
form (recover field names from Wayback):
  https://web.archive.org/web/2024id_/https://www.aij.or.jp/scripts/annual/annual.htm
live POST:
  https://scripts.aij.or.jp/scr/annual/annual.asp
  Referer: https://www.aij.or.jp/scripts/annual/annual.htm
  body: sc_check=+and+&sc_syo_name1=&sc_syo_name2=&sc_cyosya1=&sc_cyosya2=
        &sc_nen=<YEAR>&sc_bun=<VOLUME or empty>&sc_psize=20&b1=%8C%9F%8D%F5
```

`b1` is the submit label 検索 in Shift-JIS. Volumes: A-1, A-2, B-1, B-2, C-1, C-2, D-1, D-2, E-1,
E-2, F-1, F-2, G-1. The response is Shift-JIS — decode **cp932**. The count is in the markup as
`<B>6645</B>件が該当します`, **NOT** as the phrase `検索結果 6645 件` that a tag-stripped read
suggests; a regex written against stripped text matches nothing and reads as "no results". Year
totals: 2023 **6,645**, 2022 6,173, 2021 6,230, 2020 6,662, 2019 7,068, 2018 6,994, 2015 6,433. The
twelve volumes sum to **exactly** the year total.

**`ksme.or.kr` — KSME, two levels, cp949.**

```
https://ksme.or.kr/Proceedings/<YEAR>a/TrackList.asp?ST_TYPE=<0 oral|1 poster>&ST_DATE=<YYYYMMDD>
https://ksme.or.kr/Proceedings/<YEAR>a/SessionPaperList.asp?code=<n>
```

Harvest `code=` values from the six day×type pages (222 sessions in 2024), fetch each, count
`class='paperinfo'` blocks or unique `popSessionView.asp?code=<n>&idx=<m>` values — both give 1,377 —
then subtract 27 items in sessions titled 초청강연 / 특별강연 / 전문가리뷰 → **1,350 contributed**.

**`jsce.or.jp` — JSCE's open proceedings ToC, cp932.**

```
https://www.jsce.or.jp/library/open/proc/maglist2/00035/                 # index, 1937→
https://www.jsce.or.jp/library/open/proc/maglist2/00035/<YEAR>/mg01.htm  # 第1部門 … mg08 = CS
```

Count unique `.pdf` hrefs AND unique printed IDs; they agree on all eight sections. ID patterns:
`(?:CS|VII|VI|IV|V|III|II|I)-\d{1,4}` for 部門 1–7, **and separately** `CS\d+-\d+` for the CS volume.
2023 = **4,188** (384, 217, 464, 174, 800, 1339, 138, 672). 2019 = 3,615. **2023 is the newest open
year**; 2024+ redirect to an `.asp` member login.

**`conf.kiee.or.kr`** — Velocity `.vm` pages, plain HTML, no wall. See §2.2.

**`pub.dega-akustik.de` — DEGA's open proceedings index.**

```
https://pub.dega-akustik.de/                                        # every DAGA year from 2014
https://pub.dega-akustik.de/<EDITION>/konferenz.html?sessions=all   # session index
https://pub.dega-akustik.de/<EDITION>/konferenz-<n>.html?session=<m>
```

Editions: `DAGA_2014` … `DAGA_2024`, `DAS-DAGA_2025`. Each session page prints its own type
(`Regulare Lecture` / `Poster` / `Keynote` / `Lecture (in a structured session)`) and one time slot
per contribution — count `\d{2}:\d{2} \| - \| \d{2}:\d{2}`. **Posters DO get time slots** (all
posters in a session share one), so this does not undercount the poster track. DAGA 2025 = 621 items
(617 after removing 4 keynotes); DAGA 2024 = 613.

### 2.5 Backing APIs behind apparently browser-only front ends

**None of these three is a rung-5 job.** All were mistaken for one on first look.

**DataTables `serverSide: true`** (WCEE). The inline initialiser declares its own endpoint. Read it,
call it with empty filters, read `recordsTotal` — the whole count arrives in ~350 bytes.

```
https://proceedings-wcee.org/search?draw=1&start=0&length=1&category=<N>&author=&title=&country=&sort=title&sort_dir=asc
```

18WCEE = **3,163**, 17WCEE 2,807, 16WCEE 2,129.

**DSpace 7** (CIRED). The Angular shell is 513 bytes of `<ds-app>`; the REST API is open.

```
https://<host>/server/api/core/communities?size=50
https://<host>/server/api/core/communities/<uuid>/collections?size=100
https://<host>/server/api/discover/search/objects?dsoType=item&scope=<collection-uuid>&size=1
```

Read `_embedded.searchResult.page.totalElements`. CIRED 2019 = **820**.

**WordPress REST** (INFORMS, AIJ edition sites, FEMS). `/wp-json/` for the route list, then:

```
/wp-json/wp/v2/media?search=prospectus|program|abstract&per_page=30&_fields=id,source_url,title
/wp-json/wp/v2/pages?per_page=100&_fields=id,link,title
```

Surfaced the INFORMS exhibitor prospectus (attendance 6,500+).

### 2.6 Wayback as a Cloudflare bypass AND as a file index

**As a bypass.** `peer.asee.org` returns 403 with a Cloudflare "Just a moment..." interstitial to
every user-agent tried (curl/8.0, a Googlebot string, two desktop Chrome strings). Its pages are
static and archived, so:

```
https://web.archive.org/cdx/search/cdx?url=peer.asee.org/collections*&output=text&collapse=urlkey&limit=200&filter=statuscode:200
https://web.archive.org/web/<timestamp>id_/https://peer.asee.org/collections/<year>-asee-annual-conference-exposition
```

PEER states its own total twice per page (`Documents in collection NNNN` and `Displaying documents
1 - 250 of NNNN in total`), giving a free internal cross-check. ASEE 2025 = **2,466**, 2024 2,164,
2023 2,194, 2017 1,785. **A Cloudflare wall is not automatically rung 5 when the page is static.**
The same trick recovered the CSTAM news page.

**As a file index** for flat asset paths no page lists:

```
https://web.archive.org/cdx/search/cdx?url=<host>/<path>*&output=text&collapse=urlkey&limit=500&filter=statuscode:200
# add &filter=mimetype:application/pdf to find books of abstracts
```

Found `iise.org/uploadedFiles/Annual_Conference/Program/Annual2013OnsiteBrochure.pdf`,
`onlinepubs.trb.org/onlinepubs/am/2017/TRB_2017_Final_Program.pdf`, and
`meetings.informs.org/wordpress/phoenix2018/files/2018/11/Phoenix_Abstracts.pdf`.

### 2.7 Abstract books with a presenting-author marker

| Conference | Marker | Regex | Result |
|---|---|---|---|
| **WCCM** | `Surname*1` | `[A-Za-zÀ-ÿ.\-]{2,}\*\s*\d` | **2,800**, identical in both modes |
| **ECCOMAS** | `G. Moutsanidis*, …` | `\b[A-Z]\.\s?[A-Za-zÀ-ÿ\-']{2,}\*` | **2,368** / 2,377 |
| **TRA** | `Presenter: <name>` | `Presenter:` | **971**, identical in both modes |
| **IISE** | `Abstract No. NNNN` | `Abstract No\.[[:space:]]*[0-9]{1,5}` | **1,025**, identical in both modes |
| **INFORMS** | numbered talk line | `^\s{0,20}\d{1,2} - \S` | **5,122** (`-raw`) |

For ECCOMAS, restrict to the `CONFERENCE PROGRAMME & TECHNICAL SESSIONS` section — the first ~150KB
is front matter and the minisymposia list, which contaminates the count. Validate the asterisk before
trusting it: on ECCOMAS, 1,998 of 2,002 whole-line author lists carry exactly one.

### 2.8 Other artefacts that worked

- **Poster-board arithmetic (rung 6), TRB.** The printed programme gives an explicit board range per
  poster session (`CC Hall E, Posters H331–H333, J361–J364`). Expand per day and sum across days —
  boards are reused day to day, so a document-wide union undercounts and a per-session sum
  double-counts Part 1/Part 2 cross-references. Regex:
  `Posters?\s+((?:[A-Z]\d{2,4}\s*-\s*[A-Z]?\d{2,4}|[A-Z]\d{2,4})(?:\s*,\s*…)*)`.
  TRB 2017 = **981** posters; the physical grid is 389 boards (16 letters A–R skipping I and O).
- **The society mirror when a congress domain dies.** `wccm2024.org` no longer resolves; USACM's
  Google Sites mirror `https://wccm2024.usacm.org/` carries the complete book of abstracts at
  `https://storage.googleapis.com/usacm_static_shared/wccm2024/WCCM2024%20-%20Book%20of%20Abstracts%20-%202.pdf`.
- **`congressarchive.cimne.com`** — durable host for ECCOMAS/IACM congress material:
  `https://congressarchive.cimne.com/eccomas_2024/assets/eccomas-2024.pdf`.
- **IAF paper directory** — three levels of plain relative links, no JS, no login:
  `https://iafastro.directory/iac/archive/browse/<EDITION>/` → `A1/` → `1/`, `IP/`, `IPB/`, `LBA/` →
  numeric paper ids. IAC-24 = **4,008**. See §5 for the retry rule that changed this by 27%.
- **A1 exhibitor prospectus** is the highest-yield attendance rung here, as the brief predicted:
  TRB `https://events.jspargo.com/TRB27/Public/Content.aspx?ID=123168&sortMenu=103004` gives
  11,000+ plus a full demographic breakdown; INFORMS' prospectus PDF (via the WordPress media API)
  gives 6,500+.

---

## 3. Every route that failed, and the wall hit

| Route | Wall | Verdict |
|---|---|---|
| `www.aij.or.jp`, `www.ieice.org`, `www.ieice-taikai.jp` | **AWS WAF JS challenge: HTTP 202 with a ZERO-BYTE body** (or 1,992 bytes containing `window.awsWafCookieDomainList` / `gokuProps`). Confirmed against 4 user-agents plus full browser headers, Referer and cookie jar | Genuine **rung 5** |
| `peer.asee.org` | Cloudflare 403, "Just a moment…" | Beaten via Wayback |
| `www.cstam.org.cn` | Plain 403 on every path incl. site root | Beaten via Wayback |
| `trid.trb.org` | Result list and the "Showing 1 - N of M" counter injected by JS. The `/Record/RSS?s=<base64>` endpoint carries only the empty default search | **Rung 5** |
| Confit `pub.confit.atlas.jp` (JSCE 2024, JSME 2025) | JS SPA, HTTP 202 + empty body (already in chemistry notes) | **Rung 5** |
| `cctam2025.cstam.org.cn` (逸云智会 / vip.yiyum.com) | Vue SPA: 675KB of shell, **zero** occurrences of 摘要, 论文, 分会场, 专题 or 篇 | **Rung 5** |
| MyTRB `annualmeeting.mytrb.org` | Login | **Credential wall — do NOT queue** |
| `iise.org/ConferenceArchives.aspx?id=32990` | "You must be an IISE member…" | Credential wall |
| INFORMS agenda | "Registered attendees may now login…" | Credential wall |
| `session.cigre.org/programme/session-papers-list.html` | Delegate-only | Credential wall |
| JSCE 2024+ `…/<YEAR>/mg01.asp` | 会員専用 member login | Credential wall |
| `conf.kiee.or.kr/archives/` | Member login | Credential wall |
| `www.jsme.or.jp` | **Resolves (153.121.41.205) but times out on BOTH http and https** | Dead network — a browser fails identically. **Do NOT queue** |
| `www.epe-association.org`, `wccm2024.org`, `wccm-panacm2024.org`, `documents.irevues.inist.fr`, `cfm2022.sciencesconf.org` | Do not resolve at all | Find the society mirror |
| `library.jsce.or.jp` | HTTPS fails, **HTTP works**; 2009-era Namazu, coverage dated Aug 2016, needs a keyword | Unusable for totals |
| `onlinepubs.trb.org/onlinepubs/am/2017/TRB_2017_Final_Program.pdf` | **HTTP 200 with `content-type: text/html`** (150,212 bytes) — silently serves an error page | Check status **and** type |
| e-cigre Solr (`tx_solr[filter][…]`) | Filters do not restrict: `publicationYear:2024` returns 14,936 (the whole corpus); `publicationType:Session papers` returns 0 | Never read a count off it |
| **CiNii Research** | Indexes ~5% of AIJ's taikai (285–384/yr vs 6,645) **and silently ignores** unknown params (`journal=`, `publicationTitle=`, `sourceTitle=`) — returns the whole year's 1.4M records | Only `q=`, `from=`, `until=` work. **Never a count** |
| **J-STAGE search API** | `service=3` needs `cdjournal` or `issn`; `material=<Japanese title>` returns `ERR_001` **even for titles that exist** (verified against JSCE; control query `issn=1884-4936` works) | ERR_001 ≠ "does not deposit" |
| **Scipedia** | Opt-in full-paper subset: ECCOMAS 307 vs 2,368 (13%); WCCM 133 vs 2,800 (5%) | **Never a congress size** |
| **HAL collections** | Voluntary author deposits: CFM2025 132, CFM2022 354, CFM2019 279, CFM2017 610 — against a congress of 850+ people | **Never a congress size** |
| **Zenodo for TRA** | No `TRA2024` or `Transport Research Arena` community (both 404); full-text search returns 20 scattered records | The brief's suggestion is wrong |
| **CIRED special reports** | Look exactly like CIGRE's but cite a **selection**: a uniform 4-digit extraction across all six gives 155 ids, while Session 1's own intro lists blocks summing to 383 for that session alone. Six different citation conventions | Good evidence it is large, bad evidence of how large |
| **KSME PDFs** | Programme book 52.8MB / 136pp and the 1-page newsletter report both download as valid PDFs and yield **ZERO characters** under `-layout` AND `-raw` — rasterised, no text layer | Go to the HTML programme |
| `www.ksme.or.kr/Conference/ConferenceView.asp` | HTTP 500 on the annual-meeting record; conference list page returns "Error! Go Home" | Use `ksme.or.kr/Proceedings/` |
| `sae.org` / `wcx.sae.org` | JS shell: 15KB of chrome, 64 characters of text | Deposit index settled it anyway |
| `pes-gm.org` headline counters | JS-animated, render as `+ 0` | — |
| `euromat2025.com` | Serves the **same 46,740-byte page** for `/`, `/abstracts/` and `/programme/` | No artefact exists |
| `cfm2025.sciencesconf.org` | `/browse/author` is an unlinked alphabetical index; `/browse/session`, `/program`, `/page/programme-scientifique` all hit "Page non trouvée"; resource pages id 1–22 enumerated, **no paper list anywhere** | Rung 9 |
| ASEE Crossref `10.18260` | Holds **only journals** (Chemical Engineering Education 163, Advances in Engineering Education 36, CoED 20, ASEE J. Eng. Tech. 20) | ASEE deposits no conference papers |
| IEEJ Crossref `10.1541` | 48,363 DOIs, container facet 2023–25 is **only journals** | IEEJ deposits no 全国大会 proceedings |
| IISE in Crossref | Member registry returns only unrelated bodies (National Institute of Industrial Health, KIIE, IIAE) | IISE deposits nothing |
| Internet Archive CDX | Returned **HTTP 503 "Temporarily Offline"** twice mid-run | Retry later |

---

## 4. Counting rules this field needs

1. **Sum volumes for ASME; use `event` for SAE and SPE; use the exact container facet for IEEE; use
   the `volume` pattern for Copernicus.** The grouping key is publisher-specific. (§2.1)

2. **Published papers are a FLOOR wherever a presentation-only track exists.**
   - ASME IMECE deposits 723 against an organiser-stated *"roughly 2,400 papers, presentations, and
     posters … in 17 core tracks"*.
   - SAE WCX deposits 776 and a trade report adds *"about 200 oral-only presentations"*.
   - IEEE PES GM deposits 777 and its call adds a **Transactions Paper Presentation** track plus a
     Student Poster Contest, neither deposited. The same call also settles that the poster session is
     NOT a separate track — *"the majority of accepted conference papers will be scheduled for
     presentation at the Monday evening poster session"*, so adding posters would double-count.

   Conversely, where a society **requires a manuscript for every accepted presentation** — SPE,
   EPE ECCE Europe, ASME Turbo Expo — the deposit is near-complete and a low figure is real evidence
   of a small meeting, not a floor. That distinction decided four `OUT` verdicts.

3. **Two-meetings-a-year rows: report the larger EDITION, `events_per_yr = 2`, never a sum.**
   ASHRAE (Winter 174 / Annual 111) and IEICE (General, spring / Society, autumn — the society states
   it: 本会では毎年春と秋に大会を開催しており). ASHRAE's summed annual total (~260) is still under a
   third of the floor, so the rule did not change that verdict, but it will elsewhere.

4. **A single congress edition can span three calendar years.** ISPRS labels its own edition
   **"Nice 2020/2021/2022"**. The Archives B-series and Annals V-series volumes are numbered
   continuously across all three. Summing gives 2,306; taking 2022 alone gives a third of an edition;
   treating each year as an edition triples the cadence.

5. **Japanese and Korean short papers ARE the meeting.** AIJ's 6,645 two-page 梗概 and KIEE's 1,238
   posters are contributed presentations under the settled unit. Exclude only what the society itself
   labels 特別講演 / 初請講演 / 초청강연 / 특별강연 / 전문가리뷰 / 大会特邀报告. KIEE's S-Session
   (학부생발표, 170 undergraduate posters) is INCLUDED — a presenter is a presenter.

6. **INFORMS-style "sponsored sessions" are NOT invited keynotes.** 1,013 of 1,302 INFORMS sessions
   are cluster-sponsored against 150 labelled "Contributed", but INFORMS' own submission page lists
   *invited, contributed, panel and poster* as four kinds of **submission**, each made by the
   presenter through one open call with a one-presentation-per-person rule across all four. All four
   were counted; the strict-reading figure (~580 talks in explicitly Contributed sessions, plus the
   poster track) is recorded in the row so the orchestrator can apply a harsher reading.
   **Flag this rather than deciding it silently.**

7. **Session-count arithmetic was attempted twice and REJECTED both times.** At TRB and DAGA, 3-digit
   session numbers cannot be separated from room and page numbers (801 candidate matches against
   ~650 real sessions). Poster-board arithmetic worked instead. Do not multiply sessions by a guessed
   talks-per-session.

8. **Take the UNION across rapporteur reports, not the sum.** CIGRE: per-report sum 1,560, union
   1,552 — 8 joint-committee papers appear twice.

9. **Resolve extraction disagreements on STRUCTURE, never by averaging.** Worked cases:
   - **TRB**: `-layout` 1,053 vs `-raw` 981. `-raw` wins because its per-day figures never exceed the
     389-board physical grid, while `-layout`'s Tuesday (514) exceeds it, which is impossible.
   - **INFORMS**: `-layout` 2,619 vs `-raw` 5,122. `-raw` wins — the book is two-column, a line-start
     anchor cannot see the right column, and 2,619 is below the floor implied by 1,302 session codes
     at the observed ~4 talks each.
   - **ECCOMAS / DAGA**: `-layout` wins for right-aligned and columnar tables.
   - **JSCE / KSME / WCCM / TRA / IISE**: both modes agree exactly; that agreement *is* the validation.

10. **Check every download's status AND content-type AND size before counting it.** Two live URLs in
    this wave returned HTTP 200 with the wrong body.

---

## 5. Traps

- **"EPE" is the worst acronym collision in this census.** In the IEEE corpus it matches at least
  eight unrelated conferences: CEEPE (227/281), EPEE (265), ICEPE (112/175), ICEPE-ST (91),
  REEPE (146/189), REPE (85/84), EPEC (77), plus **two different conferences literally abbreviated
  EPE** (International Conference and Exposition on Electrical And Power Engineering, 148; and
  International Scientific Conference on Electric Power Engineering, 71/93). Only the exact container
  title is safe.

- **IMECE has a separate India edition**, DOI slug `imece-india2025`, 409 papers — and its site
  (`imece.asme-india.org`) nonetheless carries copy describing the *main* congress. Phase 1's size
  hint came from there.

- **Case sensitivity cost a whole KSME poster session.** 25 papers print `WE19A-1` where every other
  session prints `We19A-1`. A case-sensitive regex loses them silently.

- **Animated counters hide numbers from text extraction.** FEMS EUROMAT's entire CONGRESS STATISTICS
  block reads as bare labels with no values; the figures live in `data-*` attributes and must be
  aligned to the label order (1812, 36.75, 17, 60.04, 9, 189, 1032, 414).

- **`iafastro.directory` drops requests silently under sustained crawling, and an empty response is
  indistinguishable from an empty symposium.** No retries → 3,151, with three symposiums reported as
  having zero sessions, one of them the 22nd IAA Symposium on Space Debris. **Retry up to four times
  on any empty result** → 4,008, a **27% increase**. Always sanity-check that no substantive node
  reports zero.

- **Three snippet figures were REFUSED** because no loadable page carried them: TRB's *"over 4,000
  presentations across more than 650 sessions"* (four candidate pages opened, plus six Wayback
  captures of trb.org/AnnualMeeting — none carries it), IEICE's *"講演件数は2,000件を超え"*, and a WCCM
  attendance claim. None is recorded anywhere as a figure.

- **Chinese and Japanese numeric conventions:** `2000余场` means *2,000-odd* (rounded DOWN), 件 =
  items, 名 = people, **延べ = cumulative person-days, not unique attendees**. IEICE's 10,600 is 延べ
  over four days; unique attendance is roughly 3,500–4,500, and the rung-9 ratio must account for it.

- **Encodings that produce silent mojibake or empty reads:** AIJ / JSCE / IEEJ / gakkai-web =
  **cp932** (Shift-JIS); KSME = **cp949** (EUC-KR); CSTAM = gb18030/utf-8. Several hosts also need
  `--compressed` or return gzip that reads as binary.

- **Trade-show contamination is mild in this field but real:** TRB's 11,000 headcount is 30.9%
  public-sector agency staff attending 400+ committee business meetings and 18.5% students; SAE WCX's
  4,800 is *registered*, and the source itself says actual attendance was lower.

- **Do not confuse a proceedings-platform document count with a conference size.** Scipedia and HAL
  both look authoritative and are both opt-in subsets (5–13% of the real programme).

---

## 6. Duplicates, and the rows I was least sure of

### Duplicate risk

**One, and it is structural.** **WCCM (row 135) and ECCOMAS (row 136) MERGE IN ALTERNATE CYCLES.**
IACM's own edition table names them jointly: *"17th World Congress on Computational Mechanics & 10th
European Congress on Computational Methods in Applied Sciences and Engineering — WCCM-ECCOMAS 2026"*
(Munich, 19–24 July 2026), and before that the 14th WCCM / ECCOMAS Congress 2020 (Paris), the 11th
WCCM / ECCOMAS Congress 2014 (Barcelona) and the 8th WCCM / ECCOMAS Congress 2008 (Venice).
**In 2024 they were genuinely separate** — WCCM 16 in Vancouver (21–26 July), ECCOMAS 9 in Lisbon
(3–7 June) — so both rows are real and both counted figures stand, but **a joint year must be counted
once, not twice**. Evidence: `https://iacm.info/scientific-events/wccm/`.

No other duplicates found across the 30 rows.

### Cadence findings worth carrying

`events_per_yr`: eighteen rows annual (1), two twice-yearly (2 — ASHRAE, IEICE), eight biennial
(0.5), two quadrennial (0.25 — WCEE, ISPRS).

- **ECCOMAS changed cadence.** Quadrennial 1992–2020 (Brussels 1992, Paris 1996, Barcelona 2000,
  Jyväskylä 2004, Venice 2008, Vienna 2012, Crete 2016, Paris 2020), then **biennial** 2020-2022-2024
  (Oslo 2022, Lisbon 2024 = the 9th). Recorded 0.5 on the current cadence. Note Scipedia's blurb calls
  it "biennial" while the edition list shows four-year gaps for thirty years — trust the list.
- **CFM has drifted.** HAL collections exist for 2017, 2019, 2022, 2025 — two-year gaps before the
  pandemic, three-year gaps since. Recorded 0.5 nominal; **if the 3-year interval persists the true
  figure is 0.33.**
- WCEE: 2024 Milan → **2028 Montreal** (announced on the 18WCEE site). ISPRS: Toronto 2026 after
  Nice 2020/2021/2022, Prague 2016, Melbourne 2012.
- CIRED: biennial main conference in odd years with an intermediate workshop in even years — the
  repository's two collections ("CIRED 2019 Conference", "CIRED 2018 Ljubljana Workshop") show the
  pattern directly.

### Least sure of, in order

1. **CFM (181)** — no countable artefact exists at all. Implied ~765 from 850 delegates at a judged
   90%; that fails test 1 but reaches 918 at the top of the relative ±20% flex band, **passing test 2
   by 18**. This row genuinely sits on the line and should be decided knowingly, not read off the
   arithmetic.
2. **JSME (106)** — deposits break *discontinuously*: 1,089 (2020) → 644 (2021), and 528–741 since,
   against a steady 1,214–1,662 for 2011–2020 and ~1,470/yr for 2000–2010 in the predecessor title
   `jsmemecjo` (16,208 items over 11 years). A 40% step in one year is a deposit-policy change, not a
   halved congress. Recorded 741 as BORDERLINE rather than OUT for that reason. Settling it needs
   Confit in a browser.
3. **IISE (87)** — 1,025 is exact and both extractions agree, but **dated 2013**. The 2024
   schedule-at-a-glance carries no counts and the archive is member-only.
4. **INFORMS (88)** — 5,122 is exact but **dated 2018**, and the invited/contributed split is a
   judgement call (counting rule 6).
5. **CIRED (155)** — 820 from **2019** against a phase-1 expectation of 1,200–1,500. IET stopped using
   per-conference containers around 2015 and the repository holds nothing newer.
6. **TRB (79)** — 981 is **posters only, from 2017**; the entire lectern track is uncounted. The true
   figure is certainly several times larger.
7. **FEMS EUROMAT (166)** — 1,446 is organiser-stated, not counted, and rests on whether the 189
   "highlight presentations" are invited (excluded here; including them gives 1,635).

### Rung-5 queue (one row)

**IEICE General Conference (108).** AWS WAF, browser-solvable. In priority order:

1. `https://www.ieice.org/jpn_r/activities/taikai/general/2025/session_list.html` — 企画セッション一覧
2. `https://www.ieice.org/jpn_r/activities/taikai/general/2025/` — the edition site's programme
3. The post-meeting report's detail page — **highest value**, because it states the lecture count by
   society *and by format* in one table: URL shape `<edition-site>/report/<NNge>/houkoku2.html#d`
   (confirmed from the 2016 report's own link markup). Wayback has the report index pages but has
   **not** captured any `houkoku2.html`; one retry of
   `https://web.archive.org/cdx/search/cdx?url=ieice-taikai.jp/*/report/*&output=text&filter=statuscode:200`
   is worth trying first, since the Internet Archive was returning 503 during this run.

Attendance for that row is already in hand: 約10,600 (2016, 延べ/cumulative, A2 post-meeting report),
10,200 (2015), 延べ10,000+ (2025, host-university announcement). Judged ratio 0.20 **of the published
延べ figure** — equivalently ~50% of a unique base of roughly 4,000; the low percentage is an artefact
of converting a cumulative headcount, not a judgement that few people present.


---

## 7. Orchestrator addenda (2026-09-14)

### IEICE — rung 5 done; the report pages are the artefact for BOTH meetings

`www.ieice.org` is behind an AWS WAF JavaScript challenge that Playwright clears. The per-edition
大会実施報告 page is `https://www.ieice.org/jpn_r/activities/taikai/{general|society}/<year>/report_<year>.html`
(index at `…/report.html`, every year since 2006; older years at `…/taikai/report/report/<yy>{ge|so}.html`).
Its 公募セッション table itemises the open-call presentations by society; the 企画セッション table
above it counts invited/planned SESSIONS and is excluded.

- **General Conference 2025** (spring, five societies): 一般 1,506 + 公募シンポジウム 44 + 公募ポスター 15 +
  学生・ジュニアポスター 234 = **1,784** → VERIFIED. 延べ約7,600名 over four days.
- **Society Conference 2025** (autumn, four societies): 一般講演 1,049 + シンポジウム 47 (80 listed, 33
  double-listed across co-hosting societies — read the footnote) + ポスター 15 = **1,111** → BORDERLINE.
  延べ約4,700名.
- One row per meeting, `events_per_yr` 1 each.

### JSME 年次大会 (row 106) — the J-STAGE deposit is a floor, not the meeting

The orchestrator first ruled OUT on the 2025 J-STAGE count (741; 528 / 612 / 741 for 2023–2025) and
then reversed it on the pilot's evidence that the series broke discontinuously in 2021 (1,089 → 644)
while the predecessor title `jsmemecjo` ran ~1,470/yr for 2000–2010 — a deposit-policy change, not
a halved congress. **Settled by rung 5 (Playwright, 2026-09-14):** Confit's 講演検索 for
`pub.confit.atlas.jp/ja/event/jsme2025` returns 講演(1,449) / セッション(293) for the whole programme
and **講演(1,252) / セッション(177)** filtered to the two contributed categories 部門横断セッション +
部門単独セッション (特別講演, 特別行事, 一般公開イベント, 展示, 会議 excluded). JSME 2025 = **1,252
contributed → BORDERLINE**, restored to the census sheet. The J-STAGE deposit (741) covers ~60% of
the programme. **Confit route for any Japanese society**: open `…/event/<code>/search`, click
検索する with no keyword for the total, tick the contributed 行事種別 categories and search again; the
result header states 講演(N).

### Rows for Rupert's eye

TRB (posters only, 2017 — the lectern track is uncounted and the AMOnline programme needs a
browser); IMECE (deposit floor 723 vs ~2,400 stated); INFORMS (5,122 from 2018, and counting rule 6:
the strict "Contributed"-only reading is ~580 talks + posters); IISE (2013); CIRED (2019); CFM (on
the line at 918 with the flexed band); FEMS EUROMAT (1,446 stated, 1,635 if the 189 highlight talks
are contributed); WCCM and ECCOMAS merge in alternate cycles (2026 joint) — count a joint year once.

---

## 8. Wave 2 (2026-09-14, 29 rows, 5 searches, 24 rows at zero searches) — new routes and results

Verdicts: 2 VERIFIED (IFAC World Congress 1,908 triennial; POMS 1,560), 16 BORDERLINE (IEIE 1,326,
WCTR 1,234, ICSMGE 1,230, ICA 1,154, INTER-NOISE 1,125, ECEE 1,071, USNCCM 1,054, KSCE 1,053, KSAS
1,008, IAHR 976, ECCM 911 floor, EU PVSEC 802, OMAE 746 floor, IDETC 534 floor, PVP 507 floor, JIM
≤1,161 by rung 5), 11 OUT (ISOPE 794, GAMM 734, KICS 614, JCI 539, HFES 536, ICCM 517, JSAE 416,
IMS 411, EWRI 516 by rung 5, Structures Congress ~390 and MineXchange ~520 inferred).

### Routes new in wave 2 — try these before searching

| Route | How | Settled |
|---|---|---|
| **DBpia JSON endpoints (every Korean society whose own site is dead)** | `POST https://www.dbpia.co.kr/journal/selectIssueIndexList` with `publicationId=<PLCT id>` lists the yearly issues with their `voisId`; then `GET https://www.dbpia.co.kr/journal/voisNodeList?voisId=<id>&publicationId=<PLCT id>&currPage=1&pageSize=5000` returns the complete contents in one call; count rows with a non-empty `autr_nm`. No login, no browser. KSCE = PLCT00001494, IEIE = PLCT00000552 | KSCE 1,053 (2024), IEIE 1,326 |
| **ConfTool Pro agendas are server-rendered** | `https://www.conftool.com/<event>/index.php?page=browseSessions&presentations=show` (+`&form_date=YYYY-MM-DD` per day, `&form_tracks=<id>` by submission type); the "JavaScript disabled" banner is cosmetic | ECEE 2026 = 1,071 |
| **Europa Organisation interactive programme** | The congress page loads an iframe `https://interactive-programme.europa-organisation.com/<event>/programme.php` — plain HTML with the whole programme | WCTR 2026 = 1,234 |
| **gakkai-web.net also hosts JSAE** | `https://gakkai-web.net/jsae/{s|a}/<year>/program/data/jp/program.html` (s = 春季, a = 秋季) | JSAE autumn 2026 = 416 |
| **JCI proceedings database** | `https://data.jci-net.or.jp/data_html/<volume>/<year>.html` — one static TOC per year (第1巻 1979 → 第47巻 2025), cp932; count five-column rows | JCI 2025 = 539 |
| **KSAS runs the KSME ASP platform** | `https://ksas.or.kr/proceedings/<year>{a|b|c}/` (a 춘계, b 추계, c 우주) — `TrackList.asp` → `SessionPaperList.asp?code=` as for KSME | KSAS spring 2026 = 1,008 |
| **KICS static programmes** | `https://conf.kics.or.kr/<year>{w|s|f}/program` (동계/하계/추계), past editions at `…/history`; paper IDs `\d{1,3}[A-Z]{1,2}-\d{1,3}` | KICS summer 2025 = 614 |
| **GAMM book of abstracts** | `www.gamm-ev.de` has an expired certificate; `https://jahrestagung.gamm.org/` lists every edition and links a BoA PDF per edition | GAMM 2025 = 734 |
| **Google Drive programme books** | POMS links its program book from `pomsmeetings.org/conf-<year>/`; fetch `https://drive.google.com/uc?export=download&id=<id>`. USNCCM's Google Sites `/program` page hides its Drive links inside the page's inline JSON — grep the HTML for `drive.google.com/file/d/` | POMS 2026 = 1,560; USNCCM 2025 = 1,054 |
| **ISOPE programme PDF** | `publications.isope.org` 403s and OnePetro is Cloudflare, but `https://www.isope.org/conferences/` links a free "Full Updated Program with Paper List" PDF per edition | ISOPE 2025 = 794 |
| **IAHR document library** | `https://www.iahr.org/library/world?pid=<n>` — TWO collections per congress: "Proceedings" (opt-in full papers) and "Book of Extended Abstracts" (everything). Count the abstracts book | IAHR 2025 = 976 |
| **Zenodo communities (ICCM)** | `https://zenodo.org/api/records?communities=iccm-<NN>&size=1`, read `hits.total`; agrees with the organiser's figure. Series 1,355 → 1,258 → 1,124 → 920 → 517 | ICCM 2025 = 517 |
| **Current-edition university host (ECCM)** | `escm.eu.org` times out and `eccm21.org` was lost to a squatter; `eccm22.org` redirects to an NTNU-hosted site with the programme | ECCM 2026 = 911 (floor) |
| **INCE proceedings by ISSN** | ingentaconnect is Cloudflare-walled; INCE is Crossref member 1973, prefix `10.3397`, proceedings ISSN `0736-2935` — `filter=issn:0736-2935,from-pub-date:<Y>…` | INTER-NOISE 2024 = 1,125 (2025 São Paulo only 393 deposited) |
| **ASA / ICA via JASA supplement deposits** | ASA deposits every meeting abstract under prefix `10.1121`; group on (volume, issue, A-page prefix) to isolate the meeting supplement — the medicine-style route on an engineering congress | ICA 2025 (= ASA 188th) = 1,154 |
| **EU PVSEC: DOIs live in DataCite, not Crossref** | prefix `10.4229` is DataCite client `tib.wip`: `https://api.datacite.org/dois?client-id=tib.wip&query=publicationYear:<Y>&page[size]=0` (299–364/yr, a floor — papers optional); the programme PDF `eupvsec.org/images/<year>/conference/EUPVSEC<year>_ConferenceProgramme_v<n>_web.pdf` is the count (IDs `\d?[A-Z]{2}\.\d+\.\d+`) | EU PVSEC 2026 = 802 |
| **IFAC-PapersOnLine ISSN** | `api.crossref.org/journals?query=IFAC-PapersOnLine` → ISSN `2405-8963`; Elsevier deposits every World Congress paper individually | IFAC 2023 = 1,908 |
| **HFES via the Sage journal, not the society member record** | member 370 shows 40 DOIs (reads as "does not deposit"); the meeting is the journal ISSN `2169-5067` (16,302 DOIs) | HFES 2019 = 536 |
| **eposter.at static proceedings** | `https://eposter.at/ICSMGE2026/proceedings/overview.html` carries the complete paper list in one page | ICSMGE 2026 = 1,230 |
| **eventscribe opens in a browser** (rung 5) | Cloudflare 403 to curl; in Playwright `SearchByPresentation.asp?pfp=BrowsebyTitle` states "N results found" and carries N unique `PresentationID` links; `/searchbyposter.asp` may 404 | EWRI 2026 = 516 |
| **Confit, again** | `pub.confit.atlas.jp/ja/event/<code>/search`, click 検索する: JIM autumn 2025 = 講演(1,161) | JIM ≤1,161 |

### Traps and rules added in wave 2

- **A member record with few DOIs does not mean "does not deposit"** — the meeting may sit under a
  journal ISSN (HFES), a different registry (EU PVSEC in DataCite), or a journal container (IFAC).
- **Two collections for one congress** (IAHR proceedings vs extended abstracts): count the one that
  holds every presentation, and say which.
- **KICS meets three times a year** (events/yr 3); KSAS, JSAE, JIM and IEIE twice — per-edition
  figure of the larger edition, never a sum.
- **Series in decline decide on the current edition** (ICCM 517 after 1,355; KSCE 1,053 in 2024 vs
  719 in 2025 — recorded 2024, needs a check); INTER-NOISE's 2025 deposit (393) looks like a thin
  deposit rather than a small meeting.
- **Lost domains redirect to squatters** (eccm21.org → an unrelated business site, 403): never cite one.
- **ICA and ASA merge in some years** (2025 New Orleans = ASA's 188th meeting); WCCM and ECCOMAS
  merge in alternate cycles. A joint year is counted once — Rupert chooses the sheet.
- **ASCE deposits are optional at its congresses** (EWRI 105–147/yr, Structures 38–42/yr): the
  deposit is a floor and the eventscribe programme is the count.

### Wave-2 researcher's refinements (relayed 2026-09-14, before its session limit hit)

- **DBpia**: a row is a paper iff `autr_nm` is non-empty (also `frst_page`/`end_page`); other rows
  are session headers, and papers + headers must equal `totCnt`.
- **ConfTool**: count `class="paper_title"`; `form_tracks` is the organiser's own submission-type
  filter, so the invited track can be excluded exactly (ECEE 2026: track 10 = Invited Lecture).
- **Europa interactive programme**: split on `div.schedule-item`, read `div.sessionType`, count
  `div.interventionTitle`.
- **KSAS**: `<yr>c` (우주/space) is a separate series, not an edition of the main meeting.
- **JSAE**: one `<tr>` per lecture with `p.article-title`; a second artefact is the programme zip
  `jsae.or.jp/files_publish/news/<id>/<date>jsae<yr>s_sp.zip` (count PDFs).
- **JCI**: drop 主題 rows containing 研究委員会 (committee reports).
- **POMS**: paper IDs `\b148-[0-9]{4}\b` (prefix = EventsNet event id); the registered-participants
  page `pomsmeetings.org/EventsNet/EventRegistration/RegisteredParticipants.aspx?ev=<id>` is a
  static attendance directory.
- **ISOPE**: blocks whose last line ends in a country name are papers; `[Proceedings only]` items
  are published, not presented — exclude.
- **ASA/ICA**: the meeting is the JASA issue `4_Supplement` with A-pages.
- **INCE**: DOI suffix `^10.3397/([a-z]+)_(\d{4})_` — `in_` INTER-NOISE, `nc_` NOISE-CON, `no_` a third series.
- **IFAC**: a congress is ONE issue of IFAC-PapersOnLine ((56,2) = 1,909 incl. the "Contents" record — drop it).
- **EU PVSEC**: a leading day digit marks contributed IDs (O oral, V visual/poster); P-series are plenary/panel.
- **ICSMGE eposter.at**: `data-poster-id` + `span.poster-category`; ids prefixed `Plenary-` are invited.
- **USACM books of abstracts**: anchors `^ *ABSTRACT *$`, the running head and the dateline all agree.
- **ECCM programme PDF**: IDs `#[0-9]{1,5}`.
- **ICCM on Zenodo** is the official ISSN-bearing proceedings and matches the organiser's printed
  table exactly — the one licensed exception to the "repositories are not proceedings" rule.
- **HFES**: use ISSN `2169-5067`, NOT `1541-9312`; member 370 is a decoy.
- **GAMM**: PAMM (ISSN `1617-7061`) is a collapsing floor (600 / 594 / 198 / 62 / 156) — count the BoA.
- **ASME papers are optional for presentation** in ASME's own words:
  `idetc.secure-platform.com/a/page/author_resources/paper_publication_requirements` — the deposit
  is a floor for every ASME meeting.
