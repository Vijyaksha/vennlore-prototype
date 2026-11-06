"""Grade one census run against another.

Agreement rate on its own is a misleading score: on a hard slice most rows correctly
yield no figure, so two runs agree without either being useful. This module reports
agreement AND the violations that actually corrupt a census — an unsourced figure, a
figure credited to no rung, an `OUT` with no evidence behind it, and the documented
common failure of naming a countable artefact and then returning UNKNOWN.
"""
import re

#: phrases that mean "I found the thing that can be counted"
_ARTEFACT = re.compile(
    r"abstract book|book of abstracts|programme pdf|program pdf|proceedings|"
    r"supplement|abstract archive|\.pdf|сборник|摘要集|要旨集|index",
    re.I,
)
_NEXT_STEP = re.compile(r"\bNEXT\b|next step|should be counted|needs counting", re.I)
#: a wall is a legitimate reason not to have counted — that is what rung 5 is for
_BLOCKED = re.compile(r"403|cloudflare|just a moment|paywall|bot wall|captcha|"
                      r"JS[- ]render|SPA|HTTP 202|requires a browser|playwright|"
                      r"hijack|404|rate.?limit", re.I)

RESOLVED_VERDICTS = {"VERIFIED", "BORDERLINE", "OUT"}


def _by_row(run):
    return {r["row"]: r for r in run}


def _resolved(r):
    return r.get("abstracts_numeric") is not None


def compare(control, candidate):
    """Row-by-row agreement between a control run and a candidate run."""
    cand = _by_row(candidate)
    rows = []
    for c in control:
        o = cand.get(c["row"])
        if o is None:
            continue
        cv, ov = c.get("abstracts_numeric"), o.get("abstracts_numeric")
        if cv is not None and ov is not None:
            agreement = "SAME_FIGURE" if cv == ov else "DIFFERENT_FIGURE"
        elif cv is None and ov is not None:
            agreement = "CANDIDATE_ONLY"
        elif cv is not None and ov is None:
            agreement = "CONTROL_ONLY"
        else:
            agreement = "BOTH_UNRESOLVED"
        rows.append({"row": c["row"], "conference": c.get("conference"),
                     "agreement": agreement, "control": cv, "candidate": ov,
                     "control_rung": c.get("rung"), "candidate_rung": o.get("rung")})
    return {
        "rows": rows,
        "missing": [c["row"] for c in control if c["row"] not in cand],
        "summary": {
            "control_resolved": sum(1 for c in control if _resolved(c)),
            "candidate_resolved": sum(1 for c in candidate if _resolved(c)),
            "compared": len(rows),
        },
    }


def violations(run):
    """Method breaches, in the order they damage the census."""
    out = []

    def flag(r, kind, detail):
        out.append({"row": r.get("row"), "conference": r.get("conference"),
                    "kind": kind, "detail": detail})

    for r in run:
        method = r.get("method") or ""
        if _resolved(r):
            if not r.get("source_url"):
                flag(r, "FIGURE_WITHOUT_SOURCE",
                     "a figure was written with no exact-page URL (rule 2)")
            if r.get("rung") is None:
                flag(r, "FIGURE_WITHOUT_RUNG",
                     "a figure was written crediting no rung (rule 4)")
        else:
            # An attendance ceiling IS positive evidence of size: a 127-person meeting
            # cannot reach the floor at any ratio. It needs its own sourced URL though.
            ceiling = (r.get("attendance_numeric") is not None
                       and bool(r.get("attendance_source_url")))
            if r.get("verdict") == "OUT" and not ceiling:
                flag(r, "UNSOURCED_OUT",
                     "OUT with neither a figure nor a sourced attendance ceiling — "
                     "absence of evidence recorded as evidence (rule 1)")
            if (_ARTEFACT.search(method) and _NEXT_STEP.search(method)
                    and r.get("verdict") != "NEEDS_RUNG_5"
                    and not _BLOCKED.search(method)):
                flag(r, "ARTEFACT_NOT_COUNTED",
                     "a countable artefact was named, was not blocked, and was not counted")
    return out
