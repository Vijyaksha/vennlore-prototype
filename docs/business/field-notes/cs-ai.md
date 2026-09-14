# Field notes — computer science & AI

Companion to `census-methodology.md`, which stays general. This file holds only what is true of
**CS & AI** and would be noise in the general method. Read both before working a CS & AI row; add
what you learn here, not there.

Started 2026-09-13 from the index pass (DBLP + Crossref, 62 rows at zero searches) and the
2026-09-14 second-pass phase 1. **Interim** — the first phase-2 wave over the 31 second-pass names
has not run yet; extend this file from its results.

## The unit, settled

Accepted contributed presentations = **accepted main-track papers + posters; workshop and
companion volumes separate; invited talks excluded.** CS conferences publish acceptance counts, so a
"paper" is the abstract of this field. The old note that CS "needs a bar redefinition" is void.

## Scope, and where CS & AI overlaps other censuses

| Meeting | Where it is counted |
|---|---|
| Robotics (ICRA, IROS), signal processing (ICASSP), communications (ICC, GLOBECOM, VTC), circuits (ISCAS), control (CDC), industrial electronics (IECON), remote sensing (IGARSS), SMC | `Census - Engineering` |
| EMBC, ISBI (biomedical) | `Deleted - Engineering` (EMBC parked: counted on medicine) / OUT |
| ISMB, RECOMB, ECCB (bioinformatics) | `Census - Life Sciences` |
| BMES | `Census - Medicine & Health` |
| SPIE, Optica meetings (imaging/photonics) | `Census - Physical Sciences` |

Boundary rows on this sheet, flagged in the Umbrella column: CogSci, HICSS, BIBM, MICCAI.
INFORMS goes on Engineering (operations research); Sunbelt waits for a social-sciences sheet.

## Where CS & AI publishes its counts — zero-search routes, ranked

1. **DBLP's SPARQL endpoint — the whole indexed field in one query.** `https://sparql.dblp.org/sparql`
   is open to plain HTTP requests (dblp.org's HTML and search API sit behind an Anubis anti-bot
   challenge, which is rung 5; the SPARQL host does not challenge). Per-stream paper counts per year:
   ```
   PREFIX dblp: <https://dblp.org/rdf/schema#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
   SELECT ?stream ?title (COUNT(?p) AS ?n) WHERE {
     ?p dblp:publishedInStream ?stream ; dblp:yearOfPublication "2025"^^xsd:gYear .
     ?stream a dblp:Conference ; dblp:streamTitle ?title . }
   GROUP BY ?stream ?title HAVING (COUNT(?n) >= 300) ORDER BY DESC(?n)
   ```
   Split workshop volumes with `dblp:publishedAsPartOf ?vol` and exclude volumes titled
   "Workshops"/"Companion" (`scratchpad/dblplib.py::main_track_split`). Source URL for the row is
   the stream page `https://dblp.org/streams/<key>`; say in Method that it was read via SPARQL.
   Every stream at ≥300 papers in 2024–2025 has already been counted (`scratchpad/cs/p1_csai/dblp_checked.json`).
2. **Crossref proceedings-article facet by container title** — the independent second source and
   the catch for series DBLP lacks. `api.crossref.org/works?filter=type:proceedings-article,from-pub-date:2025-01-01,until-pub-date:2025-12-31&facet=container-title:*&rows=0`
   gives the top 1,000 containers; a per-conference query filters on the exact container title.
   Where both sources hold a meeting they agree within a few papers (CVPR 2,871 vs 2,881).
3. **The venue's own accepted-papers page / OpenReview.** ICLR, NeurIPS, ICML, COLM, RLC, MLSys,
   CoRL publish on OpenReview: `api2.openreview.net/notes?content.venueid=<venue>/2025/Conference`
   with `count` in the response; the venue's "accepted papers" page is the citable artefact.
4. **ACL Anthology** for the NLP family: one volume page per event, one row per paper
   (`aclanthology.org/events/<acronym>-2025/`), Findings volumes listed separately.
5. **National society proceedings platforms** (the second-pass rows live here):
   - **J-STAGE** hosts JSAI's annual-conference proceedings (`jstage.jst.go.jp/browse/pjsai/`,
     one volume per year, paginated listing = countable) and IPSJ material; JSAI's news page
     states the presentation count in Japanese (2025: 1,186 presentations, 4,939 participants).
   - **IPSJ National Convention** proceedings are on IPSJ's digital library (`ipsj.ixsq.nii.ac.jp`);
     the convention site states the number of presentations per year.
   - **Confit** (`confit.atlas.jp`) is a JS SPA — HTTP 202 with an empty body to `curl` — so it is
     **rung 5, orchestrator-only**; it renders a `Presentations(N)` count once loaded.
   - **DBpia / KISS** (Korea) index KCC and KIPS volumes; JS-heavy, likely rung 5.
   - **CCF** recommendation notice enumerates the 36 Chinese national CS conferences
     (`ccf.org.cn/Media_list/ccf/2025-11-21/853354.shtml`); CNCC's own site states forum counts,
     but its forums are largely invited — count contributed posters/papers only.

## Traps specific to this field

- **Workshop inflation.** A DBLP stream or Crossref container often bundles workshop and companion
  volumes: CVPR 2025 = 2,871 main + 675 workshop; CHI = 1,249 + 920. Count main track only.
- **Umbrella double-counting.** FCRC, WCCI, SSCI and the IEEE CS umbrella weeks are sums of
  tracks already counted separately (WCCI = IJCNN + FUZZ + CEC). Never add an umbrella row when
  its tracks are on the sheet.
- **Attendance ≠ presentations, worse than elsewhere.** NVIDIA GTC, RSA, FOSDEM and Grace Hopper
  are session-programmed events; CNCC's 12,000 registrations sit over mostly-invited forums. Judge
  on contributed papers, and mark CURATED where there is no open call.
- **Biennial and rotating series**: ECCV (even years), ICCV (odd years) — DBLP dates the ECCV 2024
  LNCS volumes 2025. Events/yr 0.5.
- **Journal-first venues are already covered**: VLDB (PVLDB), SIGMOD (PACMMOD), CSCW (PACMHCI),
  UbiComp (IMWUT), SIGGRAPH (TOG) all appear in DBLP under their conference identity; the
  programming-languages family (PLDI 89, POPL 81, OOPSLA 214 in 2025) is far below the bar.
- **Anubis on dblp.org.** The HTML site and search API challenge bots; a Playwright session clears
  it in ~8 s. Prefer SPARQL; only fall to the browser for the stream page as the citable URL.
