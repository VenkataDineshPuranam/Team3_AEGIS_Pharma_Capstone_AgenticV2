"""Orchestrator API -- the C4 container this belongs to (c4_containers.md: "Orchestrator
API... owns the shared state schema and HITL interrupt mechanism" -> services/api).

Wraps the three existing, already-tested graphs (graph.py, pv_graph.py, supply_graph.py)
over HTTP. No changes to any graph's internal logic -- this is purely an HTTP boundary
around code that already works, so every guarantee those graphs' own test suites already
proved (guard behavior, HITL routing, veto, dual-approval, degraded mode, fail-closed
policy engine) holds here unchanged.

Stage 21 adds READ endpoints (run history, run detail, audit timeline, evidence catalog,
governance snapshot, health detail) so the AEGIS Control Center can show what the system
actually did. They are additive: no existing endpoint's request or response shape changed
except `DecideRequest`, which now requires the justification the audit store was always
supposed to receive.

The one rule this file must never break: the API is a boundary, not a control. Every
governance decision below is made by the graph or the policy engine and reported here.
Nothing in this module decides whether an action is permitted.

Run: uvicorn services.api.main:app --reload --port 8000
"""
from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command

from packages.config.llm_client import get_llm
from packages.domain.state import new_state
from services.api import eval_dashboard, governance_view, health_probe, pending_queue
from services.api.graph import build_graph
from services.api.pv_graph import build_pv_graph
from services.api.research_graph import build_research_graph
from services.api.clinical_graph import build_clinical_graph
from services.api.regulatory_graph import build_regulatory_graph
from services.api.schemas import (
    AuditedRun,
    AuditEvent,
    DashboardResponse,
    DecideRequest,
    EvalScorecard,
    EvidenceCatalogItem,
    GovernanceSnapshot,
    HealthDetail,
    InjectCoverage,
    QueueEntry,
    RunDetail,
    RunHistoryPage,
    RunResult,
    SubmitRunRequest,
)
from services.api.supply_graph import PLANNING_LEG, QUALITY_LEG, build_supply_graph
from services.integration import audit_store, evidence_catalog

app = FastAPI(title="AEGIS Pharma AI -- Orchestrator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("WEB_ORIGIN", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

_WORKFLOWS = (
    "batch_review", "pv_intake", "supply_planning",
    "research_review", "clinical_integrity", "regulatory_completeness",
)
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
    elif workflow == "research_review":
        graph = build_research_graph(llm=_llm, research_id=subject_id)
    elif workflow == "clinical_integrity":
        graph = build_clinical_graph(llm=_llm, protocol_id=subject_id)
    elif workflow == "regulatory_completeness":
        graph = build_regulatory_graph(llm=_llm, submission_id=subject_id)
    else:
        raise HTTPException(400, f"Unknown workflow {workflow!r}")
    _GRAPH_CACHE[key] = graph
    return graph


def _evidence_dicts(state: dict) -> list[dict]:
    """EvidenceItems from a run's state, as JSON. These are already ADR-003-filtered by
    construction -- an item could not be in state otherwise."""
    return [e.model_dump(mode="json") for e in (state.get("evidence") or [])]


def _payload_dict(state: dict) -> dict | None:
    payload = state.get("domain_payload")
    return payload.model_dump(mode="json") if payload is not None else None


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
        veto_recorded=bool(state.get("veto_recorded")),
    )


def _status_for(state: dict) -> str:
    terminal = state.get("terminal_state")
    if terminal in ("completed", "abstained", "blocked", "refused"):
        return terminal
    return "abstained"  # defensive fallback -- should be unreachable given graph invariants


def _queue_entry(e: pending_queue.PendingEntry) -> QueueEntry:
    return QueueEntry(
        run_id=e.run_id, workflow=e.workflow, subject_id=e.subject_id,
        requester_role=e.requester_role, approver_roles=e.approver_roles,
        required_legs=e.required_legs, approved_legs=e.approved_legs,
        draft_summary=e.draft_summary, draft_claims=e.draft_claims, created_at=e.created_at,
        evidence=e.evidence, domain_payload=e.domain_payload,
    )


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
                evidence=_evidence_dicts(result),
                domain_payload=_payload_dict(result),
            )
        )

    return _result_from_state(run_id, req.workflow, result)


