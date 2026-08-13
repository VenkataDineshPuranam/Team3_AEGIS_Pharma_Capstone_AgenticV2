"""pv_intake LangGraph -- Stage 20b. Same spine as services/api/graph.py's batch_review
graph (langgraph_design.md SS7: "same spine, different middle") -- intake, policy_load,
retrieve, evidence_gate, synthesize, guard(x2), critic_verify, hitl_route, hitl_interrupt,
finalize are structurally identical in shape. The deltas, per SS7's own table:

  - Tool nodes: duplicate_check -> normalize_terminology (hard ordering, DDD SS7 --
    duplicate_check must complete before triage/synthesize) instead of batch's reconcile.
  - Approver role: Global Head of Pharmacovigilance (hitl_control_model.md SS2), not EU QP.
  - New: the Patient Safety Representative's advisory veto -- registrable at any point,
    forces hitl_status="rejected" immediately, never overridden by a later approval
    (failure_and_loop_guards.md SS5.4). Enforced by audit_store.write_human_override's own
    write-time check (has_veto), not re-implemented here.

Deliberately NOT sharing code with graph.py via a generic workflow-parametrized builder --
RR-2/T-10 (nothing from Batch Review is assumed to transfer) argues for each workflow's
graph being independently readable and independently correct, not a shared abstraction that
could silently apply a Batch Review assumption to PV. Some duplication is the accepted cost.
"""
from __future__ import annotations

from datetime import UTC, datetime

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from packages.domain.payloads import DuplicateCandidate, NormalizationSuggestion, PVPayload
from packages.domain.evidence import EvidenceItem
from packages.domain.state import GovernedState, ReasonCode, RETRYABLE_REASON_CODES
from infra.policies.denial_of_wallet_guardrail import DenialOfWalletGuard
from services.integration import audit_store, evidence_gate, prohibited_action_guard
from services.integration.evidence_retrieve import ToolError as RetrieveError, retrieve as tool_retrieve
from services.integration.pv_duplicate_check import ToolError as DupCheckError, duplicate_check as tool_dup_check
from services.integration.pv_normalize_terminology import normalize_terminology as tool_normalize
from services.integration.policy_engine import PolicyEngineUnavailable, get_prohibition_contract
from services.api.nodes.llm_interface import LLMNodes, StubLLM

POLICY_VERSION = "v1"
MAX_LLM_CALLS = 6  # G1, unchanged -- structural cap is graph-shape-derived, not workflow-specific

PV_PRIMARY_APPROVER = "Global Head of Pharmacovigilance"  # hitl_control_model.md SS2
PV_VETO_ROLE = "Patient Safety Representative"


