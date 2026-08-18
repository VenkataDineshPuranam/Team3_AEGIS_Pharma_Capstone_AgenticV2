"""Shadow QP (ADR-010): a HITL rejection is retrievable as evidence on the next
batch_review run. Approvals are not. HITL is still required.

Skipped when Neo4j is unset, same convention as tests/integration/test_batch_review_graph.py.
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
from services.integration.precedent_mint import finding_hash
from services.integration.precedent_retrieve import _call_tracker

pytestmark = [
    pytest.mark.stub,
    pytest.mark.skipif(
        not os.environ.get("NEO4J_PASSWORD") or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
        reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured",
    ),
]


def _invoke(batch_id: str):
    run_id = f"R-{uuid.uuid4().hex[:8]}"
    graph = build_graph(batch_id=batch_id)
    config = {"configurable": {"thread_id": run_id}}
    state = new_state(run_id=run_id, workflow="batch_review", requester_role="EU Qualified Person")
    result = graph.invoke(state, config=config)
    return run_id, graph, config, result


@pytest.fixture(autouse=True)
def _reset_precedent_ceiling():
    _call_tracker.counts.clear()
    yield
    _call_tracker.counts.clear()


def test_rejection_of_genealogy_gap_is_cited_on_next_run_and_still_interrupts():
    run_a, graph_a, config_a, first = _invoke("B-002")
    assert "__interrupt__" in first
    final_a = graph_a.invoke(Command(resume="rejected"), config=config_a)
    assert final_a["hitl_status"] == "rejected"

    run_b, graph_b, config_b, second = _invoke("B-002")
    assert "__interrupt__" in second, "a cited precedent must not skip HITL"
    evidence_ids = [e.evidence_id for e in second["evidence"]]
    assert f"HP-{run_a}" in evidence_ids
    dumped = second["draft_output"].model_dump()
    assert "release_recommended" not in dumped
    assert second.get("terminal_state") not in ("completed",)
    graph_b.invoke(Command(resume="approved"), config=config_b)


def test_approval_does_not_mint_retrievable_precedent():
    run_a, graph_a, config_a, first = _invoke("B-002")
    assert "__interrupt__" in first
    graph_a.invoke(Command(resume="approved"), config=config_a)

    _run_b, _graph_b, _config_b, second = _invoke("B-002")
    assert "__interrupt__" in second
    evidence_ids = [e.evidence_id for e in second["evidence"]]
    assert f"HP-{run_a}" not in evidence_ids


def test_gap_fixture_hash_is_stable():
    """Sanity: B-002's open findings hash is what mint and retrieve share."""
    from services.integration.batch_reconcile import reconcile
    from services.integration.evidence_retrieve import retrieve

    run_id = f"R-hash-{uuid.uuid4().hex[:8]}"
    retrieve(run_id=run_id, terms=["BATCH_RELEASE", "policy"], policy_contract_version="v1")
    result = reconcile(run_id=run_id, batch_id="B-002", evidence_ids=["K-006"], policy_contract_version="v1")
    digest = finding_hash(result["findings"])
    assert digest
