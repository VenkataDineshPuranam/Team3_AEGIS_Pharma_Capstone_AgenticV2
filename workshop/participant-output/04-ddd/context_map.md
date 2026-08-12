# Context Map — Stage 02 (DDD)

**Artifact status:** `stable` (inherits from `domain_model.md`, upgraded on EAB-3 closure)

Extracted from `domain_model.md` §4–5 for standalone reference (the prompt's required
`context_map.md` output). See `domain_model.md` for full bounded-context definitions,
including owners and the events/entities each context governs.

## Bounded contexts

| Context | Type | Owner |
|---|---|---|
| Batch Review | Core | Chief Quality Officer / EU Qualified Person |
| PV Intake | Core | Global Head of Pharmacovigilance |
| Supply Planning | Core | Supply Chain VP (+ Quality co-approval) |
| Evidence & Provenance | Supporting | Platform/shared |
| Governance & Oversight | Supporting | Chief Quality Officer, CISO, Data Protection Officer |
| Agent Orchestration | Generic | Engineering/Platform |

## Map

```
                    ┌─────────────────────────┐
                    │  Governance & Oversight   │  (upstream to all — open-host
                    │  (policy, HITL, audit)     │   service / published language)
                    └────────────┬────────────┘
                                 │ policy contract
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
      ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
      │ Batch Review   │  │  PV Intake     │  │ Supply Planning│   (core, peer contexts —
      │  (core)        │  │  (core)        │  │  (core)        │    no direct coupling)
      └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                    ┌─────────────────────────┐
                    │  Evidence & Provenance   │  (upstream, shared kernel —
                    │  (authority, conflicts)   │   conformist: core contexts accept
                    └────────────┬────────────┘   its evidence contract as-is)
                                 ▼
                    ┌─────────────────────────┐
                    │   Agent Orchestration     │  (generic/technical, hosts
                    │   (LangGraph runtime)      │   all of the above at runtime)
                    └─────────────────────────┘
```

## Relationship types

| Relationship | DDD pattern | Rationale |
|---|---|---|
| Governance & Oversight → {Batch Review, PV Intake, Supply Planning, Agent Orchestration} | Open-host service / published language | Versioned policy contract every context conforms to; deliberately not a shared kernel so it can't be silently weakened locally |
| Evidence & Provenance → {Batch Review, PV Intake, Supply Planning} | Shared kernel (conformist downstream) | All three core contexts consume one evidence-authority model |
| {Batch Review, PV Intake, Supply Planning} ↔ each other | Peer, no direct coupling | Any cross-workflow need routes through Evidence & Provenance or Governance, never context-to-context directly |
| Agent Orchestration → all | Technical hosting | Not a business relationship — Agent Orchestration owns no domain decisions |

## Anti-corruption requirements

- The Critic/Verifier Agent (Governance & Oversight) must never absorb batch-review-,
  PV-, or supply-specific vocabulary directly — it interacts with all three core contexts
  only through the common `DecisionSupportOutput` contract (Stage 08 §I2), which is this
  map's anti-corruption layer.
- Evidence & Provenance must translate each source system's local evidence representation
  (V2's brownfield, multi-source estate — `case/SOURCE_SYSTEM_FACT_PACK.md`) into the
  common `EvidenceItem` value object before any core context sees it; core contexts must
  never reach past Evidence & Provenance to a raw source system directly.

## Open questions for Stage 03/04 (C4, ADR)

- Whether Agent Orchestration is one LangGraph deployment hosting all three core contexts'
  agents, or three separate deployments — this map takes no position; it is a C4/ADR
  decision, not a domain one.
- ~~Real owner names for the three TBD roles (EAB-3)~~ — **closed**, see
  [`hitl_control_model.md`](../../governance/hitl_control_model.md).
