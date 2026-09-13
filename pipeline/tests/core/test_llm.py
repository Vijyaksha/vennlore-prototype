import pytest
from gps_core.llm import AnthropicLLM, FakeLLM


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
    import gps_core.llm as llm_mod
    monkeypatch.setattr(llm_mod.time, "sleep", lambda s: None)

    with pytest.raises(RuntimeError, match="no usable JSON response after 3 attempts"):
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
    from gps_core.llm import LLMRefusal
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


def test_anthropic_llm_tolerates_trailing_prose(monkeypatch):
    from anthropic.types import TextBlock
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    llm = AnthropicLLM(model="claude-x")

    class StubMessage:
        stop_reason = "end_turn"
        content = [TextBlock(type="text",
                             text='Here you go:\n{"ok": 1}\nHope that helps!')]

    llm._client.messages.create = lambda **kwargs: StubMessage()
    assert llm.complete_json("p", schema_hint="x") == {"ok": 1}


def test_anthropic_llm_retries_malformed_json(monkeypatch):
    from anthropic.types import TextBlock
    import gps_core.llm as llm_mod
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    monkeypatch.setattr(llm_mod.time, "sleep", lambda s: None)
    llm = AnthropicLLM(model="claude-x")

    replies = ['{"broken": ,}', '{"ok": 2}']

    class StubMessage:
        def __init__(self, text):
            self.stop_reason = "end_turn"
            self.content = [TextBlock(type="text", text=text)]

    llm._client.messages.create = lambda **kwargs: StubMessage(replies.pop(0))
    assert llm.complete_json("p", schema_hint="x") == {"ok": 2}


# ---------- DeepSeekLLM (OpenAI-compatible endpoint) ----------

def _ds(monkeypatch):
    from gps_core.llm import DeepSeekLLM
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")
    return DeepSeekLLM(model="deepseek-chat")


class _Choice:
    def __init__(self, content, finish_reason="stop"):
        self.finish_reason = finish_reason
        self.message = type("M", (), {"content": content})()


class _Resp:
    def __init__(self, content, finish_reason="stop"):
        self.choices = [_Choice(content, finish_reason)]


def test_deepseek_llm_parses_json(monkeypatch):
    llm = _ds(monkeypatch)
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return _Resp('{"ok": true}')

    llm._client.chat.completions.create = create
    assert llm.complete_json("p", schema_hint="x") == {"ok": True}
    # JSON mode must be requested and the schema hint must reach the model.
    assert captured["response_format"] == {"type": "json_object"}
    assert captured["model"] == "deepseek-chat"
    assert any("x" in m["content"] for m in captured["messages"]
               if m["role"] == "system")


def test_deepseek_llm_tolerates_fences_and_trailing_prose(monkeypatch):
    llm = _ds(monkeypatch)
    llm._client.chat.completions.create = (
        lambda **kwargs: _Resp('```json\n{"ok": 1}\n```\nHope that helps!'))
    assert llm.complete_json("p", schema_hint="x") == {"ok": 1}


def test_deepseek_llm_retries_malformed_then_succeeds(monkeypatch):
    import gps_core.llm as llm_mod
    monkeypatch.setattr(llm_mod.time, "sleep", lambda s: None)
    llm = _ds(monkeypatch)
    replies = ['{"broken": ,}', '{"ok": 2}']
    llm._client.chat.completions.create = (
        lambda **kwargs: _Resp(replies.pop(0)))
    assert llm.complete_json("p", schema_hint="x") == {"ok": 2}


def test_deepseek_llm_empty_content_exhausts_retries(monkeypatch):
    import gps_core.llm as llm_mod
    monkeypatch.setattr(llm_mod.time, "sleep", lambda s: None)
    llm = _ds(monkeypatch)
    llm._client.chat.completions.create = lambda **kwargs: _Resp(None)
    from gps_core.llm import LLMUnusable
    with pytest.raises(LLMUnusable, match="no usable JSON response"):
        llm.complete_json("p", schema_hint="x")


def test_deepseek_llm_content_filter_raises_llm_refusal(monkeypatch):
    """finish_reason 'content_filter' is the OpenAI-compatible analogue of
    Anthropic's 'refusal' stop reason — deterministic, no retries."""
    from gps_core.llm import LLMRefusal
    llm = _ds(monkeypatch)
    calls = []

    def create(**kwargs):
        calls.append(1)
        return _Resp("", finish_reason="content_filter")

    llm._client.chat.completions.create = create
    with pytest.raises(LLMRefusal):
        llm.complete_json("p", schema_hint="x")
    assert len(calls) == 1
