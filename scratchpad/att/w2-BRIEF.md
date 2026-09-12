# Rung 9 — attendance converted to approximate abstracts. Agent brief (wave 2, medicine).

You are finding **attendance** figures for academic/medical conferences, and then making a
**judgement call** about what share of those attendees submit an abstract.

You do NOT count abstracts. You do NOT decide a row's fate. You do NOT touch the workbook.

## Why this exists

Rungs 1–8 of the abstract ladder already failed on every row in your slice: no abstract book, no
journal supplement, no programme PDF, nothing countable. Rung 9 is the fallback. Attendance is
almost always published somewhere, so we find that, then reason from it.

## Part 1 — find the attendance figure

This is a **credibility ladder**, not a counting ladder. Many numbers exist, of wildly differing
honesty, counting different things. Rank sources by how much the source had to answer for the
number:

- **A1 — Exhibitor / sponsor prospectus.** Search `"<conference>" exhibitor prospectus attendee
  demographics filetype:pdf` or `"<conference>" "why exhibit"`. Highest yield and highest
  accountability: exhibitors pay real money against these figures.
- **A2 — Post-meeting report / "congress by the numbers" / society annual report.** Retrospective.
  **Prefer A2 over A1 when both exist and disagree** — a projection is not a count.
- **A3 — Society press release / newsroom / trade-press coverage of that edition.**
- **A4 — Venue / convention bureau / ICCA / economic-impact study.** Independent of the society.
- **A5 — Programme-platform artefact.** Browser-only. **Do not attempt.** Return
  `attendance_rung: "A5"`, a null figure, and say what to open.
- **A6 — Proxy arithmetic** (sessions x room capacity, exhibition sqm). Order-of-magnitude only;
  flag as an estimate.
- **A7 — Prior year / sister meeting.** State the year explicitly.

**Rules that matter more than the rungs:**

1. **Every figure carries a BASIS tag**: `DELEGATES` | `TOTAL_ONSITE` | `TOTAL_INC_VIRTUAL` |
   `UNSPECIFIED`. If the source does not say, it is `UNSPECIFIED`. Never guess.
2. **Record disagreement, never average.** Prospectus says 15,000 and the press release says
   11,400? Headline = the more accountable rung, the other in `alt_figures`. The spread is a
   finding.
3. **Stop at the first figure with a basis. Hard cap: 2 searches per row**, 3 for a genuinely hard
   one. Prefer opening a promising URL over another search.
4. **Never report a figure you did not see on a page you actually loaded.** Search-result snippets
   assert numbers that are not on the cited page — this has already happened four times in this
   workbook. If the snippet says it, open the page and confirm. If the page 403s or the figure
   isn't there, the figure does not exist for our purposes. Say so in `attendance_method`.
5. If nothing is found: `attendance_numeric: null`, and say which rungs you tried and why each
   failed. **Absence of evidence is not evidence the meeting is small — write that sentence.**

## Part 2 — judge the conversion ratio (the part that needs your judgement)

**This is a qualitative read, not a number to hunt down.** Do NOT go looking for an exact abstract
count to back-derive a ratio: rungs 1–8 already failed at that, and chasing it burns your budget
and tempts you into asserting things you cannot source. Rupert's framing: *"an imperfect science, a
gut feel from the LLM."*

Read what the conference says about itself — programme pages, session types, the call for abstracts
(or the absence of one), what the exhibitor material brags about — and answer one question:

> **What share of the people in that room submitted something?**

Then state it as a percentage, and say what made you land there. Numbers you happen to encounter
are context for that judgement, not the object of it.

**Anchor against real counted conferences** (medicine rows where we have BOTH a counted abstract
figure and an attendance figure — these are facts, not guesses):

```
EuroPCR 6%   (teaching and live-case course — attendance says nothing about submitted science)
PAS 9%   |  AAD 9%  |  RSNA 11%  |  ASHP 12%  |  ESC 15%
ERA 21%  |  ASTRO 21%  |  SABCS 21%  |  EASL 24%  |  WCLC 25%
UEG 35%  |  ASN 35%  |  DDW 37%  |  ESCMID 40%  |  SOT 46%
ECR 48%  |  ATS 50%  |  AAIC 50%
GSA 119% |  ESPGHAN 155%   (small specialty meetings where nearly everyone presents)
```

Name the comparable you reasoned from: *"judged 25%, against SABCS 21% and WCLC 25%, both oncology
congresses of similar shape."* That sentence is what makes your row auditable later.

**Two traps:**

