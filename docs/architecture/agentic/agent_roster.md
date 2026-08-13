# Agent Roster — Stage 10

**Executes:** `prompts/14_agentic_architecture.md` §1, §3, §6
**Builds on:** DDD `domain_model.md` §10–11 (`stable`), C4 `c4_components.md` (`stable`),
ADR-004/005/008, `docs/quality/dmaic-lean/build_constraints_from_lean.md` §A

**Artifact status:**
- **Batch Review graph — `stable`.** DDD and C4 are both `stable`; this is the interim slice
  (20a) and every element traces to a ratified decision.
- **PV Intake and Supply Planning graphs — `provisional`.** They are designed here by
  *analogy* to Batch Review. RR-2 says explicitly that Batch Review's shape may not transfer
  to PV's duplicate/clock semantics or Supply's option ranking. Marking these `stable` would
  claim a generalization the programme has agreed not to assume until it is re-checked
  (trigger T-10).

---

## 1. What counts as an agent here

An **agent node** is a node whose output depends on an LLM call. Everything else is a
**deterministic node**. The distinction matters because it decides where authority can leak:
only agent nodes can produce unbounded text, so only agent nodes need an authority limit and a
stop condition. Deterministic nodes have contracts, not authority.

**Four agents total across the whole system** — exactly the four DDD §10 names. No agent is
added here.

## 2. Roster

| Agent | Bounded context owned | Graph(s) | Tools it may call (MCP names, contracts at Stage 11) | Authority limit | Stop / escalation condition |
|---|---|---|---|---|---|
| **Batch-Review Agent** | Batch Review | `batch_review` only | `evidence.retrieve` (scoped: batch), `batch.reconcile` | May **synthesize** reconciled evidence into prose and **flag** deviations, gaps, and conflicts. May not rank, score, or characterize batch disposition | Abstain + escalate on: unresolved evidence conflict; incomplete evidence; any draft that the Prohibited-Action Guard flags as release/reject-adjacent; budget cap hit |
| **PV-Intake Agent** | PV Intake | `pv_intake` only | `evidence.retrieve` (scoped: PV), `pv.duplicate_check`, `pv.normalize_terminology` | May **triage/prioritize** signals and **suggest** terminology normalization (suggestion + confidence, never silently applied) | 100% escalation by construction — every PV output routes to a human. Additionally abstains on unresolved duplicate status or clock ambiguity |
| **Supply-Planning Agent** | Supply Planning | `supply_planning` only | `evidence.retrieve` (scoped: supply), `supply.generate_options` | May **rank and explain** options *within* a candidate set that already passed the deterministic constraint filter | 100% escalation by construction. Abstains if the constraint filter returns an empty or unbounded candidate set |
| **Critic/Verifier Agent** | Governance & Oversight (cross-cutting) | All three, **one instance per graph** — not a shared runtime service (ADR-008) | Read-only view of the proposed `DecisionSupportOutput`. **No retrieval, no domain tools** | May **approve-for-human-review** or **reject-back** with a reason code. May never edit domain output | Two rejections with the same reason code ⇒ stop retrying, escalate to HITL with the reason attached (see `failure_and_loop_guards.md` §4) |

**Every row traces to a bounded context and a named authority limit** — the first exit
criterion. The Critic/Verifier's context is Governance & Oversight, which is why it reasons
only over the common `DecisionSupportOutput` contract and never in workflow vocabulary.

## 3. Deterministic nodes — not agents, listed for completeness

These carry the controls. None of them calls an LLM, which is deliberate: **no control in this
system is implemented by a model.**

| Node | Owner context | Responsibility |
|---|---|---|
| `intake` | Agent Orchestration | Validate request; bind the caller's **current** authorization (Entra role resolved at execution time, not at session start); initialize state and budget counters |
| `policy_load` | Governance | Load the versioned policy contract. **Unreachable ⇒ refuse the request** (ADR-005, BC-3). Not a warning, not a cached-policy fallback |
| `retrieve` | Evidence & Provenance | Invoke `evidence.retrieve`. The `untrusted`/`superseded` filter lives **inside the tool, at the retrieval boundary** (ADR-003, BC-2) — non-citable documents never reach the graph, let alone a context window |
| `evidence_gate` | Evidence & Provenance | Assert the post-condition: zero non-citable items in state, evidence sufficient for the request. Insufficient ⇒ route to `abstain`, never to synthesis |
| `reconcile` / `duplicate_check` / `generate_options` | Per core context | Structured, rule-based tool invocation. Produces the candidate set the agent is allowed to reason *within* |
| `prohibited_action_guard` | Governance | Runtime hook on every state transition that produces or mutates output. Blocks and emits `ProhibitedActionBlocked` |
| `hitl_route` | Governance | Resolve the approver role per `hitl_control_model.md` §2, including Supply's dual approval |
| `hitl_interrupt` | Agent Orchestration | LangGraph durable interrupt; default-safe on timeout |
| `finalize` | Governance | Emit the `AgentRun` record and write audit **before** returning to the caller |
| `abstain` | Governance | Terminal safe exit. Records why. **Always a valid outcome** |

