"""Filing: assign each extracted method (name + usage description) to up to
MAX_NODES PhySH concepts with confidences — the librarian step. Candidate
shelves come from local embeddings (cheap); the assignment judgment is one
LLM call per method. 'none' is a legal answer: an unfiled method simply
gets no tree prior and falls back to the embedding+LLM path."""
from gps_core.llm import LLMClient
from gps_engine.physh import PhySH

MAX_NODES = 3
N_CANDIDATES = 10

FILING_PROMPT = """A research method extracted from a physics conference abstract:
METHOD: {name}
HOW THIS WORK USES IT: {context}

Candidate concepts from the PhySH physics taxonomy (label < parent < ...):
{candidates}

File the method onto the concepts that genuinely classify it (its technique
family, and optionally the property it measures). Rules:
- assignments: 0 to {max_nodes} entries; each {{"index": <candidate number>,
  "confidence": 0.0-1.0}}. confidence = how certain you are the method IS
  (or is a direct kind of) that concept.
- Only file onto a concept if the method truly belongs there; an empty list
  is correct when no candidate fits.
- Never file by application domain or by what system is studied."""


def candidate_shortlist(name: str, context: str, physh: PhySH,
                        embed, target_vecs=None):
    """Top-N filing targets by embedding similarity. target_vecs may be
    precomputed via embed_targets() to avoid re-embedding per method."""
    if target_vecs is None:
        target_vecs = embed_targets(physh, embed)
    import math
    q = embed([f"{name}: {context}"])[0]
    qn = math.sqrt(sum(x * x for x in q))
    scored = []
    for cid, v, vn in target_vecs:
        if qn and vn:
            scored.append((sum(a * b for a, b in zip(q, v)) / (qn * vn), cid))
    scored.sort(reverse=True)
    return [cid for _, cid in scored[:N_CANDIDATES]]


def embed_targets(physh: PhySH, embed):
    import math
    targets = physh.filing_targets()
    texts = [f"{physh.label[cid]} ({physh.parent_chain_labels(cid)})"
             for cid in targets]
    vecs = embed(texts)
    return [(cid, v, math.sqrt(sum(x * x for x in v)))
            for cid, v in zip(targets, vecs)]


def file_method(name: str, context: str, cand_ids: list[str],
                physh: PhySH, llm: LLMClient) -> list[dict]:
    """Returns [{"concept": id, "label": ..., "confidence": float}]."""
    if not cand_ids:
        return []
    lines = [f"{i + 1}. {physh.label[cid]}  ({physh.parent_chain_labels(cid)})"
             for i, cid in enumerate(cand_ids)]
    out = llm.complete_json(
        FILING_PROMPT.format(name=name, context=context,
                             candidates="\n".join(lines),
                             max_nodes=MAX_NODES),
        schema_hint='{"assignments": [{"index": 1, "confidence": 0.9}]}',
    )
    filings = []
    for a in (out.get("assignments") or []):
        if len(filings) >= MAX_NODES:
            break
        try:
            idx = int(a["index"]) - 1
            conf = float(a["confidence"])
        except (KeyError, TypeError, ValueError):
            continue
        if 0 <= idx < len(cand_ids) and 0.0 < conf <= 1.0:
            cid = cand_ids[idx]
            filings.append({"concept": cid, "label": physh.label[cid],
                            "confidence": conf})
    return filings
