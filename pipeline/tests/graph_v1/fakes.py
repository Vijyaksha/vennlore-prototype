"""Deterministic stand-ins: an LLM that answers by prompt type, an embedder
that answers by keyword, and a 6-node PhySH tree."""
from gps_engines.graph_v1.physh import PhySH


class RoutingFakeLLM:
    """Routes on the prompt text so call ORDER does not matter (the engine
    runs stages on a thread pool)."""

    def __init__(self, methods_by_title: dict[str, list[str]],
                 rubric_by_title: dict[str, dict]):
        self.methods_by_title = methods_by_title
        self.rubric_by_title = rubric_by_title
        self.prompts: list[str] = []

    def _title_in(self, prompt: str, table: dict):
        for title, val in table.items():
            if title in prompt:
                return val
        return None

    def complete_json(self, prompt: str, schema_hint: str) -> dict:
        self.prompts.append(prompt)
        if "List every method" in prompt:                       # extraction
            return {"methods": self._title_in(prompt, self.methods_by_title) or []}
        if "missed_methods" in prompt:                          # glean + describe
            ms = self._title_in(prompt, self.methods_by_title) or []
            return {"missed_methods": [], "descriptions": {m: f"uses {m}" for m in ms}}
        if "factual claims" in prompt:                          # claims
            return {"claims": []}
        if "File the method onto" in prompt:                    # PhySH filing
            return {"assignments": []}
        if "Two research-method names" in prompt:               # pair judge
            return {"verdict": "related", "strength": 7, "why": "kin"}
        if "METHOD-related" in prompt:                          # rubric
            r = self._title_in(prompt, self.rubric_by_title)
            return r or {"strongest_parallel": "none", "same_method": 0,
                         "specificity": 0, "usage_parallel": 0, "match": False, "why": "no"}
        raise AssertionError(f"unrouted prompt: {prompt[:80]!r}")


def keyword_embedder(texts: list[str]) -> list[list[float]]:
    out = []
    for t in texts:
        t = t.lower()
        if "photocurrent" in t:
            out.append([1.0, 0.0, 0.0])
        elif "self-assembl" in t:
            out.append([0.0, 1.0, 0.0])
        else:
            out.append([0.0, 0.0, 1.0])
    return out


def tiny_physh() -> PhySH:
    label = {"opt": "Optical techniques", "pl": "Photoluminescence",
             "pc": "Photocurrent", "sp": "Sample preparation",
             "sa": "Self-assembly", "lb": "Langmuir-Blodgett deposition"}
    broader = {"pl": ["opt"], "pc": ["opt"], "sa": ["sp"], "lb": ["sa"], "opt": [], "sp": []}
    facet = {k: "Experimental Techniques" for k in label}
    return PhySH(label, {k: [] for k in label}, broader, facet)
