"""Deterministic stand-ins for graphrag_v1: a tiny corpus spanning four APS
units and an LLM that answers by prompt type (call order never matters,
because the engine runs stages on a thread pool)."""
from dataclasses import replace

from gps_core.llm import LLMUnusable
from gps_data.talk import Talk, external_anchor

ANCHOR_T = "Photoconductivity of self-assembled porphyrin nanorods"
EXCITON_T = "Exciton transport in organic semiconductor films"
MEMBRANE_T = "Transient photocurrent probes of light-gated membrane proteins"
GRAV_T = "Transformer networks for continuous gravitational-wave searches"
POLYML_T = "Machine-learned potentials for polymer melts"
LEAK = "SHOULD_NOT_LEAK"


def talk(id: int, title: str, abstract: str, units: list[str], topics: list[str]) -> Talk:
    # Fields an engine must not read carry a marker the tests look for.
    return replace(external_anchor(title, abstract, units), id=id, topics=tuple(topics),
                   session_title=LEAK, room=LEAK, funding_acknowledgement=LEAK)


def corpus() -> list[Talk]:
    return [
        talk(2, EXCITON_T,
             "We measure exciton diffusion and photoconductivity in organic semiconductor "
             "films self-assembled from porphyrin dyes using transient photocurrent.",
             ["DPOLY"], ["Excitons", "Organic Materials", "Polymer Physics"]),
        talk(3, MEMBRANE_T,
             "Light-gated ion channels are probed with transient photocurrent recordings "
             "to resolve gating kinetics in lipid membranes.",
             ["DBIO"], ["Biological Physics", "Membranes", "Ion Channels"]),
        talk(4, GRAV_T,
             "We search for continuous gravitational waves from neutron stars with "
             "transformer neural networks trained on detector noise.",
             ["DGRAV"], ["Gravitational Waves", "AI/Machine Learning", "Neutron Stars"]),
        talk(5, POLYML_T,
             "Neural network interatomic potentials accelerate molecular dynamics of "
             "entangled polymer melts.",
             ["DPOLY"], ["Polymer Physics", "AI/Machine Learning", "Molecular Dynamics"]),
    ]


def anchor() -> Talk:
    return external_anchor(
        ANCHOR_T,
        "Self-assembled porphyrin nanorods become photoconductive under illumination; "
        "we use transient photocurrent and exciton models to explain the response.",
        ["DPOLY"])


METHODS = {
    ANCHOR_T: ["transient photocurrent", "self-assembly"],
    EXCITON_T: ["exciton diffusion measurement", "self-assembly"],
    MEMBRANE_T: ["transient photocurrent", "patch clamp"],
    GRAV_T: ["transformer neural network", "matched filtering"],
    POLYML_T: ["machine-learned potential", "molecular dynamics"],
}


class RoutingFakeLLM:
    def __init__(self, methods: dict[str, list[str]] | None = None,
                 explain_fails: bool = False, everything_fails: bool = False):
        self.methods = METHODS if methods is None else methods
        self.explain_fails = explain_fails
        self.everything_fails = everything_fails
        self.prompts: list[str] = []

    def complete_json(self, prompt: str, schema_hint: str) -> dict:
        self.prompts.append(prompt)
        if self.everything_fails:
            raise LLMUnusable("no usable JSON response after 3 attempts")
        if "List the research methods" in prompt:
            for title, ms in self.methods.items():
                if title in prompt:
                    return {"methods": ms}
            return {"methods": []}
        if "Name the research theme" in prompt:
            return {"title": "Light-driven charge transport",
                    "summary": "Talks that read out charge dynamics with light."}
        if "Answer the question using ONLY these research themes" in prompt:
            return {"answer": "Grounded answer from the listed themes."}
        if "Explain each recommendation" in prompt:
            if self.explain_fails:
                raise LLMUnusable("no usable JSON response after 3 attempts")
            ids = [line.split(" | ")[0].strip() for line in prompt.splitlines()
                   if line.strip().split(" | ")[0].strip().isdigit()]
            return {"reasons": {i: f"Grounded reason for talk {i} from its graph link."
                                for i in ids}}
        raise AssertionError(f"unexpected prompt: {prompt[:80]!r}")


class ExhaustedLLM:
    """Fails the test if called: used to prove a rerun resumes from checkpoints."""

    def complete_json(self, prompt: str, schema_hint: str) -> dict:
        raise AssertionError("LLM called although every result was checkpointed")
