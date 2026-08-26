import math
from typing import Callable

from gps_engine.graph import MethodGraph
from gps_engine.llm import LLMClient

Embedder = Callable[[list[str]], list[list[float]]]

JUDGE_PROMPT = """Two research-method names from physics conference abstracts:
A: {a}
B: {b}
Verdict:
- "same": the same method under different names/spellings/acronyms
- "related": distinct methods that are mathematically or operationally kin
  (one derives from the other, shares core formalism, or routinely substitutes)
- "unrelated": otherwise
Be strict: "related" requires genuine methodological kinship, not co-occurrence."""


def propose_pairs(
    names: list[str], embed: Embedder, threshold: float = 0.75
) -> list[tuple[str, str]]:
    vecs = embed(names)
    norms = [math.sqrt(sum(x * x for x in v)) for v in vecs]
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            na, nb = norms[i], norms[j]
            if na and nb:
                dot = sum(x * y for x, y in zip(vecs[i], vecs[j]))
                cos = dot / (na * nb)
            else:
                cos = 0.0
            if cos >= threshold:
                pairs.append(tuple(sorted((names[i], names[j]))))
    return sorted(set(pairs))


def sbert_embedder() -> Embedder:
    """Live embedder (not unit-tested; used by scripts)."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    return lambda names: model.encode(names).tolist()


def judge_pair(a: str, b: str, llm: LLMClient) -> dict:
    return llm.complete_json(
        JUDGE_PROMPT.format(a=a, b=b),
        schema_hint='{"verdict": "same|related|unrelated", "why": "string"}',
    )


def apply_verdicts(g: MethodGraph, verdicts: list[tuple[str, str, dict]]) -> None:
    for a, b, v in verdicts:
        if v["verdict"] == "same":
            g.merge(g.node_id(a), g.node_id(b))
        elif v["verdict"] == "related":
            g.add_related(g.node_id(a), g.node_id(b))
        elif v["verdict"] != "unrelated":
            raise ValueError(f"unknown verdict {v['verdict']!r} for ({a!r}, {b!r})")
