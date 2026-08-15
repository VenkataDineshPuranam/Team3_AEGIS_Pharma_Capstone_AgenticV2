"""Stage 23 -- the live HITL escalation notifier (services/integration/
hitl_escalation_watch.py), the scheduler hitl_timer.py's own docstring said did not exist.

Three properties this module has to hold, each with its own test group below:

  1. It notifies at the right moment (severity 3/T2, severity 4/T3) and not before.
  2. It notifies EXACTLY ONCE per (run_id, tier), even across many poll cycles and across
     a simulated process restart (idempotency keyed on the audit store, not memory).
  3. It never decides anything -- the run's terminal/pending status and eligible
     approvers are byte-for-byte unchanged by a scan, no matter how many times it runs.

The email side is exercised through the real degraded-mode path (no SMTP_* configured in
the test environment), matching every other optional-dependency test in this repo
(response_cache's Redis-absent tests, llm_client's missing-API-key tests) -- a scan must
never fail or skip the audit write just because mail could not be sent.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from services.api import pending_queue
from services.integration import audit_store, hitl_escalation_watch, hitl_timer


def _add_pending(run_id: str, workflow: str, hours_ago: float, **overrides) -> None:
    defaults = dict(
        subject_id=f"SUBJ-{run_id}",
        requester_role="EU Qualified Person",
        approver_roles=["EU Qualified Person"],
        required_legs=None,
        approved_legs=[],
        draft_summary=None,
        draft_claims=[],
        created_at=(datetime.now(UTC) - timedelta(hours=hours_ago)).isoformat(),
    )
    defaults.update(overrides)
    pending_queue.add(pending_queue.PendingEntry(run_id=run_id, workflow=workflow, **defaults))


@pytest.fixture(autouse=True)
def _clean_pending_queue():
    """pending_queue is a bare module-level dict (services/api/pending_queue.py's own
    stated simplification) -- clear it before and after each test so one test's entries
    can never leak into another's scan."""
    pending_queue._PENDING.clear()
    yield
    pending_queue._PENDING.clear()


@pytest.fixture
def db_path(tmp_path):
    """An isolated audit-store file, not audit_store.py's shared dev database.
    scan_once() writes real rows and keys idempotency against exactly those rows -- run it
    against the shared file and a fixed run_id like "R-t2" would find itself already
    "notified" by a previous test session and go silent, a false negative rather than a
    passing test."""
    return tmp_path / "audit_store.sqlite3"


@pytest.fixture
def scan(db_path):
    return lambda **kwargs: hitl_escalation_watch.scan_once(db_path=db_path, **kwargs)


# batch_review's ladder (hitl_timer.WORKFLOW_LADDER_HOURS): 8h/16h/24h -- T2 starts at 16h,
# T3 at 24h.
_T0_HOURS = 1
_T2_HOURS = 17
_T3_HOURS = 25


# --- 1. fires at the right moment, not before ---------------------------------


def test_a_fresh_run_does_not_notify(scan):
    _add_pending("R-fresh", "batch_review", _T0_HOURS)
    assert scan() == []


def test_a_run_at_t2_fires_exactly_one_notice(scan):
    _add_pending("R-t2", "batch_review", _T2_HOURS)
    fired = scan()

    assert len(fired) == 1
    assert fired[0].run_id == "R-t2"
    assert fired[0].tier == "T2"
    assert fired[0].severity == 3


def test_a_run_at_t3_fires_at_t3_not_t2(scan):
    _add_pending("R-t3", "batch_review", _T3_HOURS)
    fired = scan()

    assert len(fired) == 1
    assert fired[0].tier == "T3"
    assert fired[0].severity == 4


def test_a_decided_or_absent_run_is_simply_not_in_the_scan(scan):
    """No pending entries at all -- the common case most polls will find."""
    assert scan() == []


def test_pv_intakes_shorter_ladder_is_respected(scan):
    """4h/8h/24h for pv_intake -- 9h (which is only T1 for batch_review) is already past
    pv_intake's own T2 threshold (8h), so this is really asserting the watcher defers
    entirely to hitl_timer.compute rather than hardcoding batch_review's numbers."""
    _add_pending("R-pv-t2", "pv_intake", 9)
    fired = scan()
    assert len(fired) == 1
    assert fired[0].tier == "T2"


