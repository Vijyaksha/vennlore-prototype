import pytest

from gps_engine.similarity import propose_pairs
from gps_engine.graph import MethodGraph
from gps_engine.llm import FakeLLM
from gps_engine.similarity import apply_verdicts, judge_pair


def fake_embed(names):  # canned 2-D embeddings keyed by name
    table = {
        "dmrg": [1.0, 0.0],
        "density-matrix renormalization group": [0.98, 0.05],
        "neutron scattering": [0.0, 1.0],
    }
    return [table[n] for n in names]


def test_proposes_only_near_pairs():
    names = ["dmrg", "density-matrix renormalization group", "neutron scattering"]
    pairs = propose_pairs(names, embed=fake_embed, threshold=0.9)
    assert pairs == [("density-matrix renormalization group", "dmrg")]


def test_no_pairs_when_all_far():
    pairs = propose_pairs(["dmrg", "neutron scattering"], embed=fake_embed, threshold=0.9)
    assert pairs == []


def test_judge_pair_parses_verdict():
    llm = FakeLLM(responses=[{"verdict": "same", "why": "acronym"}])
    assert judge_pair("dmrg", "density-matrix renormalization group", llm)["verdict"] == "same"


def test_apply_verdicts_merges_and_relates():
    g = MethodGraph()
    g.link_talk(1, "dmrg"); g.link_talk(2, "density-matrix renormalization group")
    g.link_talk(3, "transfer-matrix methods")
    verdicts = [
        ("dmrg", "density-matrix renormalization group", {"verdict": "same", "why": ""}),
        ("dmrg", "transfer-matrix methods", {"verdict": "related", "why": ""}),
    ]
    apply_verdicts(g, verdicts)
    assert g.talks_using(g.node_id("dmrg")) == {1, 2}
    assert g.node_id("transfer-matrix methods") in g.related_to(g.node_id("dmrg"))


def test_apply_verdicts_ignores_unrelated():
    g = MethodGraph()
    g.link_talk(1, "dmrg"); g.link_talk(2, "neutron scattering")
    apply_verdicts(g, [("dmrg", "neutron scattering", {"verdict": "unrelated", "why": ""})])
    assert g.related_to(g.node_id("dmrg")) == set()


def test_apply_verdicts_rejects_unknown_verdict():
    g = MethodGraph()
    g.link_talk(1, "dmrg"); g.link_talk(2, "neutron scattering")
    with pytest.raises(ValueError):
        apply_verdicts(g, [("dmrg", "neutron scattering", {"verdict": "similar", "why": ""})])
