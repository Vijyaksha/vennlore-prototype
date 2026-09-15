import json, os, sys
sys.path.insert(0, '.')
from streamline import build_wave_brief

E = {r['row']: r for r in json.load(open('waveA_prep/earth_candidates.json'))}
S = {r['row']: r for r in json.load(open('waveA_prep/soc_candidates.json'))}

E1 = [26,76,65,70,61,62,11,9,10,58,60,17,125,105,119,34,93,96,97,35,36,59,106,103,91,92,82,83,55,118]
E2 = [28,63,68,71,22,23,99,89,81,44,114,128,84,31,101,67,69,79,53,127,111,90,24,25,27,29,32,41,57,95]
S1 = [23,8,22,195,90,15,145,120,121,24,80,92,124,86,87,56,159,17,25,30,67,91,93,101,146,147,192,60,74,82]
S2 = [143,9,59,186,21,116,118,95,183,184,185,64,189,19,28,96,114,188,196,61,81,115,148,132,26,38,191,49,50,20]
for q in (E1,E2,S1,S2): assert len(q)==30 and len(set(q))==30
assert not (set(E1)&set(E2)) and not (set(S1)&set(S2))
assert all(r in E for r in E1+E2) and all(r in S for r in S1+S2)

IUGG = ("IUGG-family association: the IUGG annual reports (https://iugg.org/publications/iugg-annual-reports/, "
        "report2023.pdf sized IAVCEI 2023 = 1,258 abstracts / 1,080 people and IAG 2023 = 643 orals / 1,202 participants) "
        "and each association's own assembly site. Count THIS association's own assembly (or the joint pair as ONE meeting), "
        "never the IUGG General Assembly (row 8, already counted). Joint editions: IAGA-IASPEI 2025 Lisbon and IACS-IAMAS-IAPSO 2025 Busan are one meeting each.")
