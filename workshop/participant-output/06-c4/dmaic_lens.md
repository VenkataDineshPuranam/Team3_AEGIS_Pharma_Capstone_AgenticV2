# DMAIC Lens — Stage 03 (C4)

**Full cycle** (C4 is a designated full-DMAIC stage, alongside Discovery/01, Frame/01(SCQA),
DDD/02, ADR/04). Builds on Stage 02's full DMAIC output.

## Define

Restated at architecture granularity: which container/component boundary exists
specifically to eliminate a named waste? Answer: the **Audit/Evidence Log Store as a
container separate from LangSmith** exists specifically to eliminate an Observability-waste
risk (Stage 01 register) — coupling compliance-critical audit retention to a third-party
hosted SLA would be exactly the kind of "logs/metrics with no owner" risk that register
named, except inverted (owned but fragile, rather than unowned).

## Measure

Architectural metrics as proxies for Transportation/Waiting waste, counted directly from
`c4_components.md`'s design (current/target, since no implementation exists to measure
against yet):

- **Hop count, common path (Batch Review request):** Web App → Orchestrator API →
  Batch-Review Agent node → MCP Tool Server (Evidence Retrieval) → Evidence & Provenance
  Store → *(return)* → Critic/Verifier node → Governance/Policy Engine (HITL check) → *(if
  escalation)* HITL notification → *(return)* → Web App. **Counted: 7 container/component
  boundary crossings one-way**, before any HITL round-trip. Target: keep this at or below 7
  for the minimum governed workflow (Stage 02 DDD §14); any design change that raises this
  count needs an explicit justification.
- **Sync-call depth:** 3 (Web App → Orchestrator → MCP Tool Server is the deepest
  synchronous chain in the common path; Agent Workers exist specifically to take
  long-running work off this synchronous path).
- **Fan-out:** Governance/Policy Engine fans out to 4 consumers (3 core-context agents +
  Agent Orchestration's HITL interrupt handler) — this is the direct architectural
  expression of the open-host-service pattern from `context_map.md`, not accidental
  coupling.

## Analyze

Does the map reduce Transportation/Integration waste? The peer-context-no-direct-coupling
design (DDD §5, carried into `c4_context.md`) means no request ever crosses core-context
boundaries directly — every cross-context need routes through Evidence & Provenance or
Governance, which are both single, well-defined hops, not N-to-N coupling. Where could
containers create Waiting? The HITL interrupt is an intentional wait (business-required
NVA, same classification as Stage 01's DOWNTIME register gave V1's sequential prompt
pipeline) — but the *async* Agent Workers container exists specifically so a long-running
Supply Planning search doesn't force the whole request into a synchronous wait. Risk of
Observability waste: addressed by the separate Audit/Evidence Log Store (Define, above).
Any over-built containers vs. minimum governed workflow? **Yes, flagged honestly:** 9
containers is more than the DDD's "minimum governed workflow" (one domain agent + evidence
tool + critic + HITL gate, per workflow) strictly requires — Redis, LangSmith, and the
separate Audit store are all justified by *specific* named risks (cache, observability,
compliance) rather than by the minimum-workflow principle itself, which is a legitimate but
worth-flagging tension between DDD's minimalism and C4's operational completeness.

## Improve

The architecture is the Improve artifact. Per container, what it removes and its accepted
trade-off:
- **Separate Governance/Policy Engine:** removes Defects risk (policy drift across
  contexts) at the cost of one more network hop — trade-off flagged for ADR ratification
  (`adr_candidates.md` #3).
- **Separate Audit/Evidence Log Store:** removes Observability/compliance-coupling risk at
  the cost of one more data store to operate — ADR candidate #4.
- **Agent Workers as a distinct container from Orchestrator API:** removes Waiting waste
  (long-running work blocking the synchronous path) at the cost of an async-consistency
  design burden (Stage 20's problem to solve concretely).
- **Redis Cache with defined no-cache fallback (not "cache required"):** removes Token waste
  (repeat identical queries) without accepting Inventory waste (stale-cache risk) — the
  fallback-to-no-cache rule in `boundary_and_degraded_mode.md` is the explicit mechanism.

## Control

Which container/component needs a health/SLO check so architectural drift or degraded mode
is caught operationally (feeds `boundary_and_degraded_mode.md`, firmed up at Stage 09/12,
implemented Stage 17):
- Hop-count regression: if Stage 20's actual implementation exceeds the 7-hop baseline
  measured here without a documented reason, that's a Stage 12 assurance finding.
- Each hosted dependency (LLM provider, LangSmith, Redis) needs a health check feeding its
  documented degraded-mode fallback — not just a design intention.
- The Audit/Evidence Log Store's independence from LangSmith needs a periodic check that it
  is actually receiving records even when LangSmith is healthy (proving the "separate for a
  reason" design isn't silently degrading to LangSmith-only in practice).

## Waste register updates

See `waste_register_downtime.md` and `waste_register_ai_specific.md` (this folder).
