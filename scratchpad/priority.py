"""Order a census section so the next wave works the likely-large rows first.

Unresearched rows come first, highest likely-size score at the top; researched rows
follow, grouped VERIFIED, BORDERLINE, OUT. The sort is stable, so ties keep their
original order. The score is a general-knowledge guess for SEQUENCING only — it is
never evidence and never decides a tier.
"""
UNRESEARCHED = "NOT YET CENSUSED"
_DONE_ORDER = {"VERIFIED": 0, "BORDERLINE": 1, "OUT": 2}


def order(rows):
    def key(r):
        if r["tier"] == UNRESEARCHED:
            return (0, -(r.get("score") or 0))
        return (1, _DONE_ORDER.get(r["tier"], 3))
    return sorted(rows, key=key)
