import importlib.util
from pathlib import Path

from gps_core.records import Recommendation

spec = importlib.util.spec_from_file_location(
    "eval_stage0", Path(__file__).resolve().parents[2] / "scripts" / "eval_stage0.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def rec(cid, match):
    return Recommendation(for_talk_id=0, candidate_id=cid, score=0.5, rank=1, match=match,
                          cross_domain=False, why="", strongest_parallel="", shared_methods=(),
                          evidence={}, engine_id="e", run_id="r")


def test_report_counts_hits_misses_fps_and_funnel_gaps():
    rows = [rec(1, True), rec(2, False), rec(9, True)]
    r = mod.report(rows, positives={1, 2, 3}, corpus_size=58)
    assert r["hit_positives"] == [1] and r["missed_positives"] == [2, 3]
    assert r["false_positives"] == [9] and r["positives_not_in_funnel"] == [3]
    assert r["funnel_candidates"] == [1, 2, 9] and r["corpus_size"] == 58
