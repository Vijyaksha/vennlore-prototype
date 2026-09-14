"""Build `Census - CS & Engineering` from DBLP (primary) + Crossref (second source).

Usage:  python3 build_cs_sheet.py --dry   # print the review tables, write plan.json, touch nothing
        python3 build_cs_sheet.py         # create the sheet pair and write every row

Inputs (pulled 2026-09-13, see dblp_probe/):
  dblp_probe/cand_by_year.json   per-stream per-year counts 2018-2025 for streams >=800 in 2024 or 2025
  dblp_probe/cand_volumes.json   per-volume counts for 2024/2025 (workshop split)
  dblp_probe/cand_meta.json      stream titles
  dblp_probe/crossref_proc_{2024,2025}.json   Crossref proceedings-article container-title facets
  dblp_probe/existing_names.json every conference already on any census/deleted sheet
"""
import json, sys, os, re, collections
sys.path.insert(0, "/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad")
import dblplib, chemlib, writeback, dedupe

D = "/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/cs/dblp_probe"
FIELD = "CS & Engineering"
TODAY = "2026-09-13"

def sp(name):
    return json.load(open(f"{D}/{name}"))["results"]["bindings"]

def key(iri):
    return iri.split("/streams/")[-1]

# --- DBLP side -------------------------------------------------------------
yearly = {(key(b["stream"]["value"]), int(b["year"]["value"])): int(b["n"]["value"]) for b in sp("cand_by_year.json")}
vols = [dict(stream=key(b["stream"]["value"]), year=int(b["year"]["value"]), vtitle=b["vtitle"]["value"], n=int(b["n"]["value"]))
        for b in sp("cand_volumes.json")]
meta = dblplib.one_row_per_stream([dict(stream=key(b["stream"]["value"]), title=b["title"]["value"],
                                        acr=b.get("acrs", {}).get("value", "")) for b in sp("cand_meta.json")])
split = dblplib.main_track_split(vols)

# --- Crossref side -----------------------------------------------------------
xr = {}   # series_key -> {year: (count, title)}
for y in (2024, 2025):
    vals = json.load(open(f"{D}/crossref_proc_{y}.json"))["message"]["facets"]["container-title"]["values"]
    for title, n in vals.items():
        if n < 300 or dblplib.is_not_a_conference(title) or dblplib.is_workshop_volume(title):
            continue
        k = dblplib.series_key(title)
        xr.setdefault(k, {})
        if y not in xr[k] or n > xr[k][y][0]:
            xr[k][y] = (n, title)

def crossref_match(title, year):
    """Best Crossref series for a DBLP stream title: acronym match, else token overlap."""
    acr = dblplib._acronyms(title)
    toks = dblplib._tokens(title)
    best = None
    for k, years in xr.items():
        if year not in years:
            continue
        n, xt = years[year]
        xa = dblplib._acronyms(xt)
        xtoks = dblplib._tokens(xt)
        score = None
        if acr and xa and (acr & xa):
            score = (2, n)                      # an acronym match always beats a word match
        elif ALIAS.get(title) and ALIAS[title].lower() in xt.lower():
            score = (3, n)
        elif toks and xtoks and len(toks & xtoks) >= max(3, int(0.7 * min(len(toks), len(xtoks)))):
            score = (1, n)
        if score and (best is None or score > best[0]):
            best = (score, n, xt, k)
    return best

ALIAS = {"ACM International Conference on Multimedia (MM)": "ACM International Conference on Multimedia",
         "Conference of the International Speech Communication Association (INTERSPEECH)": "Interspeech"}
CADENCE_OVERRIDE = {"conf/eccv": (0.5, "ECCV is biennial (even years); DBLP dates the ECCV 2024 LNCS volumes 2025, so the 2025 count IS the 2024 edition"),
                    "conf/iccv": (0.5, "ICCV is biennial (odd years)")}
TIER_OVERRIDE = {"IEOM International Conference on Industrial Engineering and Operations Management":
                 ("BORDERLINE", "the Crossref container aggregates several IEOM conferences a year, so 1,525 is an upper bound on any single meeting — BORDERLINE, not VERIFIED")}

existing = json.load(open(f"{D}/existing_names.json"))
ENG_STREAMS = {"icassp", "igarss", "icra", "iros", "embc", "icc", "globecom", "vtc", "cdc", "iecon", "isbi", "iscas",
               "smc", "wcnc", "apsipa", "icme"}
BOUNDARY_STREAMS = {"cogsci": "cognitive science society (psychology / CS)", "hicss": "information systems / management",
                    "bibm": "bioinformatics (IEEE) — ISMB sits on the life-sciences sheet", "miccai": "medical imaging (CS side; MICCAI society)",
                    "embc": "biomedical engineering — BMES sits on the medicine sheet", "isbi": "biomedical imaging"}

