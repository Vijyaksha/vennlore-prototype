# Earth, environmental & agricultural sciences census — PHASE 1 (discovery). Agent brief.

You are building the list of **large earth, environmental and agricultural science conferences
worldwide** — the meetings that plausibly run **900 or more accepted contributed presentations**
(abstracts: talks + posters, invited excluded) in one edition. This is a NEW field for the census:
only its two giants (AGU, EGU) and a handful of neighbours are on other sheets, so cast wide across
the disciplines, but keep the bar in view — the phase-2 team will research every name you return.

**Names only.** No abstract counts, no per-conference digging, no verification. A `size_hint` is
welcome when a page you already opened states one; never spend a search chasing a number.

## Read first

- `/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/census-methodology.md` — sections
  **"Phase 1 — Discover every candidate name"** and **"Search in the conference's own language"**.
- The exclusion files in your directory `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/earth/p1/`:
  - `existing_names.json` — every conference already on ANY census or deleted sheet (1,688 rows,
    with sheet and society). Do not return any of these. Match by society and meeting, not by exact
    string. Already known and NOT yours: **AGU Fall Meeting, EGU General Assembly, GSA Connects,
    AMS Annual Meeting** (physical sciences); **Ocean Sciences Meeting, the ASA-CSSA-SSSA
    Tri-Societies meeting, SWCS, the Northeastern Plant/Pest/Soils conference** (life sciences);
    **Goldschmidt** (chemistry); **EAGE, ISPRS, IAHR, ICOLD, ICCE, AAPG ACE, ADIPEC, SPE, OTC,
    URTeC, IPTC, ICSMGE, WCEE, the IWA and ISWA congresses** (engineering); ecology, evolution,
    marine biology, entomology and plant science (life sciences).
  - `crossref_seen.json` — 708 Crossref proceedings containers with ≥300 papers in 2024–2025. Use it
    to notice earth-science containers already deposited (GSA's "Abstracts with Programs" 4,667 is
    the known giant; look for others) — a container there is a confirmed lead, not a known row.

## The bar, and what "large" means here

