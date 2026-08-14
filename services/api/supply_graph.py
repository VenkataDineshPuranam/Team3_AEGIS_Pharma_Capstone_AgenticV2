"""supply_planning LangGraph -- Stage 20b. Same spine as batch_review/pv_intake
(langgraph_design.md SS7). The one genuinely new mechanism here: **dual-approval HITL** --
`hitl_control_model.md` SS2's dual-approval structure (Supply Chain VP's planning leg +
Quality's leg) means a single `hitl_interrupt` call is not enough; both legs must approve
independently, and one approving is NOT approval (`failure_and_loop_guards.md` SS5.4:
"partial approval is not approval -- it expires to no action like any other incomplete
approval").

Deliberately not sharing code with graph.py/pv_graph.py -- RR-2/T-10, same reasoning as
pv_graph.py's module docstring.
"""
from __future__ import annotations

from datetime import UTC, datetime

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from packages.domain import hitl_decision
from packages.domain.payloads import ConstraintSet, ShortageOption, SupplyPayload
from packages.domain.evidence import EvidenceItem
from packages.domain.state import GovernedState, ReasonCode, RETRYABLE_REASON_CODES
from infra.policies.denial_of_wallet_guardrail import DenialOfWalletGuard
from services.integration import audit_store, evidence_gate, prohibited_action_guard
from services.integration.evidence_retrieve import ToolError as RetrieveError, retrieve as tool_retrieve
from services.integration.supply_generate_options import ToolError as OptionsError, generate_options as tool_generate_options
from services.integration.policy_engine import PolicyEngineUnavailable, get_prohibition_contract
from services.api.nodes.llm_interface import LLMNodes, StubLLM

POLICY_VERSION = "v1"
MAX_LLM_CALLS = 6

SUPPLY_PLANNING_APPROVER = "Supply Chain VP"  # hitl_control_model.md SS2, planning leg
SUPPLY_QUALITY_APPROVER = "EU Qualified Person"  # Quality co-approval leg
PLANNING_LEG = "planning"
QUALITY_LEG = "quality"