- **Discount an inflated headcount before converting.** EUROSPINE's 3,809 headline includes 1,478
  industry representatives who never submit; the delegate count is 2,331. Converting the headline
  would overstate that row by 63%. Virtual-inclusive totals inflate the same way. If you convert a
  padded number because no clean one exists, say so.
- **A figure a source states beats any ratio.** If you find an organiser saying "nearly 2,000
  abstracts", put it in `direct_abstracts` and note whether it counts submissions (higher) or
  accepted papers (lower). Do not spend extra searches trying to find one.

Valid ratios run 0.5%–200%. A ratio without reasoning is rejected by the orchestrator.

### Your ratio gets a sensitivity test, so judge it honestly

The orchestrator flexes your ratio by ±20% relative (you say 25%, it also tries 20% and 30%) and
includes the conference if the top of that band reaches within 100 of the ~1,000-abstract bar.

What this means for you: **do not shade your ratio to push a conference over or under the line.**
The band does that work, and shading corrupts it. State the percentage you actually believe, and if
you are torn between two readings — say a taught programme with a real poster stream that could be
15% or 30% — say so in `ratio_rationale` and give the figure you find most likely. Your honest
uncertainty is more useful to the decision than a confident number.

Two things NOT to do:
- Do not discount a headcount for being virtual/online, or for containing students, trainees or
  allied-health attendees. Online abstracts count; a presenter is a presenter. Discount only people
  who cannot submit at all: exhibitor booth staff, trade-show visitors, accompanying persons.
- Do not judge a meeting small because its attendees are "the wrong sort". Judge it small only when
  little contributed science happens there.

## Programme character (cheap, separate)

Does an open call for abstracts exist? Submission deadline page, author guidelines, "submit your
abstract" CTA.

- abstract book exists + open call → `CONTRIBUTED`
- no call; invited-speaker, CME, live-case or hands-on-course framing → `CURATED`
- both, or a small call bolted onto a taught programme → `HYBRID`
- nothing found → `UNKNOWN`

## Your queue

Each row carries `list: "APPROVED"` (currently on the census sheet) or `list: "REMOVED"` (currently
on the deleted sheet, with `why_deleted`). **Research both identically.** A removed row that turns
out to be large gets upgraded back onto the approved list by the orchestrator — that is the point
of including them. Do not treat a removed row as settled.

## What you must NOT do

- Do NOT write to the workbook. You return JSON; the orchestrator writes.
- Do NOT set or suggest a Tier. Never write VERIFIED / BORDERLINE / OUT / DELETE.
- Do NOT re-research abstracts via rungs 1–8. That has been done and it failed.
- Do NOT present your inferred figure as a count anywhere in your output.
- Do NOT trigger browser dialogs or attempt rung A5.
- If a page returns 403 to the fetch tool, a plain `curl` with a browser user-agent often works —
  that is still loading the real page, which is allowed. Guessing URLs is not.

## Output contract — one JSON object per queue row, in a JSON array

```json
{
  "row": 42,
  "conference": "<echo EXACTLY as given — used to re-anchor if rows shift>",
  "list": "APPROVED",
  "attendance": "approximately 12,000 participants",
  "attendance_numeric": 12000,
  "attendance_year": "2024",
  "attendance_basis": "TOTAL_ONSITE",
  "attendance_rung": "A2",
  "attendance_rung_name": "post-meeting report",
  "attendance_source_url": "https://... (the page the number is ON, never a search page)",
  "attendance_method": "What you opened, where on it the number sits, any caveat, and — if you found nothing — which rungs you tried and why each failed.",
  "alt_figures": [{"value": 15000, "year": "2024", "basis": "UNSPECIFIED", "rung": "A1", "url": "https://..."}],
  "ratio": 0.25,
  "ratio_rationale": "What about THIS conference puts it there, naming the counted comparable you reasoned from. Mandatory whenever attendance_numeric is not null.",
  "programme_type": "majority-abstract | half-and-half | majority-teaching",
  "programme_evidence": "the wording that led you there",
  "direct_abstracts": null,
  "character": "CONTRIBUTED",
  "character_evidence": "https://... — open call for abstracts, deadline 15 Jan 2025",
  "confidence": "HIGH",
  "searches_used": 2
}
```

`confidence`: HIGH = named source, stated basis, recent year. MEDIUM = named source, unspecified
basis. LOW = proxy arithmetic, a figure older than 2019, or a pre-event projection.

## Budget and progress

~30 rows, ~60 searches, hard cap 2 per row. Work in order.

**Write your results incrementally to the output file named in your task prompt, rewriting the
whole file as a JSON array after every 5 rows**, so that if you are stopped, everything finished so
far survives on disk and a rerun resumes rather than restarts. Say in your final message how many
rows you completed and where the file is.
