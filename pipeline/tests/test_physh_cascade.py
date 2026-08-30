"""Offline tests for the PhySH tree module, filing, and the edge cascade."""
import pytest

from gps_engine.cascade import Decision, _decide
from gps_engine.filing import file_method
from gps_engine.llm import FakeLLM
from gps_engine.physh import PhySH, Relation


def tiny_tree():
    #      root(optical)              root2(sample-prep)
    #        |- photolum                |- self-assembly
    #        |- photocurrent(prop)           |- lb-deposition
    label = {"opt": "Optical techniques", "pl": "Photoluminescence",
             "pc": "Photocurrent", "sp": "Sample preparation",
             "sa": "Self-assembly", "lb": "Langmuir-Blodgett deposition"}
    broader = {"pl": ["opt"], "pc": ["opt"], "sa": ["sp"], "lb": ["sa"],
               "opt": [], "sp": []}
    facet = {k: "Experimental Techniques" for k in label}
    return PhySH(label, {k: [] for k in label}, broader, facet)


def test_relations():
    p = tiny_tree()
    assert p.relation("sa", "sa").kind == "same"
    r = p.relation("lb", "sa")
    assert r.kind == "ancestor" and r.distance == 1
    r = p.relation("pl", "pc")
    assert r.kind == "cousin" and r.distance == 2 and r.lca_label == "Optical techniques"
    assert p.relation("pl", "sa").kind == "disconnected"


def test_best_relation_over_node_sets():
    p = tiny_tree()
    # method A filed on (pl); method B filed on (pc, sa): closest is cousin via pc
    assert p.best_relation(["pl"], ["pc", "sa"]).kind == "cousin"
    # sharing any node wins
    assert p.best_relation(["pl", "sa"], ["sa"]).kind == "same"


def F(c, conf):  # filing record
    return {"concept": c, "label": c, "confidence": conf}


def test_cascade_auto_same_needs_confidence():
    p = tiny_tree()
    d = _decide("a", "b", {"a": [F("sa", .9)], "b": [F("sa", .95)]}, p, sim=0.2)
    assert d.action == "auto-same" and d.provenance == "physh-same-concept"
    d = _decide("a", "b", {"a": [F("sa", .5)], "b": [F("sa", .95)]}, p, sim=0.5)
    assert d.action == "judge"  # same shelf but shaky filing -> LLM, not auto


def test_cascade_hub_shelf_never_auto_merges():
    p = tiny_tree()
    filings = {"a": [F("sa", .9)], "b": [F("sa", .9)]}
    hub_fanin = {"sa": 20}
    d = _decide("a", "b", filings, p, sim=0.6, fanin=hub_fanin)
    assert d.action == "judge" and d.provenance == "llm-hub-shelf"
    d = _decide("a", "b", filings, p, sim=0.2, fanin=hub_fanin)
    assert d.action == "drop"
    # rare shelf still auto-merges
    d = _decide("a", "b", filings, p, sim=0.2, fanin={"sa": 2})
    assert d.action == "auto-same"


def test_cascade_parent_child_auto_related():
    p = tiny_tree()
    d = _decide("a", "b", {"a": [F("lb", .9)], "b": [F("sa", .9)]}, p, sim=0.1)
    assert d.action == "auto-related" and d.strength == 8


def test_cascade_veto_and_escape_valve():
    p = tiny_tree()
    filings = {"a": [F("pl", .9)], "b": [F("sa", .9)]}
    assert _decide("a", "b", filings, p, sim=0.3).action == "drop"
    d = _decide("a", "b", filings, p, sim=0.8)
    assert d.action == "judge" and d.provenance == "llm-escape-valve"


def test_cascade_unfiled_falls_back_to_embedding_gate():
    p = tiny_tree()
    assert _decide("a", "b", {}, p, sim=0.6).action == "judge"
    assert _decide("a", "b", {}, p, sim=0.3).action == "drop"


def test_file_method_validates_indices_and_caps():
    p = tiny_tree()
    llm = FakeLLM(responses=[{"assignments": [
        {"index": 1, "confidence": 0.9}, {"index": 99, "confidence": 0.9},
        {"index": 2, "confidence": 1.5}, {"index": 2, "confidence": 0.6},
    ]}])
    out = file_method("self-assembly", "builds the layer", ["sa", "lb"], p, llm)
    assert [f["concept"] for f in out] == ["sa", "lb"]
    assert out[0]["confidence"] == 0.9 and out[1]["confidence"] == 0.6
    assert "self-assembly" in llm.prompts[0] and "Langmuir-Blodgett" in llm.prompts[0]


def test_file_method_empty_candidates():
    p = tiny_tree()
    assert file_method("x", "y", [], p, FakeLLM(responses=[])) == []
