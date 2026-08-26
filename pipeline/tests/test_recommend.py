from gps_engine.recommend import assemble
from gps_engine.rubric import Judgment


def J(cid, score, match=True, cross=False):
    s = score // 3
    return Judgment(candidate_id=cid, shared_methods=s, transferability=s,
                    analogous_phenomena=score - 2 * s, match=match,
                    cross_domain=cross, why="w")


def test_caps_1_2_core_and_2_3_unexpected():
    js = [J(1, 12), J(2, 11), J(3, 10),                     # core
          J(4, 12, cross=True), J(5, 11, cross=True),
          J(6, 10, cross=True), J(7, 9, cross=True)]        # unexpected
    picks = assemble(js)
    assert [j.candidate_id for j in picks.core] == [1, 2]
    assert [j.candidate_id for j in picks.unexpected] == [4, 5, 6]


def test_non_matches_never_picked():
    picks = assemble([J(1, 15, match=False), J(2, 15, match=False, cross=True)])
    assert picks.core == [] and picks.unexpected == []


def test_empty_input_is_valid():
    picks = assemble([])
    assert picks.core == [] and picks.unexpected == []


def test_min_score_threshold_applies():
    picks = assemble([J(1, 5), J(2, 5, cross=True)], min_score=8)
    assert picks.core == [] and picks.unexpected == []
