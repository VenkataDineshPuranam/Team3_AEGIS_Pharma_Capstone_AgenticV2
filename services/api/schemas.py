"""HTTP wire-format models -- deliberately distinct from packages/domain/'s domain models
(GovernedState, DecisionSupportOutput, etc.). This is the API's own contract, not a
re-export of the domain layer, so the two can evolve independently."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

Workflow = Literal["batch_review", "pv_intake", "supply_planning"]
RunStatus = Literal[
    "pending_approval",
    "completed",
    "abstained",
    "blocked",
    "refused",
    "timed_out",
]


class SubmitRunRequest(BaseModel):
    workflow: Workflow
    subject_id: str  # batch_id / case_id / product_id
    requester_role: str


class DecideRequest(BaseModel):
    workflow: Workflow
    action: Literal["approved", "rejected", "veto", "timed_out"]
    leg: Literal["planning", "quality"] | None = None  # supply_planning only
    justification: str | None = None

    @model_validator(mode="after")
    def justification_required_for_human_action(self) -> "DecideRequest":
        if self.action != "timed_out":
            text = (self.justification or "").strip()
            if len(text) < 8:
                raise ValueError(
                    "justification is required for approve/reject/veto (G-10) -- at least 8 characters."
                )
        return self


class DraftClaim(BaseModel):
    text: str
    cites: list[str] = []


class EvidenceItemOut(BaseModel):
    evidence_id: str
    source: str
    status: str
    effective_date: str | None = None
    jurisdiction: str | None = None
    supersedes: str | None = None
    content_excerpt: str = ""


class RunResult(BaseModel):
    run_id: str
    workflow: Workflow
    subject_id: str | None = None
    requester_role: str | None = None
    status: RunStatus
    terminal_state: str | None = None
    abstention_reason: str | None = None
    llm_calls: int | None = None
    tool_calls: int | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    draft_summary: str | None = None
    draft_claims: list[dict[str, Any]] = []
    approver_roles: list[str] = []
    required_legs: list[str] | None = None
    approved_legs: list[str] = []
    policy_contract_version: str | None = None
    hitl_status: str | None = None
    hitl_tier: str | None = None
    hitl_deadline: str | None = None
    veto_recorded: bool = False
    evidence: list[dict[str, Any]] = []
    domain_payload: dict[str, Any] | None = None
    critic_verdict: str | None = None
    critic_reason_codes: list[str] = []
    guard_verdict: str | None = None
    trace_id: str | None = None
    created_at: str | None = None
    audit_events: list[dict[str, Any]] = []


class QueueEntry(BaseModel):
    run_id: str
    workflow: Workflow
    subject_id: str
    requester_role: str
    approver_roles: list[str]
    required_legs: list[str] | None
    approved_legs: list[str]
    draft_summary: str | None
    draft_claims: list[dict[str, Any]]
    created_at: str
    hitl_tier: str | None = None
    hitl_deadline: str | None = None
    policy_contract_version: str | None = None
    critic_reason_codes: list[str] = []
    snapshot: dict[str, Any] = Field(default_factory=dict)


class DashboardResponse(BaseModel):
    workflow: str | None
    cost: dict[str, Any]
    guardrail_trip: dict[str, Any]
    terminal_states: dict[str, Any]
    cache: dict[str, Any]


class GuardrailEvent(BaseModel):
    run_id: str
    workflow: str | None = None
    matched_terms: list[str] = []
    draft_sha256: str | None = None
    recorded_at: str | None = None
    abstention_reason: str | None = None