# --- 2. idempotent: exactly once per (run_id, tier) ---------------------------


def test_repeated_scans_of_the_same_run_notify_only_once(scan):
    _add_pending("R-repeat", "batch_review", _T2_HOURS)

    first = scan()
    second = scan()
    third = scan()

    assert len(first) == 1
    assert second == []
    assert third == []


def test_idempotency_survives_a_simulated_process_restart(scan, db_path):
    """The check is keyed against the audit store, not an in-memory set -- this is what
    that buys: a fresh `scan()` call (nothing about the module's own state carries forward
    between calls either) still recognizes the run was already notified, because the
    record is durable, not held in a variable that a restart would wipe."""
    _add_pending("R-restart", "batch_review", _T2_HOURS)
    scan()

    conn = audit_store.get_connection(db_path)
    try:
        already = audit_store.has_hitl_escalation(conn, "R-restart", "T2")
    finally:
        conn.close()
    assert already is True

    assert scan() == []


def test_a_run_can_notify_twice_total_once_at_each_distinct_tier(scan):
    """T2 then (later) T3 are two different facts, not a repeat of one -- both should
    reach the operator."""
    _add_pending("R-progress", "batch_review", _T2_HOURS)
    first = scan()
    assert [n.tier for n in first] == ["T2"]

    entry = pending_queue.get("R-progress")
    entry.created_at = (datetime.now(UTC) - timedelta(hours=_T3_HOURS)).isoformat()
    second = scan()
    assert [n.tier for n in second] == ["T3"]


def test_multiple_pending_runs_are_each_scanned_independently(scan):
    _add_pending("R-multi-1", "batch_review", _T2_HOURS)
    _add_pending("R-multi-2", "pv_intake", _T0_HOURS)
    _add_pending("R-multi-3", "supply_planning", _T3_HOURS)

    fired = scan()
    fired_by_id = {n.run_id: n.tier for n in fired}

    assert fired_by_id == {"R-multi-1": "T2", "R-multi-3": "T3"}


# --- 3. never decides anything -------------------------------------------------


def test_scanning_never_removes_a_run_from_the_pending_queue(scan):
    _add_pending("R-t3-still-pending", "batch_review", _T3_HOURS)
    scan()
    scan()

    assert pending_queue.get("R-t3-still-pending") is not None


def test_scanning_never_changes_who_may_approve(scan):
    """BC-12 restated as a check: reaching T3 (would-be timeout) must not widen the
    approver set. hitl_route.py's own ESCALATION_ROLE widening is a separate, unwired
    state machine this module does not touch."""
    _add_pending("R-t3-approvers", "batch_review", _T3_HOURS, approver_roles=["EU Qualified Person"])
    scan()

    entry = pending_queue.get("R-t3-approvers")
    assert entry.approver_roles == ["EU Qualified Person"]


def test_the_audit_record_is_written_even_though_no_smtp_is_configured(scan, db_path, monkeypatch):
    """The durable half (audit write) must not depend on the best-effort half (email)
    succeeding -- this is the test that proves that ordering. No SMTP_* env vars are set
    in this test environment, so notifier.send_email is expected to raise
    EmailNotConfigured on every call; the scan must swallow it and still record."""
    for var in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "NOTIFY_EMAIL_TO"):
        monkeypatch.delenv(var, raising=False)

    _add_pending("R-no-smtp", "batch_review", _T2_HOURS)
    fired = scan()

    assert len(fired) == 1
    conn = audit_store.get_connection(db_path)
    try:
        assert audit_store.has_hitl_escalation(conn, "R-no-smtp", "T2") is True
    finally:
        conn.close()


def test_a_severity_2_run_is_display_only_matching_the_ui_badge(scan):
    """Severity 1-2 (T0/T1) is the Decision Queue's grey/amber -- "normal waiting," not
    yet urgent. This asserts the watcher's own threshold agrees with hitl_timer's tier
    labels rather than picking a different cutoff by coincidence."""
    hours_for_t1 = 9  # batch_review: T1 starts at 8h, T2 at 16h
    _add_pending("R-t1", "batch_review", hours_for_t1)
    timer = hitl_timer.compute(pending_queue.get("R-t1").created_at, "batch_review")
    assert timer.severity == 2  # sanity: this really is T1, not accidentally T2

    assert scan() == []
