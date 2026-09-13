# Field notes — life sciences (US)

Companion to `census-methodology.md`, which stays general. This file holds only what is true of
**life sciences** and would be noise in the general method. Read both before working a life-sciences
row; add what you learn here, not there.

Started 2026-09-12 from the US-only phase 1 sweep and a 20-row inline phase 2 pilot
(`scratchpad/life/pilot/RESULTS.json`, 18 searches).

## Scope, and where life sciences overlaps other censuses

**US only for now** (Rupert, 2026-09-12). The local-language sweep is therefore not required, but the
Method text must still name the language searched.

Life sciences sits between medicine and chemistry, and many of its biggest meetings were enumerated
there first. **36 phase-1 names are parked on `Deleted - Life Sciences` as already counted elsewhere
or held inside another meeting** — never research or total them again here:

| Already on | Meetings |
|---|---|
| `Census - Medicine & Health` | SfN, ASM Microbe, ASHG, AAI IMMUNOLOGY, ISSCR, NUTRITION (ASN), ENDO, ARVO, ASGCT, BMES, ASBMR, ARO MidWinter, GSA (gerontology), DIA, BIO, ASV (virology), Society For Biomaterials |
| `Deleted - Medicine & Health` | ACVIM Forum, AVMA Convention |
| `Census - Chemistry` / `Deleted - Chemistry` | ASBMB, Biophysical Society, Protein Society, Keystone, IFT FIRST, Controlled Release Society, SOT, AAPS PharmSci 360 |
| `Census - Physical Sciences` / `Deleted` | ESA (Ecological Society), AAAS, ASGSR |
| Inside another life-sciences row | ASN + SSB → Evolution Meeting; Herpetologists' League + SSAR → JMIH; ASPT + American Fern Society → Botany Conference |

**Acronym collisions — check the society, not the letters.** `ESA` is both the Ecological Society
(physical-sciences sheet) and the Entomological Society (this sheet). `APS` is the American
Physiological Society, the American Phytopathological Society (Plant Health), the Association for
Psychological Science and the American Physical Society. `ASA` here is agronomy (CANVAS); elsewhere it
is anesthesiology or acoustics. `CNS` here is Cognitive Neuroscience; on medicine it is the Congress of
Neurological Surgeons. `ASP` is parasitologists, pharmacognosy, primatologists — and astronomers on
physical sciences.

**Joint years double-count.** ASLO co-sponsors the Ocean Sciences Meeting and sometimes meets with the
Society for Freshwater Science; the Society of Nematologists has in some years met jointly with the
plant pathologists (unverified — check per year); TAGC absorbs
the Drosophila, C. elegans, yeast and zebrafish meetings in its years. Count a joint year once.

**Boundary rows** kept per over-include, flagged `BOUNDARY` in the subfield column: APA and APS
(psychology — probably social sciences), WVC (veterinary CE — likely `CURATED`), DIA, SACNAS (all-STEM).

## Where life sciences hides its counts

Life sciences behaves like **medicine, not chemistry**: societies publish abstracts in journals, so
the Crossref deposit index is again the highest-yield route. But the journals split three ways, and
the society platforms are more varied. Ranked by what they settled in the pilot:

1. **Per-abstract Crossref deposits in a society journal — exact, zero searches.** Cursor-page the
   journal-year and group by `(volume, issue)`; the meeting issue stands out by an order of magnitude.
   **Do not assume `S` pages — most of these carry no supplement pagination at all.**

   | Meeting | Journal (ISSN) | How the abstracts are deposited |
   |---|---|---|
   | American Physiology Summit | *Physiology* (1548-9213) | issue `S1`, **no page field**; 2025 = 1,816, 2024 = 1,893 |
   | ASPET | *JPET* (0022-3565) | 2024: vol 389 with **issue blank**, page = abstract number (1–570). 2025 moved to Elsevier and mixes into regular issue 3 — not separable |
   | VSS | *Journal of Vision* (1534-7362) | one issue per year (2025 = 25(9) 1,117; 2024 = 24(10) 1,178), page = abstract number |
   | ASAS | *Journal of Animal Science* (0021-8812) | **three supplements a year** — two section meetings + the national meeting. Identify the national one by a deposited publisher note (2024 = Supplement_3, 922) |

2. **Confex whole-meeting endpoint** — `<host>.confex.com/<org>/<code>/meetingapi.cgi/Paper`. Gives
   `MGroupType`, `ProgramCode`, **`Invited`** and **`Withdrawn`** per paper, so the contributed split is
   exact. CANVAS: `scisoc.confex.com/scisoc/2025am` → 2,876 contributed after removing 250 invited and
   147 withdrawn. PAG: `pag.confex.com/pag/33`. **AGU restricts it**: `agu/OSM24` returns a 31-paper
   sample, not the meeting — not a count.
3. **Society WordPress sites.** Two distinct wins:
   - **Media index** `/wp-json/wp/v2/media?search=book|program|abstract` exposes abstract books hidden
     behind download plugins — GSA (Drosophila 2025), Cognitive Neuroscience Society (2024 books).
   - **Custom abstract post types.** SICB exposes `/wp-json/wp/v2/abstract_years` (per-year counts
     2001–2021) and `/wp/v2/abstract?abstract_years=<id>` with session codes in the excerpt (`S` symposium,
     `P` poster, numeric = contributed talk). Check `/wp-json/` routes on every society site.
4. **Journal supplement PDFs behind Cloudflare, counted in the browser.** MBoC (ASCB) is one DOI with an
   oral PDF and a poster PDF; `curl` gets 403, but in Chrome a same-origin `fetch` of
   `/doi/suppl/<doi>/suppl_file/<name>.pdf` plus pdf.js (from cdnjs) extracts the text in-page. Run the
   extraction as a background job and poll — a 1,393-page PDF exceeds the 45-second evaluate limit.
