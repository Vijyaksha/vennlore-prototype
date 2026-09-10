# TAM analysis — society-anchored (v2, 2026-09-09)

Rebuilds TAM around **conferences run by professional societies in the physical sciences**, replacing the old "all ~10,000 scholarly conferences" universe. Companion to `tam-sam-som.xlsx` (which keeps the SAM/SOM detail).

## 1. Verifying "42 professional societies in the physical sciences"

The 42 is real but **Europe-only**: the European Physical Society (EPS) federates the national physical societies of **42 countries**. It is not the global count. The global universe:

| Federation / bloc | Societies | Scope | Source |
|---|---|---|---|
| EPS (Europe) | **42** national physical societies | physics, one per country | en.wikipedia.org/wiki/European_Physical_Society |
| AIP (US) | **10** member societies (+26 affiliates) | APS, Optica, AAS, AVS, AMS, ASA, AAPM, AAPT, ACA, SoR | aip.org/member-societies |
| AAPPS (Asia-Pacific) | **21** societies (20 countries/regions) | JPS, CPS, KPS, AIP-Australia, … | aapps.org |
| Rest of world (not in above) | ~12–15 | CAP (Canada), SBF (Brazil), SMF (Mexico), SAIP (South Africa), … | — |
| Independent physical-science majors | ~15 | MRS, SPIE, ECS, AGU, EGU, IUCr, ACerS, … (some counted as AIP affiliates) | — |

Cross-check: IUPAP has **~52–60 territorial members** (one physics community per country), consistent with EPS + AAPPS + Americas + Africa national societies.

**De-duplicated global estimate: ~90–110 professional societies in the physical sciences. Working number: 100.**
(Physics-proper only: ~85. The 42 figure undercounts by ~2.4x because it excludes the US, Asia-Pacific, and non-physics physical sciences.)

## 2. Conferences per year run by these societies

Societies fall into three tiers by conference portfolio:

| Tier | Societies | Conferences/yr each | Subtotal | Anchors |
|---|---|---|---|---|
| Portfolio societies | ~10 | ~13 avg | ~130 | APS "more than twenty science meetings each year" (aps.org); SPIE ~25 flagship events/yr; Optica dozens of topical meetings; IOP ~30 group conferences; DPG ~7 spring meetings |
| Mid national societies | ~30 | 2 | ~60 | JPS annual + autumn; CPS; KPS |
| Small national societies | ~60 | 1 | ~60 | one annual meeting each |
| **Total** | **~100** | | **~250** (range 220–300) | |

Large-only cut (≥ ~2,000 attendees), from the `SAM by field` sheet: physics/astro ~25 + chemistry/materials ~20 + earth/space ~15 = **~60 large physical-science conferences/yr**.

## 3. TAM

Simple model (price × conferences), per Rupert: **not** the $5,000 anchor — base case $1,000/conference/yr. Sensitivity shown so any price can be read off.

| Universe | Conferences/yr | @ $1,000 | @ $2,500 | @ $5,000 (ref only) |
|---|---|---|---|---|
| **TAM — all physical-science society conferences** | ~250 | **$250k/yr** | $625k/yr | $1.25M/yr |
| TAM-narrow — large only (≥2k attendees) | ~60 | $60k/yr | $150k/yr | $300k/yr |

Value-based cross-check (from `Per-conference economics` sheet): event-tech is ~3–4% of conference cost; the 14 modeled large events alone carry a ~$1.7M/yr event-tech bucket (~$30k–500k each). Extrapolated across the ~250-conference universe: **~$8–12M/yr of total event-tech spend**, of which a program/recommendation product plausibly addresses a 10–30% slice (~$1–3M/yr).

## 4. Honest read

- Anchoring TAM to physical-science societies at a flat $1k/conference gives a **sub-$1M TAM**. That is defensible and honest, but it caps the story at a niche/lifestyle SaaS.
- Three levers make the number bigger without dishonesty: (a) keep the field-agnostic universe (old TAM: 10,000 conferences → $10M @ $1k — medicine and CS/AI dwarf physics, see `SAM by field`); (b) size-based pricing (a 14k-attendee GPS is worth far more than a 1,500-person DAMOP — the value-based $8–12M event-tech bucket captures this); (c) per-attendee pricing instead of per-conference.
- Recommended framing: **TAM = total event-tech spend of all abstract-driven conferences (field-agnostic, value-based); SAM = the ~250 physical-science society conferences; SOM = the 27-event physics list × capture** — this keeps the 42/100-society research as the SAM layer, where it is strongest.

## Sources

- https://en.wikipedia.org/wiki/European_Physical_Society (42 national member societies)
- https://www.aip.org/member-societies (10 members, 26 affiliates)
- https://aapps.org / https://www.jps.or.jp/english/about-jps/aapps.html (21 societies, 20 countries/regions)
- https://iupap.org/who-we-are/members/ (~52–60 territorial members)
- https://www.aps.org/events ("more than twenty science meetings each year")
- https://spie.org/conferences-and-exhibitions/conferences-and-exhibitions-calendar
- https://www.optica.org/events/
