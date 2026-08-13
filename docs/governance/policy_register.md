# Policy Register — Stage 16

**Executes:** `prompts/20_governance_control.md` §1
**Consumes:** ADR-004, ADR-005, `.claude/hooks/hooks.md` §1 (10 hook bindings), BC-1/BC-3/BC-12
**Artifact status:** `stable` for `batch_review` entries; `provisional` for PV/Supply entries
(same split as `agent_roster.md`, `hooks.md`)

---

## 0. What this document is and isn't

`hooks.md` already catalogued every deterministic control node and confirmed each one does not
depend on prompt compliance. This document does not redesign those controls — per the
Lean/DMAIC lens in `prompts/20`, **it consolidates them into one governed-boundary register**,
because "which hook enforces which rule" and "what proves the rule holds" were previously split
across `hooks.md`, the ADRs, and `failure_and_loop_guards.md` with no single index. Every entry
below traces to an existing hook row or ADR; none is invented here.

## 1. Register

| Policy ID | Governed boundary | Rule | Enforcing hook(s) | Source | Proving eval (Stage 14) |
|---|---|---|---|---|---|
| **P-01** | Prohibited terminal decisions (batch release/reject/reprocess/relabel/recall; PV causality/seriousness/expectedness/reportability/signal confirmation; supply allocation/reservation/shipment/recall) | Structurally unrepresentable at three layers: schema, tool method, runtime guard | `prohibited_action_guard` (pre-output, ×2) + schema absence (Stage 11 contracts) + tool capability absence (Stage 11) | ADR-004, BC-1 | `G-PROHIBITED_ACTION` (`prohibited_action_grader.py`), Category 13 `agent_wrong_handoff` regression suite |
| **P-02** | Evidence authority / citability | Only `active`/`local_approved`/status-verified evidence may be cited; `untrusted`/`superseded` items are a hard stop, never silently dropped | `evidence_gate` (post-tool-call) | ADR-003 | `G-EVIDENCE_AUTHORITY_VIOLATION`, `G-FABRICATED_OR_UNCITED_FACT` |
| **P-03** | Cross-graph tool access | A run may only call the MCP server bound to its own bounded context; no cross-graph credential exists | server-credential check (pre-tool-call) | ADR-008 | `G-SCHEMA_FAILURE` path / Category 13 `unauthorized_tool_call` |
| **P-04** | Retry legitimacy (no blind retry) | Every retry carries a reason code from a closed enum, distinct from every prior code in the run; `PROHIBITION_ADJACENT` is never retried | `critic_verify` reason-code gate (pre-output) | BC-5, `failure_and_loop_guards.md` §4 | Category 13 `agent_wrong_handoff` (`AWH-01`, the `PROHIBITION_ADJACENT` regression) |
| **P-05** | Governance/Policy Engine availability | Engine unreachable ⇒ refuse (`fail_closed`); never fail open | `policy_load` (session-start) | ADR-005, **BC-3** | `G-FAIL_OPEN_VIOLATION` (`security_grader.py:grade_fail_closed`) |
| **P-06** | Structural caps / safety ceilings | Runs may not exceed G1–G8 (structural) or C1/C2/C4 (safety ceiling); breach ⇒ `abstained`/`ceiling_exceeded`, alerted as a defect, never silently absorbed | graph edge conditions (no edge exists past cap) + runtime ceiling check | `failure_and_loop_guards.md` §2–3 | `G-STRUCTURAL_CAP_EXCEEDED` (`loop_guard_grader.py`) |
| **P-07** | HITL timeout / default-safe behavior | Timeout ⇒ `hitl_status = timed_out`, terminal state `abstained`, **no action taken**, ever; approver roles are roles, not individuals | `hitl_route` → `hitl_interrupt` (on-interrupt) | **BC-12**, `hitl_control_model.md`, `failure_and_loop_guards.md` §5 | `G-AUDIT_TRAIL_INCOMPLETE` covers the record; no dedicated timeout grader yet — **gap, see §3** |
| **P-08** | Escalation eligibility (E1–E5) | T2 escalation proceeds only if all five conditions hold at that moment; any failure is skipped silently to the approver but logged loudly to audit | `hitl_route` → `hitl_interrupt` (on-interrupt) | `failure_and_loop_guards.md` §5.3 | Not yet covered by an executable grader — **gap, see §3** |
| **P-09** | Advisory veto (PV) | Patient Safety Representative's veto may be registered at any tier, forces `hitl_status = rejected` immediately, is never overridden by a later approval | `hitl_route` → `hitl_interrupt` (on-interrupt) | `failure_and_loop_guards.md` §5.4 | Not yet covered — PV graph is `provisional` (RR-2) |
| **P-10** | PII/PHI redaction before write | Redact before any write to LangSmith or the audit store; discard the text of a guard-blocked draft, keep only reason code + prohibition class + hash | trace/audit redaction (post-tool-call / pre-checkpoint) | ADR-006, BC-8 | Not yet gradeable — ruleset owned by Stage 17, **binding point stable, content not written**, per `hooks.md` §4 |
| **P-11** | Audit write before response | An `AgentRun` record is written before returning to the caller; no response reaches the caller with no audit write | `finalize` (post-run) | ADR-006, `hitl_control_model.md` §1 | `G-AUDIT_TRAIL_INCOMPLETE` (`audit_trail_grader.py`) |
| **P-12** | Denial-of-wallet | Refuse to admit a run once (user, workflow, day) run-count or spend ceiling is already exceeded | denial-of-wallet check (pre-tool-call) | `failure_and_loop_guards.md` C1/C4; Stage 15 pricing | `tests/unit/policies/` (7/7 passing) — the one row with a real implemented grader already |
| **P-13** | Batch Review HITL risk-tiering | **Deferred.** No tiering exists; 100% of Batch Review outputs route to HITL until U7 (measured false-abstention/approval-burden data) exists | N/A — no hook, because no tiering is implemented | **BC-17** | N/A — deferring is the correct state, not a gap |

## 2. Approver-role wiring (pointer, not a copy)

Every P-07/P-08/P-09 entry above resolves its named roles from `hitl_control_model.md` §2/§4,
which this stage extends (§3 of this register) rather than restating. Duplicating the role
table here would create two places that could drift; the register cites, `hitl_control_model.md`
owns.

## 3. Honest gaps this register surfaces

Cataloguing the policies against Stage 14's actual grader inventory (`release_gates.md` §3)
shows three policies — **P-07, P-08, P-09** — with a *design* that is `stable` but **no
executable eval test proving it**, unlike P-01 through P-06 and P-11/P-12. This was not visible
before this register existed as a single table. Recorded honestly rather than smoothed over:

- **P-07/P-08 (HITL timeout/escalation):** the ladder's logic is fully specified
  (`failure_and_loop_guards.md` §5) but exercising it requires a running clock and a real
  interrupt, which Stage 14's fixture-based harness does not simulate. This is a legitimate
  gap for Stage 18 (red-team the *running* slice) or a targeted Stage 14 follow-up once 20a
  exists — not a design defect.
- **P-09 (PV veto):** blocked on the PV graph itself being `provisional` (RR-2) — cannot be
  tested before it is built.

None of these three block Stage 16's exit criteria, which require a policy entry, an enforcing
hook, and a passing eval test **per prohibited-decision boundary from the DDD** — P-01 through
P-06 satisfy that fully. P-07/P-08/P-09 are HITL *process* controls, not prohibited-decision
boundaries; the exit criterion for those is "timeout/default-safe behavior is defined for every
interrupt point" (met, in §5 above), not "has an automated grader."
