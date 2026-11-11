import json
from dataclasses import replace

import pytest

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


def make_engine(anchor_methods=("photocurrent measurement", "self-assembly"),
                refuse=()):
    llm = RoutingFakeLLM(
        methods_by_title={ANCHOR_T: list(anchor_methods),
                          PEROV_T: ["transient photocurrent"],
                          GEMS_T: ["raman spectroscopy"]},
        rubric_by_title={PEROV_T: {"strongest_parallel": "time-resolved photocurrent",
                                   "same_method": 4, "specificity": 3, "usage_parallel": 5,
                                   "match": True, "why": "same readout"}},
        raise_refusal_for=set(refuse))
    return GraphV1Engine(extract_llm=llm, pair_llm=llm, rubric_llm=llm,
                         embed=keyword_embedder, physh=tiny_physh(), workers=1,
                         models={"extract": "fake", "pair_judge": "fake", "rubric": "fake"}), llm


def test_build_returns_an_engine_with_models():
    e = build(provider="deepseek", embed=keyword_embedder, physh=tiny_physh(), llm_factory=lambda m: None)
    assert isinstance(e, Engine) and e.id == "graph_v1" and e.models["rubric"] == "deepseek-reasoner"


def test_build_takes_per_stage_model_overrides():
    """The stage-0 reference run judged PAIRS with deepseek-reasoner; the
    provider default (deepseek-chat) is the stage-1 choice."""
    e = build(provider="deepseek", pair_judge_model="deepseek-reasoner",
              embed=keyword_embedder, physh=tiny_physh(), llm_factory=lambda m: m)
    assert e.models["pair_judge"] == "deepseek-reasoner"
    assert e.pair_llm == "deepseek-reasoner"
    assert e.models["extract"] == "deepseek-chat" and e.extract_llm == "deepseek-chat"


def test_index_rejects_duplicate_talk_ids(tmp_path):
    e, _ = make_engine()
    dup = corpus() + [corpus()[0]]
    with pytest.raises(AssertionError, match="duplicate talk ids"):
        e.index(dup, tmp_path / "idx")


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


def test_anchor_method_names_are_normalised_against_the_index(tmp_path):
    """An anchor method spelled differently in case is the SAME name: it must
    not be re-filed, nor cross-judged against its own twin in the index."""
    e, llm = make_engine(anchor_methods=["Transient Photocurrent"])
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    n = len(llm.prompts)
    rows, _ = run_recommend(e, external_anchor(ANCHOR_T, "x", ["DPOLY"]), art, tmp_path / "q")
    after = llm.prompts[n:]
    assert not [p for p in after if "METHOD: Transient Photocurrent" in p]   # no re-filing
    assert not [p for p in after if "Two research-method names" in p]        # no self-pair judge
    assert [r.candidate_id for r in rows] == [12772]
    assert rows[0].shared_methods == ("transient photocurrent",)


def test_rubric_refusal_defaults_to_no_match_and_says_so(tmp_path, capsys):
    e, _ = make_engine(refuse=[PEROV_T])
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    rows, _ = run_recommend(e, external_anchor(ANCHOR_T, "x", ["DPOLY"]), art, tmp_path / "q")
    r = rows[0]
    assert r.evidence["same_method"] == r.evidence["specificity"] == r.evidence["usage_parallel"] == 0
    assert r.match is False and r.score == 0.0 and "API REFUSAL" in r.why
    assert "REFUSAL" in capsys.readouterr().out


def test_recommend_reuses_index_checkpoints_for_candidates(tmp_path):
    e, llm = make_engine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    n = len(llm.prompts)
    run_recommend(e, external_anchor(ANCHOR_T, "x", ["DPOLY"]), art, tmp_path / "q")
    after = llm.prompts[n:]
    # only the ANCHOR's own extraction/claims are new; the candidate's are hits
    assert len([p for p in after if "List every method" in p]) == 1
    assert len([p for p in after if "factual claims" in p]) == 1


def test_recommend_is_resumable(tmp_path):
    e, llm = make_engine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    anchor = external_anchor(ANCHOR_T, "x", ["DPOLY"])
    run_recommend(e, anchor, art, tmp_path / "q")
    n = len(llm.prompts)
    run_recommend(e, anchor, art, tmp_path / "q")
    assert len(llm.prompts) == n


def test_query_status_dirs_do_not_collide_between_external_anchors(tmp_path):
    e, _ = make_engine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    run_recommend(e, external_anchor(ANCHOR_T, "x", ["DPOLY"]), art, tmp_path / "q1")
    run_recommend(e, external_anchor("A different anchor entirely", "y", ["DPOLY"]),
                  art, tmp_path / "q2")
    # both anchors are id 0; their engine-side status dirs must still differ
    assert len(list((art.path / "queries").iterdir())) == 2


def test_checkpoint_keys_depend_only_on_the_stage_model(tmp_path):
    e1, _ = make_engine()
    e2, _ = make_engine()
    e2.models = {**e2.models, "pair_judge": "other"}
    assert e1._ck(tmp_path, "methods", 1) == e2._ck(tmp_path, "methods", 1)
    assert e1._ck(tmp_path, "verdicts", "a", "b", "") != e2._ck(tmp_path, "verdicts", "a", "b", "")
    e3, _ = make_engine()
    e3.models = {**e3.models, "extract": "other"}
    assert e1._ck(tmp_path, "methods", 1) != e3._ck(tmp_path, "methods", 1)


def test_unusable_llm_response_defaults_to_no_match_and_says_so(tmp_path, capsys):
    llm = RoutingFakeLLM(
        methods_by_title={ANCHOR_T: ["photocurrent measurement"], PEROV_T: ["transient photocurrent"],
                          GEMS_T: ["raman spectroscopy"]},
        rubric_by_title={}, raise_unusable_for={PEROV_T})
    e = GraphV1Engine(extract_llm=llm, pair_llm=llm, rubric_llm=llm, embed=keyword_embedder,
                      physh=tiny_physh(), workers=1,
                      models={"extract": "fake", "pair_judge": "fake", "rubric": "fake"})
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    rows, _ = run_recommend(e, external_anchor(ANCHOR_T, "x", ["DPOLY"]), art, tmp_path / "q")
    r = rows[0]
    assert r.match is False and r.score == 0.0 and "API UNUSABLE" in r.why
    assert "UNUSABLE" in capsys.readouterr().out


def test_build_local_provider_runs_free_on_lm_studio_or_ollama():
    """provider='local' uses the free LocalLLM client (no API key, no spend)."""
    from gps_core.llm import LocalLLM
    from gps_engines.graph_v1.engine import PROVIDERS
    assert PROVIDERS["local"]["client"] is LocalLLM
    made = []
    e = build(provider="local", embed=keyword_embedder, physh=tiny_physh(),
              llm_factory=lambda m: made.append(m) or m)
    assert e.models == {"extract": "local", "pair_judge": "local", "rubric": "local"}
    assert made == ["local", "local", "local"]