## 4. Pattern choice: router–executor–critic, **not** planner–executor–critic

**Decision: no planner agent.** The prompt asks which agent plans; the answer is **none — a
deterministic router plans.**

Reasoning, stated because the constraint says not to add agents without one:

- **There is nothing to plan.** Each governed workflow has a fixed, known sequence: load
  policy → retrieve within scope → gate evidence → run the structured tool → synthesize →
  verify → route to a human. The variability is in *content*, not in *order*. A planner would
  be an LLM re-deriving a sequence that is already written down.
- **A planner is a new authority surface.** An agent that chooses which tools to call and in
  what order can, in principle, choose an order that skips a gate. Deterministic routing makes
  that unrepresentable rather than unlikely — the same argument as ADR-004.
- **It is pure Token and Context waste.** Every planning turn is an extra LLM call plus the
  state re-serialization to feed it (register rows AI-Token, AI-Context), for a plan that is a
  constant.
- **Cost of the choice, stated honestly:** the graph is less adaptive. A genuinely novel
  request shape cannot be handled by re-planning; it hits `abstain` and a human. For a
  decision-support system whose safe default is abstention, that is the correct failure
  direction — but it does mean the graph will abstain on cases a more autonomous design might
  have handled.

**What each role does in the pattern actually used:**

| Role | Implemented by | Why |
|---|---|---|
| Plan | `hitl_route` + the graph's conditional edges (deterministic) | The sequence is a constant; see above |
| Execute | `retrieve`, `reconcile` (tool nodes) + the domain agent for synthesis only | Tools do the structured work; the model does the language work |
| Verify | Critic/Verifier agent **plus** the deterministic guard and evidence gate | Two different kinds of check — see §5 |

## 5. Critic scope — complementary to the deterministic gates, never overlapping (BC-6)

The Critic re-checking what a schema already enforces would be designed-in token waste on
every run (register row E3). The split:

| Check | Owner | Kind |
|---|---|---|
| Prohibited action representable at all | `Batch`/`ShortageOption`/PV output **schema** | Type system — cannot fail at runtime because it cannot compile |
| Prohibited action attempted in generated text | `prohibited_action_guard` | Deterministic hook, closed pattern set |
| Non-citable evidence present | `evidence.retrieve` boundary + `evidence_gate` | Deterministic status lookup |
| Every claim carries a citation, and every citation resolves to an item actually in state | **Critic** | Requires reading the prose |
| Claims are supported by the cited evidence, and no claim exceeds what the evidence says | **Critic** | Judgement — the one thing here a model is genuinely better at |
| Abstention used where the evidence is insufficient | **Critic** | Judgement |
| Output conforms to `DecisionSupportOutput` | Schema validation | Deterministic |

**Rule:** if a check can be expressed as a lookup, a type, or a pattern match, the Critic does
not perform it. The Critic exists for the checks that require reading the argument.

## 6. Cross-workflow reuse

**Shared as a compile-time template; never shared at runtime.** ADR-008 forbids cross-graph
calls, so "reuse" here means three graph instances built from one template — not one graph
serving three workflows, and not a service the three graphs call.

| Element | Shared? | Note |
|---|---|---|
| Governed spine: `intake` → `policy_load` → … → `hitl_interrupt` → `finalize` / `abstain` | **Yes — template** | Identical structure, instantiated three times |
| `prohibited_action_guard` | **Yes — code**, with a **per-workflow prohibition contract injected** | The mechanism is shared; the prohibition list is not. Workflow A's list (release/reject/reprocess/relabel/recall) must never be loaded into workflow B's graph |
| Critic/Verifier | **Yes — node implementation**, one instance per graph, per-workflow contract injected | Reasons only over `DecisionSupportOutput`, so it needs no workflow vocabulary |
| State schema | **Yes — base**, with a per-workflow `domain_payload` extension | Base carries governance/budget/evidence; extensions carry workflow specifics |
| Domain agent nodes | **No** | One per context, by design (DDD §10 rejects a generalist) |
| Tools, retrieval scopes, approver routing | **No** | Per context |

**Reuse is a hypothesis, not a finding.** Everything above is designed from Batch Review's
shape. Per RR-2/T-10, each element must be re-checked when PV and Supply are actually built at
20b — particularly the state schema base, which assumes a single approver decision and a
single candidate set, and may not fit Supply's dual approval or PV's clock reconstruction.

## 7. Exit criteria

- [x] Every agent traces to a DDD bounded context and a named authority limit — §2.
- [x] Every HITL interrupt matches a domain-critical decision from DDD §11 — see
      `langgraph_design.md` §5; all three approver roles are the ones named in
      `hitl_control_model.md`, with **Manufacturing VP explicitly excluded** for Batch Review.
- [x] Loop guards and budgets are numeric — `failure_and_loop_guards.md` §2–3. The HITL
      timeout is a four-tier escalation ladder (§5), with durations set per workflow;
      Stage 16 confirms them with the accountable roles, and PV's 24h expiry additionally
      needs verification against V2's actual reporting-clock material before it is final.
- [x] Artifact status stated, split by graph, with the reason for the split.
