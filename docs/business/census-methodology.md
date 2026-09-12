# Conference census — reusable method

How to census one field's conferences for the TAM/SAM model in `tam-sam-som-v3.xlsx`.
Physical sciences (complete) and medicine & health (Phase 2 complete, attendance in progress)
were built this way.

**Where the work stands right now, and what to do next, is in `HANDOFF.md`.** This file is the
method only; it does not track progress.

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

## Seven rules

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
   **The one exception is rung 9**, and it is a bounded one (Rupert, 2026-09-12): when rungs 1–8
   have all failed, an abstract figure may be INFERRED from a sourced attendance number times a
   programme-type ratio. The attendance number itself still obeys this rule — it must be read off
   a page that actually loaded — and the inferred figure must carry the `NOT COUNTED` label
   wherever it is written. Everything else in this document still forbids estimating.
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
7. **Never take a shortcut. If the method requires a search you cannot make, REFUSE and stop.**
   This governs every number in this document — abstracts and attendance alike.

   The method is not a suggestion that degrades gracefully when a tool runs out. Rungs 1–8 and
   A1–A3 all *begin* with a search: search is what locates the countable artefact, or locates the
   page that states the attendance. With no search there is no method, only guessing dressed up
   as one.

   **When the WebSearch budget is exhausted, the correct output is a refusal, not a thin file.**
   Say plainly, to the user and in one line:

   > **The session's search limit is used up. The chat has to be restarted to proceed.**

   Then stop. Do not fill the rows in anyway. Do not substitute blind URL guessing, unaudited
   directory sites, a cached recollection, or a figure from a search snippet you never opened.
   Do not quietly lower the standard so the run *looks* finished.

   **Why this is a rule and not a preference:** a search-starved run does not produce fewer
   results, it produces *false* ones. Every unreachable row comes back `UNKNOWN` or null — and an
   `UNKNOWN` in this workbook means "we looked and the number is not published", which is a claim
   about the conference. A tooling block that masquerades as a finding corrupts the census in the
   one direction that is hardest to detect later, because the row looks researched. This was
   measured on 2026-09-11: with search exhausted, blind WebFetch against guessed society URLs
   returned **1 usable figure in 15 fetches (~7%)** — five 403s, five 404s, four pages carrying no
   number. Extrapolated over a 45-row slice: ~400 fetches, perhaps 5–8 real figures, and ~38 nulls
   that are artefacts of the tooling rather than facts about the meetings. **That file is worse
   than no file, because it looks like evidence and is not.**

   The same applies to any other blocked rung: a paywalled PDF is `CLICK TO CONFIRM`, not a
   guess; a browser-only count is a rung 5 queue entry, not an estimate. Refusing is the
   diligent outcome — it hands the user a decision they can act on in ten seconds (raise the
   budget, or restart the chat) instead of a file they have to audit row by row.

   **Check the budget BEFORE launching a wave, not after.** ~45 rows x 2 searches x 5 agents is
   ~450 calls against a default cap of 200, the cap is session-wide and shared by local *and*
   remote subagents, and an earlier phase in the same session can leave a wave with zero budget
   before it issues a single search. Raising it is Rupert's config change, never yours to make.

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

### Search in the conference's own language — mandatory, both phases

**An English-only search does not mean the figure is unpublished. It means you did not look.**
This has now bitten twice, in two different fields, and both times the missing rows were large:

- **Medicine, 2026-09-10.** A completeness pass reported 9 rows as unresearchable. Re-run with
  local-language queries, three of them turned out to have conferences the sheet claimed did not
  exist: Kazakhstan (~70 reports), Mongolia (43), and a co-organised Greater Bay Area congress in
  Macau. All were invisible to English-language searching alone.
- **Chemistry, 2026-09-12.** The Chemical Society of Japan's 106th meeting publishes **3,604
  presentations and 6,000+ participants** on its own news page — in Japanese. English queries
  returned nothing usable for one of the largest chemistry meetings in the world.

**The rule:** when a conference is run by a non-anglophone society, at least one query must be in
the society's working language, using the local term for the artefact. A row may only be marked
`UNKNOWN` once that has been tried — and the method text must say which language was searched.

