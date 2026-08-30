"""Claims extraction (adapted from MS GraphRAG's covariate pattern): the
specific factual assertions a talk makes, each anchored to a verbatim quote
from the abstract so any downstream justification can show where it came
from. Grounding is checked mechanically: a claim whose quote is not actually
a substring of the abstract is marked ungrounded, never silently trusted."""
from gps_engine.corpus import Talk
from gps_engine.llm import LLMClient

CLAIMS_PROMPT = """Title: {title}
Abstract: {abstract}

Extract the specific factual claims this work asserts: results achieved,
quantities measured, capabilities or effects demonstrated, firsts claimed.
For each claim:
- about: the method, material, or quantity the claim concerns
- claim: one faithful sentence stating it
- quote: the EXACT abstract text it comes from, copied verbatim (a
  contiguous substring, not a paraphrase)
Only claims grounded in the text above; no background knowledge. [] if the
abstract asserts nothing specific."""


def _squash(text: str) -> str:
    return " ".join(text.casefold().split())


def extract_claims(talk: Talk, llm: LLMClient) -> list[dict]:
    out = llm.complete_json(
        CLAIMS_PROMPT.format(title=talk.title, abstract=talk.abstract),
        schema_hint='{"claims": [{"about": "string", "claim": "string", '
                    '"quote": "string"}]}',
    )
    haystack = _squash(f"{talk.title} {talk.abstract}")
    claims = []
    for c in out.get("claims", []) or []:
        quote = str(c.get("quote", "")).strip()
        claims.append({
            "about": str(c.get("about", "")).strip(),
            "claim": str(c.get("claim", "")).strip(),
            "quote": quote,
            "grounded": bool(quote) and _squash(quote) in haystack,
        })
    return claims


def claims_digest(claims: list[dict], limit: int = 6) -> str:
    """Grounded claims rendered for inclusion in a judge/rubric prompt."""
    lines = [f'- {c["claim"]} [source: "{c["quote"]}"]'
             for c in claims if c["grounded"]][:limit]
    return "\n".join(lines)
