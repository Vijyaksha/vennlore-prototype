# Field notes — earth, environmental & agricultural sciences

Companion to `census-methodology.md`, which stays general. This file holds only what is true of
**earth, environmental and agricultural sciences** and would be noise in the general method. Read
both before working a row in this field; add what you learn here, not there.

Started 2026-09-15. Sections 1–6 are the phase-2 wave-1 pilot researcher's report (30 rows, one
Opus agent, 11 searches, 20 rows at zero searches).

Outputs: `scratchpad/earth/wave1/results_1.json`, `scratchpad/earth/wave1/STATUS_1.json`.

## The unit, the bar, and the scope

Accepted contributed presentations = **orals + posters presented at one edition**; plenary /
keynote / invited (特邀报告 / 大会邀请报告 / 招待講演 / Invited / Keynote / Palestra Temática /
conferencia plenaria) excluded; exhibitor, sponsor and trade sessions excluded; withdrawn and
no-show excluded. ≥1,500 counted = VERIFIED; 800–1,499 = BORDERLINE; below 800 on positive
evidence = OUT; no evidence either way = BORDERLINE, never OUT. A stated total never beats a
countable artefact. A deposit or paper index that misses a presentation-only track is a FLOOR
(`confidence: floor`), not evidence of a small meeting — see counting rule 2.

| Meeting | Counted on |
|---|---|
| AGU, EGU, AMS | `Census - Physical Sciences` (already counted; not re-censused here) |
| AAPG ACE | `Census - Engineering` row 188 — now duplicated by SEG IMAGE (row 19) |
| NSA (National Shellfisheries Association) | life-sciences sheet — possible duplicate of Aquaculture (row 100) |

---

## 1. Wave 1 results

**20 of 30 rows cost ZERO searches.** Five `VERIFIED`, seventeen `BORDERLINE`, eight `OUT` on
positive evidence. Total 11 searches. Counted events/yr: VERIFIED 2.95, BORDERLINE 11.49.

| Row | Conference | Abstracts | Rung | Verdict | Ev/yr |
|---|---|---|---|---|---|
| 45 | Chinese Geoscience Union Annual Meeting (中国地球科学联合学术年会) | 3,922 | 2 | VERIFIED | 1 |
| 6 | AOGS Annual Meeting | 3,861 | 4 | VERIFIED | 1 |
| 14 | IUFRO World Congress | 3,320 | 3 | VERIFIED | 0.2 |
| 12 | INQUA Congress | 2,660 | 3 | VERIFIED | 0.25 |
| 33 | Congresso Brasileiro de Geologia (CBG) | 1,696 | 3 | VERIFIED | 0.5 |
| 5 | JpGU Meeting (Japan Geoscience Union) | ~4,600 stated | 2 | BORDERLINE | 1 |
| 8 | IUGG General Assembly | 4,439 | 2 | BORDERLINE | 0.25 |
| 94 | ESA Living Planet Symposium (LPS) | 4,200 stated | 2 | BORDERLINE | 0.33 |
| 80 | Chinese Geophysical Society Annual Meeting | 3,922 (dup of row 45) | 2 | BORDERLINE | 1 |
| 7 | International Geological Congress (IGC) | 2,978 | 2 | BORDERLINE | 0.25 |
| 16 | EAAP Annual Meeting | 1,347 | 3 | BORDERLINE | 1 |
| 13 | World Congress of Soil Science (WCSS) | 1,330 | 2 | BORDERLINE | 0.25 |
| 100 | Aquaculture (WAS Triennial / Aquaculture America) | 1,300 stated | 3 | BORDERLINE | 1 |
| 15 | International Horticultural Congress (IHC) | 1,164 floor | 4 | BORDERLINE | 0.25 |
| 107 | CSES Annual Conference (中国环境科学学会科学技术年会) | 1,136 floor | 2 | BORDERLINE | 1 |
| 124 | International Conference on Urban Climate (ICUC) | 1,030 | 3 | BORDERLINE | 0.33 |
| 21 | Lunar and Planetary Science Conference (LPSC) | 1,000 (2026) | 3 | BORDERLINE | 1 |
| 37 | Congresso Brasileiro de Ciência do Solo (CBCS) | 973 | 3 | BORDERLINE | 0.5 |
| 43 | SSA Annual Meeting | ~904 | 2 | BORDERLINE | 1 |
| 78 | Congreso Geológico Chileno | 900+ | 2 | BORDERLINE | 0.33 |
| 19 | SEG IMAGE | 611 floor | 4 | BORDERLINE | 1 |
| 46 | Chinese Meteorological Society Annual Meeting | UNKNOWN | — | BORDERLINE | 1 |
| 52 | Réunion des Sciences de la Terre (RST) | 782 | 3 | OUT | 0.5 |
| 66 | IAH Congress | 735 | 3 | OUT | 1 |
| 110 | JSSSPN Annual Meeting (日本土壌肥料学会年次大会) | 734 | 4 | OUT | 1 |
| 117 | RAUGM (Unión Geofísica Mexicana) | 700+ | 2 | OUT | 1 |
| 18 | EMS Annual Meeting | 690 | 3 | OUT | 1 |
| 51 | DGGV annual meeting (GeoBerlin series) | 551 | 4 | OUT | 1 |
| 113 | Geological Society of Japan Annual Meeting | 508 | 4 | OUT | 1 |
| 47 | Meteorological Society of Japan (spring/autumn) | 190 | 3 | OUT | 2 |

**Plan earth-science waves around platforms and society reports, not around search.** Only 10 of
30 rows needed a search at all, and **no search ever returned a usable figure directly** — each
only pointed at an artefact that then had to be counted or opened.

---

## 2. Every route that worked

### 2.1 Copernicus per-abstract static pages — the single most valuable find, and it generalises

The meeting root redirects to a login and the session programme is JavaScript, which is the normal
state of a Copernicus meeting. But **every abstract has a static HTML page**:

```
https://meetingorganizer.copernicus.org/<MEETING>/<MEETING>-<n>.html
```

Plain curl, no login, no JS. Enumerate `n` upward and count pages whose `<title>` begins
`Abstract <MEETING>-`. Proven on two independent meetings in this run:

- **ICUC12 = 1,030** abstracts (IDs 2–1141, 110 unused), probed 1–1300.
- **EMS2025 = 690** abstracts (IDs 1–736, 46 unused), probed 1–900.

