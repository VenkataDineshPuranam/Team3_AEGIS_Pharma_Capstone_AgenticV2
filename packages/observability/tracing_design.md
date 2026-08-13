# Tracing Design — Stage 17

**Executes:** `prompts/21_observability.md` §1
**Consumes:** `langgraph_design.md` (11 nodes, `batch_review` graph), `hooks.md` (10 hook
bindings, all already the trace-worthy control points), `memory_design.md` §3–4 (what
persists / what must never persist), `rbac_model.md` (actor identity)
**Artifact status:** `stable` for `batch_review`; `provisional` for PV/Supply (same split as
every upstream artifact it depends on)

---

## 1. Core question, answered directly

**Can we explain, after the fact, exactly what every agent did and why?** Yes, for the
`batch_review` graph, if every row in §2 below is wired — this design does not add new nodes
to trace; `langgraph_design.md`'s 11 nodes and `hooks.md`'s 10 hook bindings are already the
complete list of trace-worthy events. This stage's job is the trace *schema* and *span
structure*, not discovering new things to observe.

## 2. What is traced per node (LangSmith run + OpenTelemetry span)

| Node (`langgraph_design.md`) | Span name | Captured | Not captured (redacted before write, §`trace_redaction_and_retention.md`) |
|---|---|---|---|
| `intake` | `intake` | Actor identity (`actor_role`, `actor_id` — see §3), workflow type, `run_id` | Raw request body if it contains PII |
| `policy_load` | `policy_load` | `policy_contract_version` loaded, load latency | — |
| `evidence_retrieve` (×2, incl. broadening) | `tool.evidence_retrieve` | Tool identity (`mi-mcp-<context>`, per `rbac_model.md` §4), query terms, item count, authority-status breakdown, latency | Retrieved document text (evidence content is not PII by construction — ADR-003 — but full-text capture is unnecessary trace volume; item IDs + statuses suffice for explainability) |
| `synthesize` (×≤3) | `agent.synthesize` | Token counts (in/out), model identity, latency, evidence IDs cited | The draft output text **only if guard-clear**; a guard-blocked draft's text is never traced at all (§4) |
| `prohibited_action_guard` (×2) | `guard.prohibited_action` | Verdict (`clear`/`blocked`), matched prohibition class if blocked, latency | The candidate output text on a `blocked` verdict — hash only, per `memory_design.md` §4 |
| `critic_verify` (×≤3) | `agent.critic_verify` | Verdict, reason code (from the closed enum, `failure_and_loop_guards.md` §4), token counts, latency | — |
| `hitl_route` / `hitl_interrupt` | `hitl.wait` (long-running span, paused at interrupt) | Tier transitions (T0→T3), `HitlEscalation`/`HumanOverrideRecorded`/`HitlExpired` record references (`escalation_override_log_design.md`), elapsed wait time | Approver personal identity (role + role-assignment ID only, per `memory_design.md` §4); justification text stays in the audit store, not duplicated into the trace |
| `finalize` | `finalize` | Terminal state, `AgentRun` record reference, total tokens/latency/tool-calls for the run | — |
| Denial-of-wallet check (pre-tool-call, `hooks.md`) | `guard.denial_of_wallet` | Admit/refuse, counter values checked | — |
| `evidence_gate` (post-tool-call) | `guard.evidence_gate` | Non-citable-item count found (expected: zero) | The non-citable item's content, if any — reason and status code only |

**One trace per `run_id`, one span per node execution** (a retried node produces a new span,
not a mutated one — so the full synthesis→critic→synthesis loop history is visible, which is
exactly what "explain what every agent did" requires for a rejected-then-accepted draft).

## 3. Actor identity on every span — closing the RBAC/trace gap

Before this stage, no artifact specified that a trace records **whose identity** initiated a
node's action — `rbac_model.md` names service identities per container but didn't yet say they
appear in the trace itself. Every span above carries:

| Field | Value | Why it's structural, not optional |
|---|---|---|
| `actor_plane` | `human` \| `service` | Matches `rbac_model.md` §2's two planes |
| `actor_role` | e.g. `EU Qualified Person`, `mi-orchestrator` | Role, never personal identity for the human plane (`hitl_control_model.md` §1); managed-identity name for the service plane |
| `actor_id` | Role-assignment ID (human) or managed-identity resource ID (service) | The same "verifiable but not personally identifying" pattern `escalation_override_log_design.md` §3 already uses for override records — this design reuses it rather than inventing a second convention |

**This is what makes a Stage 18 red-team finding attributable.** Without `actor_plane`/
`actor_role`/`actor_id` on every span, "an unauthorized tool call occurred" (Category 13,
Stage 14) would be visible in a trace but not attributable to which identity attempted it —
closing that is the concrete reason this field exists, not a general completeness gambit.

## 4. Guard-blocked drafts — trace behavior restated, not re-decided

`memory_design.md` §4 already settled this: a guard-blocked draft's text must never persist
anywhere, including traces. This design's only addition is making the *span* exist (so the
event is visible — "a guard fired" — per `hooks.md`'s zero-tolerance metrics) while the
*payload* stays exactly what `memory_design.md` specifies (reason code, prohibition class,
SHA-256 hash). A trace that omitted the span entirely, to be safe, would be wrong in the
opposite direction — the whole point of `ProhibitedActionBlocked` being a zero-expected,
alert-on-any metric (`failure_and_loop_guards.md` §7) is that it must be observable when it
fires.

## 5. Correlation — BC-19

Every span carries `run_id` (correlates the OpenTelemetry trace to the LangSmith run) and
every audit-store write (`escalation_override_log_design.md`'s three record types, plus
`AgentRun`) carries the same `run_id`. This is the entire BC-19 requirement — one correlation
key, present on both sinks, set once at `intake` and never regenerated. No second correlation
scheme is introduced.

## 6. Degraded-mode tracing

Per `langgraph_design.md` §6 and ADR-007: if LangSmith is unreachable, spans are buffered
locally and the run proceeds (observability degrades gracefully — this is the ADR-006
distinction from the Policy Engine, which fails closed). The audit store write at `finalize`
is never skipped regardless of LangSmith availability — `hooks.md`'s `finalize` row already
states a response reaching the caller with no audit write is not a valid terminal state, and
that holds independent of trace-sink health.

## 7. What this stage explicitly does not redesign

No new LangGraph node, no new hook, no new guard. Every span in §2 binds to a node or hook
that already exists (`langgraph_design.md`, `hooks.md`). This stage's contribution is schema
and structure, consistent with `prompts/21`'s own framing ("Prompt 14 already designed the
graph — Prompt 21 makes it explainable after the fact").
