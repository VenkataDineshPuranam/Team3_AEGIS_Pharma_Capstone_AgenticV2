# Project AEGIS-PHARMA — V3 Agentic AI: Spec-Driven Development Plan

## 0. What V3 Is

V3 evolves the V2 capstone (a document-and-rubric-driven FDE exercise with a static
inject-explorer `app/` and a completed Next.js reference `submission/app-advanced/`)
into an **agentic AI system**: a multi-agent, tool-using, governed application that
performs the same three governed pharma workflows (GxP batch-review evidence
reconciliation; pharmacovigilance intake/signal support; supply-shortage/cold-chain
option planning) via orchestrated agents instead of a single-shot Q&A app — while
preserving V2's non-negotiables: synthetic-only data, no terminal safety/release
decisions made by the system, full evidence provenance, and GxP/privacy boundaries.

**Runtime stack decision (binding, formalized in `docs/adr/ADR-0001-runtime-stack.md`):**
- **Orchestration:** LangGraph (stateful multi-agent graphs, checkpointing, HITL interrupts)
- **Observability/Evals:** LangSmith (tracing, eval datasets, regression, cost/latency dashboards), backed by OpenTelemetry
- **Caching:** Redis (semantic + exact-match response cache, tiered TTL by workflow risk)
- **Governance:** a policy/guardrail layer independent of any single agent (`docs/governance/`, `security/policies/`, enforced via `.claude/hooks/`)

## 1. Repository Pattern

This repo follows the `.claude`-based "AI-Assisted SDLC Repository" scaffold
(15 top-level sections): `.claude/`, `docs/`, `plans/`, `apps/`, `services/`,
`packages/`, `tests/`, `quality/`, `security/`, `infra/`, `deploy/`, `ops/`,
`evidence/`, `templates/`, `workshop/` — plus V2-derived carry-overs
(`prompts/`, `knowledge/`, `evaluation/`, `runbooks/`, `eval-ai-cache/`).
See `README.md` for the full folder map and `STRUCTURE_MANIFEST.json` for the
machine-readable tree.

## 2. Method: Spec-Driven Development (SDD)

**Process discovery and design come first; the app is built last.** Every stage
follows the same loop, mirroring V2's prompt-driven pipeline
(`prompts/01_discovery.md` … `13_solution_proposal.md`):

1. **Spec** — write the stage's spec doc (in `plans/active/`, then the stage's home folder) before any code/diagram.
2. **Review gate** — spec states what "provisional" vs "stable" means; downstream stages inherit the weaker status (same propagation rule as V2 prompts).
3. **Build** — implement only what the spec calls for.
4. **Verify** — DMAIC "Control" check: what test/metric/evidence proves this stage's exit criteria are met (logged under `evidence/`).
5. **Branch + PR** — each stage lives on its own git branch (see §4), merged to `main` only when exit criteria are met; the spec then moves `plans/active/` → `plans/completed/`.

### Lean + DMAIC applied at every stage
Each stage doc includes a DMAIC-Lean block:
- **Define** — problem/decision this stage resolves
- **Measure** — current-state baseline (metric, doc, or artefact reference)
- **Analyze** — root cause / options considered, incl. an AI-waste register entry (unused context, redundant calls, over-generation, un-graded output — per V2's DOWNTIME+AI-waste model)
- **Improve** — the decision/design taken
- **Control** — the check/eval/guardrail that prevents regression

## 3. Stage Sequence (Discovery → SCQA → DDD → C4 → ADR → SDD internals → ... → App last)

| # | Stage | Branch | Primary folder(s) | DMAIC focus |
|---|---|---|---|---|
| 00 | Foundation: repo scaffold + SDD charter | `stage-00-foundation` | root, `.claude/`, this file | Define |
| 01 | Process discovery & SCQA | `stage-01-discovery-scqa` | `docs/product/` | Define |
| 02 | Current state of the repo | `stage-02-current-state` | `docs/product/state/current/` | Measure |
| 03 | Interim state (transition architecture) | `stage-03-interim-state` | `docs/product/state/interim/` | Analyze/Improve |
| 04 | Final state (target agentic architecture) | `stage-04-final-state` | `docs/product/state/final/` | Improve |
| 05 | Graphical views (current/interim/final) | `stage-05-graphical` | `docs/architecture/graphical/` | Improve (visual control) |
| 06 | Domain-Driven Design | `stage-06-ddd` | `docs/architecture/ddd/`, `packages/domain/` | Analyze |
| 07 | C4 architecture | `stage-07-c4` | `docs/architecture/c4/` | Improve |
| 08 | ADRs | `stage-08-adr` | `docs/adr/` | Improve/Control |
| 09 | DMAIC/Lean consolidated workbook | `stage-09-dmaic-lean` | `docs/quality/dmaic-lean/` | Control |
| 10 | Agentic architecture (LangGraph multi-agent design) | `stage-10-agentic-architecture` | `docs/architecture/agentic/`, `packages/domain/` | Improve |
| 11 | MCP servers/tools | `stage-11-mcp` | `services/integration/`, `packages/contracts/`, `.claude/mcp.json` | Improve |
| 12 | Skills & Hooks | `stage-12-skills-hooks` | `.claude/skills/`, `.claude/hooks/` | Improve |
| 13 | Ontology, Knowledge Graph, Semantic Layer | `stage-13-ontology-kg` | `docs/architecture/ontology/`, `packages/domain/` | Analyze/Improve |
| 14 | Eval-AI-Cache (eval harness + response cache) | `stage-14-eval-ai-cache` | `eval-ai-cache/`, `quality/gates/`, `tests/` | Control |
| 15 | Performance tuning (Redis, cache, token economics) | `stage-15-performance-tuning` | `docs/quality/performance/`, `infra/`, `packages/observability/` | Control |
| 16 | Governance & Control (policy, guardrails, HITL) | `stage-16-governance-control` | `docs/governance/`, `security/policies/` | Control |
| 17 | Observability (LangSmith, OTel, dashboards) | `stage-17-observability` | `packages/observability/`, `ops/dashboards/` | Control |
| 18 | AI Security — threat modeling | `stage-18-ai-security` | `security/threat-models/`, `security/abuse-cases/` | Analyze/Control |
| 19 | Compliance (EU AI Act, ISO 42001) | `stage-19-compliance` | `docs/governance/compliance/`, `evidence/` | Control |
| 20 | Repo implementation — **app building (last)** | `stage-20-repo-implementation` | `apps/`, `services/`, `deploy/` | Improve |
| 21 | Documentation & final defense pack | `stage-21-documentation` | `workshop/`, `runbooks/`, root docs | Control |

Stages 01–09 mirror V2's document lifecycle (Discovery → SCQA → DDD → C4 → ADR → DMAIC);
10–19 are V3-specific agentic/governance/eval/security/compliance additions; **20 (app
build) is deliberately last** — no code is written until discovery, SCQA, DDD, C4, ADR,
and the agentic/governance/eval design are stable. 21 closes the loop with a defensible
submission, matching V2's `requirements/FINAL_DEFENCE.md` pattern.

## 4. Git Workflow

- `main` — always holds the latest merged, exit-criteria-met state.
- One branch per stage, named exactly as in the table above, created off `main`.
- Commit the stage's spec doc first (in `plans/active/`), then supporting artefacts, on that branch.
- Open for merge only when the spec's exit criteria are checked off; move spec to `plans/completed/` on merge.
- Branches are created empty/ready in this pass; content is authored stage-by-stage, in order.

## 5. Status Legend (used in `STAGES.md`)

`not started` → `spec drafted` → `in review` → `stable` (mirrors V2's provisional/stable propagation rule).