**TRAP — the status code is useless here.** A non-existent abstract number returns **HTTP 200**
with a 9,011-byte page whose `<title>` is `<MEETING> - 404`. Counting by status code returns the
whole probe range. Test the title (or the byte size).

Public programme entry points that do work: `…/<MEETING>/meetingprogramme` (302s to
`/sessionprogramme`). `presentations.copernicus.org/<MEETING>/` is a **404** — that half of the
brief's Copernicus hypothesis does not apply.

**The Copernicus meeting list is enumerable.** An unknown slug falls back to a 3.53MB
"CO Meeting Organizer" overview page which lists every current meeting slug. As of this run:
`25IOAP, CC2027, DACH2022, DKT-13, ECSS2023, ECSS2025, EGU22–EGU27, EMS2022–EMS2026,
EPSC-DPS2025, EPSC2022, EPSC2024, EPSC2026, GC7-WaterPart2, GC8-Hydro, GC10-Pliocene,
GC11-solidearth, GC12-FibreOptic, GC14-FibreOptic, GSTM2022, GSTM2024, GSTM2026, IAHS2022,
ICG2022, ICUC12, OOS2025, Plinius17, Plinius18, Plinius19, WBF2026, alpshop2022, alpshop2024`.
No DGGV meeting is among them.

### 2.2 Society annual reports and newsletters — itemised programme statistics

**Look for the union's or society's annual report before researching the congress.** Three rows
were settled this way at zero searches.

| Body | Artefact | What it gave |
|---|---|---|
| **IUGS** | `wp-json/wp/v2/media?search=annual report` → `https://www.iugs.org/wp-content/uploads/2026/05/IUGS_Annual_Report_2024.pdf` | IGC Busan 2024: 1,649 oral + 1,329 poster = 2,978; 6,413 delegates from 99 countries |
| **IUGG** | `https://iugg.org/publications/iugg-annual-reports/` → `report2023.pdf` | 28th GA Berlin: 640 sessions, 3,109 oral + 1,330 poster = 4,439; ~5,000 participants. Also IAVCEI 2023 = 1,080 people / 1,258 abstracts, IAG 2023 = 1,202 / 643 orals |
| **CGS (China)** | `http://www.cgs.org.cn/drupal/?q=node/90` → `/files/huixun/huixun173.htm` | CGU 2025: 143 专题, 3,922 论文 (2,839 口头 + 1,083 张贴), 9 大会邀请报告, 4,700 到会代表 of which 4,490 registered and 210 厂商 |

CGS also publishes older per-meeting minutes at `?q=jiyao/<n>` (n runs to 33 = 2017; 34+ are 404).
The 2017 minutes give CGU 2017 as 2,400余篇 (近1,800 口头 + 600余 张贴) across 108 专题 — useful
for establishing a growth trajectory.

### 2.3 MARS / meetmatt-svr.net — AOGS's platform, fully server-rendered

```
https://meetmatt-svr.net/Public/Abstracts?cfId=<n>              # session <select name="ssId">
https://meetmatt-svr.net/Public/Abstracts?cfId=<n>&ssId=<id>    # that session's COMPLETE abstract list
https://meetmatt-svr.net/Timetable?cfId=<n>                     # year <select> gives the cfId map
```

cfId: 1=AOGS2019, 2=2020, 3=2021, 4=2022, 5=2023, 6=2024, 7=2025, 8=2026, 9=2027. No JS, no login,
unpaginated. 284 sessions crawled for AOGS 2026 → 3,899 unique IDs
(`[A-Z]{2}\d{2,3}-[A-Z]\d{3,4}[A-Z]?`), 3,861 after removing the 38 SS items.

### 2.4 Books of abstracts on flat, guessable archive paths

- **EAAP — the cleanest archive in the field.**
  `https://docs.eaap.org/boa/<YEAR>_<City>_EAAP_Book_Abstracts.pdf`, 2009 Barcelona onward, and
  **the pattern resolves for years the index page does not list** (I guessed 2025_Innsbruck and
  2026_Hamburg; both returned 200). Index at `https://meetings.eaap.org/previous-annual-meetings/`.
  Count unique `Session NN Theatre NNN` and `Session NN Poster NNN` slugs.
  Series: 2022 Porto 1,226 (767+459); 2023 Lyon 1,787 (1,113+674); 2024 Florence 1,783 (1,111+672);
  2025 Innsbruck 1,347 (906+441).
- **IUFRO** — `https://iufro2024.com/book-of-abstracts/` → `…/wp-content/uploads/iufro2024abstracts.pdf`
  (14.2MB, 3,889pp). The book **states its own total**: "This document contains 3320 abstracts that
  were presented in some format (oral only; poster only; oral or poster)". Independent TOC count 3,238 (97.5%).
- **WAS / Aquaculture** — `https://www.was.org/meeting/code/AQ2025` links the book on an Azure blob
  store: `https://wasblobstorage.blob.core.windows.net/meeting-abstracts/AQ2025AbstractBook.pdf`
  (141MB, 1,288pp — needs a long timeout). States "over 1,300 abstracts, 110 scientific and
  technical sessions, and 210 posters".
- **INQUA — the official book is on Zenodo.** doi 10.5281/zenodo.12749221; resolve via
  `https://zenodo.org/api/records?q=INQUA%20abstract%20book`, then
  `https://zenodo.org/api/records/12749221/files/<name>/content` (14MB, 3,400pp) → 2,660.
- **WCSS via the co-organiser** — `https://soils.org.uk/wcss22/science/` links both books plus the
  annual report on `cdn-bsss-new.b-cdn.net`.
- **GeoBerlin / DGGV** — see §2.8.

### 2.5 Acta Horticulturae sums — exactly as the brief predicted

Each IHC becomes a set of Acta volumes, one per symposium. Two steps:

1. **Identify the volumes by TITLE**, never by range. Fetch
   `https://www.actahort.org/books/<vol>/index.htm` across a range and read the `<title>`; 25
   volumes are titled `XXXI International Horticultural Congress (IHC2022): …`. They are
   **interleaved with unrelated symposia** — 1353, 1355, 1356, 1358–1362, 1364–1370, 1372–1375,
   1377, 1378, 1380, 1381, 1384, 1407, with 1354/1357/1363/1371/1376 belonging to other meetings.
2. **Count** distinct article DOIs `10.17660/ActaHortic\.\d{4}\.<vol>\.(\d+)` on each volume index
   page and sum → **1,164**.

Cross-check with Crossref by ISSN `0567-7572`, **grouping on the DOI's volume component** — the
Crossref records carry no `volume` field:

