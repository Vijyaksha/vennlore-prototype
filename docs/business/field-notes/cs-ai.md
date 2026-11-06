# Field notes — computer science & AI

Companion to `census-methodology.md`, which stays general. This file holds only what is true of
**CS & AI** and would be noise in the general method. Read both before working a CS & AI row; add
what you learn here, not there.

Started 2026-09-13 from the index pass (DBLP + Crossref, 62 rows at zero searches) and the
2026-09-14 second-pass phase 1; the wave-1 section at the end records what phase 2 over the 30
second-pass names found (2026-09-14).

## The unit, settled

Accepted contributed presentations = **accepted main-track papers + posters; workshop and
companion volumes separate; invited talks excluded.** CS conferences publish acceptance counts, so a
"paper" is the abstract of this field. The old note that CS "needs a bar redefinition" is void.

## Scope, and where CS & AI overlaps other censuses

| Meeting | Where it is counted |
|---|---|
| Robotics (ICRA, IROS), signal processing (ICASSP), communications (ICC, GLOBECOM, VTC), circuits (ISCAS), control (CDC), industrial electronics (IECON), remote sensing (IGARSS), SMC | `Census - Engineering` |
| EMBC, ISBI (biomedical) | `Deleted - Engineering` (EMBC parked: counted on medicine) / OUT |
| ISMB, RECOMB, ECCB (bioinformatics) | `Census - Life Sciences` |
| BMES | `Census - Medicine & Health` |
| SPIE, Optica meetings (imaging/photonics) | `Census - Physical Sciences` |

Boundary rows on this sheet, flagged in the Umbrella column: CogSci, HICSS, BIBM, MICCAI.
INFORMS goes on Engineering (operations research); Sunbelt waits for a social-sciences sheet.

## Where CS & AI publishes its counts — zero-search routes, ranked

1. **DBLP's SPARQL endpoint — the whole indexed field in one query.** `https://sparql.dblp.org/sparql`
   is open to plain HTTP requests (dblp.org's HTML and search API sit behind an Anubis anti-bot
   challenge, which is rung 5; the SPARQL host does not challenge). Per-stream paper counts per year:
   ```
   PREFIX dblp: <https://dblp.org/rdf/schema#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
   SELECT ?stream ?title (COUNT(?p) AS ?n) WHERE {
     ?p dblp:publishedInStream ?stream ; dblp:yearOfPublication "2025"^^xsd:gYear .
     ?stream a dblp:Conference ; dblp:streamTitle ?title . }
   GROUP BY ?stream ?title HAVING (COUNT(?n) >= 300) ORDER BY DESC(?n)
   ```
   Split workshop volumes with `dblp:publishedAsPartOf ?vol` and exclude volumes titled
   "Workshops"/"Companion" (`scratchpad/dblplib.py::main_track_split`). Source URL for the row is
   the stream page `https://dblp.org/streams/<key>`; say in Method that it was read via SPARQL.
   Every stream at ≥300 papers in 2024–2025 has already been counted (`scratchpad/cs/p1_csai/dblp_checked.json`).
2. **Crossref proceedings-article facet by container title** — the independent second source and
   the catch for series DBLP lacks. `api.crossref.org/works?filter=type:proceedings-article,from-pub-date:2025-01-01,until-pub-date:2025-12-31&facet=container-title:*&rows=0`
   gives the top 1,000 containers; a per-conference query filters on the exact container title.
   Where both sources hold a meeting they agree within a few papers (CVPR 2,871 vs 2,881).
3. **The venue's own accepted-papers page.** ICLR, NeurIPS, ICML, COLM, RLC, MLSys, CoRL review on
   OpenReview, but **the OpenReview API is now behind a challenge** (`api2.openreview.net` returns
   HTTP 403 `ChallengeRequiredError` even with a browser user-agent — rung 5, 2026-09-14). Use the
   venue's own accepted-papers table instead: COLM moved to `colm.cc/Conferences/<year>/AcceptedPapers`
   (static HTML, one `<tr>` per paper; 856 in 2026, workshops separate).
4. **ACL Anthology** for the NLP family: one volume page per event, one row per paper
   (`aclanthology.org/events/<acronym>-2025/`), Findings volumes listed separately.
