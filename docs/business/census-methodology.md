# Conference census — reusable method

How to census one field's conferences for the TAM/SAM model in `tam-sam-som-v3.xlsx`.
Physical sciences (complete) and medicine & health (partial) were built this way.

## The bar

**A conference counts if it has ≥1,500 submitted abstracts.** That is the `VERIFIED` bar and it
has not moved.

**But the *retention* floor is ~700 abstracts, not 1,500** (Rupert: ~800 on 2026-09-09, lowered to
~700 on 2026-09-10). A meeting between
roughly 700 and 1,499 is kept as `BORDERLINE` on the census sheet — the model is generous by design
and the product's value does not switch off at 1,499. Only positive evidence of *under ~700*
justifies moving a row to the deleted sheet.

**When the floor moves, re-sweep the deleted sheet — do not just apply it going forward.** The
whole reason the deleted sheet keeps every counted number (rule 5) is that a floor change should be
answerable by re-reading it, never by re-researching. Lowering 800 → 700 on 2026-09-10 released
three rows (SciX 763, SPIE Medical Imaging 737, APS SCCM 716) at zero research cost.
**Check for duplicates before moving any of them**: at that same sweep, M&M (1,035) and ECS (2,400)
also cleared the floor but were already present on the census sheet, and restoring them would have
listed both conferences twice. In practice:

| Counted abstracts | Tier | Sheet |
|---|---|---|
| ≥1,500 | `VERIFIED` | census |
| ~700–1,499 | `BORDERLINE` | census |
| <~700, on positive evidence | `OUT` | deleted |
| no evidence either way | `BORDERLINE` | census — never `OUT` |

Abstracts, not attendance — the program is public even when attendance isn't, and abstract
volume measures the navigation pain the product solves. Attendance is recorded alongside as
context, never as the test. Two real examples of why: OFC has 16,700 attendees but 1,300 papers
(a trade show by attendance, but 1,300 papers clears the 800 floor, so it stays); APS DPP has
2,190 attendees and 2,131 presentations (a research congress — in).

## Six rules

1. **Prove positives, never negatives.** Only look up conferences that might clear the bar.
   Never spend searches confirming that a small society is small. The result is an honest
   *floor*, not an exhaustive count — that trade is deliberate.
   **This is not a licence to rule things out.** Not looking is fine; looking once, finding
   nothing, and recording that as a failure is not. A candidate you chose to research is only
   `OUT` on positive evidence — see the escalation ladder in Phase 2.
   **Rule 1 is suspended during a completeness pass.** When the task is "re-verify every row"
   rather than "census the field", this rule works against you: it tells an agent to skip exactly
   the rows the pass exists to check. On 2026-09-10 an agent applied it correctly-as-written and
   returned 9 rows marked "NOT RESEARCHED THIS PASS"; when those were reworked under a suspension,
   three of them turned out to have conferences the sheet claimed did not exist (Kazakhstan ~70
   reports, Mongolia 43, Macau a co-organised Greater Bay Area congress) — all invisible to
   English-only searching. **Say so explicitly in the brief when you suspend it**, because an agent
   following the written method will otherwise skip them and be right to.
2. **Every number needs an exact-page clickable URL** plus the year it refers to. Not a
   homepage, not a search-results page — the page where the number actually appears, so it
   can be clicked and checked. Link PDFs directly.
3. **No figure without a source is written down.** Mark it `UNKNOWN`. Never estimate,
   interpolate, or reason "probably about X".
4. **Record the method, not just the number.** Both physical-sciences sheets carry a
   `Method — which escalation-ladder rung produced the number, and exactly how` column (col `T`
   on the census sheet, col `V` on the deleted sheet). Every figure you write must name the rung
   *and* be reproducible from what you wrote: the exact page or PDF, the exact `grep`/count used,
   the ID pattern, and which IDs you spot-checked. A number nobody can re-derive is a number
   nobody can trust six months from now.
   **Credit the rung that PRODUCED the figure, never the highest rung you reached.** These are
   different things and conflating them produces rows that read "RUNG 4" beside an `UNKNOWN`
   abstract count, which is nonsense on its face. A row with no figure says
   `NO RUNG YIELDED A FIGURE — highest rung reached: n`, and per rule 1 that is absence of
   evidence, not evidence the meeting is small. This bit us on 2026-09-10: an agent correctly
   reported its highest rung attempted, and the writeback logic printed it as though it had
   yielded, mislabelling 12 rows until it was caught on review.