```
https://api.crossref.org/journals/0567-7572/works?filter=from-pub-date:<Y1>-01-01,until-pub-date:<Y2>-12-31&rows=1000&select=DOI,page,title&cursor=*
```

Per-volume agreement was exact on 22 of 25 volumes; the three that showed zero in Crossref were
simply published before the date filter.

### 2.6 Cloudflare asset paths are often unwalled — this converted LPSC from rung 5 to a zero-search count

Every HTML path on `www.hou.usra.edu` and `www.lpi.usra.edu` is a Cloudflare 403, **including** the
meeting landing page and the e-program. But:

```
https://www.hou.usra.edu/meetings/<meeting>/pdf/<abstract-number>.pdf     # HTTP 200, the abstract
https://www.hou.usra.edu/meetings/<meeting>/pdf/<missing-number>.pdf      # clean HTTP 404
```

HEAD-enumerate the ID space (10 threads, 3 retries). **LPSC 2026 = 1,000** (IDs 1001–2027, 27
unused). **LPSC 2025 = 1,831** (IDs 1005–2903, 68 unused). Verified there is no second block:
2030/2100/2200/2300/5000/6000/7000/9000 all 404. No index PDF exists (`program.pdf`,
`sessions.pdf`, `toc.pdf`, `authorindex.pdf`, `lpsc<year>.pdf`, `sess_all.pdf` all 404), so the ID
enumeration IS the artefact and its internal structure — contiguous block, scattered gaps, hard
stop — is the validation.

### 2.7 The society mirror when the congress host blocks

`22wcss.org` and `iuss.org` are hard Cloudflare 403s on every path and every user-agent, and
Wayback was offline. But the **co-organiser** publishes the whole record unwalled:

```
https://soils.org.uk/wcss22/science/
https://cdn-bsss-new.b-cdn.net/wp-content/uploads/2023/06/WCSS-Oral-book-of-abstracts-28.07.22.pdf
https://cdn-bsss-new.b-cdn.net/wp-content/uploads/2023/06/WCSS-Poster-Book-of-abstracts-31.07.22.pdf
https://cdn-bsss-new.b-cdn.net/wp-content/uploads/2023/05/WCSS_Annual-Report_final_WEB.pdf
```

The annual report itemises everything: 1,675 delegates (1,377 in person + 298 online);
**445 oral accepted, 387 presented (86.9%); 1,488 poster accepted, 943 featured (63.34%)**.
My independent count of the oral book (387, both extraction modes) matched the report exactly.

### 2.8 Static ConfTool mirrors left on dead meeting domains

DGGV leaves a wget-style local copy of its ConfTool Pro agenda on each edition's own domain, with
the query strings preserved as hashed filenames:

```
https://www.geoberlin2023.de/programme2023/Programm_GeoBerlin/www.conftool.pro/geoberlin2023/
  index4eff.html?page=browseSessions&print=export&ismobile=false&presentations=show   # unfiltered
  index4e2a / indexa557 / indexc3e9 / indexafc1 / indexb43e                            # per date
  index0445 / index2903 / index293b / …                                                # per room
```

Plain server-rendered HTML; the "JavaScript is Disabled" banner is cosmetic. Count
`class="paper_title"`. GeoBerlin 2023 = **598**, and the four per-date views sum to exactly 598.

### 2.9 J-STAGE prints its own volume totals — one fetch per year, no crawling

```
https://www.jstage.jst.go.jp/browse/<code>/-char/ja                       # journal, find the code
https://www.jstage.jst.go.jp/browse/<code>/<vol>/0/_contents/-char/ja      # contents page
```

The contents page contains the string `選択された号の論文のN件中` — that N is the volume total. It
paginates at 50 per page via `?from=1..N` if the items themselves are wanted.

- `dohikouen` = 日本土壌肥料学会講演要旨集. Volume = 67 (2021) … 71 (2025). Totals 587, 530, 648,
  705, 734. Abstract IDs `P1-1-9` (poster) / `1-1-10` (oral).
- `geosocabst` = 日本地質学会学術大会講演要旨. **Volume key is the YEAR**, not a number: 2023 = 517,
  2024 = 520, 2025 = 508.
- The society's own abstracts page is how you find the code (jssspn.jp/book/abstracts/ carries
  exactly one outbound link, to J-STAGE).

### 2.10 Brazilian anais live with the PUBLISHER, not the society

- **CBCS** — sbcs.org.br carries only news; the Anais are published commercially by Editora Novus:
  `https://editoranovus.com.br/anais-do-xxxix-congresso-brasileiro-de-ciencia-do-solo-sbcs-2025/`
  → `…/wp-content/uploads/2026/02/Anais-CBCS-2025.pdf` (ISBN 978-65-84364-24-0,
  DOI 10.29327/5792634, 51MB, 1,047pp). Count Sumário dot leaders → **973**.
- **CBG** — the society mirrors the complete proceedings itself at
  `https://sbgeo.org.br/anais_digitalizados/51_CBG_ANAIS.pdf` (10.3MB, 1,705pp). The folder name
  "anais_digitalizados" is misleading: this volume is born-digital, and the folder is worth walking
  for earlier editions. Structure is a gift — one record per work with `ID do trabalho:`,
  `Área Técnica do trabalho:`, `Título do Trabalho:`, `Forma de apresentação:`, `Autores:`.
  **1,699 works = 1,184 Pôster + 512 Oral + 3 Palestra Temática** → 1,696 contributed.

### 2.11 Google Sites + Google Drive — the Japanese meteorological layer

MSJ runs each edition as its own Google Site:

```
https://sites.google.com/metsoc.or.jp/{spr|atm}<YYYY>/            # spr = 春季, atm = 秋季
  /program/oral_program            口頭発表プログラム
  /program/ondemand_program        ポスター発表プログラム
  /program/現地発表プログラム       (URL-encoded)
```

Each sub-page embeds its programme as a Google Drive PDF whose file id must be grepped out of the
page HTML (`drive.google.com/file/d/([A-Za-z0-9_-]{20,})`). Download with:

```
https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t
```

Note it returns `content-type: application/octet-stream`, not `application/pdf` — a content-type
check would wrongly reject it. Count IDs `\b([A-Z]{1,2}\d{3})\b`.

### 2.12 Chinese government sites report society meetings and are not walled

When a Chinese society's own site blocks (chinacses.org 403, cms1924.org JS), the ministry and
municipal environment/meteorology bureaux publish the meeting report and fetch cleanly with plain
curl. Proven hosts: `mee.gov.cn`, `*.nanjing.gov.cn`, `cma.gov.cn`.

