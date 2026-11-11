"""Preprints as Talk records: arXiv (Atom API), bioRxiv and medRxiv
(api.biorxiv.org). Papers are extra candidates next to the programme's talks:

  external_id  "arXiv:<id>" or "doi:<doi>"      (no version suffix)
  type         "preprint:arxiv" | "preprint:biorxiv" | "preprint:medrxiv"
  topics       the paper's categories
  units        () for physics arXiv papers (division unknown at a physics meeting),
               ("arXiv:<cat>",) / ("bioRxiv:<cat>",) / ("medRxiv:<cat>",) otherwise
  start        None: papers have no slot, so the agenda leaves them out
  id           stable hash of external_id in [ID_BASE, ID_BASE + ID_SPAN)
Parsing only; downloading lives in scripts/fetch_preprints.py."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import replace

from gps_data.archive import clean_text
from gps_data.talk import Talk, external_anchor

ID_BASE = 1_500_000_000          # programme ids are far below this
ID_SPAN = 600_000_000            # stays under the Postgres integer limit

PHYSICS_ARXIV = ("physics", "cond-mat", "quant-ph", "astro-ph", "gr-qc", "hep-",
                 "nucl-", "nlin", "math-ph")
ARXIV_NAMES = {
    "cs.LG": "Machine Learning", "stat.ML": "Machine Learning", "cs.AI": "Artificial Intelligence",
    "cs.CV": "Computer Vision", "cs.CL": "Computation and Language", "cs.RO": "Robotics",
    "cs.AR": "Hardware Architecture", "cs.DC": "Distributed Computing", "cs.PF": "Performance",
    "cs.NE": "Neural and Evolutionary Computing", "eess.IV": "Image and Video Processing",
    "eess.SP": "Signal Processing", "eess.SY": "Systems and Control", "math.OC": "Optimization",
    "physics.optics": "Optics", "physics.app-ph": "Applied Physics",
    "physics.bio-ph": "Biological Physics", "physics.chem-ph": "Chemical Physics",
    "physics.comp-ph": "Computational Physics", "physics.data-an": "Data Analysis",
    "physics.flu-dyn": "Fluid Dynamics", "physics.med-ph": "Medical Physics",
    "physics.ins-det": "Instrumentation and Detectors", "physics.atom-ph": "Atomic Physics",
    "physics.plasm-ph": "Plasma Physics", "quant-ph": "Quantum Physics",
    "cond-mat.mtrl-sci": "Materials Science", "cond-mat.soft": "Soft Matter",
    "cond-mat.stat-mech": "Statistical Mechanics", "cond-mat.mes-hall": "Mesoscale and Nanoscale Physics",
    "cond-mat.str-el": "Strongly Correlated Electrons", "cond-mat.supr-con": "Superconductivity",
    "cond-mat.dis-nn": "Disordered Systems and Neural Networks", "math-ph": "Mathematical Physics",
    "q-bio.NC": "Neurons and Cognition", "q-bio.BM": "Biomolecules",
    "q-bio.QM": "Quantitative Methods", "gr-qc": "General Relativity and Quantum Cosmology",
}


def arxiv_name(code: str) -> str:
    """Readable topic for an arXiv category; the code itself when unknown."""
    if code in ARXIV_NAMES:
        return ARXIV_NAMES[code]
    for prefix, name in (("astro-ph", "Astrophysics"), ("hep-", "High Energy Physics"),
                         ("nucl-", "Nuclear Physics")):
        if code.startswith(prefix):
            return name
    return code


_NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
_VERSION = re.compile(r"v\d+$")


def preprint_id(external_id: str) -> int:
    h = int.from_bytes(hashlib.sha256(external_id.encode()).digest()[:8], "big")
    return ID_BASE + h % ID_SPAN


def paper_url(external_id: str | None) -> str | None:
    if not external_id:
        return None
    if external_id.startswith("arXiv:"):
        return "https://arxiv.org/abs/" + external_id.removeprefix("arXiv:")
    if external_id.startswith("doi:"):
        return "https://doi.org/" + external_id.removeprefix("doi:")
    return None


def _paper(external_id: str, title: str, abstract: str, source: str,
           topics: tuple[str, ...], units: tuple[str, ...], date: str) -> Talk:
    t = external_anchor(clean_text(title), clean_text(abstract), list(units))
    label = {"arxiv": "arXiv", "biorxiv": "bioRxiv", "medrxiv": "medRxiv"}[source]
    return replace(t, id=preprint_id(external_id), external_id=external_id,
                   type=f"preprint:{source}", topics=topics,
                   publication_reference=f"{label} {date[:10]}" if date else label)


def parse_arxiv(xml_text: str) -> list[Talk]:
    root = ET.fromstring(xml_text)
    out = []
    for e in root.findall("a:entry", _NS):
        raw_id = (e.findtext("a:id", default="", namespaces=_NS) or "").rsplit("/abs/", 1)[-1]
        if not raw_id:
            continue
        prim = e.find("arxiv:primary_category", _NS)
        primary = prim.get("term") if prim is not None else ""
        cats = [c.get("term") for c in e.findall("a:category", _NS) if c.get("term")]
        codes = [primary, *cats] if primary else cats
        topics = tuple(dict.fromkeys(arxiv_name(c) for c in codes))
        physics = primary.startswith(PHYSICS_ARXIV)
        out.append(_paper(
            "arXiv:" + _VERSION.sub("", raw_id),
            e.findtext("a:title", default="", namespaces=_NS),
            e.findtext("a:summary", default="", namespaces=_NS),
            "arxiv", topics, () if physics or not primary else (f"arXiv:{primary}",),
            e.findtext("a:published", default="", namespaces=_NS)))
    return out


def parse_rxiv(json_text: str) -> list[Talk]:
    """One page of api.biorxiv.org/details/{biorxiv|medrxiv}/... output."""
    out = []
    for item in json.loads(json_text).get("collection") or []:
        server = str(item.get("server", "bioRxiv"))
        source = server.casefold()
        if source not in ("biorxiv", "medrxiv") or not item.get("doi"):
            continue
        cat = clean_text(item.get("category", "")).casefold()
        out.append(_paper(
            "doi:" + item["doi"], item.get("title", ""), item.get("abstract", ""), source,
            (cat,) if cat else (), (f"{'bioRxiv' if source == 'biorxiv' else 'medRxiv'}:{cat}",)
            if cat else (), item.get("date", "")))
    return out


def dedupe(talks: list[Talk]) -> list[Talk]:
    """One row per paper (last seen wins: listings repeat papers across versions)."""
    return list({t.external_id: t for t in talks}.values())