5. **Write the number even when the row is being deleted.** A row moving to the deleted sheet
   still gets its counted abstracts, year, source URL and method filled in. The deleted sheet is a
   *reversible* parking place, not a bin — if the bar is lowered again, restoring a row must be a
   re-read of the sheet, never a re-run of the research. Sharpen vague figures on the way through:
   ACA went from "400+" to an exact 390 with a clickable source, and stays deleted.
6. **The link must be the link the number came from.** Different conferences yield their number at
   different rungs, so the source column points at whatever *that* row's evidence actually was —
   the journal supplement issue page, the programme PDF, the society blog post — never a homepage
   or a generic conference page that merely mentions the meeting.

## Two phases (Phase 1 inline; Phase 2 may be parallelised — see the agent protocol)

Both phases use web search — they differ in **what** they search for. Phase 1 searches
*broad*: find every conference name that exists. Phase 2 searches *deep*: get the numbers for
each name found. The phases are strictly ordered and must not be interleaved. Enumerating
while verifying is the one mistake that wrecks a census: the budget runs out mid-way and you
never learn what you missed.

Split the budget roughly **one third to Phase 1, two thirds to Phase 2**.

**Phase 1 is always inline.** Discovery is a judgement task with a saturation stopping rule — you
have to see the whole accumulating list to know when a sweep has stopped returning new names, and
that judgement does not survive being split across agents. **Phase 2 is the parallelisable one**,
because each row is independent: a conference's abstract count does not depend on any other row.

### Phase 1 — Discover every candidate name (broad searches)

Purpose: the **complete list of candidate conference names**. Names only — no abstract
counts, no verification, no per-conference digging.

Start from knowledge (list what you already know), then search to find what you don't.
Discovery queries are list-shaped, not conference-shaped:

- `"largest <field> conferences by attendance"`
- `"list of <specialty> society annual meetings"`
- `"top <field> conferences 2025"` / `"major <specialty> congresses Europe"`
- `"<umbrella body> member societies"` — federations publish member lists that name meetings
- conference-aggregator and society-directory pages, which enumerate in bulk

**Run the same sweep a second time.** Same area, same prompt — the point is simply to catch
the odd ones out that the first pass missed. Keep going until a pass returns mostly names you
already have; that saturation is the signal the list is near-complete.

These are the gaps a second pass most often catches, worth a glance before calling it done:

- **Geography** — the US body *and* its European/Asian counterpart (ACC/ESC, ACR/EULAR,
  ASH/EHA). Missing the mirror society is the most common gap.
- **Umbrella bodies** — federations, joint meetings, multi-society events.
- **Adjacent disciplines** — allied health, nursing, informatics, education, public health,
  and the research-side societies next to the clinical ones.
- **Publication trails** — journal supplements and proceedings series imply a meeting.
- **Industry** — where the field's vendors exhibit.

Over-include. A name that turns out to be small costs one Phase 2 search; a name never
listed is invisible forever.

**Write the whole list into the sheet before starting Phase 2**, one row per conference,
`Tier = NOT YET CENSUSED`, every number column empty. The sheet is now complete in *names*
and empty in *numbers* — which is what makes progress measurable.

### Phase 2 — Verify each candidate (deep searches)

Work down the candidate list **largest-first**, upgrading rows in place from
`NOT YET CENSUSED` to `VERIFIED` or `BORDERLINE`.

**Run Phase 2 in two passes, census sheet first, deleted sheet second.** Pass A works
`Census - <Field>` and keeps the good ones. Pass B then runs the *same* process over
`Deleted - <Field>`, because a deleted sheet built under an older, higher bar always hides
qualifying meetings — and because most deleted rows were ruled out on `UNKNOWN` rather than on
evidence. Never treat the deleted sheet as settled: it is the single richest source of cheap
restorations, and Pass B costs nothing but the ladder.

1. **Search in parallel batches of ~4**, one query per conference, shaped like
   `"<conference> number of abstracts submitted <year>"`.
   **Cap: 3 searches per conference.** Rung 1, one rung-2 reword, and at most one more. Then
   either fall to the zero-search counting rungs or record the trail and stop. Session-2 data and
   this session agree: query 3+ on the same conference is nearly always wasted.
2. **Record as you go**: number, year, source URL, **the rung and how you worked it**, attendance
   if it appears, venue type. The `Method` column is not optional — see rule 4.
3. **One pass. No re-audits, no follow-up rounds.** Apply the citation rule while writing,
   not afterwards — re-audit passes roughly tripled the cost on physical sciences.
   The one sanctioned exception is a **spot-check of decisive rows**: any figure landing near the
   retention floor, or that flips a verdict, gets re-derived before it is written. That is cheap
   and targeted; a blanket re-audit is not.
4. **When the budget runs out, simply stop.** Un-reached rows keep `NOT YET CENSUSED`.
   Nothing is lost and the gap is visible and named.
