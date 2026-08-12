# ADR-005 — Governance/Policy Engine is a separate container, not embedded in the Orchestrator

**Status:** `accepted` (upgraded when EAB-3 closed and DDD reached `stable`)
**Evidence basis:** Derivation from `docs/architecture/ddd/context_map.md`'s open-host-service
relationship; no measured evidence yet.

## Context

DDD models Governance & Oversight as an **open-host service** publishing a versioned policy
contract to every other context — deliberately not a shared kernel, so policy cannot be
locally weakened by a core context's convenience. C4 raised the container question:
separate deployable, or embedded in the Orchestrator API?

## Decision

Deploy the Governance/Policy Engine as a **separate container** with an independently
versioned policy contract.

## Alternatives considered

- **Embedded in Orchestrator API** — rejected for now: simpler ops and one fewer network hop,
  but it makes the policy contract share a release cycle with the orchestrator, which
  structurally reintroduces exactly the "policy weakened for local convenience" risk the DDD
  pattern exists to prevent.

## Drivers

Independent versioning of policy; auditability (a compliance reviewer can inspect one
component); preventing policy drift across three core contexts.

## Consequences

- **Easier:** policy changes ship and are audited independently; single inspection point for
  Stage 19 compliance evidence.
- **Harder:** one more network hop on the common path (`dmaic_lens.md` measured the path at
  7 crossings, which includes this hop); one more deployable to operate.
- **Riskier:** Governance becomes a runtime dependency of every request — it must be highly
  available or fail *closed* (deny), never fail open.

## Guardrails

**Fail closed.** If the Policy Engine is unreachable, requests must be refused, not allowed
through unchecked. This is the inverse of the LangSmith rule in ADR-006 and the distinction
is deliberate: observability may degrade gracefully, authorization may not.

## Validation

Stage 20: demonstrate that Policy Engine unavailability blocks (not bypasses) a request.
Stage 15: measure whether the added hop is material against the latency budget.

## Revisit triggers

If Stage 15 latency measurement shows the extra hop is a material cost driver, **or** if
operational burden proves disproportionate for a system with only one policy consumer per
workflow — re-evaluate embedding it with a compensating control (e.g. policy contract in a
separately-signed, separately-versioned artifact even if co-deployed).
