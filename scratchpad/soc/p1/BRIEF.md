# Social sciences & education census — PHASE 1 (discovery). Agent brief.

You are building the list of **large social-science and education conferences worldwide** — the
meetings that plausibly run **900 or more accepted contributed presentations** (papers + posters,
invited talks excluded) in one edition. This is a NEW field for the census: nothing in it has been
enumerated before, so cast wide across the disciplines, but keep the bar in view — the phase-2 team
will research every name you return.

**Names only.** No abstract counts, no per-conference digging, no verification. A `size_hint` is
welcome when a page you already opened states one; never spend a search chasing a number.

## Read first

- `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md` — sections
  **"Phase 1 — Discover every candidate name"** and **"Search in the conference's own language"**.
- The exclusion files in your directory `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/soc/p1/`:
  - `existing_names.json` — every conference already on ANY census or deleted sheet (1,688 rows,
    with sheet and society). Do not return any of these. Match by society and meeting, not by exact
    string. Already known and NOT yours: APA Convention and APS Convention (on the life-sciences
    sheet as boundary rows — they will be moved, not re-listed); CogSci and HICSS (CS & AI); INFORMS
    (engineering); the medicine sheet's public-health, nursing and health-education meetings.
  - `crossref_seen.json` — 708 Crossref proceedings containers with ≥300 papers in 2024–2025. Any
    social-science or education meeting in it is a confirmed lead (AERA ~4,700; IATED's ICERI,
    EDULEARN and INTED 1,250–1,750 each; CONIC 1,125) — list those, and use the file to notice what
    else is there.

## The bar, and what "large" means here

Return names you judge **plausibly** clear ~900 accepted contributed presentations. Over-include on
genuine uncertainty (a national society's annual meeting you cannot size), but do not pad with
meetings you know run a few hundred papers. There is no target count: return as many as you are
comfortable standing behind. In this field the big US disciplinary meetings run 2,000–6,000
presentations and the European and Asian mirrors 1,000–3,000; the plausible pool is probably
80–150 names.

## Scope

**Social sciences and education**, worldwide: psychology (research societies — APA/APS are known),
sociology, political science and international relations, economics and finance (ASSA/AEA, EEA,
RES, AFA), geography (AAG, RGS-IBG, IGU), anthropology and archaeology (AAA, SAA, EAA), criminology
(ASC, ESC), communication and media (ICA, NCA, ECREA), demography and population (PAA, IUSSP),
linguistics (LSA, AILA), education research (AERA, ECER/EERA, EARLI, BERA, AARE, ISLS, NARST,
comparative and international education, engineering/medical/science education where not on
another sheet), educational technology (AECT, EDULEARN-type series), social work, public policy and
administration (APPAM, NASPAA), law and society, urban studies and planning (ACSP, AESOP), library
and information science (ASIS&T, iConference), sociology of science, gerontology (GSA — the
Gerontological Society, not the geologists), and the general social-science congresses (the national
academies' congresses, the Federation of Social Science Societies in Canada, the ESRC/ISSC-type
federations). **Business and management** (AOM, EGOS, AMA, AIB, SMS, AAA accounting) are NOT in
scope this pass — they will be their own field; list them only if they turn up incidentally, flagged
`boundary: true`. Psychology's research societies ARE in scope (SPSP, SRCD, Psychonomics, EPA,
ICP/IUPsyS, EFPA, JPA, CPS, KPA); clinical/psychiatric meetings are medicine's.

