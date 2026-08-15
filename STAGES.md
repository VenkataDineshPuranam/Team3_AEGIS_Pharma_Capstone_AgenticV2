# Stage Tracker

Status legend: `not started` · `spec drafted` · `in review` · `stable`

| # | Stage | Branch | Status |
|---|---|---|---|
| 00 | Foundation & SDD charter | stage-00-foundation | spec drafted |
| 01 | Process discovery & SCQA | stage-01-discovery-scqa | stable |
| 02 | Domain-Driven Design | stage-02-ddd | **stable** (artifact upgraded to stable on EAB-3 closure) |
| 03 | C4 architecture | stage-03-c4 | **stable** (artifact upgraded on EAB-2 closure) |
| 04 | ADRs | stage-04-adr | stable (**8 ADRs, all accepted; review = pass**) |
| 05 | Current state of the repo | stage-05-current-state | stable (re-measured post-ADR) |
| 06 | Interim state | stage-06-interim-state | stable |
| 07 | Final state | stage-07-final-state | stable |
| 08 | Graphical views | stage-08-graphical | stable |
| 09 | DMAIC/Lean workbook | stage-09-dmaic-lean | **stable** (9 lenses reconciled; structural gate = `cleared`) |
| 10 | Agentic architecture (LangGraph) | stage-10-agentic-architecture | **stable** for `batch_review`; `provisional` for PV/Supply graphs (RR-2) |
| 11 | MCP servers/tools | stage-11-mcp | **stable** for batch tools (evidence.retrieve, batch.reconcile); `provisional` for PV/Supply tools |
| 12 | Skills & Hooks | stage-12-skills-hooks | **stable** for `batch_review` bindings; `provisional` for PV/Supply |
| 13 | Ontology / Knowledge Graph | stage-13-ontology-kg | **stable** for Batch Review/Evidence classes; `provisional` for PV/Supply — NAB-3 half-resolved (`knowledge/` copied, hash-verified) |
| 14 | Eval-AI-Cache | stage-14-eval-ai-cache | **stable** — 63 scenarios, 0 FAIL/ERROR (design-pass run against synthetic fixtures; measured pass after 20a) |
| 15 | Performance tuning (Redis/token economics) | stage-15-performance-tuning | **stable** — cost/latency are models awaiting U1/U2 from 20a; denial-of-wallet ceiling is enforced and tested (7/7) |
| 16 | Governance & Control | stage-16-governance-control | not started |
| 17 | Observability (LangSmith) | stage-17-observability | not started |
| 18 | AI Security threat modeling | stage-18-ai-security | not started |
| 19 | Compliance (EU AI Act, ISO 42001) | stage-19-compliance | not started |
| 20 | **Repo implementation (app build — last)** | stage-20-repo-implementation | not started |
| 21 | Documentation & final defense pack | stage-21-documentation | not started |
| 23 | Record Assistant, PI/PG, AI-BOM, CI/CD | final_app | **stable** — chatbot over run records (deterministic facts + guarded model prose), prompt-injection input/output guard, CycloneDX AI-BOM with prompt-drift detection, GitHub Actions CI + Azure Container Apps CD |

See `SPEC_DRIVEN_DEVELOPMENT.md` for the full method and DMAIC-Lean requirements per stage.

**Delivery sequence for stages 10–21:** [`plans/active/EXECUTION_PLAN.md`](plans/active/EXECUTION_PLAN.md)
— waves, dependencies, the 20a/20b split around **Gate M**, and the decisions that need a human.
