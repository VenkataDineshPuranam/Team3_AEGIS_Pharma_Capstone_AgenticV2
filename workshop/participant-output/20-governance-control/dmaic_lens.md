# DMAIC Lens — Stage 16 (Governance & Control)

**Thin lens.** Per `prompts/20_governance_control.md`: "this stage *is* Control for the whole
system" — every policy here should trace to a Control action already flagged in Prompts
01/04/06/09/12, consolidated, not invented. This lens records that check, not a fresh cycle.

## Define

The question this stage answers: **for every governed boundary the DDD names, is there one
policy entry, one enforcing hook, and one owner — in a single place, rather than scattered
across ADRs, `hooks.md`, and `failure_and_loop_guards.md`?**

## Measure

| Metric | Value | Note |
|---|---|---|
| Governed boundaries registered | **13** (P-01…P-13) | All traced to an existing ADR/BC/hook — none invented |
| Boundaries with a passing eval test | **9** of 13 (P-01–P-06, P-11, P-12; P-13 is a correct deferral) | `policy_register.md` §3 |
| Boundaries with a *designed but untested* control | **3** (P-07, P-08, P-09) | HITL timeout/escalation/veto — need a running interrupt, not a fixture. Honest gap, not hidden |
| New revisit trigger added | **1** (T-11) | Re-confirm ladder durations against a live org at first real deployment |
| Owners newly assigned at policy granularity | **13** | Previously only 8 signals had named owners (`dmaic_plan.md`); this stage adds per-policy granularity, contradicting nothing prior |

## Analyze

The one substantive finding: consolidating the 10 `hooks.md` rows and the 4 ADR-level
invariants into a single register (§1 of `policy_register.md`) is what **surfaced** the
P-07/P-08/P-09 gap — it was not visible while HITL logic lived only in
`failure_and_loop_guards.md` prose, because that document correctly states the *design* is
`stable`, which reads differently from "and it's covered by an eval." The register is doing
its job precisely by making that distinction checkable rather than assumed.

No new Control action was invented — every row in `policy_register.md` traces to BC-1, BC-3,
BC-5, BC-8, BC-12, BC-17, or an ADR (004/005/006/008), all already flagged in Prompts 01/04/06/
09/12. This satisfies the stage's own instruction not to invent Control actions without a
traced root cause.

## Improve

No structural change to any prior artifact. The improvement this stage makes is **consolidation
and gap-surfacing**, not redesign: `hitl_control_model.md` gained §7 (duration consistency
check, not new durations); `policy_register.md`, `control_ownership.md`, and
`escalation_override_log_design.md` are new indexes and one new design (the three audit record
shapes in §2–5 of the log design), not replacements for Stage 10/11/12's control logic.

## Control

- **Standard added:** every future policy entry must cite an enforcing hook and a proving eval,
  or explicitly record why no eval exists yet (the P-07/P-08/P-09 pattern) — silence on either
  column is not acceptable going forward.
- **Ownership**: `control_ownership.md` is now the canonical per-policy owner/trigger table;
  `dmaic_plan.md`'s per-signal table is unchanged and still governs monitoring granularity.
- **T-11** (new): first real-organization deployment must re-confirm every HITL duration and
  role assignment — a design-time consistency check is not an operational one.
- **T-8 closes**: the interim placeholder approver problem it warned against never materialized
  — `hitl_control_model.md` used named stakeholder-pack roles from the start (EAB-3 closure,
  prior session). Recorded as closed, not left open by omission.
