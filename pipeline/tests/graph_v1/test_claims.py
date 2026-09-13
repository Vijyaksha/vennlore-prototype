from gps_engines.graph_v1.claims import claims_digest, extract_claims
from gps_core.llm import FakeLLM

from dataclasses import replace
from gps_data.talk import external_anchor


def mk_talk(id, title, abstract, units=()):
    return replace(external_anchor(title, abstract, list(units)), id=id)


def _talk(abstract):
    return mk_talk(1, "T", abstract)


def test_grounded_claim_verified_against_abstract():
    talk = _talk("We measure a 100-fold conductance increase upon binding.")
    llm = FakeLLM(responses=[{"claims": [
        {"about": "conductance", "claim": "Conductance rises 100x on binding.",
         "quote": "100-fold conductance increase upon binding"},
        {"about": "resolution", "claim": "Achieves 1 fs resolution.",
         "quote": "we achieve femtosecond resolution"},  # not in abstract
    ]}])
    claims = extract_claims(talk, llm)
    assert claims[0]["grounded"] is True
    assert claims[1]["grounded"] is False


def test_digest_renders_only_grounded_claims_with_quotes():
    claims = [
        {"about": "a", "claim": "Real claim.", "quote": "real quote", "grounded": True},
        {"about": "b", "claim": "Fabricated.", "quote": "nope", "grounded": False},
    ]
    d = claims_digest(claims)
    assert "Real claim." in d and 'source: "real quote"' in d
    assert "Fabricated" not in d


def test_empty_claims_response():
    llm = FakeLLM(responses=[{"claims": []}])
    assert extract_claims(_talk("A"), llm) == []
