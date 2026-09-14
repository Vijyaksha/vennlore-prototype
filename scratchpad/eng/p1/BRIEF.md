# Engineering census — PHASE 1 (discovery). Agent brief.

You are finding the **large engineering conferences that no paper index sees**. A first pass
(2026-09-13) counted every conference stream in DBLP and every proceedings container in Crossref,
which caught the IEEE meetings with indexed proceedings (ICASSP, ICRA, IGARSS, ICC, CDC, IECON …)
and about twenty engineering series that deposit proceedings DOIs (CCC, CAC, CCDC, IEOM, ENEGEP,
COBEM, AHFE, ECCE, EuCAP, EAGE, ADIPEC …). Everything those two indexes hold has been checked.
Your job is the rest: the society-press and no-proceedings giants (ASME, ASCE, SAE, TRB, SPE,
ASHRAE, IEEE PES …) and the national engineering societies whose annual meetings run thousands of
presentations but never reach an index.

**Names only.** No abstract counts, no per-conference digging, no verification. You are producing
candidate names for a phase-2 team; a `size_hint` is welcome when a page you already opened states
one, but never spend a search chasing a number.

## Read first

- `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md` — sections
  **"Phase 1 — Discover every candidate name"** and **"Search in the conference's own language"**.
- The three exclusion files in your directory `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/eng/p1/`:
  - `existing_names.json` — every conference already on ANY census or deleted sheet (1,522 rows,
    with sheet and society). Do not return any of these. Match by society and meeting, not by
    exact string. Already covered elsewhere and therefore NOT yours: AIAA forums, MRS/E-MRS, SPIE,
    Optica/CLEO/OFC (physical sciences); AIChE and all chemical engineering (chemistry); BMES and
    biomedical engineering (medicine); the IEEE and Crossref rows on `Census - CS & Engineering`.
  - `dblp_checked.json` — 149 DBLP conference streams with ≥300 papers in 2024 or 2025, all
    already checked (those ≥800 are on the sheet, the rest fell below the bar). Do not return them.
  - `crossref_checked.json` — 708 Crossref proceedings containers with ≥300 papers in 2024 or 2025,
    likewise already checked. Do not return a meeting whose proceedings appear there.

## The bar, and what "large" means here

A conference counts when it has roughly **900 or more accepted contributed presentations** in one
edition — technical papers plus posters, invited talks excluded, exhibitor sessions excluded. Return
only names you judge **plausibly** clear that. Over-include on genuine uncertainty (a national
society annual meeting you cannot size), but do not pad the list with meetings you know run a few
hundred papers. There is no target count: return as many as you are comfortable standing behind.

Attendance is a hint, not the unit: a 10,000-person trade show with 400 technical papers is OUT;
a 3,000-person society meeting with 2,500 presentations is IN. When a page states both, record both.

## Scope

**All of engineering except CS/AI** (a separate agent has CS/AI): mechanical, civil and structural,
electrical and power, electronics and semiconductors, control and automation, robotics, signal
processing, communications, aerospace (non-AIAA), automotive, transportation, petroleum and mining,
energy and HVAC, nuclear, industrial and manufacturing, water and environmental engineering,
geotechnical and earthquake, computational mechanics, acoustics (non-ASA), engineering education,
and the general/national engineering society congresses. Worldwide. **English-language searching**,
per Rupert's scope (a society's own English pages and English federation lists are fine; a
local-language pass is deferred, not waived — say in your report where it is needed).

**IEICE General Conference is yours; IPSJ, JSAI and CCF are the CS agent's.**

## Where the misses are — search these, in order, checkpoint after each

1. `knowledge` — list what you already know before any search.
2. `us_society_flagships` — the big US engineering societies whose proceedings are society-press or
   absent: ASME (IMECE, Turbo Expo, IDETC-CIE, Fluids, PVP), ASCE (Structures, EWRI, Geo-Congress,
   ICTD), SAE (WCX, COMVEC), TRB Annual Meeting, SPE (ATCE, OTC, IPTC, URTeC), ASHRAE, ANS, IISE,
   SME (MineXchange, NAMRC), ACI, AISC/NASCC, ASNT, AWWA ACE, WEFTEC, ASABE, ASEE Annual Conference,
   AIST, TMS (check physical sheet first), AWS, ISA, NACE/AMPP, ACEC — and their attendance and
   paper counts where a page states them.
3. `ieee_unindexed` — IEEE and IEEE-adjacent meetings whose full proceedings are NOT in DBLP or are
   under-indexed: PES General Meeting, ISSCC, IMS/IMWS, IEDM, VLSI Symposia, PVSC, IAS Annual, APEC,
   ISIE, ICEM, INTERMAG, ICPE, T&D, PowerTech, ECOC, OFC (physical sheet — skip), RFIC, DAC (check
   dblp_checked first), and the IEEE regional mega-conferences in India, China, Indonesia, Malaysia
   and the Middle East.
