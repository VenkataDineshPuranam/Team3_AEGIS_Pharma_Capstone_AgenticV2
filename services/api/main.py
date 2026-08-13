"""Orchestrator API -- the C4 container this belongs to (c4_containers.md: "Orchestrator
API... owns the shared state schema and HITL interrupt mechanism" -> services/api).

Wraps the three existing, already-tested graphs (graph.py, pv_graph.py, supply_graph.py)
over HTTP. No changes to any graph's internal logic -- this is purely an HTTP boundary
around code that already works, so every guarantee those graphs' own test suites already
proved (guard behavior, HITL routing, veto, dual-approval, degraded mode, fail-closed
policy engine) holds here unchanged.

Run: uvicorn services.api.main:app --reload --port 8000
"""
from __future__ import annotations

import os
import uuid

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command

from packages.config.llm_client import get_llm
from packages.domain.state import new_state
from services.api import pending_queue
from services.api.graph import build_graph
from services.api.pv_graph import build_pv_graph
from services.api.schemas import (
    DashboardResponse,
    DecideRequest,
    QueueEntry,
    RunResult,
    SubmitRunRequest,
)
from services.api.supply_graph import PLANNING_LEG, QUALITY_LEG, build_supply_graph

app = FastAPI(title="AEGIS Pharma AI -- Orchestrator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("WEB_ORIGIN", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

_WORKFLOWS = ("batch_review", "pv_intake", "supply_planning")
_llm = get_llm()

# Subject-id-parametrized graphs: batch_id/case_id/product_id is baked into the graph
# closure at build time (matches every existing graph module's own design -- it's a
# constructor argument, not a per-run field). To let a single running API serve
# different subject ids without rebuilding a graph per request, build one graph per
# (workflow, subject_id) pair the first time it's requested, and cache it -- each cached
# graph's own MemorySaver is what lets a paused run's state survive between the initial
# submit and the later decide() resume call, same assumption every existing test relies on.
_GRAPH_CACHE: dict[tuple[str, str], object] = {}


def _get_graph(workflow: str, subject_id: str):
    key = (workflow, subject_id)
    if key in _GRAPH_CACHE:
        return _GRAPH_CACHE[key]
    if workflow == "batch_review":
        graph = build_graph(llm=_llm, batch_id=subject_id)
    elif workflow == "pv_intake":
        graph = build_pv_graph(llm=_llm, case_id=subject_id)
    elif workflow == "supply_planning":
        graph = build_supply_graph(llm=_llm, product_id=subject_id)
    else:
        raise HTTPException(400, f"Unknown workflow {workflow!r}")
    _GRAPH_CACHE[key] = graph
    return graph


def _result_from_state(run_id: str, workflow: str, state: dict) -> RunResult:
    draft = state.get("draft_output")
    return RunResult(
        run_id=run_id,
        workflow=workflow,
        status="pending_approval" if "__interrupt__" in state else _status_for(state),
        terminal_state=state.get("terminal_state"),
        abstention_reason=state.get("abstention_reason"),
        llm_calls=state.get("llm_calls"),
        draft_summary=draft.summary if draft else None,
        draft_claims=[c.model_dump() for c in draft.claims] if draft else [],
        approver_roles=state.get("approver_roles") or [],
        required_legs=state.get("hitl_required_legs"),
        approved_legs=state.get("hitl_approved_legs") or [],
    )


def _status_for(state: dict) -> str:
    terminal = state.get("terminal_state")
    if terminal in ("completed", "abstained", "blocked", "refused"):
        return terminal
    return "abstained"  # defensive fallback -- should be unreachable given graph invariants


@app.post("/api/runs", response_model=RunResult)
def submit_run(req: SubmitRunRequest):
    graph = _get_graph(req.workflow, req.subject_id)
    run_id = f"R-web-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": run_id}}
    state = new_state(run_id=run_id, workflow=req.workflow, requester_role=req.requester_role)
    result = graph.invoke(state, config=config)

    if "__interrupt__" in result:
        draft = result.get("draft_output")
        pending_queue.add(
            pending_queue.PendingEntry(
                run_id=run_id, workflow=req.workflow, subject_id=req.subject_id,
                requester_role=req.requester_role,
                approver_roles=result.get("approver_roles") or [],
                required_legs=result.get("hitl_required_legs"),
                approved_legs=result.get("hitl_approved_legs") or [],
                draft_summary=draft.summary if draft else None,
                draft_claims=[c.model_dump() for c in draft.claims] if draft else [],
            )
        )

    return _result_from_state(run_id, req.workflow, result)