5. **Programme platforms in the browser.** eventScribe (Entomology 2025) 403s to `curl` but its
   Browse-by-Title page loads in Chrome with per-item type icons (Oral / Poster / Student Competition).
6. **Poster-number arithmetic** when the supplement is lumped: APS Plant Health's poster archive file
   names carry the poster number (`<id>-P-702.pdf`).
7. **Organiser / third-party recaps** — only when nothing is countable, and labelled `REPORTED BY SOURCE`.
   ASPB has no supplement and no API, but a lab's meeting recap gave an itemised breakdown that summed
   exactly (727 = 439 poster + 235 independent + 25 community + 20 workshop + 8 plenary).

**Lumped single-DOI supplements (triage only, not countable per item):** Wiley (AAA → *Developmental
Dynamics* + *Anatomical Sciences Education*), OUP *Integrative and Comparative Biology* (SICB 2025,
S1–S590), APS *Phytopathology* (Plant Health 2025, S2.1–S2.209).

## Counting rules this field needs

- **Invited talks hide in "sessions", not labels.** Plenaries are usually numbered in the programme
  book and easy to exclude (Drosophila: IDs 2–9 and 177–181), but platform sessions often open with an
  unlabelled invited slot. Record the range (Drosophila 890–911), don't pretend to precision.
- **Workshop-heavy meetings: posters are the only clean contributed track.** PAG has 1,243 workshop
  talks chosen by community organisers and a blank `Invited` field; the counted floor is its 880
  posters. Entomology's 1,599 non-student orals mix invited symposia with contributed 10-minute papers.
  Both stay `BORDERLINE` with a floor rather than guessing the split.
- **Symposium-titled topics mark invited abstracts in a flat book.** Botany's book has a `Topic:` line
  per abstract; long, colon-bearing topic names are symposia/colloquia (77 abstracts) — standard
  sections are short names.
- **`pdftotext -layout` vs `-raw` is not symmetric.** CNS: `-layout` was right (946 in two independent
  documents), `-raw` undercounted. Botany: `-raw` was right (IDs on their own line), `-layout` broke
  them. Always run both and prefer the mode that agrees with an independent marker (`Author:` lines, a
  second document).
- **Organiser headlines can undercount the book.** Botany said "over 750 contributions including
  symposia"; the final book holds 924. Count the artefact, record the stated figure as a disagreement.

## Access map

| Blocked | What it does | Workaround |
|---|---|---|
| molbiolcell.org, journals.physiology.org, sciencedirect, apsnet.org | Cloudflare 403 to `curl` | Chrome loads them; read or `fetch` same-origin |
| jov.arvojournals.org, academic.oup.com | **bot-verification interstitial even in Chrome** | do NOT bypass — use Crossref metadata or the society site |
| agu.org, agu.confex.com app | Chrome not permitted to read | Wayback `web/<ts>id_/` capture of the agu.org page |
| entomology2025.eventscribe.net | 403 to `curl` | Chrome |
| afs.confex.com, esa.confex.com | no longer resolve / 404 — societies moved platforms | find the new platform from the society page |

## The conversion ratio

Rung 9 was needed for only **2 of 20** rows (Ocean Sciences Meeting, SACNAS) — like chemistry, plan
waves around artefacts, not attendance. Generate anchors with
`attlib.ratio_rows(sheet='Census - Life Sciences')`; the pilot's observed pairs (counted figure with a
loaded attendance figure) are:

- Botany 2025: 847 contributed / 1,062 participants ≈ **80%**
- Entomology 2025: ≥1,226 contributed (floor) / 3,100 attendees ≥ **40%**

Stated breakdowns (ASPB 699 / 984 ≈ 71%; ABRCMS ~2,300 presenters / 4,000 attendees ≈ 58%) are
context only — `REPORTED BY SOURCE`, never anchors. Research-society meetings in this field run high,
like chemistry; student and diversity conferences sit in the middle because mentors, recruiters and
exhibitors inflate the headcount.

## Pilot results — 20 rows, 18 searches (2026-09-12, inline)

| Outcome | Rows |
|---|---|
| `VERIFIED` (counted ≥1,500) | 4 — CANVAS **2,876**, ASCB Cell Bio **2,084** (posters, floor), American Physiology Summit **1,816**, SICB **1,687** (dated 2020) |
| `BORDERLINE`, counted | 7 — Entomology 1,226 (floor), VSS 1,117, CNS 946, ASAS 922, Drosophila ~890–911, PAG 880 (posters, floor), Botany ~847 |
| `BORDERLINE`, counted floor under 800 but no evidence of small | 1 — Plant Health 702 (poster numbering; talks uncounted) |
| `BORDERLINE`, not counted | 3 — Ocean Sciences Meeting ~4,800 inferred, ABRCMS ~2,300 stated, SACNAS ~900 inferred |
| `OUT` on positive evidence | 3 — ASPET 504, AAA ~500+ stated, ASPB ~699 stated |
| `UNRESOLVED` (stays `BORDERLINE`) | 2 — American Fisheries Society, The Wildlife Society |

**Highest-value next actions:** the Entomology session-type split (could lift it past 1,500); the
PAG workshop invited/contributed split (same); the Plant Health supplement PDF S2.1–S2.209 (rung 5);
the AFS and TWS 2025 programme platforms; ABRCMS and SACNAS programme books for real counts; and the
2025 ASCB oral split, which would move its 2,084 floor up.
