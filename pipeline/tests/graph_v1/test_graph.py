from gps_engines.graph_v1.graph import MethodGraph

def test_identical_strings_share_a_node():
    g = MethodGraph()
    g.link_talk(1, "DMRG"); g.link_talk(2, "DMRG")
    assert g.talks_using(g.node_id("DMRG")) == {1, 2}

def test_merge_unifies_nodes_and_links():
    g = MethodGraph()
    g.link_talk(1, "DMRG"); g.link_talk(2, "density-matrix renormalization group")
    g.merge(g.node_id("DMRG"), g.node_id("density-matrix renormalization group"))
    nid = g.node_id("DMRG")
    assert nid == g.node_id("density-matrix renormalization group")
    assert g.talks_using(nid) == {1, 2}

def test_related_edge_is_symmetric():
    g = MethodGraph()
    g.link_talk(1, "DMRG"); g.link_talk(2, "transfer-matrix methods")
    g.add_related(g.node_id("DMRG"), g.node_id("transfer-matrix methods"))
    assert g.node_id("transfer-matrix methods") in g.related_to(g.node_id("DMRG"))
    assert g.node_id("DMRG") in g.related_to(g.node_id("transfer-matrix methods"))

def test_round_trips_through_json(tmp_path):
    g = MethodGraph()
    g.link_talk(1, "DMRG"); g.link_talk(2, "transfer-matrix methods")
    g.merge(g.node_id("DMRG"), g.node_id("transfer-matrix methods"))
    path = tmp_path / "g.json"
    g.save(path)
    g2 = MethodGraph.load(path)
    assert g2.talks_using(g2.node_id("DMRG")) == {1, 2}

def test_merge_rehomes_related_edges_from_both_sides():
    g = MethodGraph()
    g.link_talk(1, "DMRG"); g.link_talk(2, "density-matrix renormalization group")
    g.link_talk(3, "transfer-matrix methods"); g.link_talk(4, "tensor networks")
    keep = g.node_id("DMRG")
    absorb = g.node_id("density-matrix renormalization group")
    c = g.node_id("transfer-matrix methods")
    d = g.node_id("tensor networks")
    g.add_related(keep, c)
    g.add_related(absorb, d)
    g.merge(keep, absorb)
    assert g.related_to(keep) == {c, d}
    assert keep in g.related_to(c)
    assert keep in g.related_to(d)
    assert absorb not in g.related_to(c)
    assert absorb not in g.related_to(d)
    assert absorb not in g.nodes()

def test_related_edges_round_trip_through_json(tmp_path):
    g = MethodGraph()
    g.link_talk(1, "DMRG"); g.link_talk(2, "transfer-matrix methods")
    a = g.node_id("DMRG"); b = g.node_id("transfer-matrix methods")
    g.add_related(a, b)
    path = tmp_path / "g.json"
    g.save(path)
    g2 = MethodGraph.load(path)
    a2 = g2.node_id("DMRG"); b2 = g2.node_id("transfer-matrix methods")
    assert b2 in g2.related_to(a2)
    assert a2 in g2.related_to(b2)


def test_edge_strength_and_why_stored():
    g = MethodGraph()
    a = g.link_talk(1, "self-assembly")
    b = g.link_talk(2, "self-assembled monolayers")
    g.add_related(a, b, strength=7, why="SAMs are a specific realization")
    info = g.edge_info(a, b)
    assert info == {"strength": 7, "why": "SAMs are a specific realization"}


def test_merge_keeps_strongest_edge():
    g = MethodGraph()
    a = g.link_talk(1, "self-assembly")
    b = g.link_talk(2, "sams")
    c = g.link_talk(3, "sam formation")
    g.add_related(a, b, strength=3, why="weak")
    g.add_related(a, c, strength=8, why="strong")
    g.merge(b, c)  # c absorbed into b; colliding edges to a must keep max
    assert g.edge_info(a, b) == {"strength": 8, "why": "strong"}


def test_edge_save_load_roundtrip(tmp_path):
    g = MethodGraph()
    a = g.link_talk(1, "x")
    b = g.link_talk(2, "y")
    g.add_related(a, b, strength=5, why="kin")
    p = tmp_path / "g.json"
    g.save(p)
    g2 = MethodGraph.load(p)
    assert g2.edge_info(a, b) == {"strength": 5, "why": "kin"}
