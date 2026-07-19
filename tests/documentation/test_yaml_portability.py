import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).parents[2]
SCHEMA = json.loads((ROOT / "docs/yaml-conversion-diagnostics.schema.json").read_text())
EXAMPLES = ROOT / "docs/yaml-portability-examples"
INVALID_EXAMPLES = EXAMPLES / "invalid"
VALIDATOR = Draft202012Validator(SCHEMA)


def test_diagnostic_schema_is_valid_draft_2020_12():
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("name", ["lossless.json", "lossy.json", "unsupported.json"])
def test_diagnostic_examples_conform_to_schema(name):
    document = json.loads((EXAMPLES / name).read_text())
    VALIDATOR.validate(document)


@pytest.mark.parametrize(
    "path",
    sorted(INVALID_EXAMPLES.glob("*.json")),
    ids=lambda path: path.stem,
)
def test_invalid_diagnostic_examples_are_rejected(path):
    with pytest.raises(ValidationError):
        VALIDATOR.validate(json.loads(path.read_text()))
