"""HTML workbench routes — Jinja + HTMX, same origin as /api."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from services.api import pending_queue, run_snapshots
from services.api.health import collect as collect_health
from services.api.ui import seed
from services.api.ui.context import (
    DEFAULT_ROLE,
    FINDING_LABELS,
    NAV,
    ROLES,
    WORKFLOW_LABEL,
    can_approve,
    can_see_workflow,
    can_veto,
    enrich,
    role_by_id,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.globals["finding_labels"] = FINDING_LABELS
templates.env.autoescape = True

ROLE_COOKIE = "aegis_role"
SLA_NOTE = {
    "batch_review": "Business-hours ladder (UI approximation until P-08).",
    "pv_intake": "Wall clock — does not pause on weekends.",
    "supply_planning": "Business-hours ladder. Both legs required.",
}
WORKSPACE = {
    "batch_review": (
        "batch",
        "GxP Batch Review",
        "Reconcile genealogy, lab, EM, deviations, CAPA, change control, validation, supplier, and packet completeness. This desk cannot release, reject, reprocess, relabel, or recall a batch.",
    ),
    "pv_intake": (
        "pv",
        "PV Intake",
        "Duplicate check and terminology suggestions only. This desk cannot determine causality, seriousness, expectedness, reportability, or confirm a signal.",
    ),
    "supply_planning": (
        "supply",
        "Supply Planning",
        "Rank constraint-filtered options. Dual-leg: Supply Chain VP (planning) and Quality (QP / CQO). This desk cannot allocate, reserve, ship, or recall.",
    ),
}


def _role(request: Request) -> dict:
    return role_by_id(request.cookies.get(ROLE_COOKIE) or DEFAULT_ROLE)


def _queue(role: dict, workflow: str | None = None, *, scoped: bool = False) -> list[dict]:
    seed.ensure()
    out = []
    for e in pending_queue.list_all(workflow):
        snap = dict(e.snapshot or {})
        snap.setdefault("run_id", e.run_id)
        snap.setdefault("workflow", e.workflow)
        snap.setdefault("subject_id", e.subject_id)
        snap.setdefault("status", "pending_approval")
        if scoped and not can_see_workflow(role, e.workflow, e.approver_roles):
            continue
        out.append(enrich(snap))
    out.sort(key=lambda r: r.get("hitl_deadline") or r.get("created_at") or "")
    return out


def _runs(status: str | None = None) -> list[dict]:
    seed.ensure()
    return [enrich(s) for s in run_snapshots.list_all(status=status)]


def _base(request: Request, title: str, nav_active: str, **extra):
    role = _role(request)
    health = collect_health()
    ctx = {
        "request": request,
        "title": title,
        "nav_active": nav_active,
        "nav": NAV,
        "roles": ROLES,
        "role": role,
        "health": health,
        "pending_count": len(_queue(role)),
        "subtitle": extra.pop("subtitle", None),
    }
    ctx.update(extra)
    return ctx


@router.post("/session/role")
def set_role(request: Request, role: str = Form(...)):
    dest = RedirectResponse(request.headers.get("referer") or "/", status_code=303)
    dest.set_cookie(ROLE_COOKIE, role, httponly=False, samesite="lax")
    return dest


@router.get("/")
def home(request: Request):
    seed.ensure()
    role = _role(request)
    pending = _queue(role)
    at_risk = sum(1 for r in pending if r.get("sla") and r["sla"]["tone"] in ("warn", "bad"))
    lanes = []
    for wf, cls in (("batch_review", "batch"), ("pv_intake", "pv"), ("supply_planning", "supply")):
        items = [r for r in pending if r["workflow"] == wf][:5]
        lanes.append((wf, WORKFLOW_LABEL[wf], cls, items))
    return templates.TemplateResponse(
        request,
        "home.html",
        _base(
            request,
            "Command",
            "home",
            subtitle="Open cases on this desk. Accepting a pack is not a terminal GxP action.",
            at_risk=at_risk,
            history_count=len(_runs()),
            lanes=lanes,
        ),
    )


@router.get("/inbox")
def inbox(request: Request, workflow: str | None = Query(default=None)):
    role = _role(request)
    entries = _queue(role, workflow)
    return templates.TemplateResponse(
        request,
        "inbox.html",
        _base(
            request,
            "Inbox",
            "inbox",
            subtitle="HITL queue, sorted by clock. Silence is not approval.",
            entries=entries,
            workflow=workflow,
        ),
    )


@router.get("/partials/inbox")
def inbox_partial(request: Request, workflow: str | None = Query(default=None)):
    entries = _queue(_role(request), workflow)
    return templates.TemplateResponse(request, "partials/inbox_table.html", {"request": request, "entries": entries})


@router.get("/partials/health")
def health_partial(request: Request):
    return templates.TemplateResponse(
        request,
        "partials/health.html",
        {"request": request, "health": collect_health()},
    )


@router.get("/batch")
def batch_ws(request: Request):
    return _workspace(request, "batch_review")


@router.get("/pv")
def pv_ws(request: Request):
    return _workspace(request, "pv_intake")


@router.get("/supply")
def supply_ws(request: Request):
    return _workspace(request, "supply_planning")


def _workspace(request: Request, workflow: str):
    key, title, blurb = WORKSPACE[workflow]
    role = _role(request)
    entries = _queue(role, workflow)
    return templates.TemplateResponse(
        request,
        "workspace.html",
        _base(request, title, key, subtitle=blurb, entries=entries, workflow=workflow, blurb=blurb),
    )


@router.get("/history")
def history(request: Request, status: str | None = Query(default=None)):
    runs = _runs(status)
    return templates.TemplateResponse(
        request,
        "history.html",
        _base(
            request,
            "History",
            "history",
            subtitle="Completed, blocked, refused, and T3 timeout (no decision was made; resubmit).",
            runs=runs,
            status=status,
        ),
    )


@router.get("/submit")
def submit_get(request: Request, error: str | None = None):
    return templates.TemplateResponse(
        request,
        "submit.html",
        _base(request, "New run", "submit", subtitle="Live graph invocation.", error=error),
    )


@router.post("/submit")
def submit_post(
    request: Request,
    workflow: str = Form(...),
    subject_id: str = Form(...),
    requester_role: str = Form(...),
):
    from services.api.main import submit_run
    from services.api.schemas import SubmitRunRequest

    try:
        result = submit_run(SubmitRunRequest(workflow=workflow, subject_id=subject_id, requester_role=requester_role))
    except HTTPException as exc:
        return submit_get(request, error=str(exc.detail))
    except Exception as exc:  # noqa: BLE001
        return submit_get(request, error=str(exc))
    return RedirectResponse(f"/cases/{result.run_id}", status_code=303)


@router.get("/cases/{run_id}")
def case_file(request: Request, run_id: str):
    seed.ensure()
    from services.api.main import get_run

    try:
        result = get_run(run_id)
        run = enrich(result.model_dump())
    except HTTPException:
        snap = run_snapshots.get(run_id)
        if snap is None:
            raise
        run = enrich(snap)
    role = _role(request)
    return templates.TemplateResponse(
        request,
        "case.html",
        _base(
            request,
            f"Case {run.get('subject_id') or run_id}",
            "inbox" if run.get("status") == "pending_approval" else "history",
            subtitle="Evidence pack — not a disposition.",
            run=run,
            can_act=can_approve(role, run["workflow"]) ,
            can_veto=can_veto(role, run["workflow"]),
            sla_note=SLA_NOTE.get(run["workflow"], ""),
        ),
    )


@router.post("/cases/{run_id}/decide")
def case_decide(
    request: Request,
    run_id: str,
    workflow: str = Form(...),
    action: str = Form(...),
    justification: str = Form(""),
    leg: str | None = Form(default=None),
):
    role = _role(request)
    text = justification.strip()
    if len(text) < 8:
        raise HTTPException(400, "justification is required (G-10).")
    snap = run_snapshots.get(run_id) or {}
    if snap.get("demo_seed"):
        seed.apply_demo_decision(
            snap,
            action=action,
            justification=text,
            leg=leg,
            actor_role=role["id"],
        )
        return RedirectResponse(f"/cases/{run_id}", status_code=303)

    from services.api.main import decide_run
    from services.api.schemas import DecideRequest

    try:
        decide_run(
            run_id,
            DecideRequest(workflow=workflow, action=action, justification=text, leg=leg or None),  # type: ignore[arg-type]
        )
    except HTTPException as exc:
        return templates.TemplateResponse(
            request,
            "submit.html",
            _base(request, "Decision failed", "inbox", error=str(exc.detail)),
            status_code=exc.status_code,
        )
    return RedirectResponse(f"/cases/{run_id}", status_code=303)


@router.get("/ops")
def ops_health(request: Request):
    from services.api.main import dashboard

    dash = dashboard()
    return templates.TemplateResponse(
        request,
        "ops.html",
        _base(request, "Ops · Health", "ops", subtitle="Degraded mode is visible, never silent.", tab="health", dash=dash),
    )


@router.get("/ops/runs")
def ops_runs(request: Request):
    return templates.TemplateResponse(
        request,
        "ops.html",
        _base(request, "Ops · Run inspector", "ops", tab="runs", runs=_runs(), dash=None, guardrails=[], gov=None),
    )


@router.get("/ops/guardrails")
def ops_guardrails(request: Request):
    from services.api.main import guardrails as list_guardrails

    rows = [g.model_dump() if hasattr(g, "model_dump") else dict(g) for g in list_guardrails()]
    return templates.TemplateResponse(
        request,
        "ops.html",
        _base(request, "Ops · Guardrails", "ops", tab="guardrails", guardrails=rows, dash=None, runs=[], gov=None),
    )


@router.get("/ops/governance")
def ops_governance(request: Request):
    from services.api.main import governance

    return templates.TemplateResponse(
        request,
        "ops.html",
        _base(request, "Ops · Governance", "ops", tab="governance", gov=governance(), dash=None, runs=[], guardrails=[]),
    )
