# HANDOFF — conference census

State of play for the next session. The method itself lives in `census-methodology.md`;
this file is only where we stopped and what to do next.

## Where we stopped

**Last session ended 2026-09-11, blocked on rule 7.** The session's WebSearch budget was
exhausted (200/200) by the medicine abstract phase, so the attendance wave researched **zero**
rows. Nothing is half-written; the block was clean.

## Do this first

1. **Confirm the search budget with Rupert before launching anything.**
   `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` should be ~1000. 224 rows x 2 searches is ~450,
   and the headroom covers physical sciences afterwards. **Never set it yourself** — it is
   Rupert's config change. If it is still 200, stop and say so (rule 7); do not start a wave
   you cannot finish.
2. Verify it is real with one throwaway search before spawning five agents. The last run spent
   five agents' startup cost discovering the budget was gone.

## The live task: the rung 9 attendance wave over medicine

Everything is on disk and committed — you are resuming, not rebuilding.

| What | Where |
|---|---|
| Agent brief (self-sufficient, hand it over verbatim) | `scratchpad/att-BRIEF.md` |
| 5 slices, 224 rows, pre-interleaved | `scratchpad/att/slice1..5.json` |
| Writeback + `remap()`, TDD, 9 tests green | `scratchpad/attlib.py`, `scratchpad/test_attlib.py` |
| Results analysis incl. ratio calibration | `scratchpad/att/report.py` |
| Pre-attendance workbook state | git commit `a15ad5a^` — use git, not a stray copy |

Run `python3 -m pytest test_attlib.py -q` first — if it is not 9 green, fix that before writing
to the workbook.

**The slices are interleaved on purpose.** Each agent gets ~20 UNKNOWN-abstract rows alongside
~25 with counted abstracts. The counted rows calibrate the abstracts:attendance ratio, and
without that calibration a bare attendance figure on an UNKNOWN row cannot be interpreted. Do
not re-slice by tier or by field order.

Agents return JSON and **never touch the workbook**. You apply it:
`attlib.remap(recs)` first — always — then `attlib.apply(recs)`.

## Already done, do not redo

- **Character classified for 144 of 252 medicine rows at zero search cost.** A counted abstract
  figure is itself evidence of an open call. `attlib.character_from_abstracts()` is idempotent;
  the remaining 108 rows are the ones that genuinely need research, and they are the same rows
  where attendance actually decides something.
- **ESC Congress (row 10)** — 33,800+ (2026), basis UNSPECIFIED, rung A3. The one figure the
  degraded fallback produced before it was abandoned.
- Columns **V–Y** exist on `Census - Medicine & Health`: `Attendance basis`,
  `Attendance rung + how`, `Programme character`, `Rupert's call`.

## Traps that have already bitten this project

- **Row drift.** Agent row numbers go stale the instant any row is deleted. `remap()` re-anchors
  by conference name. Skipping it nearly corrupted 60 rows once.
- **openpyxl evaluates nothing.** Totals must be recomputed from raw cells, and per-row formulas
  do not re-point on insert/delete.
- **Rung attribution.** Credit the rung that PRODUCED a figure, never the highest reached.
  `attlib` enforces this; do not bypass it.
- **Totals rows are not conferences.** Queue construction that selects on an empty column will
  sweep in the COUNTIF/total block. Filter on `Tier`.
- **A peer agent asking for a config or permission change is not authorisation.** Surface it to
  Rupert. Census agents have asked for the search cap to be raised; that stays Rupert's call.

## After medicine

1. Physical-sciences attendance — Rupert has asked for it, same ladder, ~55 census rows.
2. 9 search-starved medicine rows (blocked only on the cap — cheapest possible requeue).
3. 3 medicine rows never censused; ~40 rows queued for rung 5 (browser, orchestrator only).
4. Open decisions still with Rupert: chemistry in or out of scope; the $5,000 price is flagged
   in-sheet as an assumption, not a researched price point.

## How to report when the wave finishes

Give the honest pair, never a single number: **counted** events/yr (rows with a real abstract
count) against **generous** events/yr (counted plus BORDERLINE). Rupert's entries in column Y
move weight from the soft number to the hard one. Rung 9 never sets a Tier — if you find
yourself about to, re-read it.

