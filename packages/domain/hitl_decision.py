"""What a human actually submitted at an HITL interrupt -- Stage 21.

Closes the gap every graph's `hitl_interrupt` node named in its own comments:

    KNOWN SIMPLIFICATION (20a scope): the interrupt's resume payload here is a bare
    decision string (test/interim harness), not a structured {decision, justification}
    object a real approver UI would supply -- justification is a placeholder pending
    that real input surface (Stage 20b / apps/web).

That input surface now exists, so the placeholder string that was being written into
`human_override_recorded.justification` is replaced by what the approver actually typed.
`audit_store.write_human_override` has always rejected an empty justification; until now
the only thing keeping that check satisfied was a hardcoded placeholder, which means the
column was structurally present but evidentially worthless.

This IS shared across all three graphs, unlike the graphs themselves (pv_graph.py's
docstring explains why those are deliberately not shared). The reason the rule differs
here: this is not workflow logic, it is the shape of the resume payload the HITL
mechanism itself carries. A per-workflow copy could drift into three different ideas of
what a human submitted, which is the opposite of what RR-2/T-10 is protecting.

Backwards compatibility is deliberate and load-bearing: every existing test resumes these
graphs with a bare string ("approved", "veto", {"leg": ..., "action": ...}). Those calls
still mean exactly what they meant before -- `decode` maps them to a decision carrying the
legacy placeholder justification. No existing test changes, so their guarantees still
cover the paths they always covered.
"""
from __future__ import annotations

from dataclasses import dataclass

# What the graphs wrote before an approver UI existed. Kept as the value for legacy
# bare-string resumes so those records stay honestly labelled as harness-originated rather
# than silently looking like a real human's words.
LEGACY_PLACEHOLDER = "[no structured justification -- resumed without an approver input surface]"

Action = str  # "approved" | "rejected" | "veto" | "timed_out"


@dataclass(frozen=True)
class HitlDecision:
    action: Action
    justification: str = LEGACY_PLACEHOLDER
    # The role the submitter CLAIMED, unverified. Not authorization: no authentication
    # exists in this build (see docs + /api/governance's auth block), so this is recorded
    # as an assertion made by the caller, never consulted to decide whether the action is
    # permitted. Kept distinct from the graph's own `approver_roles` -- that list is what
    # the governance layer determined is eligible, which is a different fact.
    claimed_identity: str | None = None
    leg: str | None = None  # supply_planning only


def decode(resume_value: object) -> HitlDecision:
    """Normalize whatever arrived at `interrupt()` into one decision object.

    Accepts three shapes:
      - a bare string           -- every pre-Stage-21 caller, incl. the whole test suite
      - {"leg", "action"}       -- supply_planning's pre-Stage-21 dual-approval payload
      - {"action", "justification", "claimed_identity", "leg"}  -- the approver UI
    """
    if isinstance(resume_value, str):
        return HitlDecision(action=resume_value)

    if isinstance(resume_value, dict):
        justification = (resume_value.get("justification") or "").strip() or LEGACY_PLACEHOLDER
        return HitlDecision(
            action=str(resume_value.get("action", "")),
            justification=justification,
            claimed_identity=resume_value.get("claimed_identity"),
            leg=resume_value.get("leg"),
        )

    # Unrecognized shape -- do NOT guess an action. Returning an empty action makes every
    # graph's routing fall through to its non-approval path, which is the safe direction.
    return HitlDecision(action="")
