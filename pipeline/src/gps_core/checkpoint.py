"""Skip-if-exists checkpoints so a stopped run resumes instead of restarting.
Keys are CONTENT hashes (engine id + stage + inputs), so a prompt, model or
input change can never silently reuse a stale result."""
import hashlib
import json
from pathlib import Path
from typing import Callable


def content_key(*parts) -> str:
    blob = json.dumps(parts, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:24]


def checkpointed(path: Path, fn: Callable[[], object]):
    if path.exists():
        return json.loads(path.read_text())
    result = fn()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(result))
    tmp.rename(path)
    return result