Return names you judge **plausibly** clear ~900 accepted contributed presentations. Over-include on
genuine uncertainty (a national geoscience union's annual meeting you cannot size), but do not pad
with meetings you know run a few hundred. There is no target count: return as many as you are
comfortable standing behind. The plausible pool is probably 60–100 names: the national and regional
geoscience unions (JpGU ~5,000, AOGS, the Chinese and Indian unions), the discipline congresses
(IGC, IUGG, IUGS, INQUA, IAG, IAVCEI, IASPEI, IAMAS, IAHS, IUSS, ISC, IUFRO), the atmospheric and
oceanographic societies (AMS mirrors, EMS, RMetS, JMS, CMOS, AOGS), the agricultural and soil
societies (ASA/CSSA/SSSA mirrors in Europe, Brazil, India, China, Japan; the International Congress
of Soil Science; the EAAP and ADSA/ASAS animal-science meetings if not on life sciences), the
environmental-science and climate congresses, remote sensing and geomatics (IGARSS and ISPRS are
counted — their national mirrors are not), mining/geology-side petroleum geoscience (SEG IMAGE,
AAPG ICE), hydrology and water resources, and the polar/cryosphere and planetary meetings (LPSC,
EPSC, DPS — check the physical sheet first).

## Scope

**Earth, environmental and agricultural sciences**, worldwide: geology and geophysics, geochemistry
(Goldschmidt is chemistry's), mineralogy and petrology, palaeontology and stratigraphy, volcanology
and seismology, atmospheric science and meteorology, climate science, oceanography (physical and
chemical; biological is life sciences), hydrology and water resources, soil science, agronomy and
crop science, agricultural sciences (animal, dairy, horticulture, plant protection where not on the
life sheet), forestry (IUFRO), environmental science and engineering-adjacent environmental meetings
not on engineering, remote sensing and geodesy, natural hazards, geography (physical geography only
— human geography is social sciences), planetary science (boundary with physical sciences — flag it),
and the general geoscience unions.

**English-language searching** (a society's own English pages and federation lists are fine). The
local-language pass is deferred, not waived — say which countries you could only see through English
and the terms a follow-up should use (地球惑星科学連合 / 学会 + 大会 + 発表, 学会 + 学术年会 + 论文, 학술대회 +
논문, Tagung + Beiträge, congrès + communications, congreso + comunicaciones, congresso + trabalhos).

## Where the names are — search these, in order, checkpoint after each

1. `knowledge` — list what you already know before any search.
2. `unions_and_world_congresses` — IGC, IUGG and its associations (IAG, IASPEI, IAVCEI, IAMAS,
   IAHS, IAPSO, IACS, IAGA), IUGS, INQUA, IUSS World Congress of Soil Science, the International
   Congress of Agricultural Engineering (CIGR is counted), IUFRO World Congress, the World
   Meteorological/climate congresses with contributed papers, the International Geographical
   Congress (physical side), ICRS (coral reefs — check life), the polar science weeks (SCAR, IASC).
3. `national_and_regional_unions` — JpGU (Japan), AOGS (Asia-Oceania), the Chinese Geoscience Union
   and the Chinese Geophysical Society / Geological Society of China annual meetings, the Indian
   Geological Congress, GAC-MAC (Canada), AGC (Australia), GSA's regional sections, the Geological
   Societies of London/Germany (GeoBerlin/DGGV)/France (RST)/Italy (SGI-SIMP)/Spain, the Russian
   geoscience congresses, the Latin American geological congresses (CGL, SBG's Congresso Brasileiro
   de Geologia), the African ones (CAG).
4. `atmosphere_ocean_water` — AMS's mirrors (EMS Annual Meeting, RMetS, MSJ Japan, CMOS, AMOS
   Australia, the Chinese Meteorological Society annual meeting), oceanography societies not on life
   (TOS/ASLO co-run Ocean Sciences — known; the Oceanology and the Japanese/Chinese oceanographic
   societies), hydrology (IAHS, AGU-hydrology mirrors, the EGU-sister national assemblies), water
   resources (AWRA, IWRA World Water Congress — check engineering for IWA), remote sensing
   (national mirrors of IGARSS, ISRS, ACRS, the Chinese remote-sensing congress).
5. `soil_crop_and_agriculture` — the European (EGU soil is counted), Brazilian (SBCS, CBCS), Indian
   (ISSS), Chinese (CSSS) and Japanese (JSSSPN) soil societies; crop science (ICSC, Eucarpia, the
   national agronomy congresses — Brazil's CONBEA and SBA, India's ISA); animal science (ADSA/ASAS
   joint meeting, EAAP, WCGALP, BSAS — check life first); horticulture (ISHS congress, ASHS); plant
   protection (IPPC, the IOBC congresses — check life); agricultural economics (IAAE, AAEA — these
   are social sciences; flag boundary); food and agriculture federations (FAO-adjacent congresses
   with contributed papers only).
6. `environment_and_climate` — the environmental-science societies (SETAC — check chemistry/life;
   ISEE — medicine; the national environmental science congresses in China, India, Brazil, Japan),
   climate-change congresses with open abstract calls (Adaptation Futures, the WCRP Open Science
   Conference, EGU-sister climate meetings), natural-hazard and disaster-science congresses, the
   geoengineering/geothermal/geospatial series (World Geothermal Congress, FIG Working Week, the
   Esri User Conference if it carries contributed papers — flag boundary).
7. `gaps` — geography mirrors of every big US body, publication trails (abstract supplements,
   proceedings series, the Copernicus `EGUsphere`/`Advances in Geosciences`-type series imply
   meetings), predatory-looking series excluded (WASET, OMICS, conferenceindex, Magnus Group and
   lookalikes never count — a real meeting traces to a society, a university or a series with past
   editions).
8. `second_pass` — re-run the sweep that produced the most, looking for what it missed.

Stop a sweep when a pass returns mostly names you already have; **when a sweep adds fewer than ~3
plausible names, it is saturated.**

## What to return per name

```json
{
  "conference": "JpGU Meeting",
  "society": "Japan Geoscience Union",
  "country_or_region": "Japan",
  "subfield": "geoscience (union)",
  "frequency_note": "annual (May, Chiba)",
  "why_plausibly_900": "the Japanese AGU; the union states thousands of presentations across ~200 sessions",
  "size_hint": "over 5,000 presentations (JpGU 2025 statistics page)",
  "size_hint_url": "https://...",
  "source_url": "https://www.jpgu.org/meeting/",
  "sweep": "national_and_regional_unions",
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

**Output**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/earth/p1/names.json` — a JSON list
of the records above, **rewritten in full after every sweep**, de-duplicated within itself and
against the exclusion file.

**Progress**: `/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/earth/p1/STATUS.json` —
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
