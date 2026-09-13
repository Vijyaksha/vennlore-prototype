from gps_engine.claims import claims_digest, extract_claims
from gps_engine.corpus import Talk
from gps_core.llm import FakeLLM


def _talk(abstract):
    return Talk(id=1, title="T", abstract=abstract, topics=(), units=(),
                session_title="", start=None, end=None)


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
