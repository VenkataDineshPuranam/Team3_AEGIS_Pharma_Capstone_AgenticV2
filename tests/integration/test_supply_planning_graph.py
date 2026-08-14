"""Phase 3 integration tests -- supply_planning graph shape, dual-approval, all exercised
with StubLLM. RR-2/T-10: independently checked, nothing assumed from batch_review/pv_intake.
"""
import os
import uuid
from pathlib import Path

import pytest
from dotenv import load_dotenv
from langgraph.types import Command

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

from packages.domain.state import new_state
from services.api.supply_graph import PLANNING_LEG, QUALITY_LEG, build_supply_graph

pytestmark = [
    pytest.mark.stub,
    pytest.mark.skipif(
        not os.environ.get("NEO4J_PASSWORD") or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
        reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured",
    ),
]


def _run_to_interrupt(product_id: str):
    run_id = f"R-supply-{uuid.uuid4().hex[:8]}"
    graph = build_supply_graph(product_id=product_id)
    config = {"configurable": {"thread_id": run_id}}
    state = new_state(run_id=run_id, workflow="supply_planning", requester_role="Supply Chain VP")
    result = graph.invoke(state, config=config)
    return graph, config, result


def test_options_available_reaches_hitl_with_dual_legs_required():
    graph, config, result = _run_to_interrupt("P-100")
    assert "__interrupt__" in result
    interrupt_payload = result["__interrupt__"][0].value
    assert set(interrupt_payload["required_legs"]) == {PLANNING_LEG, QUALITY_LEG}
    assert interrupt_payload["approved_legs"] == []


def test_one_leg_approving_is_not_approval():
    """failure_and_loop_guards.md SS5.4: partial approval is not approval -- it expires
    to no action like any other incomplete approval. Checked here as: after ONE leg
    approves, the graph must still be paused (interrupted again), never 'completed'."""
    graph, config, result = _run_to_interrupt("P-100")
    assert "__interrupt__" in result

    after_one_leg = graph.invoke(Command(resume={"leg": PLANNING_LEG, "action": "approved"}), config=config)
    assert "__interrupt__" in after_one_leg, "one leg approving must not complete the run"
    assert after_one_leg.get("terminal_state") != "completed"


def test_both_legs_approving_completes_the_run():
    graph, config, result = _run_to_interrupt("P-100")
    assert "__interrupt__" in result

    after_planning = graph.invoke(Command(resume={"leg": PLANNING_LEG, "action": "approved"}), config=config)
    assert "__interrupt__" in after_planning  # still pending the Quality leg

    final = graph.invoke(Command(resume={"leg": QUALITY_LEG, "action": "approved"}), config=config)
    assert final["terminal_state"] == "completed"
    assert final["hitl_status"] == "approved"
    assert set(final["hitl_approved_legs"]) == {PLANNING_LEG, QUALITY_LEG}


def test_either_leg_rejecting_ends_the_run_without_the_other_leg():
    graph, config, result = _run_to_interrupt("P-100")
    assert "__interrupt__" in result

    final = graph.invoke(Command(resume={"leg": QUALITY_LEG, "action": "rejected"}), config=config)
    assert final["terminal_state"] == "completed"
    assert final["hitl_status"] == "rejected"


def test_empty_option_set_abstains_agent_has_nothing_to_rank():
    """agent_roster.md SS2: abstain if the constraint filter returns an empty candidate set."""
    _, _, result = _run_to_interrupt("P-200")
    assert result["terminal_state"] == "abstained"
    assert "__interrupt__" not in result


def test_replaying_an_already_approved_leg_does_not_duplicate_the_audit_record():
    """Stage 21 gap-closure -- INJ-080: an agent resuming a supply-recovery plan from a
    stale checkpoint duplicating a draft reservation. This system has no reservation
    write to duplicate (ADR-004), but the equivalent real risk is a duplicate audit
    write for the same leg's approval -- a resumed run replaying an already-processed
    resume value. Both the approved_legs set AND the audit record stay idempotent."""
    from services.integration.audit_store import get_connection, human_overrides

    graph, config, result = _run_to_interrupt("P-100")
    assert "__interrupt__" in result

    after_first = graph.invoke(Command(resume={"leg": PLANNING_LEG, "action": "approved"}), config=config)
    assert "__interrupt__" in after_first

    # Replay: the same leg's approval resumes a second time (simulating a stale-
    # checkpoint resume of an already-applied decision).
    after_replay = graph.invoke(Command(resume={"leg": PLANNING_LEG, "action": "approved"}), config=config)
    assert "__interrupt__" in after_replay  # still just waiting on Quality, not duplicated

    conn = get_connection()
    actions = human_overrides(conn, result["__interrupt__"][0].value["run_id"])
    planning_approvals = [a for a in actions if a["role"] == "Supply Chain VP" and a["action"] == "approved"]
    assert len(planning_approvals) == 1, "the replayed resume must not write a second audit record"

    final = graph.invoke(Command(resume={"leg": QUALITY_LEG, "action": "approved"}), config=config)
    assert final["terminal_state"] == "completed"
    assert final["hitl_approved_legs"].count(PLANNING_LEG) == 1  # never duplicated in the list either


def test_timeout_produces_no_action_even_mid_dual_approval():
    graph, config, result = _run_to_interrupt("P-100")
    assert "__interrupt__" in result

    after_planning = graph.invoke(Command(resume={"leg": PLANNING_LEG, "action": "approved"}), config=config)
    assert "__interrupt__" in after_planning

    final = graph.invoke(Command(resume="timed_out"), config=config)
    assert final["terminal_state"] == "abstained"
    assert final["abstention_reason"] == "hitl_timeout"
    # The planning leg's earlier approval is preserved in the record, but the run itself
    # is still "no action" overall -- silence on the second leg is not approval.
    assert final["terminal_state"] != "completed"
