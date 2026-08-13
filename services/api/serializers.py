"""Serialize GovernedState into the HTTP case-file contract.

Does not re-export domain models -- dumps to JSON-safe dicts the UI can render.
Never includes a guard-blocked draft body; callers must pass a redacted snapshot.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from services.api.sla import deadline_for_tier, infer_tier


def _dump(obj: Any) -> Any:
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    if isinstance(obj, dict):
        return {k: _dump(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_dump(v) for v in obj]
    if hasattr(obj, "value"):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def evidence_list(state: dict) -> list[dict[str, Any]]:
    items = state.get("evidence") or []
    dumped = _dump(items) or []
    return dumped if isinstance(dumped, list) else []


def domain_payload(state: dict) -> dict[str, Any] | None:
    dumped = _dump(state.get("domain_payload"))
    return dumped if isinstance(dumped, dict) else None


def draft_claims(state: dict) -> list[dict[str, Any]]:
    draft = state.get("draft_output")
    if draft is None:
        return []
    dumped = _dump(draft)
    if isinstance(dumped, dict):
        return list(dumped.get("claims") or [])
    return []


def draft_summary(state: dict) -> str | None:
    draft = state.get("draft_output")
    if draft is None:
        return None
    if hasattr(draft, "summary"):
        return draft.summary
    if isinstance(draft, dict):
        return draft.get("summary")
    return None


def critic_reason_codes(state: dict) -> list[str]:
    codes = state.get("critic_reason_codes") or []
    out: list[str] = []
    for c in codes:
        out.append(c.value if hasattr(c, "value") else str(c))
    return out


def snapshot_from_state(
    run_id: str,
    workflow: str,
    subject_id: str,
    state: dict,
    *,
    created_at: str | None = None,
) -> dict[str, Any]:
    created = created_at or datetime.now(UTC).isoformat()
    try:
        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        if created_dt.tzinfo is None:
            created_dt = created_dt.replace(tzinfo=UTC)
    except ValueError:
        created_dt = datetime.now(UTC)
    status = "pending_approval" if "__interrupt__" in state else None
    terminal = state.get("terminal_state")
    if status is None:
        status = terminal if terminal in ("completed", "abstained", "blocked", "refused") else "abstained"

    hitl_tier = state.get("hitl_tier") or infer_tier(created_dt, workflow)
    deadline = state.get("hitl_deadline")
    if deadline is None and status == "pending_approval":
        deadline = deadline_for_tier(created_dt, workflow, hitl_tier)  # type: ignore[arg-type]
    deadline_s = deadline.isoformat() if isinstance(deadline, datetime) else _dump(deadline)

    return {
        "run_id": run_id,
        "workflow": workflow,
        "subject_id": subject_id,
        "requester_role": state.get("requester_role") or "",
        "status": status,
        "terminal_state": terminal,
        "abstention_reason": state.get("abstention_reason"),
        "policy_contract_version": state.get("policy_contract_version"),
        "approver_roles": list(state.get("approver_roles") or []),
        "required_legs": state.get("hitl_required_legs") or None,
        "approved_legs": list(state.get("hitl_approved_legs") or []),
        "hitl_status": state.get("hitl_status"),
        "hitl_tier": hitl_tier,
        "hitl_deadline": deadline_s,
        "veto_recorded": bool(state.get("veto_recorded")),
        "draft_summary": draft_summary(state) if status != "blocked" else None,
        "draft_claims": draft_claims(state) if status != "blocked" else [],
        "evidence": evidence_list(state),
        "domain_payload": domain_payload(state),
        "critic_verdict": state.get("critic_verdict"),
        "critic_reason_codes": critic_reason_codes(state),
        "guard_verdict": state.get("guard_verdict"),
        "llm_calls": state.get("llm_calls"),
        "tool_calls": state.get("tool_calls"),
        "tokens_in": state.get("tokens_in"),
        "tokens_out": state.get("tokens_out"),
        "trace_id": state.get("trace_id") or "",
        "created_at": created,
    }