5. **A rejected candidate moves to the deleted list — it is never left on the census sheet
   and never erased.** The whole point is that no later session spends energy on a candidate we
   have already ruled out. Each field gets a companion sheet, `Deleted - <Field>`, with the same
   columns plus `Deleted on` and `Why deleted`. The moment a candidate is shown to be too small,
   to have no qualifying meeting, or to duplicate a row kept elsewhere, cut the whole row across
   with its evidence intact and remove it from the census. The census sheet then holds only live
   rows, so `NOT YET CENSUSED` always means "genuinely still to do".

   **Restoration is the same move in reverse, and equally model-neutral.** When the floor is
   lowered, rows come *back* from the deleted sheet to the census sheet. Do it the same way: wire
   the ranges first, move second, verify the totals are unchanged third. On 2026-09-09 four rows
   (AVS, ASA, ICHEP, Quark Matter) were restored on numbers they already carried, and SAM Global,
   SAM US and SOM did not move at all — only the TAM physical-sciences part rose, 41.66 -> 43.83,
   because TAM counts non-`OUT` census rows while SAM spans both sheets.

   **Verify totals by recomputing them independently, not by reading the sheet.** `openpyxl` does
   not evaluate formulas, so a script that reads `F54` sees the formula text, not a number. Sum
   `Include * Events/yr` straight from the cells in Python, confirm it reproduces the known
   baseline *before* touching anything, then re-run it after. That is what proved the 2026-09-09
   moves were neutral and isolated the genuine −2.00 duplicate fix.

   **Watch for row-reference breakage when moving rows.** `openpyxl` does not rewrite formulas on
   `insert_rows`/`delete_rows`, so: per-row formulas like `=IF(O31=1,...)` must be rewritten to
   their new row on the way across; every range in every sheet that references the moved region
   must be rewired by hand (there were seven, across `Summary` and `TAM large-conf estimate`);
   and clearing a row in place is safer than deleting it when other rows carry self-referencing
   formulas. Give the deleted-sheet ranges generous headroom (row 200) so appends land inside them.

   **Deletion must never move a model number.** Totals therefore span *both* sheets: every
   SAM/SOM formula is `SUMPRODUCT(<census range>) + SUMPRODUCT(<deleted range>)`, so a row
   contributes identically wherever it sits. This matters because `Tier` and `Include` are
   independent — on `Census - Physical Sciences` a meeting can fail the 1,500-abstract bar
   (`Tier = OUT`) and still belong to the SAM universe (`Include = 1`); 113 such rows carry 73.0
   of SAM Global's 114.15 events/yr. With the totals spanning both sheets, all 113 moved across
   and SAM Global, SAM US and SOM stayed at 114.15 / 54.00 / 32.00 exactly. **Wire the totals
   before moving any row, and check the numbers are unchanged after.**

6. **Searching is how you find the countable artefact, not how you get the number.** This is the
   single most important lesson from three sessions. In this session 16 searches produced 4 usable
   figures, and *every one of them was ultimately produced by counting something*, never by a
   search returning a total: COSPAR 3,082 and DAE-SSPS 524 from PDFs, DPG SAMOP 2,028 from a
   crawled programme, M&M 1,035 and IUCr ~1,400 from browser-rendered listings. Rung 1 yielded
   nothing at all, in eight attempts. So the moment a search comes back empty, stop rewording and
   go looking for the artefact: the abstract book, the proceedings TOC, the journal supplement,
   the programme site.
7. **Sanity-check every count against the artefact's own stated total where one exists.** M&M's
   page says "1035 results found" and the independent count of unique `PresentationID` values came
   to exactly 1,035 — that agreement is what makes the number trustworthy. Where no stated total
   exists, get agreement from two *independent* extractions instead (see rung 3).

### Running Phase 2 with parallel agents

**This section adds structure; it does not add a second method.** Everything above — the bar and
the retention floor, the six rules, the escalation ladder, the citation and `Method` discipline —
is mode-independent and binds identically whether a single operator works the rows inline or three
agents work them in parallel. An agent is not following a different procedure; it is following
*this* procedure, on a slice of the rows.

What parallel mode adds is only what fan-out makes necessary: a way to hand results back without
three processes fighting over one workbook, a way to reject bad records at intake, and a rule for
the one rung that cannot run concurrently. If you are working inline, ignore this section entirely
and nothing is lost.

Rows are independent of one another, which is what makes this safe to fan out. The protocol:

1. **No agent writes to the workbook.** Three processes writing one `.xlsx` will corrupt it or
   silently drop each other's edits. Agents return one JSON record per row; the orchestrator
   validates every record and performs all workbook writes serially.
