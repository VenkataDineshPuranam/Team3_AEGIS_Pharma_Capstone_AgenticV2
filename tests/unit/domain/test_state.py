"""Phase 1 unit tests -- prove ADR-004 layer 1 holds at the type level, not just in prose.

Executes langgraph_design.md SS3's "what this schema deliberately cannot express" table.
No API key, no network, no Neo4j needed -- pure type-construction tests.
"""
import pytest
from pydantic import ValidationError

from packages.domain.evidence import Claim, EvidenceItem
from packages.domain.payloads import BatchPayload, ReconciliationFinding
from packages.domain.state import (
    RETRYABLE_REASON_CODES,
    DecisionSupportOutput,
    ProhibitionContract,
    ReasonCode,
    new_state,
)


def test_evidence_item_rejects_non_citable_status():
    """Only 'approved'/'draft' are constructible -- 'untrusted'/'superseded' are not
    valid enum values, matching evidence_retrieve.schema.json's own output enum."""
    with pytest.raises(ValidationError):
        EvidenceItem(
            evidence_id="K-999",
            source="fake",
            status="untrusted",  # type: ignore[arg-type]
            effective_date="2026-01-01",
        )


def test_batch_payload_forbids_disposition_fields():
    """ADR-004 layer 1: a release/reject signal cannot be attached to BatchPayload even
    by a caller that tries to."""
    finding = ReconciliationFinding(
        category="genealogy", status="complete", evidence_ids=("K-001",)
    )
    with pytest.raises(ValidationError):
        BatchPayload(
            batch_id="B-001",
            reconciliation_complete=True,
            findings=(finding,),
            release_recommended=True,  # type: ignore[call-arg]
        )


def test_decision_support_output_forbids_disposition_fields():
    with pytest.raises(ValidationError):
        DecisionSupportOutput(
            summary="test",
            claims=(),
            causality="probable",  # type: ignore[call-arg]
        )


def test_reason_code_prohibition_adjacent_is_not_retryable():
    """failure_and_loop_guards.md SS4 -- the one code with no retry edge."""
    assert ReasonCode.PROHIBITION_ADJACENT not in RETRYABLE_REASON_CODES
    assert ReasonCode.MISSING_CITATION in RETRYABLE_REASON_CODES


def test_new_state_starts_with_zeroed_budgets_and_empty_append_only_lists():
    state = new_state(run_id="R-1", workflow="batch_review", requester_role="EU Qualified Person")
    assert state["llm_calls"] == 0
    assert state["tool_calls"] == 0
    assert state["evidence"] == []
    assert state["critic_reason_codes"] == []
    assert state["approver_roles"] == []
    assert state["hitl_approved_legs"] == []
    assert state["terminal_state"] is None
    assert state["veto_recorded"] is False


def test_prohibition_contract_is_frozen():
    contract = ProhibitionContract(
        workflow="batch_review",
        banned_terms=("release", "reject", "reprocess", "relabel", "recall"),
        banned_field_names=("release_recommended", "reject_recommended"),
    )
    with pytest.raises(ValidationError):
        contract.workflow = "pv_intake"  # type: ignore[misc]


def test_claim_round_trips_citations():
    claim = Claim(text="Release packet completeness is defined by K-006", cites=("K-006",))
    assert claim.cites == ("K-006",)
