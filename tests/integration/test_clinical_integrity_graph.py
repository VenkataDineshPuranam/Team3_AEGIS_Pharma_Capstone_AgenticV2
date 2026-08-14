"""Stage 21 integration tests -- clinical_integrity graph shape, routing, guards, HITL
interrupt, all exercised with StubLLM. Same pattern as test_batch_review_graph.py
(RR-2/T-10: independently checked, nothing assumed from batch_review).

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
from services.api.clinical_graph import build_clinical_graph

pytestmark = [
    pytest.mark.stub,
    pytest.mark.skipif(
        not os.environ.get("NEO4J_PASSWORD") or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
        reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured",
    ),
]


def _run_to_interrupt(protocol_id: str):
    run_id = f"R-clinical-{uuid.uuid4().hex[:8]}"
    graph = build_clinical_graph(protocol_id=protocol_id)
    config = {"configurable": {"thread_id": run_id}}
    state = new_state(run_id=run_id, workflow="clinical_integrity", requester_role="Clinical Trial Medical Monitor")
    result = graph.invoke(state, config=config)
    return graph, config, result


def test_clean_clinical_reaches_hitl_interrupt_and_approves_to_completed():
    graph, config, result = _run_to_interrupt("CT-001")
    assert "__interrupt__" in result
    final = graph.invoke(Command(resume={"action": "approved", "justification": "Reviewed all six categories; complete."}), config=config)
    assert final["terminal_state"] == "completed"
    assert final["audit_record_id"] is not None


def test_eligibility_conflict_still_reaches_hitl():
    """INJ-014: eligibility ambiguity surfaces as a conflict finding, exercised end to
    end through the real graph."""
    graph, config, result = _run_to_interrupt("CT-003")
    assert "__interrupt__" in result
    final = graph.invoke(Command(resume={"action": "rejected", "justification": "Compound identity conflict must be resolved first."}), config=config)
    assert final["terminal_state"] == "completed"
    assert final["hitl_status"] == "rejected"


def test_hitl_timeout_produces_no_action():
    graph, config, result = _run_to_interrupt("CT-001")
    assert "__interrupt__" in result
    final = graph.invoke(Command(resume="timed_out"), config=config)
    assert final["terminal_state"] == "abstained" or final["hitl_status"] == "timed_out"


def test_prohibited_eligibility_determination_term_is_blocked():
    """ADR-004 layer 3: the guard blocks output asserting a final eligibility
    determination -- the exact structural boundary this workflow exists to enforce."""
    from packages.domain.evidence import Claim
    from packages.domain.state import DecisionSupportOutput, ProhibitionContract
    from services.integration import prohibited_action_guard
    from services.integration.policy_engine import get_prohibition_contract

    contract = get_prohibition_contract("v1", "clinical_integrity")
    assert isinstance(contract, ProhibitionContract)
    draft = DecisionSupportOutput(
        summary="Participant is eligible for enrollment.",
        claims=(Claim(text="Participant is eligible for enrollment.", cites=("K-008",)),),
    )
    result = prohibited_action_guard.check(draft, contract)
    assert result.verdict == "blocked"


def test_policy_engine_unreachable_refuses_closed(monkeypatch):
    import services.api.clinical_graph as clinical_module

    def _raise(*args, **kwargs):
        from services.integration.policy_engine import PolicyEngineUnavailable
        raise PolicyEngineUnavailable("simulated outage")

    monkeypatch.setattr(clinical_module, "get_prohibition_contract", _raise)
    run_id = f"R-clinical-{uuid.uuid4().hex[:8]}"
    graph = clinical_module.build_clinical_graph(protocol_id="CT-001")
    state = new_state(run_id=run_id, workflow="clinical_integrity", requester_role="Clinical Trial Medical Monitor")
    result = graph.invoke(state, config={"configurable": {"thread_id": run_id}})
    assert result["terminal_state"] == "refused"
    assert result["abstention_reason"] == "fail_closed"