| Language | Annual meeting | Abstract(s) | Attendance / participants |
|---|---|---|---|
| Japanese | 年会 / 大会 / 討論会 | 要旨 / 講演要旨集 / 発表件数 | 参加者数 |
| Chinese | 年会 / 大会 / 学术会议 | 摘要 / 论文集 / 报告数 | 参会人数 / 参加人数 |
| Korean | 학술발표회 / 총회 | 초록 / 초록집 | 참가자 수 |
| German | Jahrestagung / Tagung / Kongress | Beiträge / Kurzfassungen / Abstracts | Teilnehmerzahl / Teilnehmende |
| French | congrès / journées / réunion annuelle | résumés / communications | participants / congressistes |
| Spanish | congreso / reunión bienal | resúmenes / comunicaciones | participantes / asistentes |
| Portuguese | congresso / reunião anual | resumos / trabalhos | participantes |
| Italian | congresso nazionale / convegno | riassunti / contributi / comunicazioni | partecipanti |
| Russian | съезд / конференция | тезисы / тезисы докладов | участников |
| Polish | zjazd / kongres | streszczenia | uczestników |
| Turkish | kongre / kurultay | bildiri özetleri | katılımcı |
| Dutch | congres / jaarvergadering | samenvattingen | deelnemers |
| Nordic | møte / möte / kokous | sammendrag / abstrakt | deltakere / deltagare |

**Two practical notes.** Figures in these sources are often written in local numeral conventions —
German and Italian use `.` as the thousands separator (`3.604` is three thousand six hundred and
four, not 3.6), and Japanese and Chinese pages frequently write 件 (items) or 名 (people) after the
number. Read the unit, not just the digits. And a machine-translated page is fine to *read*, but
cite the original URL: the translation layer is not the source.

**Look for the national platform, not just the conference.** Non-anglophone countries tend to run
many societies' programmes through one shared platform or society meetings index. Finding that
platform once unlocks a whole national layer, so record it in the field's notes the first time you
meet it rather than rediscovering it per row.

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
the retention floor, the seven rules, the escalation ladder, the citation and `Method` discipline —
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

**Rung 9 is the attendance pass, not an abstract rung.** When the abstract ladder is genuinely
exhausted — or the artefact is paywalled and unreachable — the row goes to rung 9, which finds
attendance and programme character instead and refers the decision to Rupert. It is the only rung
that never decides. See *Rung 9 — the attendance pass* below.

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

**There are THREE deposit patterns, and the middle one was long mistaken for a dead end:**

