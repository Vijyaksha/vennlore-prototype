
**The meeting code must be probed, not guessed**: `world2023`, `isa2023`, `melbourne2023`, `wcs2023`
and `congress2023` all 404; `wc2023` and `wc2027` return 200. Records expose `Withdrawn`, `Type`,
`ProgramCode` and `MeetingTitle`, so the whole exclusion is done on the organiser's own fields.

**ECPR — three DevExpress ArrayStores embedded in the page.** `…/Events/AcademicProgramme/Programme?EventID=<n>`
is 1.47 MB and *looks* like a JS grid with no paper links anywhere in the visible markup. The whole
programme is inline as `ArrayStore({"data":[…]})` literals — 75 sections, 539 panels, **2,077 papers**
(each with `ID`, `EventID`, `Title`, `People`, `Keywords`, optional `AttachmentID`). **Extract with a
balanced-bracket, string-aware scan, not a regex**: a naive regex matched the 75-record sections store
instead. Get the EventID from `https://ecpr.eu/generalconference`.

**EERA/ECER — EERA's own TYPO3 abstracts database**, not ConfTool as the brief anticipated:

```
https://eera-ecer.de/ecer-programmes                                        # the search form carries both id spaces
https://eera-ecer.de/ecer-programmes/conference/<conf>/network/<net>        # listing, with an <ol> of contributions
https://eera-ecer.de/ecer-programmes/conference/<conf>/contribution/<id>    # one presentation
```

Network ids 875–916 (875 = "01. Professional Learning and Development" … 908 = "34. Citizenship
Education", plus 909 Functions, 910 Additional events, 911 Emerging Researchers' Group, 912 Governance
Meetings, 913 Central & EERA Sessions, 914 Bursaries, 915 Blocked, 916 preview); conference ids one per
year 1998–2026. **3,582** contributions, **3,216** after removing the ERC pre-conference and
central/governance networks.

**AAR — a public program book on a submission host.** `papers.aarweb.org` requires a login to *submit*
but not to read:

```
https://papers.aarweb.org/program-book/<node>?page=0..73     # 32290 = November 2026 meeting
```

Every paper is its own `<article data-history-node-id="NNNNNN" class="node node--type-paper …">`
carrying presenter, title and abstract, inline in the listing. Count **distinct node ids**: 1,396
across 299 papers-sessions, 209 roundtable-sessions and 159 other-events.