COP = "Copernicus meeting: static per-abstract pages https://meetingorganizer.copernicus.org/<SLUG>/<SLUG>-<n>.html (test the <title>, not the status); slugs seen: "
EH = {
 26: "WCRP OSC 2023 Kigali (23-27 Oct 2023): abstract book / programme on wcrp-osc2023.org or wcrp-climate.org; roughly decadal so events_per_yr ~0.1 — record the cadence evidence",
 76: "ICRS 2022 Bremen (15th) abstract book PDF on icrs2022.de / coralreefs.org; 16th ICRS 2026 Auckland. Boundary with life sciences (marine biology) — count once, flag boundary",
 65: "IMA 2022 Lyon (23rd General Meeting) abstract book on ima2022.fr; also 'Sciencesconf' hosts",
 70: "IPC6 Khon Kaen 2022 abstract volume; IPC7 2026. ipa.geo.hu-berlin.de",
 61: IUGG, 62: IUGG, 11: IUGG, 9: IUGG, 10: IUGG,
 58: IUGG + " IAHS 2022 Montpellier was Copernicus-hosted: " + COP + "IAHS2022",
 60: "ESC 2024 Corfu (39th GA) abstract book; ESC 2026 Istanbul. Phase-1 note: 36th had over 900 abstracts",
 17: "WCGALP 2022 Rotterdam proceedings are published by Wageningen Academic Publishers (Crossref: query the publisher container 'Proceedings of 12th World Congress on Genetics Applied to Livestock Production (WCGALP)'), also WCGALP 2026 Kampala",
 125: "AEGC 2023 Brisbane / AEGC 2025: extended abstracts published in 'ASEG Extended Abstracts' (Taylor & Francis, Crossref ISSN 2202-0586) — count the edition's items; also aseg.org.au",
 105: "5th World Congress on Agroforestry, Québec 2022 (book of abstracts); worldagroforestry.org / agroforestry2022.org",
 119: "Congreso Latinoamericano de la Ciencia del Suelo — check the latest edition (2023 Florianópolis? / 2027 Asunción); slcs.org.mx; a joint year with the Argentine congress counts once — set duplicate_of if your edition is joint with row 120",
 34: "Crossref: container '19th Congress of the Brazilian Geophysical Society - Proceedings' = 712 papers (phase-1 hint, prefix SBGf/Crossref). Count by container facet per edition; sbgf.org.br proceedings",
 93: "SBCS second meeting (FertBio, biennial alternating with CBCS); anais likely on a publisher platform (Editora Novus pattern seen for CBCS) or Even3 prefix 10.29327 — check the Even3/Crossref container facet",
 96: "Brazilian anais: try the Even3 Crossref prefix 10.29327 container facet (type:proceedings-article) and cbmet.com.br anais pages",
 97: "Phase-1 figure: a recent edition presented 678 papers (549 posters + 129 orals) — OPEN the page (cbagro2025.com.br) and confirm; below 800 on positive evidence = OUT",
 35: "Crossref container 'SGEM International Multidisciplinary Scientific GeoConference EXPO Proceedings' = 532 papers in one container; SGEM runs several editions per year — decide the unit (one edition) and events_per_yr, do NOT sum editions",
 36: "Crossref: 58th ARMA = 649, 59th = 473 papers (OnePetro). Count the latest edition's container; boundary with engineering",
 59: "Crossref container 'Middle East Oil, Gas and Geosciences Show (MEOS GEO)' = 667 papers (OnePetro/SPE). Boundary with petroleum engineering",
 106: "IPPC 2023 Athens (XX) abstract book; plantprotection.org. Boundary with life sciences — flag",
 103: "XXV IGC 2023 Covington Kentucky was JOINT with the XII International Rangeland Congress (row 104, not in your queue): proceedings on UKnowledge (uknowledge.uky.edu/igc/) — count the joint edition once and note it",
 91: "6th International Agronomy Congress, New Delhi, Nov 2025 (Indian Society of Agronomy): souvenir / abstract book PDF; also indianagronomy.org",
 92: "ISSS India annual convention: printed abstract book; isss-india.org publications; local-language not needed (English)",
 82: "Türkiye Jeoloji Kurultayı bildiri özetleri PDF on jmo.org.tr (search in Turkish: 'Jeoloji Kurultayı bildiri özetleri kitabı')",
 83: "Congreso Geológico de España → Geo-Temas volumes (sociedadgeologica.es/publicaciones/geo-temas); count contributions in the congress volume (XI Congreso 2024 Ávila?)",
 55: "Congreso Geológico Argentino actas (XXII, 2025 San Luis? / XXI 2022 Puerto Madryn): geologica.org.ar; Spanish search 'actas congreso geológico argentino trabajos'",
 118: "Convención Geológica Nacional (Sociedad Geológica Mexicana) — libro de resúmenes on sociedadgeologicamexicana.org.mx/cgn2023; Spanish search",
 28: "World Geothermal Congress 2023 Beijing / 2020+1 Reykjavik: every paper is in the IGA Geothermal Paper Database (https://www.geothermal-energy.org/explore/our-databases/conference-paper-database/) filterable by conference — count entries for one WGC edition; also pangea.stanford.edu ERE db",
 63: "ISC 2022 Beijing (21st, online) / ISC 2026 Wellington: abstract volume; sedimentologists.org; IAS annual IMS (row 64) is a separate series",
 68: "10th ICG Coimbra 2022 abstract book (icg2022.eu); geomorph.org",
 71: "WLF6 Florence 2023: proceedings in Springer 'Progress in Landslide Research and Technology' volumes — Crossref book chapters per volume; count chapters of the WLF6 volumes; WLF7 2026 Faridabad",
 22: COP + "EPSC2022, EPSC2024, EPSC-DPS2025 (joint year — count once and flag duplicate_of with row 23 for joint editions), EPSC2026",
 23: "DPS meets on the AAS platform (aas.org / dps.aas.org abstracts in BAAS; joint EPSC-DPS years are Copernicus — " + COP + "EPSC-DPS2025). Count a NON-joint year (DPS 2024 Boise) and flag the joint-year duplicate with row 22. Boundary with physical sciences (astronomy)",
 99: "XV World Forestry Congress Seoul 2022: FAO/KFS report itemises abstracts (poster/paper calls); largely policy — judge character. Cadence ~6 years (0.17)",
 89: "中国海洋学会 学术年会: society site (cso.org.cn?) and government/news mirrors; Chinese search '中国海洋学会学术年会 论文 摘要 报告 场'",
 81: "IMPLIED NAME — resolve first: 中国地质学会学术年会 (Geological Society of China, geosociety.org.cn); Chinese search '中国地质学会 学术年会 报告 论文摘要'; ministry/news mirrors (mnr.gov.cn, cgs.gov.cn) fetch cleanly when the society site blocks",
 44: "IMPLIED NAME — resolve first: 中国土壤学会学术年会 (csss.org.cn); Chinese search; gov/news mirrors",
 114: "IMPLIED NAME — resolve first: 中国作物学会学术年会 (cssc.org.cn / crop.org.cn); Chinese search",
 128: "TGA 臺灣地球科學聯合學術研討會 (Taipei, May): programme/abstract search on the TGA site (tga.cgu.org.tw or similar); Chinese search '臺灣地球科學聯合學術研討會 摘要 篇數'",
 84: "IMPLIED NAME — resolve first: 대한지질학회 / 지질과학연합 학술대회 (gskorea.or.kr); Korean search '지질과학연합학술대회 초록집'; society file boards (download.html?fno=) as in the KPA pattern",
 31: "GAC-MAC abstracts volume: 'GAC-MAC Abstracts' (Geological Association of Canada, gac.ca/publications; Crossref journal 'Geoscience Canada' is NOT it). 2024 Brandon, 2025 Ottawa — count the abstract volume",
 101: "WAS regional editions: https://www.was.org/MeetingAbstracts/Index lists every meeting's abstracts (countable per meeting); pick ONE edition as the unit (e.g. Aquaculture Europe 2025) and report events_per_yr for that series; row 100 (Aquaculture America / Triennial) is already counted — do not duplicate it",
 67: "IAEG XIV Congress Chengdu 2023: proceedings in Springer 'Engineering Geology for a Habitable Earth' volumes — count chapters via Crossref; boundary with engineering",
 69: "ISRM 16th Congress Salzburg 2023 proceedings (OnePetro / Austrian Society) — count papers; boundary with engineering",
 79: "https://sociedadcolombianadegeologia.org/resumenes/ — published resúmenes volume; Spanish search",
 53: "Congresso SGI-SIMP 'Geosciences' (Bari 2024, Potenza 2023): abstract book PDF on socgeol.it / congresso site; Italian search 'abstract book congresso SGI-SIMP'",
 127: "Съезд Общества почвоведов им. Докучаева (IX 2024 Kazan?): тезисы докладов PDF on soilsociety.ru; Russian search",
 111: "日本作物学会講演会 (twice yearly): abstract volumes on J-STAGE — find the journal code (browse/jcsproc?) and read the volume total string '選択された号の論文のN件中'; report the larger edition with events_per_yr=2",
 90: "日本海洋学会秋季大会 (autumn only; spring is inside JpGU): 講演要旨集 on kaiyo-gakkai.jp or J-STAGE; count the autumn edition; Japanese search",
 24: "SCAR OSC 2024 Pucón abstract book (scar2024.org); biennial; 'POLAR' joint years are larger — say which edition",
 25: "ASSW 2025 Boulder / 2024 Edinburgh: programme + abstracts (assw.info); largely a business/science week — judge character",
 27: "Adaptation Futures 2025 Christchurch (Oct 2025) / 2023 Montréal: programme, abstract count; adaptationfutures2025.com",
 29: "FIG Working Week / Congress: every paper is listed on fig.net/resources/proceedings/fig_proceedings/<year>/ — count the technical programme papers for one WW (2025 Brisbane / 2024 Accra)",
 32: "AESC 2025 Adelaide / 2023 Perth: abstract volume on gsa.org.au (GSA Abstracts series)",
 41: "IWRA XIX World Water Congress Marrakech Dec 2025 / XVIII Beijing 2023: programme / abstracts; iwra.org",
 57: "SGA 2025 Golden Colorado (18th Biennial) proceedings volumes (usually 2 vols, countable TOC); e-sga.org",
 95: COP + "OOS2025 (One Ocean Science Congress, Nice 2025) — static per-abstract pages; one-off/irregular cadence — record it honestly",
}
SH = {
 23: "ISA (INTERNATIONAL STUDIES Association, isanet.org) — NOT the sociology ISA. Programme on the ISA convention site / All Academic (CAPTCHA-walled: do not fight it); try isanet.org wp-json media for a program PDF and the convention 'program' pages; ~1,300 panels",
 8: "AAA Annual Meeting: programme historically on Confex — try https://aaa.confex.com/aaa/<year>/meetingapi.cgi/Program and /Paper (open backing API); americananthro.org",
 22: "MPSA: All Academic (CAPTCHA) — use the society's program PDF (mpsanet.org wp-json media?search=program) or the online program's static export",
 195: "ISA Forum of Sociology 2025 Rabat: Confex backing API https://isaconf.confex.com/isaconf/forum2025/meetingapi.cgi/Paper (use --compressed; probe the meeting code — wc2023 pattern) — exclude Withdrawn via the record field; distinct from World Congress (row 88, counted)",
 90: "ICP 2024 Prague (33rd): abstract book / programme; icp2024.com; quadrennial",
 15: "SRCD Biennial 2025 Minneapolis: programme on Confex (srcd.confex.com/srcd/2025/meetingapi.cgi/Program?) or the SRCD program book PDF",
 145: "ICAP 2026 Florence (July 2026) / ICAP 2023 (30th, online?): abstract book / programme; iaapsy.org",
 120: "CLACSO Conferencia Latinoamericana y Caribeña de Ciencias Sociales (10th, Bogotá 2025): programa/ponencias; Spanish search",
 121: "ALAS Congreso Latinoamericano de Sociología (XXXV 2025? / XXXIV Guadalajara 2024?): memorias/ponencias by GT; Spanish search 'ALAS congreso ponencias memoria'",
 24: "Law and Society Association: programme on lawandsociety.org (program PDF; possibly Confex/'Cadmium'); 2025 Chicago",
 80: "ECP 2025 Paphos (19th European Congress of Psychology): abstract book PDF (efpa.eu / ecp2025.eu)",
 92: "IGC 2024 Dublin (35th International Geographical Congress): abstract book / programme (igc2024dublin.org); igu-online.org",
 124: "Indian Science Congress: check whether recent editions were HELD (2024 and 2025 editions were postponed/cancelled per news) — a meeting that does not currently take place is recorded as such; boundary/general-science — judge character; sciencecongress.nic.in",
 86: "IATED Crossref prefix 10.21125: container facet 'EDULEARN24 Proceedings' = 1,739 / EDULEARN25 = 1,696 (phase-1 hint). Verify via the facet + cursor re-derivation as in the field notes §2.4",
 87: "IATED Crossref prefix 10.21125: 'INTED2024 Proceedings' = 1,312 / INTED2025 = 1,255 (phase-1 hint). Same method as ICERI (counted)",
 56: "EARLI 2025 Graz (21st Biennial): book of abstracts / programme (earli.org, conftool?)",
 159: "Deutscher Kongress für Geographie 2023 Frankfurt: 'more than 1,500 presentations, 400+ sessions' claimed in a SNIPPET — open the page; programme on dkg2023.de / dgfg.org; German search 'Deutscher Kongress für Geographie Programm Vorträge'",
 17: "Psychonomic Society 2025 Denver: abstract book PDF published yearly on psychonomic.org (program/abstracts PDF)",
 25: "4S 2025 Seattle / 4S 2024 Amsterdam (joint with EASST): programme (4sonline.org; often on a 'program' site with paper pages)",
 30: "ABAI 2026 (52nd Annual Convention): programme via the ABAI portal (abainternational.org/events); 'program book' PDF",
 67: "DGS Kongress 2024 Duisburg-Essen (42nd): programme (kongress2024.soziologie.de); German search 'Programm Beiträge'",
 91: "IUAES 2023 (Delhi, joint with WAU) / IUAES-WAU 2025 Antigua: programme; iuaes.org",
 93: "IUSSP International Population Conference 2025 Brisbane: programme on iussp.org (Confex-like backend; count sessions × papers), 'IPC2025'",
 101: "SIP Interamerican Congress of Psychology 2025 (40th, Rio? / 39th 2023 Asunción): programa / libro de resúmenes; Spanish/Portuguese search",
 146: "WAC-10 Darwin 2025 (10th World Archaeological Congress, June 2025): programme; worldarch.org",
 147: "EASA 2024 Barcelona (18th Biennial): programme on nomadit.co.uk/conference/easa2024 — NomadIT lists every paper per panel (countable, plain HTML)",
 192: "ICPS 2025 Brussels (APS): programme / abstracts; psychologicalscience.org/conventions/icps — distinct from APS Annual Convention (counted on this sheet already? check duplicate_of)",
 60: "Eurocrim 2025 Athens (25th ESC conference): book of abstracts PDF (esc-eurocrim.org / conference site)",
 74: "Congreso Español de Sociología (XV, 2025?/XIV 2022 Murcia): libro de resúmenes / programa on fes-sociologia.com; Spanish search 'comunicaciones'",
 82: "ESERA 2025 Copenhagen (biennial): book of abstracts / programme (esera2025.org)",
 143: "UMBRELLA: Congress of the Humanities and Social Sciences (Canada) is 70+ associations meeting together; member rows CPSA (152), CSA (153), CSSE (154) are on this sheet but NOT in your queue. Count the umbrella's total contributed papers if an artefact exists (federationhss.ca programme), label it UMBRELLA, and note in duplicate_of that the member associations are inside it",
 9: "SAA: every meeting's abstracts are archived on tDAR — https://core.tdar.org/collection/71737/... (89th New Orleans 2024) and https://core.tdar.org/collection/88704 (all meetings) — count the records for one edition; also saa.org Abstract-Archives page and the final program PDF",
 59: "EAA Annual Meeting 2025 Belgrade / 2024 Rome: 'abstract book' PDF published on e-a-a.org after each meeting (count papers + posters)",
 186: "Congresso Brasileiro de Psicologia: Ciência e Profissão (7th, 2022? 'nearly 6,000 works approved' in a SNIPPET — open the page https://www.7cbp.cbpsi.org.br/atividade/programa); count the programme; quadrennial",
 21: "CIES 2025 Chicago / 2026: programme on cies.us (All Academic? CAPTCHA) — try the program PDF via wp-json media and the CIES 'program' site export",
 116: "SBPC Reunião Anual (77th 2025): resumos on sbpcnet.org.br anais (por edição); general-science congress — boundary; judge character and count",
 118: "ANPUH Simpósio Nacional de História (32nd 2023 / 33rd 2025): anais on anpuh.org.br / snh2025.anpuh.org — count trabalhos; boundary with humanities — flag",
 95: "IAMCR 2025 Singapore / 2024 Christchurch: abstract book per section (iamcr.org publishes abstract books by section — sum sections, check union)",
 183: "CONEDU (Realize Eventos): anais on editorarealize.com.br/anais/ — per edition, count trabalhos; also the Even3/Crossref route; Portuguese",
 184: "EDUCERE (PUCPR) anais on eventum.pucpr.br/educere — count trabalhos per edition",
 185: "ENDIPE (biennial): anais per edition (endipe.com.br / host university); Portuguese search 'anais ENDIPE trabalhos'",
 64: "RGS-IBG Annual International Conference 2025 Birmingham: programme (rgs.org, ex-ordo? or 'conference programme' PDF)",
 189: "IAFOR ACE 2025 Tokyo: 'over 1,640 submissions' is a SNIPPET — open the page; the programme/abstract book PDF is on ace.iafor.org; count accepted presentations, not submissions",
 19: "APPAM Fall Research Conference 2025 Seattle: programme on appam.confex.com — try https://appam.confex.com/appam/2025/meetingapi.cgi/Program and /Paper",
 28: "AEJMC 2025 San Francisco: All Academic (CAPTCHA) — use aejmc.org program PDF / 'paper abstracts' pages; refereed paper counts are often stated per division",
 96: "AILA World Congress 2024 Kuala Lumpur (21st): programme / book of abstracts; aila.info; triennial",
 114: "ANPOCS Encontro Anual (48th 2024 / 49th 2025): anais/programação on anpocs.com — count trabalhos across GTs and SPGs",
 188: "RBA (ABA) 34th Reunião Brasileira de Antropologia 2024: anais on portal.abant.org.br — count trabalhos across GTs",
 196: "EISA PEC 2025 (18th Pan-European Conference): programme (eisa-net.org / conftool); count papers",
 61: "ECREA ECC 2024 Ljubljana (10th): abstract book PDF / programme; ecrea.eu",
 81: "EAWOP 2025 Prague (22nd Congress): programme / abstract book; eawop2025.org",
 115: "SBS Congresso Brasileiro de Sociologia (22nd 2025 / 21st 2023): anais on sbsociologia.com.br — count trabalhos",
 148: "Econometric Society World Congress 2025 Seoul (13th): programme (econometricsociety.org / conference site) — count papers; quinquennial (0.2)",
 132: "SBL Annual Meeting 2025 Boston: program book PDF on sbl-site.org (co-located with AAR, row 131 counted — count SBL's own sessions only); boundary with humanities — flag",
 26: "SSWR 2026 (30th Annual Conference): programme on sswr.confex.com? — try the Confex backing API; sswr.org",
 38: "NARST 2025 National Harbor: programme / abstract book; narst.org",
 191: "NSTA National Conference 2026 Indianapolis: '1,400 presentations and workshops' is a SNIPPET — open the page; practitioner-heavy → judge character (workshop sessions ≈ 1 presentation each, per the NCTM precedent)",
 49: "MLA Convention 2026 Toronto: programme on mla.confex.com (backing API meetingapi.cgi/Program) — ~800 sessions, count papers inside sessions; boundary with humanities — flag",
 50: "ALA Annual Conference 2025 Philadelphia: practitioner meeting; judge character — is there an open research call? count contributed sessions/posters only",
 20: "ACSP 2025 Minneapolis: programme / 'book of accepted abstracts' PDF on acsp.org",
}
def mk(cands, rows, hints):
    q=[]
    for r in rows:
        c = dict(cands[r])
        if r in hints: c['route_hint'] = hints[r]
        q.append(c)
    return q

