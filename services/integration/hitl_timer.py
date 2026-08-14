"""hitl_timer -- computes the SAME tier concept hitl_route.py already defines
(T0/T1/T2/T3), but as a pure, read-time function over `created_at` rather than mutated
graph state.

Why this exists separately from hitl_route.resolve_tier: that function is Batch Review's
own escalation-ladder state machine, wired into nothing (no scheduler advances it -- see
the finding this module closes). This module answers a narrower, purely presentational
question -- "how severe does this wait look right now" -- for EVERY workflow's queue
entry and run detail, recomputed fresh on each request (the Decision Queue already polls
every 10s, so this is naturally live without adding a background job or notification
channel, neither of which exists in this build).

SCOPE, stated plainly: this is DISPLAY ONLY. Reaching T2 here does not change who is
authorized to decide a run -- user_store.approver_string_for is unchanged. Actually
widening approver eligibility at T2 (the "escalate to another approver" half of the
original ask) is a real RBAC change, deliberately not made in this pass.

THRESHOLDS -- per-workflow, not uniform. `docs/governance/hitl_control_model.md` SS7
already specifies distinct ladders for the three original workflows, confirmed against
each role's stated authority:
  - Batch Review:      8h / 16h / 24h  (business-hours clock, approximated as wall-clock)
  - PV Intake:          4h / 8h / 24h  (deliberately shorter -- a real regulatory
                                        reporting clock is at stake, per the Global Head
                                        of PV's own stated concern about "clock errors")
  - Supply Planning:    8h / 16h / 24h (Quality co-approval leg; matches Batch Review)
An earlier version of this module used the Batch Review numbers for all six workflows,
which silently understated PV Intake's urgency (a PV run reads "on time" for twice as
long as SS7 intends). Fixed here. research_review/clinical_integrity/
regulatory_completeness have no ladder specified anywhere in the governance docs (they
postdate hitl_control_model.md) -- they fall back to the Batch Review numbers as the
closest documented analog, stated as an explicit assumption, not a researched duration.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

# (T1 reminder, T2 escalation, T3 expiry), in hours -- hitl_control_model.md SS7.
_DEFAULT_LADDER = (8, 16, 24)
WORKFLOW_LADDER_HOURS: dict[str, tuple[float, float, float]] = {
    "batch_review": (8, 16, 24),
    "pv_intake": (4, 8, 24),
    "supply_planning": (8, 16, 24),
    # Not specified in hitl_control_model.md -- these three workflows postdate it.
    # Falling back to the Batch Review ladder as the closest documented analog.
    "research_review": _DEFAULT_LADDER,
    "clinical_integrity": _DEFAULT_LADDER,
    "regulatory_completeness": _DEFAULT_LADDER,
}

TIER_LABEL = {
    "T0": "On time",
    "T1": "Reminder due",
    "T2": "Escalation due",
    "T3": "Expired",
}

# Severity scale, 1 (lowest) to 4 (highest) -- 1:1 with the tier, expressed as a number
# because "severity 4" reads faster at a glance across a queue than "T3" does.
TIER_SEVERITY = {"T0": 1, "T1": 2, "T2": 3, "T3": 4}


@dataclass(frozen=True)
class HitlTimer:
    tier: str  # T0 | T1 | T2 | T3
    label: str
    severity: int  # 1 (lowest) .. 4 (highest / red)
    hours_elapsed: float
    hours_to_next_tier: float | None  # None once at T3 -- there is no next tier


def compute(created_at: str, workflow: str, now: datetime | None = None) -> HitlTimer:
    t1_hours, t2_hours, t3_hours = WORKFLOW_LADDER_HOURS.get(workflow, _DEFAULT_LADDER)

    started = datetime.fromisoformat(created_at)
    if started.tzinfo is None:
        started = started.replace(tzinfo=UTC)
    now = now or datetime.now(UTC)
    elapsed = now - started
    hours_elapsed = elapsed.total_seconds() / 3600

    if elapsed >= timedelta(hours=t3_hours):
        tier, hours_to_next_tier = "T3", None
    elif elapsed >= timedelta(hours=t2_hours):
        tier, hours_to_next_tier = "T2", t3_hours - hours_elapsed
    elif elapsed >= timedelta(hours=t1_hours):
        tier, hours_to_next_tier = "T1", t2_hours - hours_elapsed
    else:
        tier, hours_to_next_tier = "T0", t1_hours - hours_elapsed

    return HitlTimer(
        tier=tier, label=TIER_LABEL[tier], severity=TIER_SEVERITY[tier],
        hours_elapsed=hours_elapsed, hours_to_next_tier=hours_to_next_tier,
    )
