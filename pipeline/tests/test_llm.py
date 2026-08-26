import json
import pytest
from gps_engine.llm import FakeLLM


def test_fake_llm_returns_queued_json():
    llm = FakeLLM(responses=[{"methods": ["DMRG"]}])
    assert llm.complete_json("extract", schema_hint="methods") == {"methods": ["DMRG"]}


def test_fake_llm_records_prompts():
    llm = FakeLLM(responses=[{"ok": True}])
    llm.complete_json("hello world", schema_hint="x")
    assert "hello world" in llm.prompts[0]


def test_fake_llm_exhausted_raises():
    llm = FakeLLM(responses=[])
    with pytest.raises(IndexError):
        llm.complete_json("p", schema_hint="x")
