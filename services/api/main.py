"""Orchestrator API -- the C4 container this belongs to (c4_containers.md).

Wraps the three existing graphs over HTTP. Graph internal logic is unchanged except
HITL resume now accepts an optional justification (G-10) while still accepting the
bare-string resumes used by existing tests.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import UTC, datetime

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command

from packages.config.llm_client import get_llm
from packages.domain.state import new_state
from services.api import pending_queue, run_snapshots
from services.api.graph import build_graph
from services.api.health import collect as collect_health
from services.api.pv_graph import build_pv_graph
from services.api.schemas import (
    DashboardResponse,
    DecideRequest,
    GuardrailEvent,
    QueueEntry,
    RunResult,
    SubmitRunRequest,
)
from services.api.serializers import snapshot_from_state
from services.api.supply_graph import build_supply_graph
from services.integration import audit_store

app = FastAPI(title="AEGIS Pharma AI -- Orchestrator API")

_web = os.environ.get("WEB_ORIGIN", "http://localhost:3000")
_admin = os.environ.get("ADMIN_ORIGIN", "http://localhost:3001")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[_web, _admin, "http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_WORKFLOWS = ("batch_review", "pv_intake", "supply_planning")
_llm = None
_GRAPH_CACHE: dict[tuple[str, str], object] = {}


def _get_llm():
    """Lazy: missing keys must not prevent the API (and workbench) from starting.
    Submit/decide still fail closed with 503 if the client cannot be constructed."""
    global _llm
    if _llm is None:
        try:
            _llm = get_llm()
        except Exception as exc:  # noqa: BLE001 -- KeyError on missing ANTHROPIC_API_KEY/GROQ_API_KEY
            raise HTTPException(503, f"LLM unavailable: {exc}") from exc
    return _llm


def _get_graph(workflow: str, subject_id: str):
    key = (workflow, subject_id)
    if key in _GRAPH_CACHE:
        return _GRAPH_CACHE[key]
    llm = _get_llm()
    if workflow == "batch_review":
        graph = build_graph(llm=llm, batch_id=subject_id)
    elif workflow == "pv_intake":
        graph = build_pv_graph(llm=llm, case_id=subject_id)
    elif workflow == "supply_planning":
        graph = build_supply_graph(llm=llm, product_id=subject_id)
    else:
        raise HTTPException(400, f"Unknown workflow {workflow!r}")
    _GRAPH_CACHE[key] = graph
    return graph


def _status_for(state: dict) -> str:
    if "__interrupt__" in state:
        return "pending_approval"
    terminal = state.get("terminal_state")
    if terminal == "abstained" and state.get("abstention_reason") == "hitl_timeout":
        return "timed_out"
    if terminal in ("completed", "abstained", "blocked", "refused"):
        return terminal
    return "abstained"


def _result_from_snapshot(snap: dict, extra: dict | None = None) -> RunResult:
    data = {**snap, **(extra or {})}
    status = data.get("status") or "abstained"
    if status == "abstained" and data.get("abstention_reason") == "hitl_timeout":
        status = "timed_out"
    return RunResult(
        run_id=data["run_id"],
        workflow=data["workflow"],
        subject_id=data.get("subject_id"),
        requester_role=data.get("requester_role"),
        status=status,
        terminal_state=data.get("terminal_state"),
        abstention_reason=data.get("abstention_reason"),
        llm_calls=data.get("llm_calls"),
        tool_calls=data.get("tool_calls"),
        tokens_in=data.get("tokens_in"),
        tokens_out=data.get("tokens_out"),
        draft_summary=data.get("draft_summary") if status != "blocked" else None,
        draft_claims=data.get("draft_claims") or [] if status != "blocked" else [],
        approver_roles=data.get("approver_roles") or [],
        required_legs=data.get("required_legs"),
        approved_legs=data.get("approved_legs") or [],
        policy_contract_version=data.get("policy_contract_version"),
        hitl_status=data.get("hitl_status"),
        hitl_tier=data.get("hitl_tier"),
        hitl_deadline=data.get("hitl_deadline"),
        veto_recorded=bool(data.get("veto_recorded")),
        evidence=data.get("evidence") or [],
        domain_payload=data.get("domain_payload"),
        critic_verdict=data.get("critic_verdict"),
        critic_reason_codes=data.get("critic_reason_codes") or [],
        guard_verdict=data.get("guard_verdict"),
        trace_id=data.get("trace_id"),
        created_at=data.get("created_at"),
        audit_events=data.get("audit_events") or [],
    )


def _maybe_record_blocked(run_id: str, snap: dict) -> None:
    if snap.get("status") != "blocked" and snap.get("terminal_state") != "blocked":
        return
    summary = snap.get("draft_summary") or ""
    digest = hashlib.sha256(summary.encode("utf-8")).hexdigest() if summary else "none"
    conn = audit_store.get_connection()
    audit_store.write_prohibited_action_blocked(
        conn,
        run_id=run_id,
        matched_terms=["prohibited_action"],
        draft_sha256=digest,
        recorded_at=datetime.now(UTC).isoformat(),
    )


def _persist(workflow: str, subject_id: str, state: dict, created_at: str | None = None) -> dict:
    run_id = state["run_id"]
    snap = snapshot_from_state(run_id, workflow, subject_id, state, created_at=created_at)
    snap["status"] = _status_for(state)
    if snap["status"] == "blocked":
        _maybe_record_blocked(run_id, snap)
        snap["draft_summary"] = None
        snap["draft_claims"] = []
    run_snapshots.upsert(snap)
    if snap["status"] == "pending_approval":
        pending_queue.add(
            pending_queue.PendingEntry(
                run_id=run_id,
                workflow=workflow,
                subject_id=subject_id,
                requester_role=snap.get("requester_role") or "",
                approver_roles=snap.get("approver_roles") or [],
                required_legs=snap.get("required_legs"),
                approved_legs=snap.get("approved_legs") or [],
                draft_summary=snap.get("draft_summary"),
                draft_claims=snap.get("draft_claims") or [],
                created_at=snap["created_at"],
                snapshot=snap,
            )
        )
    else:
        pending_queue.remove(run_id)
    return snap


@app.post("/api/runs", response_model=RunResult)
def submit_run(req: SubmitRunRequest):
    graph = _get_graph(req.workflow, req.subject_id)
    run_id = f"R-web-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": run_id}}
    state = new_state(run_id=run_id, workflow=req.workflow, requester_role=req.requester_role)
    result = graph.invoke(state, config=config)
    snap = _persist(req.workflow, req.subject_id, result)
    return _result_from_snapshot(snap)


@app.get("/api/queue", response_model=list[QueueEntry])
def get_queue(workflow: str | None = None, x_approver_role: str | None = Header(default=None)):
    entries = []
    for e in pending_queue.list_all(workflow):
        snap = e.snapshot or {}
        if x_approver_role:
            if not _role_can_see(x_approver_role, e.workflow, e.approver_roles):
                continue
        entries.append(
            QueueEntry(
                run_id=e.run_id,
                workflow=e.workflow,
                subject_id=e.subject_id,
                requester_role=e.requester_role,
                approver_roles=e.approver_roles,
                required_legs=e.required_legs,
                approved_legs=e.approved_legs,
                draft_summary=e.draft_summary,
                draft_claims=e.draft_claims,
                created_at=e.created_at,
                hitl_tier=snap.get("hitl_tier"),
                hitl_deadline=snap.get("hitl_deadline"),
                policy_contract_version=snap.get("policy_contract_version"),
                critic_reason_codes=snap.get("critic_reason_codes") or [],
                snapshot=snap,
            )
        )
    entries.sort(key=lambda q: q.hitl_deadline or q.created_at)
    return entries


def _role_can_see(role: str, workflow: str, approver_roles: list[str]) -> bool:
    if role in approver_roles:
        return True
    if role == "Patient Safety Representative" and workflow == "pv_intake":
        return True
    if role == "Chief Quality Officer" and workflow in ("batch_review", "supply_planning"):
        return True
    if role == "Chief Medical Officer" and workflow == "pv_intake":
        return True
    return False


@app.get("/api/queue/{run_id}", response_model=RunResult)
def get_queue_item(run_id: str):
    entry = pending_queue.get(run_id)
    if entry is None:
        snap = run_snapshots.get(run_id)
        if snap is None:
            raise HTTPException(404, f"No run {run_id!r}.")
        snap = _attach_audit(snap)
        return _result_from_snapshot(snap)
    snap = dict(entry.snapshot)
    snap = _attach_audit(snap)
    return _result_from_snapshot(snap)


@app.post("/api/runs/{run_id}/decide", response_model=RunResult)
def decide_run(run_id: str, req: DecideRequest):
    entry = pending_queue.get(run_id)
    if entry is None:
        raise HTTPException(404, f"No pending run {run_id!r} -- already decided, or never existed.")

    graph = _get_graph(req.workflow, entry.subject_id)
    config = {"configurable": {"thread_id": run_id}}

    if req.workflow == "supply_planning":
        if req.action == "timed_out":
            resume_value: object = {"action": "timed_out", "justification": req.justification or ""}
        else:
            if req.leg is None:
                raise HTTPException(400, "supply_planning decisions require a leg ('planning' or 'quality').")
            resume_value = {
                "leg": req.leg,
                "action": "rejected" if req.action == "rejected" else "approved",
                "justification": req.justification,
            }
    else:
        resume_value = {"action": req.action, "justification": req.justification or ""}

    result = graph.invoke(Command(resume=resume_value), config=config)
    snap = _persist(req.workflow, entry.subject_id, result, created_at=entry.created_at)

    if "__interrupt__" in result and req.workflow == "supply_planning" and req.action == "approved" and req.leg:
        approved_legs = list(entry.approved_legs)
        if req.leg not in approved_legs:
            approved_legs.append(req.leg)
        pending_queue.update_approved_legs(run_id, approved_legs)
        snap["approved_legs"] = approved_legs
        snap["status"] = "pending_approval"
        run_snapshots.upsert(snap)

    snap = _attach_audit(snap)
    return _result_from_snapshot(snap)


@app.get("/api/runs", response_model=list[RunResult])
def list_runs(workflow: str | None = None, status: str | None = None):
    snaps = run_snapshots.list_all(workflow=workflow, status=status)
    if not snaps:
        # Fall back to audit rows that predate snapshots.
        out = []
        for row in audit_store.list_agent_runs(workflow):
            st = row["terminal_state"]
            if st == "abstained" and row.get("abstention_reason") == "hitl_timeout":
                st = "timed_out"
            out.append(
                RunResult(
                    run_id=row["run_id"],
                    workflow=row["workflow"],
                    status=st,
                    terminal_state=row["terminal_state"],
                    abstention_reason=row.get("abstention_reason"),
                    llm_calls=row.get("llm_calls"),
                    tokens_in=row.get("tokens_in"),
                    tokens_out=row.get("tokens_out"),
                    policy_contract_version=row.get("policy_contract_version"),
                    trace_id=row.get("trace_id"),
                    created_at=row.get("recorded_at"),
                )
            )
        return out
    return [_result_from_snapshot(s) for s in snaps]


@app.get("/api/runs/{run_id}", response_model=RunResult)
def get_run(run_id: str):
    snap = run_snapshots.get(run_id)
    if snap is None:
        entry = pending_queue.get(run_id)
        if entry is not None:
            snap = dict(entry.snapshot)
        else:
            row = audit_store.get_agent_run(run_id)
            if row is None:
                raise HTTPException(404, f"No run {run_id!r}.")
            st = row["terminal_state"]
            if st == "abstained" and row.get("abstention_reason") == "hitl_timeout":
                st = "timed_out"
            snap = {
                "run_id": row["run_id"],
                "workflow": row["workflow"],
                "status": st,
                "terminal_state": row["terminal_state"],
                "abstention_reason": row.get("abstention_reason"),
                "llm_calls": row.get("llm_calls"),
                "tokens_in": row.get("tokens_in"),
                "tokens_out": row.get("tokens_out"),
                "policy_contract_version": row.get("policy_contract_version"),
                "trace_id": row.get("trace_id"),
                "created_at": row.get("recorded_at"),
            }
    snap = _attach_audit(snap)
    return _result_from_snapshot(snap)


def _attach_audit(snap: dict) -> dict:
    run_id = snap["run_id"]
    events: list[dict] = []
    for o in audit_store.list_overrides(run_id):
        events.append({"kind": "HumanOverrideRecorded", **o})
    row = audit_store.get_agent_run(run_id)
    if row:
        events.append(
            {
                "kind": "AgentRun",
                "terminal_state": row["terminal_state"],
                "recorded_at": row["recorded_at"],
                "policy_contract_version": row.get("policy_contract_version"),
            }
        )
        if row.get("abstention_reason") == "hitl_timeout":
            events.append(
                {
                    "kind": "HitlExpired",
                    "abstention_reason": "hitl_timeout",
                    "recorded_at": row["recorded_at"],
                    "message": "No decision was made; resubmit.",
                }
            )
    snap["audit_events"] = events
    return snap


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


@app.get("/api/guardrails", response_model=list[GuardrailEvent])
def guardrails():
    return [GuardrailEvent(**row) for row in audit_store.list_blocked()]


@app.get("/api/governance")
def governance():
    from services.api.sla import SLA
    from services.integration.policy_engine import load_policy_contract

    try:
        contract = load_policy_contract("v1")
        version = contract.get("version", "v1")
        ok = True
        detail = "loaded"
    except Exception as exc:  # noqa: BLE001
        version = None
        ok = False
        detail = str(exc)
        contract = {}
    return {
        "policy_engine_ok": ok,
        "policy_contract_version": version,
        "detail": detail,
        "hitl_ladder": SLA,
        "prohibition_workflows": list((contract.get("prohibition_contracts") or {}).keys()),
        "note": "HITL ladder config is read-only until Stage 16 owns writes.",
    }


@app.get("/api/health")
def health():
    return collect_health()


from services.api.ui import attach_ui

attach_ui(app)
