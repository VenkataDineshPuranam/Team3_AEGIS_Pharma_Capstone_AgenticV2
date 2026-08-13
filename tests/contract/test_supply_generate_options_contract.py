"""Validates services/integration/supply_generate_options.py against the real Stage 11
schema, using the synthetic supply fixtures.
"""
import json
from pathlib import Path

import pytest
from jsonschema import validate

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "packages" / "contracts" / "tool_contracts" / "supply_generate_options.schema.json"


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text())


def test_options_available_matches_schema(schema):
    from services.integration.supply_generate_options import generate_options

    result = generate_options(
        run_id="R-supply-1", product_id="P-100", constraint_set={}, evidence_ids=["K-009"]
    )
    validate(instance=result, schema=schema["output"])
    assert len(result["options"]) == 2


def test_empty_result_raises_constraint_set_empty_result(schema):
    from services.integration.supply_generate_options import ToolError, generate_options

    with pytest.raises(ToolError) as exc_info:
        generate_options(run_id="R-supply-2", product_id="P-200", constraint_set={}, evidence_ids=["K-009"])
    assert exc_info.value.code == "CONSTRAINT_SET_EMPTY_RESULT"


def test_output_has_no_disposition_field(schema):
    """The schema's own what_this_schema_cannot_express list, checked against a live
    output (ADR-004 layer 2, second independent check)."""
    from services.integration.supply_generate_options import generate_options

    result = generate_options(run_id="R-supply-3", product_id="P-100", constraint_set={}, evidence_ids=["K-009"])
    banned = set(schema["what_this_schema_cannot_express"][:-1])
    assert not banned & set(result.keys())
    for option in result["options"]:
        assert not banned & set(option.keys())
