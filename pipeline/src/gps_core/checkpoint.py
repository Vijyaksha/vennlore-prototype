"""Skip-if-exists checkpoints so a stopped run resumes instead of restarting.
Keys are CONTENT hashes (engine id + stage + inputs), so a prompt, model or
input change can never silently reuse a stale result.
Inputs must be JSON-native (str/int/float/bool/None, lists, dicts with str
keys); on resume the value is the JSON round-trip, so tuples come back as
lists."""
import hashlib
import json
import os
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
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(result))
    os.replace(tmp, path)
    return result