def build_supply_graph(llm: LLMNodes | None = None, product_id: str = "P-100", checkpointer=None):
    llm = llm or StubLLM()
    audit_conn = audit_store.get_connection()
    dow_guard = DenialOfWalletGuard()

    def intake(state: GovernedState) -> dict:
        admission = dow_guard.check_and_admit(
            user_id=state["requester_role"], workflow=state["workflow"], as_of=datetime.now(UTC).date()
        )
        if not admission["admit"]:
            return {
                "authorization_checked_at": datetime.now(UTC), "trace_id": f"TR-{state['run_id']}",
                "terminal_state": "refused", "abstention_reason": admission["reason"],
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
                run_id=state["run_id"], terms=["SUPPLY", "COLD_CHAIN", "policy"],
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

    def generate_options_node(state: GovernedState) -> dict:
        evidence_ids = [e.evidence_id for e in state["evidence"]]
        try:
            result = tool_generate_options(
                run_id=state["run_id"], product_id=product_id, constraint_set={}, evidence_ids=evidence_ids,
            )
        except OptionsError as exc:
            if exc.code == "CONSTRAINT_SET_EMPTY_RESULT":
                # agent_roster.md SS2: abstain -- agent has nothing to rank.
                return {"terminal_state": "abstained", "abstention_reason": "insufficient_evidence"}
            return {"terminal_state": "abstained", "abstention_reason": "dependency_unavailable"}
        options = tuple(ShortageOption(**o) for o in result["options"])
        payload = SupplyPayload(
            product_id=product_id, options=options, constraint_set=ConstraintSet(),
            inventory_snapshot_version=result["inventory_snapshot_version"],
            allocation_ethics_flags=tuple(result.get("allocation_ethics_flags") or ()),  # Stage 21, INJ-056
        )
        return {"domain_payload": payload, "tool_calls": state["tool_calls"] + 1}

    def synthesize(state: GovernedState) -> dict:
        try:
            draft, tin, tout = llm.synthesize(state)
        except Exception:  # noqa: BLE001
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
        # Dual approval: BOTH legs required, per hitl_control_model.md SS2. No escalation
        # role exists for the planning leg (failure_and_loop_guards.md SS5.4) -- only the
        # Quality leg can ever widen at T2, not modeled in this 20b scope (no real clock
        # wiring exists for any workflow yet, same simplification as batch_review/pv_intake).
        return {
            "hitl_required": True,
            "approver_roles": [SUPPLY_PLANNING_APPROVER, SUPPLY_QUALITY_APPROVER],
            "hitl_required_legs": [PLANNING_LEG, QUALITY_LEG],
            "hitl_approved_legs": [],
            "hitl_status": "pending", "hitl_tier": "T0",
        }

    def hitl_interrupt(state: GovernedState) -> dict:
        """Loops on interrupt() until both legs approve, one leg rejects, or a timeout
        arrives. One leg approving alone is not approval -- the loop simply doesn't exit."""
        approved_legs = list(state.get("hitl_approved_legs") or [])
        required_legs = state["hitl_required_legs"]

        while set(approved_legs) < set(required_legs):
            decision = hitl_decision.decode(interrupt(
                {
                    "approver_roles": state["approver_roles"], "run_id": state["run_id"],
                    "product_id": product_id, "required_legs": required_legs, "approved_legs": approved_legs,
                }
            ))
            if decision.action == "timed_out":
                audit_store.write_hitl_expired(
                    audit_conn, state["run_id"], state["workflow"],
                    eligible_roles_at_expiry=state["approver_roles"], recorded_at=datetime.now(UTC).isoformat(),
                )
                return {
                    "hitl_status": "timed_out", "hitl_approved_legs": approved_legs,
                    "terminal_state": "abstained", "abstention_reason": "hitl_timeout",
                }
            # The role recorded is derived from the LEG, not from anything the submitter
            # claimed about themselves -- a caller cannot file the Quality leg's approval
            # under the Supply Chain VP's name, or vice versa.
            if decision.action == "rejected":
                role = SUPPLY_QUALITY_APPROVER if decision.leg == QUALITY_LEG else SUPPLY_PLANNING_APPROVER
                audit_store.write_human_override(
                    audit_conn, state["run_id"], role=role, tier_at_action=state.get("hitl_tier") or "T0",
                    action="rejected", justification=decision.justification,
                    recorded_at=datetime.now(UTC).isoformat(),
                )
                return {"hitl_status": "rejected", "hitl_approved_legs": approved_legs, "terminal_state": "completed"}
            if decision.action == "approved":
                leg = decision.leg
                role = SUPPLY_QUALITY_APPROVER if leg == QUALITY_LEG else SUPPLY_PLANNING_APPROVER
                # Stage 21 gap-closure (INJ-080: checkpoint corruption / duplicate writes
                # on resume). LangGraph re-executes this node's Python code from the top
                # on every resume, replaying each already-consumed interrupt()'s return
                # value -- so on a later resume, this branch runs AGAIN for a leg that was
                # already approved during an earlier invoke() call, with `approved_legs`
                # freshly rebuilt as [] from the still-stale checkpointed state (that
                # state is only persisted once this whole node function returns). An
                # in-memory `if leg not in approved_legs` guard is reset by the same
                # replay it's supposed to guard against. The audit store itself -- not
                # memory -- is the only thing that actually remembers a prior write, so
                # it is the only thing that can make this check replay-safe.
                if not audit_store.has_recorded_action(audit_conn, state["run_id"], role, "approved"):
                    audit_store.write_human_override(
                        audit_conn, state["run_id"], role=role, tier_at_action=state.get("hitl_tier") or "T0",
                        action="approved", justification=decision.justification,
                        recorded_at=datetime.now(UTC).isoformat(),
                    )
                if leg not in approved_legs:
                    approved_legs = approved_legs + [leg]

        return {"hitl_status": "approved", "hitl_approved_legs": approved_legs, "terminal_state": "completed"}

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
            subject_id=product_id, requester_role=state["requester_role"],
            approver_roles=state.get("approver_roles") or [], hitl_status=state.get("hitl_status"),
            evidence_ids=[e.evidence_id for e in state["evidence"]],
        )
        return {"terminal_state": terminal, "audit_record_id": audit_record_id}

    graph = StateGraph(GovernedState)
    graph.add_node("intake", intake)
    graph.add_node("policy_load", policy_load)
    graph.add_node("retrieve", retrieve)
    graph.add_node("evidence_gate", evidence_gate_node)
    graph.add_node("generate_options", generate_options_node)
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
            return "generate_options"
        return "retrieve"

    graph.add_conditional_edges(
        "evidence_gate", route_after_gate,
        {"terminal": "finalize", "generate_options": "generate_options", "retrieve": "retrieve"},
    )
    graph.add_conditional_edges(
        "generate_options", lambda s: "abstain" if s.get("terminal_state") == "abstained" else "synthesize",
        {"abstain": "finalize", "synthesize": "synthesize"},
    )
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
