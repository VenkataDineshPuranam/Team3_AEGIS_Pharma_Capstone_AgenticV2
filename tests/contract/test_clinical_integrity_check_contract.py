"""Validates services/integration/clinical_integrity_check.py against
packages/contracts/tool_contracts/clinical_integrity_check.schema.json, using the synthetic
fixtures (tests/fixtures/synthetic/clinical/). Same pattern as
test_batch_reconcile_contract.py.
"""
import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from jsonschema import validate

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "packages" / "contracts" / "tool_contracts" / "clinical_integrity_check.schema.json"

pytestmark = pytest.mark.skipif(
    not os.environ.get("NEO4J_PASSWORD") or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
    reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured (evidence_retrieve is a prerequisite)",
)


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text())


def _retrieve_then_reconcile(run_id: str, protocol_id: str):
    from services.integration.clinical_integrity_check import integrity_check
    from services.integration.evidence_retrieve import retrieve

    retrieve(run_id=run_id, terms=["CLINICAL", "policy"], policy_contract_version="v1")
    return integrity_check(run_id=run_id, protocol_id=protocol_id, evidence_ids=["K-008"], policy_contract_version="v1")


def test_clean_clinical_matches_schema_and_is_complete(schema):
    result = _retrieve_then_reconcile("R-recon-clean", "CT-001")
    validate(instance=result, schema=schema["output"])
    assert result["reconciliation_complete"] is True


def test_eligibility_conflict_matches_schema_and_is_incomplete(schema):
    result = _retrieve_then_reconcile("R-recon-conflict", "CT-003")
    validate(instance=result, schema=schema["output"])
    assert result["reconciliation_complete"] is False
    elig = next(f for f in result["findings"] if f["category"] == "eligibility_criteria")
    assert elig["status"] == "conflict"


def test_output_has_no_qualification_field(schema):
    result = _retrieve_then_reconcile("R-recon-disposition-check", "CT-001")
    banned = set(schema["what_this_schema_cannot_express"][:-1])
    assert not banned & set(result.keys())
    for finding in result["findings"]:
        assert not banned & set(finding.keys())


def test_evidence_id_not_in_run_is_rejected():
    from services.integration.clinical_integrity_check import ToolError, integrity_check
    from services.integration.evidence_retrieve import retrieve

    run_id = "R-recon-untraced"
    retrieve(run_id=run_id, terms=["CLINICAL", "policy"], policy_contract_version="v1")
    with pytest.raises(ToolError) as exc_info:
        integrity_check(run_id=run_id, protocol_id="CT-001", evidence_ids=["K-999-NOT-RETRIEVED"], policy_contract_version="v1")
    assert exc_info.value.code == "EVIDENCE_ID_NOT_IN_RUN"
