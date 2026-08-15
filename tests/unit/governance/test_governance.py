"""Phase 3 unit tests -- no Neo4j, no API key needed. Pure logic over the governance
modules: policy_engine (fail-closed), prohibited_action_guard (ADR-004 layer 3),
evidence_gate (ADR-003 second check), hitl_route (ladder), audit_store (append-only, veto).
"""
import sqlite3
from datetime import UTC, datetime, timedelta

import pytest

from packages.domain.evidence import Claim, EvidenceItem
from packages.domain.state import DecisionSupportOutput
from services.integration import audit_store, evidence_gate, hitl_route, prohibited_action_guard
from services.integration.policy_engine import PolicyEngineUnavailable, get_prohibition_contract


# --- policy_engine (fail closed, ADR-005/BC-3) ---

def test_load_real_v1_policy_contract():
    contract = get_prohibition_contract("v1", "batch_review")
    assert contract.workflow == "batch_review"
    assert "recommend release" in contract.banned_terms


def test_policy_engine_fails_closed_on_missing_version():
    with pytest.raises(PolicyEngineUnavailable):
        get_prohibition_contract("v999-does-not-exist", "batch_review")


# --- prohibited_action_guard (ADR-004 layer 3) ---

@pytest.fixture
def batch_contract():
    return get_prohibition_contract("v1", "batch_review")


def test_guard_clears_a_clean_draft(batch_contract):
    draft = DecisionSupportOutput(
        summary="Reconciliation shows one genealogy gap for batch B-002.",
        claims=(Claim(text="Genealogy is incomplete per K-006.", cites=("K-006",)),),
    )
    result = prohibited_action_guard.check(draft, batch_contract)
    assert result.verdict == "clear"


def test_guard_blocks_a_disposition_signal(batch_contract):
    draft = DecisionSupportOutput(
        summary="Based on the evidence, I recommend release of batch B-001.",
        claims=(Claim(text="All categories are complete per K-006.", cites=("K-006",)),),
    )
    result = prohibited_action_guard.check(draft, batch_contract)
    assert result.verdict == "blocked"
    assert any("release" in t for t in result.matched_terms)


def test_guard_is_case_insensitive(batch_contract):
    draft = DecisionSupportOutput(summary="RECOMMEND RELEASE of this batch.", claims=())
    result = prohibited_action_guard.check(draft, batch_contract)
    assert result.verdict == "blocked"


# --- evidence_gate (ADR-003 second check) ---

def test_gate_sufficient_when_evidence_present():
    items = [EvidenceItem(evidence_id="K-006", source="x", status="approved", effective_date="2026-06-01")]
    assert evidence_gate.check(items, broadenings_used=0).outcome == "sufficient"


def test_gate_broadens_once_then_abstains():
    assert evidence_gate.check([], broadenings_used=0).outcome == "broaden"
    assert evidence_gate.check([], broadenings_used=1).outcome == "abstain"


# --- hitl_route (four-tier ladder, BC-12) ---

def test_ladder_widens_at_t2_without_removing_primary():
    state = hitl_route.HitlState(run_id="R-1")
    now = state.started_at + timedelta(hours=17)
    resolved = hitl_route.resolve_tier(state, now)
    assert resolved.tier == "T2"
    assert hitl_route.PRIMARY_APPROVER in resolved.approver_roles
    assert hitl_route.ESCALATION_ROLE in resolved.approver_roles


def test_ladder_expires_to_timed_out_at_t3():
    state = hitl_route.HitlState(run_id="R-2")
    now = state.started_at + timedelta(hours=25)
    resolved = hitl_route.resolve_tier(state, now)
    assert resolved.tier == "T3"
    assert resolved.status == "timed_out"


def test_approval_after_t3_is_rejected():
    state = hitl_route.HitlState(run_id="R-3", tier="T3", status="timed_out")
    with pytest.raises(ValueError):
        hitl_route.record_approval(state, hitl_route.PRIMARY_APPROVER, "approved")


def test_approval_by_ineligible_role_is_rejected():
    state = hitl_route.HitlState(run_id="R-4")  # T0, only primary eligible
    with pytest.raises(ValueError):
        hitl_route.record_approval(state, hitl_route.ESCALATION_ROLE, "approved")


# --- audit_store (append-only, veto invariant) ---

@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.executescript(audit_store._SCHEMA)
    yield connection
    connection.close()


def test_agent_run_write_and_no_update_method_exists(conn):
    audit_store.write_agent_run(conn, "R-1", "batch_review", "completed", datetime.now(UTC).isoformat())
    row = conn.execute("SELECT terminal_state FROM agent_run WHERE run_id='R-1'").fetchone()
    assert row[0] == "completed"
    assert not hasattr(audit_store, "update_agent_run")
    assert not hasattr(audit_store, "delete_agent_run")


def test_override_requires_nonempty_justification(conn):
    with pytest.raises(ValueError):
        audit_store.write_human_override(
            conn, "R-1", "EU Qualified Person", "T0", "approved", "   ", datetime.now(UTC).isoformat()
        )


def test_veto_cannot_be_superseded_by_later_approval(conn):
    audit_store.write_human_override(
        conn, "R-5", "Patient Safety Representative", "T1", "veto_registered",
        "Safety concern on record.", datetime.now(UTC).isoformat(),
    )
    assert audit_store.has_veto(conn, "R-5") is True
    with pytest.raises(ValueError):
        audit_store.write_human_override(
            conn, "R-5", "Chief Medical Officer", "T2", "approved",
            "Attempting to override.", datetime.now(UTC).isoformat(),
        )
