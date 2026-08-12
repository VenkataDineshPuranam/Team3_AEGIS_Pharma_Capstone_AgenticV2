# ADR-007 — V3 is "degraded-mode-safe," not "offline-capable"

**Status:** `accepted` — sponsor confirmed cloud-connected operation is acceptable
(EAB-2 closed). The reframing below is ratified, not assumed.
**Evidence basis:** Fact (V2's `CLAUDE.md` requires "an offline deterministic mode and
AI-disabled continuity path"; ADR-001's stack introduces networked dependencies; sponsor
decision on EAB-2).

## Context

V2 was genuinely offline-capable: a static app with zero network dependency. V3's directed
stack (ADR-001) includes an LLM provider, LangSmith, and Redis — two of them networked
services. This is EAB-2 from `docs/product/discovery/evidence_acquisition_backlog.md`, and
it is a real departure from a stated V2 non-negotiable, not a detail.

## Decision

V3 targets **degraded-mode-safe**, defined as: every hosted dependency has an explicit,
documented fallback that preserves *correctness* even when it sacrifices *capability*.
Specifically (from `docs/architecture/c4/boundary_and_degraded_mode.md`):

| Dependency | Fallback |
|---|---|
| LLM provider unreachable | Rules-only deterministic mode for non-generative steps; **abstain** on anything requiring generation — never guess |
| LangSmith unreachable | Trace locally to the owned audit store, sync later; never block the request (ADR-006) |
| Redis unreachable | No-cache mode; **never** serve a stale response as-if-cached |
| MCP tool server unreachable | Agent abstains and escalates to HITL; never proceeds on unretrieved evidence |
| Policy Engine unreachable | **Fail closed** — refuse the request (ADR-005) |

V2's "AI-disabled continuity path" requirement is satisfied by the LLM-unreachable row: the
deterministic rules layer (evidence-authority gating per ADR-003, unit/identity checks) runs
without any model call.

## Alternatives considered

- **Preserve literal offline capability** — rejected: incompatible with a LangGraph/LLM
  architecture. Claiming it would be false.
- **Ignore the tension** — rejected: it would silently drop a stated non-negotiable.

## Drivers

Honesty about a real constraint change; preserving the *intent* behind V2's rule (the system
must not become unusable or unsafe when a dependency fails).

## Consequences

- **Easier:** each dependency's failure behavior is explicit and testable rather than
  assumed.
- **Harder:** every fallback path needs its own test coverage (Stage 14).
- **Riskier:** V3 genuinely cannot run air-gapped. If the sponsor requires true air-gap, the
  entire stack decision (ADR-001) reopens.

## Guardrails

No fallback may trade correctness for availability. "Fail closed" for authorization,
"degrade gracefully" for observability — never the reverse.

## Validation

Stage 14: run the eval suite with each dependency disabled in turn; all correctness gates
must still pass (capability may reduce).

## Known limitation (recorded, not papered over)

This decision is correct for the capstone/workshop deployment context. **A real deployment
inside a GxP manufacturing network would likely require the air-gapped variant** — self-hosted
open-weight models on on-prem GPUs and a self-hosted trace backend — which would change model
choice, cost model, eval approach, and probably output quality. That variant is out of scope
here by explicit sponsor decision, and is recorded so the limitation is visible to anyone
reading this as a production design rather than discovered later.

## Revisit triggers

If the deployment target changes to a GxP manufacturing network or any environment without
outbound internet, this ADR and ADR-001 both reopen. The V2 non-negotiable that motivated
the original tension ("AI-disabled continuity path") remains satisfied either way by the
deterministic rules layer.
