from gps_core.filters import default_cross_domain, exclude_authored, ranked
from gps_core.records import Recommendation
from gps_data.talk import external_anchor


def rec(cid, score, for_talk=0):
    return Recommendation(for_talk_id=for_talk, candidate_id=cid, score=score, rank=0,
                          match=True, cross_domain=False, why="", strongest_parallel="",
                          shared_methods=(), evidence={}, engine_id="e", run_id="r")


def test_cross_domain_requires_affirmative_evidence():
    a = external_anchor("a", "x", ["DPOLY"])
    assert default_cross_domain(a, external_anchor("b", "x", ["DBIO"])) is True
    assert default_cross_domain(a, external_anchor("b", "x", ["DPOLY", "DBIO"])) is False
    assert default_cross_domain(a, external_anchor("b", "x", [])) is False
    assert default_cross_domain(external_anchor("a", "x", []), a) is False


def test_exclude_authored_drops_own_work():
    rows = [rec(1, 0.9), rec(2, 0.8), rec(3, 0.7)]
    assert [r.candidate_id for r in exclude_authored(rows, {2})] == [1, 3]


def test_ranked_orders_by_score_then_id_within_each_anchor():
    rows = [rec(5, 0.5), rec(3, 0.9), rec(4, 0.9), rec(9, 1.0, for_talk=7)]
    out = ranked(rows)
    assert [(r.for_talk_id, r.candidate_id, r.rank) for r in out] == [
        (0, 3, 1), (0, 4, 2), (0, 5, 3), (7, 9, 1)]
