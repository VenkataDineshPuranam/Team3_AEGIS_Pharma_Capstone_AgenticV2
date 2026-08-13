"""Pending-approval registry for the Approver Workbench.

KNOWN SIMPLIFICATION vs a multi-worker deployment: SQLite file, not Redis. Survives
process restart (the previous in-memory dict did not). This is NOT the audit trail --
audit_store.py remains append-only. Rows here are disposable UI state describing
"what is currently waiting" and are deleted when the run leaves HITL.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO_ROOT / "evidence" / "pending_queue.sqlite3"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS pending (
    run_id TEXT PRIMARY KEY,
    workflow TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload TEXT NOT NULL
);
"""


def _connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


@dataclass
class PendingEntry:
    run_id: str
    workflow: str
    subject_id: str
    requester_role: str
    approver_roles: list[str]
    required_legs: list[str] | None
    approved_legs: list[str]
    draft_summary: str | None
    draft_claims: list[dict[str, Any]]
    created_at: str
    snapshot: dict[str, Any]


def add(entry: PendingEntry) -> None:
    payload = {
        "requester_role": entry.requester_role,
        "approver_roles": entry.approver_roles,
        "required_legs": entry.required_legs,
        "approved_legs": entry.approved_legs,
        "draft_summary": entry.draft_summary,
        "draft_claims": entry.draft_claims,
        "snapshot": entry.snapshot,
    }
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO pending (run_id, workflow, subject_id, created_at, payload) VALUES (?, ?, ?, ?, ?)",
        (entry.run_id, entry.workflow, entry.subject_id, entry.created_at, json.dumps(payload)),
    )
    conn.commit()
    conn.close()


def get(run_id: str) -> PendingEntry | None:
    conn = _connect()
    row = conn.execute(
        "SELECT run_id, workflow, subject_id, created_at, payload FROM pending WHERE run_id = ?",
        (run_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return _row_to_entry(row)


def remove(run_id: str) -> None:
    conn = _connect()
    conn.execute("DELETE FROM pending WHERE run_id = ?", (run_id,))
    conn.commit()
    conn.close()


def update_approved_legs(run_id: str, approved_legs: list[str]) -> None:
    entry = get(run_id)
    if entry is None:
        return
    entry.approved_legs = approved_legs
    entry.snapshot["approved_legs"] = approved_legs
    add(entry)


def update_snapshot(run_id: str, snapshot: dict[str, Any]) -> None:
    entry = get(run_id)
    if entry is None:
        return
    entry.snapshot = snapshot
    entry.approved_legs = list(snapshot.get("approved_legs") or entry.approved_legs)
    entry.draft_summary = snapshot.get("draft_summary", entry.draft_summary)
    add(entry)


def list_all(workflow: str | None = None) -> list[PendingEntry]:
    conn = _connect()
    if workflow:
        rows = conn.execute(
            "SELECT run_id, workflow, subject_id, created_at, payload FROM pending WHERE workflow = ? ORDER BY created_at",
            (workflow,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT run_id, workflow, subject_id, created_at, payload FROM pending ORDER BY created_at"
        ).fetchall()
    conn.close()
    return [_row_to_entry(r) for r in rows]


def _row_to_entry(row: tuple) -> PendingEntry:
    run_id, workflow, subject_id, created_at, payload_raw = row
    payload = json.loads(payload_raw)
    snapshot = payload.get("snapshot") or {}
    return PendingEntry(
        run_id=run_id,
        workflow=workflow,
        subject_id=subject_id,
        requester_role=payload.get("requester_role") or "",
        approver_roles=list(payload.get("approver_roles") or []),
        required_legs=payload.get("required_legs"),
        approved_legs=list(payload.get("approved_legs") or []),
        draft_summary=payload.get("draft_summary"),
        draft_claims=list(payload.get("draft_claims") or []),
        created_at=created_at,
        snapshot=snapshot,
    )


def now_iso() -> str:
    return datetime.now(UTC).isoformat()
