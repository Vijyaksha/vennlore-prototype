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
