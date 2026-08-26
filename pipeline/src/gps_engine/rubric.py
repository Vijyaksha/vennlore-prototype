"""Interrogation rubric: judges a funneled candidate against the researcher's
abstract along fixed lines of inquiry. cross_domain is derived deterministically
from unit metadata, never from the LLM."""
from dataclasses import dataclass

from gps_engine.corpus import Talk
from gps_engine.llm import LLMClient

RUBRIC_PROMPT = """You judge whether a conference talk is method-relevant to a
researcher, via these lines of inquiry (score each 0-5):
1. shared_methods: do they USE the same or equivalent methods, even under
   different names? (Judge the mathematics/apparatus, not the vocabulary.)
2. transferability: could the candidate's techniques plausibly transfer to the
   researcher's problem?
3. analogous_phenomena: do they study analogous phenomena in different systems?
Then decide match: true only if a physicist would thank you for the pointer.
Be strict; most candidates are not matches.

RESEARCHER'S ABSTRACT:
{mine}

CANDIDATE TALK:
Title: {title}
Abstract: {abstract}"""


@dataclass(frozen=True)
class Judgment:
    candidate_id: int
    shared_methods: int
    transferability: int
    analogous_phenomena: int
    match: bool
    cross_domain: bool
    why: str

    @property
    def score(self) -> int:
        return self.shared_methods + self.transferability + self.analogous_phenomena


def judge_candidate(mine: Talk, cand: Talk, llm: LLMClient) -> Judgment:
    out = llm.complete_json(
        RUBRIC_PROMPT.format(
            mine=f"{mine.title}\n{mine.abstract}",
            title=cand.title, abstract=cand.abstract),
        schema_hint='{"shared_methods": 0, "transferability": 0, '
                    '"analogous_phenomena": 0, "match": true, "why": "string"}',
    )
    if not isinstance(out["match"], bool):
        raise ValueError(f"non-boolean match from LLM: {out['match']!r}")
    return Judgment(
        candidate_id=cand.id,
        shared_methods=int(out["shared_methods"]),
        transferability=int(out["transferability"]),
        analogous_phenomena=int(out["analogous_phenomena"]),
        match=out["match"],
        # unknown domain never counts as cross-domain — surprise picks need affirmative evidence
        cross_domain=bool(mine.units) and bool(cand.units) and not (set(mine.units) & set(cand.units)),
        why=str(out["why"]),
    )
