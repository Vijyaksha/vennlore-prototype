"""graphrag_v1: Vennlore's GraphRAG as a pluggable engine. Rows must be
contract-valid, so the existing web UI can serve them with ENGINE_ID=graphrag_v1."""
import json

import pytest

from gps_core import registry
from gps_core.contracts import validate
from gps_core.protocol import Engine
from gps_core.run import run_index, run_recommend
from gps_engines.graphrag_v1.engine import GraphRAGEngine, build

from .fakes import (
    ANCHOR_T,
    EXCITON_T,
    LEAK,
    MEMBRANE_T,
    METHODS,
    ExhaustedLLM,
    RoutingFakeLLM,
    anchor,
    corpus,
)


def make(llm=None, **kw):
    models = {"extract": "fake", "themes": "fake", "explain": "fake"} if llm else {}
    return GraphRAGEngine(llm=llm, models=models, workers=1, **kw)


def run(engine, tmp_path, a=None):
    talks = corpus()
    art, _ = run_index(engine, talks, tmp_path / "idx")
    rows, _ = run_recommend(engine, a or anchor(), art, tmp_path / "q", corpus=talks)
    return {r.candidate_id: r for r in rows}, art


# ---- registry and factory -------------------------------------------------

def test_registered_in_the_engine_registry():
    assert registry.ENGINES["graphrag_v1"] == "gps_engines.graphrag_v1.engine:build"


def test_build_defaults_to_the_free_local_llm():
    made = []
    e = build(llm_factory=lambda m: made.append(m) or object())
    assert isinstance(e, Engine) and e.id == "graphrag_v1"
    assert e.models == {"extract": "local", "themes": "local", "explain": "local"}
    assert made == ["local"]


def test_build_provider_none_runs_without_any_llm():
    e = build(provider="none")
    assert e.llm is None and e.models == {}


def test_build_rejects_unknown_provider():
    with pytest.raises(KeyError, match="local"):
        build(provider="nope")


# ---- index ------------------------------------------------------------------

def test_index_rejects_duplicate_talk_ids(tmp_path):
    with pytest.raises(AssertionError, match="duplicate talk ids"):
        make().index(corpus() + corpus()[:1], tmp_path)


def test_index_writes_graph_themes_and_a_status_file(tmp_path):
    art = make(RoutingFakeLLM()).index(corpus(), tmp_path)
    data = json.loads((art.path / "index.json").read_text())
    assert art.engine_id == "graphrag_v1"
    assert {t["id"] for t in data["talks"]} == {2, 3, 4, 5}
    assert "transient photocurrent" in data["talks"][1]["methods"]
    assert data["themes"] and all(t["title"] and t["talk_ids"] for t in data["themes"])
    assert json.loads((tmp_path / "status.json").read_text())["phase"]


def test_rerun_resumes_from_checkpoints_without_calling_the_llm(tmp_path):
    make(RoutingFakeLLM()).index(corpus(), tmp_path)
    make(ExhaustedLLM()).index(corpus(), tmp_path)   # would raise if it called the LLM


# ---- recommend: the contract --------------------------------------------------

def test_rows_are_contract_valid_and_tagged(tmp_path):
    rows, _ = run(make(RoutingFakeLLM()), tmp_path)
    assert rows
    for r in rows.values():
        validate("recommendation", r.to_row())
        assert r.engine_id == "graphrag_v1" and 0.0 <= r.score <= 1.0


def test_engine_returns_rank_zero_and_empty_run_id(tmp_path):
    e = make(RoutingFakeLLM())
    art = e.index(corpus(), tmp_path)
    raw = e.recommend(anchor(), art)
    assert raw and all(r.rank == 0 and r.run_id == "" for r in raw)


def test_engine_reads_only_permitted_talk_fields(tmp_path):
    llm = RoutingFakeLLM()
    rows, art = run(make(llm), tmp_path)
    assert not any(LEAK in p for p in llm.prompts)
    assert LEAK not in (art.path / "index.json").read_text()
    assert not any(LEAK in json.dumps(r.to_row()) for r in rows.values())


# ---- recommend: GraphRAG behaviour ---------------------------------------------

def test_same_division_neighbour_is_a_core_pick(tmp_path):
    rows, _ = run(make(RoutingFakeLLM()), tmp_path)
    core = rows[2]
    assert core.match and not core.cross_domain
    assert "self-assembly" in core.shared_methods


def test_other_division_sharing_a_method_is_an_unexpected_pick(tmp_path):
    rows, _ = run(make(RoutingFakeLLM()), tmp_path)
    surprise = rows[3]
    assert surprise.match and surprise.cross_domain
    assert "transient photocurrent" in surprise.shared_methods
    assert "transient photocurrent" in surprise.strongest_parallel
    assert surprise.evidence["bridge"] == "transient photocurrent"


