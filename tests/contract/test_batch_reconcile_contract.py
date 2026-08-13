"""Validates services/integration/batch_reconcile.py against
packages/contracts/tool_contracts/batch_reconcile.schema.json, using the synthetic
fixtures (tests/fixtures/synthetic/batches/). Requires evidence_retrieve to have run
first in the same run_id, matching the real graph's node order (retrieve -> reconcile).
"""
import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from jsonschema import validate

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "packages" / "contracts" / "tool_contracts" / "batch_reconcile.schema.json"

pytestmark = pytest.mark.skipif(
    not os.environ.get("NEO4J_PASSWORD") or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
    reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured (evidence_retrieve is a prerequisite)",
)


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text())


def _retrieve_then_reconcile(run_id: str, batch_id: str):
    from services.integration.batch_reconcile import reconcile
    from services.integration.evidence_retrieve import retrieve

    retrieve(run_id=run_id, terms=["BATCH_RELEASE"], policy_contract_version="v1")
    return reconcile(run_id=run_id, batch_id=batch_id, evidence_ids=["K-006"], policy_contract_version="v1")


def test_clean_batch_matches_schema_and_is_complete(schema):
    result = _retrieve_then_reconcile("R-recon-clean", "B-001")
    validate(instance=result, schema=schema["output"])
    assert result["reconciliation_complete"] is True
    assert all(f["status"] == "complete" for f in result["findings"])


def test_genealogy_gap_batch_matches_schema_and_is_incomplete(schema):
    result = _retrieve_then_reconcile("R-recon-gap", "B-002")
    validate(instance=result, schema=schema["output"])
    assert result["reconciliation_complete"] is False
    genealogy = next(f for f in result["findings"] if f["category"] == "genealogy")
    assert genealogy["status"] == "gap"
    assert genealogy["gap_description"]


def test_conflict_batch_matches_schema_and_is_incomplete(schema):
    result = _retrieve_then_reconcile("R-recon-conflict", "B-003")
    validate(instance=result, schema=schema["output"])
    assert result["reconciliation_complete"] is False
    lab = next(f for f in result["findings"] if f["category"] == "lab_results")
    assert lab["status"] == "conflict"


def test_output_has_no_disposition_field(schema):
    """The schema's own what_this_schema_cannot_express list, checked against a live
    output, not just the type definition (ADR-004 layer 1+2, second independent check)."""
    result = _retrieve_then_reconcile("R-recon-disposition-check", "B-001")
    banned = set(schema["what_this_schema_cannot_express"][:-1])  # last entry is prose, not a field name -- see schema
    assert not banned & set(result.keys())
    for finding in result["findings"]:
        assert not banned & set(finding.keys())


def test_evidence_id_not_in_run_is_rejected():
    from services.integration.batch_reconcile import ToolError, reconcile
    from services.integration.evidence_retrieve import retrieve

    run_id = "R-recon-untraced"
    retrieve(run_id=run_id, terms=["BATCH_RELEASE"], policy_contract_version="v1")
    with pytest.raises(ToolError) as exc_info:
        reconcile(run_id=run_id, batch_id="B-001", evidence_ids=["K-999-NOT-RETRIEVED"], policy_contract_version="v1")
    assert exc_info.value.code == "EVIDENCE_ID_NOT_IN_RUN"
