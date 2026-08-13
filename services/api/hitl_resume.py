"""Parse HITL interrupt resume payloads.

Existing graph tests resume with a bare string ("approved" | "rejected" | "veto" |
"timed_out") or, for Supply, a {leg, action} dict. The Approver Workbench sends a
structured object that also carries a required justification (G-10). This helper
accepts both so graph tests stay valid and the UI can close the placeholder gap.
"""
from __future__ import annotations

from typing import Any

PLACEHOLDER_JUSTIFICATION = (
    "[20a placeholder -- no structured justification input surface yet]"
)


def parse_hitl_resume(payload: Any) -> tuple[str, str, str | None]:
    """Return (action, justification, leg).

    justification is empty for timed_out (no human decision). For string resumes
    (tests), the historical placeholder is used so audit_store's nonempty rule holds.
    """
    if payload == "timed_out":
        return "timed_out", "", None
    if isinstance(payload, str):
        return payload, PLACEHOLDER_JUSTIFICATION, None
    if isinstance(payload, dict):
        action = str(payload.get("action") or "")
        if action == "timed_out":
            return "timed_out", "", payload.get("leg")
        just = (payload.get("justification") or "").strip() or PLACEHOLDER_JUSTIFICATION
        leg = payload.get("leg")
        return action, just, leg if isinstance(leg, str) else None
    return str(payload), PLACEHOLDER_JUSTIFICATION, None