CSES 2025, from `https://sthjj.nanjing.gov.cn/hbyw/hjky/glzc/202507/t20250729_5617382.html`:
`安排12场特邀主旨报告，设置76个分会场，包含1136个学术报告，同时还举办了…研究生专场、墙报交流等活动`
— 12 invited keynotes, 76 sessions, **1,136 academic reports**, plus an unquantified poster track.

### 2.13 Other artefacts that worked

- **IAH dated programme PDFs.** `https://iah2026budapest.com/program/` links
  `IAH2026_Oral_Program_<YYYYMMDD>.pdf`, `IAH2026_Poster_Program_<YYYYMMDD>.pdf`,
  `IAH2026_Daily.pdf`. **The filenames embed a build date and change as the programme is revised**
  — cite the dated URL and re-derive the name from the /program/ page. Oral rows match
  `\d{2}:\d{2}[–-]\d{2}:\d{2}\s+(LID)\s+`; poster rows `(P-\d{3,4})\s+Session\s+[\d.]+\s+(LID)`.
  423 + 312 = **735**, triple-corroborated by the HTML programme's 736 numeric `<td>` cells.
  Find the congress through `https://iah.org/events` (the "IAH Events" heading); note
  `iah.org/events/iah-congress` is a 404.
- **SSA via the WordPress media API.** `https://meetings.seismosoc.org/wp-json/wp/v2/media?search=program&per_page=50&_fields=source_url,title`
  returns 20 programme PDFs including `SSA-Program-2026.pdf` (167pp). Its p.1 states "more than 950
  technical oral and poster presentations as well as plenary sessions, workshops"; the string
  `Invited:` appears 46 times in both extraction modes → ~904 contributed.
- **WordPress media APIs found four artefacts no page linked**: IUGS annual reports, SSA's
  programme PDFs, INQUA's third circular, and DGGV's per-edition "Call for Abstracts" graphics —
  the last of which is how the real name of DGGV's 2025 meeting (**Geo4Göttingen**, not GeoBremen)
  was recovered.
- **RST's public Google Sheets.** The 29e RST publishes its detailed oral programme and poster list
  as public sheets: `docs.google.com/spreadsheets/d/1qf81zDc3VsxZlzbCCKSgOGB_NnKylm3jI-uA-WllJeQ`
  (gid=0 orals, gid=138396748 posters) — an independent route to the same count.
- **JpGU / IGC / LPS organiser statements.** JpGU's own `meeting_e2025/about.php` carries the
  Program Committee Chair's greeting: "We received over 4,600 presentations in total. The number of
  registered participants exceeded 8,000, and approximately 85% attended … in person".

---

## 3. Every route that failed, and the wall hit