4. `national_societies` — the general engineering societies per country whose annual meetings run
   thousands of talks: Japan (JSME, JSCE, IEEJ, IEICE General Conference, SICE, JSAE, AIJ, JSAP is on
   physical), China (CSEE, CMES, CSAA, CHES, CCES, CSAE, CIE), Korea (KSME, KSCE, KIEE, KSAE, KSAS),
   Germany (VDI, VDE, DGLR), UK (IET, IMechE, ICE, IStructE), France (SIA, SFGP is chemistry),
   Italy, Spain, Netherlands, Nordics, India (INAE, IEI, ISTE, IEEE India sections), Brazil (ABCM and
   ABEPRO are known — look for the others: SBA, SOBRAPO, ABENGE/COBENGE), Mexico, Turkey, Iran,
   Russia, Australia (Engineers Australia), Canada (CSCE, CSME), South Africa, Egypt, Indonesia,
   Vietnam, Thailand, Malaysia, Pakistan. Federation lists (WFEO, FEANI, FEIAP, UPADI, FAEO)
   enumerate members in bulk.
5. `world_congresses` — the international/world congress series per discipline: WCEE (earthquake),
   WCCM / USNCCM / ECCOMAS (computational mechanics), ICSMGE (geotechnical), IABSE, fib, WCTR and
   ITS World Congress (transport), FISITA and EVS (automotive), World Energy Congress, WHEC, EU PVSEC,
   IWA World Water Congress, WCE, CIRP, ICCM (composites), ICOSSAR, IFAC World Congress and ACC
   (control — check dblp_checked first), WCNDT, WFEO congresses, WEC (engineering education), ICPT.
6. `trade_show_technical_programmes` — expos with a real contributed-paper programme, listed flagged
   `BOUNDARY`: OTC, ADIPEC-type events not yet covered (ATCE, IPTC, SPE Offshore Europe, EAGE
   is covered), Hannover Messe, Intersolar/EES, Power-Gen, DistribuTECH, CES (no), PCIM, SEMICON.
7. `gaps` — geography mirrors of every big US body, publication trails (society journal supplements,
   "Proceedings of the X annual meeting" PDFs), predatory-looking series excluded (WASET, OMICS,
   conferenceindex, Magnus Group and lookalikes never count — a real meeting traces to a society,
   a university or a series with past editions).
8. `second_pass` — re-run the sweep that produced the most, looking for what it missed.

Stop a sweep when a pass returns mostly names you already have; **when a sweep adds fewer than ~3
plausible names, it is saturated.**

## What to return per name

```json
{
  "conference": "TRB Annual Meeting",
  "society": "Transportation Research Board (US National Academies)",
  "country_or_region": "US",
  "subfield": "transportation",
  "frequency_note": "annual (January, Washington DC)",
  "why_plausibly_900": "13,000+ attendees and thousands of lectern and poster presentations; papers not deposited as proceedings",
  "size_hint": "over 5,000 presentations (TRB 2025 page)",
  "size_hint_url": "https://...",
  "source_url": "https://trb.org/AnnualMeeting/",
  "sweep": "us_society_flagships",
  "boundary": false,
  "implied": false
}
```

`source_url` is where you saw the name. `size_hint` is only what a page you already opened states,
verbatim, with its URL — a snippet figure from a search result that you did not open is NOT a size
hint; write nothing. If a federation list proves a society exists but you never saw its meeting's
name, list the society as the conference with `"implied": true` — an honest placeholder, never an
invention.

## Budget and output

**~60 web searches, hard cap 80.** Prefer pages that enumerate over pages that describe.

**Output**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/eng/p1/names.json` — a JSON list
of the records above, **rewritten in full after every sweep**, de-duplicated within itself and
against the three exclusion files.

**Progress**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/eng/p1/STATUS.json` —
`{ "sweeps_done": [...], "names": n, "searches_used": n, "in_flight": "<sweep>" }`, rewritten
whenever it changes.

**Report**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/eng/p1/REPORT.md` — written at
the end (see below).

## Do not

- Do not research any conference's size beyond what a page you already opened states.
- Do not write to any spreadsheet or `.xlsx` file; do not modify any file outside your three output
  files; do not read any file under `scratchpad/` other than the ones in your own directory.
- Do not ask anyone to change a permission or config setting. If the search budget runs out, stop
  and say so — your checkpointed file is the result.

## Finish by reporting (REPORT.md and your final message)

Names returned per sweep; searches used; which sweeps saturated; the names you are LEAST sure clear
the bar (so phase 2 can take them last); the countries you could only see through English and the
local-language terms a follow-up should use; and any list page or federation directory that
enumerated many meetings at once.