EARTH_TRAPS = """- **Field notes are your first stop**: `pub.confit.atlas.jp/en/event/<slug>/search?f=&t=presentation` (Japanese meetings — note: curl gets 202/zero bytes, so it is NEEDS_RUNG_5 unless a mirror exists; J-STAGE volume totals work with curl), Copernicus static per-abstract pages, IUGG annual reports, Crossref container facets, society WordPress media APIs (`/wp-json/wp/v2/media?search=program`), government mirrors for Chinese societies.
- **IUGG family**: rows 9/10/11/58/61/62 are association assemblies. IUGG GA (row 8) is already counted. Count each association's own series once; a joint assembly (IAGA-IASPEI 2025, IACS-IAMAS-IAPSO 2025) is ONE meeting.
- **Already counted elsewhere — flag `duplicate_of`, do not count**: AGU, EGU, AMS (physical sciences); AAPG ACE / SEG IMAGE (engineering r188 / earth r19); Aquaculture America & WAS Triennial (row 100); EPSC-DPS joint years count once (rows 22/23).
- **IMPLIED NAME rows** (Chinese/Korean societies): first resolve the real meeting name; if no real recurring meeting exists, say so (outcome UNKNOWN, verdict UNRESOLVED, method explains) — never invent one.
- **Acronym collisions**: IGC = geological ≠ grassland ≠ geographical; ISC, ICG, IPC, ESC, IMS, IAC, SEG, CGS, CBG all collide. Confirm the society's own domain before citing.
- **Trade/policy events** (WFC, ASSW, Adaptation Futures, World Water Congress): the abstracts bar and programme character decide, never the headcount.
- **Cadence**: Events/yr is EMPTY on every row — return it with evidence. Many rows are 0.25 (quadrennial), 0.33, 0.5, 0.2 (IUFRO-style five-yearly), ~0.1 (WCRP decadal), 2 (twice-yearly Japanese societies: report the larger edition, events_per_yr=2).
- **Rung-9 anchors for this field** (from counted wave-1 rows, presentations per attendee): IUGG 89%, AOGS 106%, INQUA 89%, IUFRO ~80%, CBCS 65%, IGC 46%, Aquaculture ~33% (trade hybrid), ICUC 111%. Judge THIS conference's ratio from its own programme wording; name the anchor you reasoned from in `ratio_rationale`; never copy a ratio across.
- Wayback may be offline; DNS failures are not rung 5; password-protected PDFs are not rung 5; credential walls (C-IN portals) are not rung 5."""