rows, dupes, review = [], [], []
used_xr = set()
for m in meta:
    s = m["stream"]
    y = dblplib.latest_year(s, split)
    if y is None:
        continue
    main, ws = split[(s, y)]["main"], split[(s, y)]["workshop"]
    ev = dblplib.cadence(s, yearly)
    cm = crossref_match(m["title"], y)
    xr_n, xr_t = (cm[1], cm[2]) if cm else (None, None)
    if cm:
        used_xr.add(cm[3])
    if s in CADENCE_OVERRIDE:
        ev = CADENCE_OVERRIDE[s][0]
    row = dblplib.census_row(s, m["title"], y, main, ws, ev, crossref=xr_n, crossref_title=xr_t)
    if s in CADENCE_OVERRIDE:
        row["method"] += f"  ||  CADENCE OVERRIDE: {CADENCE_OVERRIDE[s][1]}"
    row["stream"] = s
    row["subfield"] = ("engineering (IEEE society meeting)" if key(s).split("/")[-1] in ENG_STREAMS else "CS / AI")
    if key(s).split("/")[-1] in BOUNDARY_STREAMS:
        row["subfield"] += " — BOUNDARY: " + BOUNDARY_STREAMS[key(s).split("/")[-1]]
    hit = dblplib.find_existing(m["title"], existing)
    if hit:
        dupes.append(dict(conference=m["title"], counted_on=hit["sheet"], stream=s, main=main, year=y,
                          existing=hit["conference"]))
    else:
        rows.append(row)

# Crossref-only series (>=800 in 2025 or 2024) not matched to any DBLP stream
xr_only = []
for k, years in xr.items():
    if k in used_xr:
        continue
    y = 2025 if 2025 in years else 2024
    n, t = years[y]
    if n < 800:
        continue
    hit = dblplib.find_existing(t, existing)
    xr_only.append(dict(series=k, title=t, year=y, n=n, existing=(hit["sheet"] + " / " + hit["conference"]) if hit else None))


