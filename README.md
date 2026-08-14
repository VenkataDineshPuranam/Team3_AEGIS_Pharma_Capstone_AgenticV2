# Project AEGIS-PHARMA — V3: Agentic AI

V3 evolves the [V2 capstone](./Project_AEGIS_Pharma_AI_FDE_Capstone_Workshop_Ready_v2_claude/)
from a document-driven FDE exercise into a governed, observable, multi-agent AI system —
the **AEGIS Control Center** — covering six pharma workflows (GxP batch review,
pharmacovigilance intake, supply-shortage planning, preclinical research review, clinical
trial integrity, regulatory submission completeness), built with **LangGraph**
(orchestration), Redis caching, real login/authorization, and explicit governance,
security, and compliance layers enforced server-side, not just documented.

Process discovery, SCQA, DDD, C4, and ADR came first, then the app (Stage 20), then a
real login layer and full gap closure across all 84 V2 tabletop-exercise scenarios
(Stage 21–22). See:
- [`SPEC_DRIVEN_DEVELOPMENT.md`](./SPEC_DRIVEN_DEVELOPMENT.md) — the method, full stage list, and git workflow
- [`STAGES.md`](./STAGES.md) — live status tracker for every stage/branch
- [`STRUCTURE_MANIFEST.json`](./STRUCTURE_MANIFEST.json) — machine-readable folder tree
- [`PROJECT_SUMMARY.md`](./PROJECT_SUMMARY.md) — detailed per-stage summary of everything built

## The application

A real FastAPI orchestrator (`services/api/`) wrapping six governed LangGraph workflows,
and a Next.js operator UI (`apps/web/`, the **AEGIS Control Center**).

**Run it locally:**
```sh
# Backend — from the repo root
python3 -m services.integration.seed_users   # one-time: seeds the 10 demo accounts
uvicorn services.api.main:app --port 8000

# Frontend — from apps/web/
npm install
npm run build && npm start   # or `npm run dev` for hot reload
```
Open `http://localhost:3000` — every page except `/login` requires a signed-in session.
Demo credentials for all ten roles are in
[`docs/governance/demo_login_credentials.md`](./docs/governance/demo_login_credentials.md)
(synthetic accounts only, no real people).

**Login and authorization** (Stage 22): `services/integration/user_store.py` is a real,
credential-backed login — salted PBKDF2-hashed passwords, server-side sessions with an
8-hour expiry, no client-supplied identity ever trusted. Every workflow decision
(`POST /api/runs/{run_id}/decide`) is authorized server-side against the signed-in role
before it reaches any graph — a role not eligible to approve a given workflow gets a 403,
not a UI-only restriction. See the credentials doc above for the full role/permission table.

**HITL severity/timer** (Stage 22): every pending decision shows a live 1–4 severity
badge (grey → amber → purple → red) in the Decision Queue and on the Decision Detail
page header, computed fresh on every poll from `services/integration/hitl_timer.py`
against the per-workflow ladder durations `docs/governance/hitl_control_model.md` §7
specifies (Batch Review/Supply Planning 8h/16h/24h, PV Intake's deliberately shorter
4h/8h/24h). **Display only** — reaching severity 4 does not widen who can approve a run;
see §8 of that document for exactly what this does and does not close (no live scheduler,
no notifications). A dev-only endpoint for exercising all four tiers without waiting real
hours is documented there too, off by default.

**Explore the architecture:** [`docs/architecture/graphical/architecture_explorer.html`](./docs/architecture/graphical/architecture_explorer.html)
is a self-contained, interactive diagram of the actual implemented system — every
frontend page, API endpoint, the six workflow graphs' shared spine, the tool layer, and
the stores — with a Flows panel that highlights real end-to-end paths (login, submitting
a run, approving a decision, a prohibited-action guard blocking a draft, dual-approval,
and more). The same data is available as machine-readable JSON at
[`architecture_graph.json`](./docs/architecture/graphical/architecture_graph.json).

**Coverage:** every one of the V2 predecessor's 84 tabletop-exercise "inject" scenarios
is mapped to a real, citable V3 artifact (test, fixture, structural guard, or governance
document) — see the in-app Evaluation & Security dashboard (`/coverage`) or
`evidence/quality-gates/inject_coverage_v2_to_v3.json`.

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
