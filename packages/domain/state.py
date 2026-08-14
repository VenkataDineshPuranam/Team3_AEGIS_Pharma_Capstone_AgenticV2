"""Shared graph state -- Stage 20a Phase 1.

Direct transcription of langgraph_design.md SS3 (GovernedState) and SS3's reducer rules.
One state object per run; every node reads and writes only this (BC-9). This module is the
single source of truth other Stage 20a phases import from -- no phase reconstructs any of
these types independently.
"""
from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal, TypedDict

from pydantic import BaseModel, ConfigDict

from packages.domain.evidence import Claim, EvidenceItem
from packages.domain.payloads import BatchPayload

Workflow = Literal[
    "batch_review", "pv_intake", "supply_planning",
    # Stage 21 -- close D02/D03/D07's OUT_OF_SCOPE injects with real governed workflows
    # following the exact same pattern (ADR-008: one graph per workflow).
    "research_review", "clinical_integrity", "regulatory_completeness",
]


class ReasonCode(StrEnum):
    """Closed enum -- failure_and_loop_guards.md SS4. A retry is only legitimate if its
    reason code is in this enum AND distinct from every prior code in the run.
    PROHIBITION_ADJACENT is the one code with no retry edge at all (checked first,
    unconditionally, in the graph's routing table -- the bug this session's earlier fix
    closed)."""

    MISSING_CITATION = "MISSING_CITATION"
    CITATION_UNRESOLVED = "CITATION_UNRESOLVED"
    CLAIM_EXCEEDS_EVIDENCE = "CLAIM_EXCEEDS_EVIDENCE"
    ABSTENTION_EXPECTED = "ABSTENTION_EXPECTED"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
    PROHIBITION_ADJACENT = "PROHIBITION_ADJACENT"


# Reason codes that PERMIT a retry to `synthesize`. PROHIBITION_ADJACENT is deliberately
# excluded -- retrying it would ask the model to rephrase a near-miss on the system's
# highest-severity control (failure_and_loop_guards.md SS4).
RETRYABLE_REASON_CODES: frozenset[ReasonCode] = frozenset(
    {
        ReasonCode.MISSING_CITATION,
        ReasonCode.CITATION_UNRESOLVED,
        ReasonCode.CLAIM_EXCEEDS_EVIDENCE,
        ReasonCode.ABSTENTION_EXPECTED,
        ReasonCode.CONTRACT_VIOLATION,
    }
)


class ProhibitionContract(BaseModel):
    """Per-workflow banned-signal list the prohibited_action_guard pattern-matches
    against (ADR-004 layer 3). Injected at compile time, never agent-supplied."""

    model_config = ConfigDict(frozen=True)

    workflow: Workflow
    banned_terms: tuple[str, ...]
    banned_field_names: tuple[str, ...]


class DecisionSupportOutput(BaseModel):
    """What `synthesize` may produce. `extra="forbid"` means a disposition field
    (release_recommended, causality, allocated_quantity, ...) cannot be attached even by
    a malformed node -- construction itself raises (ADR-004 layer 1)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    summary: str
    claims: tuple[Claim, ...]


class GovernedState(TypedDict, total=False):
    # --- identity & authorization ---
    run_id: str
    workflow: Workflow
    requester_role: str
    authorization_checked_at: datetime

    # --- policy ---
    policy_contract_version: str | None
    prohibition_contract: ProhibitionContract

    # --- evidence ---
    evidence: list[EvidenceItem]
    evidence_sufficient: bool
    broadenings_used: int

    # --- work product ---
    domain_payload: BatchPayload | None
    draft_output: DecisionSupportOutput | None
    critic_verdict: Literal["approve_for_human", "reject"] | None
    critic_reason_codes: list[ReasonCode]
    guard_verdict: Literal["clear", "blocked"] | None

    # --- human oversight ---
    hitl_required: bool
    approver_roles: list[str]
    hitl_required_legs: list[str]
    hitl_approved_legs: list[str]
    hitl_status: Literal["pending", "approved", "rejected", "timed_out"] | None
    hitl_tier: Literal["T0", "T1", "T2", "T3"] | None
    hitl_deadline: datetime | None
    veto_recorded: bool

    # --- budgets (BC-7) ---
    llm_calls: int
    tool_calls: int
    graph_steps: int
    tokens_in: int
    tokens_out: int

    # --- outcome & audit ---
    terminal_state: Literal["completed", "abstained", "blocked", "refused"] | None
    abstention_reason: str | None
    trace_id: str
    audit_record_id: str | None


def new_state(run_id: str, workflow: Workflow, requester_role: str) -> GovernedState:
    """The only constructor for a fresh run's state -- every field starts at its
    zero/empty value so append-only reducers (SS3 "Reducer rules") have something
    correct to append to."""

    return GovernedState(
        run_id=run_id,
        workflow=workflow,
        requester_role=requester_role,
        authorization_checked_at=datetime.now(UTC),
        policy_contract_version=None,
        evidence=[],
        evidence_sufficient=False,
        broadenings_used=0,
        domain_payload=None,
        draft_output=None,
        critic_verdict=None,
        critic_reason_codes=[],
        guard_verdict=None,
        hitl_required=False,
        approver_roles=[],
        hitl_required_legs=[],
        hitl_approved_legs=[],
        hitl_status=None,
        hitl_tier=None,
        hitl_deadline=None,
        veto_recorded=False,
        llm_calls=0,
        tool_calls=0,
        graph_steps=0,
        tokens_in=0,
        tokens_out=0,
        terminal_state=None,
        abstention_reason=None,
        trace_id="",
        audit_record_id=None,
    )
