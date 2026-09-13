import pytest

from gps_core import registry
from gps_core.protocol import Engine, IndexArtifact


class DummyEngine:
    id = "dummy"
    models = {}

    def index(self, corpus, out):
        return IndexArtifact(path=out, engine_id=self.id)

    def recommend(self, anchor, index):
        return []


def build_dummy(**kw):
    return DummyEngine()


def test_get_engine_by_name(monkeypatch):
    monkeypatch.setitem(registry.ENGINES, "dummy", f"{__name__}:build_dummy")
    e = registry.get_engine("dummy")
    assert isinstance(e, Engine) and e.id == "dummy"


def test_unknown_engine_lists_known_names():
    with pytest.raises(KeyError, match="graph_v1"):
        registry.get_engine("nope")


def test_graph_v1_is_registered():
    assert "graph_v1" in registry.ENGINES


def test_target_without_a_factory_is_rejected(monkeypatch):
    monkeypatch.setitem(registry.ENGINES, "broken", "gps_core.registry")
    with pytest.raises(ValueError, match="expected 'module:factory'"):
        registry.get_engine("broken")


def test_engine_from_env_reads_name_and_json_config(monkeypatch):
    monkeypatch.setitem(registry.ENGINES, "dummy", f"{__name__}:build_dummy")
    monkeypatch.setenv("ENGINE", "dummy")
    monkeypatch.setenv("ENGINE_CONFIG", '{"pair_judge_model": "x"}')
    seen = {}

    def build_recording(**kw):
        seen.update(kw)
        return DummyEngine()

    monkeypatch.setitem(registry.ENGINES, "dummy", f"{__name__}:build_recording")
    globals()["build_recording"] = build_recording
    e = registry.engine_from_env()
    assert e.id == "dummy" and seen == {"pair_judge_model": "x"}


def test_engine_from_env_defaults(monkeypatch):
    monkeypatch.delenv("ENGINE", raising=False)
    monkeypatch.delenv("ENGINE_CONFIG", raising=False)
    monkeypatch.setitem(registry.ENGINES, "graph_v1", f"{__name__}:build_dummy")
    assert registry.engine_from_env().id == "dummy"
