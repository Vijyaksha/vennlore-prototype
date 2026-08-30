"""Method extraction via LlamaIndex's SchemaLLMPathExtractor: a strict,
schema-constrained knowledge-graph builder that pulls the research METHODS a
talk USES (not the system it studies) from its title and abstract."""
from typing import Literal

from llama_index.core.graph_stores.types import KG_NODES_KEY
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor
from llama_index.core.schema import TextNode
from llama_index.llms.anthropic import Anthropic

from gps_engine.corpus import Talk
from gps_engine.llm import LLMClient

# Two entity types, not one: a METHOD--USES_METHOD-->METHOD schema only
# surfaces entities that appear in a valid, non-self-referencing triplet, so
# a talk that uses exactly one method (no partner to pair with) would be
# structurally dropped. WORK is a single fixed node representing the paper/
# talk itself, so even a lone method still forms a valid WORK->METHOD
# triplet and survives extraction.
entities = Literal["WORK", "METHOD"]
relations = Literal["USES_METHOD"]
kg_validation_schema = {"WORK": ["USES_METHOD"]}

EXTRACT_PROMPT = (
    "A METHOD is a technique, algorithm, measurement, fabrication, or "
    "theoretical framework the authors USE — not the system they study, "
    "not the phenomenon. Use the authors' own terminology.\n"
    "Emit one triplet per method found. The subject of every triplet is "
    "ALWAYS the single node named \"THIS_WORK\" (type WORK), representing "
    "the paper/talk itself. The object of every triplet is a METHOD, named "
    "in the authors' own terminology. The relation is always USES_METHOD.\n"
    "Limit to {max_triplets_per_chunk} extracted paths.\n"
    "-------\n"
    "{text}\n"
    "-------\n"
)


def build_extractor(anthropic_model: str) -> SchemaLLMPathExtractor:
    llm = Anthropic(model=anthropic_model)
    return SchemaLLMPathExtractor(
        llm=llm,
        extract_prompt=EXTRACT_PROMPT,
        possible_entities=entities,
        possible_relations=relations,
        kg_validation_schema=kg_validation_schema,
        strict=True,
        # Malformed LLM output must raise, not be swallowed into an empty
        # triplet list that then checkpoints as a false "0 methods" result.
        raise_on_error=True,
        # Visible cap, not the library's silent default of 10.
        max_triplets_per_chunk=25,
    )


def extract_methods_li(talk: Talk, extractor) -> list[str]:
    node = TextNode(
        text=f"{talk.title}\n\n{talk.abstract}",
        id_=str(talk.id),
        metadata={"talk_id": talk.id},
    )
    out_nodes = extractor([node])
    out_node = out_nodes[0]
    if KG_NODES_KEY not in out_node.metadata:
        raise RuntimeError(
            f"extractor did not annotate node with '{KG_NODES_KEY}' metadata "
            f"(talk {talk.id}); cannot distinguish 'no methods found' from "
            "'extraction did not run'"
        )

    seen: set[str] = set()
    result: list[str] = []
    for entity in out_node.metadata[KG_NODES_KEY]:
        if getattr(entity, "label", None) != "METHOD":
            continue
        name = entity.name
        key = " ".join(str(name).casefold().split())
        if key and key not in seen:
            seen.add(key)
            result.append(str(name).strip())
    return result


GLEAN_PROMPT = """Title: {title}
Abstract: {abstract}

A first extraction pass found these METHODS (techniques, algorithms,
measurements, fabrication, or theoretical frameworks the authors USE):
{found}

Reply with:
1. missed_methods: additional methods the authors actually USE that the first
   pass missed. Fabrication, synthesis, and sample-preparation steps COUNT as
   methods even when the resulting structure is the paper's subject (a study
   OF self-assembled monolayers that BUILDS them by self-assembly USES
   self-assembly). Use the authors' own terminology; do not invent methods
   not grounded in the text; [] if nothing was missed.
2. descriptions: for EVERY method (first-pass and missed), one sentence on
   how THIS work uses it."""


def _norm(name: str) -> str:
    return " ".join(str(name).casefold().split())


def glean_and_describe(
    talk: Talk, methods: list[str], llm: LLMClient
) -> tuple[list[str], dict[str, str]]:
    """Second-pass recall sweep + per-method usage descriptions (one call).

    Returns (full method list with gleaned additions deduped in,
    {method name -> one-line description of how this talk uses it})."""
    out = llm.complete_json(
        GLEAN_PROMPT.format(
            title=talk.title, abstract=talk.abstract,
            found="\n".join(f"- {m}" for m in methods) or "(none)"),
        schema_hint='{"missed_methods": ["name"], '
                    '"descriptions": {"name": "one sentence"}}',
    )
    merged = list(methods)
    seen = {_norm(m) for m in methods}
    for m in out.get("missed_methods", []) or []:
        key = _norm(m)
        if key and key not in seen:
            seen.add(key)
            merged.append(str(m).strip())
    descriptions = {str(k).strip(): str(v).strip()
                    for k, v in (out.get("descriptions", {}) or {}).items()}
    return merged, descriptions
