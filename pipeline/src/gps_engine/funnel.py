"""Candidate funnel: recall-only graph traversal from a talk to nearby talks
sharing a method node or one RELATED_TO hop away. No scoring/filtering here
beyond the caller-chosen edge-strength floor — precision comes later from the
rubric."""
from gps_engine.graph import MethodGraph


def candidates(g: MethodGraph, talk_id: int, min_strength: int = 0) -> set[int]:
    """Contract: an unknown talk_id (not present in the graph) returns an
    empty set rather than raising. min_strength is the query-time tightness
    dial: RELATED_TO edges below it are not walked (shared nodes always are).
    Edges recorded without a strength (0) are only walked at min_strength=0."""
    my_nodes = [n for n in g.nodes() if talk_id in g.talks_using(n)]
    out: set[int] = set()
    for n in my_nodes:
        out |= g.talks_using(n)
        for r in g.related_to(n):
            info = g.edge_info(n, r)
            strength = info["strength"] if info else 0
            if strength >= min_strength:
                out |= g.talks_using(r)
    out.discard(talk_id)
    return out
