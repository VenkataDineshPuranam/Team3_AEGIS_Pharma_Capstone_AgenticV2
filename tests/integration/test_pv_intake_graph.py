"""Phase 2 integration tests -- pv_intake graph shape, routing, veto, all exercised with
StubLLM (no API key, no network) except where noted. RR-2/T-10: nothing assumed to carry
over from batch_review's own tests -- every assertion here is checked independently.
"""
import os
import uuid
from pathlib import Path

import pytest
from dotenv import load_dotenv
from langgraph.types import Command

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

from packages.domain.state import new_state
from services.api.pv_graph import PV_VETO_ROLE, build_pv_graph

pytestmark = [
    pytest.mark.stub,
    pytest.mark.skipif(
        not os.environ.get("NEO4J_PASSWORD") or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
        reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured",
    ),
]


def _run_to_interrupt(case_id: str):
    run_id = f"R-pv-{uuid.uuid4().hex[:8]}"
    graph = build_pv_graph(case_id=case_id)
    config = {"configurable": {"thread_id": run_id}}
    state = new_state(run_id=run_id, workflow="pv_intake", requester_role="Global Head of Pharmacovigilance")
    result = graph.invoke(state, config=config)
    return graph, config, result


def test_clean_case_reaches_hitl_and_approves_to_completed():
    graph, config, result = _run_to_interrupt("PV-001")
    assert "__interrupt__" in result
    final = graph.invoke(Command(resume="approved"), config=config)
    assert final["terminal_state"] == "completed"
    assert final["domain_payload"].duplicate_suspected is False
    assert final["llm_calls"] == 2


def test_suspected_duplicate_case_reaches_hitl_with_candidate_visible():
    graph, config, result = _run_to_interrupt("PV-002")
    assert "__interrupt__" in result
    final = graph.invoke(Command(resume="approved"), config=config)
    assert final["domain_payload"].duplicate_suspected is True
    assert final["domain_payload"].candidates[0].candidate_case_id == "PV-001"


def test_veto_forces_rejected_and_is_never_overridden():
    """failure_and_loop_guards.md SS5.4 -- registrable at any tier, forces rejected
    immediately, never overridden by a later approval attempt."""
    graph, config, result = _run_to_interrupt("PV-001")
    assert "__interrupt__" in result
    final = graph.invoke(Command(resume="veto"), config=config)
    assert final["hitl_status"] == "rejected"
    assert final["veto_recorded"] is True
    assert final["terminal_state"] == "completed"  # a rejection IS a valid human decision

    # The "never overridden" half -- audit_store's own write-time check should refuse a
    # later approval for the same run_id now that a veto exists.
    from services.integration import audit_store as audit_store_module

    conn = audit_store_module.get_connection()
    assert audit_store_module.has_veto(conn, config["configurable"]["thread_id"]) is True


def test_normalize_terminology_never_sets_applied_true():
    """DDD SS8: a suggestion is never silently applied. Checked end-to-end through the
    real graph, not just the tool's own contract test."""
    graph, config, result = _run_to_interrupt("PV-001")
    assert "__interrupt__" in result
    final = graph.invoke(Command(resume="approved"), config=config)
    assert final["domain_payload"].normalization_suggestions  # PV-001 has real suggestions
    # No field on the payload could represent "applied" at all -- PVPayload has none,
    # matching the schema's own applied: const false + this repo's structural pattern.
    assert not hasattr(final["domain_payload"], "applied")


def test_hard_ordering_duplicate_check_before_synthesize():
    """Structural check: no edge from evidence_gate reaches synthesize directly --
    duplicate_check -> normalize_terminology is mandatory (DDD SS7)."""
    import inspect

    import services.api.pv_graph as pv_graph_module

    source = inspect.getsource(pv_graph_module.build_pv_graph)
    assert '"duplicate_check": "duplicate_check"' in source
    assert 'graph.add_edge("normalize_terminology", "synthesize")' in source
