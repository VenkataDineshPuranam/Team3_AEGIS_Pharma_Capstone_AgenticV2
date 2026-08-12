# ADR-006 — Compliance audit records live in an owned store, separate from LangSmith traces

**Status:** `proposed`
**Evidence basis:** Derivation (compliance retention needs, Stage 19) + fact (LangSmith is an
external hosted service outside our operational control).

## Context

`AgentRun` records (DDD §7) serve two distinct purposes that are easy to conflate:
engineering debugging (rich, high-volume, short-lived) and compliance evidence (EU AI Act /
ISO 42001, Stage 19 — durable, retention-governed, must be producible on demand). LangSmith
serves the first well. It is a third-party hosted service with its own SLA and retention
policy.

## Decision

Maintain a **separate, owned Audit/Evidence Log Store** as the system of record for
compliance-relevant `AgentRun` data. LangSmith remains the tracing/eval/debugging backend,
and is **additive, never load-bearing** for compliance or for request success.

## Alternatives considered

- **LangSmith as the sole record** — rejected: couples a regulatory retention obligation to a
  third-party SLA and retention policy we do not control.
- **Owned store only, no LangSmith** — rejected: forfeits the LLM-native eval/regression
  tooling that ADR-001 selected LangSmith for.

## Drivers

Regulatory retention independence; avoiding a hosted dependency on the compliance path.

## Consequences

- **Easier:** compliance evidence (Stage 19) has a guaranteed, inspectable home; the system
  keeps working correctly when LangSmith is unreachable.
- **Harder:** two sinks to write and keep consistent; some duplication of trace data.
- **Riskier:** the two could silently diverge — mitigated by the Control check in
  `c4/dmaic_lens.md` (verify the audit store is still receiving records even when LangSmith
  is healthy).

## Guardrails

Both sinks must be redacted before write — PII/PHI must never leave the Orchestrator
boundary unredacted (Stage 17 requirement). Request success must never depend on either sink
being reachable.

## Validation

Stage 14/17: run the eval suite with LangSmith unreachable — all evals must still pass and
audit records must still be written.

## Revisit triggers

If LangSmith offers contractual retention/residency guarantees that satisfy Stage 19's
requirements, the duplication may become unjustified — re-evaluate then.
