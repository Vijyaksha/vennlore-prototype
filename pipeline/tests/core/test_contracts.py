import json
from pathlib import Path

import pytest

from gps_core.contracts import ContractError, FIXTURES, validate

VALID = FIXTURES / "valid"
INVALID = FIXTURES / "invalid"


@pytest.mark.parametrize("kind", ["talk", "recommendation", "run"])
def test_valid_fixture_passes(kind):
    validate(kind, json.loads((VALID / f"{kind}.json").read_text()))


@pytest.mark.parametrize("path", sorted(INVALID.glob("*.json")), ids=lambda p: p.stem)
def test_invalid_fixture_fails(path: Path):
    kind = path.stem.split("-")[0]
    with pytest.raises(ContractError):
        validate(kind, json.loads(path.read_text()))


def test_unknown_kind():
    with pytest.raises(KeyError):
        validate("nope", {})
