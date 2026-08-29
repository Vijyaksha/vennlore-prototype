import pytest
from llama_index.core.graph_stores.types import KG_NODES_KEY, EntityNode

from gps_engine.corpus import Talk
from gps_engine.li_extraction import build_extractor, extract_methods_li

TALK = Talk(id=1, title="Kondo physics probed by STM",
            abstract="We use scanning tunneling microscopy and DMRG simulations.",
            topics=(), units=("DCMP",), session_title="", start=None, end=None)


class FakeExtractor:
    """Test double for SchemaLLMPathExtractor: a callable TransformComponent
    stand-in that annotates passed nodes with fake METHOD entities, mimicking
    the real KG_NODES_KEY metadata structure without any LLM call."""

    def __init__(self, entities: list[EntityNode] | None = None, annotate: bool = True):
        self.entities = entities or []
        self.annotate = annotate
        self.received_nodes: list = []

    def __call__(self, nodes):
        self.received_nodes.extend(nodes)
        if self.annotate:
            for node in nodes:
                node.metadata[KG_NODES_KEY] = list(self.entities)
        return nodes


def test_extracts_method_names_from_annotated_entities():
    fake = FakeExtractor(entities=[
        EntityNode(label="METHOD", name="scanning tunneling microscopy"),
        EntityNode(label="METHOD", name="DMRG"),
    ])
    assert extract_methods_li(TALK, fake) == ["scanning tunneling microscopy", "DMRG"]


def test_node_text_contains_title_and_abstract():
    fake = FakeExtractor(entities=[])
    extract_methods_li(TALK, fake)
    node = fake.received_nodes[0]
    assert "Kondo physics" in node.text and "DMRG simulations" in node.text


def test_dedupes_and_drops_blank():
    fake = FakeExtractor(entities=[
        EntityNode(label="METHOD", name="DMRG"),
        EntityNode(label="METHOD", name="dmrg "),
        EntityNode(label="METHOD", name=""),
    ])
    assert extract_methods_li(TALK, fake) == ["DMRG"]


def test_non_method_labeled_entities_are_ignored():
    fake = FakeExtractor(entities=[
        EntityNode(label="METHOD", name="DMRG"),
        EntityNode(label="ORGANIZATION", name="MIT"),
    ])
    assert extract_methods_li(TALK, fake) == ["DMRG"]


def test_missing_annotation_raises():
    fake = FakeExtractor(annotate=False)
    with pytest.raises(RuntimeError):
        extract_methods_li(TALK, fake)


def test_build_extractor_smoke(monkeypatch):
    """Construction only — never call() this; no network, no live LLM."""
    pytest.importorskip("llama_index.llms.anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-dummy-not-a-real-key")
    extractor = build_extractor("claude-haiku-4-5-20251001")
    assert extractor.strict is True
    assert extractor.kg_validation_schema == {"METHOD": ["USES_METHOD"]}