5. **National society proceedings platforms** (the second-pass rows live here):
   - **J-STAGE** hosts JSAI's annual-conference proceedings (`jstage.jst.go.jp/browse/pjsai/`,
     one volume per year, paginated listing = countable) and IPSJ material; JSAI's news page
     states the presentation count in Japanese (2025: 1,186 presentations, 4,939 participants).
   - **IPSJ National Convention** proceedings are on IPSJ's digital library (`ipsj.ixsq.nii.ac.jp`);
     the convention site states the number of presentations per year.
   - **Confit** (`confit.atlas.jp`) is a JS SPA — HTTP 202 with an empty body to `curl` — so it is
     **rung 5, orchestrator-only**; it renders a `Presentations(N)` count once loaded.
   - **Korea is NOT rung 5**: KIISE publishes a downloadable programme book and KIPS runs on
     ManuscriptLink (both routes in the wave-1 table below); DBpia/KISS are not needed.
   - **CCF** recommendation notice enumerates the 36 Chinese national CS conferences
     (`ccf.org.cn/Media_list/ccf/2025-11-21/853354.shtml`); CNCC's own site states forum counts,
     but its forums are largely invited — count contributed posters/papers only.

## Traps specific to this field

- **Workshop inflation.** A DBLP stream or Crossref container often bundles workshop and companion
  volumes: CVPR 2025 = 2,871 main + 675 workshop; CHI = 1,249 + 920. Count main track only.
- **Umbrella double-counting.** FCRC, WCCI, SSCI and the IEEE CS umbrella weeks are sums of
  tracks already counted separately (WCCI = IJCNN + FUZZ + CEC). Never add an umbrella row when
  its tracks are on the sheet.
- **Attendance ≠ presentations, worse than elsewhere.** NVIDIA GTC, RSA, FOSDEM and Grace Hopper
  are session-programmed events; CNCC's 12,000 registrations sit over mostly-invited forums. Judge
  on contributed papers, and mark CURATED where there is no open call.
- **Biennial and rotating series**: ECCV (even years), ICCV (odd years) — DBLP dates the ECCV 2024
  LNCS volumes 2025. Events/yr 0.5.
- **Journal-first venues are already covered**: VLDB (PVLDB), SIGMOD (PACMMOD), CSCW (PACMHCI),
  UbiComp (IMWUT), SIGGRAPH (TOG) all appear in DBLP under their conference identity; the
  programming-languages family (PLDI 89, POPL 81, OOPSLA 214 in 2025) is far below the bar.
- **Anubis on dblp.org.** The HTML site and search API challenge bots; a Playwright session clears
  it in ~8 s. Prefer SPARQL; only fall to the browser for the stream page as the citable URL.

## Wave 1 (2026-09-14, the 30 second-pass rows): 4 searches, 26 rows at zero searches

