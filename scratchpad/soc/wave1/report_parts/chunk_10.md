
## 3. Every route that failed, and the wall hit

| Route | Wall | Verdict |
|---|---|---|
| **All Academic** `convention2.allacademic.com/one/<org>/<org><yy>/` | **Google reCAPTCHA interstitial on EVERY path** (1,949–1,987 bytes, HTTP 200) for APSA, ASA and ASC — with or without a cookie jar, deep `cmd=` links, or a desktop Chrome UA. Wayback holds only session-keyed 700–1,200 byte stubs | **Worse than rung 5 — a CAPTCHA needs a human.** The brief's central prediction for this field is dead; use the society PDF instead |
| All Academic, **LASA** instance | `lasa26` is **not** gated (a real 81 KB guest session) but every `cmd=` returns the same JS menu shell; `lasa25` **is** gated | Rung 5 at best; the society PDF beat it |
| **Wayback / Internet Archive** | `Gateway Time-out`, then the `Internet Archive: Temporarily Offline` page, for most of the run | **Every Wayback bypass in the engineering notes was unavailable this wave.** Retry later |
| `icahdq.org` (ICA) | Cloudflare JS challenge — HTTP 403 "Just a moment…" to curl **and** to WebFetch | **Rung 5** |
| `www.uni.lu` (DGPs congress + press kit) | **AWS WAF: HTTP 202 with a 2,087-byte `window.awsWafCookieDomainList` / `gokuProps` body; the press-kit PDF returns 202 with a ZERO-BYTE body** | **Rung 5** (the IEICE/AIJ pattern) |
| **Confit** `pub.confit.atlas.jp`, `confit.atlas.jp` (JPA) | HTTP 202, zero-byte body, on event, search and subject-detail URLs alike | **Rung 5** — beaten here by J-STAGE |
| `eea-esem-congresses.org` | **Cloudflare challenges every QUERY-STRING URL while serving the bare path fine**: `/full-programme` 200/255 KB, `?page=1`, `?page=2`, `?items_per_page=5000`, `?items_per_page=All` all 403. Views AJAX (`view_name=full_programme`, display `page_1`, POST `/views/ajax`) returns a Drupal 403. No `sitemap.xml`. S3 bucket not listable | **Rung 5 — since resolved by the orchestrator** |

