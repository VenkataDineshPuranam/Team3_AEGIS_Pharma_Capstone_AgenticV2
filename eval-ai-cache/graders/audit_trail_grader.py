"""Audit trail / data-integrity grader.

Rule source: docs/architecture/agentic/langgraph_design.md node `finalize`
("emit the AgentRun record and write audit BEFORE returning to the caller
-- a response that reaches the caller with no audit write is not a valid
terminal state") and memory_design.md SS4 ("the text of a draft the guard
blocked" must never persist -- only a reason code, prohibition class, and
hash).
"""


def grade_audit_trail(terminal_state, trace_id, audit_record_id,
                       blocked_draft_reason_code=None,
                       blocked_draft_hash=None,
                       blocked_draft_text=None):
    if not trace_id:
        return {"pass": False, "reason": "missing_trace_id"}
    if not audit_record_id:
        return {"pass": False, "reason": "audit_record_id missing -- finalize requires it before response returns"}

    if terminal_state == "blocked":
        if not blocked_draft_reason_code or not blocked_draft_hash:
            return {"pass": False, "reason": "blocked_draft_missing_reason_code_or_hash"}
        if blocked_draft_text:
            return {"pass": False, "reason": "draft_text_persisted -- memory_design.md SS4 forbids storing the prohibited text itself"}

    return {"pass": True, "reason": "audit_trail_ok"}
