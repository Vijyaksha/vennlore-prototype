- **Sister meetings share one platform.** ISA's Confex host serves both `wc2023` (World Congress,
  quadrennial) and `forum2025` (ISA Forum, quadrennial, offset). IATED runs ICERI, EDULEARN and INTED
  off one Crossref prefix. NCTM runs four separate event families with four separate attendance
  projections in one media kit (Annual Meeting 6,000; Spring Conferences 2,000 each; NCTE-NCTM Joint
  1,300; Interactive Institute 500). **Never merge, never substitute.**
- **One publisher can deposit the same meeting twice.** AERA deposits its programme *and* its Online
  Paper Repository under **interleaved submission ids** (proc 2178471–2253013, ip 2178470–2257239);
  1,375 ids recur, so summing the two containers double-counts. Crossref also lists each IATED
  container twice, year-stamped and generic, with identical counts.
- **`?page=N` fails in three distinct ways in this field, so always fetch page 2 and diff it against
  page 1**: Cloudflare challenges the query string but not the bare path (EEA-ESEM); the parameter is
  silently ignored and every page returns identical rows (AEA `/preliminary`, and COMIE's `&p=`); or it
  works perfectly (AAR, ANPEd).
- **Local numeric conventions.** Chinese 篇 = papers, 人 = people, 场 = sessions, **人次 = person-times**:
  CPS's `线上实际参会超过4.5万人次` is 45,000 person-*times* of online viewing, **not** 45,000 attendees,
  and was not used as attendance. Korean 초록집 = abstract book, 프로그램북 = programme book, 구두 = oral,
  포스터 = poster. Japanese 大会発表論文集 = convention proceedings, 正誤訂正一覧 = errata.
- **Regex over-matching in CJK.** An exclusion regex on `プログラム` caught genuine JPA paper titles
  (`…自伝プログラムの効果`, `…予防プログラム`) — 21 false positives. Anchor CJK exclusions to **whole
  titles** (`^\s*(正誤訂正一覧|目次|表紙|奥付|索引)\s*$`), which leaves exactly one real exclusion.
- **Practitioner conventions are a different animal and the character judgement decides them.** NCTM's
  own media kit sells an audience of classroom teachers and district purchasers who come "to get new
  ideas for teaching" and "visit the exhibit hall for over an hour"; its sessions are 60–75 minute
  workshops delivered by one or two teachers, so each session yields about **one** presentation, not
  four. That structural difference is precisely why its judged ratio is **14%** against DGPs' **80%** —
  and why a ratio must never be copied across from one meeting to another.
- **Spam-injected but genuine hosts.** `anais.anped.org.br` carries injected Turkish gambling links yet
  serves the society's real Drupal proceedings. Don't discard the host; don't follow the links.
- **Credential walls are not rung 5.** IPSA's proceedings library, and the ASA/ASC member archives. A
  browser gains nothing — do not queue them.
- **A "PDF" URL may not be a PDF, and a 200 may not be a page.** IPSA's programme excerpt (HTML catch-all
  at 261,910 bytes), ANPEd's homepage (a 403 body inside a 200), the uni.lu press kit (202, zero bytes).
  **Check status AND content-type AND size before counting anything.**

---

