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
match is the most valuable kind.

FIRST, before scoring, steelman: state in one sentence the STRONGEST
usage-parallel between the two works that the texts support (field
"strongest_parallel"). Then score THAT parallel — not the works' overall
similarity.

Scoring discipline:
- Differences in phenomena, materials, timescales, transported quantity,
  or programming input must NOT lower any score. Two works that both use
  self-assembly as their fabrication step match on that axis even if one
  studies conduction and the other mechanics.
- Cataloguing differences is not a judgment. Judge the shared usage.
- Abstracts are compressed: score what the texts support or are plainly
  consistent with. Do not demand that every procedural detail be spelled
  out; do not credit anything the texts contradict.

Explicitly NOT the criterion:
- Shared phenomenon or physics alone is NOT sufficient (two works about
  conduction that MEASURE it by different techniques do not match).
- Usefulness is NOT the question ("could they learn from each other" or
  "transferable insight" must not enter the judgment).
- Shared vocabulary or community is NOT the question.

Score each 0-5, using these anchors:
1. same_method — is there at least one shared technique/measurement/
   fabrication/algorithm/framework? Judge the apparatus and procedure, not
   the words.
   5 = the same named technique. 4 = VARIANTS of one technique differing
   only in implementation — timescale (femtosecond vs millisecond),
   resolution, drive, or contrast knob (light vs bias vs field): a DC
   photocurrent transient and an ultrafast pump-probe photocurrent
   transient are the same method at 4; lab-source and synchrotron
   diffraction are the same method at 4. 3 = different techniques that
   effect the same operation by the same physical principle. 2 = same
   broad family only. 0-1 = nothing genuinely shared.
2. specificity — how specific is the sharpest shared method? 0-1 =
   ubiquitous umbrella (transport, spectroscopy, simulation, microscopy).
   2-3 = a real named method. 4-5 = named the way its practitioners name
   it (an EGaIn junction, Langmuir-Blodgett deposition,
   transient-photocurrent readout).
3. usage_parallel — does the shared method play the same ROLE? 5 = same
   role and same inference pattern (both read a transient's shape to
   infer microscopic dynamics; both program a persistent state and read
   it back). 4 = same role, inference differs in detail. 3 = same role
   in the workflow (e.g. both use self-assembly AS the fabrication step
   that builds the functional structure). 2 = loosely similar role.
   0-1 = the method does different jobs in the two works.
   Implementation differences already priced into same_method must not
   be double-counted here.

match: true only if same_method >= 3 AND usage_parallel >= 3 AND
specificity >= 2.

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
    strongest_parallel: str = ""

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
        schema_hint='{"strongest_parallel": "string", "same_method": 0, '
                    '"specificity": 0, "usage_parallel": 0, "match": true, '
                    '"why": "string"}',
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
        strongest_parallel=str(out.get("strongest_parallel", "")),
    )
