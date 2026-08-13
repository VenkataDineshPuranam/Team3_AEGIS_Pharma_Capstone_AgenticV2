"""hitl_route / hitl_interrupt -- Stage 20a Phase 3. Four-tier escalation ladder
(failure_and_loop_guards.md SS5), Batch Review only. Durations from that document's SS5.2;
the clock is injectable so tests don't wait 24 business hours (`now` parameter, defaults to
real time only at the call site, never inside this module's logic).

BC-12: timeout => no action, ever. The ladder only ever WIDENS who may approve -- never
replaces the primary, never auto-approves (SS5.1).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

# failure_and_loop_guards.md SS5.2, Batch Review row (business-hours clock -- approximated
# here as wall-clock hours for 20a's local dev/testing; the business-hours calendar
# resolution is a Stage 20 deploy-time concern, not a design change).
T1_REMINDER_HOURS = 8
T2_ESCALATION_HOURS = 16
T3_EXPIRY_HOURS = 24

PRIMARY_APPROVER = "EU Qualified Person"
ESCALATION_ROLE = "Chief Quality Officer"  # failure_and_loop_guards.md SS5.4, Batch Review row


@dataclass
class HitlState:
    run_id: str
    tier: str = "T0"
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    approver_roles: tuple[str, ...] = (PRIMARY_APPROVER,)
    status: str = "pending"  # pending | approved | rejected | timed_out


def resolve_tier(state: HitlState, now: datetime) -> HitlState:
    """Pure function of elapsed time -- never a model decision (agent_roster.md SS4)."""
    elapsed = now - state.started_at
    if elapsed >= timedelta(hours=T3_EXPIRY_HOURS):
        return HitlState(
            run_id=state.run_id,
            tier="T3",
            started_at=state.started_at,
            approver_roles=state.approver_roles,
            status="timed_out",
        )
    if elapsed >= timedelta(hours=T2_ESCALATION_HOURS):
        roles = state.approver_roles
        if ESCALATION_ROLE not in roles:
            # Widens, never replaces -- SS5.1. Primary stays eligible.
            roles = roles + (ESCALATION_ROLE,)
        return HitlState(
            run_id=state.run_id, tier="T2", started_at=state.started_at,
            approver_roles=roles, status=state.status,
        )
    if elapsed >= timedelta(hours=T1_REMINDER_HOURS):
        return HitlState(
            run_id=state.run_id, tier="T1", started_at=state.started_at,
            approver_roles=state.approver_roles, status=state.status,
        )
    return state


def record_approval(state: HitlState, role: str, action: str) -> HitlState:
    """action: 'approved' | 'rejected'. Approval after T3 must be structurally impossible,
    not just discouraged -- this is that check."""
    if state.tier == "T3" or state.status == "timed_out":
        raise ValueError("Cannot record an approval/rejection after T3 expiry -- no action was the terminal state.")
    if role not in state.approver_roles:
        raise ValueError(f"Role {role!r} is not in the eligible set {state.approver_roles} at tier {state.tier}.")
    return HitlState(
        run_id=state.run_id, tier=state.tier, started_at=state.started_at,
        approver_roles=state.approver_roles, status=action,
    )
