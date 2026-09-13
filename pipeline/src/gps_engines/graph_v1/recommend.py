"""Pick assembly: turns judgments into the product's output contract.
Thresholds gate inclusion, not top-k — an empty result is an honest answer."""
from dataclasses import dataclass

from gps_engines.graph_v1.rubric import Judgment


@dataclass(frozen=True)
class Picks:
    core: list[Judgment]
    unexpected: list[Judgment]


def assemble(judgments: list[Judgment], min_score: int = 5,
             max_core: int = 2, max_unexpected: int = 3) -> Picks:
    # min_score=5: calibrated on the Stage-0 10+47 ground truth (positives
    # score 5-11 total, negatives topped out at 4).
    ok = sorted((j for j in judgments if j.match and j.score >= min_score),
                key=lambda j: (-j.score, j.candidate_id))
    return Picks(
        core=[j for j in ok if not j.cross_domain][:max_core],
        unexpected=[j for j in ok if j.cross_domain][:max_unexpected],
    )
