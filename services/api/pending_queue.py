"""In-memory pending-approval registry -- the Approver Dashboard's queue source.

KNOWN SIMPLIFICATION, stated explicitly (same pattern as
infra/policies/denial_of_wallet_guardrail.py's own docstring): this is a module-level
dict, single-process only. It does not survive a restart and would not be correct behind
more than one API worker process. A real deployment needs a shared store (Redis, or the
audit store) for this -- not built here, because nothing in this demo build needs it to
survive a restart. This is explicitly NOT the audit trail (services/integration/
audit_store.py) -- that stays append-only and compliance-grade; this is disposable UI
state describing "what's currently waiting," rebuilt from scratch on every process start.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass
class PendingEntry:
    run_id: str
    workflow: str
    subject_id: str  # batch_id / case_id / product_id
    requester_role: str
    approver_roles: list[str]
    required_legs: list[str] | None
    approved_legs: list[str]
    draft_summary: str | None
    draft_claims: list[dict[str, Any]]
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    # Stage 21: the evidence the draft cites and the workflow's structured findings, both
    # captured from the paused run's own state at the moment it interrupted. Held here
    # rather than re-fetched later because this is precisely the state the approver is
    # being asked to judge -- re-retrieving it at render time could show a different
    # corpus than the one the run actually reasoned over.
    evidence: list[dict[str, Any]] = field(default_factory=list)
    domain_payload: dict[str, Any] | None = None


_PENDING: dict[str, PendingEntry] = {}


def add(entry: PendingEntry) -> None:
    _PENDING[entry.run_id] = entry


def get(run_id: str) -> PendingEntry | None:
    return _PENDING.get(run_id)


def remove(run_id: str) -> None:
    _PENDING.pop(run_id, None)


def update_approved_legs(run_id: str, approved_legs: list[str]) -> None:
    entry = _PENDING.get(run_id)
    if entry is not None:
        entry.approved_legs = approved_legs


def debug_backdate(run_id: str, hours_ago: float) -> PendingEntry | None:
    """Dev-only aid for exercising the hitl_timer severity tiers without waiting real
    hours. Rewrites created_at on an already-real, already-evidence-backed pending entry
    -- nothing about the run's findings, evidence, or governance state is touched, only
    the timestamp the severity badge reads. Wired to a debug-only endpoint in main.py;
    not reachable from any UI control."""
    entry = _PENDING.get(run_id)
    if entry is None:
        return None
    entry.created_at = (datetime.now(UTC) - timedelta(hours=hours_ago)).isoformat()
    return entry


def list_all(workflow: str | None = None) -> list[PendingEntry]:
    entries = list(_PENDING.values())
    if workflow:
        entries = [e for e in entries if e.workflow == workflow]
    return sorted(entries, key=lambda e: e.created_at)
