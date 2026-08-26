"""LLM boundary. Everything above this module is deterministic and unit-tested
with FakeLLM; AnthropicLLM is exercised only by gated scripts."""
import json
import os
from typing import Protocol


class LLMClient(Protocol):
    def complete_json(self, prompt: str, schema_hint: str) -> dict: ...


class FakeLLM:
    def __init__(self, responses: list[dict]):
        self._responses = list(responses)
        self.prompts: list[str] = []

    def complete_json(self, prompt: str, schema_hint: str) -> dict:
        self.prompts.append(prompt)
        if not self._responses:
            raise IndexError("FakeLLM has no queued responses")
        return self._responses.pop(0)


class AnthropicLLM:
    def __init__(self, model: str, max_tokens: int = 1024):
        import anthropic
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._model = model
        self._max_tokens = max_tokens

    def complete_json(self, prompt: str, schema_hint: str) -> dict:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system="Respond with a single JSON object and nothing else. "
                   f"Expected shape: {schema_hint}",
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        if text.startswith("```"):
            text = text.strip("`").removeprefix("json").strip()
        return json.loads(text)
