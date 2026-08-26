from gps_engine.similarity import propose_pairs


def fake_embed(names):  # canned 2-D embeddings keyed by name
    table = {
        "dmrg": [1.0, 0.0],
        "density-matrix renormalization group": [0.98, 0.05],
        "neutron scattering": [0.0, 1.0],
    }
    return [table[n] for n in names]


def test_proposes_only_near_pairs():
    names = ["dmrg", "density-matrix renormalization group", "neutron scattering"]
    pairs = propose_pairs(names, embed=fake_embed, threshold=0.9)
    assert pairs == [("density-matrix renormalization group", "dmrg")]


def test_no_pairs_when_all_far():
    pairs = propose_pairs(["dmrg", "neutron scattering"], embed=fake_embed, threshold=0.9)
    assert pairs == []
