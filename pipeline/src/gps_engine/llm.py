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


def _parse_json_text(text: str) -> dict | None:
    """First complete JSON object in `text`, tolerating markdown fences and
    trailing prose; None when the text holds no parseable object."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    start = text.find("{")
    try:
        obj, _ = json.JSONDecoder().raw_decode(
            text[start:] if start >= 0 else text)
        return obj
    except json.JSONDecodeError:
        return None


SYSTEM_PROMPT = ("Respond with a single JSON object and nothing else. "
                 "Expected shape: {schema_hint}")


class DeepSeekLLM:
    """OpenAI-compatible DeepSeek endpoint behind the same LLMClient seam.
    JSON mode is requested explicitly; the repair/retry harness stays because
    json_object mode still occasionally yields truncated or fenced output."""

    def __init__(self, model: str, max_tokens: int = 4096):
        import openai
        self._client = openai.OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
        )
        self._model = model
        self._max_tokens = max_tokens

    def complete_json(self, prompt: str, schema_hint: str) -> dict:
        last_kinds: list[str] = []
        for attempt in range(3):
            if attempt:
                time.sleep(2 * attempt)
            resp = self._client.chat.completions.create(
                model=self._model,
                max_tokens=self._max_tokens,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system",
                     "content": SYSTEM_PROMPT.format(schema_hint=schema_hint)},
                    {"role": "user", "content": prompt},
                ],
            )
            choice = resp.choices[0]
            if choice.finish_reason == "content_filter":
                raise LLMRefusal(f"model refused: {prompt[:120]!r}")
            text = choice.message.content or ""
            if text.strip():
                obj = _parse_json_text(text)
                if obj is not None:
                    return obj
                last_kinds = [f"malformed-json({text[:80]!r})"]
            else:
                last_kinds = ["empty-content"]
        raise RuntimeError(
            f"no usable JSON response after 3 attempts, got {last_kinds}")


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
                system=SYSTEM_PROMPT.format(schema_hint=schema_hint),
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
                # Malformed JSON consumes a retry attempt rather than
                # killing the run.
                obj = _parse_json_text(block.text)
                if obj is not None:
                    return obj
                last_kinds = [f"malformed-json({block.text[:80]!r})"]
                continue
            last_kinds = [type(b).__name__ for b in msg.content]
        raise RuntimeError(
            f"no usable JSON response after 3 attempts, got {last_kinds}")
