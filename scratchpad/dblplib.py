"""dblplib — DBLP SPARQL results and Crossref proceedings facets -> census rows.

Unit: accepted contributed papers (Rupert, 2026-09-12). Workshop / companion / adjunct volumes are
reported separately and never counted toward the bar. DBLP's SPARQL endpoint
(https://sparql.dblp.org/sparql) is the artefact; the stream page is the clickable source.
"""
import re
from collections import defaultdict

BAR, FLOOR = 1500, 800          # VERIFIED at 1,500; ~900 floor with the within-100 leeway
WORKSHOP_WORDS = ("workshop", "companion", "adjunct", "tutorial", "demo", "extended abstracts",
                  "satellite", "challenge", "doctoral consortium", "late breaking", "posters")
NOT_A_CONFERENCE = ("aip conference proceedings", "sae technical paper", "iop conference series",
                    "journal of physics: conference series", "e3s web of conferences", "matec web of conferences",
                    "lecture notes", "proceedings of spie", "ceur workshop proceedings", "advances in intelligent systems",
                    "springer proceedings", "communications in computer and information science")
STOP = {"the", "of", "on", "and", "in", "for", "a", "an", "&", "proceedings", "conference", "international",
        "annual", "meeting", "symposium", "congress", "ieee", "acm", "with", "its", "at", "cvf"}
ORDINAL = re.compile(r"\b\d{1,3}(st|nd|rd|th)\b", re.I)
YEAR = re.compile(r"\b(19|20)\d{2}\b")
ORDINAL_WORDS = re.compile(r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|"
                           r"thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|"
                           r"thirtieth|fortieth|fiftieth|twenty|thirty|forty|fifty|sixty)[- ]?\w*", re.I)


def is_workshop_volume(title):
    t = title.lower()
    return any(w in t for w in WORKSHOP_WORDS)


def main_track_split(volume_rows):
    """{(stream, year): {'main': n, 'workshop': n}} from per-volume counts."""
    out = defaultdict(lambda: {"main": 0, "workshop": 0})
    for v in volume_rows:
        key = (v["stream"], int(v["year"]))
        out[key]["workshop" if is_workshop_volume(v["vtitle"]) else "main"] += int(v["n"])
    return dict(out)


def latest_year(stream, split, prefer=(2025, 2024)):
    for y in prefer:
        if (stream, y) in split and split[(stream, y)]["main"] > 0:
            return y
    years = [y for (s, y) in split if s == stream]
    return max(years) if years else None


def cadence(stream, yearly, years=range(2018, 2026)):
    """Events per year = share of recent years in which the stream has records (1 annual, 0.5 biennial)."""
    hit = sum(1 for y in years if yearly.get((stream, y), 0) > 0)
    total = len(list(years))
    frac = hit / total
    return 1 if frac >= 0.85 else round(frac, 2)


# --- de-duplication ----------------------------------------------------------

GENERIC_ACRONYMS = {"IEEE", "ACM", "CVF", "IEEE/CVF", "RSJ", "RJS", "INC", "USA", "UK", "EU", "APS-DLS", "DLS",
                    "AAAS", "USNC", "URSI", "SIG", "IFAC", "IFIP", "AIP", "IOP", "CCF", "IET", "ASME", "SAE"}


def _acronyms(name):
    found = {a.upper() for a in re.findall(r"\(([A-Za-z][A-Za-z0-9/&+\-]{1,15})\)", name or "")} | \
            {a.upper() for a in re.findall(r"\b([A-Z]{3,8}(?:/[A-Z]{2,6})*)\b", name or "")}
    return {a for a in found if a not in GENERIC_ACRONYMS and not a.isdigit()}


def _tokens(name):
    return {w for w in re.sub(r"[^a-z0-9 ]", " ", (name or "").lower()).split() if w not in STOP and len(w) > 2}


def find_existing(name, existing):
    """The existing workbook row this conference already is, or None. Acronym match first, then names."""
    acr = _acronyms(name)
    toks = _tokens(name)
    for e in existing:
        ea = _acronyms(e["conference"])
        if acr and ea and (acr & ea):
            # an acronym collision (ICML lymphoma vs ICML machine learning) shares the letters but no words
            et = _tokens(e["conference"]) - {a.lower() for a in ea}
            mine = toks - {a.lower() for a in acr}
            if len(et) >= 1 and len(mine) >= 1 and not (et & mine):
                continue
            return e
    for e in existing:
        et = _tokens(e["conference"])
        if toks and et and len(toks & et) >= max(3, int(0.8 * min(len(toks), len(et)))):
            return e
    return None


