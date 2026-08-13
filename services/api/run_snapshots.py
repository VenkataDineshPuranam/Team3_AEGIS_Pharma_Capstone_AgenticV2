"""Completed-run snapshots for the workbench history and case file.

Separate from audit_store (WORM) and pending_queue (waiting HITL). Holds the
JSON case file the UI needs after the graph has finalized -- evidence, payload,
critic codes -- which agent_run does not store.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO_ROOT / "evidence" / "run_snapshots.sqlite3"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS run_snapshot (
    run_id TEXT PRIMARY KEY,
    workflow TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    status TEXT NOT NULL,
    payload TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def _connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def upsert(snapshot: dict[str, Any]) -> None:
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO run_snapshot (run_id, workflow, subject_id, status, payload, updated_at) "
        "VALUES (?, ?, ?, ?, ?, datetime('now'))",
        (
            snapshot["run_id"],
            snapshot["workflow"],
            snapshot["subject_id"],
            snapshot.get("status") or snapshot.get("terminal_state") or "unknown",
            json.dumps(snapshot),
        ),
    )
    conn.commit()
    conn.close()


def get(run_id: str) -> dict[str, Any] | None:
    conn = _connect()
    row = conn.execute("SELECT payload FROM run_snapshot WHERE run_id = ?", (run_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return json.loads(row[0])


def list_all(workflow: str | None = None, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    conn = _connect()
    clauses: list[str] = []
    params: list[Any] = []
    if workflow:
        clauses.append("workflow = ?")
        params.append(workflow)
    if status:
        clauses.append("status = ?")
        params.append(status)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = conn.execute(
        f"SELECT payload FROM run_snapshot {where} ORDER BY updated_at DESC LIMIT ?",
        (*params, limit),
    ).fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]
