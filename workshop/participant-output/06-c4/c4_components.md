# C4 Level 3 — Components — Stage 03

**Artifact status:** `stable` (EAB-2/EAB-3 closed). Scoped to the containers with the most decision-workflow
risk: Orchestrator API, MCP Tool Servers, Governance/Policy Engine — per the prompt's
guidance to deepen only where risk warrants.

## Orchestrator API — components

| Component | Responsibility | DDD mapping |
|---|---|---|
| LangGraph state schema | Shared state object all nodes read/write; single source of truth for in-flight request data | Cross-cutting (Stage 08 §I2 will formalize) |
| Batch-Review Agent node | Executes the Batch-Review Agent's reasoning turn | `domain_model.md` §10 |
| PV-Intake Agent node | Executes the PV-Intake Agent's reasoning turn | §10 |
| Supply-Planning Agent node | Executes the Supply-Planning Agent's reasoning turn | §10 |
| Critic/Verifier node | Checks any domain agent's proposed output against the prohibited-action contract and evidence-citation completeness before it can reach a human | §10 |
| HITL interrupt handler | Pauses graph execution, notifies the named approver role, and enforces default-safe-on-timeout (no action, never auto-proceed) | §11 |

## MCP Tool Servers — components

| Component | Capability | Write access? |
|---|---|---|
| Evidence Retrieval tool | Scoped, per-bounded-context retrieval through the Evidence & Provenance semantic layer; filters `untrusted`-status documents at the retrieval boundary | Read-only |
| Reconciliation tool (Batch Review) | Structured evidence-completeness/conflict check | Read-only |
| Duplicate-Check tool (PV Intake) | Case-duplicate detection | Read-only |
| Option-Generation tool (Supply Planning) | Constraint-filtered candidate option generation | Read-only, and **structurally has no allocation/reservation write method at all** — per DDD §10, this is a tool-capability constraint, not a permission the agent chooses not to use |

## Governance/Policy Engine — components

| Component | Responsibility |
|---|---|
| Prohibited-Action Guard | Runtime hook checking every domain-agent output against the schema-level prohibited-action constraint (`domain_model.md` §7) before it can proceed past the Critic/Verifier node |
| HITL Router | Determines which named role must approve a given output, per `domain_model.md` §11's 100%-routing rules for PV/Supply |
| Policy Register loader | Loads the versioned policy contract that the open-host-service relationship (`context_map.md`) publishes to every other context |

## Level 4 (Code) — deferred

Not produced this stage. Per the prompt's guidance ("deepen Code level only where risk
warrants"), and because no implementation exists yet (Stage 20 is deliberately last), a
Code-level view would be speculative. The one invariant worth flagging now for Stage 20:
the `Batch` aggregate's schema (DDD §7) must be validated as **structurally** incapable of
carrying a release/reject field — this should become a concrete schema/type definition,
not a runtime check alone, when Stage 20 implements it.
