# Engineering census — Phase 1 (discovery) report

Field: all of engineering except CS/AI. Worldwide. English-language searching.
Output: `names.json` (136 candidate names), `STATUS.json`.

## Names returned per sweep

| Sweep | Names |
|---|---|
| knowledge | 93 |
| world_congresses | 15 |
| national_societies | 15 |
| second_pass | 7 |
| us_society_flagships | 4 |
| trade_show_technical_programmes | 2 |
| **Total** | **136** |

81 of the 136 are flagged `boundary` (I am not confident they clear 900). 9 are flagged
`implied` — a society I can prove exists whose meeting name I never saw in English.

Searches used: **49** of the ~60 budget (hard cap 80). I stopped on saturation, not on budget.

## Which sweeps saturated

- **us_society_flagships** — saturated. The ABET member-society list enumerates the US
  engineering societies in bulk and produced nothing the knowledge sweep had missed except
  MS&T and the ACerS ceramics congress. ASABE and the American Nuclear Society turned out to
  be on the life-sciences and deleted-physical sheets already, so both were dropped.
- **gaps** — saturated hard. Four searches aimed at Taiwan, European civil engineering,
  Indian metallurgy and Latin American national congresses returned zero names above the bar.
  Taiwan's Chinese Institute of Engineers joint annual meeting draws about 400 people. Mexico's
  and Colombia's national engineering congresses are of the same order.
- **national_societies** — saturated in English, NOT saturated in fact. See the language gap below.
- **world_congresses** — saturated. The last pass returned ISPRS, EUROMAT and the Combustion
  Institute symposium and nothing else new.
- **second_pass** — added 7, then stopped returning new names.

## Removed as already covered

Checked every candidate against the three exclusion files and dropped these, which are already
on a census or deleted sheet or already checked in DBLP or Crossref: PVSC, APEC, IEEE IAS Annual
Meeting, ICEM, ECOC, WHEC, European Control Conference, Frontiers in Education, IWA World Water
Congress, EUROCORR, AMPP, Geo-Congress, ESREL, COBENGE, SEG IMAGE, PowerTech, ICSV, ASABE,
American Nuclear Society meetings, IABSE, INTERMAG.

## The names I am LEAST sure clear 900 — take these last

1. **NASCC: The Steel Conference** and **ACI Concrete Convention** — practitioner conventions.
   Session programmes are large but contributed technical papers may be near zero.
2. **ASCE ICTD**, **SAE COMVEC**, **ASME FEDSM** — society-press proceedings in the low hundreds.
3. **ISARC** — I expect 200 to 400 papers. Included only because construction automation had no
   other candidate.
4. **PCIM Europe**, **OTC**, **URTeC**, **IPTC** — big exhibitions with small paper programmes.
   All flagged BOUNDARY.
5. **IMEKO World Congress**, **ICPR**, **APIEMS**, **CSCE Annual Conference**, **DGLR
   Luft- und Raumfahrtkongress**, **SEFI** — several hundred each on my estimate.
6. **ICCE (Coastal Engineering)** — ASCE states about 900 *participants* in 2024, so the paper
   count is well under that.
7. **IEEE PES General Meeting** — the call for papers says up to about 800 conference papers are
   accepted. It clears 900 only if panel and poster presentations are counted. Real boundary case.
8. **WEFTEC** — 23,000 attendees but only 125-plus technical sessions. I moved it to boundary
   after reading the program page.
9. The **9 `implied` rows** — six Chinese national societies (CSEE, CMES, CSAA, CCES, CHES, CIE,
   CSAE), the CAST annual meeting, and the Indian Engineering Congress. These are honest
   placeholders: I confirmed the society, never the meeting's size or even its exact name.

## Names I am most confident about

TRB Annual Meeting, AIJ Annual Meeting, JSCE Annual Meeting, IEEJ Annual Meeting, IEICE General
and Society Conferences, ASME IMECE, IAC, INFORMS Annual Meeting, WCEE, CCTAM, WCCM, ECCOMAS,
ISPRS Congress, KSME Annual Meeting, KIEE Summer Conference, ASEE Annual Conference, CIGRE
Session, CIRED, JIM Spring and Autumn Meetings, EUROMAT.

## Size hints recorded (from pages I opened)

