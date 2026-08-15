# Project AEGIS-PHARMA — V2 Agentic AI: Spec-Driven Development Plan

## 0. What V2 Is

V2 evolves the V1 capstone (a document-and-rubric-driven FDE exercise with a static
inject-explorer `app/` and a completed Next.js reference `submission/app-advanced/`)
into an **agentic AI system**: a multi-agent, tool-using, governed application that
performs the same three governed pharma workflows (GxP batch-review evidence
reconciliation; pharmacovigilance intake/signal support; supply-shortage/cold-chain
option planning) via orchestrated agents instead of a single-shot Q&A app — while
preserving V1's non-negotiables: synthetic-only data, no terminal safety/release
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
`evidence/`, `templates/`, `workshop/` — plus V1-derived carry-overs
(`prompts/`, `knowledge/`, `evaluation/`, `runbooks/`, `eval-ai-cache/`).
See `README.md` for the full folder map and `STRUCTURE_MANIFEST.json` for the
machine-readable tree.

## 1b. Authoritative SDD reference

The SDD methodology this repo follows is defined by the course material at
`/Users/puranamdinesh/Documents/FDE-training/Day-27/1785208772944-Deck/`:
- `Spec-Driven-Development-Techademy.pdf` — the method deck
- `VisionScan-POS-SDD-Techademy.pdf` + `visionscan-pos-spec.md` — a worked example SDD

**Core principles (from the deck):**
- *"Layered specifications that reduce ambiguity one stage at a time."*
- The anti-pattern is the single enormous spec: business context buried beside definitions,
  nobody reads it end to end, changing one thing forces rewriting the whole file, retrieval
  pulls in irrelevant pages, and review becomes impossible so review stops happening.
- What works instead: **small documents, each with one job**; ambiguity removed
  progressively; version-controlled alongside the code; retrievable in isolation so the
  agent reads only what it needs; reviewable in one sitting by one person.
- *"The question is never PRD or SRS — it is which question this particular file is
  answering."* Each layer takes the output of the one above and makes **one more category of
  decision explicit**, so that by the time you reach implementation tasks there is nothing
  left for the agent to guess, and nothing was written twice.
- *"Value to an AI agent rises as ambiguity falls. That is the whole mechanism."*

**Layer → question → this repo's stage:**

| Layer | Question it answers | Stage here |
|---|---|---|
| PRD | What problem are we solving? | 01 (Discovery/SCQA) |
| SRS | What should the system do? | 02–04 (DDD/C4/ADR) |
| High SRS | Exactly how should it behave? | Technical design (`prompts/08_technical_design.md`) |
| Design / Architecture | How will we build it? | 10–19 (agentic, MCP, governance, eval, security) |
| Implementation tasks | What code needs writing? | 20 (app build, last) |

`visionscan-pos-spec.md` is the structural template for the technical-design layer
(FR-NNN with Input/Processing/Output, measurable NFR table, BR-NNN business rules, AC-NNN
acceptance criteria, standard error envelope, and the Appendix A traceability matrix with
its explicit "gaps surfaced" section). `prompts/08_technical_design.md` already encodes this
format — it is the layer where exact behavior gets pinned down.

## 2. Method: Spec-Driven Development (SDD)

**Process discovery and design come first; the app is built last.** Every stage
follows the same loop, mirroring V1's prompt-driven pipeline
(`prompts/01_discovery.md` … `13_solution_proposal.md`):

1. **Spec** — write the stage's spec doc (in `plans/active/`, then the stage's home folder) before any code/diagram.
2. **Review gate** — spec states what "provisional" vs "stable" means; downstream stages inherit the weaker status (same propagation rule as V1 prompts).
3. **Build** — implement only what the spec calls for.
4. **Verify** — DMAIC "Control" check: what test/metric/evidence proves this stage's exit criteria are met (logged under `evidence/`).
5. **Branch + PR** — each stage lives on its own git branch (see §4), merged to `main` only when exit criteria are met; the spec then moves `plans/active/` → `plans/completed/`.

