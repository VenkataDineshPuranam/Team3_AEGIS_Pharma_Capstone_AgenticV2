# Boundaries & Degraded Mode — Stage 03 (C4)

**Artifact status:** `stable` (EAB-2 and EAB-3 both closed)

## Trust boundary

Domain-agent output is **untrusted** until it clears the Critic/Verifier node and (for
PV/Supply, always; for Batch Review, when the agent cannot self-resolve) the named human
approver. Only Governance & Oversight's Policy Register is trusted axiomatically — it is
the one component every other container conforms to (per `context_map.md`'s open-host-service
relationship), and it is not something a domain agent can influence at runtime.

## Data boundary

Every external system in `c4_context.md` is **read-only**. No container in this system has
outbound write capability to any V1 brownfield source system (Manufacturing, Laboratory,
Quality, Safety, Supply). This is the architecture-level enforcement matching DDD's
schema-level constraint — two independent layers implementing the same non-negotiable, which
is intentional redundancy, not duplication to clean up.

## Privacy boundary

LangSmith traces and the Audit/Evidence Log Store must both pass through redaction before
storage — PII/PHI must never leave the Orchestrator API boundary unredacted. This is a
**Stage 17 (observability) design requirement**, flagged here because the C4 view is where
the trace's *destination* (an external, hosted service) becomes visible as an architectural
fact, not just a policy statement.

## Authority boundary

Only the Governance/Policy Engine may authorize a HITL bypass (there should be none for
PV/Supply; Batch Review's self-resolution path is itself governed by the Prohibited-Action
Guard, not by agent judgment). No domain agent or MCP tool server can self-authorize.

## Degraded / offline mode

V1's `CLAUDE.md` names a hard requirement inherited here: **"maintain an offline
deterministic mode and AI-disabled continuity path."** V2's hosted dependencies (LLM
provider, LangSmith, Redis) each need an explicit degraded-mode behavior — this is exactly
the EAB-2 tension flagged in Stage 01, now made concrete per dependency:

| Dependency | Failure mode | Required degraded behavior |
|---|---|---|
| LLM provider (Anthropic) unreachable | No agent reasoning possible | System must fall back to a deterministic, rules-only mode for the parts of each workflow that don't require generative reasoning (e.g., rule-based evidence-authority resolution can still run); anything requiring generation must abstain, not guess |
| LangSmith unreachable | No hosted tracing | **Must not block the request.** Trace locally (Audit/Evidence Log Store) and sync to LangSmith when available; this is the direct architectural resolution of EAB-2 — LangSmith is additive observability, not a hard dependency, because the Audit/Evidence Log Store is deliberately a separate container |
| Redis unreachable | No cache | Fall back to no-cache (slower, costs more) — **never** serve a response as-if-cached when the cache is down; correctness over performance, always |
| MCP Tool Server unreachable | Agent cannot retrieve evidence/execute a tool | Agent must abstain and escalate to HITL — never proceed with an unretrieved-evidence guess |

**This resolves EAB-2 architecturally**: V2 is not "offline-compatible" in the sense V1's
static app was (zero network dependency), but it is **degraded-mode-safe** — every hosted
dependency has a defined, safe fallback that preserves correctness even if it sacrifices
some capability (tracing completeness, cache speed). This distinction should be written up
explicitly as an ADR (see `adr_candidates.md`).

## Prohibited operational write paths

Restated from `c4_context.md`: zero write integrations to any brownfield source system.
Additionally, per DDD: the Supply-Planning Agent's tool has no allocation/reservation write
method; the Batch-Review Agent's aggregate schema has no release/reject field; the PV-Intake
Agent's output schema has no causality/seriousness/reportability field. All three are
structural, not permission-based.
