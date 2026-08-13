# Control Ownership — Stage 16

**Executes:** `prompts/20_governance_control.md` §4 (mirrors DMAIC Control from Prompt 09/12)
**Consumes:** `policy_register.md`, `dmaic_plan.md` §Control (monitoring-ownership table),
`hitl_control_model.md` §3 (bounded-context owners)
**Artifact status:** `stable` for `batch_review` rows; `provisional` for PV/Supply rows

---

## 1. Purpose

`dmaic_plan.md`'s Control section already named monitoring owners for eight signals. This
document is the same exercise run one level down, **per policy** rather than per signal, so
every entry in `policy_register.md` has a named owner and a revisit trigger — the exit
criterion `prompts/20` asks for. Owners are drawn from `hitl_control_model.md` §3's bounded-
context table; no new accountable role is invented here.

## 2. Ownership table

| Policy ID | Owner (role) | Revisit trigger | Trigger source |
|---|---|---|---|
| P-01 (prohibited actions) | Chief Quality Officer (Batch); Global Head of PV (PV); Supply Chain VP + Quality co-approval (Supply) — per workflow, `hitl_control_model.md` §3 | **T-1**: interim assumption 1 fails (prohibited action becomes representable) | `dmaic_plan.md` Control — stop-the-line |
| P-02 (evidence authority) | Chief Quality Officer (evidence authority is a quality-system concern, `hitl_control_model.md` §3) | **T-2**: interim assumption 2 fails (authority gate leaks) | `dmaic_plan.md` Control — stop-the-line |
| P-03 (cross-graph tool access) | Engineering/Platform (Agent Orchestration owner, `hitl_control_model.md` §3 — technical control, no business decision authority) | **T-9**: implemented hop count exceeds 7 without documented reason | `dmaic_plan.md` Control |
| P-04 (no blind retry) | Engineering/Platform | Any `PROHIBITION_ADJACENT` retry observed (should be structurally impossible post-fix) — zero-tolerance, per `hooks.md` §1 `critic_verify` row | `failure_and_loop_guards.md` §7 |
| P-05 (fail closed) | Chief Quality Officer (AI-management-system owner) + CISO (security controls) — `hitl_control_model.md` §3 | Any observed fail-open event | `failure_and_loop_guards.md` §6 (`refused`/`fail_closed` row, alert: yes) |
| P-06 (structural caps / safety ceilings) | Architecture owner (Stage 15 sets replacement budgets from measurement) | **T-3**: U1 measures far above expectation → revisit ADR-008 topology | `dmaic_plan.md` Control |
| P-07 (HITL timeout) | Per-workflow primary approver role (`hitl_control_model.md` §2); Chief Quality Officer as AI-management-system owner for the ladder's design | **T-11**: first real-organization deployment — every duration re-confirmed against a live Entra assignment (`hitl_control_model.md` §7) | This stage |
| P-08 (escalation eligibility) | Per-workflow escalation role (`hitl_control_model.md` §4) | Any `hitl_escalation_skipped` on **E2** (empty/lapsed role assignment) — zero-tolerance | `failure_and_loop_guards.md` §5.6 |
| P-09 (PV advisory veto) | Patient Safety Representative | **T-10**: any Batch Review interim conclusion applied to PV without re-checking (PV is `provisional`, RR-2) | `dmaic_plan.md` Control |
| P-10 (redaction before write) | Data Protection Officer (privacy risk acceptance) + Chief Quality Officer (GxP preservation) jointly — `hitl_control_model.md` §5 names this tension explicitly | Stage 17 populates the actual ruleset; revisit when it does, to confirm the binding point still holds | `hooks.md` §4 |
| P-11 (audit before response) | Audit store owner (`dmaic_plan.md` Control monitoring table) | Audit-store write success rate <100% while LangSmith healthy | `dmaic_plan.md` Control |
| P-12 (denial of wallet) | Architecture owner | Stage 15 budget replaces the current placeholder ceiling | `failure_and_loop_guards.md` §3 replacement condition |
| P-13 (Batch Review HITL tiering — deferred) | Chief Quality Officer | U7 becomes available (measured false-abstention/approval-burden data) | **BC-17** |

## 3. Cross-cutting owner: Governance & Oversight context

Per `hitl_control_model.md` §3, the **Governance & Oversight** bounded context itself is owned
by the Chief Quality Officer (AI-management-system owner), with the **CISO** and **Data
Protection Officer** as named co-owners for security controls and privacy risk acceptance
respectively. This register does not reassign that — every per-policy owner above operates
within that context's accountability, consistent with ADR-005's open-host-service model (one
versioned policy contract, not per-workflow policy forks).

## 4. What "ownership" means operationally, now vs. later

At this stage, "owner" names the **role accountable if the control fails**, for use in incident
routing and Stage 19 compliance evidence — it does not yet bind to a monitoring dashboard
(Stage 17) or an alerting pipeline (also Stage 17). The table above is the input Stage 17 wires
alerts against; it is not itself an alerting system.

## 5. Consistency check against `dmaic_plan.md`

Every owner named above matches `dmaic_plan.md`'s existing monitoring-ownership table exactly
where the same signal appears in both (e.g. HITL routing rate → workflow approver roles; audit
write success → audit store owner). No new owner contradicts a prior stage's assignment — this
document adds the per-*policy* granularity that table didn't carry, it does not re-derive
ownership from scratch.
