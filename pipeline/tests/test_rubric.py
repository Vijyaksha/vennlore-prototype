import pytest

from gps_engine.corpus import Talk
from gps_engine.llm import FakeLLM
from gps_engine.rubric import Judgment, judge_candidate

ME = Talk(id=1, title="Porphyrin nanorod photoconductivity",
          abstract="Self-assembled nanorods; trainable photocurrent.",
          topics=(), units=("DPOLY",), session_title="", start=None, end=None)
OTHER = Talk(id=2, title="Optoelectronic synapses",
             abstract="Photoinduced charge transfer; synaptic memory.",
             topics=(), units=("DMP",), session_title="", start=None, end=None)


def make_llm(match=True):
    return FakeLLM(responses=[{
        "same_method": 4, "specificity": 3, "usage_parallel": 4,
        "match": match, "why": "both exhibit optically trained conductance memory",
    }])


def test_judgment_fields_populated():
    j = judge_candidate(ME, OTHER, make_llm())
    assert isinstance(j, Judgment) and j.match and j.candidate_id == 2
    assert j.why.startswith("both exhibit")


def test_cross_domain_computed_from_units_not_llm():
    j = judge_candidate(ME, OTHER, make_llm())
    assert j.cross_domain is True          # DPOLY vs DMP: disjoint
    same_unit = Talk(**{**OTHER.__dict__, "units": ("DPOLY",)})
    j2 = judge_candidate(ME, same_unit, make_llm())
    assert j2.cross_domain is False


def test_prompt_contains_both_abstracts():
    llm = make_llm()
    judge_candidate(ME, OTHER, llm)
    assert "trainable photocurrent" in llm.prompts[0]
    assert "synaptic memory" in llm.prompts[0]


def test_non_boolean_match_raises():
    llm = FakeLLM(responses=[{"same_method": 4, "specificity": 3,
                              "usage_parallel": 4, "match": "false", "why": "w"}])
    with pytest.raises(ValueError):
        judge_candidate(ME, OTHER, llm)


def test_empty_units_is_not_cross_domain():
    no_units = Talk(**{**OTHER.__dict__, "units": ()})
    j = judge_candidate(ME, no_units, make_llm())
    assert j.cross_domain is False
