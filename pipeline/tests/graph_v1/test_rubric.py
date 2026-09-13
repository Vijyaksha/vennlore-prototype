import pytest

from gps_core.llm import FakeLLM
from gps_engines.graph_v1.rubric import Judgment, judge_candidate

from dataclasses import replace
from gps_data.talk import external_anchor


def mk_talk(id, title, abstract, units=()):
    return replace(external_anchor(title, abstract, list(units)), id=id)

ME = mk_talk(1, "Porphyrin nanorod photoconductivity",
             "Self-assembled nanorods; trainable photocurrent.", units=("DPOLY",))
OTHER = mk_talk(2, "Optoelectronic synapses",
                "Photoinduced charge transfer; synaptic memory.", units=("DMP",))


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
    same_unit = replace(OTHER, units=("DPOLY",))
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
    no_units = replace(OTHER, units=())
    j = judge_candidate(ME, no_units, make_llm())
    assert j.cross_domain is False


def test_judge_candidate_includes_claims_when_given():
    from gps_core.llm import FakeLLM
    llm = FakeLLM(responses=[{"same_method": 3, "specificity": 3,
                              "usage_parallel": 3, "match": True, "why": "w"}])
    judge_candidate(ME, OTHER, llm,
                    mine_claims="- Anchor claim [source: \"aq\"]",
                    cand_claims="- Cand claim [source: \"cq\"]")
    assert "Anchor claim" in llm.prompts[0]
    assert "Cand claim" in llm.prompts[0]
    assert "STATED CLAIMS" in llm.prompts[0]


def test_judge_candidate_without_claims_has_no_claims_block():
    from gps_core.llm import FakeLLM
    llm = FakeLLM(responses=[{"same_method": 1, "specificity": 1,
                              "usage_parallel": 1, "match": False, "why": "w"}])
    judge_candidate(ME, OTHER, llm)
    assert "STATED CLAIMS" not in llm.prompts[0]


def test_missing_match_defaults_to_false():
    """Some providers (observed: deepseek-chat) omit the match boolean.
    It is decorative — callers derive match from the calibrated score sum —
    so absence defaults to False rather than killing a run; the axis scores
    remain required."""
    llm = FakeLLM(responses=[{
        "same_method": 4, "specificity": 3, "usage_parallel": 4,
        "why": "same trained-photocurrent readout",
    }])
    j = judge_candidate(ME, OTHER, llm)
    assert j.match is False
    assert (j.same_method, j.specificity, j.usage_parallel) == (4, 3, 4)