### Lean + DMAIC applied at every stage
Each stage doc includes a DMAIC-Lean block:
- **Define** — problem/decision this stage resolves
- **Measure** — current-state baseline (metric, doc, or artefact reference)
- **Analyze** — root cause / options considered, incl. an AI-waste register entry (unused context, redundant calls, over-generation, un-graded output — per V1's DOWNTIME+AI-waste model)
- **Improve** — the decision/design taken
- **Control** — the check/eval/guardrail that prevents regression

## 3. Stage Sequence (Discovery → SCQA → DDD → C4 → ADR → SDD internals → ... → App last)

| # | Stage | Driving prompt | Branch | Primary folder(s) | DMAIC focus |
|---|---|---|---|---|---|
| 00 | Foundation: repo scaffold + SDD charter | — | `stage-00-foundation` | root, `.claude/`, this file | Define |
| 01 | Process discovery & SCQA | `prompts/01_discovery.md`, `02_scqa_minto.md` | `stage-01-discovery-scqa` | `docs/product/` | Define |
| 02 | Domain-Driven Design | `prompts/04_ddd.md` | `stage-02-ddd` | `docs/architecture/ddd/`, `packages/domain/` | Analyze |
| 03 | C4 architecture | `prompts/06_c4.md` | `stage-03-c4` | `docs/architecture/c4/` | Improve |
| 04 | ADRs | `prompts/07_adrs.md` | `stage-04-adr` | `docs/adr/` | Improve/Control |
| 05 | Current state of the repo | `prompts/01_discovery.md` (applied to this repo) | `stage-05-current-state` | `docs/product/state/current/` | Measure |
| 06 | Interim state (transition architecture) | `prompts/03_prd_vision.md` | `stage-06-interim-state` | `docs/product/state/interim/` | Analyze/Improve |
| 07 | Final state (target agentic architecture) | `prompts/03_prd_vision.md` | `stage-07-final-state` | `docs/product/state/final/` | Improve |
| 08 | Graphical views (current/interim/final) | `prompts/06_c4.md` (visual views) | `stage-08-graphical` | `docs/architecture/graphical/` | Improve (visual control) |
| 09 | DMAIC/Lean consolidated workbook | `prompts/09_lean_dmaic.md` | `stage-09-dmaic-lean` | `docs/quality/dmaic-lean/` | Control |
| 10 | Agentic architecture (LangGraph multi-agent design) | `prompts/14_agentic_architecture.md` | `stage-10-agentic-architecture` | `docs/architecture/agentic/`, `packages/domain/` | Improve |
| 11 | MCP servers/tools | `prompts/15_mcp.md` | `stage-11-mcp` | `services/integration/`, `packages/contracts/`, `.claude/mcp.json` | Improve |
| 12 | Skills & Hooks | `prompts/16_skills_hooks.md` | `stage-12-skills-hooks` | `.claude/skills/`, `.claude/hooks/` | Improve |
| 13 | Ontology, Knowledge Graph, Semantic Layer | `prompts/17_ontology_knowledge_graph.md` | `stage-13-ontology-kg` | `docs/architecture/ontology/`, `packages/domain/` | Analyze/Improve |
| 14 | Eval-AI-Cache (eval harness + response cache) | `prompts/18_eval_ai_cache.md` | `stage-14-eval-ai-cache` | `eval-ai-cache/`, `quality/gates/`, `tests/` | Control |
| 15 | Performance tuning (Redis, cache, token economics) | `prompts/19_performance_tuning.md` | `stage-15-performance-tuning` | `docs/quality/performance/`, `infra/`, `packages/observability/` | Control |
| 16 | Governance & Control (policy, guardrails, HITL) | `prompts/20_governance_control.md` | `stage-16-governance-control` | `docs/governance/`, `security/policies/` | Control |
| 17 | Observability (LangSmith, OTel, dashboards) | `prompts/21_observability.md` | `stage-17-observability` | `packages/observability/`, `ops/dashboards/` | Control |
| 18 | AI Security — threat modeling | `prompts/22_ai_security_threat_modeling.md` | `stage-18-ai-security` | `security/threat-models/`, `security/abuse-cases/` | Analyze/Control |
| 19 | Compliance (EU AI Act, ISO 42001) | `prompts/23_compliance.md` | `stage-19-compliance` | `docs/governance/compliance/`, `evidence/` | Control |
| 20 | Repo implementation — **app building (last)** | `prompts/11_product_and_build.md` | `stage-20-repo-implementation` | `apps/`, `services/`, `deploy/` | Improve |
| 21 | Documentation & final defense pack | `prompts/13_solution_proposal.md`, `12_assurance.md` | `stage-21-documentation` | `workshop/`, `runbooks/`, root docs | Control |

**Sequencing note (revised from the original draft):** Stages 01–04 follow the user's
explicit instruction verbatim — discovery → SCQA → DDD → C4 → ADR — with no state-assessment
stages inserted in between. Stages 05–08 (current/interim/final state, graphical views) were
originally placed *before* DDD but were moved to **after** ADR: they now synthesize and
visualize the domain/architecture model once it is stable, rather than speculating about
state before the domain model exists. Stage 09 (DMAIC/Lean) consolidates everything from
01–08 before Stage 10 begins the V2-specific agentic/governance/eval/security/compliance
additions (10–19). **Stage 20 (app build) remains deliberately last** — no code is written
until discovery, SCQA, DDD, C4, ADR, and the agentic/governance/eval design are stable.
Stage 21 closes the loop with a defensible submission, matching V1's
`requirements/FINAL_DEFENCE.md` pattern.

## 4. Git Workflow

- `main` — always holds the latest merged, exit-criteria-met state.
- One branch per stage, named exactly as in the table above, created off `main`.
- Commit the stage's spec doc first (in `plans/active/`), then supporting artefacts, on that branch.
- Open for merge only when the spec's exit criteria are checked off; move spec to `plans/completed/` on merge.
- Branches are created empty/ready in this pass; content is authored stage-by-stage, in order.

## 5. Status Legend (used in `STAGES.md`)

`not started` → `spec drafted` → `in review` → `stable` (mirrors V1's provisional/stable propagation rule).