2. **The return contract**, per row:
   `row, conference, outcome, abstracts, abstracts_numeric, year, source_url, rung, method,
   spot_checks[], searches_used, verdict, confidence`
   where `verdict` is `RESTORE` / `STAY_DELETED` / `UNRESOLVED` / `NEEDS_RUNG_5`, and `confidence`
   is `exact` / `derived` / `dated` / `floor`.
3. **Intake validation is mechanical, and rejection is the default.** A record is rejected and
   requeued if it has no resolvable URL, names no rung, or carries a method the orchestrator
   cannot re-run from the text alone. "Reproducible" means the exact grep/ID pattern or the exact
   page and control that was clicked — not "counted the programme".
4. **Rung 5 is serial.** There is one browser instance, so agents work rungs 1–4 and 6–8 and
   return `NEEDS_RUNG_5` for anything behind a 403 or a JS-rendered listing. The orchestrator runs
   that queue afterwards. Agents may first try a spoofed browser user-agent with `curl`, which
   beats some walls (spie.org) but not others (mrs.org, journals.iucr.org, iucr2023.org).
5. **Spot-check the decisive rows, not the batch.** Re-derive anything landing near the retention
   floor or flipping a verdict; sample the rest. Blanket re-auditing is the cost sink the original
   rule was protecting against.
6. **Budget: 3 searches per row, hard.** See Phase 2 rule 1.

### The escalation ladder — never stop at the first empty search

**A conference is never marked `OUT` because a number wasn't found.** `OUT` means positive evidence
that it fails the bar (FiO+LS: 780 contributed papers) or that the programme isn't a contributed-abstract
programme at all (AAAS: ~120 curated sessions). Absence of evidence is `BORDERLINE`, never `OUT`.
The reason this needs stating: on `Deleted - Physical Sciences`, **91 of 110 rows were ruled out on
`UNKNOWN` alone** — only 19 carry an actual number below the bar. Most of those 91 really are small
national societies, but nothing on the sheet distinguishes "checked and found small" from "looked
once and found nothing", and that distinction is the whole point.

Work the rungs in order and stop at the first that yields. Record which rung produced the figure.

| # | Rung | Cost | Notes |
|---|---|---|---|
| 1 | `"<conf> number of abstracts submitted <year>"` | 1 search | The default shape. Works ~1 time in 4. |
| 2 | **Reword generically** — `"<conf> <year> how many abstracts presentations"`, or in the society's own language (`Anzahl Beiträge`, `número de resúmenes`) | 1 search | The rung that was missing, and the highest-yield one. Societies write "how many abstracts" in blog posts and press releases; almost none use the phrase "abstracts submitted". Produced the IASP, SMFM, ECE, NASS and ECS figures. |
| 3 | **Count the abstract supplement** | 0 searches | Download the programme/abstract PDF, count unique abstract IDs (`grep -oE '<id pattern>' \| sort -u \| wc -l`). Proven: ESAIC 2025 → 1,490; COSPAR 2024 → 3,082 (`[A-Z]{1,4}[0-9]?\.[0-9]+-[0-9]{4}-24`, of which 193 WITHDRAWN); DAE-SSPS 2024 → 524 (`[a-l][0-9]{4}`). **Extract twice** (`pdftotext -layout` and `-raw`) and compare — agreement means the count is real, disagreement means extraction is lossy. **Also record the highest assigned ID**: DAE-SSPS showed 524 published against 684 issued, i.e. accepted vs submitted. |
| 4 | **Count the abstract archive** | 0 searches | Purpose-built archives paginate and count: mdsabstracts.org, iadr.abstractarchives.com, archive.ismrm.org, atcmeetingabstracts.com, ma.ecsdl.org. Also **journal supplement issue pages** — ACA 2023 = 390 from Acta Cryst A79 part a1 — and **static programme archives**, which are the highest-yield artefact of all: DPG Verhandlungen (SAMOP 2025 = 2,028 from 269 session pages) and the **APS Meeting Archive** (`meetings-archive.aps.org/<div>/<year>` — meetings.aps.org now 302s here; plain HTML, no JS, no pagination, and each session states its own count: DNP 2025 = 887, validated against 745 for 2024). **Indico** exposes an exact count with one call: `<host>/export/event/<id>.json?detail=contributions` (EPS-HEP = 684; CERN, IN2P3, DESY all serve it). **Crossref's publisher-deposit index** settles whole publisher back-catalogues in one pass — it produced FiO+LS 593, all eight Optica topical congresses at once, and SPIE Advanced Lithography 433 across 5 volumes. |
| 5 | **Drive the JS programme site with a browser** | 0 searches | confex / eventscribe / abstractscorecard defeat `curl` but not Playwright or Chrome. Covers most US societies, and also the plain 403 walls — journals.iucr.org, mrs.org, iucr2023.org all refuse `curl`/WebFetch but open fine in Playwright. **Watch for virtualised lists**: journals.iucr.org drops rows out of the DOM as you scroll, so a single `innerText` grab undercounts badly — scroll in small steps and accumulate IDs into a `Set` across steps. |
| 6 | **Poster-board arithmetic** | 0 searches | Programmes print "boards 1–2,400", or poster sessions × boards per session. A direct floor. |
| 7 | **Prior-year or sister-meeting figure** | 1 search | Mark `DATED`. A congress at 1,800 in 2019 is not under 1,500 now. |
| 8 | **Third-party congress review** | 1 search | EMJ, ASCO Post, Medscape quote totals. Source of UEG's 3,800 and ERA's 2,800. |