def build_pv_graph(llm: LLMNodes | None = None, case_id: str = "PV-001", checkpointer=None):
    llm = llm or StubLLM()
    audit_conn = audit_store.get_connection()
    dow_guard = DenialOfWalletGuard()

    def intake(state: GovernedState) -> dict:
        admission = dow_guard.check_and_admit(
            user_id=state["requester_role"], workflow=state["workflow"], as_of=datetime.now(UTC).date()
        )
        if not admission["admit"]:
            return {
                "authorization_checked_at": datetime.now(UTC),
                "trace_id": f"TR-{state['run_id']}",
                "terminal_state": "refused",
                "abstention_reason": admission["reason"],
            }
        return {"authorization_checked_at": datetime.now(UTC), "trace_id": f"TR-{state['run_id']}"}

    def policy_load(state: GovernedState) -> dict:
        try:
            contract = get_prohibition_contract(POLICY_VERSION, state["workflow"])
        except PolicyEngineUnavailable:
            return {"policy_contract_version": None, "terminal_state": "refused", "abstention_reason": "fail_closed"}
        return {"policy_contract_version": POLICY_VERSION, "prohibition_contract": contract}

    def retrieve(state: GovernedState) -> dict:
        try:
            result = tool_retrieve(
                run_id=state["run_id"], terms=["PHARMACOVIGILANCE", "policy"],
                policy_contract_version=state["policy_contract_version"],
                broadening=state["broadenings_used"] > 0,
            )
        except RetrieveError:
            return {"terminal_state": "abstained", "abstention_reason": "dependency_unavailable"}
        items = [EvidenceItem(**item) for item in result["items"]]
        return {"evidence": state["evidence"] + items, "tool_calls": state["tool_calls"] + 1}

    def evidence_gate_node(state: GovernedState) -> dict:
        result = evidence_gate.check(state["evidence"], state["broadenings_used"])
        if result.outcome == "broaden":
            return {"broadenings_used": state["broadenings_used"] + 1}
        if result.outcome == "abstain":
            return {"terminal_state": "abstained", "abstention_reason": result.reason}
        if result.outcome == "defect_halt":
            return {"terminal_state": "refused", "abstention_reason": "gate_defect"}
        return {"evidence_sufficient": True}

    def duplicate_check_node(state: GovernedState) -> dict:
        """DDD SS7 hard ordering invariant: must complete before synthesize -- enforced
        below as the only edge out of this node, never a conditional skip."""
        evidence_ids = [e.evidence_id for e in state["evidence"]]
        try:
            result = tool_dup_check(run_id=state["run_id"], case_id=case_id, case_summary_evidence_ids=evidence_ids)
        except DupCheckError:
            return {"terminal_state": "abstained", "abstention_reason": "dependency_unavailable"}
        candidates = tuple(DuplicateCandidate(**c) for c in result["candidates"])
        return {
            "domain_payload": PVPayload(
                case_id=case_id, duplicate_suspected=result["duplicate_suspected"],
                comparison_window_version=result["comparison_window_version"], candidates=candidates,
                normalization_suggestions=(), terminology_table_version="",
            ),
            "tool_calls": state["tool_calls"] + 1,
        }

    def normalize_terminology_node(state: GovernedState) -> dict:
        result = tool_normalize(run_id=state["run_id"], source_text=_case_source_text(case_id))
        suggestions = tuple(NormalizationSuggestion(**s) for s in result["suggestions"])
        payload = state["domain_payload"]
        updated_payload = PVPayload(
            case_id=payload.case_id, duplicate_suspected=payload.duplicate_suspected,
            comparison_window_version=payload.comparison_window_version, candidates=payload.candidates,
            normalization_suggestions=suggestions, terminology_table_version=result["terminology_table_version"],
        )
        return {"domain_payload": updated_payload, "tool_calls": state["tool_calls"] + 1}

    def synthesize(state: GovernedState) -> dict:
        try:
            draft, tin, tout = llm.synthesize(state)
        except Exception:  # noqa: BLE001 -- ADR-007, same as batch_review
            return {"terminal_state": "abstained", "abstention_reason": "degraded_mode"}
        return {
            "draft_output": draft, "llm_calls": state["llm_calls"] + 1,
            "tokens_in": state["tokens_in"] + tin, "tokens_out": state["tokens_out"] + tout,
        }

    def guard(state: GovernedState) -> dict:
        result = prohibited_action_guard.check(state["draft_output"], state["prohibition_contract"])
        if result.verdict == "blocked":
            # See services/api/graph.py's guard() for why this doesn't write_agent_run
            # here too -- finalize is the single write, avoiding the run_id PRIMARY KEY
            # collision that crashed this exact path in graph.py before this stage.
            return {"guard_verdict": "blocked", "terminal_state": "blocked", "abstention_reason": "prohibited_action"}
        return {"guard_verdict": "clear"}

    def critic_verify(state: GovernedState) -> dict:
        try:
            verdict, reason_code, tin, tout = llm.critic(state)
        except Exception:  # noqa: BLE001
            return {"terminal_state": "abstained", "abstention_reason": "degraded_mode"}
        updates: dict = {
            "critic_verdict": verdict, "llm_calls": state["llm_calls"] + 1,
            "tokens_in": state["tokens_in"] + tin, "tokens_out": state["tokens_out"] + tout,
        }
        if reason_code is not None:
            updates["critic_reason_codes"] = state["critic_reason_codes"] + [reason_code]
        return updates

    def hitl_route_node(state: GovernedState) -> dict:
        # 100% escalation by construction (agent_roster.md SS2) -- every PV output routes
        # to a human; there is no lower-risk-tier skip path, unlike Batch Review's future P-13.
        return {
            "hitl_required": True, "approver_roles": [PV_PRIMARY_APPROVER],
            "hitl_status": "pending", "hitl_tier": "T0",
        }

    def hitl_interrupt(state: GovernedState) -> dict:
        decision = interrupt(
            {"approver_roles": state["approver_roles"], "run_id": state["run_id"], "case_id": case_id}
        )
        from services.api.hitl_resume import parse_hitl_resume

        action, justification, _leg = parse_hitl_resume(decision)
        if action == "timed_out":
            audit_store.write_hitl_expired(
                audit_conn, state["run_id"], state["workflow"],
                eligible_roles_at_expiry=state["approver_roles"], recorded_at=datetime.now(UTC).isoformat(),
            )
            return {"hitl_status": action, "terminal_state": "abstained", "abstention_reason": "hitl_timeout"}
        if action == "veto":
            audit_store.write_human_override(
                audit_conn, state["run_id"], role=PV_VETO_ROLE, tier_at_action=state.get("hitl_tier") or "T0",
                action="veto_registered", justification=justification,
                recorded_at=datetime.now(UTC).isoformat(),
            )
            return {"hitl_status": "rejected", "veto_recorded": True, "terminal_state": "completed"}
        audit_store.write_human_override(
            audit_conn, state["run_id"], role=state["approver_roles"][0], tier_at_action=state.get("hitl_tier") or "T0",
            action=action, justification=justification,
            recorded_at=datetime.now(UTC).isoformat(),
        )
        return {"hitl_status": action, "terminal_state": "completed"}

    def mark_blocked_prohibition_adjacent(state: GovernedState) -> dict:
        return {"guard_verdict": "blocked", "terminal_state": "blocked", "abstention_reason": "prohibition_adjacent"}

    def mark_abstained_cap_exceeded(state: GovernedState) -> dict:
        return {"terminal_state": "abstained", "abstention_reason": "cap_exceeded"}

    def finalize(state: GovernedState) -> dict:
        terminal = state.get("terminal_state") or "completed"
        if terminal != "refused":
            dow_guard.record_run(
                user_id=state["requester_role"], workflow=state["workflow"],
                as_of=datetime.now(UTC).date(), actual_tokens=state["tokens_in"] + state["tokens_out"],
            )
        audit_record_id = f"AR-{state['run_id']}"
        audit_store.write_agent_run(
            audit_conn, state["run_id"], state["workflow"], terminal,
            datetime.now(UTC).isoformat(), abstention_reason=state.get("abstention_reason"),
            trace_id=state["trace_id"], policy_contract_version=state.get("policy_contract_version"),
            llm_calls=state["llm_calls"], tokens_in=state["tokens_in"], tokens_out=state["tokens_out"],
        )
        return {"terminal_state": terminal, "audit_record_id": audit_record_id}

    graph = StateGraph(GovernedState)
    graph.add_node("intake", intake)
    graph.add_node("policy_load", policy_load)
    graph.add_node("retrieve", retrieve)
    graph.add_node("evidence_gate", evidence_gate_node)
    graph.add_node("duplicate_check", duplicate_check_node)
    graph.add_node("normalize_terminology", normalize_terminology_node)
    graph.add_node("synthesize", synthesize)
    graph.add_node("guard1", guard)
    graph.add_node("guard2", guard)
    graph.add_node("critic_verify", critic_verify)
    graph.add_node("hitl_route", hitl_route_node)
    graph.add_node("hitl_interrupt", hitl_interrupt)
    graph.add_node("blocked_terminal", mark_blocked_prohibition_adjacent)
    graph.add_node("abstain_cap", mark_abstained_cap_exceeded)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("intake")
    graph.add_conditional_edges(
        "intake", lambda s: "refuse" if s.get("terminal_state") == "refused" else "policy_load",
        {"refuse": "finalize", "policy_load": "policy_load"},
    )
    graph.add_conditional_edges(
        "policy_load", lambda s: "refuse" if s.get("terminal_state") == "refused" else "retrieve",
        {"refuse": "finalize", "retrieve": "retrieve"},
    )
    graph.add_conditional_edges(
        "retrieve", lambda s: "abstain" if s.get("terminal_state") == "abstained" else "gate",
        {"abstain": "finalize", "gate": "evidence_gate"},
    )

    def route_after_gate(s: GovernedState) -> str:
        if s.get("terminal_state") in ("abstained", "refused"):
            return "terminal"
        if s.get("evidence_sufficient"):
            return "duplicate_check"
        return "retrieve"

    graph.add_conditional_edges(
        "evidence_gate", route_after_gate,
        {"terminal": "finalize", "duplicate_check": "duplicate_check", "retrieve": "retrieve"},
    )
    graph.add_conditional_edges(
        "duplicate_check", lambda s: "abstain" if s.get("terminal_state") == "abstained" else "normalize",
        {"abstain": "finalize", "normalize": "normalize_terminology"},
    )
    # Hard ordering invariant (DDD SS7): no edge from normalize_terminology skips synthesize.
    graph.add_edge("normalize_terminology", "synthesize")

    graph.add_conditional_edges(
        "synthesize", lambda s: "degraded" if s.get("terminal_state") == "abstained" else "guard1",
        {"degraded": "finalize", "guard1": "guard1"},
    )
    graph.add_conditional_edges(
        "guard1", lambda s: "blocked" if s["guard_verdict"] == "blocked" else "critic",
        {"blocked": "finalize", "critic": "critic_verify"},
    )

    def route_after_critic(s: GovernedState) -> str:
        if s.get("terminal_state") == "abstained":
            return "degraded"
        if s["critic_verdict"] == "approve_for_human":
            return "guard2"
        codes = s["critic_reason_codes"]
        if not codes:
            # Defense-in-depth: a reject verdict with no reason code should never reach
            # here (packages/config/llm_client.py's parser now rejects that shape), but
            # this router must not crash if it ever does -- escalate to a human rather
            # than trust an assumption a second time (found live under Groq, this session).
            return "hitl_escalate"
        latest = codes[-1]
        if latest == ReasonCode.PROHIBITION_ADJACENT:
            return "blocked"
        if s["llm_calls"] >= MAX_LLM_CALLS:
            return "abstain"
        if codes.count(latest) > 1:
            return "hitl_escalate"
        if latest in RETRYABLE_REASON_CODES:
            return "synthesize"
        return "hitl_escalate"

    graph.add_conditional_edges(
        "critic_verify", route_after_critic,
        {
            "guard2": "guard2", "blocked": "blocked_terminal", "abstain": "abstain_cap",
            "hitl_escalate": "hitl_route", "synthesize": "synthesize", "degraded": "finalize",
        },
    )
    graph.add_edge("blocked_terminal", "finalize")
    graph.add_edge("abstain_cap", "finalize")
    graph.add_conditional_edges(
        "guard2", lambda s: "blocked" if s["guard_verdict"] == "blocked" else "hitl",
        {"blocked": "finalize", "hitl": "hitl_route"},
    )
    graph.add_edge("hitl_route", "hitl_interrupt")
    graph.add_conditional_edges(
        "hitl_interrupt", lambda s: "no_action" if s.get("hitl_status") == "timed_out" else "finalize",
        {"no_action": "finalize", "finalize": "finalize"},
    )
    graph.add_edge("finalize", END)

    return graph.compile(checkpointer=checkpointer or MemorySaver())


def _case_source_text(case_id: str) -> str:
    """Looks up the fixture's own source_text so normalize_terminology_node's tool call
    matches what the fixture actually declares -- avoids duplicating fixture content here."""
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "synthetic" / "pv_cases" / f"{case_id}.json"
    return json.loads(path.read_text())["source_text"]
