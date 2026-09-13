"""Read the corpus id lists the datasets/ files name. Offline, no LLM."""
import json
from pathlib import Path


def corpus_ids(path: Path) -> set[int]:
    """The talk ids a dataset file names: either an explicit `ids` list
    (sample-500.json) or the union of positives and negatives (micro-corpus.json)."""
    d = json.loads(Path(path).read_text())
    if "ids" in d:
        return set(d["ids"])
    neg = d["negatives"]
    return ({p["id"] for p in d["positives"]} | set(neg["random_unrelated"])
            | set(neg["same_domain_different_method"]))
