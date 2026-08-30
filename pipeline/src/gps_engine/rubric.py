"""Interrogation rubric: judges a funneled candidate against the researcher's
abstract along fixed lines of inquiry. cross_domain is derived deterministically
from unit metadata, never from the LLM."""
from dataclasses import dataclass

from gps_engine.corpus import Talk
from gps_engine.llm import LLMClient

RUBRIC_PROMPT = """You judge whether a candidate talk is METHOD-related to a
researcher's work.

The ONLY criterion: both works USE at least one same (or equivalent) method,
and use it the same WAY — the method plays the same role in each workflow.
Domain, material system, and scientific problem are IRRELEVANT; a cross-domain
match is the most valuable kind. Do NOT lower any score because the fields,
materials, or research questions differ.

Explicitly NOT the criterion:
- Shared phenomenon or physics is NOT sufficient (two works about
  conduction that MEASURE it by different techniques do not match).
- Usefulness is NOT the question ("could they learn from each other" or
  "transferable insight" must not enter the judgment).
- Shared vocabulary or community is NOT the question.

Score each 0-5:
1. same_method: do they use at least one same or equivalent technique,
   measurement, fabrication process, algorithm, or theoretical framework —
   even under different names? Judge the apparatus/procedure, not the words.
2. specificity: how specific is the sharpest shared method? Ubiquitous
   umbrella terms (transport, spectroscopy, simulation, microscopy) score
   0-1; a method named the way practitioners name it (e.g. an EGaIn
   junction, Langmuir-Blodgett deposition, transient-photocurrent readout)
   scores 4-5.
3. usage_parallel: is the shared method used the same WAY — same role in
   the workflow, same inference pattern? (E.g. both use self-assembly AS
   the fabrication step that builds the functional structure; both read a
   time-transient's shape to infer microscopic dynamics; both program a
   persistent state and read it back in transport.)

match: true only if same_method >= 3 AND specificity >= 3 AND
usage_parallel >= 3.

RESEARCHER'S ABSTRACT:
{mine}
{mine_claims}
CANDIDATE TALK:
Title: {title}
Abstract: {abstract}
{cand_claims}"""


@dataclass(frozen=True)
class Judgment:
    candidate_id: int
    same_method: int
    specificity: int
    usage_parallel: int
    match: bool
    cross_domain: bool
    why: str

    @property
    def score(self) -> int:
        return self.same_method + self.specificity + self.usage_parallel


def _claims_block(label: str, digest: str) -> str:
    if not digest:
        return ""
    return f"\n{label} (each with its verbatim source quote):\n{digest}\n"


def judge_candidate(mine: Talk, cand: Talk, llm: LLMClient,
                    mine_claims: str = "", cand_claims: str = "") -> Judgment:
    out = llm.complete_json(
        RUBRIC_PROMPT.format(
            mine=f"{mine.title}\n{mine.abstract}",
            title=cand.title, abstract=cand.abstract,
            mine_claims=_claims_block("RESEARCHER'S STATED CLAIMS", mine_claims),
            cand_claims=_claims_block("CANDIDATE'S STATED CLAIMS", cand_claims)),
        schema_hint='{"same_method": 0, "specificity": 0, '
                    '"usage_parallel": 0, "match": true, "why": "string"}',
    )
    if not isinstance(out["match"], bool):
        raise ValueError(f"non-boolean match from LLM: {out['match']!r}")
    return Judgment(
        candidate_id=cand.id,
        same_method=int(out["same_method"]),
        specificity=int(out["specificity"]),
        usage_parallel=int(out["usage_parallel"]),
        match=out["match"],
        # unknown domain never counts as cross-domain — surprise picks need affirmative evidence
        cross_domain=bool(mine.units) and bool(cand.units) and not (set(mine.units) & set(cand.units)),
        why=str(out["why"]),
    )
