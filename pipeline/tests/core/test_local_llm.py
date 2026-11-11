"""LocalLLM: a free, keyless client for any OpenAI-compatible local server
(LM Studio by default, Ollama via base_url). No network in these tests: the
OpenAI SDK client is replaced by a stub."""
import pytest

from gps_core.llm import LLMUnusable, LocalLLM


class StubClient:
    """Mimics the slice of openai.OpenAI that LocalLLM uses."""

    def __init__(self, replies: list[str], models: list[str] = ("qwen2.5-7b-instruct",)):
        self.replies = list(replies)
        self.calls: list[dict] = []
        self.chat = self
        self.completions = self
        self.models = self
        self._model_ids = list(models)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        text = self.replies.pop(0)

        class Msg:
            content = text

        class Choice:
            message = Msg()
            finish_reason = "stop"

        class Resp:
            choices = [Choice()]

        return Resp()

    def list(self):
        ids = self._model_ids

        class M:
            def __init__(self, i):
                self.id = i

        class Page:
            data = [M(i) for i in ids]

        return Page()


def make(replies, **kw):
    stub = StubClient(replies, **{k: v for k, v in kw.items() if k == "models"})
    llm = LocalLLM(model=kw.get("model"), client=stub, sleep=lambda s: None)
    return llm, stub


def test_has_the_llm_client_seam():
    llm, _ = make(['{"a": 1}'], model="m")
    assert callable(llm.complete_json)


def test_returns_parsed_json_and_sends_schema_hint():
    llm, stub = make(['{"methods": ["DMRG"]}'], model="m")
    assert llm.complete_json("extract", schema_hint='{"methods": [str]}') == {"methods": ["DMRG"]}
    sent = stub.calls[0]
    assert sent["model"] == "m"
    assert '{"methods": [str]}' in sent["messages"][0]["content"]
    assert sent["messages"][1] == {"role": "user", "content": "extract"}


def test_strips_reasoning_model_think_block():
    llm, _ = make(['<think>{"wrong": 1} hmm</think>\n{"ok": true}'], model="m")
    assert llm.complete_json("p", schema_hint="x") == {"ok": True}


def test_tolerates_fences_and_prose_from_small_models():
    llm, _ = make(['Sure! Here you go:\n```json\n{"ok": 1}\n```\nHope that helps'], model="m")
    assert llm.complete_json("p", schema_hint="x") == {"ok": 1}


def test_retries_malformed_output_then_succeeds():
    llm, stub = make(["not json at all", '{"ok": 2}'], model="m")
    assert llm.complete_json("p", schema_hint="x") == {"ok": 2}
    assert len(stub.calls) == 2


def test_gives_up_with_llm_unusable_after_three_attempts():
    llm, stub = make(["nope", "", "<think>ran out of tokens"], model="m")
    with pytest.raises(LLMUnusable):
        llm.complete_json("p", schema_hint="x")
    assert len(stub.calls) == 3


def test_model_none_uses_the_server_loaded_model():
    llm, stub = make(['{"ok": 1}'], models=["llama-3.2-1b-instruct"])
    llm.complete_json("p", schema_hint="x")
    assert stub.calls[0]["model"] == "llama-3.2-1b-instruct"
    assert llm.model == "llama-3.2-1b-instruct"


def test_default_base_url_is_lm_studio_and_env_overrides(monkeypatch):
    monkeypatch.delenv("LOCAL_LLM_URL", raising=False)
    assert LocalLLM.default_base_url() == "http://localhost:1234/v1"
    monkeypatch.setenv("LOCAL_LLM_URL", "http://localhost:11434/v1")
    assert LocalLLM.default_base_url() == "http://localhost:11434/v1"


def test_model_named_local_means_use_the_loaded_model():
    """Engines record models={'extract': 'local'}; the client resolves it."""
    stub = StubClient(['{"ok": 1}'], models=["phi-3-mini"])
    llm = LocalLLM(model="local", client=stub, sleep=lambda s: None)
    llm.complete_json("p", schema_hint="x")
    assert stub.calls[0]["model"] == "phi-3-mini"