**There is no "ask the society" rung.** Emailing an organiser was once listed as a final rung; it is
removed, because nothing in this workflow can send or receive email, so it functioned only as an
escape hatch that let a row be abandoned while looking diligent. If the ladder runs out, the row is
`UNRESOLVED` with its trail recorded — say that plainly rather than deferring to a step nobody will
take.

Rungs proven *not* to work, so don't retry them: **Crossref** (congress abstracts get no DOIs) and
**PubMed** (doesn't index individual abstracts). Both were tested and returned ordinary article
counts in the dozens.

**`UNKNOWN` is only permitted once every *applicable* rung is exhausted.** Stopping at rung 2 with
rung 4 sitting there unworked is not a result, it is an unfinished row. A rung counts as exhausted
only if it was worked, or if it is genuinely inapplicable — and inapplicable must be *stated with
its reason* ("the society publishes no programme, so rungs 3-6 have nothing to count").

The specific failure to watch for, because it is the common one: **identifying the countable
artefact and then not counting it.** On 2026-09-10 seven of thirteen numberless rows in a single
agent batch had located the exact artefact — an abstract yearbook, a proceedings record, a
programme archive — written "NEXT: rung 4, count it", and returned `UNKNOWN`. Those counts cost
*zero searches*. Naming the next rung is not a substitute for climbing it; it is only acceptable
when the next rung is genuinely out of reach (needs a browser you do not have).

If every applicable rung really does fail, the row stays `BORDERLINE` with `UNKNOWN` **and its
Method column records which rungs were tried, which were inapplicable and why, and the exact next
action**, so the next session escalates rather than repeating rung 1.

### The publisher deposit index — the highest-yield rung in medicine

Medicine publishes its abstracts in journal supplements, and **OUP and Elsevier deposit those
abstracts to Crossref individually**. That makes a whole conference countable exactly, at zero
search cost, without ever opening a PDF. This one pipeline settled a dozen rows in a single agent
slice on 2026-09-10.

The method: cursor-page the journal's Crossref endpoint for a date range, group on
`(volume, issue)`, and filter on `page` starting with `S` — supplement pagination is what marks an
abstract apart from a regular article.

```
https://api.crossref.org/journals/<ISSN>/works?filter=from-pub-date:<Y>-01-01,until-pub-date:<Y>-12-31&rows=1000&select=volume,page,title&cursor=*
```

Then follow `next-cursor` until it stops. Proven counts: ESTRO 2,823 (Radiotherapy and Oncology
vol 206, out of a 3,453-item journal-year), ESOC 1,981, EHRA 876 (DOIs `euaf085.001`–`.876`,
contiguous with zero gaps), ICML 926, ASCO GU 882, ASCO GI 833, Tandem 810, AACE 778, SGO 695
(696 S-paged items less one FOREWORD), EUROTOX 1,075.

**Publisher boundary, established empirically:** Elsevier, LWW and OUP deposit abstracts per item,
so they are countable this way. **Wiley, Springer, Karger, Liebert and AAPM do not** — they deposit
the whole supplement under one DOI. For those, two workarounds beat the paywall before you resort
to rung 5:
- **The society's own mirror.** AGS is the template: `agsjournals.onlinelibrary.wiley.com` 403s and
  deposits nothing, but AGS mirrors the entire JAGS supplement as a free PDF on its own meeting
  site — 1,008 abstracts, both `pdftotext` modes agreeing on every prefix. Try the society site
  before giving up on a Wiley-published supplement.
- **Confex's backing API.** `meetingapp.cgi/Program` 403s, but the SPA's own endpoint
  `<host>/<meeting>/meetingapi.cgi/Program` returns JSON with a `ChildList_Paper` array per
  programme. That gave AcademyHealth ARM 1,784 (2025) and 2,089 (2023) at zero search cost.

**Supplement pagination is not always `S`.** The `S`-prefix filter is the default, not the rule, and
getting it wrong makes a large conference look unresolvable or tiny:
- **`e`-pages**: IJROBP puts ASTRO's *posters* on e-pages. The S-filter alone returns 460 (orals
  only); the true figure is 460 + 1,805 = **2,265**, an almost fourfold undercount.
