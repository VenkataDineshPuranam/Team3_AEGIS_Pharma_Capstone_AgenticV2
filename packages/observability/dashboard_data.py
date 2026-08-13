"""Dashboard data -- Stage 20b Phase 6. Makes dashboards.md SS1's panels computable from
real data, now that three workflows + a cache exist. NOT a UI -- these functions compute
the numbers a real dashboard would render, queried from evidence/audit_store.sqlite3 and
Redis. Closes dashboards.md SS3's "designed, not populated" gap for these specific panels.

Every function here is workflow-filterable, per dashboards.md SS4 (RR-2/T-10: never
present an aggregate that would misrepresent a workflow with no real data yet).
"""
from __future__ import annotations

from dataclasses import dataclass

from services.integration.audit_store import get_connection


@dataclass(frozen=True)
class CostPanel:
    """dashboards.md SS1: 'Tokens/run (distribution + p95), cost/run vs. Stage 15 budget,
    per-node token breakdown.' Per-node breakdown is NOT computable from agent_run alone
    (it only has run-total tokens) -- that granularity lives in LangSmith traces, named
    honestly as still-design-only below, not fabricated here."""

    run_count: int
    mean_tokens_per_run: float | None
    p95_tokens_per_run: float | None
    mean_llm_calls_per_run: float | None


@dataclass(frozen=True)
class GuardrailTripPanel:
    """dashboards.md SS1: 'ProhibitedActionBlocked, critic_reject_rate by reason code,
    hitl_escalation_skipped by condition.' critic_reject_rate needs per-attempt reason-code
    data LangSmith traces carry, not agent_run -- named honestly as not computable here."""

    run_count: int
    blocked_count: int
    blocked_rate: float | None


@dataclass(frozen=True)
class TerminalStatePanel:
    """Not one of dashboards.md's five named panels verbatim, but the input every other
    panel's rate calculations need -- included so the module is self-contained rather than
    silently assuming a caller has this breakdown already."""

    run_count: int
    by_terminal_state: dict[str, int]
    by_abstention_reason: dict[str, int]


def cost_panel(workflow: str | None = None) -> CostPanel:
    conn = get_connection()
    where = "WHERE workflow = ? AND tokens_in IS NOT NULL" if workflow else "WHERE tokens_in IS NOT NULL"
    params = (workflow,) if workflow else ()
    rows = conn.execute(
        f"SELECT tokens_in + tokens_out AS total_tokens, llm_calls FROM agent_run {where}", params
    ).fetchall()
    if not rows:
        return CostPanel(run_count=0, mean_tokens_per_run=None, p95_tokens_per_run=None, mean_llm_calls_per_run=None)

    totals = sorted(r[0] for r in rows)
    calls = [r[1] for r in rows if r[1] is not None]
    p95_index = min(len(totals) - 1, int(len(totals) * 0.95))
    return CostPanel(
        run_count=len(rows),
        mean_tokens_per_run=sum(totals) / len(totals),
        p95_tokens_per_run=float(totals[p95_index]),
        mean_llm_calls_per_run=(sum(calls) / len(calls)) if calls else None,
    )


def guardrail_trip_panel(workflow: str | None = None) -> GuardrailTripPanel:
    conn = get_connection()
    where = "WHERE workflow = ?" if workflow else ""
    params = (workflow,) if workflow else ()
    total = conn.execute(f"SELECT COUNT(*) FROM agent_run {where}", params).fetchone()[0]
    blocked_where = (where + " AND" if where else "WHERE") + " terminal_state = 'blocked'"
    blocked = conn.execute(f"SELECT COUNT(*) FROM agent_run {blocked_where}", params).fetchone()[0]
    return GuardrailTripPanel(
        run_count=total, blocked_count=blocked, blocked_rate=(blocked / total) if total else None,
    )


def terminal_state_panel(workflow: str | None = None) -> TerminalStatePanel:
    conn = get_connection()
    where = "WHERE workflow = ?" if workflow else ""
    params = (workflow,) if workflow else ()
    total = conn.execute(f"SELECT COUNT(*) FROM agent_run {where}", params).fetchone()[0]
    by_state: dict[str, int] = {}
    for row in conn.execute(f"SELECT terminal_state, COUNT(*) FROM agent_run {where} GROUP BY terminal_state", params):
        by_state[row[0]] = row[1]
    by_reason: dict[str, int] = {}
    reason_where = (where + " AND" if where else "WHERE") + " abstention_reason IS NOT NULL"
    for row in conn.execute(f"SELECT abstention_reason, COUNT(*) FROM agent_run {reason_where} GROUP BY abstention_reason", params):
        by_reason[row[0]] = row[1]
    return TerminalStatePanel(run_count=total, by_terminal_state=by_state, by_abstention_reason=by_reason)


def cache_hit_rate_panel() -> dict:
    """dashboards.md SS1 Cache panel. Real Redis INCR counters (response_cache.py), not a
    proxy -- a stale (superseded-evidence) entry counts as a miss, which is the same event
    the 'stale-serve count must be zero' guarantee depends on: this counter and that
    guarantee can never diverge, by construction, not by convention."""
    from services.integration.response_cache import hit_rate_stats

    return hit_rate_stats()
