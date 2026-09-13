import json

from gps_core.checkpoint import checkpointed, content_key


def test_content_key_is_stable_and_order_independent_for_dicts():
    a = content_key("graph_v1", "methods", {"id": 1, "title": "t"})
    b = content_key("graph_v1", "methods", {"title": "t", "id": 1})
    assert a == b and len(a) == 24


def test_content_key_changes_when_any_part_changes():
    base = content_key("graph_v1", "methods", {"id": 1})
    assert content_key("graph_v2", "methods", {"id": 1}) != base
    assert content_key("graph_v1", "claims", {"id": 1}) != base
    assert content_key("graph_v1", "methods", {"id": 2}) != base


def test_checkpointed_runs_once_and_resumes(tmp_path):
    calls = []
    p = tmp_path / "x.json"
    assert checkpointed(p, lambda: calls.append(1) or {"v": 1}) == {"v": 1}
    assert checkpointed(p, lambda: calls.append(1) or {"v": 2}) == {"v": 1}
    assert calls == [1]
    assert json.loads(p.read_text()) == {"v": 1}
    assert not p.with_suffix(".tmp").exists()
