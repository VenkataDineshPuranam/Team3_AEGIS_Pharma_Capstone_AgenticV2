"""HITL ladder durations from failure_and_loop_guards.md SS5.

The graph does not yet enforce wall-clock expiry (P-08). The workbench still shows
the designed ladder so approvers can see time-to-next-tier. Durations here are
configuration, not a substitute for graph-side clock wiring.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Literal

HitlTier = Literal["T0", "T1", "T2", "T3"]

# Hours until each tier from interrupt (T0). Batch/Supply use a business-hours clock
# in the spec; the UI approximates with wall hours until P-08 is wired.
SLA: dict[str, dict[str, int | str]] = {
    "batch_review": {"clock": "business_hours", "t1": 8, "t2": 16, "t3": 24},
    "pv_intake": {"clock": "wall", "t1": 4, "t2": 8, "t3": 24},
    "supply_planning": {"clock": "business_hours", "t1": 8, "t2": 16, "t3": 24},
}


def ladder(workflow: str) -> dict[str, int | str]:
    return SLA.get(workflow, SLA["batch_review"])


def deadline_for_tier(created_at: datetime, workflow: str, tier: HitlTier = "T0") -> datetime:
    spec = ladder(workflow)
    hours = {"T0": spec["t1"], "T1": spec["t2"], "T2": spec["t3"], "T3": spec["t3"]}[tier]
    return created_at + timedelta(hours=int(hours))


def infer_tier(created_at: datetime, workflow: str, now: datetime | None = None) -> HitlTier:
    now = now or datetime.now(UTC)
    spec = ladder(workflow)
    elapsed = (now - created_at).total_seconds() / 3600
    if elapsed >= float(spec["t3"]):
        return "T3"
    if elapsed >= float(spec["t2"]):
        return "T2"
    if elapsed >= float(spec["t1"]):
        return "T1"
    return "T0"
