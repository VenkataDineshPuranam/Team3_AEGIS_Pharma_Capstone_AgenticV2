# Build Constraints from Lean (Stage 09)

**Executes:** `prompts/09_lean_dmaic.md` §D
**Consumers:** Stages 10 (agentic architecture), 11 (MCP), 12 (skills/hooks), 13 (ontology) —
and, through them, Stage 20 (implementation)
**Artifact status: `stable`**

Three buckets, per the prompt: **must-fix-before-build**, **fix-in-pilot**, and
**accept-as-residual-risk**. "Before build" means before the corresponding design stage
finalizes — not before Stage 20, which would be too late to change anything cheaply.

---

## A. Must fix before build

Each of these, if deferred, becomes structurally expensive or unsafe to retrofit.

| ID | Constraint | Waste it removes | Owner stage | Why it cannot wait |
|---|---|---|---|---|
| **BC-1** | **Prohibited-Action Guard exists from day one**, in all three layers (absent schema field, absent tool method, runtime guard). No workflow slice ships without it | D1 | 10, 12, 16 | ADR-004's entire argument is that this control cannot be retrofitted — retrofitting means the unsafe representation already existed |
| **BC-2** | **Evidence status gate sits at the retrieval boundary**, filtering `untrusted`/`superseded` **before** ranking. Content never self-declares authority | D2, AI-Retrieval, AI-Model(b) | 11, 13 | Filtering after generation means the model already read it. Post-hoc filtering is not the same control |
| **BC-3** | **Governance/Policy Engine is a separate container that fails closed**; unreachable ⇒ refuse | D3 | 16 | A fail-open default written in code is an incident waiting for an outage. Cheap now, invasive later |
| **BC-4** | **Stage 10 designs agents against an ontology *contract*; Stage 13 fills it in.** No agent is built against ad-hoc raw-document RAG | E1 | 10 → 13 | Resolves `lens_rollup.md` C1 — the stage order (10 before 13) contradicts Stage 01's advice, and the contract-first approach is the option that makes the order safe |
| **BC-5** | **Explicit retry / backoff / diagnosis rules — no blind retry.** A retry must record why the previous attempt failed | AI-Model(a) | 10 | Gap G3 — this item lost its owner in the resequencing. Retry policy is a graph-structure decision, not a tuning knob added later |
| **BC-6** | **Critic/Verifier scope is complementary to the deterministic gates, never overlapping.** The Critic does not re-check what a schema or status lookup already enforces | E3, AI-Token | 10 | Overlap is designed-in token waste on every single run |
| **BC-7** | **Token/cost accounting is emitted from the first run**, per node and per graph — not added after the topology is judged | AI-Token (U1) | 10, 17, 20 | The interim state's whole purpose includes assumption 6. Un-instrumented first runs waste the only chance to measure cheaply |
| **BC-8** | **Trace redaction rules are written before the first trace is written** | AI-Observability(b) | 17 | PII already in a trace store is an incident, not a backlog item |
| **BC-9** | **LangGraph shared-state schema is the single source of truth**; no per-agent context reconstruction | AI-Context | 10 | The schema is the graph's spine; changing it later touches every node |
| **BC-10** | **Versioned MCP schemas with contract tests** in `tests/contract/` from the first tool | AI-Integration | 11 | Unversioned contracts drift silently; version-after-the-fact requires a migration |
| **BC-11** | **Zero cross-graph agent invocations**, enforced structurally rather than by convention | T3, D1 | 10 | ADR-008. A convention is not an enforcement |
| **BC-12** | **HITL timeout ⇒ no action**, never auto-proceed; named approver **roles** (not individuals) wired to the routing | W2, AI-Human-review | 16 | A default-proceed timeout is the single most dangerous default in the system |

## B. Fix in pilot (the interim state / Batch Review slice)

Deferred deliberately — these need either a running system or real measurements to resolve
correctly. Fixing them by guesswork now would be worse than fixing them later with data.