SOC_TRAPS = """- **THE PANEL RULE**: count PAPERS inside panels/sessions, never sessions (ECPR 2,077 papers in 539 panels; APSA 5,570 in 1,295). Sanity-check papers per session (~3.7–4.7 at academic congresses; ~1 at practitioner workshop conventions like NCTM).
- **Field-notes routes first**: society WordPress media index (`/wp-json/wp/v2/media?search=program&per_page=50&_fields=source_url,date`, with a Chrome UA + `Accept: application/json`); two-column programme PDFs counted by typography (`pdftohtml -xml -i -stdout`); Confex backing API (`<host>/<meeting>/meetingapi.cgi/Program` and `/Paper`, `--compressed`, probe the meeting code); Crossref container facets (IATED 10.21125, AERA 10.3102, Even3 10.29327 for Brazilian anais); NomadIT conference sites (EASA) list every paper; Drupal `?page=N` pagers (test page 2 vs page 1); J-STAGE for Japan; Korean society file boards.
- **All Academic is CAPTCHA-walled** (APSA/ASA/ASC/MPSA/AEJMC/CIES instances) — do not fight it; find the society's own PDF. Credential walls (member archives) are not rung 5.
- **Search snippets were wrong on real numbers twice in the pilot** — never record a snippet figure; open the page. Several queue notes carry snippet-derived claims (DKG, Congressão, ACE, NSTA, CEC): treat them as hints only.
- **Acronym collisions**: ISA (International Studies vs Sociology — both on this sheet, rows 23 vs 88/195), ASA (sociology/American Studies/African Studies), APA/APS, AAS (Asian vs African Studies), AHA, ECE, ECP, SRA (Risk Analysis vs Research on Adolescence), ICA (Communication vs Cartographic). Confirm the society's own domain.
- **Umbrella and co-located meetings**: Congress of the Humanities and Social Sciences (Canada) contains CPSA/CSA/CSSE; ASSA/JSM already counted as umbrellas; SBL is co-located with AAR (counted) — count SBL's own programme only; ISA Forum ≠ ISA World Congress (counted); ICPS ≠ APS Annual Convention; EPSC-style joint years count once.
- **Practitioner conventions** (NSTA, ALA, NCTE-type): the character judgement decides — is there an open research call and what share of sessions is contributed research? A 60–75-minute workshop is ~1 presentation.
- **Brazilian rows**: anais live on publisher/event platforms (Even3, Realize, Eventum) — the Even3 Crossref facet is a one-call count where the congress deposits; otherwise count the anais listing. Portuguese search terms: anais, trabalhos, resumos.
- **Cadence**: Events/yr is EMPTY on every row — return it with evidence (quadrennial 0.25, triennial 0.33, biennial 0.5, quinquennial 0.2).
- **Rung-9 anchors for this field**: DGPs judged 80% (academic congress built on submitted contributions) vs NCTM 14% (teachers' convention with expo floor) — the only two judged so far; counted rows show ~4 papers per session at academic congresses. Judge THIS conference's ratio from its own wording; name what you reasoned from in `ratio_rationale`; never copy a ratio.
- Wayback may be offline; a 200 may be a 403 body or an HTML catch-all — check status AND content-type AND size."""

