
**NCA needs no geometry either, because it marks papers typographically**: every contributed paper is
a curly-quoted title followed immediately by its authors, while panellists appear as bare names under
a `Presenters:` label. Count on whitespace-collapsed text, per page:

```
“([^“”]{10,400})”\s*([A-Z][A-Za-z.’'\-]+(?:\s+[A-Z][A-Za-z.’'\-]+){0,3},|[A-Z][A-Za-z.’'\-]+\s+[A-Z][A-Za-z.’'\-]+;)
```

The author-follows constraint is what excludes the front matter's quoted prose (without it the bare
quote count is 2,477/2,567 and includes the president's welcome). **2,248** (`-raw`).

**PAA needs neither**, because it numbers every oral paper `<session>-<n>` in the margin. Count unique
ids with two different anchors on the two extraction modes — `(?:^|\s{2,})([A-Z]?\d{1,3}-\d{1,3})\s{2,}\S`
on `-layout` and `(?m)^\s*([A-Z]?\d{1,3}-\d{1,3})\s+\S` on `-raw`. Both give **1,106**.

### 2.3 Programme-platform data files and backing APIs

**None of these five is a rung-5 job**, and three of them look like one at first glance.

**JSM — a static JSON export behind a 5 KB shell.** The programme page footer says "data from the
Attendee Interactive API"; its client script `assets/app2.js?v=62` names four open endpoints:

```
https://ww2.amstat.org/meetings/jsm/<year>/onlineprogram/data/stats.json?v=62     # {"sessions":910,"talks":2873}
https://ww2.amstat.org/meetings/jsm/<year>/onlineprogram/data/search.json?v=62    # 1.9 MB, every session
```

`search.json` carries `type` and `talkCount` per session, i.e. **the organiser's own invited/
contributed split for free**: Contributed Papers 1,091 + Topic-Contributed 621 + Contributed Posters
337 + Contributed Speed 129 = **2,178**, against Invited Paper Session 598 and Invited Posters 40.

**ISA — the Confex backing API.** The SPA front end is irrelevant; the API is open:

```
https://isaconf.confex.com/isaconf/<meeting>/meetingapi.cgi/Paper     # use --compressed
https://isaconf.confex.com/isaconf/<meeting>/meetingapi.cgi/Program
```

