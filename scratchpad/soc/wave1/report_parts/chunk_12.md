| **AEA** `/conference/<year>/program?q=…&page=N&per-page=N` | Returns a 46 KB shell with zero sessions, with or without a cookie jar, `Referer` or `X-Requested-With`. `/preliminary?page=N` **silently ignores the parameter** and returns the same 50 sessions for every N | Enumerate session ids instead |
| **AIEvolution** (NCTM) `aievolution.com/ntm2601/` | Angular app; all data behind a single POST-driven `?do=cnt.jsonServices` | **Rung 5** — note JSM is the same platform family but its operator publishes a static JSON export |
| **PsychArchives** | `api.psycharchives.org` fails TLS certificate verification; `www.psycharchives.org` 404s on the DSpace REST community endpoint | Unusable this run |
| **Crossref** for ANPEd, CNIE, LASA, ICME, ISA, ECER, JPA | No container at all (JPA: `query=日本心理学会` returns `total-results: 0`) | These bodies do not deposit — do not retry hopefully |
| `www.eeassoc.org/conferences`, `www.dgps.de/kongress/`, `www.isa-sociology.org/en/conferences/world-congress`, `www.ipsa.org/wc`, `www.mathunion.org/icmi/conferences/icme…` | Plain 404 — **the URLs in the phase-1 notes are stale** | Navigate from the society root |

---

## 4. Counting rules this field needs

1. **Report papers, never sessions.** See *The unit* above. This is the field's defining rule.
2. **Exclude by the organiser's own label wherever one exists, and say so.** JSM types its sessions
   Invited / Contributed / Topic-Contributed; ISA's API carries `Withdrawn`, `Type` and `ProgramCode`;
   SPSP's table has a Category column; ANPEd labels every entry's type; EEA-ESEM types each session.
   Where **no** label exists — AEA/ASSA marks no paper invited anywhere — **say plainly that invited
   content could not be separated** rather than implying it was.
3. **Withdrawals are real and large.** ISA flags 2,128 of 6,765 records withdrawn; counting the raw
   total would overstate that row by 46%. Always look for a withdrawal flag before counting an API.