@app.get("/api/queue", response_model=list[QueueEntry])
def get_queue(workflow: str | None = None):
    return [
        QueueEntry(
            run_id=e.run_id, workflow=e.workflow, subject_id=e.subject_id,
            requester_role=e.requester_role, approver_roles=e.approver_roles,
            required_legs=e.required_legs, approved_legs=e.approved_legs,
            draft_summary=e.draft_summary, draft_claims=e.draft_claims, created_at=e.created_at,
        )
        for e in pending_queue.list_all(workflow)
    ]


@app.post("/api/runs/{run_id}/decide", response_model=RunResult)
def decide_run(run_id: str, req: DecideRequest):
    entry = pending_queue.get(run_id)
    if entry is None:
        raise HTTPException(404, f"No pending run {run_id!r} -- already decided, or never existed.")

    graph = _get_graph(req.workflow, entry.subject_id)
    config = {"configurable": {"thread_id": run_id}}

    if req.workflow == "supply_planning":
        if req.leg is None:
            raise HTTPException(400, "supply_planning decisions require a leg ('planning' or 'quality').")
        resume_value = {"leg": req.leg, "action": "rejected" if req.action == "rejected" else "approved"}
        if req.action == "timed_out":
            resume_value = "timed_out"
    else:
        resume_value = req.action  # "approved" | "rejected" | "veto" | "timed_out"

    result = graph.invoke(Command(resume=resume_value), config=config)

    if "__interrupt__" in result:
        # supply_planning: one leg approved, still pending the other. NOTE: result's own
        # hitl_approved_legs is NOT yet updated here -- supply_graph.py's hitl_interrupt
        # loops on multiple interrupt() calls inside ONE node execution, and LangGraph
        # only persists a node's state changes once the node function fully returns.
        # Mid-loop (after exactly one leg), the graph's own state snapshot still shows the
        # pre-this-call value, not what we just submitted -- found live, via this exact
        # endpoint. Tracked here instead, from what the API itself just sent, which it
        # knows unambiguously regardless of when the graph's checkpoint catches up.
        approved_legs = list(entry.approved_legs)
        if req.workflow == "supply_planning" and req.action == "approved" and req.leg not in approved_legs:
            approved_legs.append(req.leg)
        pending_queue.update_approved_legs(run_id, approved_legs)
    else:
        pending_queue.remove(run_id)

    response = _result_from_state(run_id, req.workflow, result)
    if "__interrupt__" in result:
        # Same reason as above -- report what the API just tracked, not the graph's
        # not-yet-caught-up snapshot, so the UI shows the real approval progress.
        response.approved_legs = pending_queue.get(run_id).approved_legs
    return response


@app.get("/api/dashboard", response_model=DashboardResponse)
def dashboard(workflow: str | None = None):
    from packages.observability.dashboard_data import (
        cache_hit_rate_panel,
        cost_panel,
        guardrail_trip_panel,
        terminal_state_panel,
    )

    return DashboardResponse(
        workflow=workflow,
        cost=cost_panel(workflow).__dict__,
        guardrail_trip=guardrail_trip_panel(workflow).__dict__,
        terminal_states=terminal_state_panel(workflow).__dict__,
        cache=cache_hit_rate_panel(),
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "workflows": list(_WORKFLOWS)}
