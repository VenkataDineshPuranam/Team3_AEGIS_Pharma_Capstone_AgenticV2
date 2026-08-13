"""Validates services/integration/pv_duplicate_check.py and pv_normalize_terminology.py
against the real Stage 11 JSON schemas, using the synthetic PV fixtures
(tests/fixtures/synthetic/pv_cases/). Requires evidence_retrieve to have run first in the
same run_id, matching pv_duplicate_check's own ordering requirement (DDD SS7).
"""
import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from jsonschema import validate

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = REPO_ROOT / "packages" / "contracts" / "tool_contracts"

pytestmark = pytest.mark.skipif(
    not os.environ.get("NEO4J_PASSWORD") or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
    reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured (evidence_retrieve is a prerequisite)",
)


@pytest.fixture(scope="module")
def duplicate_check_schema():
    return json.loads((CONTRACTS_DIR / "pv_duplicate_check.schema.json").read_text())


@pytest.fixture(scope="module")
def normalize_schema():
    return json.loads((CONTRACTS_DIR / "pv_normalize_terminology.schema.json").read_text())


def _retrieve_evidence(run_id: str):
    from services.integration.evidence_retrieve import retrieve

    return retrieve(run_id=run_id, terms=["PHARMACOVIGILANCE"], policy_contract_version="v1")


def test_clean_case_duplicate_check_matches_schema(duplicate_check_schema):
    from services.integration.pv_duplicate_check import duplicate_check

    run_id = "R-pv-clean"
    retr = _retrieve_evidence(run_id)
    evidence_ids = [item["evidence_id"] for item in retr["items"]]
    result = duplicate_check(run_id=run_id, case_id="PV-001", case_summary_evidence_ids=evidence_ids)
    validate(instance=result, schema=duplicate_check_schema["output"])
    assert result["duplicate_suspected"] is False
    assert result["candidates"] == []


def test_suspected_duplicate_case_matches_schema_and_flags(duplicate_check_schema):
    from services.integration.pv_duplicate_check import duplicate_check

    run_id = "R-pv-dup"
    retr = _retrieve_evidence(run_id)
    evidence_ids = [item["evidence_id"] for item in retr["items"]]
    result = duplicate_check(run_id=run_id, case_id="PV-002", case_summary_evidence_ids=evidence_ids)
    validate(instance=result, schema=duplicate_check_schema["output"])
    assert result["duplicate_suspected"] is True
    assert result["candidates"][0]["candidate_case_id"] == "PV-001"


def test_duplicate_check_rejects_evidence_not_in_run():
    from services.integration.pv_duplicate_check import ToolError, duplicate_check

    run_id = "R-pv-untraced"
    _retrieve_evidence(run_id)
    with pytest.raises(ToolError):
        duplicate_check(run_id=run_id, case_id="PV-001", case_summary_evidence_ids=["K-999-NOT-RETRIEVED"])


def test_normalize_terminology_matches_schema_and_never_applies(normalize_schema):
    from services.integration.pv_normalize_terminology import normalize_terminology

    result = normalize_terminology(run_id="R-pv-norm", source_text="pacient reported severe nawsea after dose")
    validate(instance=result, schema=normalize_schema["output"])
    assert result["applied"] is False
    assert len(result["suggestions"]) == 2


def test_normalize_terminology_unmatched_text_returns_empty_not_guessed(normalize_schema):
    from services.integration.pv_normalize_terminology import normalize_terminology

    result = normalize_terminology(run_id="R-pv-norm2", source_text="text with no matching fixture at all")
    validate(instance=result, schema=normalize_schema["output"])
    assert result["suggestions"] == []
    assert result["applied"] is False
