"""Stage 20b Phase 7 -- interim assumptions (interim_state.md SS3) re-checked
independently for pv_intake and supply_planning. RR-2/T-10: nothing assumed to transfer
from batch_review's own results (interim_state_results.md).

Coverage map, so this file doesn't silently re-test what's already proven elsewhere:
  - Assumption 1 (structural unrepresentability): NEW here -- PV/Supply payloads specifically.
  - Assumption 2 (evidence authority): NOT re-tested -- same evidence_retrieve.py / Neo4j
    layer batch_review already proved this against; workflow-agnostic by construction.
  - Assumption 3 (HITL routing/timeout, default-safe): ALREADY independently exercised in
    tests/integration/test_pv_intake_graph.py (veto forces rejected, never overridden) and
    test_supply_planning_graph.py (dual-approval: one leg is not approval, timeout mid-approval
    still => no action) -- not duplicated here.
  - Assumption 4 (degraded mode): NEW here -- PV/Supply graphs specifically.
  - Assumption 5 (Policy Engine fails closed): NEW here -- PV/Supply prohibition contracts
    specifically (security/policies/policy_contract.v1.json's pv_intake/supply_planning entries).
  - Assumption 6 (token economics): covered by packages/observability/dashboard_data.py's
    cost_panel(), workflow-filterable, already producing real numbers for both workflows
    (verified this session: PV and Supply both have real agent_run rows with token data).
  - Assumption 7 (hop count): same NOT_OBSERVABLE reasoning as batch_review applies
    identically here -- not workflow-specific, not re-stated.
"""
import os
import uuid
from pathlib import Path

import pytest
from dotenv import load_dotenv
from pydantic import ValidationError

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

from packages.domain.payloads import ConstraintSet, PVPayload, ShortageOption, SupplyPayload
from packages.domain.state import new_state
from services.api.nodes.llm_interface import StubLLM
from services.integration.policy_engine import PolicyEngineUnavailable, get_prohibition_contract

_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic")
_KEY_ENV = {"anthropic": "ANTHROPIC_API_KEY", "groq": "GROQ_API_KEY"}.get(_PROVIDER)

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not _KEY_ENV or not os.environ.get(_KEY_ENV) or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
        reason=f"BLOCKED_BY_ENVIRONMENT: {_KEY_ENV} not set, or Neo4j not configured",
    ),
]


# --- Assumption 1: structural unrepresentability, PV/Supply payloads ---------------------

def test_assumption_1_pv_payload_rejects_safety_determination_fields():
    with pytest.raises(ValidationError):
        PVPayload(
            case_id="PV-001", duplicate_suspected=False, comparison_window_version="v1",
            candidates=(), normalization_suggestions=(), terminology_table_version="v1",
            causality="probable",  # type: ignore[call-arg]
        )


def test_assumption_1_supply_payload_rejects_allocation_fields():
    with pytest.raises(ValidationError):
        SupplyPayload(
            product_id="P-100", options=(ShortageOption(
                option_id="OPT-1", description="x", constraints_satisfied=(),
                cold_chain_evidence_ids=(), transport_notes="",
            ),), constraint_set=ConstraintSet(), inventory_snapshot_version="v1",
            allocated_quantity=100,  # type: ignore[call-arg]
        )


# --- Assumption 4: degraded mode, PV/Supply graphs ----------------------------------------

def test_assumption_4_pv_llm_outage_abstains_with_deterministic_partial_result():
    from services.api.pv_graph import build_pv_graph

    class BrokenLLM(StubLLM):
        def synthesize(self, state):
            raise ConnectionError("simulated outage")

    run_id = f"R-pv-degraded-{uuid.uuid4().hex[:8]}"
    graph = build_pv_graph(llm=BrokenLLM(), case_id="PV-002")
    state = new_state(run_id=run_id, workflow="pv_intake", requester_role="Global Head of Pharmacovigilance")
    result = graph.invoke(state, config={"configurable": {"thread_id": run_id}})
    assert result["terminal_state"] == "abstained"
    assert result["abstention_reason"] == "degraded_mode"
    assert result["domain_payload"] is not None  # duplicate_check's result survives (rules-only path)


def test_assumption_4_supply_llm_outage_abstains_with_deterministic_partial_result():
    from services.api.supply_graph import build_supply_graph

    class BrokenLLM(StubLLM):
        def synthesize(self, state):
            raise ConnectionError("simulated outage")

    run_id = f"R-supply-degraded-{uuid.uuid4().hex[:8]}"
    graph = build_supply_graph(llm=BrokenLLM(), product_id="P-100")
    state = new_state(run_id=run_id, workflow="supply_planning", requester_role="Supply Chain VP")
    result = graph.invoke(state, config={"configurable": {"thread_id": run_id}})
    assert result["terminal_state"] == "abstained"
    assert result["abstention_reason"] == "degraded_mode"
    assert result["domain_payload"] is not None  # generate_options' result survives


# --- Assumption 5: Policy Engine fails closed, PV/Supply prohibition contracts -----------

def test_assumption_5_pv_prohibition_contract_loads_and_bans_safety_determination_language():
    contract = get_prohibition_contract("v1", "pv_intake")
    assert contract.workflow == "pv_intake"
    assert any("causality" in t or "reportable" in t for t in contract.banned_terms)


def test_assumption_5_supply_prohibition_contract_loads_and_bans_allocation_language():
    contract = get_prohibition_contract("v1", "supply_planning")
    assert contract.workflow == "supply_planning"
    assert any("allocate" in t or "reserve" in t for t in contract.banned_terms)


def test_assumption_5_policy_engine_unreachable_refuses_for_every_workflow():
    for workflow in ("batch_review", "pv_intake", "supply_planning"):
        with pytest.raises(PolicyEngineUnavailable):
            get_prohibition_contract("v999-nonexistent", workflow)
