import json, os, sys, re
sys.path.insert(0, '.')
from streamline import build_wave_brief
exec(open('waveA_prep/build.py').read().split("plan = [")[0])  # loads E, S, EH, SH, traps
E1 = [26,76,65,70,61,62,11,9,10,58,60,17,125,105,119,34,93,96,97,35,36,59,106,103,91,92,82,83,55,118]
E2 = [28,63,68,71,22,23,99,89,81,44,114,128,84,31,101,67,69,79,53,127,111,90,24,25,27,29,32,41,57,95]
S1 = [23,8,22,195,90,15,145,120,121,24,80,92,124,86,87,56,159,17,25,30,67,91,93,101,146,147,192,60,74,82]
S2 = [143,9,59,186,21,116,118,95,183,184,185,64,189,19,28,96,114,188,196,61,81,115,148,132,26,38,191,49,50,20]
unfinished_e = [41,57]; unfinished_s = [147,192,60,74,82]
doneE = set(E1+E2) - set(unfinished_e); doneS = set(S1+S2) - set(unfinished_s)
remE = [r for r in E if r not in doneE]; remS = [r for r in S if r not in doneS]
print('earth remaining', len(remE), 'soc remaining', len(remS))
orderE = unfinished_e + [131,98,64,72,74,102,104,112,120,126,20,88,123,38,40,48,49,50,54,73,85,86,129,130,56,42,108,109,75,115,39,77,87,121,122]
orderS = unfinished_s + [37,34,27,29,31,43,44,54,65,69,70,72,103,105,107,109,127,154,177,199,200,197,167,164,40,48,179,129,130,133,123,122,151,150,155,35,46,172,163,36,45,84,79,77,78,111,112,157,193,198,178,62,102,52,66,128,32,41,42,39,51,53,76,83,75,73,71,100,97,98,99,126,134,135,136,137,138,139,140,141,142,144,149,152,153,156,160,161,165,166,168,169,170,171,173,174,175,176,180,181,182,187,190,194,201,106]
assert len(orderE)==len(set(orderE)) and len(orderS)==len(set(orderS))
missE=[r for r in remE if r not in orderE]; missS=[r for r in remS if r not in orderS]; badE=[r for r in orderE if r not in remE]; badS=[r for r in orderS if r not in remS]
print('missing from order: E', missE, 'S', missS, '| not-remaining in order: E', badE, 'S', badS)
orderE += missE; orderS += missS
EQ = orderE                      # all remaining earth rows (37) on one agent
SQ = orderS[:90]                 # 3 x 30 social
S4, S5, S6 = SQ[0::3], SQ[1::3], SQ[2::3]
print('earth agent', len(EQ), '| soc agents', len(S4), len(S5), len(S6), '| soc left after wave B', len(orderS)-90)
EH2 = {
 41: "IWRA XIX World Water Congress Marrakech (Dec 2025) / XVIII Beijing 2023: programme / abstracts on iwra.org; count sessions x papers",
 57: "SGA 2025 Golden Colorado (18th Biennial) proceedings volumes (countable TOC); e-sga.org",
 131: "Phase-1 figure: 300 orals + 208 posters = 508 in 2025 (Tuebingen) — OPEN the DBG page (dbges.de / jahrestagung site) and confirm; <800 on positive evidence = OUT",
 98: "Copernicus static per-abstract pages https://meetingorganizer.copernicus.org/ECSS2025/ECSS2025-<n>.html (test the <title>, not status; some meetings use 200/302 instead — test a known-good and known-absent id first)",
 64: "IAS International Meeting of Sedimentology (Aberdeen 2025 / Izmir 2027): abstract book PDF on the IAS site; distinct from ISC (row 63, counted 724)",
 72: "Meteoritical Society annual meeting runs on LPI/USRA: try the unwalled asset path https://www.hou.usra.edu/meetings/metsoc2025/pdf/<abstract-number>.pdf (HEAD-enumerate ids, clean 404 for missing) as for LPSC; HTML pages are Cloudflare 403",
 74: "ICOP 2024 Whitehorse (12th International Conference on Permafrost): abstract book PDF (icop2024.org / permafrost.org)",
 102: "ICID 26th Congress Marrakech 2025 / 25th Vizag 2023 + World Irrigation Forum: abstract volume PDFs on icid-ciid.org",
 104: "XII IRC 2023 Covington KY was JOINT with the XXV International Grassland Congress (row 103, counted 416 — the joint edition is ONE meeting): set duplicate_of row 103 if your latest edition is that joint one; else count a standalone IRC (e.g. 2021 Nairobi)",
 112: "J-STAGE volume total: https://www.jstage.jst.go.jp/browse/agrmet2/-char/ja → contents page string '選択された号の論文のN件中' for the 全国大会 講演要旨 volume",
 120: "Argentine soil congress alone (non-joint years, e.g. XXVIII 2022 / XXIX 2024): actas/resúmenes; in joint years it is row 119's meeting — flag duplicate_of",
 126: "Swiss Geoscience Meeting abstract volume PDF per year on https://geoscience-meeting.ch/ (sgm<year>/abstracts) — count abstracts per symposium, sum, check union",
 20: "AAPG ICE (international, non-US) — check whether the series still runs after the IMAGE merger (row 19); Crossref prefix 10.1306 has no ICE container (field notes); AAPG Search & Discovery lists ICE abstracts per edition",
 88: "Geomodel / Saint Petersburg (EAGE-affiliated, geomodel.ru/spb26): EAGE is already counted on physical sciences — if this is an EAGE event, flag duplicate_of; Russian search",
 123: "SEG = Society of ECONOMIC Geologists (segweb.org), NOT the geophysics SEG; SEG 2025 Conference abstracts/program PDF",
 39: "IMPLIED NAME — resolve first (Indian Geological Congress / Geological Society of India annual convention); if no real recurring meeting, UNRESOLVED with the trail",
 77: "IMPLIED NAME — resolve first (NMGS Annual International Conference, nmgs.org.ng)",
 87: "IMPLIED NAME — resolve first (Geological Society of Iran symposium, gsi.ir? / Persian search همایش انجمن زمین‌شناسی ایران)",
 121: "IMPLIED NAME — resolve first (Israel Geological Society annual meeting, igs.org.il; abstracts booklet PDF is published yearly — count)",
 122: "IMPLIED NAME — resolve first (Nepal Geological Society / Nepal Geological Congress, ngs.org.np)",
 56: "PDAC: trade convention — the abstracts bar and programme character decide, never the 25,000 headcount; look for a technical program with contributed talks",
 42: "World Water Week: session-proposal event, not abstract-based — character decides",
 108: "Esri UC: product/user sessions, no peer-reviewed call — character decides",
 109: "INTERGEO: trade fair + conference — count the contributed-paper share only",
 75: "Groundwater Week (NGWA): mostly trade/training; count the contributed technical presentations only",
 115: "中国农学会年会: umbrella forum — character decides; Chinese search",
 38: "CONBEA (SBEA): anais per edition — Brazilian anais may sit on Even3 (Crossref prefix 10.29327 container facet) or a host university; Portuguese search",
 40: "AWRA annual conference: program PDF on awra.org (count presentations)",
 48: "CMOS Congress: abstract book / programme (cmos.ca; Confex? probe cmos.confex.com meetingapi.cgi/Program)",
 49: "AMOS annual meeting: abstract book / programme PDF (amos.org.au)",
 50: "RMetS annual conference: programme (rmets.org); likely small",
 54: "CAG (Colloquium of African Geology): abstract volume PDF per edition (CAG30 2025? Geological Society of Africa)",
 73: "CBGA congress (XXII 2022 Plovdiv?): abstract volume PDF",
 85: "Geocongress (GSSA, biennial): abstract volume / programme",
 86: "GSNZ annual conference: abstracts volume (Geoscience Society of NZ Miscellaneous Publication series, PDF)",
 129: "NGC Malaysia (Geological Society of Malaysia): proceedings / abstract volume PDF (gsm.org.my)",
 130: "IAGOD Quadrennial Symposium (2026 Porto / 2022?): abstract volume",
}
SH2 = {
 147: "EASA 2024 Barcelona: NomadIT programme https://nomadit.co.uk/conference/easa2024 lists every paper per panel (plain HTML) — count papers, exclude roundtables/labs",
 192: "ICPS 2025 Brussels (APS International Convention of Psychological Science): programme / abstract listing; distinct from the APS Annual Convention (on this sheet already — check duplicate_of)",
 60: "Eurocrim 2025 Athens (ESC): book of abstracts PDF on the conference site / esc-eurocrim.org",
 74: "Congreso Español de Sociología (FES, triennial; XV 2025?): libro de resúmenes / programa; Spanish 'comunicaciones'",
 82: "ESERA 2025 Copenhagen: book of abstracts / programme (esera2025.org)",
 37: "ISTE Live: practitioner convention — character decides; count only contributed research/poster sessions if an open research call exists",
 34: "NCTE Annual Convention: practitioner convention — character decides (workshop sessions ≈ 1 presentation); look for a program PDF",
 35: "NAEYC Annual Conference: practitioner — character decides", 46: "NASP Convention: practitioner-heavy but has a research poster call — count posters + papers", 172: "SHAPE America: practitioner — character decides", 163: "TESOL: practitioner — character decides", 165: "ACTFL: practitioner — character decides", 166: "CEC Convention: practitioner + research posters — count contributed", 201: "NAEA: practitioner — character decides",
 27: "CSWE APM: programme on cswe.org (maybe Confex-like 'APM program' or All Academic); count papers + posters",
 29: "SIOP Annual Conference: program on siop.org; SIOP publishes 'accepted submissions' counts in its program; count posters + symposia papers",
 31: "ACJS Annual Meeting: program book PDF on acjs.org (count papers inside panels)",
 43: "AAEA Annual Meeting: AgEcon Search deposits selected papers (a floor); the program PDF on aaea.org is the artefact",
 44: "SRA Biennial (Society for Research on Adolescence) 2026: program on s-r-a.org (Confex? probe sra.confex.com or the SRA 'program book')",
 54: "ICQI (International Congress of Qualitative Inquiry): program PDF on icqi.org — count papers",
 65: "EASP General Meeting 2026 (triennial): programme / abstract book",
 69: "DGfE Kongress 2026 (biennial): programme on the host site (ConfTool likely) — count Beiträge",
 70: "GEBF Tagung 2026: programme (ConfTool?) — count Beiträge",
 72: "Congrès de l'AFS 2025 (biennial): programme by RT (research networks) on afs-socio.fr — count communications",
 103: "ISSBD 2026 Biennial Meeting: programme / abstract book",
 105: "日本教育心理学会総会: proceedings 発表論文集 on J-STAGE (search the journal code via jstage browse; API cdjournal=<code>&vol=) — one volume per convention",
 107: "日本社会学会大会: 報告要旨 on jss-sociology.org (大会報告要旨 PDF per 大会) — count reports",
 109: "中国社会学会学术年会: forum count and papers per forum from the society site / news mirrors; Chinese search",
 127: "ASEEES Convention: All Academic (CAPTCHA) likely — find the program PDF on aseees.org (wp-json media)",
 154: "CSSE meets inside Congress (row 143, umbrella counted ~4,350 inferred): count CSSE's own programme (csse-scee.ca program PDF) and set duplicate_of 'contained in row 143 umbrella'",
 152: "CPSA meets inside Congress (row 143 umbrella): count CPSA's own programme (cpsa-acsp.ca conference programme) and flag duplicate_of row 143",
 153: "CSA meets inside Congress (row 143 umbrella): count CSA's own programme (csa-scs.ca) and flag duplicate_of row 143",
 177: "WEAI Annual Conference: program on weai.org (session listing with papers)",
 199: "SASE Annual Meeting: programme (sase.org; often Confex or 'program' pages) — count papers",
 200: "ICPP (IPPA, biennial; ICPP7 2025 Chiang Mai): programme with papers per panel on ippapublicpolicy.org",
 197: "CPA National Convention: programme / abstract book PDF (cpa.ca)",
 167: "AEA Evaluation conference: program on evaluationconference.org (count sessions x papers; posters)",
 164: "AAAL Annual Conference: program book PDF on aaal.org",
 40: "SRA (Society for Risk Analysis) Annual Meeting: program/abstract book on sra.org; Crossref co-listing with ESREL is a trap",
 48: "AHA Annual Meeting: program on historians.org (session listing; count papers inside ~300 sessions); boundary with humanities — flag",
 179: "International Cartographic Conference (ICA, biennial; ICC 2025 Vancouver): proceedings on Copernicus 'Proceedings of the ICA' / 'Abstracts of the ICA' (Crossref / static pages) — count abstracts",
 129: "ASA = AMERICAN STUDIES Association (theasa.net), not sociology: program (All Academic? or program PDF)",
 130: "ASA = AFRICAN Studies Association (africanstudies.org): program PDF",
 133: "NWSA: program on nwsa.org (Confex? probe nwsa.confex.com meetingapi.cgi/Program)",
 123: "Indian Sociological Society All India Sociological Conference: programme / abstracts on insoso.org",
 122: "Jornadas de Sociología UBA (biennial): programa/ponencias on jornadasdesociologia.sociales.uba.ar — count ponencias",
 151: "PSA (UK Political Studies Association) Annual Conference: programme (psa.ac.uk, ex-ordo/conftool) — count papers",
 150: "World Economic History Congress 2025 Lund (triennial): programme (sessions x papers) on wehc2025.org",
 155: "UAPS African Population Conference (quadrennial): programme on uaps-uepa.org (Confex-like)",
 36: "AECT Convention: program on aect.org (count concurrent sessions/papers)",
 45: "Society for Prevention Research: abstract book PDF on preventionresearch.org",
 84: "AESOP Congress 2025 Istanbul: book of abstracts PDF",
 79: "EAERE Annual Conference 2025 Bergen: programme with papers (eaere-conferences.org) — count",
 77: "BERA Conference 2025: programme / abstract book (bera.ac.uk)",
 78: "BPS Annual Conference: programme / abstract book (bps.org.uk)",
 111: "AARE Conference 2025: program / abstracts (aare.edu.au) — count",
 112: "APS (Australian Psychological Society) Congress/Festival: programme; likely small — count",
 157: "ALAP Congreso (biennial): ponencias listing on alapop.org",
 193: "Sunbelt (INSNA) 2025 Paris: programme (abstract book PDF) — count paper + poster abstracts",
 198: "UAA Conference: program PDF on urbanaffairsassociation.org",
 178: "Southern Economic Association: program on southerneconomic.org (Confex? probe southerneconomic.confex.com)",
 62: "European Population Conference 2026 (EAPS, biennial): programme on eaps.nl / Confex-like",
 102: "IACCP Congress 2026 (biennial): programme / abstract book",
 52: "NARSC (RSAI North American): program on narsc.org — count papers",
 66: "ESRA Conference 2025 (biennial): programme (europeansurveyresearch.org) — count papers",
 128: "MESA Annual Meeting: program (mesana.org, All Academic likely CAPTCHA — find PDF)",
 32: "ASHE Conference: program on ashe.ws (count papers + posters)",
 187: "IMPLIED NAME — CBAS (Congresso Brasileiro de Assistentes Sociais, CFESS, triennial; 17th 2022?): anais on cfess.org.br / Dype platform; resolve name first",
 190: "IAFOR ECE: https://ece.iafor.org/accepted-presentations/ pattern (as ACE, row 189 counted 1,006) — count accepted presentations, not submissions",
 180: "IMPLIED NAME — Women's Worlds Congress (triennial; WW 2023 Kigali?): resolve the real event first",
 181: "IMPLIED NAME — Iranian Psychological Association congress: resolve via Persian search (کنگره انجمن روانشناسی ایران)",
 182: "IMPLIED NAME — Iranian Sociological Association congress: Persian search (همایش انجمن جامعه‌شناسی ایران)",
 194: "SWSD 2026 Nairobi (biennial): programme / abstract book (swsd2026.or.ke)",
 138: "Russian Psychological Society congress: 1,417 participants is a SNIPPET claim — open psyrus.ru pages; Russian search (съезд РПО тезисы)",
 137: "Ulusal Psikoloji Kongresi (Turkish, biennial): bildiri özetleri kitabı PDF; Turkish search",
 136: "Ulusal Eğitim Bilimleri Kongresi: bildiri özetleri kitabı; Turkish search",
 139: "Congreso Nacional de Psicología (COP, Spain): libro de resúmenes; Spanish search",
 140: "AIDIPE congreso: libro de actas/resúmenes; Spanish",
 141: "KONASPI (quadrennial, Indonesia): proceedings; Indonesian search",
 142: "한국교육학회 연차학술대회: 자료집 on the society file board (KPA-style download.html?fno=)",
 144: "CODESRIA General Assembly (triennial): programme; largely curated — character decides",
 149: "IEA World Congress 2026 (triennial): programme on iea-world.org (Confex-like) — count papers",
 156: "Asian Population Association conference (triennial): programme (asianpa.org)",
 160: "EUGEO Congress 2025 (biennial): programme / book of abstracts",
 161: "日本地理学会大会 (spring/autumn): 発表要旨集 on J-STAGE (journal code for 日本地理学会発表要旨集; volume total string) — report the larger edition, events_per_yr=2",
 168: "AACE (E-Learn / SITE / EdMedia): LearnTechLib proceedings per conference (countable) — pick ONE conference as the unit and say so",
 169: "ICDE World Conference (biennial): programme",
 170: "HERDSA: programme / abstracts on herdsa.org.au",
 171: "ICSEI Congress: programme (icsei.net)",
 173: "ASPA Annual Conference: program on aspanet.org",
 174: "EGPA Conference: programme by permanent study group (egpa-conference.org) — count papers",
 175: "IIAS Congress: programme (iias-iisa.org)",
 176: "ENHR Conference: programme by workshop (enhr.net) — count papers",
 100: "IFLA WLIC: library.ifla.org deposits the congress papers (countable, a floor); programme sessions ~500 — count papers",
 97: "WERA Focal Meeting: usually held inside a member association's conference — check duplicate_of (e.g. inside AERA/ECER) before counting",
 98: "WCCES World Congress (triennial; XIX 2025?): programme / abstract book",
 99: "ISLS Annual Meeting (ICLS+CSCL): Crossref/ISLS repository per year — ICLS 2025 = 620 papers (phase-1 hint); count both tracks of one year, do not double count",
 126: "AAS = Association for ASIAN Studies (asianstudies.org): program (All Academic? CAPTCHA) — find PDF",
 134: "SIPED Convegno Nazionale: programma / atti (siped.it); Italian search",
 135: "Onderwijs Research Dagen: programma boek (Dutch search 'ORD <jaar> programma')",
 41: "AAPOR conference: program on aapor.org (count papers + posters)",
 42: "SREE conference: program (sree.org / Confex-like) — count",
 39: "LSA (Linguistic Society of America) Annual Meeting: abstracts/program on lsadc.org (count papers + posters)",
 51: "SSSP Annual Meeting: program PDF on sssp1.org",
 53: "Eastern Psychological Association: program PDF (large poster meeting) — count posters + papers",
 76: "NERA Congress: programme (nera-education.org / ConfTool)",
 83: "ATEE Annual Conference: book of abstracts PDF",
 75: "AIS Convegno Nazionale (Italian sociology, biennial): programma; Italian search",
 73: "Congrès de l'AFSP (biennial): programme by section thématique (afsp.info) — count communications",
 71: "DVPW Kongress (triennial): programme (ConfTool) — count Beiträge",
}
os.makedirs('earth/wave4', exist_ok=True)
for d in ['soc/wave4','soc/wave5','soc/wave6']: os.makedirs(d, exist_ok=True)
NEW_ROUTES = """
## Routes and traps learned tonight (wave A, 2026-09-15) — additions to the field notes
- **Dype Soluções platform** runs many Brazilian society congresses (CFP, ANPUH, ANPOCS, RBA, SBS): `/atividade/programacao` (whole programme) and `/atividade/hub/<track>`; papers are `<p class="m-4">` on consolidated pages — but consolidated pages can PAD (ANPOCS 423 vs 357 on detail pages): verify on detail pages.
- **Realize Eventos** (CONEDU, ENDIPE): schedule table carries `data-ajax-url=".../base/api/divulgacoes/trabalhosAlocados"` returning every session with its works (open JSON).
- **Confex is alive** for SSWR, MLA, ISA (`<host>/<meeting>/meetingapi.cgi/Paper`, `--compressed`) — probe the host before assuming a society left it.
- **All Academic**: APPAM's instance issues a guest session and browse pages render to curl; AEJMC/APSA/ASA/ASC/MPSA still serve the reCAPTCHA stub. AEJMC publishes accepted abstracts as an .xlsx on its Higher Logic S3 bucket.
- **WebFetch clears some Cloudflare walls curl cannot** (federationhss.ca, igc2024dublin.org) — try it before declaring rung 5; it did not help on SBL/ACSP/plantprotection.org.
- **Oxford Abstracts**: `/event/<id>/titles` states the total submissions; `apigw.oxfordabstracts.com/services/program-pdf?event_id=<id>` serves the programme PDF unauthenticated (sessions only).
- **C-IN portals** (czech-in.org cmPortalV15): the guest 'Abstract List' states the total (browser only).
- **MiraSmart** (AAS/DPS): two-step cookie handshake (fetch Itinerary/ with a jar, then EventsAAG.aspx with the jar) yields the full server-rendered programme.
- **WAS abstract books**: `wasblobstorage.blob.core.windows.net/meeting-abstracts/<CODE>AbstractBook.pdf` — HEAD tells you which editions exist.
- **Unwalled WordPress mirrors** of Cloudflare-blocked societies exist (mineralogy-ima-wordpress.website); WordPress REST APIs may live at `/api/` instead of `/wp-json/` (IAVCEI). Media API `?search=` works where `mime_type=` returns 400.
- **Programme data as a JS literal** (`EMBEDDED={...}`, ESC 2026) — a text extractor sees an empty page; grep the HTML for JSON.
- **Google Drive public folders** list via `drive.google.com/embeddedfolderview?id=<id>#list`; files via `drive.usercontent.google.com/download?id=<id>&export=download&confirm=t` (content-type octet-stream).
- **Crossref**: member+year faceting beats container filters (comma in a container title breaks the filter; `container-title` arrays double-count SGEM). Container filters need the exact string.
- **Copernicus title discriminator varies**: EPSC2026/EPSC-DPS2025 title `Abstract <SLUG>-<n>`; EPSC2022/ICG2022 title every page `CO Meeting Organizer <SLUG>` and the discriminator is HTTP 200 vs 302. Test a known-good and known-absent id first.
- **Dead domains that return HTTP 200**: Wayback-downloader demo stubs (suelossantacruz2025.com), domain-broker sale pages (ippcathens2024.gr, sociedadgeologicamexicana.org.mx), gambling squatters (sbagro.org→olxbaut.com, icme15.org), empty documents (cbagro2025.com.br content-length 0). Check the body, never the status.
- **Credential walls are not rung 5**: Ex Ordo event spaces 'restricted to registered delegates' (RGS-IBG), eventi.unibo.it (IAG), IPSA library. **reCAPTCHA v2 is a human wall** (ABAI).
- **Wayback / Internet Archive** was HTTP 503 all night — do not build a route on it.
"""
EARTH_TRAPS = open('waveA_prep/build.py').read().split('EARTH_TRAPS = """')[1].split('"""')[0] + NEW_ROUTES
SOC_TRAPS = open('waveA_prep/build.py').read().split('SOC_TRAPS = """')[1].split('"""')[0] + NEW_ROUTES
def mk(cands, rows, hints, base):
    q=[]
    for r in rows:
        c=dict(cands[r]); h = hints.get(r) or base.get(r)
        if h: c['route_hint']=h
        q.append(c)
    return q
