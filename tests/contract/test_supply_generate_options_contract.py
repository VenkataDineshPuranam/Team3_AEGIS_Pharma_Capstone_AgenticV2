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


def test_gap_closure_fields_surface_as_informational_triage_data(schema):
    """Stage 21 gap-closure -- INJ-051 (cold-chain excursion), INJ-052 (serialization
    aggregation break), INJ-053 (counterfeit suspicion), INJ-054 (sole-source shortage),
    INJ-055 (CMO capacity conflict), INJ-056 (allocation ethics), INJ-057 (customs
    mismatch), INJ-058 (recall-scope triage info -- never a recall_scope itself)."""
    from services.integration.supply_generate_options import generate_options

    result = generate_options(run_id="R-supply-gaps", product_id="P-300", constraint_set={}, evidence_ids=["K-009"])
    validate(instance=result, schema=schema["output"])

    opt1, opt2 = result["options"]
    assert opt1["cold_chain_excursion"]["exceeded_range"] is True
    assert opt1["serialization_status"] == "aggregation_gap"
    assert opt1["counterfeit_review_flag"] == "inconsistent_print_history"
    assert opt2["shortage_root_cause"]["supplier_type"] == "sole_source"
    assert opt2["cmo_capacity_conflict"]["window_overlap"] is True
    assert opt2["customs_status"] == "description_mismatch"
    assert "excipient-lot-EX-7743" in opt2["overlap_information"]["shared_components"]
    assert set(result["allocation_ethics_flags"]) == {
        "trial_demand_present", "compassionate_use_present", "cross_market_conflict",
    }

    # The structural guarantee INJ-058 depends on: no key anywhere in this output could
    # ever spell "recall_scope" -- checked live, not just in the schema's own type.
    banned = set(schema["what_this_schema_cannot_express"][:-1])
    assert not banned & set(opt2["overlap_information"].keys())


def test_output_has_no_disposition_field(schema):
    """The schema's own what_this_schema_cannot_express list, checked against a live
    output (ADR-004 layer 2, second independent check)."""
    from services.integration.supply_generate_options import generate_options

    result = generate_options(run_id="R-supply-3", product_id="P-100", constraint_set={}, evidence_ids=["K-009"])
    banned = set(schema["what_this_schema_cannot_express"][:-1])
    assert not banned & set(result.keys())
    for option in result["options"]:
        assert not banned & set(option.keys())
