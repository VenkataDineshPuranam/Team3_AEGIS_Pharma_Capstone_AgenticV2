# C4 Level 2 — Containers — Stage 03

**Artifact status:** `provisional` (inherits from DDD/Context)

Each container maps to a folder in this repo's Stage 20 build target (`apps/`, `services/`,
`packages/`) — the mapping is listed so the eventual implementation has an unambiguous home.

| Container | Type | Owns/hosts | Maps to bounded context (Stage 02) | Repo folder (Stage 20) |
|---|---|---|---|---|
| **Web/Admin App** | UI (SPA) | Human-facing views: workflow input, decision-support output, HITL approval queue | Presentation layer over all three core contexts | `apps/web`, `apps/admin` |
| **Orchestrator API** | Service | LangGraph graph execution: hosts the Batch-Review, PV-Intake, Supply-Planning, and Critic/Verifier agent nodes as graph nodes; owns the shared state schema and HITL interrupt mechanism | Hosts Batch Review, PV Intake, Supply Planning, and (the Critic/Verifier part of) Governance & Oversight at runtime | `services/api` |
| **Agent Workers** | Service | Long-running/async agent tasks (e.g. a Supply Planning option search that exceeds a single request's latency budget) | Same as Orchestrator API, async variant | `services/worker` |
| **MCP Tool Servers** | Service (one or more) | Evidence Retrieval tool, Reconciliation tool, Duplicate-Check tool, Option-Generation tool — each exposing exactly the read/write capability its owning domain agent needs, per DDD's tool-capability constraint | Evidence & Provenance (retrieval); per-core-context (reconciliation/duplicate-check/option-generation) | `services/integration` |
| **Evidence & Provenance Store / Semantic Layer** | Data + service | The shared evidence-authority model (`EvidenceItem` value objects); backing for the ontology/knowledge-graph semantic layer (Stage 13 dependency) | Evidence & Provenance | `packages/domain` + Stage 13 output |
| **Governance/Policy Engine** | Service (cross-cutting) | Prohibited-action guard, HITL routing rules, policy register — implements the open-host-service relationship from `context_map.md` | Governance & Oversight | `docs/governance/` (design) → enforced via `.claude/hooks/` and a runtime policy-check component |
| **Redis Cache** | Data store | Semantic + exact-match response cache, tiered TTL by workflow risk (Stage 15) | Generic/technical | `infra/` |
| **LangSmith** | External, hosted | Tracing, eval regression, cost/latency dashboards | Generic/technical (Observability) | N/A — external service, integrated via `packages/observability` |
| **Audit/Evidence Log Store** | Data store | Durable `AgentRun` records (DDD §7) — **kept distinct from LangSmith traces** because compliance retention requirements (Stage 19) may differ from trace/debugging retention, and this store must survive even if the hosted LangSmith integration is degraded (see Boundary & Degraded Mode) | Governance & Oversight (audit) | `evidence/` (design), real store TBD at Stage 20 |

## Why a separate Governance/Policy Engine container (not embedded in Orchestrator API)

This is listed here as a **decision candidate for Stage 04 (ADR)**, not settled: the
DDD context map already commits to Governance being an *open-host service* relationship
(not a shared kernel), which argues for a separate container so the policy contract can be
versioned and deployed independently of the orchestrator. The counter-argument (simpler
ops, fewer network hops) is real and should be weighed explicitly in an ADR — see
`adr_candidates.md`.

## Why a separate Audit/Evidence Log Store (not just LangSmith)

Also a **decision candidate**: LangSmith is a hosted, external, non-negotiably-outside-our-
control service; compliance evidence (Stage 19, EU AI Act/ISO 42001) likely needs guaranteed
retention and possibly on-premises storage that a hosted trace tool may not contractually
provide. Keeping these separate avoids coupling the compliance-evidence requirement to a
third-party SLA.