@app.get("/api/queue", response_model=list[QueueEntry])
def get_queue(workflow: str | None = None):
    return [_queue_entry(e) for e in pending_queue.list_all(workflow)]


@app.post("/api/runs/{run_id}/decide", response_model=RunResult)
def decide_run(run_id: str, req: DecideRequest):
    """Resume a paused run with a human's decision.

    This endpoint is never retried automatically by any client, and must not be: it
    records an irreversible human action in an append-only store. The API layer enforces
    only shape here (a justification of real length, a leg where the workflow needs one);
    every governance consequence -- whether a veto stands, whether one leg is enough, what
    a timeout means -- is decided inside the graph, unchanged from before this endpoint
    existed.
    """
    entry = pending_queue.get(run_id)
    if entry is None:
        raise HTTPException(404, f"No pending run {run_id!r} -- already decided, or never existed.")

    if req.workflow != entry.workflow:
        # The client sends the workflow it believes it is deciding. If that disagrees with
        # the paused run, something is out of sync -- resolving it by trusting either side
        # would resume the wrong graph, so refuse instead.
        raise HTTPException(409, "Workflow does not match the pending run.")

    graph = _get_graph(req.workflow, entry.subject_id)
    config = {"configurable": {"thread_id": run_id}}

    if req.workflow == "supply_planning":
        if req.action == "veto":
            raise HTTPException(400, "Veto applies to pv_intake only.")
        if req.action != "timed_out" and req.leg is None:
            raise HTTPException(400, "supply_planning decisions require a leg ('planning' or 'quality').")
        if req.leg is not None and req.leg in entry.approved_legs:
            raise HTTPException(409, f"The {req.leg} leg has already been approved for this run.")
    elif req.action == "veto" and req.workflow != "pv_intake":
        raise HTTPException(400, "Veto applies to pv_intake only.")

    resume_value = {
        "action": req.action,
        "justification": req.justification,
        "claimed_identity": req.claimed_identity,
        "leg": req.leg,
    }
    if req.action == "timed_out":
        # A timeout is not a human action and carries no justification -- it is the
        # ABSENCE of one. Sent as the bare legacy string so every graph takes exactly the
        # timeout path its own tests already cover.
        resume_value = "timed_out"

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


# ---------------------------------------------------------------------------
# Read endpoints (Stage 21)
# ---------------------------------------------------------------------------


