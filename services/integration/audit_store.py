"""audit_store -- Stage 20a Phase 3. SQLite, append-only. Emulates the WORM property
locally (ADR-009's real Blob WORM immutability is a Stage 20 deploy concern) by exposing
no UPDATE/DELETE at the data-access layer -- there is no function in this module that can
modify or remove an existing row, which is the actual enforcement, not a comment promising
one.

Record shapes from escalation_override_log_design.md SS2-5: AgentRun, HumanOverrideRecorded,
HitlEscalation, HitlExpired. `finalize` (langgraph_design.md node #11) writes AgentRun before
any response reaches the caller -- ADR-006.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO_ROOT / "evidence" / "audit_store.sqlite3"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_run (
    run_id TEXT PRIMARY KEY,
    workflow TEXT NOT NULL,
    terminal_state TEXT NOT NULL,
    abstention_reason TEXT,
    trace_id TEXT,
    policy_contract_version TEXT,
    recorded_at TEXT NOT NULL,
    llm_calls INTEGER,
    tokens_in INTEGER,
    tokens_out INTEGER
);

CREATE TABLE IF NOT EXISTS human_override_recorded (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    role TEXT NOT NULL,
    role_assignment_id TEXT,
    tier_at_action TEXT NOT NULL,
    action TEXT NOT NULL,
    justification TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hitl_escalation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    workflow TEXT NOT NULL,
    tier TEXT NOT NULL,
    evaluated_at TEXT NOT NULL,
    conditions TEXT NOT NULL,
    outcome TEXT NOT NULL,
    skip_reason TEXT,
    escalation_role TEXT,
    policy_contract_version TEXT
);

CREATE TABLE IF NOT EXISTS hitl_expired (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    workflow TEXT NOT NULL,
    eligible_roles_at_expiry TEXT NOT NULL,
    abstention_reason TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prohibited_action_blocked (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    matched_terms TEXT NOT NULL,
    draft_sha256 TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);
"""


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(_SCHEMA)
    _migrate(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Stage 20b Phase 6: agent_run predates llm_calls/tokens_in/tokens_out (added to
    make the Stage 17 dashboards panels computable from real data). CREATE TABLE IF NOT
    EXISTS doesn't add columns to an already-existing table -- this does, idempotently."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(agent_run)")}
    for column in ("llm_calls", "tokens_in", "tokens_out"):
        if column not in existing:
            conn.execute(f"ALTER TABLE agent_run ADD COLUMN {column} INTEGER")
    conn.commit()


def write_agent_run(
    conn: sqlite3.Connection,
    run_id: str,
    workflow: str,
    terminal_state: str,
    recorded_at: str,
    abstention_reason: str | None = None,
    trace_id: str | None = None,
    policy_contract_version: str | None = None,
    llm_calls: int | None = None,
    tokens_in: int | None = None,
    tokens_out: int | None = None,
) -> None:
    """finalize's mandatory write -- a response reaching the caller with no audit write
    is not a valid terminal state (hooks.md). llm_calls/tokens_in/tokens_out (Stage 20b)
    are what makes dashboards.md's Cost panel computable from real data."""
    conn.execute(
        "INSERT INTO agent_run (run_id, workflow, terminal_state, abstention_reason, trace_id, policy_contract_version, recorded_at, llm_calls, tokens_in, tokens_out) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, workflow, terminal_state, abstention_reason, trace_id, policy_contract_version, recorded_at, llm_calls, tokens_in, tokens_out),
    )
    conn.commit()


def write_human_override(
    conn: sqlite3.Connection,
    run_id: str,
    role: str,
    tier_at_action: str,
    action: str,
    justification: str,
    recorded_at: str,
    role_assignment_id: str | None = None,
) -> None:
    if not justification.strip():
        raise ValueError("justification is required and cannot be empty -- escalation_override_log_design.md SS3.")
    if action == "approved" and has_veto(conn, run_id):
        raise ValueError(
            "A veto_registered record already exists for this run_id -- escalation_override_log_design.md SS4: "
            "a veto cannot be superseded by a later approval."
        )
    conn.execute(
        "INSERT INTO human_override_recorded (run_id, role, role_assignment_id, tier_at_action, action, justification, recorded_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (run_id, role, role_assignment_id, tier_at_action, action, justification, recorded_at),
    )
    conn.commit()


def has_veto(conn: sqlite3.Connection, run_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM human_override_recorded WHERE run_id = ? AND action = 'veto_registered' LIMIT 1",
        (run_id,),
    ).fetchone()
    return row is not None


def write_hitl_escalation(
    conn: sqlite3.Connection,
    run_id: str,
    workflow: str,
    evaluated_at: str,
    conditions: dict[str, bool],
    outcome: str,
    skip_reason: str | None = None,
    escalation_role: str | None = None,
    policy_contract_version: str | None = None,
) -> None:
    conn.execute(
        "INSERT INTO hitl_escalation (run_id, workflow, tier, evaluated_at, conditions, outcome, skip_reason, escalation_role, policy_contract_version) "
        "VALUES (?, ?, 'T2', ?, ?, ?, ?, ?, ?)",
        (run_id, workflow, evaluated_at, json.dumps(conditions), outcome, skip_reason, escalation_role, policy_contract_version),
    )
    conn.commit()


def write_hitl_expired(
    conn: sqlite3.Connection,
    run_id: str,
    workflow: str,
    eligible_roles_at_expiry: list[str],
    recorded_at: str,
) -> None:
    conn.execute(
        "INSERT INTO hitl_expired (run_id, workflow, eligible_roles_at_expiry, abstention_reason, recorded_at) "
        "VALUES (?, ?, ?, 'hitl_timeout', ?)",
        (run_id, workflow, json.dumps(eligible_roles_at_expiry), recorded_at),
    )
    conn.commit()
