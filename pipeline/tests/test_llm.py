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
        stop_reason = "end_turn"
        content = [object()]  # not a TextBlock

    llm._client.messages.create = lambda **kwargs: StubMessage()
    import gps_engine.llm as llm_mod
    monkeypatch.setattr(llm_mod.time, "sleep", lambda s: None)

    with pytest.raises(RuntimeError, match="no TextBlock in response after 3 attempts"):
        llm.complete_json("p", schema_hint="x")


def test_anthropic_llm_skips_thinking_block(monkeypatch):
    """Models with extended thinking prepend a ThinkingBlock; the wrapper
    must find the TextBlock wherever it sits in the content list."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    from anthropic.types import TextBlock
    llm = AnthropicLLM(model="claude-x")

    class StubMessage:
        stop_reason = "end_turn"
        content = [object(), TextBlock(type="text", text='{"ok": true}')]

    llm._client.messages.create = lambda **kwargs: StubMessage()

    assert llm.complete_json("p", schema_hint="x") == {"ok": True}


def test_anthropic_llm_raises_llm_refusal(monkeypatch):
    """stop_reason 'refusal' is deterministic — must raise LLMRefusal
    immediately (no retries) so callers can apply a fallback policy."""
    from gps_engine.llm import LLMRefusal
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    llm = AnthropicLLM(model="claude-x")

    calls = []

    class StubMessage:
        stop_reason = "refusal"
        content = []

    def create(**kwargs):
        calls.append(1)
        return StubMessage()

    llm._client.messages.create = create

    with pytest.raises(LLMRefusal):
        llm.complete_json("p", schema_hint="x")
    assert len(calls) == 1
