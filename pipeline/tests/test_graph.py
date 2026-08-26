from gps_engine.graph import MethodGraph

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
