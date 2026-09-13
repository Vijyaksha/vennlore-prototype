import json
from dataclasses import replace
from pathlib import Path

from gps_core.contracts import validate
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


def test_write_seed_is_contract_valid(tmp_path):
    e = StubEngine()
    art, _ = run_index(e, corpus(), tmp_path / "idx")
    rows, man = run_recommend(e, external_anchor("m", "a", []), art, tmp_path / "q")
    seed = write_seed(tmp_path / "seed.json", corpus(), rows, [man])
    d = json.loads((tmp_path / "seed.json").read_text())
    assert d["contract_version"] == 1 and len(d["talks"]) == 3 and len(d["runs"]) == 1
    for t in d["talks"]:
        validate("talk", t)
