# Field notes — chemistry

Companion to `census-methodology.md`, which stays general. This file holds only what is true of
**chemistry** and would be noise in the general method. Read both before working a chemistry row;
add what you learn here, not there.

Started 2026-09-12 from the phase 1 sweep and a 9-row phase 2 pilot.

## Scope, and where chemistry overlaps other censuses

Chemistry sits between two censuses that already exist, so **de-duplicate before trusting any
total**. These are already counted elsewhere and must not be added again:

| Conference | Already on |
|---|---|
| ACS Spring + Fall (one row) | `Census - Physical Sciences` — abstracts UNKNOWN there; the pilot has now counted them |
| MRS Spring/Fall, E-MRS Spring/Fall | `Census - Physical Sciences` |
| SciX (FACSS) | `Census - Physical Sciences` |
| ECS Meetings (Electrochemical Society) | `Census - Physical Sciences` |
| SOT Annual Meeting | `Census - Medicine & Health` (2,276 abstracts) |
| EUROTOX | `Deleted - Medicine & Health` (counted 1,075) |

Boundary calls to make once and apply consistently: materials chemistry, biochemistry and chemical
biology, pharmaceutical sciences, crystallography, and chemical engineering. The phase 1 sweep
over-included all of them deliberately.

## Where chemistry hides its counts

Chemistry publishes abstract counts more readily than medicine — three of the pilot's first five
rows resolved at rungs 2–3 with a real counted figure and never needed rung 9. But the artefacts
are **not** the ones the medicine ladder looks for:

1. **The society's own magazine.** C&EN's meeting programme PDF carries an itemised breakdown:
   ACS Spring 2025 = 12,723 accepted papers (6,736 in-person oral + 941 digital oral + 5,046
   posters, summing exactly). Look for `cen.acs.org/content/dam/cen/...meeting-program.pdf`.
2. **The president's business-meeting slide deck.** ASMS publishes a five-year table — abstracts
   submitted, orals, posters, attendance, membership — in one PDF presented at the annual meeting.
   One artefact, five years of history, for one search. Worth checking for any society that holds a
   members' business meeting.
3. **Society news pages in the local language.** CSJ's 106th meeting states 3,604 academic-programme
   presentations and 6,000+ participants on its own Japanese news page; English queries return
   nothing usable. See the mandatory local-language rule in the general method.
4. **Publisher deposit / proceedings index for chemical engineering.** `proceedings.aiche.org`
   indexes papers per meeting — the chem-eng equivalent of medicine's Crossref route. Untested but
   the obvious next step for AIChE, whose "6,000 papers" figure is snippet-only so far.
5. **National platforms.** Japan: Confit (`confit.atlas.jp`) hosts programmes and abstract books for
   many societies including JSAC. China: the Chinese Chemical Society meetings index
   (`chemsoc.org.cn/meeting/home/`) enumerates its division congresses. Each is one browser target
   covering a whole national layer.

## Conversion ratio — chemistry runs high

Chemistry converts **far** higher than medicine. The first three counted chemistry rows landed
between roughly 55% and 90%, against medicine's 25% median, which means medicine's anchors would
understate a chemistry row two- to threefold.

Do not maintain a static anchor list here — generate the current one with
`attlib.ratio_rows(sheet='Census - Chemistry')`, and record in each row's Method cell the specific
anchors you actually reasoned from. The no-shortcuts rule in the general method still applies: the
ratio is judged for the conference in front of you, never copied across.

Why the ratio is high: chemistry meetings are built on divisional programmes where nearly every
attendee presents, and the poster hall is the main event. The exceptions are the trade-fair-adjacent
meetings below.

## Field-specific traps

- **Predatory aggregators are worse here than in medicine.** WASET, conferenceseries.com (OMICS),
  conferenceindex.org, Magnus Group, Peers Alley, United Scientific Group and lookalikes dominate
  result pages for every subfield, and they manufacture plausible names ("International Conference
  on Analytical and Bioanalytical Chemistry, Istanbul"). All three phase 1 agents hit them
  independently. **A real meeting traces to a society, a university, or a series with past
  editions.** Nanochemistry is the worst-infested area.
- **ACS is many meetings, not one.** Two national meetings a year plus eight regional meetings
  (MARM, NERM, SERMACS, MWRM, SWRM, NORM, WRM, CERM), each with its own abstract call. Events/yr
  must reflect that.
- **Trade fairs wear conference clothing.** Pittcon, ACHEMA, analytica, JASIS, ARABLAB, K and
  CHINAPLAS all carry technical programmes of very different weight. Judge them on contributed
  science, not on the exhibition.
- **Index-page societies hide dozens of meetings behind one row.** RSEQ (Spain) has 30 specialised
  groups each running a recurring reunión; SCI (Italy) has 11 divisional congresses; the Chinese
  Chemical Society runs division congresses on one index. One fetch of the index yields 20–30 names.
- **Invite-led series.** Gordon Research Conferences (~300 meetings/yr), Keystone Symposia, CECAM
  and Telluride are each currently ONE row standing in for hundreds of small invitation-based
  meetings with no open abstract call. Individually they fail the bar; collectively they would swing
  the headline conference count. **Open question for Rupert: one row or many?**

## Phase 1 state (2026-09-12)

582 unique names merged from four sources: a knowledge-first list, a societies/geography sweep, a
subfields/techniques sweep, and a gap sweep — ~105 searches. A final sweep for index expansion and
Russian/Korean/Portuguese/Central Asian coverage was running when these notes were written.

Known weaknesses to resolve in phase 2:

- **~60 entries are society-implied placeholders** — "Annual meeting of the X Chemical Society",
  where a federation member list proves the society exists but the meeting's real name was never
  confirmed. Honest placeholders, not inventions. Each must resolve to a real name or be dropped.
  Concentrated in small African and FACS member societies and the Baltics/Balkans.
- **Thin coverage**: Central Asia and the Caucasus (a complete blank), India (under-listed for its
  size), Latin America outside the big five, Portugal, Korea, Russia.

## Pilot results

`scratchpad/chem/pilot_results.json` — 9 rows, ~12 searches. Three counted outright (ACS, CSJ,
ASMS), one stated forward figure (Pittcon), five UNKNOWN with a named next step.
