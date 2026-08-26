import pytest
from gps_engine.llm import AnthropicLLM, FakeLLM


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


def test_anthropic_llm_rejects_non_text_block(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    llm = AnthropicLLM(model="claude-x")

    class StubMessage:
        content = [object()]  # not a TextBlock

    llm._client.messages.create = lambda **kwargs: StubMessage()

    with pytest.raises(RuntimeError, match="expected TextBlock"):
        llm.complete_json("p", schema_hint="x")
