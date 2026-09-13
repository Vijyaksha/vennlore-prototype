import pytest

from gps_core.contracts import ContractError, validate
from gps_core.records import CONTRACT_VERSION, Recommendation, RunManifest


def rec(**kw):
    base = dict(for_talk_id=0, candidate_id=12772, score=0.8, rank=1, match=True,
                cross_domain=True, why="w", strongest_parallel="p",
                shared_methods=("transient photocurrent",),
                evidence={"rubric_sum": 12}, engine_id="graph_v1", run_id="r1")
    return Recommendation(**{**base, **kw})


def test_recommendation_row_is_contract_valid():
    validate("recommendation", rec().to_row())


def test_recommendation_row_carries_contract_version():
    assert rec().to_row()["contract_version"] == CONTRACT_VERSION == 1


def test_recommendation_score_out_of_range_is_rejected_by_contract():
    with pytest.raises(ContractError):
        validate("recommendation", rec(score=1.5).to_row())


def test_manifest_row_is_contract_valid():
    m = RunManifest(run_id="r1", engine_id="graph_v1", kind="recommend",
                    engine_version="abc1234", models={"rubric": "deepseek-reasoner"},
                    corpus_hash="deadbeef", anchor_ids=(0,),
                    started_at="2026-09-12T12:00:00Z", finished_at="2026-09-12T12:00:34Z",
                    index_path="out/x")
    validate("run", m.to_row())