| ID | Item | Waste | Resolves at | What it waits on |
|---|---|---|---|---|
| **BC-13** | Numeric token/cost budgets per graph and per node | AI-Token | Stage 15 | U1 from interim assumption 6. The *mechanism* is BC-7/I-9; only the numbers wait |
| **BC-14** | Latency SLOs, including whether ADR-005's extra hop is material | T2 | Stage 15 | U2, U6 |
| **BC-15** | Hop-count tolerance band around the designed 7 | T1 | Stage 12 | U5 from interim assumption 7 |
| **BC-16** | Fast-subset vs. full-regression eval split | AI-Evaluation | Stage 14 | U3 and an observed suite runtime |
| **BC-17** | Batch Review HITL risk-tiering | AI-Human-review, N2 | Stage 16 | U7. **PV and Supply are not candidates** — 100% routing is regulatory |
| **BC-18** | Cache design: status-aware keys, no as-if-cached fallback | D5, I1 | Stages 14–15 | Correctness of the uncached path being proven first |
| **BC-19** | Trace-to-audit correlation IDs so one run is followable end-to-end | M2 | Stage 17 | A running system to trace |
| **BC-20** | Consume `eval-ai-cache/` (29 files) and decide NAB-3 (copy V1 `knowledge/`+fixtures locally vs. cross-repo reference) | O3 | Stages 13, 14 | A decision, not data — but it is cheapest to make when Stage 13/14 opens |

## C. Accept as residual risk

Named, owned, and **not** mitigated further. Each carries the trigger that would force a
re-decision.

| ID | Residual risk | Why accepted | Re-decision trigger |
|---|---|---|---|
| **RR-1** | **Topology was locked without a cost number.** ADR-008 was accepted while U1 remained Unknown, contrary to Stage 01's stated precondition | ADR-008's constraints are conservative in the cost-reducing direction, and waiting would have blocked all of Stages 05–08 | **T-3** — interim assumption 6 materially above expectation reopens ADR-008 *before* the pattern is built three times |
| **RR-2** | **Single-workflow generalization.** Batch Review's evidence-reconciliation shape may not transfer to PV's duplicate/clock semantics or Supply's option ranking | Proving one workflow properly beats proving three ambiguously | **T-10** — every interim conclusion must be re-checked per workflow at Stage 20, never assumed to transfer |
| **RR-3** | **Shared blast radius.** One deployment serves all three graphs (ADR-008) | Deliberate, accepted trade-off: operational simplicity over isolation, with graph-level separation preserved | A production incident where one graph's failure affects another |
| **RR-4** | **9 containers exceed DDD's "minimum governed workflow"** | Each addition (Redis, LangSmith, separate audit store) answers a specific named risk. Reconciled at `lens_rollup.md` C2: DDD minimalism governs the interim state, C4 completeness the final state | A container that cannot name the risk it answers |
| **RR-5** | **Vendor concentration** — Microsoft *and* the model provider. V1's source-system pack flags "bundled vendor, weak cost controls" as a known org failure pattern | Sponsor directive (ADR-009). OpenTelemetry keeps the trace backend swappable; Redis and the audit store are substitutable | A material pricing or availability event |
| **RR-6** | **Air-gapped GxP-network deployment is not supported** | Sponsor confirmed cloud-connected operation is acceptable (EAB-2 closed); recorded as a known limitation in ADR-007 | **T-5** — a later hard air-gap requirement reopens ADR-001 and ADR-007 |
| **RR-7** | **Dual audit-sink duplication** (ADR-006) | The alternative couples a regulatory retention obligation to a vendor SLA | Audit-write success dropping below 100% while LangSmith is healthy |
| **RR-8** | **Fallback-path test burden** (ADR-007) | Untested fallbacks are worse than no fallbacks | Only if the burden makes the suite unrunnable — then split it (BC-16), do not cut coverage |
| **RR-9** | **Approval-path coverage in the interim state is partial** — one approver role exercised; Supply's dual approval untested | Proving the mechanism is the interim state's job; coverage is the final state's | Final state cannot be declared complete with dual approval untested |

---

## Handoff to Stage 10

Stage 10's task order should be: **BC-1, BC-9, BC-11 first** (the structural spine — guard,
state schema, graph isolation), then **BC-4, BC-5, BC-6** (contract-first retrieval, retry
rules, Critic scope), then **BC-7** (instrumentation) before any node is considered done. That
ordering front-loads the two stop-the-line assumptions (interim §3 items 1 and 2) and the one
measurement the whole programme has been deferring since Stage 01.
