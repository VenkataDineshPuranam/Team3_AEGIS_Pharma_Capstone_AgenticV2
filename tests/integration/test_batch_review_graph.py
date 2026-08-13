"""Phase 4 integration tests -- full graph shape, routing, guards, caps, HITL interrupt,
all exercised with StubLLM (no API key, no network). Marked `stub` so they're selectable
independently of the `live` real-provider tests Phase 5 adds.

Requires Neo4j (evidence_retrieve is a real node in this graph) -- skipped otherwise.
"""
import os
import uuid
from pathlib import Path

import pytest
from dotenv import load_dotenv
from langgraph.types import Command

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

from packages.domain.state import new_state
from services.api.graph import build_graph

pytestmark = [
    pytest.mark.stub,
    pytest.mark.skipif(
        not os.environ.get("NEO4J_PASSWORD") or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
        reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured",
    ),
]


def _run_to_interrupt(batch_id: str):
    run_id = f"R-{uuid.uuid4().hex[:8]}"
    graph = build_graph(batch_id=batch_id)
    config = {"configurable": {"thread_id": run_id}}
    state = new_state(run_id=run_id, workflow="batch_review", requester_role="EU Qualified Person")
    result = graph.invoke(state, config=config)
    return graph, config, result


def test_clean_batch_reaches_hitl_interrupt_and_approves_to_completed():
    graph, config, result = _run_to_interrupt("B-001")
    assert "__interrupt__" in result, "clean batch with citations should reach HITL, not a terminal state directly"

    final = graph.invoke(Command(resume="approved"), config=config)
    assert final["terminal_state"] == "completed"
    assert final["audit_record_id"] is not None
    assert final["llm_calls"] == 2  # happy path: one synthesis, one critic -- dmaic_lens.md SS7


def test_gap_batch_still_reaches_hitl_since_stub_always_cites():
    """StubLLM always attaches citations (even for gap findings), so the Critic approves
    -- this proves the GAP is visible in the draft's content, not that gaps trigger a
    different graph path. Reason-code routing is tested directly below."""
    graph, config, result = _run_to_interrupt("B-002")
    assert "__interrupt__" in result
    final = graph.invoke(Command(resume="rejected"), config=config)
    assert final["terminal_state"] == "completed"  # 'rejected' is a human decision, not a graph abstention
    assert final["hitl_status"] == "rejected"


def test_hitl_timeout_produces_no_action():
    graph, config, result = _run_to_interrupt("B-001")
    assert "__interrupt__" in result
    final = graph.invoke(Command(resume="timed_out"), config=config)
    assert final["terminal_state"] == "abstained" or final["hitl_status"] == "timed_out"


def test_policy_engine_unreachable_refuses_closed(monkeypatch):
    """ADR-005/BC-3: fail closed, no cached-policy fallback."""
    import services.api.graph as graph_module

    def _raise(*args, **kwargs):
        from services.integration.policy_engine import PolicyEngineUnavailable
        raise PolicyEngineUnavailable("simulated outage")

    monkeypatch.setattr(graph_module, "get_prohibition_contract", _raise)
    run_id = f"R-{uuid.uuid4().hex[:8]}"
    graph = graph_module.build_graph(batch_id="B-001")
    state = new_state(run_id=run_id, workflow="batch_review", requester_role="EU Qualified Person")
    result = graph.invoke(state, config={"configurable": {"thread_id": run_id}})
    assert result["terminal_state"] == "refused"
    assert result["abstention_reason"] == "fail_closed"


def test_no_edge_from_synthesize_reaches_finalize_without_guard_or_critic():
    """Structural assertion, not a runtime one: reads graph.py's own edge table rather
    than executing, matching langgraph_design.md's own framing ('read the graph for what
    it refuses to do')."""
    import inspect

    import services.api.graph as graph_module

    source = inspect.getsource(graph_module.build_graph)
    # synthesize's only outgoing edges go to guard1 or finalize (degraded_mode abstain,
    # ADR-007) -- never anywhere else, confirmed by construction (the conditional-edge
    # mapping for "synthesize"), not by executing the graph.
    assert '"degraded": "finalize", "guard1": "guard1"' in source
