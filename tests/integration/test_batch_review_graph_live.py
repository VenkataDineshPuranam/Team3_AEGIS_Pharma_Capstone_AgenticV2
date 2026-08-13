"""Phase 5 'live' tests -- real LLM provider, real network call. Marked `live` so they're
run separately from the zero-key `stub` suite (test_batch_review_graph.py).

Skipped entirely if no usable key is configured. When LLM_PROVIDER=groq, results are
PROVISIONAL (see packages/config/llm_client.py's module docstring and ADR-009) -- this
test still runs and asserts correctness of the GRAPH's routing (terminal states are
well-formed, caps are respected), but does NOT assert the interim-assumption content
claims that only count under LLM_PROVIDER=anthropic (Phase 6 owns that distinction).
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

_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic")
_KEY_ENV = {"anthropic": "ANTHROPIC_API_KEY", "groq": "GROQ_API_KEY"}.get(_PROVIDER)

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not _KEY_ENV or not os.environ.get(_KEY_ENV) or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
        reason=f"BLOCKED_BY_ENVIRONMENT: {_KEY_ENV} not set, or Neo4j not configured",
    ),
]


def _run(batch_id: str, resume_decision: str = "approved"):
    from packages.config.llm_client import get_llm

    llm = get_llm()
    run_id = f"R-live-{uuid.uuid4().hex[:8]}"
    graph = build_graph(llm=llm, batch_id=batch_id)
    config = {"configurable": {"thread_id": run_id}}
    state = new_state(run_id=run_id, workflow="batch_review", requester_role="EU Qualified Person")
    result = graph.invoke(state, config=config)
    if "__interrupt__" in result:
        result = graph.invoke(Command(resume=resume_decision), config=config)
    return result


def test_graph_produces_a_well_formed_terminal_state():
    """Provider-agnostic assertion: whatever the model does, the graph must land on one
    of the four valid terminal states -- never None, never something else (the class of
    bug this session's routing fixes closed)."""
    result = _run("B-001")
    assert result["terminal_state"] in ("completed", "abstained", "blocked", "refused")
    assert result["audit_record_id"] is not None or result["terminal_state"] == "abstained"


def test_graph_never_exceeds_g1_llm_call_cap():
    result = _run("B-002")
    assert result["llm_calls"] <= 6  # G1, failure_and_loop_guards.md SS2


@pytest.mark.skipif(_PROVIDER != "anthropic", reason="Interim-assumption content only counts under Route A (ADR-009)")
def test_happy_path_uses_exactly_two_llm_calls_under_claude():
    """dmaic_lens.md SS7's expected happy-path count -- the actual interim-assumption
    check, gated to the provider whose measurements count."""
    result = _run("B-001")
    assert result["terminal_state"] == "completed"
    assert result["llm_calls"] == 2
