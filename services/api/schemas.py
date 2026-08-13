"""HTTP wire-format models -- deliberately distinct from packages/domain/'s domain models
(GovernedState, DecisionSupportOutput, etc.). This is the API's own contract, not a
re-export of the domain layer, so the two can evolve independently."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

Workflow = Literal["batch_review", "pv_intake", "supply_planning"]


class SubmitRunRequest(BaseModel):
    workflow: Workflow
    subject_id: str  # batch_id / case_id / product_id
    requester_role: str


class DecideRequest(BaseModel):
    workflow: Workflow
    action: Literal["approved", "rejected", "veto", "timed_out"]
    leg: Literal["planning", "quality"] | None = None  # supply_planning only


class RunResult(BaseModel):
    run_id: str
    workflow: Workflow
    status: Literal["pending_approval", "completed", "abstained", "blocked", "refused"]
    terminal_state: str | None = None
    abstention_reason: str | None = None
    llm_calls: int | None = None
    draft_summary: str | None = None
    draft_claims: list[dict[str, Any]] = []
    approver_roles: list[str] = []
    required_legs: list[str] | None = None
    approved_legs: list[str] = []


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


class DashboardResponse(BaseModel):
    workflow: str | None
    cost: dict[str, Any]
    guardrail_trip: dict[str, Any]
    terminal_states: dict[str, Any]
    cache: dict[str, Any]
