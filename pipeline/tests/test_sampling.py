from gps_engine.sampling import allocate, stratified_sample


def test_allocate_sqrt_proportional_with_floor():
    counts = {"DQI": 1600, "DCMP": 900, "GFB": 4}
    # sqrt weights 40:30:2 over 72 seats -> without floor GFB gets ~2..4;
    # floor 3 guarantees small units survive, capped at unit size.
    out = allocate(counts, total=72, floor=3)
    assert sum(out.values()) == 72
    assert out["GFB"] >= 3 or out["GFB"] == counts["GFB"]
    assert out["DQI"] > out["DCMP"] > out["GFB"]
    # sqrt flattens: DQI has ~1.8x DCMP's sqrt mass, never 1600/900 raw ratio
    assert out["DQI"] / out["DCMP"] < 1600 / 900


def test_allocate_never_exceeds_unit_size():
    out = allocate({"A": 2, "B": 1000}, total=50, floor=3)
    assert out["A"] == 2 and sum(out.values()) == 50


def test_stratified_sample_deterministic_and_covers_units():
    talks = {u: list(range(i * 1000, i * 1000 + 40))
             for i, u in enumerate(["A", "B", "C"])}
    s1 = stratified_sample(talks, total=30, seed=2026)
    s2 = stratified_sample(talks, total=30, seed=2026)
    assert s1 == s2 and len(s1) == 30
    for i in range(3):  # every unit represented
        assert any(i * 1000 <= t < i * 1000 + 40 for t in s1)


def test_stratified_sample_must_include_kept_within_total():
    talks = {"A": list(range(40)), "B": list(range(100, 140))}
    forced = {0, 1, 100}
    s = stratified_sample(talks, total=20, seed=7, must_include=forced)
    assert forced <= set(s) and len(s) == 20