| Pattern | Publishers | What to do |
|---|---|---|
| **Per abstract** | Elsevier, LWW, OUP (+ *Alzheimer's & Dementia*) | Count the items — this is the exact figure |
| **Per section** | Wiley on several titles | **Enumerate the volume/issue and SUM the sections.** RACS = 27 DOIs totalling 226 pages; ECTRIMS = 8 DOIs totalling 1,528 |
| **Whole supplement, one DOI** | Springer, Karger, Liebert, Sage, Thieme, Cell Press, AAPM | No count available — but read its `page` field for the extent |

Always query the volume *and* issue before concluding a publisher "doesn't deposit": a single-DOI
lookup that returns `page: '3-4'` is not a lumped supplement, it is **one section of many**, and
summing them reconstructs the whole thing.

**Read the page extent off the lumped DOI — it is free.** Even when nothing is countable, the
supplement's own Crossref record carries its page range: ESMRMB returns `1-889`, IARS `1-1247`,
ICEM `1-234`, SSO `1-310`. No browser, no paywall, one API call.

**Extent is TRIAGE, NOT A COUNT.** Calibrated against rows where both are known, the ratio runs
**0.64 abstracts per page** (Radiotherapy and Oncology) to **2.18** (Toxicology Letters) — a 3.4x
spread, because journals differ in how many abstracts they set per page. So 889 pages brackets to
roughly 570-1,940, which straddles both the floor and the bar. Use extent to decide which paywalls
are worth breaking; never write it as the figure.

**PubMed and Europe PMC are a confirmed dead end for this purpose, and now for the right reason:**
they *systematically exclude* meeting-abstract supplements. Europe PMC returns 312 items where
Crossref has 695 (SGO), and 452 where Crossref has 2,823 (ESTRO). Strictly worse than Crossref —
do not retry it hopefully. For those, two workarounds beat the paywall before you resort
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

## Rung 9 — attendance converted to abstracts (the last rung of the ladder)

**Changed 2026-09-12 by Rupert.** Rung 9 used to sit outside the ladder as a non-deciding
referral packet. It is now **the ninth and final rung of the abstract ladder, inside Phase 2**:
when rungs 1–8 fail to produce a countable artefact, rung 9 finds the attendance figure, judges
what kind of programme the meeting runs, and converts attendance into an approximate abstract
number. That number decides whether the row is large enough for the approved list.

The purpose is completeness, not precision. Rupert's framing: *"We don't need exact abstract
numbers. What we really need is approximate numbers, so we can get all of the conferences that
are large enough on the list, and the ones that are not large enough on the removed list."*

**The four constraints that keep this honest:**

1. **The attendance figure must be real.** Read off a page that actually loaded, with its basis
   tag and the rung that produced it. Only the *conversion* is approximate. A snippet is not a
   source (see rule 7 and "What rung 9 must never do" below).
2. **The inferred figure goes in the Abstracts column, labelled.** Write it as
   `~N INFERRED FROM ATTENDANCE, NOT COUNTED (rung 9 — <attendance> x <ratio> for a
   <programme type> programme) — see Method column. PRIOR: <what the cell said before>`.
   A figure an organiser merely states, with no artefact behind it, is labelled
   `~N REPORTED BY SOURCE, NOT COUNTED` instead. The prior cell text is preserved, never erased.
3. **Rungs 1–8 outrank rung 9.** A row that already carries a counted figure is never overwritten.
4. **Inferred figures are excluded from the ratio calibration**, or the ratio feeds on its own
   output and becomes self-fulfilling. The `NOT COUNTED` marker is what makes this mechanical:
   `attlib._counted()` returns `None` for any cell carrying it.

Rung 9 exists because abstracts turned out to be unrecoverable for a large slice of medicine.
The decisive test across 26 blocked rows carrying a Crossref handle returned **2 countable,
23 extent-only, 1 no handle**. Behind those paywalls is a PDF that needs a subscription, and
no metadata route substitutes for opening it. So for the ~70 blocked rows, the ~26 with no
artefact at all, and any row where the abstract ladder is exhausted, attendance plus character
is the evidence Rupert decides on.

### Why this ladder is shaped differently

**Do not copy the abstract ladder.** Abstracts are almost never stated, so that ladder was about
locating a countable artefact and then counting it. **Attendance is almost always stated
somewhere.** The problem is the opposite one: many numbers exist, of wildly differing honesty,
counting different things. So the attendance ladder ranks sources by **how much the source had
to answer for the number**. It is a credibility ladder, not a counting ladder.

The practical consequence: rung 1 was near-useless for abstracts; **here search is the workhorse**.
Expect most rows to resolve at A1–A3 in one or two searches.

### The ladder

| Rung | Source | Why it ranks there |
|---|---|---|
| **A1** | **Exhibitor / sponsor prospectus** — search `"<conf>" exhibitor prospectus attendee demographics filetype:pdf`, or `"<conf>" "why exhibit"` | Highest yield AND highest accountability: exhibitors pay real money against these figures, and they are usually broken down (delegates vs exhibitors vs country) |
| **A2** | **Post-meeting report / "congress by the numbers" / society annual report** | Retrospective; often gives the actual figure against A1's projection. **Prefer A2 over A1 when both exist and disagree** |
| **A3** | **Society press release / newsroom / trade-press coverage of that edition** | Cheap, usually one round number, no breakdown |
| **A4** | **Venue / convention bureau / ICCA / economic-impact study** | Independent of the society. Good corroboration; may report *bid* size rather than actual |
| **A5** | **Programme-platform artefact** — participant directory, badge/ID ranges, app attendee list | The only rung that COUNTS rather than reads. Browser-only, reserved to the orchestrator — agents return `A5` with a null figure and say what to open |
| **A6** | **Proxy arithmetic** — parallel sessions × room capacity, exhibition floor sqm, exhibitor count | Order-of-magnitude ONLY, and must be flagged as an estimate in the method text |
| **A7** | **Prior year / sister meeting** | Carry a nearby year's figure, stating the year explicitly |

### Three rules that matter more than the rungs

**1. Every number carries a BASIS tag.** `12,177` is meaningless without knowing whether it counts
delegates only, or delegates + exhibitor staff + press + virtual. Tags: `DELEGATES`,
`TOTAL_ONSITE`, `TOTAL_INC_VIRTUAL`, `UNSPECIFIED`. If the source does not say, the tag is
`UNSPECIFIED` — never guess. This is the single most abused number in the whole census.

**What the basis tag is NOT for** (Rupert, 2026-09-12). Two things that look like disqualifiers are
explicitly NOT disqualifiers:

- **Virtual and online participation counts.** The product is a matching system, and an abstract
  presented online is exactly as matchable as one presented in a room. A `TOTAL_INC_VIRTUAL` figure
  is not to be discounted for being virtual. This is why Japan Medical Congress, whose only figure
  is ~540,000 including online participation, is converted rather than refused.
- **Attendee type is irrelevant.** Students, trainees, allied health, industry scientists — a
  presenter is a presenter. Never discount a meeting for having the "wrong sort" of attendees.

The tag exists for one purpose only: so the *number* can be read correctly. Discount a headcount
only where the people counted **cannot submit an abstract at all** — exhibitor booth staff, trade
-show visitors, accompanying persons. That is a statement about who submits, never about who counts
as a real scientist.

**The corollary, which bit on 2026-09-12:** if a meeting is judged small, the reason must be that
*little contributed science happens there*, never that its attendees are the wrong kind. Chicago
Dental Society Midwinter Meeting is the worked example: 30,000+ attendees, briefly included on the
"students count too" principle, then correctly left out — not because the presenters are students,
but because the only contributed science is one poster session, so even a generous 2% gives ~600
against a ~1,000 bar.

**2. Record disagreement; do not resolve it.** If the prospectus says 15,000 and the press release
says 11,400, keep both — headline = the more accountable rung, the rest in `alt_figures`.
The spread IS a finding: it measures that society's marketing inflation. **Never average.**

**3. Stop at the first rung that yields a figure with a basis.** Cap: **2 searches per row**, 3 for
a genuinely hard one. The conversion below is approximate by design, so a second corroborating
figure rarely changes the answer — spend the search on the next row instead.

### The conversion — attendance to abstracts

**There is no band table and no default ratio. Do not hard-code one** (Rupert, 2026-09-12). For
every row, the agent judges *this conference's* ratio from the wording it actually found, states it
as a percentage, and says what justifies it. A ratio that arrives without its reasoning is rejected
(`attlib.check_ratio()` enforces both, plus a 2%–200% plausibility range).

The question to answer per conference: **what share of the people in the room submitted something?**
Read it off the programme's own wording — is the meeting built on an open call, or on invited
faculty and courses? Does the abstract deadline page read like the spine of the event or like a
sideshow? Is the headline headcount padded with exhibitor staff, industry, virtual viewers?

`implied abstracts = attendance x the judged ratio`. Round it; never carry decimals into the sheet.

**NO SHORTCUTS ON THE CONVERSION** (Rupert, 2026-09-12). The anchors below are *reference material*,
never a lookup table. You may consult them, an industry rule of thumb, or the same conference's
figure from a previous year — but the ratio you write down must be a judgement about **this
conference**, reached by reading what this conference says about itself. Copying a comparable's
percentage across because the two meetings are in the same field is a shortcut and is not allowed;
neither is reusing the field median because a row is hard. If the evidence is thin, say so in
`ratio_rationale` and give the figure you actually believe — an honest uncertain number is usable,
a borrowed confident one is not.

**Anchor the judgement against real counted rows, don't guess in a vacuum.** Run
`attlib.ratio_rows(sheet='Census - <Field>')` at the start of a wave: it returns every row in that
field carrying BOTH a counted abstract figure and an attendance figure, which are the only ratios
anyone has actually observed. Read them, then judge the conference in front of you.

Name the comparable you reasoned from in the row's Method cell: *"judged 25%, against two counted
oncology congresses of similar shape at 21% and 25%."* That sentence is what makes the row
auditable later — and it belongs in the workbook beside the figure, not in this document.

**Every field starts its own anchor set and borrows from none.** Fields converge at very different
rates, so an anchor from the wrong field is worse than no anchor at all.

**Do not copy anchor numbers into this document — generate them.** `attlib.ratio_rows(sheet=...)`
returns every row in that field carrying BOTH a counted abstract figure and an attendance figure,
computed live from the workbook. A list written down here goes stale the moment a row gains a
number; a generated one improves with every verified row. **Record the specific anchors you
reasoned from in the row's own Method cell** — and only the ones you actually used. That way the
justification sits next to the number it justifies, where anyone checking the row will find it.

**Discount an inflated headcount before converting, or say you didn't.** EUROSPINE's 3,809 headline
contains 1,478 industry representatives; converting the headline instead of the 2,331 delegates
would overstate that row by 63%. Virtual-inclusive and exhibitor-inclusive totals inflate the same
way.

**Treat the result as an order of magnitude, not a measurement.** The medicine spread is ~25x end to
end, so a single row can be wrong by 3x either way. It is good enough to sort large from small,
which is all it is for.

**A figure stated by a source beats any ratio.** If the attendance pass turns up an organiser saying
"nearly 2,000 abstracts", use it, label it `REPORTED BY SOURCE, NOT COUNTED`, and note whether it
counts submissions (higher) or accepted papers (lower).

#### What the ratio is NOT (Rupert, 2026-09-12)

**Do not go hunting for an exact number to back-derive the ratio.** That is the failure mode here:
an agent decides it must find "the real abstract count" to justify a percentage, spends its search
budget chasing a figure rungs 1–8 have already failed to find, and ends up either empty or
asserting something it cannot source.

The ratio is **a qualitative read of the conference** — the agent reads about the meeting, takes in
the context (numbers that happen to appear are part of that context, not the object of the
exercise), and forms a judgement: this looks *majority-abstract*, or *minority-abstract*, or
somewhere between. In Rupert's words: **"an imperfect science, a gut feel from the LLM."**

That is acceptable *because* the output is labelled `NOT COUNTED` everywhere it appears, and
because the bar it feeds (~1,000) only has to sort large from small. What is NOT acceptable is
dressing that judgement up as precision, or spending a row's whole search budget trying to make it
precise. Read, judge, state the reasoning, move to the next row.

### The bar for the approved list

**~1,000 implied abstracts** (Rupert, 2026-09-12) — deliberately below the ≥1,500 counted bar,
because an inferred figure is coarse and the aim is to catch every conference that is plausibly
large. Above it the row stays on `Census - <Field>`; below it the row belongs on
`Deleted - <Field>`. A row straddling the bar between its band and the next one up is recorded as
`BORDERLINE` in `Rupert's call` and left for him.

**A row with no attendance figure at all is never moved to the removed list.** No evidence of size
is not evidence of small size (rule 1); those rows stay put and go back in the queue.

### Resolving a row that lands near the bar (Rupert, 2026-09-12)

A hard cutoff at 1,000 would be false precision on top of an estimate, so a row near the line gets a
sensitivity test instead of a coin flip. `attlib.resolve_borderline()` applies it; **either test
includes the row**:

1. **Within 100 of the bar.** A figure of 900 or more counts as clearing 1,000.
2. **Flex the ratio and see if it reaches.** Vary the judged ratio up and down, and if the top of
   that band reaches 900, include the row. This measures the error in the judgement: if a small,
   defensible change of mind about the conversion rate flips the answer, the row deserves the
   benefit of the doubt.

**The flex is RELATIVE (±20%), never percentage points.** 25% flexes to 20–30%. Adding *points*
would rescue precisely the rows that should fail: a 2% CE-and-trade meeting flexed by +5 points
becomes 7%, a 3.5x change that drags it over the bar on arithmetic alone. Chicago Dental Midwinter
is the live example — ~600 at 2%, and 720 at the top of its relative band, so it stays out.

**A figure a source stated is not flexed.** There is no judged ratio behind it to vary, so it faces
only test 1. WOC's reported 800 posters therefore fails, though the log notes that orals are not in
that 800 — a real count could still overturn it.

Record the band (`low`–`high`) and which test decided it in the Method column, so the call can be
re-checked without redoing the reasoning.

### The upgrade sweep — rescuing rows from the removed list

**Run this as the final sweep, after the main rung-9 pass** (Rupert, 2026-09-12). Rows landed on
`Deleted - <Field>` for two very different reasons, and only one of them is reversible here:

- **Deleted because a counted figure came in under the bar** — leave it alone. A counted number
  outranks any rung-9 estimate; do not "rescue" it with arithmetic.
- **Deleted because no abstract count could be found** — this is the upgrade candidate. Run rung 9
  on it. If the resulting approximate figure reaches the ~1,000 bar, **move the row back onto
  `Census - <Field>` automatically**, without asking. That is the whole point of the sweep.

`attlib.upgrade_rows()` performs the move and is the only sanctioned way to do it, because three
things have to happen together or the workbook quietly breaks:

1. **The row lands as `BORDERLINE`, never `VERIFIED`.** Nothing was counted for it. `VERIFIED`
   means a published count ≥1,500 seen on a page, and an upgraded row has no such thing.
2. **The totals block must be widened.** The census totals carry FIXED ranges (`N5:N257`) and
   openpyxl re-points nothing on insert. A row appended past the range end sits outside every
   total, silently — the row looks present and counts for nothing. `_widen_totals()` extends the
   ranges to cover the new row.
3. **The history travels with the row**: when it was deleted, why it was deleted, and its prior
   method text, all preserved in the Method column ahead of the new rung-9 log. A row that has been
   out and back must be able to explain both trips.

A row is refused an upgrade if its figure is under the bar, or if its ratio arrives without
reasoning (`check_ratio()`).

**Report every upgrade in a table in chat** — conference, attendance and its source, the judged
ratio and why, the resulting figure, and the old deletion reason — so Rupert can vet the moves.
This step carries more error risk than anything upstream: it is the only place where an estimate
changes which list a conference sits on. Never report an upgrade count without the table behind it.

**A known inconsistency to watch.** The counted bar is ≥1,500 but the inferred bar is ~1,000, so a
row with a *counted* 1,200 stays removed while a row with an *inferred* ~1,100 gets upgraded — the
better-evidenced row treated more harshly. One row is currently affected: EUROTOX / ISES joint
meetings, counted 1,075, on `Deleted - Medicine & Health`. Flag it; do not silently fix it.

### Programme character — the second signal

Strongest single discriminator: **does an open call for abstracts exist?** A submission deadline
page, author guidelines, a "submit your abstract" CTA.

- abstract book exists + open call → `CONTRIBUTED`
- no call, invited-speaker programme, CME / live-case / hands-on-course framing → `CURATED`
- both, or a small call bolted onto a taught programme → `HYBRID`
- nothing found → `UNKNOWN`

**A counted abstract figure settles character at zero search cost** — an open call necessarily
produced those abstracts. `attlib.character_from_abstracts()` does this mechanically; it
classified 144 of 252 medicine rows without a single search. Only spend effort where the
abstracts column is UNKNOWN or blank.

**EuroPCR is the worked example**: 12,177 attendees against 743 counted abstracts. Without the
character signal that row reads as a giant contributed congress; it is a teaching and live-case
course. Attendance alone will mislead you — that is why character is not optional.

Once attendance and abstracts both exist, the **abstracts : attendance ratio** separates the two
kinds directly. Slice queues so each agent gets a mix of counted-abstract and UNKNOWN rows: the
counted rows calibrate the ratio, and without that calibration a bare attendance figure on an
UNKNOWN row cannot be read.

### Budget — settle this BEFORE launching

A full wave (~45 rows × 2 searches × 5 agents) needs **~450 WebSearch calls against a default cap
of 200 per session**. The cap is session-wide and **shared by local *and* remote subagents**, so
fanning out buys nothing, and a phase run earlier in the same session can leave a later wave with
zero budget. Ask Rupert to set `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` (~1000) or run the wave
in a fresh session. Never edit that setting yourself.

**Do not substitute a degraded method to avoid asking — this is rule 7, and it is a refusal, not a preference.** This was measured, not guessed: with
search exhausted, blind WebFetch against guessed society URLs yielded **1 usable figure in 15
fetches (~7%)** — five 403s, five 404s, four pages carrying no figure. Extrapolated, ~400 fetches
for maybe 5–8 real numbers and ~38 nulls that are artefacts of tooling rather than findings about
the meetings. Per rule 2 below, that file is *worse than no file*: it looks like evidence and is
not. Search-engine result pages fetched through WebFetch are also not a workaround — DuckDuckGo
returns a CAPTCHA and Mojeek returns 403.

Unaudited conference-directory sites (10times and similar) are fetchable and cover nearly every
row, but their numbers are self-reported and sit below A4. Do not use them without Rupert's
explicit word, and if used, tag every such row `confidence: LOW`, basis `UNSPECIFIED`.

### NON-NEGOTIABLE — a rung-9 abstract number is an APPROXIMATION and must say so

This is the rule most likely to cause real damage if it slips, because an unlabelled estimate is
indistinguishable from a counted figure six months later, and the whole census is built on the
promise that every number is re-derivable from its source.

**A rung-9 abstract figure is NOT ACCURATE. It is arithmetic on a headcount, not a count of
anything.** Wherever such a figure appears — spreadsheet cell, agent JSON, report, chat summary,
slide — it carries, in the same breath as the number:

- the words **`NOT COUNTED`**, plus `INFERRED FROM ATTENDANCE` or `REPORTED BY SOURCE`;
- the inputs that produced it: the attendance figure, the ratio, and the programme type;
- a `~` before the number. Never write a rung-9 figure as a bare integer.

Never round a rung-9 figure to false precision (`~2,900`, not `2,872`, in prose). Never let one
into the `Abstracts (exact, as published)` column unlabelled — that column's name is a promise.
Never quote one in a total, a TAM/SAM figure or a sentence to Rupert without repeating that it is
inferred. Never let one be re-used as an input to the ratio calibration. If you are ever unsure
whether a number in the sheet was counted or inferred, that is the failure this rule exists to
prevent: check the `NOT COUNTED` marker.

### What rung 9 must never do

1. Never overwrite a counted figure from rungs 1–8, and never change a Tier directly — Tier is the
   record of the *abstract* test. Rung 9's verdict goes in `Rupert's call` and the Method column,
   and list membership is expressed by which sheet the row sits on.
2. Never report a figure not seen on a page actually loaded. A number asserted only in a search
   snippet is not evidence. Four rows in this workbook already assert figures their own cited
   sources do not contain — do not add a fifth.
3. Never present an inferred figure as a counted one. See the NON-NEGOTIABLE section above.
4. Never carry forward a number already in the sheet as if it were a finding. "Carried forward"
   is not a method.
5. Absence of evidence is not evidence the meeting is small — say so explicitly in the method text,
   and leave the row where it is.

### Columns and writeback

Rung 9 writes only these, on `Census - <Field>`:

| Col | Field |
|---|---|
| G | `Abstracts (exact, as published)` — ONLY the labelled rung-9 figure, and ONLY where no counted figure exists. Prior text preserved after `PRIOR:` |
| J | `Attendance` — as published, with the year |
| K | `Attendance source (click)` — the page the number is ON, never a search page |
| T | `Method` — the full audit log, appended after any existing method text: decision, attendance + basis + rung + URL, programme type and its evidence, the ratio, the bar, and the statement that the abstracts column holds an inferred figure |
| V | `Attendance basis` — DELEGATES / TOTAL_ONSITE / TOTAL_INC_VIRTUAL / UNSPECIFIED |
| W | `Attendance rung + how` — which rung PRODUCED it, plus any DISAGREEMENT block |
| X | `Programme character` — CONTRIBUTED / CURATED / HYBRID / UNKNOWN |
| Y | `Rupert's call` — INCLUDE / BORDERLINE / BELOW BAR, dated, with the figure and the bar |

`scratchpad/attlib.py` (tests in `scratchpad/test_attlib.py`, TDD) does the writeback. It credits
**only the rung that produced a figure**, never the highest rung reached; renders disagreement
without averaging; and **re-anchors every record by conference name** via `remap()`, because agent
row numbers go stale the instant any row is deleted. Agents return JSON and never touch the
workbook. Per-row agent contract: `row`, `conference` (echoed verbatim for re-anchoring),
`attendance`, `attendance_numeric`, `attendance_year`, `attendance_basis`, `attendance_rung`,
`attendance_rung_name`, `attendance_source_url`, `attendance_method`, `alt_figures[]`,
`character`, `character_evidence`, `confidence`, `searches_used`, plus the conversion fields
`programme_type`, `programme_evidence`, `direct_abstracts` (a figure a source states, else null),
**`ratio`** (judged for this conference, as a decimal) and **`ratio_rationale`** (what about this
conference puts it at that ratio, naming the counted comparable reasoned from). Both are mandatory
on any row with an attendance figure; `check_ratio()` rejects a bare ratio with no reasoning.
The orchestrator — never the agent — computes `implied`, writes the labelled abstracts cell via
`write_inferred_abstracts()` and the audit log via `log_inclusion()`.

### Reporting

Always report **counted** events/yr (rows with a real abstract count) separately from **inferred**
events/yr (rows admitted on a rung-9 estimate). Never merge them into a single headline number:
the whole point of the `NOT COUNTED` marker is lost if the two are added together silently. State
the ratio and the bar alongside any inferred total, and name the rows still awaiting evidence.


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
- `Abstracts (exact, as published)` means exactly that: a counted figure off a real artefact. The
  only other thing allowed in it is a rung-9 figure carrying `NOT COUNTED` — see the
  NON-NEGOTIABLE section under rung 9.
- **SAM = every conference on the approved (census) sheets of medicine AND physical sciences,
  minus everything on the `Deleted - <Field>` sheets** (Rupert, 2026-09-12). This replaces the old
  "SAM is physical sciences only" rule. Membership of the approved list IS the inclusion
  mechanism — no switch column, no separate override file, no parallel list.
  **Not yet wired:** the Summary sheet still computes SAM from the `Include (1/0)` column across
  the physical-sciences census AND deleted sheets — so it currently counts ~62 events/yr of
  *removed* conferences and no medicine at all. Fixing that formula is a pending change.
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
| Medicine & health | **Phase 2 and rung 9 both COMPLETE (2026-09-12).** 252 census rows: 144 carry a counted abstract figure, 86 carry a rung-9 estimate labelled `NOT COUNTED`, 22 have no figure of any kind. Rung-9 calls: 42 INCLUDE, 44 BELOW BAR, 10 of them personally vetted by Rupert. 56 deleted rows, all now carrying attendance where one exists. The upgrade sweep produced **no upgrades**: of 5 candidates, 3 convert far below the bar (Yankee Dental ~95 on 19,084 attendees, Arab Health ~33, ACR ~24) and 2 yielded no figure |
| CS / AI / engineering | Not started — the selective-paper world (NeurIPS: 21,575 submissions). **Needs a bar redefinition before a census**: papers-with-acceptance-rates do not map onto "1,500 abstracts" |
| Life sciences | Not started. Partly pre-empted: SfN, ASM, ESHG and others already sit in the medicine census |
| Chemistry | **Phase 1 running (2026-09-12).** The richest uncounted pool left: ACS Spring+Fall alone run ~12,000–16,000 abstracts each and sit as ONE physical-sciences row with abstracts UNKNOWN. Dedup against physical sciences (ACS, MRS, E-MRS, SciX) before trusting any total |
| Earth sciences | Effectively done inside physical sciences — AGU (25,000+) and EGU (18,896) are the field |
| Social sciences | Not started |

### Settled by Rupert, 2026-09-12 — do not reopen without him

- **The unit is ACCEPTED contributed presentations: orals + posters.** Not submissions (an upper
  bound including rejects), not posters alone (a lower bound missing the orals).
- **Invited speakers are NOT counted.** Measured on this workbook's own data: invited programmes
  run 2–16% of abstracts at real research congresses, but 2–10x the abstracts at teaching and
  trade events — so counting them would admit exactly the meetings the bar exists to exclude.
  BIO International is the worked example: ~108 abstracts, 1,100 invited speakers, no call for
  abstracts at all; counting invited would clear it over a 1,000 bar. Most sources also say
  "speakers" rather than "invited speakers", and that figure usually already contains the abstract
  presenters — adding it double-counts the same people.
- Consequence to accept knowingly: the bar measures *contributed science*, not *total matchable
  content*. Those come apart at teaching-heavy meetings. That is a product question, not a data
  fault.

### Next action
Chemistry phase 1 — discovery, names only, cast as wide as possible; then phase 2 over the
candidate list. After that: physical-sciences attendance (rung 9), which Rupert has asked for,
and the ~80 medicine rows whose rungs 1–8 came back empty before the exhibitor-prospectus route
was known.

### Open, awaiting Rupert
1. **The abstract ladder has a hole.** Five medicine rows turned up PUBLISHED abstract counts that
   rungs 1–8 missed because they sit in exhibitor prospectuses, not supplements: AANS 3,778,
   IADR 2,949, ORS 2,353, EBMT 1,324, UICC 1,200 — the first three clear the 1,500 counted bar
   outright. Add that route as a rung and re-run it over the rows that came back empty.
2. **Counted bar 1,500 vs inferred bar 1,000** punishes the better-evidenced row. One row affected:
   EUROTOX / ISES, counted 1,075, still on the deleted sheet.
3. **Summary SAM formula does not implement Rupert's definition** — it reads `Include (1/0)` across
   the physical-science census AND deleted sheets, so it counts ~62 events/yr of removed
   conferences and no medicine at all.
4. **Identity collisions**: ACCP is two societies (pharmacology ~546 vs pharmacy, much larger);
   ASRA runs two annual meetings and the row names neither. **Renamed**: IPRAS→ICOPLAST,
   ETS→ECTES, SmileCon→ADA Scientific Session, ATA→ATA Nexus; CMDA holds no single meeting.

### Model numbers as of 2026-09-10
SAM Global **112.15** (was 114.15 — the Iran and IPS duplicate fix is the only genuine model
movement of the run), SAM US **54.00**, SOM **32.00**. Every restoration and deletion is
model-neutral by construction, because the totals span both sheets.
