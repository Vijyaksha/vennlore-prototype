"""LLM boundary. Everything above this module is deterministic and unit-tested
with FakeLLM; AnthropicLLM is exercised only by gated scripts."""
import json
import os
import time
from typing import Protocol


class LLMClient(Protocol):
    def complete_json(self, prompt: str, schema_hint: str) -> dict: ...


class LLMRefusal(RuntimeError):
    """The API's safety layer declined the request (stop_reason 'refusal').
    Deterministic for a given prompt — retrying is pointless; callers decide
    the fallback policy."""


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
    def __init__(self, model: str, max_tokens: int = 4096):
        import anthropic
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._model = model
        self._max_tokens = max_tokens

    def complete_json(self, prompt: str, schema_hint: str) -> dict:
        from anthropic.types import TextBlock

        # The API intermittently returns an empty content list (observed
        # live: stop_reason end_turn, content []); retry before giving up.
        last_kinds: list[str] = []
        for attempt in range(3):
            if attempt:
                time.sleep(2 * attempt)
            msg = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system="Respond with a single JSON object and nothing else. "
                       f"Expected shape: {schema_hint}",
                messages=[{"role": "user", "content": prompt}],
                # Models with adaptive thinking (claude-sonnet-5) may burn
                # the whole token budget on a ThinkingBlock and return no
                # text for these small JSON calls; thinking buys nothing
                # here.
                thinking={"type": "disabled"},
            )
            if msg.stop_reason == "refusal":
                raise LLMRefusal(f"model refused: {prompt[:120]!r}")
            # Take the first TextBlock wherever it sits (thinking-capable
            # models may prepend other block types).
            block = next(
                (b for b in msg.content if isinstance(b, TextBlock)), None)
            if block is not None:
                text = block.text.strip()
                if text.startswith("```"):
                    text = text.strip("`").removeprefix("json").strip()
                # Some models append prose after the object; take the first
                # complete JSON value and ignore trailing data. Malformed
                # JSON consumes a retry attempt rather than killing the run.
                start = text.find("{")
                try:
                    obj, _ = json.JSONDecoder().raw_decode(
                        text[start:] if start >= 0 else text)
                    return obj
                except json.JSONDecodeError:
                    last_kinds = [f"malformed-json({text[:80]!r})"]
                    continue
            last_kinds = [type(b).__name__ for b in msg.content]
        raise RuntimeError(
            f"no usable JSON response after 3 attempts, got {last_kinds}")
