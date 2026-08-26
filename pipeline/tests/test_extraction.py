from gps_engine.corpus import Talk
from gps_engine.extraction import extract_methods
from gps_engine.llm import FakeLLM

TALK = Talk(id=1, title="Kondo physics probed by STM",
            abstract="We use scanning tunneling microscopy and DMRG simulations.",
            topics=(), units=("DCMP",), session_title="", start=None, end=None)

def test_extracts_method_list_from_llm():
    llm = FakeLLM(responses=[{"methods": ["scanning tunneling microscopy", "DMRG"]}])
    assert extract_methods(TALK, llm) == ["scanning tunneling microscopy", "DMRG"]

def test_prompt_contains_title_and_abstract():
    llm = FakeLLM(responses=[{"methods": []}])
    extract_methods(TALK, llm)
    assert "Kondo physics" in llm.prompts[0] and "DMRG simulations" in llm.prompts[0]

def test_dedupes_and_drops_blank():
    llm = FakeLLM(responses=[{"methods": ["DMRG", "dmrg ", ""]}])
    assert extract_methods(TALK, llm) == ["DMRG"]
