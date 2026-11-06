
## 6. Duplicates, and the rows I was least sure of

### Duplicate and umbrella risk

No two rows in this queue are the same meeting, but four need flagging on the sheet:

- **JSM and ASSA are umbrella meetings** and their figures are upper bounds on any member society.
  JSM's sponsors span the ASA sections and IMS. ASSA's 478 paper-bearing sessions are hosted by **72
  distinct associations** — American Economic Association 142, Econometric Society 48, AREUEA 21,
  Labor and Employment Relations Association 15, Union for Radical Political Economics 10, and 67
  more. **Never also count a member association's ASSA sessions as its own row.**
- **AAR is co-located with the Society of Biblical Literature.** The 1,396 is AAR's own programme book
  only (session ids A20-/A21- on `papers.aarweb.org`); SBL would be a separate row.
- **ISA World Congress vs ISA Forum** — both live on one Confex host; only `wc2023` is row 88.
- **EEA-ESEM is itself a joint meeting** (EEA + Econometric Society European Meeting, joint since 2003);
  its session table splits 29 EEA / 14 ESEM / 2 joint on the page sampled. Count once.

**Boundary rows** the orchestrator should assign deliberately: **JSM** (mathematics/statistics),
**AAR** (humanities), **CONIC-SEMESP** (all disciplines, an undergraduate research congress).

**Phase-1 gap found while resolving row 162, not a result for that row:** there is a real **Pacific
Sociological Association (PSA)**, `https://www.pacificsoc.org/`, whose 97th Annual Conference ran
1–4 April 2026 at the Westin Long Beach with an open call, and a 98th announced for 2027. It is a US
regional body, not an Asia-Pacific one, it is **not on this sheet**, and it needs its own row rather
than being substituted into row 162.

### Least sure of, in order

1. **NCTM (33)** — no count at all. ~840 from **6,000 projected** (not actual) attendees at a judged
   14%. Fails test 1 except through the 800 within-100 leeway; the relative ±20% flex band tops out
   around 1,010, so it passes test 2 narrowly. **This row sits on the line and should be decided
   knowingly, not read off the arithmetic.** A counted session figure from rung 5 would settle it.
2. **KPA (110)** — 561 is **posters only**; the oral and symposium tracks are scheduled in the
   programme book but have no published abstracts. 561 is below the 800 leeway, but per rule 1 that is
   a partial artefact, **not** positive evidence of a small meeting.
3. **PAA (13)** — 1,106 orals counted, 981 posters organiser-stated and unlisted. Also a recorded
   disagreement: the counted orals **exceed PAA's own stated 1,049 by 57**, the excess sitting in nine
   8-paper and three 7-paper sessions.
4. **ASA (7)** — 2,644 is exact and doubly validated, but from **2022**. ASA publishes no newer
   programme book anywhere the media index exposes.
5. **CPS (108)** — organiser-stated, never counted, and dated **2022**; its internal reconciliation is
   what makes it usable. Cadence is **irregular** (editions 2022, 2023, 2025 — no 2024), so the true
   rate is nearer 0.75/yr than the 0.5 recorded.
6. **IPSA (89)** — organiser-stated 3,053, twice the bar but never counted; the programme is behind a
   member login so a counted figure is out of reach for this census.
7. **JPA (104)** — 1,314 from a J-STAGE deposit. The series is smooth and rising across four
   consecutive volumes (937 → 1,159 → 1,240 → 1,315) with none of the discontinuity that exposed
   JSME's partial deposit in engineering, so it is treated as a count rather than a floor — but a
   partial deposit cannot be fully excluded, and the phase-1 hint of 2,500–3,000 is unexplained.
8. **CNIE (119)** — 1,250 is a floor on COMIE's own warning that the memoria is still being completed;
   also dated 2023, with v18 (2025) returning HTTP 401.
9. **ICME (94)** — no figure of any kind. Both congress domains are dead, Crossref has no container,
   and Wayback was offline all run.
10. **ECER (55)** — 3,216 is an exact count of *contributions*, but a 200-item random sample shows ~7%
    are session containers or non-paper formats, so the papers-and-posters figure is nearer 3,000.
    Also: the URL's conference id is **ignored** and the database always serves the current edition,
    so the figure is ECER 2026, not the 2025 edition the id requested.

### Rung-5 queue for the orchestrator

| Row | Target | Why |
|---|---|---|
| 11 ICA | `https://www.icahdq.org/mpage/ICA25-program` (Cloudflare), then `…/ICA25-exhibitor-info` for A1 attendance | No figure of any kind; the CDN pattern `cdn.ymaws.com/www.icahdq.org/resource/resmgr/conference/<year>/<file>.pdf` works but the filename must come from the walled page |
| 68 DGPs | `https://www.uni.lu/fhse-en/conferences/54th-dgps-congress/program/` (AWS WAF), then the press kit PDF | Attendance ~2,000 already in hand; the count is not |
| 33 NCTM | The AIEvolution session search, `aievolution.com/ntm2601/?do=cnt.appLoader&…&code=Sessions_Search` | Converts a knife-edge judged ratio into a count |
| 13 PAA | `https://www.populationassociation.org/paa2025/program2025/mobile-and-online-app` | Would add the 981 unlisted posters |
| 104 JPA | Confit 講演検索 for `jpa2025` | Would test the J-STAGE deposit against the live programme |
| 110 KPA | Programme book `fno=25788`, or the notice "2026 창립 80주년기념 … 주요 성과 보고" (2026-09-02) | Would add the oral and symposium tracks |
| 94 ICME | Wayback captures of the real `icme15.org` from 2024, **before** the squatter, once the Internet Archive is back | The only surviving route to that programme |