def one_row_per_stream(meta):
    seen, out = set(), []
    for m in meta:
        if m["stream"] in seen:
            continue
        seen.add(m["stream"])
        out.append(m)
    return out


# --- Crossref container titles ------------------------------------------------

def series_key(title):
    t = title.lower()
    t = t.replace("&amp;", "&")
    t = YEAR.sub(" ", t)
    t = ORDINAL.sub(" ", t)
    t = ORDINAL_WORDS.sub(" ", t)
    t = re.sub(r"\([^)]*\)", " ", t)           # drop parenthesised acronyms/editions
    t = re.sub(r"^[a-z]{3,10}\s*[-–]\s*", " ", t)  # leading "ICASSP - "
    t = re.sub(r"\bvolume\s*\d+.*$", " ", t)
    t = re.sub(r"[^a-z ]", " ", t)
    words = [w for w in t.split() if w not in STOP]
    return " ".join(words)


def is_not_a_conference(title):
    t = title.lower()
    return any(k in t for k in NOT_A_CONFERENCE)


# --- rows ------------------------------------------------------------------

def tier_for(main):
    if main >= BAR:
        return "VERIFIED"
    if main >= FLOOR:
        return "BORDERLINE"
    return "OUT"


def census_row(stream, title, year, main, workshop, events_per_yr, crossref=None, crossref_title=None):
    src = f"https://dblp.org/streams/{stream}"
    xr = (f" Crossref proceedings-article facet for {year} gives {crossref:,} under '{crossref_title or title}'"
          f" (independent second source; agreement within {abs(crossref - main)} papers)." if crossref is not None
          else " No Crossref container-title with >=800 papers matched this series (DBLP is the only source).")
    method = (f"RUNG 4 PRODUCED THIS FIGURE — archive count via DBLP SPARQL (https://sparql.dblp.org/sparql): "
              f"COUNT of ?p dblp:publishedInStream <{src}> with dblp:yearOfPublication \"{year}\"^^xsd:gYear, "
              f"grouped by dblp:publishedAsPartOf volume; volumes whose title contains workshop/companion/adjunct/"
              f"tutorial/demo/extended-abstracts terms are EXCLUDED as workshop content: main track {main:,}, "
              f"workshop volumes {workshop:,}. Unit = accepted papers in the proceedings (invited keynote abstracts, "
              f"if any, are a handful and not separable). Cadence {events_per_yr}/yr from the share of 2018-2025 with "
              f"records.{xr} Language: n/a (bibliographic index). [dblp wave, 2026-09-13]")
    return dict(conference=title, abstracts_numeric=main, year=year, source_url=src, rung=4,
                tier=tier_for(main), events_per_yr=events_per_yr, method=method, workshop=workshop,
                abstracts=f"{main:,} accepted papers in the {year} proceedings (DBLP main-track volumes; "
                          f"{workshop:,} further papers in workshop/companion volumes not counted)")


def crossref_row(title, year, n, events_per_yr, dblp_note=None):
    """A row whose only artefact is Crossref's proceedings-article deposit index (rung 4)."""
    clean = re.sub(r"^\s*(19|20)\d{2}\s+", "", title)
    clean = re.sub(r"^\s*\d{1,3}(st|nd|rd|th)\s+", "", clean)
    src = (f"https://api.crossref.org/works?filter=type:proceedings-article,from-pub-date:{year}-01-01,"
           f"until-pub-date:{year}-12-31&facet=container-title:*&rows=0")
    method = (f"RUNG 4 PRODUCED THIS FIGURE — publisher deposit index (Crossref): container-title facet over all "
              f"proceedings-article DOIs published in {year} returns {n:,} items under the exact title '{title}' "
              f"(query: {src}). Unit = deposited proceedings papers = accepted papers; the deposit is by the "
              f"publisher (IEEE Xplore, ACM DL, society press), so this is an archive count not a stated total. "
              f"{dblp_note or 'Not in the DBLP candidate set (DBLP does not index this series, or indexes it under a different stream).'} "
              f"Cadence {events_per_yr}/yr. Language: n/a. [crossref wave, 2026-09-13]")
    return dict(conference=clean, abstracts_numeric=n, year=year, source_url=src, rung=4, tier=tier_for(n),
                events_per_yr=events_per_yr, method=method, workshop=0,
                abstracts=f"{n:,} proceedings papers deposited to Crossref for {year} (container title '{title}')")
