# Dashboards — Stage 17

**Executes:** `prompts/21_observability.md` §2
**Consumes:** `tracing_design.md` (span fields), `alerting.md` (severity taxonomy, thresholds),
Stage 15 (`token_economics.md`, `latency_budget.md`), Stage 14 (`scorecard.md`,
`release_gates.md`)
**Artifact status:** `provisional`

---

## 1. Dashboard set (per `prompts/21`'s named list)

| Dashboard | Primary metrics | Sourced from | Audience (`rbac_model.md` §3) |
|---|---|---|---|
| **Cost** | Tokens/run (distribution + p95), cost/run vs. Stage 15 budget, per-node token breakdown | `tracing_design.md` §2 (`synthesize`/`critic_verify` token counts) | Architecture owner, Platform Operator |
| **Latency** | Wall-clock/run vs. G6 (300s), per-node latency, `hitl.wait` elapsed (excluded from G6 per `failure_and_loop_guards.md` §2) | `tracing_design.md` §2 | Platform Operator |
| **Eval-score trend** | Gate pass/fail rate by category, trend across releases | `release_gates.md`, `scorecard.md` (Stage 14) | Governance & Oversight owner, Compliance Reviewer |
| **Cache hit-rate** | Hit rate, stale-serve count (must be zero — `G-CACHE_STALE_SERVE`) | Stage 15/20b (cache not yet built — see §3) | Architecture owner |
| **Guardrail-trip rate** | `ProhibitedActionBlocked`, `critic_reject_rate` by reason code, `hitl_escalation_skipped` by condition | `tracing_design.md` §2, `alerting.md` §3 | Governance & Oversight owner |

## 2. Severity distribution panel — new, ties dashboards to `alerting.md`

Every dashboard above carries one shared panel: **event count by severity (SEV-1…SEV-4),
trailing 30 days**, filterable by workflow. This is the one piece of `alerting.md`'s taxonomy
that belongs on every dashboard rather than a single one — without it, a viewer of (say) the
Latency dashboard has no way to tell whether a metric moved for a benign reason (SEV-4,
`abstention_rate` review) or a serious one (SEV-1, `AgentAuthorityExceeded`) without switching
to a separate alert log.

## 3. Honest gaps — what cannot be populated yet

| Dashboard | Gap | Why | Closes at |
|---|---|---|---|
| Cache hit-rate | No data — cache does not exist | `cache_design.md` (Stage 14): "not built," deferred to 20b | Stage 20b |
| Eval-score trend | Single point, not yet a trend | Only one Stage 14 run has happened (`scorecard.md`) | Accumulates from 20a onward |
| Cost / Latency | Budgets exist (Stage 15) but no live run has produced data to plot against them | Nothing has run — same status Stage 15 itself records for U1/U2 | Stage 20a |

Recorded per the standing status-honesty rule (`dmaic_plan.md` Control §1): these dashboards
are **designed**, not **populated** — the distinction the programme has enforced at every
prior stage that touched metrics.

## 4. Per-workflow filtering

Every dashboard filters by `workflow` (`batch_review` \| `pv_intake` \| `supply_planning`),
consistent with RR-2 (`dmaic_plan.md` T-10) — a Batch Review metric must never be silently
presented as if it applies to PV or Supply. The default view is `batch_review`-only until the
other two graphs exist, rather than an aggregate that would misrepresent workflows with no
data yet.

## 5. What this stage does not build

No actual dashboard tool is selected or provisioned (Azure Monitor / Application Insights per
ADR-009, or a LangSmith-native dashboard — the choice itself is a Stage 20 build decision, not
a design-stage one). This document specifies panels, metrics, and audiences; it does not wire
a specific product.