| Conference | Hint |
|---|---|
| JSCE Annual Meeting | over 5,000 attendees, over 3,000 research papers and posters |
| ASME IMECE | roughly 2,400 papers, presentations and posters in 17 core tracks |
| IAC | nearly 6,400 abstracts from 103 countries (IAC 2025 call results) |
| CCTAM | ~5,000 attendees, 27 parallel sessions, 56 thematic symposia |
| SAECCE | 800-plus presentations, 86 poster sessions, ~10,000 attendees |
| KSME Annual Meeting | more than 1,400 lectures and papers, 3,000 attendees |
| ISPRS Congress | more than 1,500 papers presented (2022) |
| FEMS EUROMAT | over 1,800 scientists (2025) |
| IEEE PES General Meeting | up to approximately 800 conference papers accepted |

## Countries I could only see through English — where a local-language pass is needed

- **China — the largest gap by far.** Chinese engineering societies run their research programme
  through 专委会 (technical-committee) annual meetings rather than one society congress, so an
  English search finds the society and not the meeting. A follow-up should search
  `<society> 年会 2025 论文 摘要 报告数 参会人数` and `学术年会 征文` for CSEE, CMES, CSAA, CCES,
  CHES, CIE and CSAE, and should look for each society's own 会议 listing page. My one Chinese
  query worked when aimed at a named meeting: it returned CCTAM's 5,000 attendees and SAECCE's
  800-plus reports. Aimed at a society, it returned nothing.
- **Japan.** I have the society names but no counts. Use `全国大会 / 年次大会 / 講演会` with
  `発表件数` or `講演件数` and `参加者数`, per society: 日本機械学会, 電気学会, 電子情報通信学会,
  日本建築学会, 日本コンクリート工学会, 自動車技術会, 精密工学会, 日本鉄鋼協会, 日本金属学会,
  日本ロボット学会, 空気調和・衛生工学会, 日本原子力学会.
- **Korea.** Use `학술대회 / 학술발표대회 / 추계학술대회` with `논문 편수` and `발표`. One useful
  calibration found in Korean: the KSCE conference proceedings hold 20,823 papers across
  2002-2025, roughly 900 a year, so KSCE sits exactly on the bar. Societies to search:
  대한기계학회, 대한토목학회, 대한전기학회, 대한건축학회, 대한전자공학회, 한국통신학회,
  한국자동차공학회, 한국항공우주학회.
- **Russia, Turkey, Iran.** English and one local-language query each returned only meetings of
  150 to 400 papers. I found no Russian, Turkish or Iranian engineering meeting that plausibly
  clears 900, but Russia deserves the `съезд / конференция / тезисы докладов` treatment that
  lifted chemistry from 4 names to 61.
- **Brazil and Latin America.** Portuguese and Spanish searching showed COBENGE at about 500
  works and CONTECC at 436, both below the bar. ABES (sanitary and environmental) is the one
  Brazilian society I could not size and have left in as boundary.
- **Germany, France, Italy, Spain.** CFM and DAGA are the only two I judged plausible. A
  `Jahrestagung / Beiträge` and `congrès / communications` pass would confirm or kill them.

## List pages and directories that enumerated many meetings at once

- **ABET member societies** — https://www.abet.org/member-societies/ — 34 US engineering
  societies in one page. The single most efficient enumeration I found for the US.
- **ASME conferences index** — https://www.asme.org/conferences-events/asme-conferences —
  states ASME runs nearly 30 conferences a year.
- **WFEO national and affiliated members** — https://www.wfeo.org/nationals/ — about 100
  national bodies by country. Useful for knowing which countries have a national engineering
  body, but nearly useless for this census: WFEO members are chambers, councils and registration
  boards, not research-conference organisers. Recorded so nobody spends the search again.
- **CAST** — states 210 national member societies and an annual meeting of 118 themed forums
  co-organised by over 100 societies. This is the door to the Chinese layer.
- **Confit** (Japan) and **DBpia** (Korea) are the national platforms for society proceedings;
  **AURIC** holds the Korean architecture and civil volumes. Each indexes many societies'
  meeting volumes in one place and would give exact per-meeting counts.

## Method notes for phase 2

- Most of these meetings publish counts only in a post-event news item, not on the conference
  site. The rung that worked was a named-meeting query in the local language.
- Several US bodies publish a session count, not a presentation count. Treat "125 technical
  sessions" as roughly 500 to 800 presentations and label it inferred.
- The Japanese and Korean society meetings are short-paper meetings: a "paper" is two to six
  pages and the counts are correspondingly high. They clear the bar on volume, not on depth,
  consistent with how the chemistry census treated CSJ.
