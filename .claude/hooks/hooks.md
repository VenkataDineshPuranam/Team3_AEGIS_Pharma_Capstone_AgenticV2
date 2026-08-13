# hooks.md — Hook Index

**Executes:** `prompts/16_skills_hooks.md` §2
**Builds on:** `docs/architecture/agentic/langgraph_design.md`,
`docs/architecture/agentic/failure_and_loop_guards.md`, `docs/governance/hitl_control_model.md`
**Artifact status:** `stable` for the `batch_review` bindings; `provisional` for PV/Supply
(same split as `agent_roster.md`)

---

## 0. What this stage adds that Stage 10 did not already have

Stage 10 already designed nine deterministic nodes precisely because a control must not depend
on a model's compliance. This stage's job is not to redesign them — it's to **catalogue every
one of them under the lifecycle-hook vocabulary the prompt specifies** (pre-tool-call,
post-tool-call, session-start, and the two more this design needs — pre-output and
on-interrupt), cross-reference each to the governance document it enforces, and confirm the
"does not depend on agent prompt compliance" property explicitly rather than leaving it
implicit in the graph diagram.

**Every row below is a LangGraph node that already exists in `langgraph_design.md`.** This file
adds no new control — it is the index the exit criteria ask for, plus the traceability link to
`docs/governance/`.

## 1. Hook index

| Hook event | Binds to (node, `langgraph_design.md`) | Purpose | Enforces (governance link) | Depends on prompt compliance? | Status |
|---|---|---|---|---|---|
| **session-start** | `intake` | Bind the caller's **current** authorization before any other work begins; reject malformed requests | `hitl_control_model.md` §1 (roles, not individuals — a stale binding is a governance failure, not a UX one) | **No** — a request with no resolvable authorization has no path forward in the graph | `stable` |
| **session-start** | `policy_load` | Load the versioned policy contract; **refuse if unreachable** | ADR-005 (fails closed); ties to `security/policies/` **once Stage 16 populates it** — forward reference, not yet resolvable | **No** — there is no edge from an unloaded policy to any further node | `stable` |
| **pre-tool-call** | server-credential check (`tool_inventory.md` §1) | Confirm the calling graph run holds a credential for the specific bounded-context server it's addressing | ADR-008 (no cross-graph tool access) — enforced at the tool-server boundary, independent of the graph-edge enforcement already in `langgraph_design.md` §2 | **No** — the credential either exists or it doesn't; nothing about it is inferred from the model's request | `stable` |
| **post-tool-call** | `evidence_gate` | Assert zero non-citable (`untrusted`/`superseded`) items in the tool's response; halt + alert on violation rather than silently dropping items | ADR-003 (deterministic evidence-authority gate) | **No** — this is a status lookup against the returned items, not an interpretation of them | `stable` |
| **pre-output** | `prohibited_action_guard` (×2 — before and after the Critic, `langgraph_design.md` "why the guard runs twice") | Pattern-match every candidate output against the per-workflow prohibited-action shape before it can advance | ADR-004 layer 3; the per-workflow prohibition contract is the artifact this hook is parameterized by | **No** — pattern-matches output shape; does not ask the model whether its own output is acceptable | `stable` |
| **pre-output** | `critic_verify`'s **reason-code gate** (`failure_and_loop_guards.md` §4) | Refuse a retry that lacks a diagnosis; refuse a retry on a repeated reason code; refuse any retry at all on `PROHIBITION_ADJACENT` | BC-5 (no blind retry) | **No** — the enum and the repeat-check are closed, code-level rules, not the Critic's own judgement about whether to try again | `stable` |
| **on-interrupt** | `hitl_route` → `hitl_interrupt` | Resolve the approver role(s); enforce the four-tier escalation ladder; **timeout ⇒ no action**, never auto-proceed | `hitl_control_model.md` §2/§4; `failure_and_loop_guards.md` §5 (durations, escalation conditions E1–E5) | **No** — tier transitions and expiry are clock-driven, not agent-driven; escalation eligibility is an Entra-group check, not a model decision | `stable` (Batch); `provisional` (PV/Supply — Supply's dual-leg and PV's advisory veto are the untested parts, RR-2) |
| **post-tool-call / pre-checkpoint** | trace + audit redaction (`memory_design.md` §4, `boundary_and_degraded_mode.md` "Privacy boundary") | Redact PII/PHI **before** any write to LangSmith or the audit store; discard (not store) the text of any guard-blocked draft, keeping only a reason code, prohibition class, and hash | ADR-006; BC-8 ("redaction rules written before the first trace is written") | **No** — redaction rules are applied mechanically to every write path, not left to the model to decide what's sensitive | `stable` (design); **not yet implemented** — Stage 17 owns the actual redaction rule set, this hook is the binding point, not the ruleset |
| **post-run** | `finalize` | Emit the `AgentRun` record and write audit **before** returning to the caller — a response that reaches the caller with no audit write is not a valid terminal state | ADR-006 (owned audit store); `hitl_control_model.md` §1 (accountability attaches to the role, which requires the record to exist) | **No** — this is a required step in the graph's own control flow, not a best-effort log call | `stable` |
| **pre-tool-call** | `intake`, denial-of-wallet check (Stage 15, [`denial_of_wallet_guardrail.py`](../../infra/policies/denial_of_wallet_guardrail.py)) | Refuse to admit a run if the (user, workflow, day) run-count or spend ceiling is already exceeded — a hard circuit breaker, not a documented policy | `docs/quality/performance/denial_of_wallet_guardrail.md`; ceiling derived from C1/C4 (`failure_and_loop_guards.md`) + verified pricing | **No** — both checks are arithmetic over recorded counters, no model judgement involved | `stable` — **implemented and tested**, 7/7 passing (`tests/unit/policies/`), the only hook row in this table with an actual executable + test file rather than only a design reference |