def test_unrelated_talk_is_not_a_match(tmp_path):
    rows, _ = run(make(RoutingFakeLLM()), tmp_path)
    assert 4 not in rows or not rows[4].match


def test_pick_caps_follow_the_product_two_core_three_unexpected(tmp_path):
    rows, _ = run(make(RoutingFakeLLM()), tmp_path)
    matched = [r for r in rows.values() if r.match]
    assert sum(not r.cross_domain for r in matched) <= 2
    assert sum(r.cross_domain for r in matched) <= 3


def test_evidence_carries_the_graph_path_and_theme(tmp_path):
    rows, _ = run(make(RoutingFakeLLM()), tmp_path)
    ev = rows[3].evidence
    assert ev["hops"] in (1, 3) and ev["path"] and isinstance(ev["theme"], str)
    assert ev["explained_by"] == "llm"


def test_why_is_written_by_the_llm_from_retrieved_context_only(tmp_path):
    llm = RoutingFakeLLM()
    rows, _ = run(make(llm), tmp_path)
    assert rows[2].why == "Grounded reason for talk 2 from its graph link."
    explain = [p for p in llm.prompts if "Explain each recommendation" in p][0]
    assert EXCITON_T in explain and MEMBRANE_T in explain
    assert "Transformer networks" not in explain   # not retrieved, so not shown


def test_falls_back_to_template_reasons_when_the_llm_fails(tmp_path):
    rows, _ = run(make(RoutingFakeLLM(explain_fails=True)), tmp_path)
    assert rows[3].why and rows[3].evidence["explained_by"] == "template"
    assert "transient photocurrent" in rows[3].why


def test_works_with_no_llm_at_all(tmp_path):
    rows, _ = run(make(None), tmp_path)
    assert rows[2].match and not rows[2].cross_domain
    assert all(r.evidence["explained_by"] == "template" for r in rows.values())


def test_survives_an_llm_that_always_fails(tmp_path):
    rows, _ = run(make(RoutingFakeLLM(everything_fails=True)), tmp_path)
    assert rows[2].match


def test_anchor_never_recommends_itself(tmp_path):
    from dataclasses import replace
    inside = replace(corpus()[0], title=ANCHOR_T)
    rows, _ = run(make(RoutingFakeLLM()), tmp_path, a=inside)
    assert inside.id not in rows


def test_anchor_with_no_graph_concepts_is_scored_on_wording_alone(tmp_path):
    """No topics, no LLM, no concept mentions: the text evidence alone must be able
    to clear the core bar instead of being halved by an empty concept term."""
    from gps_data.talk import external_anchor
    a = external_anchor("Diffusion of bound electron-hole pairs in dye films",
                        "Bound electron-hole pairs diffuse through organic semiconductor dye "
                        "films self-assembled from porphyrin molecules.", ["DPOLY"])
    rows, _ = run(make(None), tmp_path, a=a)
    assert rows[2].match and rows[2].evidence["concept_similarity"] == 0.0
    assert rows[2].score == pytest.approx(rows[2].evidence["text_similarity"], abs=1e-3)


def test_free_text_query_borrows_the_division_of_its_closest_talks(tmp_path):
    """A search query has no APS unit. It takes the units of its best-matching
    talks, so other-division talks can still be flagged unexpected."""
    from gps_data.talk import external_anchor
    query = external_anchor(
        "my research",
        "I study exciton transport and photoconductivity in self-assembled porphyrin "
        "organic semiconductor films using transient photocurrent.", [])
    llm = RoutingFakeLLM(methods={**METHODS, "my research": ["transient photocurrent"]})
    rows, _ = run(make(llm), tmp_path, a=query)
    assert rows[2].match and not rows[2].cross_domain      # DPOLY, like its best match
    assert rows[3].match and rows[3].cross_domain          # DBIO via transient photocurrent


def test_query_division_is_a_vote_of_its_top_matches_not_one_outlier(tmp_path):
    """One close paper from another field must not decide the searcher's home division."""
    from dataclasses import replace

    from gps_data.talk import external_anchor
    talks = corpus() + [
        replace(external_anchor("q", "Exciton transport and photoconductivity in self-assembled "
                                     "porphyrin organic semiconductor films.",
                                ["bioRxiv:biophysics"]), id=9,
                topics=("Excitons", "Organic Materials", "Polymer Physics")),
        replace(external_anchor("Porphyrin exciton films", "Exciton transport in self-assembled "
                                "porphyrin organic semiconductor films.", ["DPOLY"]), id=6),
    ]
    query = external_anchor("q", "Exciton transport and photoconductivity in self-assembled "
                                 "porphyrin organic semiconductor films.", [])
    e = make(None)
    art = e.index(talks, tmp_path)
    rows = {r.candidate_id: r for r in e.recommend(query, art)}
    assert not rows[2].cross_domain and not rows[6].cross_domain   # DPOLY is home
    assert rows[9].cross_domain                                    # the bioRxiv outlier is not
