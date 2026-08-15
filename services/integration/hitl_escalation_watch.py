"""hitl_escalation_watch -- Stage 23. The scheduler hitl_timer.py's own docstring says
does not exist: "no scheduler advances it -- see the finding this module closes."

WHAT THIS CLOSES, AND HOW FAR
------------------------------
hitl_timer.compute() already turns elapsed time into a severity (1-4) on every read --
the Decision Queue polls it every 10s, so the badge in the UI was already live. What was
missing was anyone being TOLD without having the page open: a run could sit at severity 4
overnight with nobody paged. This module is the poller (services/api/main.py's lifespan
runs it on an interval) that watches pending runs, and the moment one first crosses into
severity 3 (T2, "escalation due") or severity 4 (T3, "expired"), fires a notification --
an audit-store record any client can read (services/api/main.py's
GET /api/notifications, the web app's bell) plus a best-effort email via notifier.py.

WHAT THIS DOES NOT DO -- stated as plainly as hitl_timer.py states its own scope, because
the same boundary matters here for the same reason:

  This module NEVER decides a run. It cannot approve, reject, veto, widen who may
  approve, or advance any workflow's graph. BC-12 ("timeout => no action, ever") is
  unaffected -- reaching severity 4 here still does not authorize anyone new, still does
  not auto-resolve the run, still does not touch hitl_route.py's ESCALATION_ROLE
  widening. It only makes an already-true fact (this run has been waiting a long time)
  visible to a human who was not already looking at the screen. That is the entire
  feature.

IDEMPOTENCY
------------
Each (run_id, tier) fires at most once, enforced by audit_store.has_hitl_escalation --
checked against the append-only store itself, not an in-memory set, so a run that has
already been notified at T2 stays notified across an API process restart. A run can still
fire twice total over its lifetime: once at T2, once (later) at T3 -- two genuinely
different facts, not a repeat of the same one.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from services.api import pending_queue
from services.integration import audit_store, hitl_timer, notifier

logger = logging.getLogger(__name__)

#: Severities at or above this fire a notification. 3 = T2 ("escalation due"), 4 = T3
#: ("expired"/red) -- severities 1-2 (T0/T1) are normal, not-yet-urgent waiting and stay
#: silent, matching the Decision Queue's own colour ladder (grey/amber vs purple/red).
NOTIFY_AT_OR_ABOVE_SEVERITY = 3

_SEVERITY_TO_TIER = {3: "T2", 4: "T3"}


@dataclass(frozen=True)
class EscalationNotice:
    run_id: str
    workflow: str
    subject_id: str
    tier: str
    severity: int
    approver_roles: tuple[str, ...]
    hours_elapsed: float


def _build_email(notice: EscalationNotice) -> tuple[str, str]:
    label = hitl_timer.TIER_LABEL[notice.tier]
    subject = f"[AEGIS] {label}: {notice.workflow} {notice.subject_id} ({notice.run_id})"
    approvers = ", ".join(notice.approver_roles) if notice.approver_roles else "no eligible approver on file"
    body = (
        f"A pending decision has reached {label.upper()} (severity {notice.severity}/4).\n\n"
        f"Run:        {notice.run_id}\n"
        f"Workflow:   {notice.workflow}\n"
        f"Subject:    {notice.subject_id}\n"
        f"Waiting on: {approvers}\n"
        f"Elapsed:    {notice.hours_elapsed:.1f} hours\n\n"
        "This is a visibility notice only. It does not authorize any new approver and "
        "does not decide this run -- no part of this system will. A human still has to "
        "open it and record a decision.\n"
    )
    return subject, body


def scan_once(*, now: datetime | None = None, db_path: Path | None = None) -> list[EscalationNotice]:
    """One pass over the pending queue. Returns the notices that were newly fired this
    pass (empty most of the time -- most polls find nothing has just crossed a threshold).

    Never raises for an email failure: a run reaching severity 4 must be recorded and
    shown in the app regardless of whether SMTP happens to be configured or reachable
    right now, the same ADR-007 posture response_cache.py takes toward a Redis outage.
    The audit write happens before the email attempt for exactly this reason -- the
    durable half of "notified" cannot be skipped by the best-effort half failing.

    `db_path` defaults to audit_store's own DEFAULT_DB_PATH (the real, shared audit
    store) -- passed through only so tests can point this at an isolated tmp_path file,
    the same knob audit_store.get_connection already exposes. The live background loop
    in services/api/main.py never passes it.
    """
    now = now or datetime.now(UTC)
    fired: list[EscalationNotice] = []

    conn = audit_store.get_connection(db_path) if db_path else audit_store.get_connection()
    try:
        for entry in pending_queue.list_all():
            timer = hitl_timer.compute(entry.created_at, entry.workflow, now=now)
            if timer.severity < NOTIFY_AT_OR_ABOVE_SEVERITY:
                continue
            tier = _SEVERITY_TO_TIER.get(timer.severity, timer.tier)
            if audit_store.has_hitl_escalation(conn, entry.run_id, tier):
                continue

            notice = EscalationNotice(
                run_id=entry.run_id, workflow=entry.workflow, subject_id=entry.subject_id,
                tier=tier, severity=timer.severity, approver_roles=tuple(entry.approver_roles),
                hours_elapsed=timer.hours_elapsed,
            )

            audit_store.write_hitl_escalation(
                conn, run_id=entry.run_id, workflow=entry.workflow,
                evaluated_at=now.isoformat(), tier=tier,
                conditions={"severity": timer.severity, "hours_elapsed": round(timer.hours_elapsed, 2)},
                outcome="notified",
                escalation_role=entry.approver_roles[0] if entry.approver_roles else None,
            )

            try:
                subject, body = _build_email(notice)
                notifier.send_email(subject, body)
            except Exception as exc:  # noqa: BLE001 -- ADR-007: never fail the scan over mail
                logger.warning("hitl_escalation_watch: email not sent for %s: %s", entry.run_id, exc)

            fired.append(notice)
            logger.info(
                "hitl_escalation_watch: %s %s (%s) reached %s (severity %d)",
                entry.workflow, entry.subject_id, entry.run_id, tier, timer.severity,
            )
    finally:
        conn.close()

    return fired
