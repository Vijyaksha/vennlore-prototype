"""Candidate funnel: recall-only graph traversal from a talk to nearby talks
sharing a method node or one RELATED_TO hop away. No scoring/filtering here —
precision comes later from the rubric."""
from gps_engine.graph import MethodGraph


def candidates(g: MethodGraph, talk_id: int) -> set[int]:
    my_nodes = [n for n in g.nodes() if talk_id in g.talks_using(n)]
    out: set[int] = set()
    for n in my_nodes:
        out |= g.talks_using(n)
        for r in g.related_to(n):
            out |= g.talks_using(r)
    out.discard(talk_id)
    return out
