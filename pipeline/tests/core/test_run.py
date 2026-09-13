import json
from dataclasses import replace
from pathlib import Path

import pytest

from gps_core.contracts import ContractError, validate
from gps_core.protocol import IndexArtifact
from gps_core.records import Recommendation
from gps_core.run import corpus_hash, run_index, run_recommend
from gps_core.store import write_seed
from gps_data.talk import external_anchor


class StubEngine:
    id = "stub"
    models = {"judge": "none"}

    def index(self, corpus, out):
        (out / "index.json").write_text(json.dumps(sorted(t.id for t in corpus)))
        return IndexArtifact(path=out, engine_id=self.id)

    def recommend(self, anchor, index):
        return [Recommendation(for_talk_id=anchor.id, candidate_id=cid, score=s, rank=0,
                               match=s >= 0.5, cross_domain=False, why="w",
                               strongest_parallel="", shared_methods=(),
                               evidence={}, engine_id=self.id, run_id="")
                for cid, s in ((11, 0.9), (10, 0.9), (12, 0.2))]


def corpus():
    return [replace(external_anchor(f"t{i}", "a", ["DPOLY"]), id=i) for i in (10, 11, 12)]


def test_corpus_hash_is_order_independent():
    c = corpus()
    assert corpus_hash(c) == corpus_hash(list(reversed(c)))


def test_run_index_writes_manifest(tmp_path):
    art, man = run_index(StubEngine(), corpus(), tmp_path / "idx")
    assert art.path == tmp_path / "idx" and man.kind == "index"
    validate("run", json.loads((tmp_path / "idx" / "run.json").read_text()))


def test_run_recommend_ranks_filters_validates_and_writes(tmp_path):
    e = StubEngine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    anchor = external_anchor("mine", "a", ["DPOLY"])
    rows, man = run_recommend(e, anchor, art, tmp_path / "q", authored_ids={12})
    assert [(r.candidate_id, r.rank) for r in rows] == [(10, 1), (11, 2)]
    assert all(r.run_id == man.run_id for r in rows)
    saved = json.loads((tmp_path / "q" / "recommendations.json").read_text())
    for row in saved:
        validate("recommendation", row)
    validate("run", json.loads((tmp_path / "q" / "run.json").read_text()))
    assert man.index_path == str(art.path) and man.anchor_ids == (0,)


class WrongAnchorTagEngine:
    id = "stub"
    models = {"judge": "none"}

    def index(self, corpus, out):
        return IndexArtifact(path=out, engine_id=self.id)

    def recommend(self, anchor, index):
        # Two candidates tagged with two DIFFERENT wrong for_talk_ids; if
        # ranking happens before the anchor stamp, they land in separate
        # rank groups (each getting rank 1).
        return [
            Recommendation(for_talk_id=999, candidate_id=10, score=0.9, rank=0,
                           match=True, cross_domain=False, why="w",
                           strongest_parallel="", shared_methods=(),
                           evidence={}, engine_id=self.id, run_id=""),
            Recommendation(for_talk_id=998, candidate_id=20, score=0.5, rank=0,
                           match=True, cross_domain=False, why="w",
                           strongest_parallel="", shared_methods=(),
                           evidence={}, engine_id=self.id, run_id=""),
        ]


def test_run_recommend_stamps_anchor_before_ranking(tmp_path):
    e = WrongAnchorTagEngine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    anchor = external_anchor("mine", "a", ["DPOLY"])
    rows, man = run_recommend(e, anchor, art, tmp_path / "q")
    assert all(r.for_talk_id == anchor.id for r in rows)
    assert sorted(r.rank for r in rows) == [1, 2]
    saved = json.loads((tmp_path / "q" / "recommendations.json").read_text())
    assert all(row["for_talk_id"] == anchor.id for row in saved)
    assert sorted(row["rank"] for row in saved) == [1, 2]


class WrongEngineIdEngine:
    id = "stub"
    models = {"judge": "none"}

    def index(self, corpus, out):
        return IndexArtifact(path=out, engine_id=self.id)

    def recommend(self, anchor, index):
        return [Recommendation(for_talk_id=anchor.id, candidate_id=10, score=0.9, rank=0,
                               match=True, cross_domain=False, why="w",
                               strongest_parallel="", shared_methods=(),
                               evidence={}, engine_id="other", run_id="")]


def test_run_recommend_rejects_row_tagged_with_wrong_engine_id(tmp_path):
    e = WrongEngineIdEngine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    anchor = external_anchor("mine", "a", ["DPOLY"])
    with pytest.raises(ContractError):
        run_recommend(e, anchor, art, tmp_path / "q")
    assert not (tmp_path / "q" / "recommendations.json").exists()


class OutOfRangeScoreEngine:
    id = "stub"
    models = {"judge": "none"}

    def index(self, corpus, out):
        return IndexArtifact(path=out, engine_id=self.id)

    def recommend(self, anchor, index):
        return [Recommendation(for_talk_id=anchor.id, candidate_id=10, score=1.2, rank=0,
                               match=True, cross_domain=False, why="w",
                               strongest_parallel="", shared_methods=(),
                               evidence={}, engine_id=self.id, run_id="")]


def test_run_recommend_rejects_out_of_range_score(tmp_path):
    e = OutOfRangeScoreEngine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    anchor = external_anchor("mine", "a", ["DPOLY"])
    with pytest.raises(ContractError):
        run_recommend(e, anchor, art, tmp_path / "q")
    assert not (tmp_path / "q" / "recommendations.json").exists()


def test_write_seed_is_contract_valid(tmp_path):
    e = StubEngine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    rows, man = run_recommend(e, external_anchor("m", "a", []), art, tmp_path / "q")
    seed = write_seed(tmp_path / "seed.json", corpus(), rows, [man])
    d = json.loads((tmp_path / "seed.json").read_text())
    assert d["contract_version"] == 1 and len(d["talks"]) == 3 and len(d["runs"]) == 1
    for t in d["talks"]:
        validate("talk", t)