# Curated review of the Crossref-only list (orchestrator, 2026-09-13). Key = substring of the container title.
CROSSREF_ADD = {  # engineering / CS series DBLP does not carry as a candidate stream -> rows on THIS sheet
    "Chinese Control Conference": ("Chinese Control Conference (CCC)", 1, "engineering — control (TCCT / CAA, China)"),
    "China Automation Congress": ("China Automation Congress (CAC)", 1, "engineering — automation (CAA, China)"),
    "Chinese Control and Decision Conference": ("Chinese Control and Decision Conference (CCDC)", 1, "engineering — control (China)"),
    "Industrial Engineering and Operations Management": ("IEOM International Conference on Industrial Engineering and Operations Management", 1,
        "engineering — industrial; NOTE the Crossref container aggregates several IEOM conferences per year, so this is an upper bound on any one meeting"),
    "Encontro Nacional de Engenharia de Produção": ("ENEGEP — Encontro Nacional de Engenharia de Produção (ABEPRO, Brazil)", 1, "engineering — industrial (Brazil)"),
    "International Congress of Mechanical Engineering": ("COBEM — International Congress of Mechanical Engineering (ABCM, Brazil)", 0.5, "engineering — mechanical (Brazil, biennial)"),
    "AHFE International": ("AHFE International Conference (Applied Human Factors and Ergonomics)", 1, "engineering — human factors"),
    "LACCEI International Multi-Conference": ("LACCEI International Multi-Conference for Engineering, Education and Technology", 1, "engineering — Latin American multi-conference"),
    "Antennas and Propagation and INC/USNC": ("IEEE International Symposium on Antennas and Propagation and USNC-URSI Radio Science Meeting (AP-S/URSI)", 1, "engineering — antennas (IEEE APS)"),
    "Energy Conversion": ("IEEE Energy Conversion Congress and Exposition (ECCE)", 1, "engineering — power electronics (IEEE PELS/IAS)"),
    "European Conference on Antennas and Propagation": ("European Conference on Antennas and Propagation (EuCAP)", 1, "engineering — antennas (EurAAP)"),
    "EAGE Annual Conference": ("EAGE Annual Conference & Exhibition", 1, "engineering/geoscience — geophysics (EAGE); BOUNDARY with earth sciences"),
    "ADIPEC": ("ADIPEC (Abu Dhabi International Petroleum Exhibition and Conference) technical conference", 1, "engineering — petroleum (SPE-run technical programme); BOUNDARY: trade show with a technical conference"),
    "Photonics &amp; Electromagnetics Research Symposium": ("PIERS — Photonics & Electromagnetics Research Symposium", 1, "engineering — electromagnetics; BOUNDARY with physics"),
    "Plasma Science (ICOPS)": ("IEEE International Conference on Plasma Science (ICOPS)", 1, "engineering/physics — plasma (IEEE NPSS); BOUNDARY with physics"),
    "Power Electronics and Motion Control Conference": ("IEEE International Power Electronics and Motion Control Conference (IPEMC / ECCE Asia)", 0.25, "engineering — power electronics (every ~4 years)"),
    "Microwave and Millimeter Wave Technology": ("International Conference on Microwave and Millimeter Wave Technology (ICMMT)", 0.5, "engineering — microwave (China, biennial)"),
    "Forum Acusticum": ("Forum Acusticum / Euronoise (European Acoustics Association)", 0.33, "engineering/physics — acoustics (triennial); BOUNDARY with physics (ASA is on the physical sheet)"),
    "Computer and Information Technology (ICCIT)": ("International Conference on Computer and Information Technology (ICCIT, Bangladesh)", 1, "CS — general (IEEE Bangladesh)"),
    "MECÂNICA DOS SOLOS": ("COBRAMSEG — Congresso Brasileiro de Mecânica dos Solos e Engenharia Geotécnica (ABMS)", 0.5, "engineering — geotechnical (Brazil, biennial)"),
}
HANDOVER = {  # >=800 in Crossref but not this field: recorded for the next census, not loaded here
    "AERA Annual Meeting": "social sciences — education (AERA ~4,700 papers/yr): the largest social-science meeting seen so far",
    "AERA 2025": "duplicate container of the AERA row above",
    "EDULEARN": "education (IATED) — social sciences lead; low-selectivity commercial-academic conference",
    "ICERI": "education (IATED) — social sciences lead",
    "INTED": "education (IATED) — social sciences lead",
    "Congresso de Iniciação Científica": "undergraduate research congress (UFPE, Brazil) — general/student research, like NCUR",
    "Cosmic Ray Conference": "physics (ICRC, biennial) — physical-sciences sheet lead",
    "ESGE Days": "medicine — gastroenterology (check whether ESGE Days is on the medicine sheet)",
    "Endoscopy": "journal supplement carrying ESGE Days — same meeting",
    "Skull Base": "medicine — already on the medicine sheet (North American Skull Base Society)",
    "Arquivos de Neuro-Psiquiatria": "journal supplement (Brazilian neurology congress abstracts) — medicine lead",
    "São Paulo Medical Journal": "journal supplement — medicine lead (identify the congress)",
    "Zeitschrift für Gastroenterologie": "journal supplement (DGVS Viszeralmedizin) — medicine lead",
    "Medicina General y de Familia": "medicine — Spanish family-medicine congress (SEMG) lead",
    "BJN Abstract": "journal supplement (Brazilian Journal of Nephrology congress) — medicine lead",
    "Regular and Young Investigator Award Abstracts": "unidentifiable container title (a medical society's abstract supplement) — skip",
    "Poster Presentations": "unidentifiable container title — skip",
    "ABM Proceedings": "ABM (Brazilian metallurgy association) week — engineering/materials lead, title too generic to count safely",
    "Geological Society of America": "already on the physical-sciences sheet (GSA Connects)",
    "Goldschmidt": "already on the chemistry sheet",
    "CLEO": "already on the physical-sciences sheet",
    "AIAA": "already on the physical-sciences sheet",
    "Lasers and Electro-Optics Europe": "already on the physical-sciences sheet (CLEO/Europe-EQEC)",
    "Language Resources and Evaluation": "LREC-COLING 2024 joint volume — LREC is a DBLP row",
    "Findings of the Association": "Findings volumes are inside the ACL/EMNLP DBLP streams",
    "CHI Conference": "CHI is a DBLP row",
    "Empirical Methods in Natural Language Processing": "EMNLP main volume — EMNLP is a DBLP row (the Findings volume was the matched cross-check)",
    "Annual Meeting of the Association for Computational Linguistics": "ACL Volume 1 — ACL is a DBLP row",
    "Interspeech": "Interspeech is a DBLP row",
    "Computer Vision (ICCV)": "ICCV is a DBLP row", "Neural Networks (IJCNN)": "IJCNN is a DBLP row",
    "Robotics and Automation (ICRA)": "ICRA is a DBLP row", "Winter Conference": "WACV is a DBLP row",
}
xr_rows, handed = [], []
for x in list(xr_only):
    t = x["title"]
    add = next((v for k, v in CROSSREF_ADD.items() if k.lower() in t.lower()), None)
    ho = next((v for k, v in HANDOVER.items() if k.lower() in t.lower()), None)
    if add:
        name, ev, sub = add
        if any(r["conference"] == name for r in xr_rows):
            continue
        r = dblplib.crossref_row(t, x["year"], x["n"], ev); r["conference"] = name; r["subfield"] = sub; r["stream"] = None
        xr_rows.append(r)
    elif ho:
        handed.append(dict(title=t, n=x["n"], year=x["year"], why=ho))
    elif x["existing"]:
        handed.append(dict(title=t, n=x["n"], year=x["year"], why="already on " + x["existing"]))
    else:
        handed.append(dict(title=t, n=x["n"], year=x["year"], why="UNREVIEWED — orchestrator to classify"))
