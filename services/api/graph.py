"""batch_review LangGraph -- Stage 20a Phase 4. Direct transcription of
docs/architecture/agentic/langgraph_design.md SS1-2's mermaid diagram and edge table.
11 nodes, 2 of them LLM (pluggable via `llm`, defaults to StubLLM -- see nodes/llm_interface.py).

Read the graph for what it refuses to do: there is no edge from `synthesize` to `finalize`.
Generated text cannot reach a caller without passing the guard, the Critic, the guard again,
and a human (langgraph_design.md SS1).
"""
from __future__ import annotations

from datetime import UTC, datetime

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command, interrupt

from packages.domain.payloads import BatchPayload, ReconciliationFinding
from packages.domain.evidence import EvidenceItem
from packages.domain.state import GovernedState, ReasonCode, RETRYABLE_REASON_CODES
from services.integration import audit_store, evidence_gate, hitl_route, prohibited_action_guard
from services.integration.batch_reconcile import ToolError as ReconcileError, reconcile as tool_reconcile
from services.integration.evidence_retrieve import ToolError as RetrieveError, retrieve as tool_retrieve
from services.integration.policy_engine import PolicyEngineUnavailable, get_prohibition_contract
from services.api.nodes.llm_interface import LLMNodes, StubLLM

POLICY_VERSION = "v1"
MAX_LLM_CALLS = 6  # G1, failure_and_loop_guards.md SS2


