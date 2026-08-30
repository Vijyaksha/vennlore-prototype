"""Edge cascade: decides every method-name pair through three cost-ordered
stages. (a) PhySH tree zones — same-shelf pairs auto-merge, parent-child
auto-relate, confidently-distant pairs are vetoed; (b) embedding screen on
what remains; (c) LLM judgment only for the surviving residue. Every
decision carries provenance. The escape valve: a vetoed pair with very high
text similarity still goes to the LLM (a filing error must not silently
kill a true edge)."""
import math
from dataclasses import dataclass

from gps_engine.physh import PhySH

CONF_AUTO = 0.8        # both filings at least this confident for auto-decisions
FANIN_MAX = 4          # a shelf holding more methods than this is a hub: it
                       # confers no sameness (corpus-adaptive IDF — Rupert's
                       # granularity rule made structural)
COUSIN_MAX_DIST = 4    # cousins farther than this are treated as distant
SIM_COUSIN = 0.45      # embedding floor for cousin pairs to reach the LLM
SIM_UNFILED = 0.50     # embedding floor for pairs lacking tree info (old behavior)
SIM_ESCAPE = 0.70      # escape valve: vetoed pairs above this still get judged


@dataclass(frozen=True)
class Decision:
    a: str
    b: str
    action: str      # "auto-same" | "auto-related" | "judge" | "drop"
    provenance: str
    strength: int    # for auto decisions
    why: str
    evidence: str    # context line handed to the LLM for "judge" pairs


def _lca_concept(rel, fa, fb):
    """Concept id whose label matches the relation's lca (best effort)."""
    for f in list(fa) + list(fb):
        if f.get("label") == rel.lca_label:
            return f["concept"]
    return rel.lca_label


def _cos(u, v):
    nu = math.sqrt(sum(x * x for x in u))
    nv = math.sqrt(sum(x * x for x in v))
    return (sum(a * b for a, b in zip(u, v)) / (nu * nv)) if nu and nv else 0.0


def shelf_fanin(filings: dict[str, list[dict]]) -> dict[str, int]:
    """How many methods file (confidently) onto each concept."""
    fanin: dict[str, int] = {}
    for fs in filings.values():
        for f in fs:
            if f["confidence"] >= CONF_AUTO:
                fanin[f["concept"]] = fanin.get(f["concept"], 0) + 1
    return fanin


def decide_pairs(names: list[str], filings: dict[str, list[dict]],
                 physh: PhySH, embed, texts: dict[str, str]) -> list[Decision]:
    """filings: name -> [{"concept","label","confidence"}]; texts: name ->
    'name: description' string used for the embedding screen."""
    vecs = dict(zip(names, embed([texts.get(n, n) for n in names])))
    fanin = shelf_fanin(filings)
    out = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            out.append(_decide(a, b, filings, physh,
                               _cos(vecs[a], vecs[b]), fanin))
    return out


def _shared_concepts(fa, fb):
    sa = {f["concept"] for f in fa if f["confidence"] >= CONF_AUTO}
    sb = {f["concept"] for f in fb if f["confidence"] >= CONF_AUTO}
    return sa & sb


def _decide(a, b, filings, physh, sim, fanin=None) -> Decision:
    fanin = fanin or {}
    fa, fb = filings.get(a) or [], filings.get(b) or []
    if fa and fb:
        rel = physh.best_relation([f["concept"] for f in fa],
                                  [f["concept"] for f in fb])
        conf_a = max(f["confidence"] for f in fa)
        conf_b = max(f["confidence"] for f in fb)
        confident = conf_a >= CONF_AUTO and conf_b >= CONF_AUTO
        if rel.kind == "same" and confident:
            shared = _shared_concepts(fa, fb)
            rare = [c for c in shared if fanin.get(c, 0) <= FANIN_MAX]
            if rare:
                return Decision(a, b, "auto-same", "physh-same-concept", 10,
                                f"both file onto rare PhySH shelf "
                                f"'{physh.label.get(rare[0], '?')}'", "")
            # hub shelf: shared name-tag, not shared identity — needs a judge
            if sim >= SIM_COUSIN:
                ev = (f"both file onto the BROAD PhySH shelf "
                      f"'{rel.lca_label}' (a hub holding many corpus "
                      f"methods — shelf-sharing alone proves nothing); "
                      f"text similarity {sim:.2f}")
                return Decision(a, b, "judge", "llm-hub-shelf", 0, "", ev)
            return Decision(a, b, "drop", "hub-shelf-low-text-sim", 0, "", "")
        if rel.kind == "ancestor" and rel.distance <= 2 and confident                 and fanin.get(_lca_concept(rel, fa, fb), 0) <= FANIN_MAX:
            return Decision(a, b, "auto-related", "physh-parent-child",
                            9 - rel.distance,
                            f"PhySH kind-of chain at '{rel.lca_label}'", "")
        if rel.kind in ("same", "ancestor") or \
           (rel.kind == "cousin" and rel.distance <= COUSIN_MAX_DIST):
            if sim >= SIM_COUSIN:
                ev = (f"PhySH: {rel.kind} at distance {rel.distance} under "
                      f"'{rel.lca_label}'; text similarity {sim:.2f}")
                return Decision(a, b, "judge", "llm-cousin", 0, "", ev)
            return Decision(a, b, "drop", "cousin-low-text-sim", 0, "", "")
        # distant/disconnected in the tree
        if sim >= SIM_ESCAPE:
            ev = (f"PhySH places these far apart ({rel.kind}), but text "
                  f"similarity is {sim:.2f} — check for a filing error")
            return Decision(a, b, "judge", "llm-escape-valve", 0, "", ev)
        return Decision(a, b, "drop", "physh-veto", 0, "", "")
    # one or both unfiled: no tree prior — old embedding-gate behavior
    if sim >= SIM_UNFILED:
        return Decision(a, b, "judge", "llm-unfiled", 0, "",
                        f"no tree filing; text similarity {sim:.2f}")
    return Decision(a, b, "drop", "unfiled-low-text-sim", 0, "", "")
