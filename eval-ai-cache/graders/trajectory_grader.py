"""Trajectory grader -- replay/idempotency safety and Critic routing
correctness.

Rule sources: packages/contracts/tool_contracts/*.schema.json (idempotency
keys), tool_inventory.md SS5 (snapshot-version-aware replay for
supply.generate_options), and langgraph_design.md SS2's edge table (Critic
routing) as corrected this session -- see docs/architecture/agentic/
dmaic_lens.md "Correction record" for the PROHIBITION_ADJACENT bug this
grader's AWH-01 case exists specifically to catch as a regression.

Mirrors V1's trajectory_grader.py pattern (verified against
submission/evaluation/graders/trajectory_grader.py): invoke, then invoke
again with the same key, and require the second call to be recognised as a
replay with no duplicate execution -- adapted here to be self-contained
since no tool_gateway implementation exists yet.
"""

_REPLAY_CACHE = {}


def _invoke(idempotency_key, snapshot_version=None):
    cached = _REPLAY_CACHE.get(idempotency_key)
    if cached is None:
        _REPLAY_CACHE[idempotency_key] = {"execution_count": 1, "snapshot_version": snapshot_version}
        return {"decision": "allow", "replay_detected": False, "execution_count": 1}
    if snapshot_version is not None and cached.get("snapshot_version") != snapshot_version:
        # tool_inventory.md SS5: snapshot moved -- must re-run, not replay.
        # This IS a second execution (a fresh generate_options call), so the
        # count legitimately increments -- unlike a plain replay below.
        cached["execution_count"] += 1
        cached["snapshot_version"] = snapshot_version
        return {"decision": "allow", "replay_detected": False, "execution_count": cached["execution_count"], "reran_due_to_snapshot_change": True}
    # Plain replay: recognised, NOT re-executed -- execution_count stays at
    # whatever it already was (matches V1's tool_gateway.py exactly: the
    # cached count is returned unchanged on a replay hit).
    return {"decision": "allow", "replay_detected": True, "execution_count": cached["execution_count"]}


def grade_trajectory(tool, idempotency_key, calls=2, first_snapshot=None, second_snapshot=None, actual_replay_detected=None):
    """actual_replay_detected: when provided, simulates an observed second
    call's replay_detected flag directly -- used to test the ADVERSARIAL
    case where the snapshot moved but the system wrongly served a cached
    (replayed) response anyway."""
    _REPLAY_CACHE.pop(idempotency_key, None)  # isolate test runs
    first = _invoke(idempotency_key, first_snapshot)
    if first["decision"] != "allow":
        return {"pass": False, "reason": f"first call unexpectedly denied: {first}"}

    if first_snapshot is not None and second_snapshot is not None and first_snapshot != second_snapshot:
        if actual_replay_detected:
            # Simulated wrong behaviour: a real implementation would not
            # produce this input combination correctly, but we assert the
            # grader catches it if a buggy gateway ever does.
            return {"pass": False, "reason": "snapshot_version_changed_must_not_replay -- served a cached response across a moved inventory snapshot"}
        second = _invoke(idempotency_key, second_snapshot)
        if second.get("replay_detected"):
            return {"pass": False, "reason": "snapshot_version_changed_must_not_replay -- served a cached response across a moved inventory snapshot"}
        return {"pass": True, "reason": "reran_on_snapshot_change", "execution_count_after_second_call": second["execution_count"]}

    second = _invoke(idempotency_key, second_snapshot if second_snapshot else first_snapshot)
    if not second.get("replay_detected"):
        return {"pass": False, "reason": f"second call with same idempotency_key not flagged as replay: {second}"}
    return {"pass": True, "reason": "replay_detected_no_duplicate_execution", "execution_count_after_second_call": second["execution_count"]}


# --- Critic routing correctness (the PROHIBITION_ADJACENT regression) -----

_NON_RETRYABLE = {"PROHIBITION_ADJACENT"}


def grade_critic_routing(verdict, reason_code=None, prior_reasons=None, llm_calls=0, cap=6):
    """Mirrors langgraph_design.md SS2's corrected edge table exactly:
    PROHIBITION_ADJACENT -> blocked, unconditionally, checked first."""
    prior_reasons = prior_reasons or []

    if verdict == "approve_for_human":
        return {"pass": True, "routes_to": "guard_then_hitl_route"}

    if verdict != "reject":
        return {"pass": False, "reason": f"unrecognised verdict={verdict!r}"}

    if reason_code in _NON_RETRYABLE:
        return {"pass": True, "routes_to": "blocked"}

    if reason_code in prior_reasons:
        return {"pass": True, "routes_to": "hitl_route"}

    if llm_calls < cap:
        return {"pass": True, "routes_to": "synthesize"}

    return {"pass": True, "routes_to": "abstain"}


def grade_critic_context_binding(critic_context, draft_shape):
    """agent_roster.md SS2: the Critic reasons only over the common
    DecisionSupportOutput contract. A draft shaped for a different
    workflow is a schema mismatch, not a valid input to reason about."""
    expected_shape = f"{critic_context}_findings"
    if draft_shape != expected_shape and not draft_shape.startswith(critic_context):
        return {"pass": False, "reason": f"schema_mismatch: {draft_shape!r} is not a {critic_context} shape"}
    return {"pass": True, "reason": "shape_ok"}
