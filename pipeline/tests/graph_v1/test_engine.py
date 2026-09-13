import json
from dataclasses import replace

from gps_core.contracts import validate
from gps_core.protocol import Engine
from gps_core.run import run_index, run_recommend
from gps_data.talk import external_anchor
from gps_engines.graph_v1.engine import GraphV1Engine, build

from .fakes import RoutingFakeLLM, keyword_embedder, tiny_physh

ANCHOR_T = "Photoconductivity of Self-Assembled Porphyrin Nanorods"
PEROV_T = "Ultrafast transient photocurrent in hybrid lead halide perovskites"
GEMS_T = "Raman spectroscopy, a definitive tool for eliminating Diamond simulants"


def corpus():
    return [replace(external_anchor(PEROV_T, "We performed transient photocurrent measurements.", ["DLS"]), id=12772),
            replace(external_anchor(GEMS_T, "We compare Raman signatures.", ["GIMS"]), id=9856)]


def make_engine():
    llm = RoutingFakeLLM(
        methods_by_title={ANCHOR_T: ["photocurrent measurement", "self-assembly"],
                          PEROV_T: ["transient photocurrent"],
                          GEMS_T: ["raman spectroscopy"]},
        rubric_by_title={PEROV_T: {"strongest_parallel": "time-resolved photocurrent",
                                   "same_method": 4, "specificity": 3, "usage_parallel": 5,
                                   "match": True, "why": "same readout"}})
    return GraphV1Engine(extract_llm=llm, pair_llm=llm, rubric_llm=llm,
                         embed=keyword_embedder, physh=tiny_physh(), workers=1,
                         models={"extract": "fake", "pair_judge": "fake", "rubric": "fake"}), llm


def test_build_returns_an_engine_with_models():
    e = build(provider="deepseek", embed=keyword_embedder, physh=tiny_physh(), llm_factory=lambda m: None)
    assert isinstance(e, Engine) and e.id == "graph_v1" and e.models["rubric"] == "deepseek-reasoner"


def test_index_writes_graph_and_context(tmp_path):
    e, _ = make_engine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    assert (art.path / "graph.json").exists() and (art.path / "name_context.json").exists()
    g = json.loads((art.path / "graph.json").read_text())
    assert set(g["canon"]) == {"transient photocurrent", "raman spectroscopy"}


def test_index_is_resumable(tmp_path):
    e, llm = make_engine()
    run_index(e, corpus(), tmp_path / "idx")
    n = len(llm.prompts)
    run_index(e, corpus(), tmp_path / "idx")
    assert len(llm.prompts) == n           # every stage hit its checkpoint


def test_recommend_scores_from_rubric_and_names_shared_methods(tmp_path):
    e, _ = make_engine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    anchor = external_anchor(ANCHOR_T, "Nanorods self-assembled; photocurrent measured.", ["DPOLY"])
    rows, _ = run_recommend(e, anchor, art, tmp_path / "q")
    assert [r.candidate_id for r in rows] == [12772]          # gems never funneled
    r = rows[0]
    assert r.score == (4 + 3 + 5) / 15 and r.match is True and r.rank == 1
    assert r.cross_domain is True
    assert r.evidence == {"same_method": 4, "specificity": 3, "usage_parallel": 5,
                          "rubric_sum": 12, "match_min_score": 5}
    assert r.shared_methods == ("photocurrent measurement ~ transient photocurrent",)
    validate("recommendation", r.to_row())


def test_recommend_below_threshold_is_reported_not_matched(tmp_path):
    e, llm = make_engine()
    llm.rubric_by_title[PEROV_T] = {"strongest_parallel": "weak", "same_method": 2,
                                    "specificity": 1, "usage_parallel": 1, "match": True, "why": "w"}
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    rows, _ = run_recommend(e, external_anchor(ANCHOR_T, "x", ["DPOLY"]), art, tmp_path / "q")
    assert rows[0].match is False and rows[0].score == 4 / 15
