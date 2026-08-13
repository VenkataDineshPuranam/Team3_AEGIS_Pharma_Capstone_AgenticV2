# Escalation & Override Log Design — Stage 16

**Executes:** `prompts/20_governance_control.md` §3
**Consumes:** `hitl_control_model.md`, `failure_and_loop_guards.md` §5, `memory_design.md` §4
(state schema), ADR-006 (owned audit store)
**Artifact status:** `provisional` — design only, no store implemented until Stage 20

---

## 1. Two distinct events, not one log

`failure_and_loop_guards.md` §5 already distinguishes two things that a naive design would
conflate into one "human touched this run" log line. Keeping them structurally separate matters
because they answer different audit questions:

| Event class | Answers | Who/what triggers it |
|---|---|---|
| **Escalation** | "Who was *added* as an eligible approver, and did the E1–E5 conditions actually hold?" | The graph, automatically, at T2 |
| **Override** | "Did a human approve, reject, or veto — and on what stated justification?" | A named role, taking an explicit action |

An escalation is not itself a decision — it only ever widens who *may* decide
(`failure_and_loop_guards.md` §5.1). Logging it under the same schema as an override would
make "the system escalated" look like "a human acted," which is precisely the confusion BC-12
exists to prevent. This design keeps them as two record types sharing one audit store.

## 2. Escalation record — `HitlEscalation`

Emitted automatically at every T2 evaluation, **whether or not escalation actually proceeds**
(`failure_and_loop_guards.md` §5.3: a failed condition is "skipped silently to the approver but
recorded loudly to the audit store").

| Field | Value | Why |
|---|---|---|
| `run_id` | Correlates to `AgentRun` | BC-19 (trace↔audit correlation, Stage 17) |
| `workflow` | `batch_review` \| `pv_intake` \| `supply_planning` | Determines which ladder/roles apply |
| `tier` | Always `T2` (only tier that evaluates escalation) | — |
| `evaluated_at` | Timestamp | E2/E4 are evaluated "at that moment," not at submission — this timestamp is the evidence of *when* |
| `conditions` | `{E1: bool, E2: bool, E3: bool, E4: bool, E5: bool}` | All five, not just the failing one — a full record, so a later audit can see near-misses too |
| `outcome` | `escalated` \| `skipped` | Derived from `all(conditions.values())` |
| `skip_reason` | First failing condition ID, or null | Feeds the P-08 control metric `hitl_escalation_skipped` by condition (`failure_and_loop_guards.md` §5.6) |
| `escalation_role` | Role name (e.g. `Chief Quality Officer`) or null if E1 failed | — |
| `policy_contract_version` | The version checked under E4 | Lets an auditor confirm E4's check against the actual policy history |

**No override is implied by this record.** `outcome: escalated` means the escalation role is
now *eligible*; it says nothing about whether they acted.

## 3. Override record — `HumanOverrideRecorded`

Emitted whenever a named role takes an explicit action on a pending run: approve, reject, or
(PV only) register the advisory veto.

| Field | Value | Why |
|---|---|---|
| `run_id` | Correlates to `AgentRun` | Same correlation requirement as above |
| `role` | The role acting (e.g. `EU Qualified Person`, `Chief Quality Officer` — **role, not personal identity**) | `hitl_control_model.md` §1 — accountability attaches to the role; `memory_design.md` §4 states personal identity is never stored, only role + role-assignment ID |
| `role_assignment_id` | The specific live assignment checked (Entra group membership record) | Makes "was this person actually holding the role at the time" independently verifiable later, without storing who they are in the audit record's primary fields |
| `tier_at_action` | `T0` \| `T1` \| `T2` | Distinguishes a primary-approver action from an escalated-role action — feeds the P-08 metric "approvals arriving at T2 by the escalation role," whose sustained rise is itself a governance finding (`failure_and_loop_guards.md` §5.6) |
| `action` | `approved` \| `rejected` \| `veto_registered` (PV only) | `veto_registered` is structurally distinct — see §4 |
| `justification` | Free text, **required**, minimum non-empty | The exit criterion is explicit: "how a human override is recorded, by whom, with what justification." An override with no stated reason is not a valid record — the write is refused, not defaulted to empty string |
| `evidence_snapshot_ref` | Pointer to the evidence set the human reviewed (not a copy — a reference, so this record does not itself become a second copy of cited evidence) | Lets a later audit reconstruct exactly what the approver saw, without duplicating the Evidence & Provenance kernel's own record |
| `recorded_at` | Timestamp | — |

**"Override" is a naming choice, not a claim that this replaces an AI decision.** Per ADR-004,
the system never produces a release/reject/causality/allocation decision to override — this
record captures the human's *own* decision, informed by the system's decision-support output.
The field name follows the exit criterion's own vocabulary; it does not imply the AI had
decision authority to begin with.

## 4. The veto is not an override of anything

`failure_and_loop_guards.md` §5.4: the Patient Safety Representative's advisory veto "may be
registered at any tier, forces `hitl_status = rejected` immediately... is never overridden by a
later approval." Its record uses the same `HumanOverrideRecorded` schema (§3) with
`action: veto_registered`, but two invariants are enforced at write time, not left to
application logic to remember:

1. **A `veto_registered` record cannot be superseded.** Any later write with
   `action: approved` for the same `run_id` where a `veto_registered` record already exists is
   rejected by the store itself — not merely discouraged by workflow design. This is the audit
   store enforcing "never overridden," the same structural argument ADR-004 makes for
   prohibited actions applied here to the veto.
2. **`tier_at_action` is recorded but never gates a veto.** Unlike an approval, a veto is valid
   at any tier — the field is retained for the audit record's completeness, not as an
   eligibility check.

## 5. Timeout is a record too, not an absence of one

Per `failure_and_loop_guards.md` §5.5, T3 expiry is itself logged — described there as
"a `HumanOverrideRecorded`-adjacent entry recording that no decision was made and by which
roles it was not made." This design makes that concrete: a third record type,
**`HitlExpired`**, sharing `run_id`/`workflow`/`policy_contract_version` with the two record
types above, with `eligible_roles_at_expiry` (every role that was eligible to approve, whether
or not escalated) and `abstention_reason: hitl_timeout`. This is deliberately not folded into
`HumanOverrideRecorded` with `action: expired` — an expiry is the *absence* of an override, and
the exit criterion's audit trail requirement is best served by making that absence its own
first-class, unambiguous record rather than a fourth enum value sitting next to `approved` where
a future query could miscount it as an action taken.

## 6. Storage and access

- **Audit store, not LangSmith.** Per `hooks.md`'s redaction row and ADR-006, these are
  compliance records, not observability traces — a provably separate sink, append-only.
- **No personal identity in any of the three record types** (§3), consistent with
  `hitl_control_model.md` §1 and `memory_design.md` §4's role-not-individual rule.
- **Retention** is a Stage 17/19 decision (`hitl_control_model.md` §5 already flags the
  privacy-vs-GxP-preservation tension as requiring explicit DPO + CQO agreement) — this design
  does not set a retention period, only the record shapes that retention policy will apply to.

## 7. What proves this design (Stage 14 linkage)

`G-AUDIT_TRAIL_INCOMPLETE` (`audit_trail_grader.py`) currently checks that `finalize` writes an
`AgentRun` record before response. It does not yet check for the three record types above,
because they don't exist until a HITL interrupt actually fires against a running graph — the
same gap `policy_register.md` §3 records for P-07/P-08/P-09. Flagged here again rather than
silently assumed covered.
