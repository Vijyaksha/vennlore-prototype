# CS & AI census — Phase 1 second pass. Discovery report

**Date:** 2026-09-13. **Searches used:** 46 of a ~60 budget (hard cap 80). **Names returned:** 31.
**Output:** `names.json` (31 records), `STATUS.json`.

All 31 were checked against `existing_names.json` (1,522 rows), `dblp_checked.json` (149 streams)
and `crossref_checked.json` (708 containers). None duplicates a row in those files.

## Names per sweep

| Sweep | Names kept | Saturated? |
|---|---|---|
| knowledge | 24 | n/a (baseline) |
| journal_first | 0 | yes, immediately |
| national_congresses | 0 net new (refined and pruned the knowledge set) | yes |
| openreview_and_new_ai | 0 | yes |
| mega_multi_track | 2 | yes |
| education_and_industry | 1 | yes |
| gaps | 2 | yes |
| second_pass | 2 | yes |

Every sweep after the knowledge baseline returned fewer than three plausible new names, which is
the saturation signal the brief defines. Four names from the knowledge baseline were **deleted**
once searching sized them below the bar, which is as useful a result as an addition:

- **VALSE** (China, vision and learning) — 6,000 attendees but only ~390-400 posters.
- **INFORMATIK / GI Jahrestagung** (Germany) — festival format, roughly a hundred LNI papers.
- **Korea Software Congress (KSC)** — 574 papers in the 2025 proceedings.
- **CCEC, China's university computing-education congress** — ~1,000 attendees, 76 forum talks.

## Why journal_first came up empty

This was expected to be a rich vein and is not. Every large journal-first venue the brief names is
already in `dblp_checked.json` under its conference identity: VLDB, SIGMOD, SIGGRAPH, SIGGRAPH Asia,
UbiComp, CSCW, CHI. What remains is the PACMPL family, and those meetings are small: PLDI 89 papers,
POPL 81, OOPSLA 214 in 2025. Even the whole ICFP/SPLASH week does not approach 900. PACMNET
(SIGCOMM/CoNEXT) is smaller still. The vein is genuinely exhausted, not under-searched.

## The names I am LEAST sure clear the bar — take these last

Ordered from least to most confident. All are flagged `boundary: true` in `names.json`.

1. **CSI Annual Convention (India)** — `implied: true`. India is an IFIP country-representative
   member, but no 2025 or 2024 convention programme surfaced in English at all. This is an honest
   placeholder for a society that exists, not evidence of a meeting.
2. **IFIP World Computer Congress** — irregular; may not have run recently at scale.
3. **RSA Conference** and **NVIDIA GTC** — industry venues with open calls but no proceedings. GTC
   San Jose 2025 ran 700+ sessions; RSA is of the same order. Both are session counts, not papers.
4. **Grace Hopper Celebration** — very large attendance, but the contributed share (sessions plus the
   ACM Student Research Competition posters) is likely well under 900.
5. **CNCC** and **CCIG** — both have overwhelming attendance (12,000+ and 4,000+) across 150 and 45
   forums respectively, but Chinese flagship congresses run mostly **invited** forum talks. The
   contributed count could be an order of magnitude below what attendance suggests. Phase 2 must
   count contributed items, not forums.
6. **FCRC** and **WCCI** — umbrella totals that clear the bar only by summing tracks that are
   **already separately in DBLP** (STOC/ISCA/PLDI for FCRC; IJCNN/CEC for WCCI). Counting them risks
   double-counting rows already on the sheet. I listed them because the brief asks for umbrellas, but
   I would drop both before I would drop anything else here.
7. **KIPS ACK**, **JAIIO**, **CLEI**, **CEDI**, **HPC China**, **ChinaSoft**, **CCAI**, **FLoC**,
   **COLM**, **FOSDEM**, **SSCI**, **Korea Computer Congress** — genuine uncertainty rather than
   known-small. KCC is the closest call in the whole list: its 2025 proceedings run to roughly 850
   papers, just under the bar, and could cross it with posters counted.
