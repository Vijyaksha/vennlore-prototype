from gps_engine.funnel import candidates
from gps_engine.graph import MethodGraph

def build():
    g = MethodGraph()
    g.link_talk(1, "self-assembly"); g.link_talk(2, "self-assembly")   # shared node
    g.link_talk(3, "supramolecular assembly")                          # related node
    g.add_related(g.node_id("self-assembly"), g.node_id("supramolecular assembly"))
    g.link_talk(4, "neutron scattering")                               # unconnected
    return g

def test_direct_and_related_hops_found():
    assert candidates(build(), talk_id=1) == {2, 3}

def test_self_excluded():
    assert 1 not in candidates(build(), talk_id=1)

def test_isolated_talk_yields_empty():
    assert candidates(build(), talk_id=4) == set()

def test_multi_node_talk_unions_candidates_from_both_nodes():
    g = MethodGraph()
    g.link_talk(1, "self-assembly"); g.link_talk(1, "neutron scattering")
    g.link_talk(2, "self-assembly")           # shares node A with talk 1
    g.link_talk(3, "neutron scattering")      # shares node B with talk 1
    assert candidates(g, talk_id=1) == {2, 3}

def test_related_to_does_not_recurse_beyond_one_hop():
    g = MethodGraph()
    a = g.link_talk(10, "method-a")
    b = g.link_talk(20, "method-b")
    c = g.link_talk(30, "method-c")
    g.add_related(a, b)
    g.add_related(b, c)  # a is NOT related to c
    g.link_talk(1, "method-a")
    assert candidates(g, talk_id=1) == {10, 20}
