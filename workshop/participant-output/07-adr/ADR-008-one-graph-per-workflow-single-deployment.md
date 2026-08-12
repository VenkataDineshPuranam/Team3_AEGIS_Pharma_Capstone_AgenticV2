# ADR-008 — One LangGraph deployment, one graph per workflow, no cross-workflow agent calls

**Status:** `proposed`
**Evidence basis:** Derivation from `docs/architecture/ddd/context_map.md` (peer contexts,
no direct coupling) and `domain_model.md` §14 (minimum governed workflow).

## Context

`context_map.md` left the deployment topology explicitly open: one LangGraph deployment
hosting all three workflows' agents, or three separate deployments? DDD already established
that the three core contexts are **peers with no direct coupling** — any cross-context need
routes through Evidence & Provenance or Governance.

## Decision

**One deployment, three separate graphs** — one graph per workflow (Batch Review, PV Intake,
Supply Planning), each with its own domain agent + Critic/Verifier + HITL interrupt. No
graph may invoke another graph's agent. Shared capability (evidence retrieval, policy check)
is reached as a *service* (MCP tool / Policy Engine), never as an agent-to-agent call.

## Alternatives considered

- **Three separate deployments** — rejected for now: it would triple operational surface for
  a system whose workflows already share the same evidence layer, policy engine, and
  observability stack. The isolation benefit is largely achieved by separate graphs within
  one deployment.
- **One graph handling all three workflows with conditional routing** — rejected firmly:
  this reintroduces the generalist-agent failure mode already rejected in
  `domain_model.md` §10, where one context would need to hold all three distinct
  prohibited-action boundaries simultaneously.

## Drivers

Operational simplicity; DDD's peer-context isolation; avoiding the generalist-agent risk.

## Consequences

- **Easier:** one deployment to operate, monitor, and secure; shared infrastructure for
  evidence/policy/tracing.
- **Harder:** blast radius is shared — a deployment-level failure affects all three
  workflows at once.
- **Riskier:** noisy-neighbor resource contention between workflows; mitigated by per-graph
  token/step budgets (Stage 08 §I2, Stage 15).

## Guardrails

No graph may import or invoke another graph's agent nodes. Cross-workflow data flow happens
only through Evidence & Provenance, never agent-to-agent.

## Validation

Stage 20: confirm no code path allows one workflow's graph to call another's agent. Stage 18:
red-team an attempt to reach a PV agent from a Batch Review request.

## Revisit triggers

If one workflow's load, latency profile, or compliance/residency requirement diverges
materially from the others (e.g. PV data residency forcing a separate region), split that
workflow into its own deployment.
