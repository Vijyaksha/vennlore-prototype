# Attendance pass — medicine census. Agent brief.

You are finding **attendance** figures for large academic/medical conferences.
You are NOT finding abstracts. You are NOT deciding anything.

## The single most important structural fact

This is NOT the abstract ladder. Abstracts are almost never stated, so that ladder was
about locating a countable artefact and counting it. **Attendance is almost always
stated somewhere.** The problem is the opposite: many numbers exist, of wildly differing
honesty, counting different things. So this ladder ranks sources by **how much the
source had to answer for the number** — it is a credibility ladder, not a counting ladder.

Expect rung A1–A3 to resolve most rows in one or two searches. Rung 1 was near-useless
for abstracts; here it is the workhorse.

## The ladder

- **A1 — Exhibitor / sponsor prospectus.** Search `"<conference>" exhibitor prospectus attendee demographics filetype:pdf`
  or `"<conference>" "why exhibit"`. Highest yield AND highest accountability: exhibitors pay real
  money against these figures, and they are usually broken down (delegates vs exhibitors vs country).
- **A2 — Post-meeting report / "congress by the numbers" / society annual report.** Retrospective,
  often gives the actual figure against A1's projection. Prefer A2 over A1 when both exist and disagree.
- **A3 — Society press release / newsroom / trade-press coverage of that edition.** Cheap, usually one
  round number, no breakdown.
- **A4 — Venue / convention bureau / ICCA / economic-impact study.** Independent of the society.
  Good corroboration; may report *bid* size rather than actual.
- **A5 — Programme-platform artefact.** Participant directory count, badge/ID ranges, app attendee list.
  The only rung that COUNTS rather than reads. Browser-only and expensive — **do not attempt it.**
  If a row plainly needs it, return `attendance_rung: "A5"` with `attendance_numeric: null` and say what to open.
- **A6 — Proxy arithmetic.** Parallel sessions x room capacity, exhibition floor sqm, exhibitor count.
  Order-of-magnitude ONLY. Must be flagged as an estimate in the method text.
- **A7 — Prior year / sister meeting.** Carry a nearby year's figure, stating the year explicitly.

## Three rules that matter more than the rungs

**1. Every number carries a BASIS tag.** "12,177" is meaningless without knowing whether it counts
delegates only, or delegates + exhibitor staff + press + virtual. Tags:
`DELEGATES` | `TOTAL_ONSITE` | `TOTAL_INC_VIRTUAL` | `UNSPECIFIED`.
If the source does not say, the tag is `UNSPECIFIED` — do not guess.

**2. Record disagreement, do not resolve it.** If the prospectus says 15,000 and the press release
says 11,400, return BOTH — headline = the more accountable rung, and the other in `alt_figures`.
The spread IS a finding. **Never average.**

**3. Stop at the first rung that yields a figure with a basis.** Nothing here decides a row's fate,
so there is no completeness obligation. **Hard cap: 2 web searches per row, 3 for a genuinely hard one.**
Prefer fetching a promising URL over another search.

## Programme character — the second signal

Cheap and separate. Strongest single discriminator: **does an open call for abstracts exist?**
A submission deadline page, author guidelines, a "submit your abstract" CTA.

- abstract book exists + open call -> `CONTRIBUTED`
- no call, invited-speaker programme, CME / live-case / hands-on-course framing -> `CURATED`
- both, or a small call bolted onto a taught programme -> `HYBRID`
- nothing found -> `UNKNOWN`

Many queue rows already carry a counted abstract figure in the `abstracts` field. **If a row has a
real abstract count, character is already CONTRIBUTED** — do not spend a search on it; say so.
Only spend effort on character where `abstracts` is UNKNOWN or blank.

EuroPCR is the worked example of why this matters: 12,177 attendees against 743 counted abstracts.
Without the character signal that row looks like a giant contributed congress; it is a teaching
and live-case course.

## What you must NOT do

- Do NOT set or suggest a Tier. Do NOT write VERIFIED / BORDERLINE / OUT / DELETE anywhere.
- Do NOT touch, revise, or re-research the abstracts columns. The `abstracts` field in your queue
  is context for the character call ONLY.
- Do NOT write to the workbook. You return JSON; the orchestrator writes.
- Do NOT carry forward a number already in the sheet as if it were your finding. "Carried forward"
  is not a method.
- Do NOT report a figure you did not see on a page you actually loaded. If a search snippet asserts
  a number, open the page and confirm it. A number that only exists in a snippet is not evidence.
  (Four rows in this workbook already assert figures their own cited sources do not contain.
  Do not add a fifth.)
- Do NOT trigger browser dialogs or attempt rung A5.

## Output contract — one JSON object per queue row, in a JSON array

```json
{
  "row": 42,
  "conference": "<echo EXACTLY as given — used to re-anchor if rows shift>",
  "attendance": "approximately 12,000 participants",
  "attendance_numeric": 12000,
  "attendance_year": "2024",
  "attendance_basis": "TOTAL_ONSITE",
  "attendance_rung": "A2",
  "attendance_rung_name": "post-meeting report",
  "attendance_source_url": "https://... (the page the number is ON, not a search page)",
  "attendance_method": "One or two sentences: what you opened, where on it the number sits, and any caveat.",
  "alt_figures": [
    {"value": 15000, "year": "2024", "basis": "UNSPECIFIED", "rung": "A1", "url": "https://..."}
  ],
  "character": "CONTRIBUTED",
  "character_evidence": "https://... — open call for abstracts, deadline 15 Jan 2025",
  "confidence": "HIGH",
  "searches_used": 2
}
```

- `attendance_numeric`: integer, or `null` if you found nothing. Never a range — put the range in
  `attendance` as text and the midpoint-free best single accountable figure in numeric, or null.
- If nothing found: `attendance_numeric: null`, `attendance_rung: null`,
  `attendance_method` = which rungs you tried and why each failed. Absence of evidence is not
  evidence the meeting is small — say that.
- `alt_figures`: `[]` if none.
- `confidence`: HIGH = named source, stated basis, recent year. MEDIUM = named source, unspecified
  basis. LOW = proxy arithmetic, or a figure older than 2019.

## Budget and progress

Your slice is ~45 rows. Total budget ~90 web searches — stay under it; you have a hard cap and
running out mid-slice is worse than a thin row. Work in order.

**Write your results incrementally** to the output file given in your task prompt, as a JSON array,
**re-writing the whole file after every 5 rows** so that if you are stopped, everything done so far
survives on disk and a rerun resumes rather than restarts. Say in your final message how many rows
you completed and where the file is.
