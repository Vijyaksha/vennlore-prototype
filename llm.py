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
import re
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
    except Exception as e:
        print(f"[llm] call failed: {type(e).__name__}: {e}")
        return None
    return _clean(text)


def _clean(text: str) -> str | None:
    """Remove reasoning-model 'thinking' and markdown decoration. None if nothing usable is left."""
    if "<think>" in text and "</think>" not in text:
        return None  # the model ran out of tokens while still thinking
    text = text.split("</think>")[-1]
    text = re.sub(r"\*\*|__|`", "", text).strip()
    return text or None


# ---------------------------------------------------------------- small-model-friendly formats
# Small models often break JSON, so we ask for simple "LABEL: value" lines and parse forgivingly.


def complete_fields(prompt: str, fields: list[str], max_tokens: int = 400) -> dict | None:
    """Ask for 'FIELD: value' lines; return {field: value} or None if any field is missing.
    Retries once with a stricter reminder, because small models sometimes ignore the format."""
    fmt = "\n".join(f"{f}: <{f.lower()}>" for f in fields)
    for attempt in range(2):
        extra = "" if attempt == 0 else "\nIMPORTANT: use exactly the labels shown, one per line.\n"
        text = complete(f"{prompt}\n{extra}\nReply in exactly this format, nothing else:\n{fmt}", max_tokens)
        parsed = parse_fields(text or "", fields)
        if parsed:
            return parsed
    return None


def parse_fields(text: str, fields: list[str]) -> dict | None:
    out, current = {}, None
    pattern = re.compile(r"^[\s#*>\-\d.]*(" + "|".join(fields) + r")\s*[:=\-]\s*(.*)$", re.I)
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            current = m.group(1).upper()
            out[current] = m.group(2).strip()
        elif current and line.strip():
            out[current] += " " + line.strip()  # value continued on the next line
    if all(out.get(f) for f in fields):
        return {f: out[f] for f in fields}
    return None


def complete_lines(prompt: str, keys: list[str], max_tokens: int = 700) -> dict:
    """Ask for 'KEY | text' lines (e.g. 'S11 | reason'); return {key: text} for every key found."""
    text = complete(prompt, max_tokens) or ""
    out = {}
    for line in text.splitlines():
        m = re.match(r"^[\s#*>\-\d.]*\[?([A-Za-z]+\d*)\]?\s*[|:\-–]\s*(.+)$", line.strip())
        if m:
            key = m.group(1).upper()
            match = next((k for k in keys if k.upper() == key), None)
            if match and match not in out:
                out[match] = m.group(2).strip()
    return out
