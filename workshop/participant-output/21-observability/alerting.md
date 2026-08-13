# Alerting — Stage 17

**Executes:** `prompts/21_observability.md` §3
**Consumes:** `failure_and_loop_guards.md` §6–7 (failure taxonomy, control metrics),
`policy_register.md` (13 policies, P-01–P-13), `dmaic_plan.md` Control (monitoring-ownership
table, revisit triggers T-1…T-11)
**Artifact status:** `provisional` — thresholds/routing defined here; paging integration is a
Stage 20 build task

---

## 1. Severity taxonomy — the gap this stage closes

Before this stage, severity was asserted ad hoc: `failure_and_loop_guards.md` calls things
"Yes — governance," "Yes — defect," "stop-the-line class" in different tables with no shared
scale; `dmaic_lens.md` calls `PROHIBITION_ADJACENT` "highest-severity" without a taxonomy it
sits inside. This section is the one taxonomy every alert below maps into — **it does not
change what already gets flagged, it gives the existing flags a shared vocabulary.**

| Level | Meaning | Response | Examples (all pre-existing signals, none new) |
|---|---|---|---|
| **SEV-1 — Stop the line** | A structural control has failed, not merely tripped. The system may be producing untrustworthy output right now | Page immediately; **halt admission of new runs for the affected workflow** pending investigation | `AgentAuthorityExceeded` (any); `G-FAIL_OPEN_VIOLATION` / Policy Engine fail-open; T-1/T-2 trigger conditions (`dmaic_plan.md`); non-citable evidence past the retrieval boundary (`gate_defect`) |
| **SEV-2 — Governance incident** | A control fired correctly, but its firing is itself reportable — the event is rare-by-design and each occurrence needs review | Page on-call (Governance & Oversight owner); does not halt admission — the control worked | `ProhibitedActionBlocked` (any); `hitl_escalation_skipped` on **E2** specifically (lapsed role assignment — a governance defect, not scheduling); veto registered (PV, informational but always reviewed) |
| **SEV-3 — Engineering defect** | A structural cap or safety ceiling was hit, or a metric crossed its expected-zero threshold, indicating a design or implementation gap rather than a live control failure | Ticket + notify (Architecture owner / Engineering-Platform); no page unless sustained | `cap_exceeded`, `ceiling_exceeded` (`failure_and_loop_guards.md` §6); `llm_calls` p95 ≥ 5; any approval recorded after T3 (expiry not enforced) |
| **SEV-4 — Operational signal** | Expected, non-zero-by-design metric moving in a direction that warrants attention but not urgency | Dashboard visibility only; reviewed at the cadence Stage 21 sets, not real-time | `hitl_timed_out` rate rising (approver capacity, not correctness); `abstention_rate` dropping (system got less cautious); approvals arriving at T2 by the escalation role, sustained rise |

**The fourth row exists because not everything that should be watched should page someone** —
per `failure_and_loop_guards.md` §5.6's own note that a rising escalation-approval rate "has
not solved a latency problem; it has moved accountability away from the role," which is a
finding for a periodic review, not a 3am page.

## 2. Alert routing by severity

| Severity | Routes to | Basis |
|---|---|---|
| SEV-1 | Governance & Oversight owner (CQO) + CISO + Engineering on-call, simultaneously | `hitl_control_model.md` §3 — both business and security accountability for a stop-the-line event |
| SEV-2 | Governance & Oversight owner (per-policy, via `control_ownership.md`) | `control_ownership.md` §2 already names a per-policy owner; this is that table wired to a paging destination |
| SEV-3 | Architecture owner / Engineering-Platform | `dmaic_plan.md` Control monitoring-ownership table |
| SEV-4 | No routing — dashboard only | §1 |

**No alert routes to a role excluded from the relevant plane in `rbac_model.md`.** Manufacturing
VP, having no decision or operational-access role, receives no alert at any severity — stated
explicitly so a future paging-tool configuration doesn't add them "for visibility."

## 3. Threshold table

| Metric | Source | Threshold | Severity |
|---|---|---|---|
| `AgentAuthorityExceeded` | `failure_and_loop_guards.md` §7 | Any | SEV-1 |
| Policy Engine fail-open observed | ADR-005, P-05 | Any | SEV-1 |
| `gate_defect` (non-citable evidence past retrieval boundary) | `failure_and_loop_guards.md` §6 | Any | SEV-1 |
| `ProhibitedActionBlocked` | ADR-004, P-01 | Any | SEV-2 |
| `hitl_escalation_skipped` on E2 | `failure_and_loop_guards.md` §5.6, P-08 | Any | SEV-2 |
| `cap_exceeded` / `ceiling_exceeded` | `failure_and_loop_guards.md` §6 | Any | SEV-3 |
| Approval recorded after T3 | `failure_and_loop_guards.md` §5.6 | Any | SEV-3 |
| `llm_calls` per run (p95) | `failure_and_loop_guards.md` §7 | ≥ 5 | SEV-3 |
| Cost per run vs. budget | Stage 15 (`token_economics.md`) — **budget now exists, unlike at Stage 10** | > budget (Stage 15 sets the number; this design does not re-derive it) | SEV-3 |
| Cache serving superseded evidence | ADR-003, `G-CACHE_STALE_SERVE` | Any | SEV-1 — **elevated from the SEV-2 a naive reading of "governance incident" might assign**, because a served stale answer is untrustworthy output already delivered, not a caught-and-blocked attempt |
| `hitl_timed_out` rate | `failure_and_loop_guards.md` §5.6 | Sustained rise (trend, not single-instance) | SEV-4 |
| `abstention_rate` | `failure_and_loop_guards.md` §7 | Sudden drop | SEV-4 |
| Approvals at T2 by escalation role | `failure_and_loop_guards.md` §5.6 | Sustained rise | SEV-4 |

**Cost-per-run is the one row this stage can set a real threshold for that Stage 10 explicitly
could not** (`failure_and_loop_guards.md` §3, C3: "not set... would be a guess") — because
Stage 15 (performance tuning) has since run and produced `token_economics.md`'s measured
budget. Everything else in this table was already alert-worthy before Stage 15; this row is
the one place the Wave 4 "measured pass" ordering visibly pays off inside Stage 17's own
design.

## 4. What this does not do

No paging tool is selected or configured (Stage 20 build task — this document specifies
severity and routing, not PagerDuty/Opsgenie config). No alert here is new *content* — every
row in §3 traces to a metric `failure_and_loop_guards.md` or `policy_register.md` already
named as alert-worthy; this stage's contribution is the severity scale and the routing table,
consistent with the instruction that Stage 17 makes existing controls explainable and
actionable, not that it invents new ones.
