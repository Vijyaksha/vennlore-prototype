"""Validate rows against the committed JSON Schema in packages/contracts.
The zod source in packages/contracts/src is the truth; the JSON files are
generated from it and a TypeScript test keeps them in sync."""
import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[3]
SCHEMA_DIR = REPO / "packages" / "contracts" / "schema"
FIXTURES = REPO / "packages" / "contracts" / "fixtures"
KINDS = ("talk", "recommendation", "run", "themes_response", "ask_response")


class ContractError(ValueError):
    """A row does not conform to its contract."""


@lru_cache(maxsize=None)
def validator(kind: str) -> Draft202012Validator:
    if kind not in KINDS:
        raise KeyError(kind)
    schema = json.loads((SCHEMA_DIR / f"{kind}.schema.json").read_text())
    return Draft202012Validator(schema)


def validate(kind: str, row: dict) -> None:
    errors = sorted(validator(kind).iter_errors(row), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        where = "/".join(str(p) for p in first.path) or "<root>"
        raise ContractError(f"{kind} row invalid at {where}: {first.message}")
