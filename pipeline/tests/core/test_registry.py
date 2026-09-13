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