**Ten node-level bindings, covering every governance-critical control named in this file's own
pre-existing convention** ("blocking a terminal safety/release decision, redacting PII before a
tool call, requiring HITL sign-off before a high-risk tool executes"): the first is
`prohibited_action_guard`, the second is the redaction binding, the third is `hitl_route`/
`hitl_interrupt`. All three are hooks, not skills, and none of the three has a skill-based
alternative anywhere in `skills.md` — see `skill_vs_hook_boundary.md` for the check that
confirms this.

## 2. What is explicitly *not* a hook, and why that's correct

| Not a hook | Why | Where it actually lives |
|---|---|---|
| Deciding *what to write* in a synthesis draft | Content generation is exactly what a skill is for — advisory, not enforced | `skills.md` §1 |
| Deciding *whether* a claim is well-supported by its citations | Requires reading the argument — the one class of check `agent_roster.md` §5 assigns to the Critic's judgement, not to a deterministic pattern match | `critic-verify-decision-support-output` skill, checked by the Critic, then re-checked by the `pre-output` hook above for the shape (not the substance) of the result |
| Choosing which approver role to notify first | Deterministic lookup already, but framed as ordinary routing logic, not a governance boundary in itself — the boundary is the **timeout/expiry** behaviour, which *is* a hook (`on-interrupt`, above) | `hitl_route` |

## 3. Confirming the "not dependent on agent prompt compliance" property, per row

The exit criteria require this stated explicitly, not left as an inference from "it's a
deterministic node." For every row in §1, the "Depends on prompt compliance?" column is **No**,
and the reason is structural in each case: a schema field absent from the type (guard), a
status lookup against retrieved data (evidence gate), a credential presence check (pre-tool-
call), a clock (on-interrupt), or a required step in control flow with no bypass edge
(post-run). None of the nine rows would fail differently if the model's system prompt were
deleted entirely — which is the actual test of "not prompt-dependent," and a stronger claim
than "the design intends this."

## 4. Forward reference — `security/policies/`

Several rows above cite `security/policies/` as a governance link that does not yet resolve to
content (Stage 16 populates it). This is stated honestly rather than papered over: the *hook
binding* is stable now (it's a LangGraph node that already exists), but the *policy content*
the hook enforces against — beyond the four ADR-derived invariants already wired in — is not
fully specified until Stage 16. No hook in this table is blocked on that; each already enforces
its ADR-derived invariant directly. Stage 16 adds policy *content* to load, not new hook
*bindings*.
