# Phase-2 verification run — physical sciences — sessions 3 (2026-09-09/10)

Retention floor **~800 abstracts** (relaxed from 1,500 per Rupert).
>=1,500 VERIFIED | ~800-1,499 BORDERLINE (keep) | <~800 on positive evidence OUT | no evidence -> never OUT.

## Status: PASS A COMPLETE. PASS B COMPLETE except 7 browser rows.

### Model numbers
| | Baseline | Now | Why |
|---|---|---|---|
| SAM Global | 114.15 | **112.15** | duplicate Iran + IPS rows both Include=1 (-2.00) |
| SAM US | 54.00 | **54.00** | unchanged |
| SOM | 32.00 | **32.00** | unchanged |
| TAM phys-sci part | 41.66 | **~46** | restorations, net of 2 rows moved out |

Every restoration is model-neutral by construction (totals span both sheets). The only real
movement is the -2.00 duplicate fix.

### Coverage
- Census sheet: 52 live rows (28 VERIFIED, 24 BORDERLINE)
- Deleted sheet: 106 rows, **all 106 carry a Method entry**
- **Deleted rows carrying an actual number: 72 of 106 — was 16 of 110 when Pass B started**
- 5 agents x ~20-25 rows, ~63 searches total across the whole fan-out

### Restored to the census sheet this run
| Conference | Figure | How |
|---|---|---|
| M&M | 1,035 (2025) | eventscribe Browse-by-Title; found twice independently (browser + curl) |
| APS DNP Fall | 887 (2025) | APS Meeting Archive; method validated on 2024 = 745 |
| Congresso Nazionale SIF | 777 (2025), >802 (2024) | SIF annual reports; society states "oltre 800 ... contributi sottoposti" |
| E-MRS Fall | ~1,540-1,565 (2019) | pixel-calibrated from E-MRS's own chart; kept BORDERLINE, not VERIFIED |
| AVS / ASA / ICHEP / Quark Matter | 868 / 850-1,100 x2 / ~1,180 / 1,029 | numbers already on the rows, released by the lower floor |

### Still open — 7 rows, browser queue (orchestrator only, one shared instance)
16 Uzbekistan (ResearchGate 403) | 24 AAAS (confex JS shell) | 47 SPIE Sensors+Imaging (Distil/Incapsula)
| 50 NSBP (Cloudflare) | 52 Society of Rheology (ASP.NET postback) | 59 Croatian (CROSBI interstitial)
| 70 IOP (403)

### Genuinely unresolvable, recorded as such
- **56 Belarus** — network-layer block, not a JS wall; a browser fails identically. Rung 9 or another network.
- **53 Russia** — a **Phase-1 gap**, not a Phase-2 failure: the row names no conference, so the ladder has no query.

### Open decision for Rupert
**SciX (FACSS), deleted row 48 — 763 presentations**, ~5% under the floor (~740 excluding award/plenary
lectures). Currently STAY_DELETED. On a generous reading of "about 800" this flips to BORDERLINE. The
number and method are in the row, so flipping it is a one-line change.

### Corrections made to the sheet's own prior claims
Kazakh, Mongolian, Macau and Iceland were all recorded as having no recurring conference. All four do.
Belarus likewise has a named recurring congress. EPS Plasma's "at least 141" was a floor three times too
low (real: 446). ACA's "400+" is exactly 390. EPS-HEP's ">650" is exactly 684.

### Traps caught
- ÖPG/SPS: highest programme ID 994 would have cleared the floor; IDs are block-reserved and the real
  count is ~465-496.
- SPIE Medical Imaging advertises "737 Papers, 353 Presentations"; 1,090 would clear the floor, but the
  "Presentations" are recordings of papers already counted. Real: 737.
- hkps.org.hk is the Hong Kong PSYCHOLOGICAL Society — live domain lookalike.
- Rows 17/18 (Hong Kong, Macau) are the same Greater Bay Area event; only one may ever carry Include=1.
- Rows 19/110 (Iran) de-dup IS applied: 110 survives, 19 is zeroed. Cross-referenced on both rows.
