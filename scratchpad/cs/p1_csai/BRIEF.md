# CS & AI census — PHASE 1 (discovery), second pass. Agent brief.

You are finding the **large computer-science and AI conferences that the first pass missed**.
The first pass (2026-09-13) counted every conference stream in DBLP and every proceedings container
in Crossref; everything those two indexes hold has already been checked. Your job is the rest:
meetings that are big but whose papers are NOT indexed as conference proceedings.

**Names only.** No abstract counts, no per-conference digging, no verification. You are producing
candidate names for a phase-2 team; a `size_hint` is welcome when a page you already opened states
one, but never spend a search chasing a number.

## Read first

- `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md` — sections
  **"Phase 1 — Discover every candidate name"** and **"Search in the conference's own language"**.
- The three exclusion files in your directory `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/cs/p1_csai/`:
  - `existing_names.json` — every conference already on ANY census or deleted sheet (1,522 rows,
    with sheet and society). Do not return any of these. Match by society and meeting, not by
    exact string: "ACM MM" and "ACM International Conference on Multimedia" are the same row.
  - `dblp_checked.json` — 149 DBLP conference streams with ≥300 papers in 2024 or 2025. Every one
    was checked: those ≥800 are on the sheet, the rest fell below the bar. Do not return any of them.
  - `crossref_checked.json` — 708 Crossref proceedings containers with ≥300 papers in 2024 or 2025,
    likewise already checked. Do not return a meeting whose proceedings appear there.

## The bar, and what "large" means here

A conference counts when it has roughly **900 or more accepted contributed presentations** in one
edition — main-track papers plus posters, workshops excluded, invited talks excluded. Return only
names you judge **plausibly** clear that. Over-include on genuine uncertainty (a national society
meeting you cannot size), but do not pad the list with meetings you know run a few hundred papers.
There is no target count: return as many as you are comfortable standing behind. Twenty solid names
beat sixty weak ones.

## Scope

**CS and AI** worldwide: machine learning, NLP, vision, HCI, data mining, databases, systems,
networking, security, software engineering, programming languages, theory, graphics, computational
biology (CS side), speech, multimedia, information retrieval, web, computer science education, and
the general/national computer-science congresses. **English-language searching**, per Rupert's scope
(a society's own English pages and English federation lists are fine; a local-language pass is
deferred, not waived — say in your report where it is needed).

**Not yours** (the engineering agent has them): robotics, signal processing, communications,
circuits, control, power, electronics, and every other IEEE engineering society meeting. IEICE
General Conference is theirs; **IPSJ, JSAI and the CCF congresses are yours.**

## Where the misses are — search these, in order, checkpoint after each

1. `knowledge` — list what you already know before any search.
2. `journal_first` — venues whose papers are indexed as a JOURNAL, so they are invisible to a
   proceedings count: PVLDB (VLDB), PACMPL (OOPSLA/POPL/ICFP/PLDI), PACMHCI (CSCW), PACM IMWUT
   (UbiComp), PACMMOD (SIGMOD), PACMNET, ACM TOG (SIGGRAPH / SIGGRAPH Asia), the ACL Anthology
   "Findings" series if it is the main venue for a meeting. Check the size of the underlying meeting,
   not the journal.
3. `national_congresses` — the general computer-science / informatics society meetings per country:
   CCF's CNCC and its subfield congresses (China), IPSJ National Convention and JSAI Annual Conference
   (Japan), KIISE Korea Computer Congress and KSC (Korea), CSI (India), GI INFORMATIK (Germany), BCS,
   SBC's CSBC (Brazil), CLEI (Latin America), ACS (Australia), the Russian, Turkish, Iranian, Polish,
   Spanish and Italian national CS societies, and the African and Middle-Eastern equivalents. Federation
   member lists (IFIP, CEPIS, SEARCC) enumerate these in bulk.
4. `openreview_and_new_ai` — AI venues that publish only on OpenReview or their own site and so
   sit outside DBLP's proceedings model: COLM, RLC, AutoML, MLSys, CoRL, ML4H, the large regional
   AI congresses (PRICAI, ECAI, ACML, AIAI, CICAI, PRCV, CCL, NLPCC), and industry-academic AI
   summits that accept contributed papers.
5. `mega_multi_track` — meetings that are one brand but many co-located conferences, where the
   umbrella total could clear the bar even if no single track is in DBLP: WCCI, SSCI, IEEE CS
   umbrella weeks, SC/ISC (supercomputing), COMPSAC, ICSE co-located week, FSE/ASE, ETAPS, FLoC,
   Computing Research weeks, the World Computer Congress.
6. `education_and_industry` — SIGCSE TS, ITiCSE, ICER, CSEDU, and the industry conferences with a
   real contributed-paper track (GTC, KubeCon/CNCF, Strata, ODSC) — list flagged `BOUNDARY`.
7. `gaps` — geography mirrors of every big US body, publication trails (journal supplements that
   imply a meeting), predatory-looking series excluded (WASET, OMICS, conferenceindex, Magnus Group
   and lookalikes never count — a real meeting traces to a society, a university or a series with
   past editions).
8. `second_pass` — re-run the sweep that produced the most, looking for what it missed.

Stop a sweep when a pass returns mostly names you already have; **when a sweep adds fewer than ~3
plausible names, it is saturated.**

## What to return per name

```json
{
  "conference": "China National Computer Congress (CNCC)",
  "society": "China Computer Federation (CCF)",
  "country_or_region": "CN",
  "subfield": "general CS",
  "frequency_note": "annual",
  "why_plausibly_900": "CCF's flagship; 10,000+ attendees across 100+ forums in 2024",
  "size_hint": "10,000+ attendees, 130 forums (society news page)",
  "size_hint_url": "https://...",
  "source_url": "https://www.ccf.org.cn/...",
  "sweep": "national_congresses",
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

**Output**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/cs/p1_csai/names.json` — a JSON
list of the records above, **rewritten in full after every sweep**, de-duplicated within itself and
against the three exclusion files.

**Progress**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/cs/p1_csai/STATUS.json` —
`{ "sweeps_done": [...], "names": n, "searches_used": n, "in_flight": "<sweep>" }`, rewritten
whenever it changes.

**Report**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/cs/p1_csai/REPORT.md` — written
at the end (see below).

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
