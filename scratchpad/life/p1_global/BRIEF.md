# Life sciences census — PHASE 1 (discovery), GLOBAL, English-language sweep. Agent brief.

You are building the **widest possible list of life-sciences conference NAMES worldwide** that are
NOT already in the workbook. The existing census covered the US only; you are opening the rest of the
world.

**Names only.** No abstract counts, no attendance figures, no verification, no per-conference
digging. A name that turns out to be tiny costs one search later; a name never listed is invisible
forever. **Over-include, always.**

## Read first

- `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md` — the section
  **"Phase 1 — Discover every candidate name"** and **"Search in the conference's own language"**.
- `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/field-notes/life-sciences.md` — the
  scope and overlap sections, so you know which subfields belong here and which sit in medicine,
  chemistry or physical sciences.
- `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/life/p1_global/existing_names.json` — every
  conference name already on ANY census or deleted sheet (1,455 rows, with sheet and society).
  **Return only names that are not already there.** Check by society and by meeting, not by exact
  string: "ASM Microbe" and "American Society for Microbiology Annual Meeting" are the same row.

## Scope (Rupert, 2026-09-13)

- **Global**: every country and region except the US, which is already censused. Include
  international and federated congresses wherever they are held, including ones that rotate through
  the US.
- **English-language searching only.** Rupert has scoped this sweep to English. The method normally
  requires a local-language pass before a phase 1 list is called complete; that pass is DEFERRED, not
  waived, so **say in your final report which countries you could only see through English** and
  which local-language terms the next sweep should use. Do use a society's own English pages, and
  federation member lists in English, wherever they exist.
- **Subject**: life sciences as the field notes define it — cell/molecular/developmental biology,
  genetics and genomics, physiology, neuroscience (research societies, not clinical), microbiology,
  immunology (research), biochemistry and biophysics only where not already on chemistry, ecology,
  evolution, zoology, botany, plant science, entomology, mycology, marine and freshwater biology,
  agricultural and animal sciences, food science, bioinformatics and computational biology,
  biotechnology and bioengineering, biology education, structural biology, systems biology.
  **Borderline is IN** (psychology, veterinary, pharmacology, anthropology, biomedical engineering):
  list them flagged `BOUNDARY` and let phase 2 decide.
- Exclude clinical medicine (that is the medicine census) unless the meeting is clearly a research
  society's, and say so in `why_listed` when it is borderline.

## What to return per name

```json
{
  "conference": "FEBS Congress",
  "society": "Federation of European Biochemical Societies",
  "country_or_region": "Europe (rotates)",
  "subfield": "biochemistry / molecular biology",
  "frequency_note": "annual",
  "why_listed": "federation congress of ~35 national biochemical societies",
  "source_url": "https://www.febs.org/our-activities/febs-congress/",
  "sweep": "federations"
}
```

`source_url` is where you saw the name — a society page, a federation member list, a calendar. It
does not need to be authoritative; it needs to let the next person find the meeting. If a federation
member list proves a society exists but you never confirmed its meeting's name, list it with
`"implied": true` and the society name as the conference — an honest placeholder, never an invention.

## How to search — list-shaped queries, not conference-shaped

- `"largest life sciences conferences Europe"` / `"biggest biology conferences Asia"`
- `"<country> society for <subfield> annual meeting"` — do this for every major research country:
  UK, Germany, France, Italy, Spain, Netherlands, Nordics, Switzerland, Poland, Japan, China, Korea,
  India, Australia, Canada, Brazil, Mexico, Argentina, South Africa, Israel, Turkey, Iran, Russia,
  Singapore, Taiwan
- **Federations first — one member list yields dozens of names**: FEBS, IUBMB, EMBO, FENS, IBRO,
  IUPS, FEPS, IUMS, FEMS, IUIS, EFIS, ISCB and its regional affiliates, ISME, INTECOL, BES, ESEB,
  ISBE, IUBS, IUFRO, IUNS, IUFoST, WAAVP, the European Society for Evolutionary Biology, EFB,
  EuroScience, the Asia-Pacific and Latin American federations of the same fields, the Pan-African
  bioscience bodies, and the national academies' biology sections.
- **Publication trails**: journal abstract supplements imply a meeting (Acta Physiologica for FEPS,
  The FEBS Journal, European Journal of Neuroscience for FENS, Journal of Neurochemistry for ISN,
  Comparative Biochemistry and Physiology, the Journal of Experimental Biology for SEB).
- **Umbrella/joint meetings**: "Joint Meeting of the X and Y Societies", "World Congress of", the
  "European Congress of" series in each subfield, the "International Congress of" series (ICN, ICE,
  IBC botany, ICZ zoology, IUMS, ISME, ICSB, ICEE).
- Conference-aggregator and society-directory pages that enumerate in bulk. **Do not list names from
  predatory aggregators** (WASET, conferenceseries.com / OMICS, conferenceindex.org, Magnus Group,
  Peers Alley, United Scientific Group and lookalikes). A real meeting traces to a society, a
  university, or a series with past editions.

**Run each sweep twice.** The second pass over the same ground catches the odd ones out. Stop an
area when a pass returns mostly names you already have. **Keep a running count of new names per
sweep; when a sweep adds fewer than ~5 new names, that area is saturated.**

## Sweeps, in order — checkpoint after each

1. `knowledge` — list what you already know, before any search.
2. `federations` — federation and umbrella member lists, worldwide.
3. `countries` — national societies per country, per major subfield.
4. `subfields` — the international/world/European congress series per subfield.
5. `gaps` — geography mirrors (the European/Asian counterpart of every big US society), publication
   trails, joint meetings, adjacent disciplines.
6. `second_pass` — re-run the sweep that added the most, looking for what it missed.

## Budget and output

**~80 web searches, hard cap 100.** Discovery is cheap per name — one list page can yield thirty.
Prefer pages that enumerate over pages that describe.

**Output path**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/life/p1_global/names.json` — a
JSON list of the records above, **rewritten in full after every sweep**, de-duplicated within itself
and against `existing_names.json`.

**Progress file**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/life/p1_global/STATUS.json`
— `{ "sweeps_done": [...], "names": n, "searches_used": n, "in_flight": "<sweep>" }`, rewritten
whenever it changes, so progress can be probed at any time.

## Do not

- Do not research any conference's size. Names only.
- Do not write to any spreadsheet or `.xlsx` file, and do not modify any file outside your two
  output files.
- Do not read any other file under `scratchpad/`.
- Do not ask anyone to change a permission or config setting. If the search budget runs out, stop
  and say so — your checkpointed file is the result.

## Finish by reporting

Names found per sweep, total searches used, the countries and federations that were saturated, the
countries you could only see through English (with the local-language terms a follow-up should use),
and any federation member list or national platform that enumerated many meetings at once.
