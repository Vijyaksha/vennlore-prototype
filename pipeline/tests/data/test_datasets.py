import json

from gps_data.datasets import corpus_ids


def test_corpus_ids_reads_an_ids_list(tmp_path):
    p = tmp_path / "sample.json"
    p.write_text(json.dumps({"seed": 2026, "total": 3, "ids": [7, 3, 7, 11]}))
    assert corpus_ids(p) == {3, 7, 11}


def test_corpus_ids_unions_micro_corpus_positives_and_negatives(tmp_path):
    p = tmp_path / "micro.json"
    p.write_text(json.dumps({
        "anchor": {"title": "t"},
        "positives": [{"id": 1}, {"id": 2}],
        "negatives": {"random_unrelated": [3, 4], "same_domain_different_method": [5, 2]},
    }))
    assert corpus_ids(p) == {1, 2, 3, 4, 5}