plan=[('earth','earth/wave4',EQ,EH2,EH,'docs/business/field-notes/earth-sciences.md','Earth, environmental & agricultural sciences',EARTH_TRAPS),
      ('soc','soc/wave4',S4,SH2,SH,'docs/business/field-notes/social-sciences.md','Social sciences & education',SOC_TRAPS),
      ('soc','soc/wave5',S5,SH2,SH,'docs/business/field-notes/social-sciences.md','Social sciences & education',SOC_TRAPS),
      ('soc','soc/wave6',S6,SH2,SH,'docs/business/field-notes/social-sciences.md','Social sciences & education',SOC_TRAPS)]
st=json.load(open('census_waves_status.json'))
for key,d,rows,h2,h1,notes,field,traps in plan:
    q=mk(E if key=='earth' else S, rows, h2, h1)
    json.dump(q, open(f'{d}/queue.json','w'), ensure_ascii=False, indent=1)
    open(f'{d}/BRIEF.md','w').write(build_wave_brief(field, notes, f'scratchpad/{d}/queue.json', f'scratchpad/{d}/results.json', f'scratchpad/{d}/STATUS.json', len(q), extra_traps=traps))
    st['waves'][d]={"field":field,"wave":"B","rows_queued":len(q),"rows":rows,"rows_returned":0,"agent":"prepared (not dispatched)","rung5_pending":[],"written_back":False,"commit":None,"searches_used":None}
    print(d, len(q), 'rows;', sum('route_hint' in x for x in q), 'hinted')
st['wave_B_leftover_soc_rows']=orderS[90:]
json.dump(st, open('census_waves_status.json','w'), indent=1)
print('soc rows left for Rupert after wave B:', orderS[90:])
