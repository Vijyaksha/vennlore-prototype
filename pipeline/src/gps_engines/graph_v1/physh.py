"""PhySH (Physics Subject Headings, physh.org, CC0) — the APS's official
physics taxonomy. Loaded from a vendored snapshot (resources/physh.json.gz,
release v2.8.0). Used at graph-construction time as a structural prior for
method-method edges: methods file onto concepts, and the tree relation
between two methods' concept sets decides same/related/veto/judge zones.
The inDiscipline (domain) property is DELIBERATELY ignored — matching must
never key on domain."""
import gzip
import json
from dataclasses import dataclass
from pathlib import Path

SK = "http://www.w3.org/2004/02/skos/core#"
PH = "https://physh.org/rdf/2018/01/01/core#"

TECHNIQUE_FACETS = {
    "Techniques", "Experimental Techniques", "Theoretical Techniques",
    "Computational Techniques", "Theoretical & Computational Techniques",
}
# Properties (measured quantities like Photocurrent) are allowed as
# SECONDARY filing targets: a measurement method is identified partly by
# what it measures. Research Areas / Physical Systems / Professional Topics
# are never filing targets — that would smuggle domain back in.
PROPERTY_FACETS = {"Properties"}


@dataclass(frozen=True)
class Relation:
    kind: str      # "same" | "ancestor" | "cousin" | "disconnected"
    distance: int  # hops (0 for same; 99 for disconnected)
    lca_label: str


class PhySH:
    def __init__(self, label, alt, broader, concept_facet):
        self.label = label                  # id -> prefLabel
        self.alt = alt                      # id -> [altLabels]
        self.broader = broader              # id -> [parent ids]
        self.concept_facet = concept_facet  # id -> facet name (or None)

    def filing_targets(self) -> list[str]:
        return [cid for cid, f in self.concept_facet.items()
                if f in TECHNIQUE_FACETS | PROPERTY_FACETS and cid in self.label]

    def ancestors(self, cid: str) -> list[str]:
        out, cur, seen = [cid], cid, set()
        while self.broader.get(cur) and cur not in seen:
            seen.add(cur)
            cur = self.broader[cur][0]
            out.append(cur)
        return out

    def parent_chain_labels(self, cid: str) -> str:
        return " < ".join(self.label.get(a, "?") for a in self.ancestors(cid))

    def relation(self, a: str, b: str) -> Relation:
        if a == b:
            return Relation("same", 0, self.label.get(a, "?"))
        aa, ab = self.ancestors(a), self.ancestors(b)
        if b in aa:
            return Relation("ancestor", aa.index(b), self.label.get(b, "?"))
        if a in ab:
            return Relation("ancestor", ab.index(a), self.label.get(a, "?"))
        aset = set(ab)
        common = [x for x in aa if x in aset]
        if common:
            lca = common[0]
            return Relation("cousin", aa.index(lca) + ab.index(lca),
                            self.label.get(lca, "?"))
        return Relation("disconnected", 99, "")

    def best_relation(self, a_nodes: list[str], b_nodes: list[str]) -> Relation:
        """Closest relation across two methods' filed node sets."""
        best = Relation("disconnected", 99, "")
        rank = {"same": 0, "ancestor": 1, "cousin": 2, "disconnected": 3}
        for a in a_nodes:
            for b in b_nodes:
                r = self.relation(a, b)
                if (rank[r.kind], r.distance) < (rank[best.kind], best.distance):
                    best = r
        return best


def load_physh(path: Path | None = None) -> PhySH:
    if path is None:
        path = Path(__file__).resolve().parents[3] / "resources" / "physh.json.gz"
    raw = json.loads(gzip.decompress(path.read_bytes()))
    label, alt, broader, facet_of, facets = {}, {}, {}, {}, {}
    for rec in raw:
        rid = rec["@id"]
        labs = rec.get(SK + "prefLabel") or rec.get(PH + "prefLabel") or []
        if labs:
            label[rid] = labs[0]["@value"]
        if PH + "Facet" in rec.get("@type", []):
            facets[rid] = labs[0]["@value"] if labs else rid
        broader[rid] = [x["@id"] for x in rec.get(SK + "broader", [])]
        facet_of[rid] = [x["@id"] for x in rec.get(PH + "inFacet", [])]
        alt[rid] = [x["@value"] for x in rec.get(SK + "altLabel", [])]

    def facet_for(rid, seen):
        if rid in seen:
            return None
        seen.add(rid)
        if facet_of.get(rid):
            return facets.get(facet_of[rid][0])
        for b in broader.get(rid, []):
            f = facet_for(b, seen)
            if f:
                return f
        return None

    concept_facet = {rid: facet_for(rid, set()) for rid in label}
    return PhySH(label, alt, broader, concept_facet)