| Route | Wall | Verdict |
|---|---|---|
| **Confit** (`confit.atlas.jp`) — JpGU, IHC2026 | **HTTP 202 with a zero-byte body** to curl with a desktop Chrome UA | Genuine **rung 5** |
| `22wcss.org`, `www.iuss.org` | Cloudflare 403 on **every** path including `/sitemap.xml` and `/wp-json/`, to Chrome, curl/8.0, a Googlebot string and no UA | Beaten via the BSSS mirror (§2.7) |
| `hou.usra.edu`, `lpi.usra.edu` HTML | Cloudflare 403 ("Just a moment...") | Beaten via the `/pdf/` asset path (§2.6) |
| `chinacses.org` | 403 with a 107-byte stub, http and https, with and without `Accept-Language: zh-CN` | **Rung 5**; beaten via government sites |
| `cms1924.org` | JavaScript shell — `academic.html`, `gnMeeting.html`, `xhdt.html` are 2–3 KB and render lists client-side | **Rung 5** |
| `nh.cms1924.org` (36th CMS meeting, on the sciconf.cn / 会务通 platform) | 802-byte page reading `404页面 网站升级维护中` | Retry when maintenance ends |
| **Internet Archive / Wayback** | HTTP **503 "Temporarily Offline" for the whole run** | Every Wayback bypass in the engineering notes was unavailable. Retry later |
| IUGG's C-IN portal `czech-in.org/cmPortalV15/Portal/iugg23/normal` | Redirects to `/cmPortalV15/Account/Login` | **Credential wall — do NOT queue for rung 5** |
| `c-in.floq.live/event/iugg2023berlin/program_day_by_day` | 404 | — |
| **Ex Ordo** (INQUA) | SPA: the same 269KB shell for `/programme`, `/programme/at-a-glance`, `/programme/presentations`. Its embedded JSON DOES expose per-track `submission_count` (588/589, 673, 960, 574, 1,348, 205, 64 = 4,412) — **but that is 1.7x the abstract book and 1.47 per participant, so it is not a count of presentations** | Figure REFUSED; count the book instead |
| `lps25.esa.int` | **Does not resolve at all** — DNS failure, not a 403 | A browser fails identically. **Do NOT queue** |
| `igc2024korea.org` | 460-byte JS shell ("Loading IGC 2024") | Rung 5. `igc2024.org` and `37igc.org` do not resolve |
| `ihc2022.org`, `geomuenster2024.de`, `geobremen2025.de`, `wcss2026.org`, `23wcss.org`, `rst2024/2026/2023.sciencesconf.org` | Do not resolve | Find the society mirror or the real subdomain name |
| `50cbg.com` — **linked live from sbgeo.org.br's own front page** | Lapsed to a squatter serving a Vietnamese online-gambling site (`lode88vn.skin`) | Never cite |
| `usbrasil.iweventos.com.br/evento/cbg2024/trabalhosaprovados` | Cloudflare 403 (the site's own pages serve fine) | Rung 5; beaten via the society mirror |
| `repositorio.sernageomin.cl` | Broken TLS chain (`curl: (60)` — needs `curl -k`), then HTTP **503** | Down service, not a bot wall. Retry |
| **Copernicus meeting-name guessing** | An unknown slug returns **HTTP 200 with a 3.53MB generic "CO Meeting Organizer" overview page**, never a 404. Six DGGV name guesses all "succeeded" this way | Check the body, not the status |
| `presentations.copernicus.org/EMS2025/` | 404 | That half of the brief's Copernicus route does not apply |
| **SRL on Crossref** (the brief's suggested SSA route) | Seismological Research Letters deposits **no supplement**: 316 / 271 / 235 ordinary articles for 2024 / 2025 / 2026, evenly spread across issues, no supplement issue and no S-paged band | **The Crossref page-prefix method does not work for SSA** |
| **MSJ deposits** | No Crossref journal for 大会講演予稿集 or its English name; J-STAGE has no `msjtaikai` / `jmsjtaikai` / `metsoctaikai` (all 404) — only `tenki`, the regular magazine. metsoc.jp states the preprints are participant-only since spring 2019 | Use the Google Sites route (§2.11) |
| **AAPG prefix `10.1306`** for the IMAGE merger | 114 items in 2024, 62 in 2025, 57 in 2026, of which 84–87/yr are *AAPG Bulletin* articles and the rest are AAPG **section** meetings. No IMAGE container exists | AAPG's half of IMAGE is presentation-only |
| **EAAP 2026 Hamburg** book | HTTP 200, 30,850,148 bytes, but **password-protected** (`pdftotext: Incorrect password`) | A real user password — **NOT** a rung-5 job |
| **RAUGM's GEOS abstract volume** | HTTP 200, 228pp, but a broken/custom font encoding: body text extracts as mojibake under BOTH modes and no ID pattern survives (`[A-Z]{2,4}-\d{1,3}` returns only `CS-137` and `GOES-16`) | Use the site's stated total |
| RST `/page/bilan_edition` ("Bilan de cette édition") | Loads its body by JS — renders as `Chargement...` | **Rung 5**, and it is the ideal A2 report |
| RST `/program/details` | Returns only 39 plenary-level events, not the session programme | Use the Livre des résumés |
| CGU 论文集 | Distributed **only on a USB stick to on-site attendees** — the download page says so: `本页面不提供会议论文集（U盘）… 无其它公开方式` | Use the society's statistics |
| `dggv.de` / GeoMinBochum 2026 | The current edition publishes only a sessions PDF; no programme yet | Count a past edition |
| CGS `/files/huixun/huixun148.htm` and `?q=jiyao/34+` | 404 | Only huixun172–175 and jiyao≤33 exist |

---

## 4. Counting rules this field needs

1. **The union/association family must be counted once per series, and the associations are real
   separate meetings.** IUGG's General Assembly (row 8, 4,439) is the quadrennial JOINT meeting of
   eight associations (IAG, IASPEI, IAVCEI, IAMAS, IAPSO, IACS, IAGA, IAHS), which hold their own
   assemblies in between, sometimes jointly in pairs. The 2023 IUGG report sizes two of them —
   IAVCEI Rotorua 1,080 people / 1,258 abstracts, IAG 1,202 participants / 643 orals — so they are
   substantial meetings in their own right. **Count each series once; never add an association
   assembly to the GA row; say in Method which editions you counted.**

2. **Published papers and deposit indexes are a FLOOR wherever a presentation-only track exists.**
   - IHC's 1,164 Acta papers miss every presenter who never wrote a paper (an Acta paper is a
     separate, optional post-congress submission).
   - SEG IMAGE's 611 deposited expanded abstracts miss AAPG's entire half of the merged meeting.
   - CSES's 1,136 academic reports exclude an unquantified 墙报交流 poster track.
   Conversely, where the artefact **is** the programme (AOGS, IAH, LPSC, CBG, DGGV, EAAP), the
   count is complete and a low figure is real evidence of a small meeting.

3. **Take "presented", not "accepted" — and say which you took.** WCSS22 accepted 1,933
   (445 oral + 1,488 poster) and presented 1,330 (387 + 943). That single choice moves the row
   between BORDERLINE and VERIFIED. The settled unit excludes withdrawn and no-shows, so
   "presented" is correct — but flag it, because it is the whole difference.

4. **A world congress is very often not annual, and "quadrennial" is not the default.** Observed in
   this queue: **IUFRO 0.2** (five-yearly, stated in its own book — the brief's 0.25 is wrong for
   it); ICUC, Congreso Geológico Chileno and ESA LPS **0.33**; IGC, IUGG, INQUA, WCSS, IHC 0.25;
   CBG, CBCS, RST 0.5; MSJ **2**. Verify every cadence against the society's own edition list.

5. **Two-meetings-a-year rows report the larger EDITION with `events_per_yr = 2`, never a sum.**
   MSJ (春季 + 秋季) is the case here; the autumn edition is typically the larger.

6. **Sum Acta Horticulturae volumes by TITLE, never by range.** An IHC congress's volumes are
   interleaved with unrelated ISHS symposia.

7. **Extract twice and resolve on STRUCTURE, never by averaging.** Agreement is the validation, and
   it was exact at AOGS, EAAP, CBG, IAH, DGGV, WCSS-orals and MSJ. Where the modes disagree, prefer
   the structurally-anchored one:
   - **INQUA**: "title line whose next non-empty line begins with an author honorific" (2,660) beat
     "right-aligned page number" (2,632), because the latter drops short wrapped title lines.
   - **CBCS**: the dot leader (973) beat a letter-count heuristic (840).
   - **IUFRO / RST**: `-layout` wins for right-aligned dot leaders; `-raw` destroys them.
   - **WAS**: `-layout` 1,078 vs `-raw` 4 — raw collapses the columns entirely.

8. **Zero page-number collisions across a large table of contents is itself proof the count is
   clean.** 2,448/2,448 distinct at INQUA, 973/973 at CBCS, 782/782 at RST, 3,238/3,238 at IUFRO.
   Conversely, collisions are the signal that the regex is catching author superscripts or index
   lines.

9. **Chinese and Japanese sources itemise the invited layer for you — read the sentence, do not
   estimate.** CGU: `大会邀请报告 9 篇` stated outside the 3,922. CSES: `12场特邀主旨报告` outside
   the 1,136. IUGG: "the Gold Medal Lecture, nine Union Lectures, six special sessions and four
   Union Symposia" listed as completing the programme *alongside* the 4,439.

10. **Check status AND content-type AND size before counting.** Google Drive serves PDFs as
    `application/octet-stream`; a Copernicus miss is HTTP 200; a `.pdf` URL returned `text/html` in
    the engineering wave and would again.

---

## 5. Traps

- **Session codes are not two digits.** My first AOGS regex required `[A-Z]{2}\d{2}` and silently
  dropped every three-digit session (`AS105-A003`), giving 3,785 and eleven sessions that looked
  empty. Widening to `\d{2,3}` recovered 109 IDs and left only 4 genuinely empty sessions.
  **Always inspect a "zero-result" page before believing it.**
- **Spaced dot leaders.** RST's Livre des résumés uses `. . . . . .`, so a `\.{3,}` regex matches
  nothing and the 1,535-page book reads as having no contents page at all. Use `(?:\.[ \t]){3,}`.
  (Same trap as Curran/proceedings.com in the engineering notes.)
- **Animated counters hide the numbers from text extraction.** AOGS's "Event Impact" block extracts
  as `Attendees 0`; the values live in `data-target` attributes (3640 / 49 / 372 / 314). **And that
  block's year is ambiguous** — it sits among AOGS2025 retrospective links on the AOGS2026 site.
- **Percentages are not counts.** AOGS's exhibitor "Key Statistics" page carries a "Scientific
  Presentations" pie whose slices live in a JS `drawPie()` call. Its split (AS 33.0%) did not match
  my counted 2026 split (AS 29.4%, IG 13.3% vs 7.2%), because it is prior-year prospectus data.
- **A "success" that is a fallback page.** Copernicus returns HTTP 200 + a 3.53MB overview for an
  unknown meeting; Copernicus returns HTTP 200 + a 9,011-byte "404" page for a missing abstract;
  CGU returns a styled 404. Test the title or the byte size, never the status code alone.
- **Acronym collisions, all live in this field**: **CBG** = Congresso Brasileiro de Geologia *and*
  Congresso Brasileiro de Geógrafos (`cbg2024.agb.org.br`), and is one letter from **CBGE**
  (engineering geology). **CGS** = Chinese Geophysical Society (`cgs.org.cn`) *and* China
  Geological Survey. On J-STAGE, `jgeography` is 地学雑誌 (Tokyo Geographical Society), not the
  Geological Society of Japan. **Confirm the society's own domain before citing any page.**
- **Attendance is not the unit, and the presentation-to-attendee ratio varies hugely**: IUGG 89%,
  AOGS 106%, INQUA 89%, IUFRO ~80%, CBCS 65%, IGC 46%, Aquaculture ~33% (a genuine tradeshow
  hybrid), ICUC 111%. Never carry a ratio across meetings.
- **Discount exhibitor staff only, and only when the source itemises them.** CGU states its own
  split: 4,700 到会代表 of which 210 厂商参会人数 → 4,490 delegates, which is exactly the source's
  own 会议注册人数.
- **Encodings and numeral conventions**: Chinese `余` means "-odd" and rounds DOWN (the 2017 CGU
  figures are all `余`; the 2025 ones are exact); `篇` counts items, `人` people, `名` people;
  Chinese society pages decode as utf-8 or gb18030; Japanese society sites may be cp932.
- **A society's own front page can link a spam squatter.** sbgeo.org.br still links `50cbg.com`.
- **Password-protected PDFs are not rung 5** (EAAP 2026 Hamburg). No browser beats a user password.
- **A DNS failure is not a bot wall.** `lps25.esa.int` does not resolve; queueing it for a browser
  wastes the orchestrator's time.
- **Congress subdomains are not guessable by year.** RST's live sciencesconf subdomains are
  `rst-montpellier` (29e, 2025), `rst2023-rennes`, `rst2020-lyon`, `rst2014-pau` — every
  `rst<YEAR>` guess failed.
- **SEG deposits an edition in the FOLLOWING calendar year.** The "Fifth IMAGE" (2025) appears in
  the 2026 Crossref window; a naive year filter reports the edition as missing. Each edition is
  also **double-labelled** in the facet (ordinal container 555 AND generic container 548 in the
  same year) — do not add them.

---

## 6. Duplicates, and the rows I was least sure of

### Duplicate risk

- **Rows 45 and 80 are ONE meeting — proven, not inferred.** CGS's 2025 annual report:
  `中国地球物理学会第41届学术年会与「中国地球科学联合学术年会」联合举行`, followed by a single set
  of figures; and CGS's own annual-meeting index labels its 30th edition
  `第30届年会（2014年中国地球科学联合学术年会）`. CGU **is** the CGS annual meeting, every year
  since at least 2014, and CGS is its sole 承办单位. **Keep row 45, zero row 80.** Counting both
  would double 1.0 events/yr and 3,922 abstracts.
- **Row 19 (SEG IMAGE) duplicates `Census - Engineering` row 188 (AAPG ACE, 914, dated 2019)** — set
  as the queue's orchestrator note instructed. The Crossref container series proves the merger:
  `SEG Technical Program Expanded Abstracts 2019` ends and `First International Meeting for Applied
  Geoscience & Energy` begins in 2021.
- **Row 100 (Aquaculture) may duplicate the life-sciences NSA row** — the National Shellfisheries
  Association is one of four co-hosts named on the abstract book's title page (with WAS, the AFS
  Fish Culture Section and the National Aquaculture Association). I could not settle this without
  reading the life-sciences sheet, which the blind run forbids. **Flagged for the orchestrator.**

