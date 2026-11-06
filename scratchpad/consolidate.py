"""Pick the best result per conference across the seven research runs.

The method decides, not recency and not which model produced it:

    COUNTED (rungs 3-6)  >  STATED (rungs 1, 2, 7, 8)  >  INFERRED (rung 9)

because a counted artefact is re-derivable and a stated total is not — and stated
totals routinely include invited speakers, which the census excludes. Within the
same class the later edition wins. A figure with no exact-page URL is never chosen
(rule 2), and a conference with no figure is never tiered `OUT` (rule 1).
"""

COUNTING_RUNGS = {3, 4, 5, 6}
INFERRED_RUNG = 9

VERIFIED_BAR = 1500
RETENTION_FLOOR = 900
#: within this of the floor still counts as clearing it — for counted AND inferred figures
#: (Rupert, 2026-09-12: "one floor for both kinds of figure")
NEAR_BAR = 100


def _class(rec):
    """3 = counted, 2 = stated, 1 = inferred, 0 = no usable figure."""
    if rec.get("abstracts_numeric") is None or not rec.get("source_url"):
        return 0
    rung = rec.get("rung")
    if rung in COUNTING_RUNGS:
        return 3
    if rung == INFERRED_RUNG:
        return 1
    return 2


def _richness(rec):
    """How useful an unresolved record is to the next session."""
    score = len(rec.get("method") or "")
    if rec.get("verdict") == "NEEDS_RUNG_5":
        score += 1000            # a named, reachable artefact beats a bare UNKNOWN
    if rec.get("attendance_numeric") is not None:
        score += 500
    return score


def _key(rec):
    return (_class(rec), rec.get("year") or 0, _richness(rec))


def best(records):
    """The winning record, annotated with any figures other runs disagreed on."""
    ranked = sorted(records, key=_key, reverse=True)
    winner = dict(ranked[0])
    win_fig = winner.get("abstracts_numeric")
    winner["disagreements"] = [
        {"run": r.get("run"), "abstracts_numeric": r.get("abstracts_numeric"),
         "rung": r.get("rung")}
        for r in ranked[1:]
        if r.get("abstracts_numeric") is not None
        and r.get("abstracts_numeric") != win_fig
    ]
    return winner


def tier(abstracts, rung=None):
    """Tier from the counted bar and the ~900 retention floor (Rupert, 2026-09-12)."""
    if abstracts is None:
        return "BORDERLINE"                       # rule 1: never OUT on absence
    keep = abstracts >= RETENTION_FLOOR - NEAR_BAR
    if rung == INFERRED_RUNG:
        return "BORDERLINE" if keep else "OUT"    # nothing counted: never VERIFIED
    if abstracts >= VERIFIED_BAR:
        return "VERIFIED"
    return "BORDERLINE" if keep else "OUT"
