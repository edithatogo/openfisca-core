import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
SCHEMA = json.loads((ROOT / "docs/yaml-conversion-diagnostics.schema.json").read_text())
EXAMPLES = ROOT / "docs/yaml-portability-examples"


def validate_contract(document):
    required = set(SCHEMA["required"])
    assert required <= document.keys()
    assert document.keys() <= SCHEMA["properties"].keys()
    assert document["schema_version"] == "1.0"
    assert document["target"]["openfisca_core"].startswith("44.")

    errors = [item for item in document["diagnostics"] if item["severity"] == "error"]
    warnings = [
        item for item in document["diagnostics"] if item["severity"] == "warning"
    ]
    assert all(item["code"].startswith("OFC-E-") for item in errors)
    assert all(
        item["code"].startswith("OFC-W-") and item.get("assumption")
        for item in warnings
    )

    if document["outcome"] == "success":
        assert document["output_emitted"] is True
        assert document["diagnostics"] == []
    elif document["outcome"] == "success_with_warnings":
        assert document["output_emitted"] is True
        assert warnings and not errors
    elif document["outcome"] == "failure":
        assert document["output_emitted"] is False
        assert errors
    else:
        raise AssertionError("unknown outcome")


@pytest.mark.parametrize("name", ["lossless.json", "lossy.json", "unsupported.json"])
def test_diagnostic_examples_conform_to_schema(name):
    document = json.loads((EXAMPLES / name).read_text())
    validate_contract(document)


@pytest.mark.parametrize(
    ("outcome", "output_emitted", "diagnostics"),
    [
        (
            "failure",
            True,
            [
                {
                    "severity": "error",
                    "code": "OFC-E-X",
                    "source_path": "",
                    "message": "x",
                }
            ],
        ),
        (
            "success",
            True,
            [
                {
                    "severity": "warning",
                    "code": "OFC-W-X",
                    "source_path": "",
                    "message": "x",
                    "assumption": "a",
                }
            ],
        ),
        ("success_with_warnings", True, []),
    ],
)
def test_diagnostic_outcomes_fail_closed(outcome, output_emitted, diagnostics):
    document = json.loads((EXAMPLES / "lossless.json").read_text())
    document.update(
        outcome=outcome, output_emitted=output_emitted, diagnostics=diagnostics
    )

    with pytest.raises(AssertionError):
        validate_contract(document)
