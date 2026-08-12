# Decision Index — Stage 04 (ADR)

| ADR | Title | Status | DDD context | C4 element | Evidence basis | Blocked on backlog? |
|---|---|---|---|---|---|---|
| [001](ADR-001-runtime-stack.md) | Runtime stack: LangGraph, LangSmith, Redis | `accepted` | Agent Orchestration (generic) | Orchestrator API, Redis Cache, LangSmith | Fact (sponsor directive) | No |
| [002](ADR-002-build-v3-separate-from-v2.md) | V3 built separately from V2 | `accepted` | All | Whole system | Fact (user decision) + verified V2 constraints | No |
| [003](ADR-003-evidence-authority-deterministic-gate.md) | Evidence authority is a deterministic gate; `untrusted` **and** `superseded` non-citable | `accepted` | Evidence & Provenance | Evidence Retrieval tool, Semantic Layer | **Fact — verified against V2 grader code** | No |
| [004](ADR-004-prohibited-actions-structurally-unrepresentable.md) | Prohibited actions structurally unrepresentable | `accepted` | All three core contexts + Governance | Aggregate schemas, MCP tools, Prohibited-Action Guard | Fact (V2 case pack) + derivation | No |
| [005](ADR-005-governance-as-separate-container.md) | Governance/Policy Engine as separate container | `proposed` | Governance & Oversight | Governance/Policy Engine container | Derivation | No |
| [006](ADR-006-audit-store-separate-from-langsmith.md) | Audit store separate from LangSmith | `proposed` | Governance & Oversight (audit) | Audit/Evidence Log Store | Derivation | No |
| [007](ADR-007-degraded-mode-safe-not-offline-capable.md) | Degraded-mode-safe, not offline-capable | `proposed` | Cross-cutting | All hosted dependencies | Fact + **assumption (sponsor acceptance)** | **Yes — EAB-2**, needs sponsor confirmation (flag for Stage 21) |
| [008](ADR-008-one-graph-per-workflow-single-deployment.md) | One deployment, one graph per workflow | `proposed` | All three core contexts | Orchestrator API | Derivation | No |

## Status summary

- **4 `accepted`** — those resting on fact (sponsor directives, verified V2 behavior, or
  verbatim regulatory constraints).
- **4 `proposed`** — those resting on derivation or unconfirmed assumption. Per
  `prompts/07_adrs.md`, material decisions stay `proposed` while DDD/C4 are `provisional`.

## Blocked on evidence acquisition backlog

- **ADR-007 / EAB-2** — needs sponsor confirmation on whether a true air-gap is required.
  This is the single decision most capable of reopening the whole stack (ADR-001).
- **All `proposed` ADRs indirectly depend on EAB-3** (real HITL/context owners), which is
  what keeps DDD `provisional` and therefore keeps these from `accepted`.

## Carried forward from `c4/adr_candidates.md` but not yet an ADR

| Candidate | Why deferred |
|---|---|
| MCP tool authentication/authorization mechanism | Needs Stage 11 (MCP) input before a decision is meaningful |
| Redis cache topology + semantic-cache embedding model | Needs Stage 15 measurement first; deciding now would be guessing |
| Verify rules-vs-AI boundary against V2 graders | **Done this stage** — became ADR-003, and corrected the DDD model |