plan = [
 ('earth','earth/wave2', E1, EH, 'docs/business/field-notes/earth-sciences.md', 'Earth, environmental & agricultural sciences', EARTH_TRAPS),
 ('earth','earth/wave3', E2, EH, 'docs/business/field-notes/earth-sciences.md', 'Earth, environmental & agricultural sciences', EARTH_TRAPS),
 ('soc','soc/wave2', S1, SH, 'docs/business/field-notes/social-sciences.md', 'Social sciences & education', SOC_TRAPS),
 ('soc','soc/wave3', S2, SH, 'docs/business/field-notes/social-sciences.md', 'Social sciences & education', SOC_TRAPS),
]
status = {"bell": 1, "wave": "A", "started": "2026-09-15T01:00 ET", "searches_used_orchestrator": 1, "waves": {}}
for key, d, rows, hints, notes, field, traps in plan:
    os.makedirs(d, exist_ok=True)
    assert not [f for f in os.listdir(d) if f not in ('BRIEF.md','queue.json')], f'{d} not clean'
    q = mk(E if key=='earth' else S, rows, hints)
    json.dump(q, open(f'{d}/queue.json','w'), ensure_ascii=False, indent=1)
    brief = build_wave_brief(field, notes, f'scratchpad/{d}/queue.json', f'scratchpad/{d}/results.json', f'scratchpad/{d}/STATUS.json', len(q), extra_traps=traps)
    open(f'{d}/BRIEF.md','w').write(brief)
    status['waves'][d] = {"field": field, "rows_queued": len(q), "rows": rows, "rows_returned": 0, "agent": "not started", "rung5_pending": [], "written_back": False, "commit": None, "searches_used": None}
    print(d, len(q), 'rows;', sum('route_hint' in x for x in q), 'hinted; brief', len(brief), 'chars')
json.dump(status, open('census_waves_status.json','w'), indent=1)
print('status file written')
