"""Stage 21 -- the audit store's read side, and the WORM property it must not weaken.

Readers were added so the audit trail can answer questions about a specific run rather
than only aggregate counts. The store's guarantee is that no function in the module can
modify or remove a row; these tests assert that adding readers left it intact.
"""
import sqlite3
from datetime import UTC, datetime

import pytest

from services.integration import audit_store


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.executescript(audit_store._SCHEMA)
    yield connection
    connection.close()


def _write(conn, run_id, workflow="batch_review", terminal="completed", **kw):
    audit_store.write_agent_run(
        conn, run_id, workflow, terminal, datetime.now(UTC).isoformat(), **kw
    )


def test_read_layer_adds_no_mutating_function():
    """The module docstring's claim -- 'there is no function in this module that can
    modify or remove an existing row' -- restated as a check, so a future UPDATE helper
    added for convenience fails here rather than passing review."""
    source = (audit_store.__file__)
    with open(source) as f:
        body = f.read().upper()
    assert "UPDATE AGENT_RUN" not in body
    assert "DELETE FROM" not in body
    assert " DROP TABLE" not in body


def test_list_runs_is_newest_first_and_paginates():
    conn = sqlite3.connect(":memory:")
    conn.executescript(audit_store._SCHEMA)
    for i in range(5):
        audit_store.write_agent_run(
            conn, f"R-{i}", "batch_review", "completed", f"2026-01-0{i + 1}T00:00:00+00:00"
        )
    rows, total = audit_store.list_agent_runs(conn, limit=2, offset=0)
    assert total == 5
    assert [r["run_id"] for r in rows] == ["R-4", "R-3"]
    rows2, _ = audit_store.list_agent_runs(conn, limit=2, offset=2)
    assert [r["run_id"] for r in rows2] == ["R-2", "R-1"]
    conn.close()


def test_filters_narrow_by_workflow_and_terminal_state(conn):
    _write(conn, "R-a", workflow="pv_intake", terminal="completed")
    _write(conn, "R-b", workflow="batch_review", terminal="blocked")
    _write(conn, "R-c", workflow="batch_review", terminal="completed")

    rows, total = audit_store.list_agent_runs(conn, workflow="batch_review")
    assert total == 2 and {r["run_id"] for r in rows} == {"R-b", "R-c"}

    rows, total = audit_store.list_agent_runs(conn, terminal_state="blocked")
    assert total == 1 and rows[0]["run_id"] == "R-b"


def test_search_matches_run_id_and_subject_id_only(conn):
    _write(conn, "R-alpha", subject_id="B-001")
    _write(conn, "R-beta", subject_id="B-002", trace_id="TR-secret")

    rows, _ = audit_store.list_agent_runs(conn, search="alpha")
    assert [r["run_id"] for r in rows] == ["R-alpha"]

    rows, _ = audit_store.list_agent_runs(conn, search="b-002")
    assert [r["run_id"] for r in rows] == ["R-beta"]

    # trace_id is not a searchable field -- a caller must not be able to probe columns it
    # was given no filter for.
    rows, _ = audit_store.list_agent_runs(conn, search="secret")
    assert rows == []


def test_distinct_values_rejects_a_column_not_on_the_allowlist(conn):
    """The column name reaches SQL. An allowlist is the control; this is the test that
    the control exists rather than the docstring promising one."""
    assert audit_store.distinct_values(conn, "workflow") == []
    with pytest.raises(ValueError):
        audit_store.distinct_values(conn, "trace_id")
    with pytest.raises(ValueError):
        audit_store.distinct_values(conn, "workflow; DROP TABLE agent_run--")


def test_columns_absent_before_the_migration_read_as_none_not_as_empty(conn):
    """A run recorded before Stage 21 has no evidence_ids. That must arrive as None so the
    UI can say 'not recorded', never as [] which reads as 'this run used no evidence'."""
    _write(conn, "R-old")
    record = audit_store.get_agent_run(conn, "R-old")
    assert record["evidence_ids"] is None
    assert record["approver_roles"] is None
    assert record["subject_id"] is None


def test_recorded_context_round_trips(conn):
    _write(
        conn, "R-new", subject_id="B-007", requester_role="EU Qualified Person",
        approver_roles=["EU Qualified Person"], hitl_status="approved",
        evidence_ids=["K-006", "K-011"],
    )
    record = audit_store.get_agent_run(conn, "R-new")
    assert record["subject_id"] == "B-007"
    assert record["approver_roles"] == ["EU Qualified Person"]
    assert record["evidence_ids"] == ["K-006", "K-011"]


def test_timeline_merges_every_record_type_in_time_order(conn):
    _write(conn, "R-t")
    audit_store.write_human_override(
        conn, "R-t", role="EU Qualified Person", tier_at_action="T0", action="approved",
        justification="Reconciled against K-006.", recorded_at="2026-01-01T10:00:00+00:00",
    )
    audit_store.write_hitl_expired(
        conn, "R-t", "batch_review", ["EU Qualified Person"], "2026-01-01T09:00:00+00:00"
    )
    timeline = audit_store.run_timeline(conn, "R-t")
    types = [e["event_type"] for e in timeline]
    assert "HumanOverrideRecorded" in types and "HitlExpired" in types and "AgentRun" in types
    assert timeline == sorted(timeline, key=lambda e: e["at"])


def test_timeline_invents_nothing_for_a_run_with_only_one_record(conn):
    """Real events only. A run that was refused at intake has exactly one audit record,
    and the timeline must show one event -- not a plausible-looking reconstruction of the
    node-level steps that never got written here."""
    _write(conn, "R-refused", terminal="refused")
    timeline = audit_store.run_timeline(conn, "R-refused")
    assert len(timeline) == 1
    assert timeline[0]["event_type"] == "AgentRun"


def test_timeline_of_an_unknown_run_is_empty_not_an_error(conn):
    assert audit_store.run_timeline(conn, "R-does-not-exist") == []


def test_human_overrides_expose_the_real_justification(conn):
    audit_store.write_human_override(
        conn, "R-j", role="Global Head of Pharmacovigilance", tier_at_action="T0",
        action="rejected", justification="Duplicate of PV-001; reporting clock unresolved.",
        recorded_at=datetime.now(UTC).isoformat(),
    )
    actions = audit_store.human_overrides(conn, "R-j")
    assert actions[0]["justification"] == "Duplicate of PV-001; reporting clock unresolved."


def test_veto_still_cannot_be_overridden_by_a_later_approval(conn):
    """Pre-existing guarantee (escalation_override_log_design.md SS4), re-asserted here
    because Stage 21 changed what flows INTO this function. The write-time check is what
    enforces it, and it must not have become reachable-around."""
    audit_store.write_human_override(
        conn, "R-v", role="Patient Safety Representative", tier_at_action="T0",
        action="veto_registered", justification="Patient safety concern stands.",
        recorded_at=datetime.now(UTC).isoformat(),
    )
    with pytest.raises(ValueError, match="veto"):
        audit_store.write_human_override(
            conn, "R-v", role="Global Head of Pharmacovigilance", tier_at_action="T0",
            action="approved", justification="Overriding the veto.",
            recorded_at=datetime.now(UTC).isoformat(),
        )


def test_store_stats_counts_every_table(conn):
    _write(conn, "R-s")
    stats = audit_store.store_stats(conn)
    assert stats["row_counts"]["agent_run"] == 1
    assert set(stats["row_counts"]) == {
        "agent_run", "human_override_recorded", "hitl_escalation", "hitl_expired",
        "prohibited_action_blocked",
    }
