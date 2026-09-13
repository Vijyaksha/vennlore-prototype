"""Rules every engine inherits: the default cross-domain test, the
own-work exclusion, and deterministic ranking."""
from dataclasses import replace

from gps_core.records import Recommendation
from gps_data.talk import Talk


def default_cross_domain(anchor: Talk, cand: Talk) -> bool:
    """Unknown units never count as cross-domain: a surprise pick needs
    affirmative evidence that the two talks live in different divisions."""
    return bool(anchor.units) and bool(cand.units) and not (set(anchor.units) & set(cand.units))


def exclude_authored(rows: list[Recommendation], authored_ids: set[int]) -> list[Recommendation]:
    return [r for r in rows if r.candidate_id not in authored_ids]


def ranked(rows: list[Recommendation]) -> list[Recommendation]:
    """rank = 1..n within each for_talk_id, by score desc then candidate_id asc."""
    out: list[Recommendation] = []
    by_anchor: dict[int, list[Recommendation]] = {}
    for r in rows:
        by_anchor.setdefault(r.for_talk_id, []).append(r)
    for anchor_id in sorted(by_anchor):
        rs = sorted(by_anchor[anchor_id], key=lambda r: (-r.score, r.candidate_id))
        out.extend(replace(r, rank=i + 1) for i, r in enumerate(rs))
    return out