**English-language searching** (a society's own English pages and federation lists are fine). The
local-language pass is deferred, not waived — say in your report which countries you could only see
through English and the terms a follow-up should use (年会/大会 + 発表, 学会 + 学术年会 + 论文, 학술대회 +
논문, Jahrestagung + Beiträge, congrès + communications, congreso + comunicaciones, congresso +
trabalhos).

## Where the names are — search these, in order, checkpoint after each

1. `knowledge` — list what you already know before any search.
2. `us_flagships` — the US disciplinary annual meetings, one per discipline above, and their
   size where the society states it (AAG, APSA, ASA, AAA, ASC, ICA, NCA, PAA, LSA, AERA, SRCD,
   SPSP, ASSA, APPAM, ACSP, ASIS&T, GSA gerontology, NCTE/NCTM, NAEYC, ASHE, CIES …).
3. `european_mirrors` — ECPR, ESA, EAA, ESC, ECREA, EAPS, EEA, ECER, EARLI, RGS-IBG, EASP, ESRA,
   EUROGEO, the German DGS/DVPW/DGfE/DGPs, the French AFS/AFSP/SFP, the Spanish, Italian, Nordic,
   Polish and Turkish societies; the ESRC festival-type events only if they carry contributed papers.
4. `asia_pacific_and_latam` — Japan (JPA psychology ~3,000 presentations, JES education, JSS
   sociology, JPSA, JAEA), China (CPS psychology, the CASS congresses, CNKI-listed 年会), Korea
   (KPA, KSA, KAPA), India (ISPP, ISEC, IEA), Australia (AARE, APS, ASSA, TASA), Brazil (ANPEd,
   ANPOCS, SBS, ANPAD if business), Mexico (COMIE), Argentina, the Latin American federations
   (CLACSO, ALAS, FLACSO); the Asian and Pacific federations (AASSREC, APEA, WERA).
5. `federations_and_world_congresses` — the world congresses per discipline (ISA World Congress of
   Sociology, IPSA, IUPsyS/ICP, IGU, IUAES, ISSP, WERA, ICLASP, World Congress of Applied
   Linguistics, IAMCR, IUSSP, IEA World Congress, ICME mathematics education), and the federation
   member lists (ISSC/ISC, IFSSO, CESS, FeSPB) that enumerate national societies in bulk.
6. `education_series_and_edtech` — IATED (ICERI, EDULEARN, INTED), the ISTE and AECT conventions,
   EDUCAUSE, the OER/e-learning congresses, teacher-education congresses (ATE, ATEE, WFATE),
   ICME, ESERA, NARST, ASEE-type meetings for other disciplines (already on engineering — exclude),
   IEEE EDUCON/FIE (check the exclusion file — FIE may be on CS/engineering).
7. `gaps` — geography mirrors of every big US body, publication trails (journal supplements and
   proceedings series imply a meeting), predatory-looking series excluded (WASET, OMICS,
   conferenceindex, Magnus Group, IISES-type mills and lookalikes never count — a real meeting traces
   to a society, a university, or a series with past editions).
8. `second_pass` — re-run the sweep that produced the most, looking for what it missed.

Stop a sweep when a pass returns mostly names you already have; **when a sweep adds fewer than ~3
plausible names, it is saturated.**

## What to return per name

```json
{
  "conference": "AAG Annual Meeting",
  "society": "American Association of Geographers",
  "country_or_region": "US",
  "subfield": "geography",
  "frequency_note": "annual",
  "why_plausibly_900": "the largest geography meeting in the world; thousands of paper and poster sessions",
  "size_hint": "over 5,000 presentations (2025 press release)",
  "size_hint_url": "https://...",
  "source_url": "https://www.aag.org/events/aag2025/",
  "sweep": "us_flagships",
  "boundary": false,
  "implied": false
}
```

`source_url` is where you saw the name. `size_hint` is only what a page you already opened states,
verbatim, with its URL — a snippet figure from a search result you did not open is NOT a size hint;
write nothing. If a federation list proves a society exists but you never saw its meeting's name,
list the society as the conference with `"implied": true` — an honest placeholder, never an invention.

## Budget and output

**~70 web searches, hard cap 90.** Prefer pages that enumerate over pages that describe.

**Output**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/soc/p1/names.json` — a JSON list
of the records above, **rewritten in full after every sweep**, de-duplicated within itself and
against the exclusion file.

**Progress**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/soc/p1/STATUS.json` —
`{ "sweeps_done": [...], "names": n, "searches_used": n, "in_flight": "<sweep>" }`, rewritten
whenever it changes.

## Do not

- Do not research any conference's size beyond what a page you already opened states.
- Do not write to any spreadsheet or `.xlsx` file; do not modify any file outside your two output
  files; do not read any file under `scratchpad/` other than the ones in your own directory.
- Do not ask anyone to change a permission or config setting. If the search budget runs out, stop
  and say so — your checkpointed file is the result.

## Finish by reporting (INLINE in your final message — do not write a report file)

Names returned per sweep and per discipline; searches used; which sweeps saturated; the names you
are LEAST sure clear the bar; the countries you could only see through English with the
local-language terms a follow-up should use; and any list page or federation directory that
enumerated many meetings at once.
