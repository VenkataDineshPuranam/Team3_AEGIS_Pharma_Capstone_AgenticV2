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


def _retrieve_then_reconcile(run_id: str, batch_id: str, evidence_ids: list[str] | None = None):
    from services.integration.batch_reconcile import reconcile
    from services.integration.evidence_retrieve import retrieve

    # "policy" (not just "BATCH_RELEASE") matches every approved doc's authority field
    # ("NovaCura Global Policy") -- the same broadening real graph.py's retrieve() call
    # uses, needed here so the Stage 21 gap-closure fixtures below (which cite K-027/
    # K-028, not just K-006) can actually resolve their evidence_ids against this run.
    retrieve(run_id=run_id, terms=["BATCH_RELEASE", "policy"], policy_contract_version="v1")
    return reconcile(
        run_id=run_id, batch_id=batch_id, evidence_ids=evidence_ids or ["K-006"], policy_contract_version="v1"
    )


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


def test_sterility_excursion_batch_surfaces_environmental_monitoring_gap(schema):
    """Stage 21 gap-closure -- INJ-022: sterility excursion, organism ID inconclusive."""
    result = _retrieve_then_reconcile("R-recon-sterility", "B-004", evidence_ids=["K-006", "K-028"])
    validate(instance=result, schema=schema["output"])
    em = next(f for f in result["findings"] if f["category"] == "environmental_monitoring")
    assert em["status"] == "gap"
    assert "organism" in em["gap_description"].lower()


def test_unit_conversion_defect_surfaces_as_lab_results_conflict(schema):
    """Stage 21 gap-closure -- INJ-024: mg/L vs mg/mL unit-conversion defect."""
    result = _retrieve_then_reconcile("R-recon-units", "B-005")
    validate(instance=result, schema=schema["output"])
    lab = next(f for f in result["findings"] if f["category"] == "lab_results")
    assert lab["status"] == "conflict"
    assert "mg/" in lab["gap_description"]


def test_back_entered_ebr_step_surfaces_as_deviations_gap(schema):
    """Stage 21 gap-closure -- INJ-025: EBR step back-entered during network degradation."""
    result = _retrieve_then_reconcile("R-recon-backentry", "B-006")
    validate(instance=result, schema=schema["output"])
    dev = next(f for f in result["findings"] if f["category"] == "deviations")
    assert dev["status"] == "gap"
    assert "back-entered" in dev["gap_description"].lower()


def test_campaign_sequencing_change_surfaces_as_change_control_conflict(schema):
    """Stage 21 gap-closure -- INJ-026: cleaning-validation boundary after campaign resequencing."""
    result = _retrieve_then_reconcile("R-recon-campaign", "B-007")
    validate(instance=result, schema=schema["output"])
    cc = next(f for f in result["findings"] if f["category"] == "change_control")
    assert cc["status"] == "conflict"
    assert "cleaning-validation" in cc["gap_description"].lower()


def test_pat_model_recipe_drift_surfaces_as_process_analytical_gap(schema):
    """Stage 21 gap-closure -- INJ-027: PAT model version changed without recipe sync.
    Also exercises the new 'process_analytical' category added this stage."""
    result = _retrieve_then_reconcile("R-recon-pat", "B-008", evidence_ids=["K-006", "K-027"])
    validate(instance=result, schema=schema["output"])
    pat = next(f for f in result["findings"] if f["category"] == "process_analytical")
    assert pat["status"] == "gap"
    assert "PAT-DISS" in pat["gap_description"]


def test_contract_site_audit_commitment_surfaces_as_supplier_evidence_gap(schema):
    """Stage 21 gap-closure -- INJ-028: QP evidence gap, missing contract-site audit confirmation."""
    result = _retrieve_then_reconcile("R-recon-qp-gap", "B-009")
    validate(instance=result, schema=schema["output"])
    supplier = next(f for f in result["findings"] if f["category"] == "supplier_evidence")
    assert supplier["status"] == "gap"
    assert "audit" in supplier["gap_description"].lower()