def build_graph(llm: LLMNodes | None = None, batch_id: str = "B-001", checkpointer=None):
    llm = llm or StubLLM()
    audit_conn = audit_store.get_connection()

    def intake(state: GovernedState) -> dict:
        return {
            "authorization_checked_at": datetime.now(UTC),
            "trace_id": f"TR-{state['run_id']}",
        }

    def policy_load(state: GovernedState) -> dict:
        try:
            contract = get_prohibition_contract(POLICY_VERSION, state["workflow"])
        except PolicyEngineUnavailable:
            return {"policy_contract_version": None, "terminal_state": "refused", "abstention_reason": "fail_closed"}
        return {"policy_contract_version": POLICY_VERSION, "prohibition_contract": contract}

    def retrieve(state: GovernedState) -> dict:
        try:
            result = tool_retrieve(
                run_id=state["run_id"],
                terms=["BATCH_RELEASE", "policy"],
                policy_contract_version=state["policy_contract_version"],
                broadening=state["broadenings_used"] > 0,
            )
        except RetrieveError:
            return {"terminal_state": "abstained", "abstention_reason": "dependency_unavailable"}
        items = [EvidenceItem(**item) for item in result["items"]]
        return {
            "evidence": state["evidence"] + items,
            "tool_calls": state["tool_calls"] + 1,
        }

    def evidence_gate_node(state: GovernedState) -> dict:
        result = evidence_gate.check(state["evidence"], state["broadenings_used"])
        if result.outcome == "broaden":
            return {"broadenings_used": state["broadenings_used"] + 1}
        if result.outcome == "abstain":
            return {"terminal_state": "abstained", "abstention_reason": result.reason}
        if result.outcome == "defect_halt":
            return {"terminal_state": "refused", "abstention_reason": "gate_defect"}
        return {"evidence_sufficient": True}

    def reconcile(state: GovernedState) -> dict:
        evidence_ids = [e.evidence_id for e in state["evidence"]]
        try:
            result = tool_reconcile(
                run_id=state["run_id"], batch_id=batch_id,
                evidence_ids=evidence_ids, policy_contract_version=state["policy_contract_version"],
            )
        except ReconcileError:
            return {"terminal_state": "abstained", "abstention_reason": "dependency_unavailable"}
        findings = tuple(ReconciliationFinding(**f) for f in result["findings"])
        payload = BatchPayload(batch_id=batch_id, reconciliation_complete=result["reconciliation_complete"], findings=findings)
        return {"domain_payload": payload, "tool_calls": state["tool_calls"] + 1}

    def synthesize(state: GovernedState) -> dict:
        try:
            draft, tin, tout = llm.synthesize(state)
        except Exception:  # noqa: BLE001 -- ADR-007: LLM provider unreachable -> abstain,
            # never guess. The deterministic partial result (domain_payload, already
            # computed by `reconcile`) is attached via `domain_payload` staying in state --
            # failure_and_loop_guards.md SS6 "the rules-only path still produces auditable
            # findings" is satisfied by that field surviving into the AgentRun record.
            return {"terminal_state": "abstained", "abstention_reason": "degraded_mode"}
        return {
            "draft_output": draft,
            "llm_calls": state["llm_calls"] + 1,
            "tokens_in": state["tokens_in"] + tin,
            "tokens_out": state["tokens_out"] + tout,
        }

    def guard(state: GovernedState) -> dict:
        result = prohibited_action_guard.check(state["draft_output"], state["prohibition_contract"])
        if result.verdict == "blocked":
            draft_hash = str(hash(state["draft_output"].summary))  # placeholder for SHA-256 at Stage 20 deploy
            audit_store.write_agent_run(  # ProhibitedActionBlocked recorded via agent_run's terminal_state
                audit_conn, state["run_id"], state["workflow"], "blocked",
                datetime.now(UTC).isoformat(), abstention_reason="prohibited_action", trace_id=state["trace_id"],
            )
            return {"guard_verdict": "blocked", "terminal_state": "blocked", "abstention_reason": "prohibited_action"}
        return {"guard_verdict": "clear"}

    def critic_verify(state: GovernedState) -> dict:
        try:
            verdict, reason_code, tin, tout = llm.critic(state)
        except Exception:  # noqa: BLE001 -- same ADR-007 rule as synthesize
            return {"terminal_state": "abstained", "abstention_reason": "degraded_mode"}
        updates: dict = {
            "critic_verdict": verdict,
            "llm_calls": state["llm_calls"] + 1,
            "tokens_in": state["tokens_in"] + tin,
            "tokens_out": state["tokens_out"] + tout,
        }
        if reason_code is not None:
            updates["critic_reason_codes"] = state["critic_reason_codes"] + [reason_code]
        return updates

    def hitl_route_node(state: GovernedState) -> dict:
        return {
            "hitl_required": True,
            "approver_roles": [hitl_route.PRIMARY_APPROVER],
            "hitl_status": "pending",
            "hitl_tier": "T0",
        }

    def hitl_interrupt(state: GovernedState) -> dict:
        decision = interrupt(
            {"approver_roles": state["approver_roles"], "run_id": state["run_id"], "batch_id": batch_id}
        )
        # BC-12: timeout => no action, EVER. Set explicitly here, not left to finalize's
        # fallback -- that fallback is exactly what silently mislabeled a timeout as
        # "completed" before this fix (interim assumption 3's own failure mode).
        if decision == "timed_out":
            return {"hitl_status": decision, "terminal_state": "abstained", "abstention_reason": "hitl_timeout"}
        return {"hitl_status": decision, "terminal_state": "completed"}

    def mark_blocked_prohibition_adjacent(state: GovernedState) -> dict:
        """critic_verify's PROHIBITION_ADJACENT route bypasses guard2 entirely (never
        retried, failure_and_loop_guards.md SS4) -- this node is what actually sets
        terminal_state on that path, since route_after_critic is a pure router and
        cannot mutate state itself."""
        return {"guard_verdict": "blocked", "terminal_state": "blocked", "abstention_reason": "prohibition_adjacent"}

    def mark_abstained_cap_exceeded(state: GovernedState) -> dict:
        """G1 (max 6 LLM calls) hit -- failure_and_loop_guards.md SS6:
        abstained/cap_exceeded, alerted as an engineering defect (SEV-3, alerting.md)."""
        return {"terminal_state": "abstained", "abstention_reason": "cap_exceeded"}

    def finalize(state: GovernedState) -> dict:
        terminal = state.get("terminal_state") or "completed"
        audit_record_id = f"AR-{state['run_id']}"
        audit_store.write_agent_run(
            audit_conn, state["run_id"], state["workflow"], terminal,
            datetime.now(UTC).isoformat(), abstention_reason=state.get("abstention_reason"),
            trace_id=state["trace_id"], policy_contract_version=state.get("policy_contract_version"),
        )
        return {"terminal_state": terminal, "audit_record_id": audit_record_id}

    graph = StateGraph(GovernedState)
    graph.add_node("intake", intake)
    graph.add_node("policy_load", policy_load)
    graph.add_node("retrieve", retrieve)
    graph.add_node("evidence_gate", evidence_gate_node)
    graph.add_node("reconcile", reconcile)
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
    graph.add_edge("intake", "policy_load")

    graph.add_conditional_edges(
        "policy_load",
        lambda s: "refuse" if s.get("terminal_state") == "refused" else "retrieve",
        {"refuse": "finalize", "retrieve": "retrieve"},
    )
    graph.add_conditional_edges(
        "retrieve",
        lambda s: "abstain" if s.get("terminal_state") == "abstained" else "gate",
        {"abstain": "finalize", "gate": "evidence_gate"},
    )

    def route_after_gate(s: GovernedState) -> str:
        if s.get("terminal_state") in ("abstained", "refused"):
            return "terminal"
        if s.get("evidence_sufficient"):
            return "reconcile"
        return "retrieve"  # broadening

    graph.add_conditional_edges("evidence_gate", route_after_gate, {"terminal": "finalize", "reconcile": "reconcile", "retrieve": "retrieve"})
    graph.add_conditional_edges(
        "reconcile",
        lambda s: "abstain" if s.get("terminal_state") == "abstained" else "synthesize",
        {"abstain": "finalize", "synthesize": "synthesize"},
    )
    graph.add_conditional_edges(
        "synthesize",
        lambda s: "degraded" if s.get("terminal_state") == "abstained" else "guard1",
        {"degraded": "finalize", "guard1": "guard1"},
    )
    graph.add_conditional_edges(
        "guard1", lambda s: "blocked" if s["guard_verdict"] == "blocked" else "critic",
        {"blocked": "finalize", "critic": "critic_verify"},
    )

    def route_after_critic(s: GovernedState) -> str:
        if s.get("terminal_state") == "abstained":  # degraded_mode -- llm.critic() raised
            return "degraded"
        if s["critic_verdict"] == "approve_for_human":
            return "guard2"
        codes = s["critic_reason_codes"]
        latest = codes[-1]
        # PROHIBITION_ADJACENT checked first, unconditionally -- never retried (the
        # earlier-session bug fix this graph must not reintroduce).
        if latest == ReasonCode.PROHIBITION_ADJACENT:
            return "blocked"
        if s["llm_calls"] >= MAX_LLM_CALLS:
            return "abstain"
        if codes.count(latest) > 1:
            return "hitl_escalate"  # repeated code -- escalate, don't retry
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

    def route_after_hitl(s: GovernedState) -> str:
        status = s.get("hitl_status")
        if status == "timed_out":
            return "no_action"
        return "finalize"

    graph.add_conditional_edges("hitl_interrupt", route_after_hitl, {"no_action": "finalize", "finalize": "finalize"})
    graph.add_edge("finalize", END)

    return graph.compile(checkpointer=checkpointer or MemorySaver())