8. **INFORMS Annual Meeting** and **Sunbelt** — a **scope** question, not a size one. Both are
   comfortably over 900 contributed abstracts and both are abstract-only, so neither index sees them.
   INFORMS is operations research and analytics; Sunbelt is social network analysis. Someone has to
   decide whether they belong to CS at all. They are not the engineering agent's by the brief's list
   either, so they would otherwise fall through the gap between fields.

The names I am **most** confident about are JSAI (1,186 presentations, 4,939 participants in 2025),
IPSJ National Convention (~1,200 general presentations), SIAM CSE, and IC2S2.

## Countries seen only through English — where a local-language pass is needed

I searched Japanese, Chinese and Korean directly where a society was clearly non-anglophone, per
the methodology. Those three are covered. The following are **not**, and a follow-up pass should
use the terms given:

| Country / region | Terms a follow-up must use | Why it matters |
|---|---|---|
| Russia and CIS | съезд / конференция / тезисы докладов; "Информатика", "Вычислительная техника" | English search found only student and teaching conferences. Chemistry's local-language pass took Russia from 4 names to 61, so the blank here is almost certainly a search artefact. |
| Latin America | congreso nacional de informática / computación, jornadas, anales, trabajos | CLEI, JAIIO, CSBC and CEDI are the only Spanish and Portuguese names I could see. Mexico (SMCC), Chile (SCCC), Colombia and Peru returned nothing in English. |
| Turkey | kongre / kurultay / bildiri özetleri | UBMK sizes at ~135 papers, and TBD's Ulusal Bilişim Kurultayı is a professional assembly, but I only reached them through one query. |
| Iran | کنفرانس / مقالات; CSICC | Not reachable in English at all. |
| Poland, Czechia, Hungary, the Nordics | zjazd / kongres; konference; konferencia; møte / möte | CEPIS lists a society in each, but none surfaced a research congress in English. |
| Africa and the Middle East | varies; start from IFIP's Ghana, Nigeria, South Africa, Uganda and Zimbabwe members | Nothing at the 900 bar found in English. May genuinely be empty at this scale. |
| Southeast Asia | Indonesian *seminar nasional*, Vietnamese, Thai | APTIKOM's SEMNASTIK exists but looks small; the region is fragmented across hundreds of small venues rather than one large one. |

## List pages and directories that enumerated many meetings at once

These are the pages worth revisiting first in any follow-up; each named many meetings in one fetch.

- **CCF's 2025 recommendation notice** — https://www.ccf.org.cn/Media_list/ccf/2025-11-21/853354.shtml
  Enumerates **36 Chinese national CS conferences** in one table, with Chinese names. This is the
  single best China-side directory I found. Most of its rows are a few hundred papers and so are not
  in `names.json`, but the page is the definitive list of what CCF runs nationally.
- **CEPIS member societies** — https://cepis.org/member-societies/ — 28 European national informatics
  societies with countries.
- **IFIP country-representative members** — https://www.ifip.org/country-representative-members/ —
  39 countries, plus ACM, CLEI, CEPIS, SEARCC, IMIA and VLDB as affiliated members. CLEI and SEARCC
  are themselves federations and each unlocks a regional layer.
- **CCF conferences portal** — https://www.ccf.org.cn/Activities/ConferenceS/ — CCF's own brand-level
  event list (CNCC, YEF, FCES, CIMC, CCDE and others).
- **Wikipedia, List of computer science conferences** — comprehensive but almost entirely DBLP-indexed
  venues, so low marginal value for this particular job.

## Method notes and caveats

- `size_hint` is populated only where I opened the page and it stated the figure: CNCC (registrations),
  CCIG (forums and attendees), GTC (sessions). Figures quoted in `why_plausibly_900` that came from a
  search-result snippet rather than a page I opened are described as reported, not recorded as hints.
- The JSAI figure (1,186 presentations, 4,939 participants) comes from the society's own report in
  *Jinko Chino* vol. 40 no. 6. The J-Stage PDF would not render through WebFetch, so it is in the
  rationale rather than in `size_hint`.
- I did not research any conference's size beyond what a page stated, and wrote nothing outside
  `names.json`, `STATUS.json` and this file.
- Predatory series (WASET, OMICS, conferenceindex aggregator listings, Magnus Group and lookalikes)
  appeared in several Indian and Turkish result sets and were excluded on sight. Every name returned
  traces to a society, a federation or a series with past editions.
