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


def test_work_entity_ignored_single_method_survives():
    """Regression pin for the single-method dropout: SchemaLLMPathExtractor
    only surfaces entities that appear in a valid (non-self-referencing)
    triplet, so a naive METHOD--USES_METHOD-->METHOD schema structurally
    drops talks with exactly one method (no partner to pair with). The fix
    is a WORK--USES_METHOD-->METHOD schema where the subject is always the
    fixed "THIS_WORK" node, so a single method still forms a valid triplet
    and survives. This test pins that extract_methods_li harvests only the
    METHOD entity and ignores the WORK entity, even when it's the only one."""
    fake = FakeExtractor(entities=[
        EntityNode(label="WORK", name="THIS_WORK"),
        EntityNode(label="METHOD", name="DMRG"),
    ])
    assert extract_methods_li(TALK, fake) == ["DMRG"]


def test_build_extractor_smoke(monkeypatch):
    """Construction only — never call() this; no network, no live LLM."""
    pytest.importorskip("llama_index.llms.anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-dummy-not-a-real-key")
    extractor = build_extractor("claude-haiku-4-5-20251001")
    assert extractor.strict is True
    assert extractor.kg_validation_schema == {"WORK": ["USES_METHOD"]}
    assert extractor.raise_on_error is True
    assert extractor.max_triplets_per_chunk == 25


def test_glean_merges_missed_methods_and_dedupes():
    from gps_engine.li_extraction import glean_and_describe
    from gps_engine.llm import FakeLLM

    talk = Talk(id=7, title="T", abstract="A", topics=(), units=(),
                session_title="", start=None, end=None)
    llm = FakeLLM(responses=[{
        "missed_methods": ["self-assembly", "Transient Analysis", "  "],
        "descriptions": {"self-assembly": "builds the monolayer",
                         "transient analysis": "reads decay shapes"},
    }])
    methods, desc = glean_and_describe(talk, ["transient analysis"], llm)
    # gleaned method added; case-insensitive dupe of existing not re-added
    assert methods == ["transient analysis", "self-assembly"]
    assert desc["self-assembly"] == "builds the monolayer"
    # first pass results are in the prompt so the model knows what was found
    assert "transient analysis" in llm.prompts[0]


def test_glean_handles_empty_response_fields():
    from gps_engine.li_extraction import glean_and_describe
    from gps_engine.llm import FakeLLM

    talk = Talk(id=8, title="T", abstract="A", topics=(), units=(),
                session_title="", start=None, end=None)
    llm = FakeLLM(responses=[{"missed_methods": [], "descriptions": {}}])
    methods, desc = glean_and_describe(talk, ["afm"], llm)
    assert methods == ["afm"] and desc == {}
