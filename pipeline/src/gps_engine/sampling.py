"""Stratified corpus sampling: cover every division (sponsor unit) without
letting the giant ones (DQI, DCMP) drown the small ones. Allocation is
sqrt-proportional with a per-unit floor; selection within a unit is seeded
uniform — fully deterministic for a given (corpus, total, seed)."""
import math
import random


def allocate(counts: dict[str, int], total: int, floor: int = 3) -> dict[str, int]:
    """Seats per unit: sqrt-proportional to unit size, at least `floor`
    (capped at unit size), summing exactly to `total` via largest-remainder."""
    units = {u: n for u, n in counts.items() if n > 0}
    base = {u: min(floor, n) for u, n in units.items()}
    spent = sum(base.values())
    if spent >= total:
        # floors alone exhaust the budget: trim smallest-weight units last
        out = dict(base)
        for u in sorted(units, key=lambda u: math.sqrt(units[u])):
            while sum(out.values()) > total and out[u] > 0:
                out[u] -= 1
        return {u: c for u, c in out.items() if c > 0}
    weights = {u: math.sqrt(n) for u, n in units.items()}
    wsum = sum(weights.values())
    remaining = total - spent
    quota = {u: remaining * w / wsum for u, w in weights.items()}
    out = {u: base[u] + int(quota[u]) for u in units}
    # cap at unit size, then hand leftover seats out by largest remainder
    out = {u: min(c, units[u]) for u, c in out.items()}
    frac = sorted(units, key=lambda u: quota[u] - int(quota[u]), reverse=True)
    i = 0
    while sum(out.values()) < total and i < 10 * len(units):
        u = frac[i % len(frac)]
        if out[u] < units[u]:
            out[u] += 1
        i += 1
    return out


def stratified_sample(talks_by_unit: dict[str, list[int]], total: int,
                      seed: int, must_include: set[int] | None = None
                      ) -> list[int]:
    """Deterministic stratified sample of talk ids. `must_include` ids are
    forced in (they occupy their unit's seats first)."""
    must = must_include or set()
    counts = {u: len(ids) for u, ids in talks_by_unit.items()}
    alloc = allocate(counts, total)
    rng = random.Random(seed)
    chosen: list[int] = []
    for u in sorted(talks_by_unit):
        ids = sorted(talks_by_unit[u])
        seats = alloc.get(u, 0)
        forced = [t for t in ids if t in must]
        rest = [t for t in ids if t not in must]
        take = forced[:]
        extra = seats - len(forced)
        if extra > 0:
            take += rng.sample(rest, min(extra, len(rest)))
        chosen.extend(take)
    # forced talks may have overflowed some units past their seats; drop
    # unforced picks (seeded order) until we're back at total
    if len(chosen) > total:
        unforced = [t for t in chosen if t not in must]
        rng.shuffle(unforced)
        drop = set(unforced[:len(chosen) - total])
        chosen = [t for t in chosen if t not in drop]
    return sorted(chosen)
