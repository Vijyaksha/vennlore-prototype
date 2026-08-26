"""Method extraction: schema-constrained LLM call that pulls the research
methods a talk USES (not the system it studies) from its title and abstract."""
from gps_engine.corpus import Talk
from gps_engine.llm import LLMClient

PROMPT = """Extract the research METHODS used in this conference abstract.
A method is a technique, algorithm, measurement, fabrication, or theoretical
framework the authors USE (not the system they study, not the phenomenon).
Use the authors' own terminology. Return every distinct method.

Title: {title}
Abstract: {abstract}"""


def extract_methods(talk: Talk, llm: LLMClient) -> list[str]:
    out = llm.complete_json(
        PROMPT.format(title=talk.title, abstract=talk.abstract),
        schema_hint='{"methods": ["string", ...]}',
    )
    seen, result = set(), []
    for m in out.get("methods", []):
        key = " ".join(str(m).casefold().split())
        if key and key not in seen:
            seen.add(key)
            result.append(str(m).strip())
    return result
