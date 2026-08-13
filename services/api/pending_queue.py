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
from datetime import UTC, datetime
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


def list_all(workflow: str | None = None) -> list[PendingEntry]:
    entries = list(_PENDING.values())
    if workflow:
        entries = [e for e in entries if e.workflow == workflow]
    return sorted(entries, key=lambda e: e.created_at)
