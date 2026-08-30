import math
from typing import Callable

from gps_engine.graph import MethodGraph
from gps_engine.llm import LLMClient

Embedder = Callable[[list[str]], list[list[float]]]

JUDGE_PROMPT = """Two research-method names from physics conference abstracts:
A: {a}{ctx_a}
B: {b}{ctx_b}
Verdict:
- "same": the same method under different names/spellings/acronyms
- "related": distinct methods that are mathematically or operationally kin
  (one derives from the other, shares core formalism, or routinely substitutes)
- "unrelated": otherwise
For "same" or "related", also give strength 1-10: how substitutable/close the
methods are (10 = interchangeable in practice; 5 = clear shared formalism or
apparatus; 1 = distant kinship barely worth an edge). Omit or 0 for unrelated.
Be strict: "related" requires genuine methodological kinship, not co-occurrence.
Judge the METHODS themselves; any context line only disambiguates what each
name means in its source talk (the same words can name different things)."""


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


def judge_pair(
    a: str, b: str, llm: LLMClient,
    context_a: str = "", context_b: str = "",
    evidence: str = "",
) -> dict:
    ctx_b = f"\n   (context: {context_b})" if context_b else ""
    if evidence:
        ctx_b += f"\nStructural evidence: {evidence}"
    return llm.complete_json(
        JUDGE_PROMPT.format(
            a=a, b=b,
            ctx_a=f"\n   (context: {context_a})" if context_a else "",
            ctx_b=ctx_b),
        schema_hint='{"verdict": "same|related|unrelated", "strength": 0, '
                    '"why": "string"}',
    )


def apply_verdicts(g: MethodGraph, verdicts: list[tuple[str, str, dict]]) -> None:
    for a, b, v in verdicts:
        if v["verdict"] == "same":
            g.merge(g.node_id(a), g.node_id(b))
        elif v["verdict"] == "related":
            g.add_related(g.node_id(a), g.node_id(b),
                          strength=int(v.get("strength") or 0),
                          why=str(v.get("why", "")))
        elif v["verdict"] != "unrelated":
            raise ValueError(f"unknown verdict {v['verdict']!r} for ({a!r}, {b!r})")
