import math
from typing import Callable

Embedder = Callable[[list[str]], list[list[float]]]


def _cos(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def propose_pairs(
    names: list[str], embed: Embedder, threshold: float = 0.75
) -> list[tuple[str, str]]:
    vecs = embed(names)
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if _cos(vecs[i], vecs[j]) >= threshold:
                pairs.append(tuple(sorted((names[i], names[j]))))
    return sorted(set(pairs))


def sbert_embedder() -> Embedder:
    """Live embedder (not unit-tested; used by scripts)."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    return lambda names: model.encode(names).tolist()