- **`B`-pages**: TCT paginates on B. The S-filter returns nothing at all.
- Always group the journal-year by page-alpha-prefix first and look at what prefixes exist, rather
  than assuming `S`.

**One journal volume routinely holds several meetings, sometimes contiguously.** Annals of Oncology
vol 36 carries **four** ESMO meetings on *contiguous* S-pagination — only the Elsevier DOI month
separates them, confirmed by the LBA numbering restarting at each. JACC vol 85 issue 12 mixes the
regular issue with a 4,697-abstract supplement, separable on DOI form. A naive volume-wide count
merges them into one inflated number.

**The publisher boundary has one known exception.** *Alzheimer's & Dementia* deposits per item
across nine supplement parts (AAIC = 5,985) even though Wiley otherwise does not. Re-tested at EJN
and HemaSphere, which behave normally — so the boundary holds, with that title carved out. Test the
specific journal rather than trusting the publisher.

**Four traps, all hit for real:**

- **Deposited-item count, not the highest ID.** ESTRO's IDs run 10–5037 but are block-allocated
  per track; the 2,823 deposited items are the figure.
- **One journal volume can hold two conferences.** Clinical Lymphoma Myeloma & Leukemia vol 24
  mixes the IMS and SOHO supplements with both page series restarting — separate them on the
  abstract-ID prefix in the title, never on the page band.
- **OpenAlex `group_by=biblio.issue` silently merges a supplement with the regular issue of the
  same number** (seen on Endocrine Practice). Crossref's page-prefix filter is the trustworthy
  route; use OpenAlex only to corroborate.
- **Some publishers deposit the whole supplement under ONE DOI** — Wiley, Springer, Liebert and
  AAPM all do. Then there is nothing per-abstract to count and the PDF is usually paywalled, so
  the row goes to rung 5 with the TOC URL named. Absence of a per-item deposit is *never* evidence
  the meeting is small: ESMRMB's supplement is an 889-page book of abstracts.

### Why rungs 3–6 matter more than they look

The first full Phase 2 session on medicine ran ~97 searches and got a usable number from roughly
one query in four. **Most societies never publish an abstract total.** What they do publish is the
abstract supplement, and that is countable at zero search cost:

- Journal supplements (`Diabetologia`, `Journal of Hepatology`, `CHEST`, `Obesity`, `JACC`,
  `Molecular Therapy`, `Innovation in Aging`, …), abstract archives (mdsabstracts.org,
  iadr.abstractarchives.com, archive.ismrm.org, atcmeetingabstracts.com), confex programmes, and
  society program-book PDFs.
- Worked example: Euroanaesthesia 2025 publishes no total. Downloading the ESAIC abstract
  programme PDF and counting unique abstract IDs (`grep -oE '[0-9]{2}AP[0-9]{2}-[0-9]+' | sort -u | wc -l`)
  gave **1,490** — reproducible and clickable.

So: search first for a published figure, and the moment a search comes back empty, record the
countable source in the Notes column rather than spending a second query. Then work the count
offline. Budget spent on a second or third query for the same conference is nearly always wasted.

**Expect Phase 2 to span several sessions.** A session allows 200 web searches
(`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` raises it), and a full field will exceed that.
This is fine and requires no special handling: the sheet is the state. Each session picks up
the top `NOT YET CENSUSED` rows, verifies as many as the budget allows, saves, and stops.
Phase 2 **may** be run by parallel agents, under the protocol below. The older blanket rule
("never hand verification to subagents") was written after session 2, when the thing that failed
was *unverifiable provenance*: an agent returned a number and nothing on the sheet could say where
it came from, so the only remedy was a full re-audit. The `Method` column removes that failure
mode — a returned row that cannot name its rung and its exact-page URL is now mechanically
rejectable at intake, before it ever reaches the workbook. Parallelise only with the protocol
intact; without it the old rule stands.

Report progress as **verified / total candidates** so completeness is always legible.

## Tiers

