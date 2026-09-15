
**ASC is the trap worth remembering.** `https://asc41.org/wp-json/` returns **HTTP 406** to a bare
request, which reads as "not WordPress". It *is* WordPress — the page markup exposes
`/wp-json/oembed/1.0/embed` and `/wp-content/` — and the media endpoint answers normally when given
a desktop Chrome user-agent **and** an `Accept: application/json` header. Always check the markup
before concluding a society is not on WordPress.

**AAG has a second trap:** its 2025 and 2026 files are named `AAG-2025-program-missing-abstract-titles.pdf`
and `AAG-2026-working-program-missing-abstract-titles.pdf` — incomplete by the organiser's own
filename. The most recent COMPLETE book is `AAG-2024-PDF-program-FINAL.pdf`.

### 2.2 Counting a two-column programme PDF by its own typography

**This is the single most important technique in this field.** `pdftotext` alone cannot delimit
papers in any of these books: they are two-column, titles wrap over several lines, and a fixed-column
split fragments the right column (tried on ASC — the gutter drifts between columns 50 and 58 and most
pages have no clean gutter at all). The layout *is* the data. Use:

```
pdftohtml -xml -i -stdout <book>.pdf > all.xml
```

Font ids are **global** in that mode (they are re-assigned per page if you use `-f`/`-l`, so always
run the whole document). Each `<text top= left= font=>` element then carries the role.

| Book | Discriminator | Result |
|---|---|---|
| **APSA 2026** (487 pp) | font 268 = labels (`Chair:` 1,528, `Papers:` 1,295, `Disc:` 1,183, `Part:` 301), 257 = paper-title words (one element per word), 256 = author lines and session numbers, 254 = DIVISION heads. **A paper = one maximal run of font-257 inside a `Papers:` block** | **5,570** in 1,295 sessions |
| **ASA 2022** (180 pp) | the **left coordinate encodes the role**: 40/41 = first line of a paper in a paper session, 62 = first line of a paper at a roundtable table, 51 = `Table Presider:`, 78/84 = wrapped continuation (mirrored at 472/473, 494, 483, 510/516) | 2,693 blocks, **2,644** carrying the `Title - Author` separator |

