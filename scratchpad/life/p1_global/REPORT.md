# Life sciences phase 1, global English sweep — agent report (2026-09-13)

Written by the orchestrator from the agent's final replies (the agent could not write files).
Data: `names.json` (732 new names), `STATUS.json`. Existing-name check: `existing_names.json`
(1,455 rows from every census/deleted sheet at the time of the sweep).

## Result

732 new life-sciences conference names, 131 countries and regions, 78 web calls (searches plus
fetches of enumerating pages) against a target of ~80 and a cap of 100.

| Sweep | New names |
|---|---|
| knowledge | 269 |
| federations | 170 |
| subfields | 135 |
| countries | 88 |
| gaps | 48 |
| second_pass | 22 |

434 flagged `implied` (a federation member list proved the society exists; the meeting name was not
confirmed, so the society name stands as the conference). 35 flagged `boundary`. 473 carry a
`source_url`; the 259 without one are knowledge-sweep entries.

Orchestrator check (2026-09-13): no internal duplicates; no predatory-aggregator entries; two real
overlaps with existing rows — WSAVA World Congress (already on `Deleted - Medicine & Health`) and the
IUMS congress (a US-hosted row already on `Census - Life Sciences`). Drop both at load time.

## Federation and platform pages that enumerated many meetings at once

- **IUNS adhering bodies** — 85 national nutrition bodies in one fetch; ministries, academies and
  institutes deliberately dropped (they run no meetings).
- **FEMS member societies** (56 societies, 41 countries) and **IUMS member societies** (96 national
  members) — microbiology worldwide, incl. Gambia, Paraguay, Uruguay, Kazakhstan, Kosovo.
- **IUPAB members** — 55 national biophysics bodies; **EFIS** — 36 immunology societies; **FENS** — 43
  neuroscience societies; **IUPS** — ~40 physiological societies.
- **SIPaV national societies + EFPP associated societies** — ~35 national plant-pathology societies.
- **ICE Council societies page + ESA international list** — entomology; **IFCB member organizations** —
  cell biology; **Global Plant Council members** — plant science; **European Ecological Federation**
  (Wikipedia entry; the federation's own page would not render) — 18 national ecological societies.
- **HUGO worldwide genetics societies page** — Asia-Pacific and Latin American human genetics.

## Saturated, and not

Saturated at national-society level: European biochemistry, microbiology, neuroscience, immunology,
physiology; plant pathology, nutrition, biophysics.

Not saturated: national genetics, zoology, botany, mycology, ornithology and food-science societies
outside Europe.

## The federation lists that resisted fetching (still hold names)

1. **IUIS member societies** — `iuis.org/societies/` returns HTTP 403. 84 national immunology societies
   + 4 regional federations. EFIS covered the European 36; the gap is Latin America/Caribbean, Africa,
   Asia-Oceania. Retry in Chrome (rung 5) or via the regional federations.
2. **FAOBMB constituent members** — never rendered. 20 member societies across Asia and Oceania.
   Reachable at `faobmb.com` (About → Constituent Members) or the 50-year history paper
   `iubmb.onlinelibrary.wiley.com/doi/10.1002/iub.2679`, which carries the member table.
3. **FIMSA member societies** — `fimsa.org/members.html` refused the connection (ECONNREFUSED). 12 full
   members in Asia-Pacific; Australia, NZ, Japan, Korea, Thailand confirmed, seven unknown.
4. Partial: **FEBS societies directory** paginates and served 20 of 39 constituent societies
   (`?page=2` re-serves page 1). Missing: the national biochemical societies of Lithuania, Norway,
   Poland, Portugal, Romania, Russia, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, the
   Netherlands, Türkiye, Ukraine and the UK, plus associates in Belarus, Moldova, Morocco, Tunisia.
   Country list in hand; society names missing — a one-page fix.

Four guessed URLs 404'd; searching first and fetching the URL the search returns was the better trade.

## Countries seen only through English — the deferred local-language pass

Every non-anglophone name was found in English. The local-language pass is DEFERRED, not waived
(Rupert scoped this sweep to English, 2026-09-13). It matters most for the 434 `implied` rows.

- **Japan**: 年会, 大会, 学術集会; society pattern 日本〇〇学会; abstracts 講演要旨集. ~20 societies held,
  named meetings for few.
- **China**: 学术年会, 全国代表大会, 学术会议; 学会; 论文集. Almost all Chinese rows implied; only the
  National Congress of Plant Biology could be named.
- **Russia**: съезд, конференция; тезисы докладов.
- **Kazakhstan, Belarus, Armenia, Georgia, Azerbaijan**: Russian terms as working language plus each
  national language. All appear in FEMS/FEBS/IUPAB/FENS lists as societies with no meeting name.
- **South Korea**: 학술발표회, 총회, 학술대회; 초록집. **Taiwan**: 年會, 學術研討會; 摘要.
- **Brazil**: congresso, reunião anual; resumos. The 28 SBPC societies are the largest single block of
  unnamed meetings in the file.
- **Spanish-speaking Latin America** (Mexico, Argentina, Chile, Colombia, Cuba, Uruguay, Peru, Paraguay,
  Venezuela, Costa Rica): congreso, reunión anual, jornadas; resúmenes, comunicaciones.
- **Germany, Austria, Switzerland**: Jahrestagung, Tagung, Kongress; Beiträge, Kurzfassungen.
- **France and Francophone Africa**: congrès, journées, réunion annuelle; résumés, communications
  (covers APRONES and the Maghreb societies).
- **Italy**: congresso nazionale, convegno; riassunti, contributi. **Spain**: congreso, reunión;
  resúmenes. **Portugal**: congresso, reunião anual; resumos.
- **Netherlands and Flanders**: congres, jaarvergadering; samenvattingen. **Poland**: zjazd, kongres;
  streszczenia.
- **Czech Republic, Slovakia, Hungary, Romania, Bulgaria, Croatia, Serbia, Slovenia, Estonia, Latvia,
  Lithuania, North Macedonia, Bosnia**: national words for congress, meeting and abstracts. The bulk of
  the implied rows sit here.
- **Nordics**: Finnish, Swedish, Norwegian, Danish and Icelandic equivalents.
- **Türkiye**: kongre, kurultay; bildiri özetleri.
- **Iran**: کنگره, همایش; چکیده مقالات.
- **Indonesia**: seminar nasional, kongres; abstrak. **Thailand**: การประชุมวิชาการ; บทคัดย่อ.
  **Vietnam**: hội nghị khoa học; tóm tắt.
- **Arabic-speaking countries** (Egypt, Saudi Arabia, UAE, Tunisia, Morocco, Sudan, Algeria): مؤتمر,
  المؤتمر السنوي; ملخصات البحوث. Barely reached in English; Egyptian and Moroccan societies appear only
  via FASBMB and SONA.
- **Israel**: כינוס, אסיפה שנתית; תקצירים.

Worth a pass despite English being a working language: India, the Philippines, Malaysia, Singapore and
Nigeria, where English pages exist but are thin.

Phase 2 inherits a two-step job on the 434 implied rows: name the meeting, then size it.