@app.get("/api/runs", response_model=RunHistoryPage)
def list_runs(
    workflow: str | None = None,
    terminal_state: str | None = None,
    subject_id: str | None = None,
    search: str | None = None,
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Historical runs, from the append-only audit store. Newest first."""
    conn = audit_store.get_connection()
    try:
        rows, total = audit_store.list_agent_runs(
            conn, workflow=workflow, terminal_state=terminal_state,
            subject_id=subject_id, search=search, limit=limit, offset=offset,
        )
    finally:
        conn.close()
    return RunHistoryPage(
        items=[AuditedRun(**r) for r in rows], total=total, limit=limit, offset=offset
    )


@app.get("/api/runs/filters")
def run_filters():
    """Distinct values actually present in the audit store, so the History page's filters
    offer what exists rather than a hardcoded list that may not match the data."""
    conn = audit_store.get_connection()
    try:
        return {
            column: audit_store.distinct_values(conn, column)
            for column in ("workflow", "terminal_state", "requester_role", "abstention_reason")
        }
    finally:
        conn.close()


@app.get("/api/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: str):
    """One run, from both sources that can know about it: the in-memory pending registry
    (only while it is still paused in THIS process) and the audit store (once finalized).

    Neither being present is a real 404. One being present without the other is normal and
    is reported as-is -- a paused run has no audit record yet, and a run decided before
    this process started has no pending entry, which is why `decision_support_available`
    exists rather than leaving the UI to guess what an empty field means.
    """
    pending = pending_queue.get(run_id)
    conn = audit_store.get_connection()
    try:
        audited = audit_store.get_agent_run(conn, run_id)
        timeline = audit_store.run_timeline(conn, run_id)
        overrides = audit_store.human_overrides(conn, run_id)
    finally:
        conn.close()

    if pending is None and audited is None:
        raise HTTPException(404, f"No run {run_id!r} is pending or recorded.")

    reason = None
    if pending is None:
        reason = (
            "The decision-support package (draft summary, claims, evidence and structured "
            "findings) is held in the run's own graph state while it is paused for approval. "
            "It is not copied into the append-only audit store, so it is unavailable for a run "
            "that has already been decided, or that was decided before this API process started. "
            "The audit record and timeline below are complete and authoritative."
        )

    return RunDetail(
        run_id=run_id,
        pending=_queue_entry(pending) if pending else None,
        audit=AuditedRun(**audited) if audited else None,
        timeline=[AuditEvent(**e) for e in timeline],
        human_actions=overrides,
        decision_support_available=pending is not None,
        decision_support_unavailable_reason=reason,
    )


@app.get("/api/evidence", response_model=list[EvidenceCatalogItem])
def list_evidence():
    """The evidence corpus, INCLUDING non-citable items, each labelled with whether it may
    be relied upon. See services/integration/evidence_catalog.py for why showing them here
    does not weaken the rule that a run can never retrieve them."""
    try:
        return [EvidenceCatalogItem(**item) for item in evidence_catalog.list_catalog()]
    except evidence_catalog.CatalogUnavailable as exc:
        raise HTTPException(503, f"Knowledge graph unavailable: {exc}") from exc


@app.get("/api/evidence/stats")
def evidence_stats():
    try:
        return evidence_catalog.catalog_stats()
    except evidence_catalog.CatalogUnavailable as exc:
        raise HTTPException(503, f"Knowledge graph unavailable: {exc}") from exc


@app.get("/api/governance", response_model=GovernanceSnapshot)
def governance():
    return GovernanceSnapshot(**governance_view.snapshot())


@app.get("/api/evals/scorecard", response_model=EvalScorecard)
def evals_scorecard():
    """Runs the real eval-ai-cache harness in-process, live, on every request -- see
    eval_dashboard.py's module docstring for why this one is safe to compute per-request
    (pure grading logic against synthetic fixtures, ~25ms, no LLM/network calls) while
    inject coverage below is not."""
    return EvalScorecard(**eval_dashboard.eval_scorecard())


@app.get("/api/coverage/injects", response_model=InjectCoverage)
def inject_coverage():
    """The curated V2-inject-to-V3-reality coverage mapping. Read-only; there is no
    endpoint that can write to this file."""
    try:
        return InjectCoverage(**eval_dashboard.inject_coverage())
    except eval_dashboard.InjectCoverageUnavailable as exc:
        raise HTTPException(503, f"Inject coverage data unavailable: {exc}") from exc


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


@app.get("/api/health/detail", response_model=HealthDetail)
def health_detail():
    """Measured dependency health -- every entry is the result of actually touching the
    dependency, except the LLM provider, which reports configuration and says so."""
    conn = audit_store.get_connection()
    try:
        stats = audit_store.store_stats(conn)
    finally:
        conn.close()
    return HealthDetail(
        api=health_probe.DependencyHealth(
            name="Orchestrator API", status="ok",
            detail=f"Serving workflows: {', '.join(_WORKFLOWS)}. "
                   f"{len(pending_queue.list_all())} run(s) currently awaiting a decision.",
        ),
        dependencies=health_probe.all_dependencies(),
        audit_store=stats,
        checked_at=datetime.now(UTC).isoformat(),
    )
