"""One small wrapper so the rest of the code doesn't care which LLM is used.
All backends speak the same OpenAI-compatible chat API.

Backends, checked in this order:
  1. Free cloud API  - set LLM_API_URL, LLM_API_KEY and LLM_MODEL
                       e.g. Groq:       LLM_API_URL=https://api.groq.com/openai/v1
                            OpenRouter: LLM_API_URL=https://openrouter.ai/api/v1
  2. Local LLM       - LM Studio (http://localhost:1234/v1, the default) or
                       Ollama (set LOCAL_LLM_URL=http://localhost:11434/v1).
                       Free, no key, runs on your own GPU. The first loaded model is used
                       unless LOCAL_LLM_MODEL is set.
  3. None            - the app still works offline with template text.
"""

import json
import os
import time
import urllib.request

LOCAL_URL = os.environ.get("LOCAL_LLM_URL", "http://localhost:1234/v1").rstrip("/")


def _get(url: str, headers: dict | None = None, timeout: float = 2) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


_found: dict | None = None
_last_check = 0.0
RECHECK_SECONDS = 10


def backend() -> dict:
    """Return dict(kind, url, model, key) for the first working backend, or kind=None.

    A working backend is remembered; if none is found, we look again every few seconds,
    so starting LM Studio after the app is already running still works."""
    global _found, _last_check
    if _found is not None:
        return _found
    if time.time() - _last_check < RECHECK_SECONDS:
        return {"kind": None, "url": None, "key": None, "model": None}
    _last_check = time.time()
    _found = _detect()
    return _found or {"kind": None, "url": None, "key": None, "model": None}


def _detect() -> dict | None:
    """Look for a cloud API key first, then a local LM Studio / Ollama server."""
    url, key, model = (
        os.environ.get("LLM_API_URL"),
        os.environ.get("LLM_API_KEY"),
        os.environ.get("LLM_MODEL"),
    )
    if url and key and model:
        return {"kind": "cloud", "url": url.rstrip("/"), "key": key, "model": model}
    try:
        models = _get(LOCAL_URL + "/models").get("data", [])
    except Exception:
        return None  # no local server running
    if not models:
        return None
    model = os.environ.get("LOCAL_LLM_MODEL") or _loaded_lmstudio_model() or models[0]["id"]
    return {"kind": "local", "url": LOCAL_URL, "key": None, "model": model}


def _loaded_lmstudio_model() -> str | None:
    """LM Studio's /v1/models can list every downloaded model. Its native API says which one
    is actually loaded, so we use that and avoid making LM Studio load a second model."""
    base = LOCAL_URL[: -len("/v1")] if LOCAL_URL.endswith("/v1") else LOCAL_URL
    try:
        data = _get(base + "/api/v0/models").get("data", [])
    except Exception:
        return None  # not LM Studio (e.g. Ollama), or an older version
    loaded = [m["id"] for m in data if m.get("state") == "loaded" and m.get("type") in (None, "llm", "vlm")]
    return loaded[0] if loaded else None


def available() -> bool:
    return backend()["kind"] is not None


def describe() -> str:
    b = backend()
    if b["kind"] == "cloud":
        return f"cloud API ({b['model']})"
    if b["kind"] == "local":
        return f"local LLM ({b['model']})"
    return "none (offline templates)"


def complete(prompt: str, max_tokens: int = 900, temperature: float = 0.2) -> str | None:
    """Return the model's text reply, or None if no LLM is available or the call fails."""
    b = backend()
    if not b["kind"]:
        return None
    if b["kind"] == "local":
        # local reasoning models (e.g. Qwen3) "think" before answering; leave room for it
        max_tokens = max(max_tokens, 6000)
    headers = {"Content-Type": "application/json"}
    if b["key"]:
        headers["Authorization"] = "Bearer " + b["key"]
    body = json.dumps(
        {
            "model": b["model"],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")
    try:
        req = urllib.request.Request(b["url"] + "/chat/completions", data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=300) as r:
            text = json.loads(r.read().decode("utf-8"))["choices"][0]["message"]["content"] or ""
        return text.split("</think>")[-1].strip()  # drop reasoning-model "thinking" if present
    except Exception as e:
        print(f"[llm] call failed: {type(e).__name__}: {e}")
        return None


def complete_json(prompt: str, max_tokens: int = 900) -> dict | list | None:
    """Ask for JSON and parse the first JSON object or array in the reply. None on failure."""
    text = complete(prompt + "\n\nReply with valid JSON only, no other text.", max_tokens)
    if not text:
        return None
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not starts:
        return None
    start, end = min(starts), max(text.rfind("}"), text.rfind("]"))
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