| Tier | Meaning |
|---|---|
| `VERIFIED` | Published count ≥1,500, sourced to an exact page |
| `BORDERLINE` | Near the bar, or obviously huge but no count published (include it — the model is generous by design) |
| `NOT YET CENSUSED` | Known candidate, never reached. Name only, never a number |
| `OUT` | Fails the bar, or no evidence of scale. The row moves to `Deleted - <Field>` (see rule 5) |

Also flag in the notes column when a figure is **DERIVED** (arithmetic from a published
statement), **DATED** (the only published count is years old), or **CLICK TO CONFIRM** (the
page provably carries the number but blocks automated fetching).

## Output format

Two sheets per field: `Census - <Field>` for live rows and `Deleted - <Field>` for rejected ones
(same columns plus `Deleted on` and `Why deleted`). The census sheet carries these columns:

```
Field | Umbrella | Society | Country | Conference | Events/yr |
Abstracts (exact, as published) | Abstr. yr | Abstracts source (click) |
Attendance | Attendance source (click) | Venue | Agent verdict | Tier |
Include (1/0) | SOM (1/0) | US (1/0) | Rev/yr @ $5k | Notes |
Method — which escalation-ladder rung produced the number, and exactly how
```

- `Events/yr`: 1 for annual, 2 for twice-yearly, 0.5 biennial, 0.33 triennial.
- `Include = 0` on every non-physical-science sheet. SAM is physical sciences only; nothing
  from another field may leak into it. New fields feed **TAM** via Method C on the
  `TAM large-conf estimate` sheet.
- `US (1/0)` drives the US / non-US split — always fill it.
- `Method` (col `T` census / col `V` deleted) is mandatory on every row whose number you touched —
  see rule 4. It was appended at the end of each sheet deliberately, so no existing SAM/SOM
  formula's column references shift.
- Totals at the bottom: VERIFIED count, VERIFIED+BORDERLINE, of which US, of which non-US.

## De-duplication — run this before trusting any total

