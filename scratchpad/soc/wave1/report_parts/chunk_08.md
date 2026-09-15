
**AEA/ASSA — enumerate by session id, because the pager is broken.** Every pagination variant returns
the same 50 sessions (§3). Instead:

```
https://www.aeaweb.org/conference/<year>/program/<id>        # papers are class="paper-title"
```

Crawl a generous id range with a resumable script. Ids resolve only at **1000–2458**; the empty
margins on both sides (600–999 and 2459–2700 all 404) are what proves the range complete. A second
pass over the 478 paper-bearing sessions recovers each session's `type` and `Hosted By:` association.
**2,210** papers; 72 distinct host associations.

### 2.4 Crossref proceedings containers

Coverage in this field is thin — ANPEd, CNIE, LASA, ICME, ISA and ECER deposit **nothing** — but where
it exists it is exact and free.

```
# the facet IS the figure; query.container-title only re-ranks
https://api.crossref.org/works?filter=type:proceedings-article,prefix:<PREFIX>,from-pub-date:<Y>-01-01,until-pub-date:<Y>-12-31&rows=0&facet=container-title:200
# then re-derive by cursor-paging and grouping, to be safe
https://api.crossref.org/works?filter=…&rows=1000&select=DOI,container-title,title&cursor=*
```

| Body | Member / prefix | Result |
|---|---|---|
| **AERA** | 1604 / `10.3102` | `Proceedings of the 2025 AERA Annual Meeting` **4,676**; 2024 4,189; 2023 4,678 |
| **IATED** | 8703 / `10.21125` | 2025: ICERI **1,619** / EDULEARN 1,696 / INTED 1,255, summing exactly to the prefix total 4,570 |
| **Even3** | 11875 / `10.29327` | A **Brazilian anais platform depositing one DOI per trabalho for many congresses** — 13,848 proceedings items in 2025 alone. CONIC = **1,125**, confirmed by DOI slug `10.29327/xxxiii-conic.` |

**Even3 is the find to carry forward**: its year-scoped container facet is a one-call census of a large
slice of Brazilian conference output. The same 2025 facet also shows XLII Congresso Brasileiro de
Reumatologia 741, Anais SIMPEP 551, SBAI+SBSE 546, SOBER 491 — phase-1 material for other fields.

