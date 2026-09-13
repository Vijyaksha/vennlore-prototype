"""Offline tests for the PhySH tree module, filing, and the edge cascade."""
import pytest

from gps_engine.cascade import Decision, _decide
from gps_engine.filing import file_method
from gps_core.llm import FakeLLM
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
    # Confident same-shelf is strong tree evidence: descriptions carry each
    # talk's own domain, so cross-domain kin pairs sit in the 0.30-0.45 band
    # (observed: anchor photoconductivity x perovskite transient photocurrent
    # at 0.32) — the judge, not the text screen, must decide those.
    d = _decide("a", "b", filings, p, sim=0.35, fanin=hub_fanin)
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


def test_decide_pairs_screens_on_max_of_name_and_text_sim():
    """Description texts carry each talk's own domain, so cross-domain uses
    of the SAME technique can score low on text sim while the bare names are
    near-identical (observed: 'self-assembly' vs 'self-assembled monolayers'
    text 0.43 / names 0.51 with a 0.50 unfiled gate). The screen must pass a
    pair when EITHER view clears the floor — the judge, which sees the
    descriptions, keeps precision."""
    from gps_engine.cascade import decide_pairs
    p = tiny_tree()

    def embed(items):
        # name-view vectors are identical (sim 1.0); text-view orthogonal.
        if any(":" in it for it in items):   # texts carry "name: description"
            return [[1.0, 0.0], [0.0, 1.0]]
        return [[1.0, 0.0], [1.0, 0.0]]      # bare names

    texts = {"self-assembly": "self-assembly: porphyrin nanorod growth",
             "self-assembled monolayers": "self-assembled monolayers: CISS films"}
    (d,) = decide_pairs(["self-assembly", "self-assembled monolayers"],
                        {}, p, embed, texts)
    assert d.action == "judge" and d.provenance == "llm-unfiled"


def test_decide_pairs_bulk_matches_decide_pairs():
    """The bulk path (numpy sims, relation caching, drops summarized) must
    reach identical decisions to the reference implementation."""
    from gps_engine.cascade import decide_pairs, decide_pairs_bulk
    p = tiny_tree()
    names = ["a", "b", "c", "d"]
    filings = {"a": [F("sa", .9)], "b": [F("sa", .9)], "c": [F("sb", .9)]}

    def embed(items):
        vecs = {"a": [1.0, 0.0], "b": [0.9, 0.1], "c": [0.0, 1.0], "d": [0.5, 0.5]}
        return [vecs[i.split(":")[0].strip()] for i in items]

    texts = {n: f"{n}: desc of {n}" for n in names}
    ref = decide_pairs(names, filings, p, embed, texts)
    kept, n_dropped = decide_pairs_bulk(names, filings, p, embed, texts)
    ref_kept = [d for d in ref if d.action != "drop"]
    assert sorted((d.a, d.b, d.action, d.provenance) for d in kept) == \
           sorted((d.a, d.b, d.action, d.provenance) for d in ref_kept)
    assert n_dropped == len(ref) - len(ref_kept)


def test_decide_pairs_cross_bipartite_only():
    """Query-time cascade: new (anchor) methods are decided against every
    existing name, but existing-existing pairs are NOT re-decided."""
    from gps_engine.cascade import decide_pairs_cross
    p = tiny_tree()
    filings = {"new1": [F("sa", .9)], "old1": [F("sa", .9)]}

    def embed(items):
        vecs = {"new1": [1.0, 0.0], "old1": [0.95, 0.05], "old2": [0.0, 1.0]}
        return [vecs[i.split(":")[0].strip()] for i in items]

    texts = {n: f"{n}: d" for n in ("new1", "old1", "old2")}
    ds = decide_pairs_cross(["new1"], ["old1", "old2"],
                            filings, p, embed, texts)
    pairs = {(d.a, d.b) for d in ds}
    assert ("new1", "old1") in pairs and ("new1", "old2") in pairs
    assert not any(a == "old1" and b == "old2" for a, b in pairs)
    same = next(d for d in ds if d.b == "old1")
    assert same.action in ("auto-same", "judge")
