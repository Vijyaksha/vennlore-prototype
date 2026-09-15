| `spsp.org` / `meeting.spsp.org` | `/wp-json/` Cloudflare 403; `/events/annual-convention` and `/schedule` **HTTP 522** (origin unreachable) throughout the run; `spsp2026.eventscribe.net` 403 | Beaten via the Drupal file store `/sites/default/files/<YYYY-MM>/` |
| `anped.org.br` | **HTTP 200 whose BODY is a LiteSpeed "403 Forbidden" page** — a status-code check alone misses it | Beaten via the `anais.` subdomain |
| `www.cpsbeijing.org` | Frameset; the CMS channel URLs (`/cms/show.action?code=…&siteid=100000`) return 236-byte bodies without a session | Beaten via a CAS institute report |
| **IPSA** full programme | `/user/login?destination=/events/congress/past-world-congress-programs` and `/my-ipsa/conference-proceedings-library/search` | **Credential wall — do NOT queue for rung 5.** A browser gains nothing |
| `wc2025.ipsa.org/sites/default/files/…/wc2025-ipsa-program-exerpt.pdf` | **HTTP 200, `content-type: text/html`, 261,910 bytes** — the site's Drupal catch-all page, not a PDF | Check status **and** content-type |
| `icme15.org` | **Domain lost to a squatter** — now an Indonesian online-gambling site (`<html lang="id">`, "Dewi11 · Bandar Togel Online"), same body on every path. `icme15.com` is a content-free loading shell | Never cite; the figures a snippet attributed to it were refused |
| `apsa.asia` | A Hong Kong **rowing-equipment retailer** (NK Nielsen Kellerman); `asiapacificsociology.org` returns 114 empty bytes | The row's society does not exist |
| **ConfTool** for ESA | `conftool.com/esa2024/` and `/esa2026/` serve the **ConfTool marketing homepage** (instances closed); `.pro` / `.org` / `.net` variants 404 | Beaten via the abstract book |
| `paa.confex.com`, `ipsa.confex.com`, `nctm.confex.com`, `spsp.confex.com` | Do not resolve — these societies have all **left Confex** | Find the new platform |

