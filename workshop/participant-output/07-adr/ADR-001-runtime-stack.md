# ADR-001 — Runtime stack: LangGraph, LangSmith, Redis

**Status:** `accepted`
**Evidence basis:** Fact (explicit user/sponsor directive recorded in
`docs/product/discovery/discovery.md` §5) — not a technical derivation.

## Context

V3 must be a multi-agent system with governance, control, and observability
(`discovery.md` §5). A stateful orchestration mechanism, a tracing/eval backend, and a
response cache are all required by the architecture in `docs/architecture/c4/`.

## Decision

Use **LangGraph** for multi-agent orchestration (stateful graphs, checkpointing, HITL
interrupts), **LangSmith** for tracing/evals/cost-latency observability, and **Redis** for
the response cache.

## Alternatives considered

- Custom orchestration loop — rejected: checkpointing and HITL interrupt semantics are
  exactly what LangGraph provides natively; rebuilding them is Overproduction waste.
- OpenTelemetry-only observability without LangSmith — rejected as the *primary* choice,
  but retained as a complement (see ADR-006); OTel alone lacks LLM-specific eval/regression
  tooling.

## Drivers

Sponsor directive; native HITL-interrupt and checkpointing support; LLM-aware tracing.

## Consequences

- **Easier:** HITL interrupts, graph state, checkpoint/resume, trace-level debugging.
- **Harder:** introduces three infrastructure dependencies V2 never had, two of them
  networked — this is the direct cause of the degraded-mode work in ADR-007.
- **Riskier:** vendor concentration (V2's `case/SOURCE_SYSTEM_FACT_PACK.md` explicitly
  names "bundled vendor, stale entitlements… weak cost controls" as a known failure
  pattern in this organization's AI-platform estate — V3 should not repeat it).

## Guardrails

No agent logic may depend on LangSmith being reachable (ADR-006/007). Redis is a cache,
never a system of record.

## Validation

Stage 20 build must demonstrate a working HITL interrupt and a checkpoint/resume; Stage 14
evals must pass with LangSmith unreachable.

## Revisit triggers

Vendor pricing/availability change; if LangGraph's HITL semantics prove insufficient for
the 100%-routing requirement in `domain_model.md` §11.