No other duplicates found across the 30 rows. Note that JpGU (row 5) and the Geological Society of
Japan (row 113) are **not** duplicates despite JGS being one of JpGU's 50 member societies — they
are separate meetings, which is why one is ~4,600 and the other ~508.

### Cadence findings worth carrying

Eighteen rows annual (1), one twice-yearly (2 — MSJ), four biennial (0.5 — CBG, CBCS, RST, and
IHC's sister series), five 0.25–0.33, and one at **0.2** (IUFRO, five-yearly).

- **IUFRO is five-yearly**, stated in its own Book of Abstracts: "Since then, congresses have
  usually been held every five years". 26th Stockholm 2024, 25th Curitiba 2019.
- **Congreso Geológico Chileno has drifted to three-yearly**: Concepción 2018, Santiago 2023,
  Valdivia 2026. Recorded 0.33, not the phase-1 note's "every 2–3 years".
- **CBG has a pandemic gap**: 48th 2016, 49th 2018, 50th Brasília 2021, 51st Belo Horizonte 2024.
  Recorded 0.5 on the standing cadence; if the 3-year interval persists it is 0.33.
- **WCSS**: 22nd Glasgow 2022, 23rd China 2026, 24th Canada 2030 (from the BSSS annual report).
- **IGC**: Busan 2024 → Calgary 2028, decided by Council vote (83 of 156 votes).

### Least sure of, in order

1. **LPSC (21)** — the edition choice decides the tier. 2026 gives 1,000 (BORDERLINE), 2025 gives
   1,831 (VERIFIED). I recorded the current edition per the "series in decline decide on the current
   edition" rule, but I have **no explanation for a 45% one-year fall** and cannot exclude from the
   asset path alone that the 2026 abstract directory was still filling when I read it.
2. **RST (52), 782** — a knife-edge OUT, **18 short of the 800 cutoff**, with extraction anchors
   spanning 728–782, and a TOC extraction loses entries rather than inventing them. The public
   Google Sheets (§2.13) would settle it in minutes.
3. **SEG IMAGE (19), 611** — a floor with an undeposited AAPG half and a pre-merger SEG series at
   1,086–1,196. Kept BORDERLINE deliberately; absence of a deposit is not evidence of a small
   meeting.
4. **SSA (43), ~904** — clears the floor by 4, and rests on the organiser's ">950 presentations"
   less 46 labelled invited, not an enumeration. The 8-column oral timetable defeats extraction; I
   could only count the poster component independently (536).
5. **EAAP (16)** — 2023 (1,787) and 2024 (1,783) both exceed 1,500 (VERIFIED) while 2025 gives
   1,347 (BORDERLINE). The four-year series swings with the venue rather than declining.
6. **Aquaculture (100)** — if the "210 posters" sit *outside* the stated 1,300 rather than inside,
   the meeting is ~1,510 and VERIFIED. The sentence is genuinely ambiguous.
7. **WCSS (13)** — accepted 1,933 vs presented 1,330 straddles the bar.
8. **IAH (66), 735** — a complete, triple-corroborated count, but only 65 below the cutoff; a
   65-presentation swing between editions brings it back.
9. **CSES (107), 1,136** — organiser-stated and excludes an unquantified poster track, so it is both
   a stated figure and a floor.
10. **IHC (15), 1,164** — a floor by construction (optional Acta papers); the real programme is
    certainly larger, possibly well over 1,500.

### Rung-5 queue, in value order

1. **JpGU (row 5)** — `https://confit.atlas.jp/guide/event/jpgu2025/top?lang=en` and the 講演検索 at
   `…/subject/-/tables?lang=en`. An exact count against the organiser's stated "over 4,600". Per the
   engineering notes: open the event search, submit an empty search for the total 講演(N), then tick
   the contributed 行事種別 categories. Exclude the 11 Public sessions, which the programme page
   states "will receive abstract submissions only from invited authors".
2. **CSES (row 107)** — `chinacses.org`, for the 论文集 and the poster count.
3. **Chinese Meteorological Society (row 46)** — `https://www.cms1924.org/xuehui-station/zbMeeting.html`
   and `academic.html` (JS lists), plus a retry of `http://nh.cms1924.org/` when its maintenance
   ends (sub-pages `/cn/web/index/29257_2531313` submission and `…_2531310` organisation).
   **This is the only row in the wave with no figure of any kind.**
4. **IHC2026 (row 15)** — `https://pub.confit.atlas.jp/en/event/ihc2026`.
5. **IGC (row 7)** — `igc2024korea.org`'s programme SPA, for an exact count against the stated 2,978.
6. **SEG IMAGE (row 19)** — the IMAGE technical programme on seg.org, which would also let the
   AAPG-side presentations be counted.
7. **RST (row 52)** — `https://rst-montpellier.sciencesconf.org/page/bilan_edition?lang=fr`, the
   post-meeting report, currently JS-only.

### Retry-later queue (not rung 5)

- **The Internet Archive** was returning HTTP 503 for the entire run, so every Wayback bypass was
  unavailable. Worth retrying for: ESA LPS 2025 (`lps25.esa.int`, domain gone), IHC2022
  (`ihc2022.org`, domain gone), and the DGGV past-edition domains.
- **`repositorio.sernageomin.cl`** — the Chilean actas (row 78). Broken TLS chain (use `curl -k`),
  then 503. DSpace, so the engineering-notes REST route applies:
  `/server/api/core/communities?size=50` → `/server/api/core/communities/<uuid>/collections?size=100`
  → `/server/api/discover/search/objects?dsoType=item&scope=<collection-uuid>&size=1`, reading
  `_embedded.searchResult.page.totalElements`.
- **`nh.cms1924.org`** — under maintenance.

---

## Orchestrator addenda (2026-09-14, after the pilot writeback)

- **Confit without the SPA — the biggest route added after the pilot.** `confit.atlas.jp` redirects
  to a NEW public mirror, `pub.confit.atlas.jp`, and
  `https://pub.confit.atlas.jp/en/event/<slug>/search?f=&t=presentation` states the platform's own
  total for any Confit-hosted meeting — JpGU 2025 = **Presentations(5,412), Sessions(761)**, read in
  one page load, no login. This superseded the rung-2 "over 4,600" greeting and promoted JpGU to
  VERIFIED. It includes invited items (marked per item, no bulk facet); state that caveat when using
  it. Expect it to settle the whole Japanese layer (soil science, geology, meteorology societies).
- **Itemised published counts are treated as counted (KCS precedent), applied consistently:** CGU
  (2,839 oral + 1,083 poster, CGS newsletter) came back VERIFIED and IUGG (3,109 oral + 1,330
  poster, annual report 2023) was raised to VERIFIED at intake to match. A ROUNDED organiser
  statement (JpGU-style "over 4,600") stays BORDERLINE. **For Rupert:** if VERIFIED should mean
  strict artefact-counts only, demote rows 8 (IUGG) and 45 (CGU) together.
- **Chinese Geophysical Society row parked as a duplicate of CGU** — the CGU annual meeting is
  co-organised by the CGS and both rows carried the identical 3,922 from the same newsletter; the
  researcher's own `duplicate_of` flag agreed. Counted once, on the CGU row.
- **SEG IMAGE (611 floor, BORDERLINE) is the post-2021 merger of the SEG Annual Meeting and AAPG
  ACE.** `Census - Engineering` row 188 still carries ACE's DATED 2019 count (914, BORDERLINE).
  **Pending Rupert's call:** whether the engineering ACE row retires in favour of the IMAGE row, so
  the merged meeting is counted once.
- **Writeback state:** wave 1 (30 rows) written 2026-09-14 — census sheet 7 VERIFIED (4.2 ev/yr) +
  14 BORDERLINE (9.24 ev/yr) + 95 NOT YET CENSUSED; deleted sheet 8 OUT on positive evidence + 1
  duplicate + the 2 load-time parkings (IGC-geography, AAG — counted on social sciences).

---

## Orchestrator addenda (2026-09-15 overnight, waves A–B, Rupert's two bells)

Routes, walls and traps found by the four wave-A researchers and the orchestrator's rung-5 pass. Field-specific
results are in the wave dirs (`scratchpad/<field>/wave*/results.json`, `REPORT` = the agents' final tables in the
session log) and in each row's Method cell; this section carries only what generalises.


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

### Earth-specific, this night
- **IUGG associations**: IAGA-IASPEI 2025 Lisbon = 1,470 (joint book of abstracts, the 43rd IASPEI assembly —
  IASPEI has held no standalone assembly this century, so its row is parked as a duplicate); IACS-IAMAS-IAPSO
  BACO-25 = 1,021; IAVCEI 2023 = 1,210; IAHS 2022 = 679 (OUT); IAG 2025 = ~700 submitted stated, 659 delegates
  (OUT; eventi.unibo.it is a CREDENTIAL wall).
- **Deposit indexes that ARE the programme** (paper required for every accepted abstract): WCGALP (Wageningen
  Academic, Crossref exact container filter, 816), SBGf (member 9850 / prefix 10.22564, 714), ARMA/MEOS (OnePetro).
  **Deposit indexes that are NOT**: IAEG (Springer chapters 309 vs 801 presented) — count the programme PDFs.
- **World Geothermal Congress**: worldgeothermal.org/cpdb2/search_results.php?conference=World+Geothermal+Congress&year=<Y>
  prints 'Found N results' (deposit index, lags); the organiser's itemised session pages are the current count (679).
- **ISC**: confer.co.nz/isc2026 links an EventsAir 'Presenters by Session' .xlsx (parse the OOXML directly) — 724.
- **Copernicus**: EPSC2026 = 1,257 (static pages); EPSC-DPS joint years count once; DPS on its own (MiraSmart) = 298.
- **Chinese societies**: CSO (cso.org.cn, plain http) publishes meeting reports but no abstract volume — rung 9
  (~110, CURATED forum, OUT); GSC circulars are mirrored by member journals/bureaux (cmgb.com.cn) — rung 9 ~780 B;
  SSSC/CSSC annual meetings ~300 (OUT).
- **AESC 2026**: the SPA's 'Download Program and Abstract Book' is a public Google Drive file (355 abstracts, OUT).
- **Dead/misleading**: iuss/22wcss walls (BSSS mirror), ippcathens2024.gr sold, sociedadgeologicamexicana.org.mx
  parked, suelossantacruz2025.com Wayback-downloader stub, sbagro.org squatter, cbagro2025.com.br empty 200.

### Wave B additions (2026-09-15 morning, four more agents)
- **Whova public agenda API**: `https://whova.com/xems/apis/event_webpage/agenda/public/get_agendas/?event_id=<eid>` (the `eid` is in the society page's `embedagenda.js` tag; the parameter must be `event_id`); `programs` is a nested list — flatten it. Won AAEA and EASP.
- **X-CD Technologies** (`xcdsystem.com/<society>/program/<key>/index.cfm`) serves the whole programme server-side with a Type label per item (AAAL 920 floor, NWSA 477 sessions); nested papers load via a POST proxy that answers 'No data available' to guests until the programme is final.
- **MyMeetingSavvy** (`<society>.mymeetingsavvy.net/program`): whole detailed programme on one page (Southern Economic Association 2,086).
- **Fourwaves**: the Nuxt shell is identical for every slug, but `api.fourwaves.com/events/<slug>` → uuid → `/events/<uuid>/sessions` gives every session with `presentationCount` (CSA 885).
- **CPSA's CFP system** generates the full programme with abstracts at `mycpsa-cpsa-acsp.ca/cfp/cfp_<year>/pdf`; cpsa-acsp.ca needs `curl --compressed`.
- **Confex is alive** for AHA (`aha.confex.com/aha/<year>/meetingapi.cgi/Paper`) and AAPOR (`aapor.confex.com`) too — AAPOR's 'Panels' records are individual presentations.
- **Oxford Abstracts `/event/<id>/titles`** settled AECT (649) and the Econometric Society (1,721); the program-pdf endpoint is sessions-only.
- **GrowthZone societies** (ACJS): programme books sit behind `…growthzoneapp.com/ap/CloudFile/Download/<key>` links listed on the society's past-programs page, not in wp-json.
- **ISTE**: the prior year's programme search loads a static cache `…/program/search/PROGRAM_SEARCH_CACHES/sessionDetails.<stamp>.js` holding every session with the organiser's own category (1,399 contributed of 1,827 items).
- **LRZ Sync+Share** (German universities): `syncandshare.lrz.de/dl/<token>/.dir` returns a shared folder as a ZIP (DGfE Programmheft).
- **Korean 'CUPID' slowAES anti-bot wall** (ekera.org) hands over key/IV/ciphertext in JS — decrypt with `openssl enc -d -aes-128-cbc -nopad` and pass the hex as a cookie; not rung 5.
- **Civilica** (`civilica.com/l/<id>/`) prints تعداد مقالات for every Iranian conference in plain HTML — the key to the Iranian layer (Geological Society of Iran 166).
- **CMOS archives**: `cmosarchives.ca/Congress_P_A/program_abstracts<YEAR>.pdf` holds every congress volume 2002–2026 with entries labelled 'Contributed abstract' / 'Invited session speaker'; the index page is iso-8859-1 — decode as latin-1.
- **Copernicus ICA hosts** are `ica-abs.copernicus.org` and `ica-proc.copernicus.org` (Crossref's prefix facet misses both).
- **IFLA repository** is DSpace 7 with the REST backend at `/rest/api` (not `/server/api`): deposits are a FLOOR (157 for 2025), never the programme.
- **AgEcon Search** returns HTTP 202 with a zero-byte body; **proceedings.science** (Galoa, ALAP) is a CAPTCHA; eventScribe instances are Cloudflare-403 to curl and WebFetch but render in a scripted Chrome (ALA, CSWE); naeyc.org and asianstudies.org refuse everything tried.
- **Discontinued / merged meetings found**: ICPS merged into the APS Annual Convention from 2025; no society-wide BPS Annual Conference since Jan 2023; WERA Focal Meeting is a strand inside a host association's meeting (a standalone WERA Congress comes in Bilbao 2027 — phase-1 gap); Ulusal Eğitim Bilimleri Kongresi not traceable after 2016; AARE's conference-papers database offline.
- **Umbrella handling applied**: CSA (885) and CSSE (829) parked as contained in the Canadian Congress umbrella (row 143, rung-9 ~4,350); CPSA 573 OUT. Reversible as a set if Rupert prefers counting members.
