"""Validates services/integration/evidence_retrieve.py's real output against the actual
packages/contracts/tool_contracts/evidence_retrieve.schema.json -- proving the
implementation matches the contract, not re-deriving the contract (BC-10).

Requires a live, ingested Neo4j (packages/domain/kg/ingest.py) -- skipped otherwise,
consistent with the BLOCKED_BY_ENVIRONMENT convention from Stage 14.
"""
import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from jsonschema import validate

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "packages" / "contracts" / "tool_contracts" / "evidence_retrieve.schema.json"

pytestmark = pytest.mark.skipif(
    not os.environ.get("NEO4J_PASSWORD") or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
    reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured",
)


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text())


def test_retrieve_output_matches_schema(schema):
    from services.integration.evidence_retrieve import retrieve

    result = retrieve(run_id="R-contract-1", terms=["policy"], policy_contract_version="v1")
    validate(instance=result, schema=schema["output"])


def test_retrieve_never_returns_non_citable_status(schema):
    """The schema's own output enum only allows approved/draft -- this test additionally
    proves the live query respects it, not just that the type would."""
    from services.integration.evidence_retrieve import retrieve

    result = retrieve(run_id="R-contract-2", terms=["a", "e", "i", "o"], policy_contract_version="v1")
    for item in result["items"]:
        assert item["status"] in ("approved", "draft")


def test_broadening_limit_matches_schema_error_code():
    from services.integration.evidence_retrieve import ToolError, retrieve

    run_id = "R-contract-broaden"
    retrieve(run_id=run_id, terms=["policy"], policy_contract_version="v1", broadening=True)
    with pytest.raises(ToolError) as exc_info:
        retrieve(run_id=run_id, terms=["policy"], policy_contract_version="v1", broadening=True)
    assert exc_info.value.code == "BROADENING_LIMIT_EXCEEDED"