for r in xr_rows:
    if r["conference"] in TIER_OVERRIDE:
        r["tier"], why = TIER_OVERRIDE[r["conference"]]
        r["method"] += f"  ||  TIER OVERRIDE: {why}"
rows += xr_rows
plan = dict(rows=rows, dupes=dupes, crossref_only=sorted(xr_only, key=lambda x: -x["n"]), handed_over=handed)
json.dump(plan, open(f"{D}/plan.json", "w"), indent=1, ensure_ascii=False)

print(f"DBLP rows for the sheet: {len(rows)}  |  DBLP streams already on another sheet: {len(dupes)}  |  "
      f"Crossref-only series >=800: {len(xr_only)}")
print("\n=== DBLP ROWS (main-track count, latest year; ws = workshop papers excluded; xr = Crossref figure)")
for r in sorted(rows, key=lambda r: -r["abstracts_numeric"]):
    xrn = re.search(r"gives ([\d,]+) under", r["method"])
    print(f"  {r['tier']:10} {r['abstracts_numeric']:>6} {r['year']} ev={r['events_per_yr']:<4} ws={r['workshop']:<5} "
          f"xr={xrn.group(1) if xrn else '-':>6}  {r['conference'][:70]}  [{r['stream']}]")
print("\n=== DBLP STREAMS ALREADY COUNTED ELSEWHERE (parked on the deleted sheet, not double counted)")
for d in dupes:
    print(f"  {d['main']:>6} {d['year']}  {d['conference'][:60]:60} -> {d['counted_on']} / {d['existing'][:50]}")
print("\n=== CROSSREF-ONLY SERIES >=800 (not in the DBLP candidate set) — review: engineering/CS to ADD, other fields to hand over, existing to skip")
for x in plan["crossref_only"]:
    print(f"  {x['n']:>6} {x['year']}  {x['title'][:95]:95} {('DUP: ' + x['existing'][:40]) if x['existing'] else ''}")
print("\n=== HANDED OVER / SKIPPED (not loaded on this sheet)")
for h in sorted(handed, key=lambda h: -h["n"]):
    print(f"  {h['n']:>6} {h['year']}  {h['title'][:70]:70}  -> {h['why'][:80]}")
print("\nTier counts (DBLP + Crossref rows):", collections.Counter(r["tier"] for r in rows), "| rows:", len(rows))

if "--dry" in sys.argv:
    sys.exit(0)

# --- write ---------------------------------------------------------------------
names = [dict(conference=r["conference"], society="", country_or_region="international (rotates)" if r.get("stream") else "see Method",
              subfield=r.get("subfield"), frequency_note=f"{r['events_per_yr']}/yr",
              why_listed=("DBLP stream with >=800 records in 2024 or 2025" if r.get("stream") else "Crossref proceedings-article container with >=800 papers"),
              source_url=r["source_url"]) for r in rows]
duplicates = [dict(conference=d["conference"], counted_on=d["counted_on"]) for d in dupes]
print(chemlib.build_field(names, duplicates, FIELD, today=TODAY))
wb_recs = [dict(row=5 + i, expected_name=r["conference"], abstracts=r["abstracts"], year=r["year"],
                source_url=r["source_url"], rung=r["rung"], tier=r["tier"], character="CONTRIBUTED",
                method=r["method"], events_per_yr=r["events_per_yr"]) for i, r in enumerate(rows)]
print("written", writeback.apply(wb_recs, sheet=f"Census - {FIELD}"))
outs = [dict(row=5 + i, expected_name=r["conference"], why=f"OUT on positive evidence: {r['abstracts']} — see Method [dblp wave {TODAY}]")
        for i, r in enumerate(rows) if r["tier"] == "OUT"]
if outs:
    print("moved OUT rows to the deleted sheet:", dedupe.move_to_deleted(outs, today=TODAY, census=f"Census - {FIELD}", deleted=f"Deleted - {FIELD}"))
