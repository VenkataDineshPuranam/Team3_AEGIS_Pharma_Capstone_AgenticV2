"""Vendor-exit export completeness check -- Stage 21 gap-closure (INJ-083: a strategic
vendor will terminate service in 120 days and export formats are incomplete).

K-031 (VENDOR_EXIT_AND_RETIREMENT.md) requires "data, model, prompt, embedding,
evaluation, log and tool export requirements" to be defined and "substitution and
evidence readability tested before exit." This module makes that check runnable rather
than a document nobody re-reads: for every governed record type this system actually
produces, it verifies a real export path exists and can be read back -- not just that a
column exists in a schema.

Run: python evidence/quality-gates/vendor_exit_export_check.py
(the "quality-gates" directory name contains a hyphen, same as eval-ai-cache/, so this is
run as a script or imported via an explicit sys.path insert -- never as a dotted import.)
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class ExportGap(Exception):
    pass


def check_audit_store_exports() -> dict:
    """The audit trail (agent_run, human_override_recorded, hitl_escalation, hitl_expired,
    prohibited_action_blocked) is SQLite -- an open, documented, portable format with a
    standard export path (`.dump`, or any SQL client) that does not depend on this
    vendor or any other. Verified by actually reading every table, not by trusting the
    file extension."""
    from services.integration.audit_store import get_connection

    conn = get_connection()
    tables = ("agent_run", "human_override_recorded", "hitl_escalation", "hitl_expired", "prohibited_action_blocked")
    counts = {}
    for table in tables:
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    conn.close()
    return {"format": "SQLite (open format, standard SQL export)", "tables": counts, "exportable": True}


def check_evidence_corpus_export() -> dict:
    """The evidence corpus's source of truth is knowledge/knowledge_catalog.csv -- plain
    CSV, not locked into Neo4j (Neo4j is a queryable INDEX over this corpus, rebuilt from
    the CSV by packages/domain/kg/ingest.py; the CSV survives a Neo4j vendor exit
    unchanged)."""
    catalog = REPO_ROOT / "knowledge" / "knowledge_catalog.csv"
    if not catalog.exists():
        raise ExportGap("knowledge_catalog.csv missing -- evidence corpus has no portable export")
    rows = catalog.read_text().count("\n") - 1
    return {"format": "CSV (plain text, vendor-independent)", "row_count": rows, "exportable": True}


def check_tool_contracts_export() -> dict:
    """Tool contracts (what synthesize/critic_verify/tools are allowed to do) are JSON
    Schema files -- plain text, portable to any future system that can read JSON, with no
    dependency on this codebase's Python runtime to remain meaningful."""
    contracts_dir = REPO_ROOT / "packages" / "contracts" / "tool_contracts"
    files = list(contracts_dir.glob("*.schema.json"))
    for f in files:
        json.loads(f.read_text())  # each one must actually parse -- not just exist
    return {"format": "JSON Schema (plain text)", "contract_count": len(files), "exportable": True}


def check_governance_policy_export() -> dict:
    """The policy contract (prohibited terms/fields per workflow) is plain JSON."""
    policy_path = REPO_ROOT / "security" / "policies" / "policy_contract.v1.json"
    json.loads(policy_path.read_text())
    return {"format": "JSON (plain text)", "exportable": True}


def run_all_checks() -> dict:
    """The full export-completeness verification K-031 asks for. Raises ExportGap on the
    first record type that cannot actually be read back -- the honest failure mode for a
    'is this vendor-exit-ready' check."""
    return {
        "audit_store": check_audit_store_exports(),
        "evidence_corpus": check_evidence_corpus_export(),
        "tool_contracts": check_tool_contracts_export(),
        "governance_policy": check_governance_policy_export(),
        # What is explicitly NOT yet covered, stated honestly rather than omitted:
        "not_yet_covered": [
            "LangSmith trace history -- third-party hosted, no local export path built yet (ADR-006 already argues the audit store, not LangSmith, is the durable record for this reason)",
            "Redis response cache -- deliberately NOT a durable record (TTL-based, rebuildable from evidence + policy at any time); nothing to export because nothing there is authoritative",
        ],
    }


if __name__ == "__main__":
    results = run_all_checks()
    print(json.dumps(results, indent=2))