Phase 1 enumerates the same meeting twice whenever a society is reachable under two umbrella
attributions ("Electrochemical Society (ECS)" and "The Electrochemical Society"; "Microscopy
Society of America" and "Microscopy Society of America + Microanalysis Society"). Those pairs are
invisible to eyeballing and they silently inflate the model, so check for them mechanically:

1. **Within each sheet**, group rows on normalised society+conference (strip parentheticals and the
   filler words *annual, meeting, conference, congress, symposium, international, national*) and
   flag any group with more than one row.
2. **Across the census and deleted sheets**, do the same — a meeting can sit live on one and
   duplicated on the other.
3. For every group found, **exactly one row may carry `Include = 1`.** Zero the rest. Never delete
   a row just because it repeats: keep it zeroed with a `[DUPLICATE PAIR …]` note naming which copy
   survives, so no later session zeroes the wrong one.

Found this way on physical sciences: Iran and IPS Israel each had `Include = 1` on **both** copies
and were inflating SAM Global by 2.0 — the only genuine model error the 2026-09-10 run uncovered.
M&M and ECS were duplicated too but already zeroed, so they had never double-counted.

**If you do physically delete a duplicate row, two things break silently** and must be rebuilt:
the per-row revenue formulas (`=IF(O<row>=1, F<row>*price, 0)` is self-referencing and `openpyxl`
does not re-point it on a shift), and any row numbers quoted inside notes. Verify the totals are
unchanged afterwards by recomputing them from the cells, never by reading the sheet.

## Pitfalls (all hit for real)

- **Domain lookalikes.** `aapmannualmeeting.com` redirects to the American Academy of Pain
  Medicine, not the medical-physics AAPM. Confirm the source domain belongs to the society.
- **Bot-blocked sites.** spie.org, arvo.org, mrs.org and others 403 automated fetches. Mark
  CLICK TO CONFIRM rather than dropping a real number or trusting it blindly.
- **Counting by hand beats giving up.** AMS publishes no total; downloading its 48 confex
  program pages and counting unique paper entries gave 4,580 — reproducible and clickable.
  Proceedings TOCs (SPIE, AACR, Circulation supplements) work the same way.
- **Joint and duplicate events.** DDW is four societies running one meeting — count once.
  A conference appearing under two umbrellas gets `Include = 0` on the duplicate row.
- **Trade shows.** Huge attendance plus a small paper count means it fails the bar. That's
  the bar working, not a mistake. The sharpest case found so far is **EuroPCR: 12,177 attendees
  against 743 counted abstracts** — a large teaching and live-case course, not a contributed
  congress. It sits on the ~700 floor while looking, by attendance, like a flagship. This single
  row is the best argument for why the bar is abstracts and never attendance.
- **A cited source may not contain the figure it is cited for.** Three rows in one wave asserted
  numbers their own source URLs did not carry — ISSCR "1,300 posters", AAPS "over 2,200"
  (absent from five Wayback captures back to 2022), and AAIC "5,700". All three were flagged as
  evidenced. When re-verifying an inherited row, **open the citation** rather than trusting the
  tier; a figure whose source does not support it is worse than `UNKNOWN`, because it looks settled.
- **Field boundaries.** Some meetings straddle fields (SfN: neuroscience/health). Pick one
  sheet, note the ambiguity, and count it once.
- **Check Events/yr, not just the abstract count.** A quadrennial congress counted as annual
  inflates the model fourfold. Six medicine rows were wrong on 2026-09-10: WCD and IAGG are
  quadrennial (0.25), IEA WCE and FENS triennial (0.33), ESOT and ESRS biennial (0.5). A world
  congress is very often not annual — verify the cadence whenever you write a number.
- **A meeting can stop existing.** Experimental Biology ended after 2022 and its FASEB J supplement
  vanishes from 2023. Its 5,202 abstracts were the ALL-SOCIETY total across APS/ASBMB/AAA/ASIP/
  ASPET, so a surviving "ASPET at EB" row would double-count every one of them. Delete on
  non-existence, and say that is the reason — it is not a size judgement.
- **Umbrella meetings double-count their members.** Beyond EB: COSM hosts nine societies, DDW four.
  If the only countable artefact is the umbrella, the figure is an upper bound on any one member,
  never that member's count.
- **Programme IDs are often block-reserved, so the highest ID is NOT a count.** The 2025 Austrian/Swiss
  joint meeting's highest ID is 994, which would clear any floor; IDs are allocated per session in
  blocks of 10–20 and mostly unused, and four independent extractions land at 487–496. Always sort
  the IDs into runs: contiguous within a session but jumping between sessions means block allocation.
  Conversely, where numbering *is* contiguous, the highest ID gives submitted-vs-published (DAE-SSPS
  524 published against 684 issued; AFA 360 posters published against 686 IDs issued).
- **"Papers" plus "Presentations" is usually double-counting.** SPIE Medical Imaging advertises
  "737 Papers, 353 Presentations"; 1,090 would clear the floor, but the presentations are recordings
  attached to papers already counted. Real figure 737.
- **Subject-filtered indexes return subsets, not totals.** INIS returns 18 papers for the Uzbek
  flagship only because it indexes by nuclear subject category. Never write a subset down as a total.
- **Indico has more than one host.** `indico.cern.ch/e/<slug>` may resolve to `indico.global`, and
  querying the export API on the wrong host returns an **empty result set rather than an error** —
  which reads as "no contributions". Confirm the host the event actually lives on.
- **Distinguish a bot wall from a dead network.** A 403/JS interstitial is rung 5 (a browser fixes
  it). A host that resolves but times out on every protocol is not — a browser fails identically, so
  do not queue it.
- **Domain lookalikes are live traps.** `aapmannualmeeting.com` is the American Academy of Pain
  Medicine, not medical-physics AAPM. `hkps.org.hk` is the Hong Kong *Psychological* Society, not
  the physics one. Confirm the domain belongs to the society before citing it.
- **A society's flagship may not be the society's.** Moldova's real recurring meeting (MSCMP) is run
  by the Institute of Applied Physics; Romania's "Conferința Națională de Fizică" belongs to CFMR, a
  medical-physics body. Those are Phase-1 gaps needing their own rows, not Phase-2 results.

## Status

| Field | State |
|---|---|
| Physical sciences | **Complete and fully re-verified (2026-09-10).** 55 census rows (28 VERIFIED, 27 BORDERLINE); 101 deleted rows, every one carrying a `Method` entry and 81 carrying an actual counted number (was 16). No duplicates in either direction. 6 rows remain queued for rung 5, and 2 are genuinely unreachable (Belarus: dead network; Russia: a Phase-1 gap naming no conference) |
| Medicine & health | Phase 1 complete (313 candidates over 3 sweeps). Phase 2 27% done: 34 VERIFIED, 51 BORDERLINE, 1 deleted, 227 NOT YET CENSUSED. **Not yet re-verified under the ~700 floor or the `Method` column** — both passes still to run |
| CS / AI / engineering | Not started — the selective-paper world (NeurIPS: 21,575 submissions) |
| Life sciences | Not started |
| Chemistry | Not started — ACS placeholder awaiting a decision |
| Social sciences | Not started |

### Model numbers as of 2026-09-10
SAM Global **112.15** (was 114.15 — the Iran and IPS duplicate fix is the only genuine model
movement of the run), SAM US **54.00**, SOM **32.00**. Every restoration and deletion is
model-neutral by construction, because the totals span both sheets.