def test_audit_trail_disabled_window_surfaces_as_deviations_gap(schema):
    """Stage 21 gap-closure -- INJ-029: privileged account disabled audit capture."""
    result = _retrieve_then_reconcile("R-recon-audit-disable", "B-010", evidence_ids=["K-006", "K-014"])
    validate(instance=result, schema=schema["output"])
    dev = next(f for f in result["findings"] if f["category"] == "deviations")
    assert dev["status"] == "gap"
    assert "audit" in dev["gap_description"].lower()


def test_shared_instrument_account_surfaces_as_deviations_gap(schema):
    """Stage 21 gap-closure -- INJ-030: shared laboratory instrument account."""
    result = _retrieve_then_reconcile("R-recon-shared-account", "B-011", evidence_ids=["K-006", "K-014"])
    validate(instance=result, schema=schema["output"])
    dev = next(f for f in result["findings"] if f["category"] == "deviations")
    assert dev["status"] == "gap"
    assert "attribution" in dev["gap_description"].lower()


def test_three_way_validation_state_disagreement_surfaces_as_conflict(schema):
    """Stage 21 gap-closure -- INJ-031: validation-state ambiguity across three systems."""
    result = _retrieve_then_reconcile("R-recon-val-ambiguity", "B-012", evidence_ids=["K-006", "K-010"])
    validate(instance=result, schema=schema["output"])
    vs = next(f for f in result["findings"] if f["category"] == "validation_state")
    assert vs["status"] == "conflict"


def test_unapproved_spreadsheet_surfaces_as_validation_state_gap(schema):
    """Stage 21 gap-closure -- INJ-032: unapproved macro-enabled spreadsheet."""
    result = _retrieve_then_reconcile("R-recon-spreadsheet", "B-013", evidence_ids=["K-006", "K-010"])
    validate(instance=result, schema=schema["output"])
    vs = next(f for f in result["findings"] if f["category"] == "validation_state")
    assert vs["status"] == "gap"
    assert "spreadsheet" in vs["gap_description"].lower()


def test_capa_taxonomy_evasion_surfaces_as_capa_conflict(schema):
    """Stage 21 gap-closure -- INJ-033: recurring deviation reappears under a different taxonomy code."""
    result = _retrieve_then_reconcile("R-recon-capa-taxonomy", "B-014")
    validate(instance=result, schema=schema["output"])
    capa = next(f for f in result["findings"] if f["category"] == "capa")
    assert capa["status"] == "conflict"
    assert "taxonomy" in capa["gap_description"].lower()


def test_emergency_change_never_retro_approved_surfaces_as_change_control_gap(schema):
    """Stage 21 gap-closure -- INJ-034: change-control bypass."""
    result = _retrieve_then_reconcile("R-recon-emergency-change", "B-015")
    validate(instance=result, schema=schema["output"])
    cc = next(f for f in result["findings"] if f["category"] == "change_control")
    assert cc["status"] == "gap"
    assert "emergency" in cc["gap_description"].lower()


def test_transcribed_certificate_provenance_break_surfaces_as_supplier_evidence_gap(schema):
    """Stage 21 gap-closure -- INJ-036: ALCOA+ provenance break, original unlocatable."""
    result = _retrieve_then_reconcile("R-recon-alcoa", "B-016", evidence_ids=["K-006", "K-014"])
    validate(instance=result, schema=schema["output"])
    supplier = next(f for f in result["findings"] if f["category"] == "supplier_evidence")
    assert supplier["status"] == "gap"
    assert "hash" in supplier["gap_description"].lower()


def test_evidence_id_not_in_run_is_rejected():
    from services.integration.batch_reconcile import ToolError, reconcile
    from services.integration.evidence_retrieve import retrieve

    run_id = "R-recon-untraced"
    retrieve(run_id=run_id, terms=["BATCH_RELEASE"], policy_contract_version="v1")
    with pytest.raises(ToolError) as exc_info:
        reconcile(run_id=run_id, batch_id="B-001", evidence_ids=["K-999-NOT-RETRIEVED"], policy_contract_version="v1")
    assert exc_info.value.code == "EVIDENCE_ID_NOT_IN_RUN"
