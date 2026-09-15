| **LASA 2026** (307 pp) | paper titles are **italic** (Montserrat-LightItalic, font 3); every label, session header, session title and author line is regular (font 2) | **4,609** in 1,671 sessions |
| **ESA 2024** (1,401 pp) | font 5 (30pt) = session header, **15 (24pt) = abstract title**, 16 (17pt) = author name, 2 (14pt) = affiliation and body | **3,450** |
| **SPSP 2025** (86 pp) | a four-column table whose **rightmost column (x = 1083) is the organiser's own Category** — Poster / Preconference / Symposia / \*Roundtable / Data Blitz / Professional Development / \*Event / Symposia;Featured Session | **2,265** main-convention |

**ASC needs one extra step that none of the others do.** `pdftohtml` emits **several `<text>` runs per
visual line** whenever the font changes mid-line, so the raw indent histogram is noise. Merge runs
into lines first — round `top` to a ~7-unit grid within each column and concatenate by `left` — and
the hierarchy appears: left column 70 = label or session header, 81 = first line of an entry, 91/92 =
continuation; right column 367 / 378 / 388–389 the same. Then a paper is one entry at 81/378 plus its
continuations, kept only if it carries ASC's `Title; Author, Affiliation` semicolon. **3,010** in 709
sessions.

**AAG needs no geometry at all**, because its book is not really two-column at the entry level: each
session prints the literal line `Presentations (if applicable) and Session Agenda:` and then one line
per presentation laid out as presenter | title. A presentation is a line inside that block beginning
at column 0 **and** carrying a second column (`^\S.*?\s{3,}\S`), closing on
`^(Non-Presenting Participants|Type:|Sponsor Group|Primary Organizer:|Primary Session Chair)`. The
two-column requirement is load-bearing: it removes exactly 1,077 following-session title lines
against 1,085 blocks. **3,283** presentations.

