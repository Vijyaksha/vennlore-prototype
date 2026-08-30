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


def _cos(u, v):
    nu = math.sqrt(sum(x * x for x in u))
    nv = math.sqrt(sum(x * x for x in v))
    return (sum(a * b for a, b in zip(u, v)) / (nu * nv)) if nu and nv else 0.0


def decide_pairs(names: list[str], filings: dict[str, list[dict]],
                 physh: PhySH, embed, texts: dict[str, str]) -> list[Decision]:
    """filings: name -> [{"concept","label","confidence"}]; texts: name ->
    'name: description' string used for the embedding screen."""
    vecs = dict(zip(names, embed([texts.get(n, n) for n in names])))
    out = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            out.append(_decide(a, b, filings, physh, _cos(vecs[a], vecs[b])))
    return out


def _decide(a, b, filings, physh, sim) -> Decision:
    fa, fb = filings.get(a) or [], filings.get(b) or []
    if fa and fb:
        rel = physh.best_relation([f["concept"] for f in fa],
                                  [f["concept"] for f in fb])
        conf_a = max(f["confidence"] for f in fa)
        conf_b = max(f["confidence"] for f in fb)
        confident = conf_a >= CONF_AUTO and conf_b >= CONF_AUTO
        if rel.kind == "same" and confident:
            return Decision(a, b, "auto-same", "physh-same-concept", 10,
                            f"both file onto PhySH '{rel.lca_label}'", "")
        if rel.kind == "ancestor" and rel.distance <= 2 and confident:
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