Verdicts: 1 VERIFIED (IPSJ National Convention 1,608), 7 BORDERLINE kept (JSAI 1,174, SIAM CSE 1,433,
FOSDEM 989, COLM 856, KCC 854, FCRC 856 as one federated week — Rupert's call, CSI India unresolved),
21 OUT on positive evidence, 2 parked as duplicates (WCCI = IJCNN + CEC + FUZZ-IEEE; INFORMS is on
Engineering). **The index pass had already caught everything large: the second pass added one
VERIFIED row.** CS & AI is now effectively closed at the English + JP/CN/KR level.

### Zero-search routes found in wave 1 — try these before searching

| Route | How | Settled |
|---|---|---|
| **CCF's JSONP content API** — unlocks every CCF-hosted meeting (CNCC, HPC China, ChinaSoft …) | The sites are Vue SPAs with empty HTML, but `POST https://ccf.org.cn/api/getMeetingIdByMeetingShort.action` with `meetingShort=<CODE><year>` (e.g. `CNCC2025`, `HPCChina2025`) returns the meeting id, then `GET https://ccf.org.cn/api/indexPageChannelData.action?meetingId=<id>&jsoncallback=cb` returns the whole site as JSONP: news, invited speakers, programme, the post-meeting report | CNCC (CURATED), HPC China 100+ |
| **`loadPage`-style SPAs: read the router** | `chinasoft.ccf.org.cn/2026/js/route.js` shows `./pages/${page}.html` — every section is a static file (`/2026/pages/callforpaper.html`, `/agenda/…/index.html`). Read the router JS before calling any SPA browser-only | ChinaSoft |
| **gakkai-web.net** — Japanese society programme host | `https://www.gakkai-web.net/<society>/<edition>/program<edition>.html` is one static page for the whole convention; count session codes `[0-9][A-Z]{1,3}-[0-9]{2}`. Contains only 一般/学生 sessions, so invited talks are already outside it | IPSJ 1,608 |
| **J-STAGE volume listing** | `jstage.jst.go.jp/browse/pjsai/<vol>/0/_contents/-char/ja`, 50 per page. **`?from=` is ZERO-BASED**: the bare URL is page 0 and `?from=1` is records 51–100; treating `?from=1` as the first page drops 50 records | JSAI 1,174 |
| **KIISE programme book** (Korea) — NOT rung 5 | `kiise.or.kr/conference/kcc/<year>/` is a frameset; the programme menu links `https://www.kiise.or.kr/conference02/data/<conf><year>/PB.pdf` (49MB). Count paper codes `[0-9][AP]-[OP][0-9.]+-[0-9]+` (oral `…-O…`, poster `…-P…`) | KCC 854 (188 oral + 666 poster) |
| **ManuscriptLink programme books** (KIPS and other Korean societies) | `https://manuscriptlink.com/society/kips/conference/<conf><year>/programBook` — server-rendered, no token; paper ids `KIPS_C2025B0255` | KIPS ACK 329 |
| **meetings.siam.org** | `www.siam.org` is Cloudflare-blocked, but the legacy host is plain HTML: `meetings.siam.org/speakdex.cfm?CONFCODE=<code>` (one page, every presentation with its role) and `program.cfm?CONFCODE=<code>` | SIAM CSE 1,433 |
| **Conferia.js widgets** | The programme widget is configured in the page source with a plain CSV `src:` — fetch the CSV, no browser | IC2S2 622 |
| **Google Sheets / Docs programmes** | `docs.google.com/spreadsheets/d/<id>/export?format=xlsx` exports a linked programme sheet as a workbook | CCS 359 |
| **ANLP proceedings page** (言語処理学会) | `anlp.jp/proceedings/annual_meeting/<year>/` lists one PDF per paper under `/pdf_dir/`; prefixes B/C/P/Q/TS are contributed, invited items deposit no PDF | ANLP 797 (OUT by 3) |
| **nvidia.com `<page>.json`** | `https://www.nvidia.com/gtc/session-catalog.json` returns the session catalog as JSON (Adobe CMS convention; works on some pages, not all) | GTC (CURATED, 952 industry sessions) |
| **RainFocus catalogs** (GHC and many industry events) | The page embeds `apiToken` and `widgetId`; `POST https://events.rainfocus.com/api/search` with headers `rfapiprofileid`/`rfwidgetid` and body `type=session&size=10&from=0` returns `totalSearchItems`. Per-event tokens. RSA's `path.rsaconference.com` flow portal is the authenticated variant and does NOT open this way | GHC (ceiling 425 sessions) |
| **Wayback for Cloudflare-blocked sites** | `fcrc.acm.org` 403s; the CDX listing + a 2023 capture gave the constituent conferences and cadence | FCRC |

### Traps found in wave 1

- **Forum congresses are CURATED, however big the headcount.** CNCC (12,000+ registrations, 130
  invited forums, 700+ invited speakers), CCAI (23 invited sessions), CCIG (45 forums) have no call
  for papers. The Chinese terms to test for a contributions call: 征文 / 征稿 / 投稿 / 论文 / 海报 / 墙报.
- **Umbrella weeks are sums of tracks.** WCCI = IJCNN + CEC + FUZZ-IEEE (IJCNN already on the sheet);
  FCRC's 14 tracks are each under 300 papers so none is on any sheet — FCRC was kept as ONE meeting
  (856, quadrennial) pending Rupert's call; FLoC's 10 tracks sum to 490.
- **Industry events settle on a session ceiling, no ratio needed.** When the organiser states the
  TOTAL number of sessions (RSA 570+, GHC 425+) and it is below the bar, contributed presentations
  are a subset and the row is OUT without a conversion.
- **Satellite workshops hold the bulk at complexity meetings.** CCS 359 and NetSci 534 on the main
  programme; most of their volume is in excluded satellites. They move together if the unit changes.
- **Cadence quirks**: SIAM CSE biennial (0.5); FCRC and FLoC quadrennial (0.25); GTC three editions a
  year; KIPS twice a year (ACK autumn, ASK spring); CEDI every three years.
- **DBLP absence is not a size signal.** IPSJ (1,608) and JSAI (1,174) are the two largest CS meetings
  in Japan and neither is in DBLP.
