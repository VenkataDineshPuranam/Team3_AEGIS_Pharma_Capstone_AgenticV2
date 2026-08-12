# Project AEGIS-PHARMA — V3: Agentic AI

V3 evolves the [V2 capstone](./Project_AEGIS_Pharma_AI_FDE_Capstone_Workshop_Ready_v2_claude/)
from a document-driven FDE exercise into a governed, observable, multi-agent AI system
covering the same three pharma workflows (GxP batch review, pharmacovigilance intake,
supply-shortage planning), built with **LangGraph** (orchestration) and **LangSmith**
(observability/evals), Redis caching, and explicit governance, security, and compliance layers.

Process discovery, SCQA, DDD, C4, and ADR come first — **the app is built last**
(Stage 20 of 21). See:
- [`SPEC_DRIVEN_DEVELOPMENT.md`](./SPEC_DRIVEN_DEVELOPMENT.md) — the method, full stage list, and git workflow
- [`STAGES.md`](./STAGES.md) — live status tracker for every stage/branch
- [`STRUCTURE_MANIFEST.json`](./STRUCTURE_MANIFEST.json) — machine-readable folder tree

## Repository Pattern

This repo follows a `.claude`-based "AI-Assisted SDLC Repository" scaffold: Claude-native,
platform-neutral, offline-compatible, workshop-deployable.

| Section | Purpose |
|---|---|
| `.claude/` | rules, agents, skills, hooks, `mcp.json`, `settings.json` |
| `docs/` | product (SCQA, current/interim/final state), architecture (DDD, C4, agentic design, ontology, graphical), adr, engineering, quality (DMAIC/Lean, evals, performance), security, operations, governance (incl. compliance) |
| `plans/` | active / completed / superseded stage specs |
| `apps/` | web, admin — participant/operator UI |
| `services/` | api (LangGraph orchestrator), worker (agent workers), integration (MCP servers) |
| `packages/` | domain (DDD + ontology bindings), contracts (API/tool/MCP schemas), config, observability (LangSmith/OTel), test-support |
| `tests/` | unit, integration, contract, e2e, performance, security, resilience, fixtures/synthetic |
| `quality/` | gates, coverage, mutation, static-analysis |
| `security/` | policies, threat-models, abuse-cases, exceptions, sbom, secrets |
| `infra/` | modules, environments (local/dev/staging/production), policies |
| `deploy/` | containers, manifests, migrations, rollback |
| `ops/` | dashboards, alerts, runbooks, slo, incident, chaos |
| `evidence/` | requirements, architecture, tests, security, quality-gates, releases, deployments, operations, incidents, ai-assisted-changes |
| `templates/` | change-plan, requirement, adr, test-plan, threat-model, privacy-review, runbook, release-readiness, incident-record, ai-change-record |
| `workshop/` | scenarios, labs, checkpoints, assessments, participant-output |

**Carried forward / extended from V2:** `prompts/` (numbered lifecycle prompts),
`knowledge/` (domain knowledge base), `evaluation/` (public fixtures/contracts),
`runbooks/` (participant runbooks), `eval-ai-cache/` (seeded brownfield evals +
Redis + OpenTelemetry runbook library — the direct source material for Stage 14/15).

## Non-negotiables (inherited from V2)
- Synthetic data only; no real PHI/PII.
- No agent makes a terminal safety/release/allocation decision — decision **support** only.
- Every claim traceable to evidence (provenance required).
- GxP, privacy, and security boundaries are enforced by the governance layer
  (`docs/governance/`, `security/`, `.claude/hooks/`), not by agent prompting alone.
