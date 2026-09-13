# Chemistry census — PHASE 1 (discovery). Agent brief.

You are building the **widest possible list of chemistry conference NAMES** worldwide.

**Names only.** No abstract counts, no attendance figures, no verification, no per-conference
digging. A name that turns out to be tiny costs one search later; a name never listed is invisible
forever. **Over-include, always.**

## What counts as in scope

Any recurring conference whose subject is chemistry or a chemistry subfield, anywhere in the world,
in any language. Include:

- National and regional chemical society annual meetings (every country you can find)
- Subfield congresses: analytical, organic, inorganic, physical/theoretical, polymer, catalysis,
  electrochemistry, medicinal, green/sustainable, computational, separations, mass spectrometry,
  NMR, surface, colloid, food, agricultural, environmental, forensic, nuclear/radiochemistry
- Chemical engineering meetings (AIChE, ECCE, WCCE and national equivalents)
- Instrument and trade-adjacent meetings where chemists present (Pittcon, ACHEMA, analytica)
- Joint and federated congresses (IUPAC, EuChemS, FACS, FLAQ, Pacifichem)
- Gordon Research Conferences and similar invite-led series — list the SERIES name, not every topic

**Borderline is IN.** Materials, biochemistry, chemical biology, pharmaceutical sciences and
crystallography all sit on the boundary — list them and let phase 2 decide.

## What to return per name

Just enough to identify it later, nothing more:

```json
{
  "conference": "ACS Spring National Meeting & Exposition",
  "society": "American Chemical Society",
  "country_or_region": "US",
  "subfield": "general chemistry",
  "frequency_note": "twice yearly (Spring + Fall)",
  "why_listed": "national meeting of the largest chemical society",
  "source_url": "https://www.acs.org/meetings.html"
}
```

`source_url` is where you saw the name — a society page, a federation member list, a calendar. It
does not need to be authoritative; it needs to let the next person find the meeting.

## How to search — list-shaped queries, not conference-shaped

Discovery queries enumerate; they do not investigate:

- `"largest chemistry conferences by attendance"`
- `"list of chemical society annual meetings"`
- `"<country> chemical society annual congress"`
- `"IUPAC associated organizations"` / `"EuChemS member societies"` — federations publish member
  lists, and each member implies a meeting
- `"<subfield> international congress 2025"` / `"world congress of <subfield> chemistry"`
- society-directory and conference-aggregator pages, which enumerate in bulk

**Run each sweep twice.** The second pass over the same ground catches the odd ones out. Stop an
area when a pass returns mostly names you already have.

## The gaps that get missed most often — check each before you finish

- **Geography**: the US body AND its European/Asian counterpart. Missing the mirror society is the
  single most common gap.
- **SEARCH IN THE SOCIETY'S OWN LANGUAGE — mandatory, not optional.** An English-only search does
  not mean a meeting is absent; it means you did not look. The Chemical Society of Japan publishes
  3,604 presentations and 6,000+ participants on its own news page, in Japanese, and English
  queries return nothing usable. Use the local term: 年会/大会/討論会 (JP), 年会/学术会议 (CN),
  학술발표회 (KR), Jahrestagung/Tagung (DE), congrès (FR), congreso (ES), congresso (PT/IT),
  съезд/конференция (RU), zjazd (PL), kongre (TR). A machine-translated page is fine to read, but
  cite the original URL.
- **Federations**: IUPAC, EuChemS, FACS (Asia), FLAQ (Latin America), FASC (Africa) all publish
  member lists naming dozens of societies.
- **Publication trails**: a journal supplement or proceedings series implies a meeting.
- **Industry**: where the field's instrument vendors exhibit.
- **Adjacent disciplines**: chemical engineering, materials, pharma sciences, crystallography.

## Budget and output

**~40 web searches.** Discovery is cheap per name — one list page can yield thirty. Prefer pages
that enumerate over pages that describe.

Write your results incrementally to the file named in your task prompt as a JSON array,
**rewriting the whole file every 10 names**, so nothing is lost if you stop.

In your final message: how many names you found, which territories saturated (a second pass
returned nothing new), and which you think are still under-explored. That last point matters more
than volume — say plainly where you ran out of road.
