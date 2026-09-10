# Handoff — TAM/SAM/SOM conference census

Last updated: 2026-09-10 (session 3). Everything lives in `docs/business/`. The workbook is the
source of truth; nothing depends on session scratch files.

## Start here

1. Read `census-methodology.md` — the reusable method, and it is **self-sufficient**: the bar, the
   six rules, both phases, the 9-rung ladder, the parallel-agent protocol, de-duplication, and every
   trap hit so far. You do not need any prior conversation to run it.
2. Open `tam-sam-som-v3.xlsx` — all data and all model numbers.
3. **Next action: medicine & health.** It needs both passes run under the current rules — Phase 1
   to close its candidate list, then Phase 2 over the census sheet and then the deleted sheet.
   227 of 313 candidates are still `NOT YET CENSUSED`, and *none* of the sheet has been re-verified
   under the ~700 floor or the `Method` column.

**Physical sciences is complete and fully re-verified (2026-09-10)** — 55 census rows, 101 deleted
rows, all 101 carrying a `Method` entry and 81 carrying a counted number (up from 16). No
duplicates in either direction. Six rows are queued for rung 5 (browser) and two are genuinely
unreachable: Belarus (host resolves but times out on every protocol, so a browser will not help)
and Russia (a Phase-1 gap — the row names no conference, so the ladder has no query to form).

**What the 2026-09-10 run established, in one line:** searching finds the countable artefact,
counting produces the number. Roughly 63 searches across five agents produced ~65 new figures, and
essentially every one came from counting a PDF, programme, archive or API — rung 1 yielded almost
nothing.

## Locked decisions (don't relitigate)

| Decision | Value |
|---|---|
| Size bar | **≥1,500 = VERIFIED**; **retention floor ~700** (lowered from 1,500 → 800 → 700). Not attendance |
| Price | **$5,000 per conference**, for TAM, SAM and SOM alike |
| Capture rate | **100%** (no haircut, per Rupert) |
| Borderline cases | **Included** — the model is generous by design; verified-only shown as a subtotal |
| SAM | Exactly two: **Global** and **US only**. Physical sciences only |
| SOM | AIP member societies + SPIE + affiliates AGU, BPS, AIAA, GSA |
| TAM | Large conferences (≥1,500 abstracts) across **all fields**, by field-by-field census |

---

## Workbook sheets

| Sheet | Contents |
|---|---|
| `Census - Physical Sciences` | **Complete.** 48 live rows (VERIFIED + BORDERLINE). 41.66 events/yr clear the bar |
| `Deleted - Physical Sciences` | 110 ruled-out rows with evidence. **Still counted in SAM/SOM** — totals span both sheets |
| `Census - Medicine & Health` | **Phase 1 complete, Phase 2 46% done.** 48 VERIFIED, 84 BORDERLINE, 176 NOT YET CENSUSED. Counters rows 29–37 |
| `Deleted - Medicine & Health` | 5 ruled out on positive evidence: ADLM, STS, MedInfo, SVS VAM, ACMG |
| `Summary` | The four tiers; assumption cells in yellow |
| `TAM large-conf estimate` | Methods A (~220), B (320), C (direct census — the one that eventually replaces the estimate) |
| `Notes & methodology` | Provenance, citation classes, open items |
| `APS GPS budget (v1)` | Reconstructed APS Global Physics Summit budget (~$9.8M rev / $8.5M exp) |
| `Per-conference economics` | Event-tech spend at 3–4% of conference cost — source of the $8–12M figure |

### How the deleted lists work — read before moving any row
A ruled-out candidate is **cut across** to `Deleted - <Field>` with its evidence intact, plus
`Deleted on` and `Why deleted`. So `NOT YET CENSUSED` always means "genuinely still to do", and no
later session re-researches a dead candidate.

**Deletion is model-neutral by construction, and must stay that way.** `Tier` and `Include` are
independent: a physical-sciences meeting can fail the bar (`Tier = OUT`) and still belong to the SAM
universe (`Include = 1`) — 110 such rows carry ~73 of SAM Global's events/yr. Every SAM/SOM total is
therefore `SUMPRODUCT(<census range>) + SUMPRODUCT(<deleted range>)`, on `Summary` B12–B14 and on the
census sheet's own totals rows.

**Order of operations when adding a field or moving rows: wire the totals across both sheets first,
move rows second, verify the numbers are unchanged third.**

---

## Census progress by field

| Field | State |
|---|---|
| Physical sciences | **Complete** (deleted list still needs the audit — item 4 above) |
| Medicine & health | Phase 1 complete (313 candidates, 3 sweeps). **Phase 2: 137 of 313 (46%)** — all P1 done |
| CS / AI / engineering | Not started. The selective-paper world (NeurIPS: 21,575 submissions) |
| Life sciences | Not started |
| Chemistry | Not started — ACS placeholder, `Include = 0`, awaiting decision 3 |
| Social sciences | Not started |

---

## What sessions 2–3 established about method

**The escalation ladder replaced "search once and give up".** Rule 1 was being read as a licence to
rule things out; it now says explicitly that not looking is fine, but looking once and finding
nothing is not evidence. **`OUT` requires positive evidence** — a count below the bar, or a programme
that isn't contributed-abstract at all. The justification is on the sheet: of 110 deleted
physical-sciences rows, only 19 carry a number below the bar; **91 were ruled out on `UNKNOWN`
alone**, and nothing distinguishes "checked and small" from "looked once and found nothing".

**Rung 2 is the rung that was missing.** Societies write "how many abstracts" in blog posts and press
releases; almost none use the phrase "abstracts submitted". Rewording generically — or in the
society's own language — is one search and it works.

**Rungs 3–6 cost nothing.** Count the supplement, the archive, the JS programme, the poster boards.
At roughly 1 usable number per 4 searches at rung 1, counting is usually the better first move for
any conference that publishes an abstract book.

**Proven dead ends — do not retry.** **Crossref** (congress abstracts get no DOIs) and **PubMed**
(doesn't index individual abstracts). Both tested; both return ordinary article counts in the dozens.

**Bot-blocked sources, all marked CLICK TO CONFIRM in-sheet:** astro.org (402), journals.lww.com
(402), professional.heart.org (403), era-online.org (403), toxicology.org (TLS failure), asbmr.org
(403), aasld.org (403), iadr.abstractarchives.com (login).

---

## Watch list — likely to fail the bar, get evidence then delete

ACEP (400+ selected), Greater New York Dental Meeting and Chicago Midwinter (trade/CE-led with a
student poster session), SAEM, AAPM&R and ASCPT (small supplements by page-range arithmetic),
AAFP FMX, DIA. Each carries its reasoning and next rung in Notes.

## Known duplicates and double-counts

- **Iran PSI** and **Israel IPS** — each listed twice with `Include=1` (decision 1 above)
- **M&M**, **TPS Annual Meeting**, **ANS** — duplicated but harmless (one copy has `Include=0`)
- **AAPM** appears on both census sheets (AIP member society *and* medical physics) — count once
- **ASMBS** runs inside **ObesityWeek** — check before counting both

## Known unresolved figures — physical sciences

All hand-checkable, none blocking: CPS Fall Meeting, KPS Spring/Fall, Taiwan TPS (no published
abstract counts); SPIE Defense + Commercial Sensing (bot-blocked proceedings sum — the one SPIE
flagship that could still pass); DPG SMuK / SAMOP exact tallies (countable at dpg-verhandlungen.de);
DAE India (AIP proceedings paywall).
