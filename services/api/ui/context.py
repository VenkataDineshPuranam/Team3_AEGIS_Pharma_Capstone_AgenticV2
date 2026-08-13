"""Shared labels, roles, and view helpers for the HTMX workbench."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

WORKFLOW_LABEL = {
    "batch_review": "GxP Batch Review",
    "pv_intake": "PV Intake",
    "supply_planning": "Supply Planning",
}
WORKFLOW_SHORT = {
    "batch_review": "Batch",
    "pv_intake": "PV",
    "supply_planning": "Supply",
}
PROHIBITIONS = {
    "batch_review": [
        "Release a batch",
        "Reject a batch",
        "Reprocess",
        "Relabel",
        "Recall",
    ],
    "pv_intake": [
        "Causality",
        "Seriousness",
        "Expectedness",
        "Reportability",
        "Signal confirmation",
    ],
    "supply_planning": [
        "Allocate",
        "Reserve",
        "Ship",
        "Change inventory status",
        "Initiate recall",
    ],
}
FINDING_LABELS = {
    "genealogy": "Genealogy",
    "lab_results": "Lab results",
    "environmental_monitoring": "Environmental monitoring",
    "deviations": "Deviations",
    "capa": "CAPA",
    "change_control": "Change control",
    "validation_state": "Validation state",
    "supplier_evidence": "Supplier evidence",
    "release_packet_completeness": "Release packet",
}
STATUS_LABEL = {
    "pending_approval": "Pending approval",
    "completed": "Completed",
    "abstained": "Abstained",
    "blocked": "Blocked",
    "refused": "Refused",
    "timed_out": "Timed out",
}
SUBJECT_OPTIONS = {
    "batch_review": ["B-001", "B-002", "B-003"],
    "pv_intake": ["PV-001", "PV-002"],
    "supply_planning": ["P-100", "P-200"],
}
DEFAULT_REQUESTER = {
    "batch_review": "EU Qualified Person",
    "pv_intake": "Global Head of Pharmacovigilance",
    "supply_planning": "Supply Chain VP",
}

ROLES = [
    {
        "id": "EU Qualified Person",
        "label": "EU Qualified Person",
        "approves": ["batch_review", "supply_planning"],
        "supply_leg": "quality",
        "desk": "Quality · Batch / Supply quality leg",
    },
    {
        "id": "Chief Quality Officer",
        "label": "Chief Quality Officer",
        "approves": ["batch_review", "supply_planning"],
        "supply_leg": "quality",
        "escalation": True,
        "desk": "Escalation · Quality",
    },
    {
        "id": "Global Head of Pharmacovigilance",
        "label": "Global Head of Pharmacovigilance",
        "approves": ["pv_intake"],
        "desk": "PV reviewer",
    },
    {
        "id": "Chief Medical Officer",
        "label": "Chief Medical Officer",
        "approves": ["pv_intake"],
        "escalation": True,
        "desk": "Escalation · Medical",
    },
    {
        "id": "Patient Safety Representative",
        "label": "Patient Safety Representative",
        "approves": [],
        "can_veto_pv": True,
        "desk": "Advisory veto on PV only",
    },
    {
        "id": "Supply Chain VP",
        "label": "Supply Chain VP",
        "approves": ["supply_planning"],
        "supply_leg": "planning",
        "desk": "Supply planning leg",
    },
    {
        "id": "Manufacturing VP",
        "label": "Manufacturing VP",
        "approves": [],
        "requester_only": True,
        "desk": "Requester — never a Batch approver",
    },
]
DEFAULT_ROLE = ROLES[0]["id"]
NAV = [
    ("/", "Home", "home"),
    ("/inbox", "Inbox", "inbox"),
    ("/batch", "Batch", "batch"),
    ("/pv", "PV", "pv"),
    ("/supply", "Supply", "supply"),
    ("/history", "History", "history"),
    ("/submit", "New run", "submit"),
    ("/ops", "Ops", "ops"),
]


def role_by_id(role_id: str | None) -> dict[str, Any]:
    for r in ROLES:
        if r["id"] == role_id:
            return r
    return ROLES[0]


def can_approve(role: dict[str, Any], workflow: str) -> bool:
    if role.get("requester_only"):
        return False
    return workflow in (role.get("approves") or [])


def can_veto(role: dict[str, Any], workflow: str) -> bool:
    return bool(role.get("can_veto_pv") and workflow == "pv_intake")


def can_see_workflow(role: dict[str, Any], workflow: str, approver_roles: list[str]) -> bool:
    if role.get("requester_only"):
        return True
    if role["id"] in approver_roles:
        return True
    if can_approve(role, workflow) or can_veto(role, workflow):
        return True
    if role["id"] == "Chief Quality Officer" and workflow in ("batch_review", "supply_planning"):
        return True
    if role["id"] == "Chief Medical Officer" and workflow == "pv_intake":
        return True
    return False


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except ValueError:
        return None


def fmt_dt(value: str | None) -> str:
    dt = parse_dt(value)
    if dt is None:
        return "—"
    return dt.astimezone(UTC).strftime("%d %b %Y · %H:%M UTC")


def rel_time(value: str | None, now: datetime | None = None) -> str:
    dt = parse_dt(value)
    if dt is None:
        return "—"
    now = now or datetime.now(UTC)
    seconds = int((now - dt).total_seconds())
    if seconds < 0:
        return "in " + rel_time(now.isoformat(), dt)
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    return f"{seconds // 86400}d ago"


def sla_state(deadline: str | None, now: datetime | None = None) -> dict[str, Any]:
    dt = parse_dt(deadline)
    now = now or datetime.now(UTC)
    if dt is None:
        return {"label": "No clock", "tone": "mute", "remaining": None, "pct": 0, "ms": 0}
    remaining = dt - now
    ms = int(remaining.total_seconds() * 1000)
    hours = remaining.total_seconds() / 3600
    if remaining.total_seconds() <= 0:
        return {"label": "Clock elapsed", "tone": "bad", "remaining": "elapsed", "pct": 100, "ms": ms}
    if hours < 4:
        tone = "bad"
    elif hours < 8:
        tone = "warn"
    else:
        tone = "ok"
    total = max(remaining.total_seconds(), 1)
    # Display ring against a 24h window
    elapsed_frac = max(0, min(1, 1 - (remaining.total_seconds() / (24 * 3600))))
    h = int(remaining.total_seconds() // 3600)
    m = int((remaining.total_seconds() % 3600) // 60)
    return {
        "label": f"{h}h {m:02d}m remaining",
        "tone": tone,
        "remaining": f"{h}:{m:02d}",
        "pct": int(elapsed_frac * 100),
        "ms": ms,
    }


def enrich(run: dict[str, Any]) -> dict[str, Any]:
    run = dict(run)
    wf = run.get("workflow") or ""
    run["workflow_label"] = WORKFLOW_LABEL.get(wf, wf)
    run["workflow_short"] = WORKFLOW_SHORT.get(wf, wf)
    run["status_label"] = STATUS_LABEL.get(run.get("status") or "", run.get("status") or "—")
    run["created_fmt"] = fmt_dt(run.get("created_at"))
    run["created_rel"] = rel_time(run.get("created_at"))
    run["deadline_fmt"] = fmt_dt(run.get("hitl_deadline"))
    run["sla"] = sla_state(run.get("hitl_deadline")) if run.get("status") == "pending_approval" else None
    run["prohibitions"] = PROHIBITIONS.get(wf, [])
    payload = run.get("domain_payload") or {}
    findings = payload.get("findings") or []
    run["finding_counts"] = {
        "complete": sum(1 for f in findings if f.get("status") == "complete"),
        "gap": sum(1 for f in findings if f.get("status") == "gap"),
        "conflict": sum(1 for f in findings if f.get("status") == "conflict"),
        "total": len(findings),
    }
    return run
