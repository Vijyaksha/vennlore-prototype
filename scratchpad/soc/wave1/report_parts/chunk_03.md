| 33 | NCTM Annual Meeting & Exposition | none; 6,000 attendees, judged 14% → ~840 | 2026 | 9 | BORDERLINE | 1 |
| 11 | ICA Annual Conference | blocked | — | — | NEEDS_RUNG_5 | 1 |
| 68 | DGPs Kongress | none; 2,000 attendees, judged 80% → ~1,600 | 2026 | 9 | NEEDS_RUNG_5 | 0.5 |
| 94 | ICME | none | — | — | UNRESOLVED | 0.25 |
| 162 | APSA (Asia-Pacific Sociological Association) | name did not resolve — **drop** | — | — | UNRESOLVED | — |

Row 63 was returned by the pilot as `NEEDS_RUNG_5` with a counted floor of 209 papers from 1 of 8
programme pages; **the orchestrator finished it at rung 5 on 2026-09-14** (Cloudflare-cleared pager
plus the pilot's distinct-title rule) at 1,093 papers in 297 Contributed Sessions.

**Plan waves in this field around programme artefacts, not around search.** Not one of the 10
searches returned a usable figure directly — each only located an artefact, and twice a search
snippet asserted figures that the actual page contradicted (§5).

---

## 2. Every route that worked

### 2.1 The society WordPress media index — the workhorse of this field

Five rows, zero searches each. The pattern lists programme PDFs that the site's own navigation does
not link:

```
https://<society>/wp-json/wp/v2/media?search=<term>&per_page=50&_fields=source_url,date
```

Useful `search` terms, in yield order: `program`, `annual meeting`, `convention`, `program book`,
`preliminary`, `abstract`, `schedule`.

| Society | Host | What it yields |
|---|---|---|
| **APSA** | `apsanet.org` | Full Annual Meeting programme for 2024, 2025, 2026 |
| **ASA** | `www.asanet.org` | Programme books 1999, 2000, 2011, 2012, 2015, 2019, 2022 — **nothing newer is public** |
| **ASC** | `asc41.org` | Full programme every year 2021–2025, plus a historic run back to 1958 |
| **NCA** | `www.natcom.org` | Convention programme 2024 and 2025 |
| **AAG** | `www.aag.org` | Annual meeting programme 2019, 2022, 2023, 2024, 2025, 2026 |

