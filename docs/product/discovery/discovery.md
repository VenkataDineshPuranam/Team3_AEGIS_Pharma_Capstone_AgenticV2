# Evidence Register — Stage 01 (Discovery)

**Executes:** `prompts/01_discovery.md`
**Scope:** Discovery for the V2 agentic evolution of Project AEGIS-PHARMA (the V1 capstone).
**Repository under evaluation:** this repo (V2) and its immediate predecessor, V1, at
`../Project_AEGIS_Pharma_AI_FDE_Capstone_Workshop_Ready_v2_claude/` (referenced read-only,
excluded from V2 git history per `.gitignore`).

---

## 1. Repository and source-system map

| System | What it is | Path (relative to V1 root unless noted) | Status |
|---|---|---|---|
| V1 capstone package | Synthetic pharma FDE case: 84 injects across 13 dimensions, 143 CSV datasets, 32 knowledge/policy docs, deliberately defective starter code, 30-artefact/180-point rubric | repo root | Fact — inspected directly |
| Inject dataset | Traceability spine — `injects.json` + 143 CSVs | `data/` (143 CSV files confirmed by direct count) | Fact |
| Knowledge base | Pharma/GxP/PV/AI-governance policy documents | `knowledge/` (32 files confirmed by direct count) | Fact |
| Case pack | Integrated business case, regulatory boundary pack, source-system fact pack, stakeholder pack | `case/INTEGRATED_CASE.md`, `case/REGULATORY_BOUNDARY_PACK.md`, `case/SOURCE_SYSTEM_FACT_PACK.md`, `case/STAKEHOLDER_PACK.md` | Fact — file listing confirmed |
| Lifecycle prompts | 13 numbered prompts, Discovery→Solution Proposal | `prompts/01_discovery.md` … `13_solution_proposal.md`, `PROMPT_LIBRARY.md` | Fact — read in full; ported into this repo's `prompts/` with V2 adaptations (see `prompts/ADAPTATION_NOTES.md`) |
| Artefact templates | 30 numbered blank templates | `templates/` | Fact (from prior repo exploration; not re-verified file-by-file this pass) |
| Immutable challenge app | Static vanilla-JS inject explorer, no build step | `app/index.html`, `app.js`, `data.js`, `styles.css` | Fact — this is a browsing UI over the injects, **not** the solution app |
| Reference solution (prior completed run) | Next.js 16/React 19/TypeScript app implementing workflows A–E with guardrails, evaluation views | `submission/app-advanced/` | Fact (from prior exploration) — exists as a **completed prior participant run**, not a shipped product spec |
| Eval plan (challenge-supplied, immutable) | 12 required test-suite categories, 15 public fixtures, JSON response contracts, mandatory release gates | `evaluation/EVALUATION_PLAN.md`, `evaluation/public_fixtures/PUB-01..15.json`, `evaluation/PUBLIC_FIXTURE_INDEX.csv`, `evaluation/contracts/*.schema.json` (`batch_response`, `pv_response`, `supply_response`, `evidence_item`), `evaluation/contract_samples/*.json` | Fact — directory listing confirmed directly this pass |
| Eval harness (prior completed run's implementation) | Deterministic grader-based Python harness — not a third-party eval library | `submission/evaluation/runner.py`, `submission/evaluation/graders/{authority,evidence,latency_cost,prohibited_action,schema,security,subgroup,temporal_unit,trajectory}_grader.py`, `submission/evaluation/policies/release_gates.py`, `submission/evaluation/datasets/S01–S14_*.json`, `submission/evaluation/reports/{scorecard.csv,summary.json,final_evaluation_report.md,failed_cases.json}` | Fact — directory listing confirmed directly this pass |
| Requirements/rubric | Artefact expectations, 180-point scoring model, final defense format, submission evidence standard | `requirements/ARTEFACT_EXPECTATIONS.md`, `ASSESSMENT_RUBRIC.csv`, `FINAL_DEFENCE.md`, `SCORING_MODEL.md`, `SUBMISSION_EVIDENCE_STANDARD.md` | Fact — directory listing confirmed directly this pass |
| Eval-AI-cache reference library | 24-file "brownfield evals" runbook + Redis caching runbook + OpenTelemetry runbook, seeded into V2 at repo creation | `eval-ai-cache/AI_FDE_Brownfield_Evals_Cursor_Runbook/00_Cursor_Eval_Rule.md` … `23_Final_AI_FDE_Evaluation_Report.md`, `eval-ai-cache/*.docx`, `eval-ai-cache/*.zip` | Fact — this material was supplied by the user directly into V2's `eval-ai-cache/` folder (not derived from V1 proper); it is the primary source for Stage 14/15/17 |
| `.deepeval` | Present at V1 top level, essentially empty/config-only | `.deepeval/` | Fact (from prior exploration) — DeepEval was scaffolded as an option but not substantively used in V1 |

**Sources of truth for this Discovery pass:**
1. Direct filesystem inspection of V1 (this session, commands above).
2. A prior in-session Explore-agent pass over V1 (README.md, START_HERE.md, REPOSITORY_OVERVIEW.md, MANIFEST.md, CLAUDE.md, `prompts/`, `app/`, `knowledge/`, `sources/`, `source_documents/`, `data/`, `evaluation/`, `.deepeval/`, `eval-ai-cache/`, `templates/`, `case/`, `runbooks/`, `submission/`, `requirements/`) — summarized in this conversation; **not independently re-verified line-by-line in this Discovery pass**, so treat as **derivation**, not raw fact, where not directly re-confirmed above.
3. The user's explicit requirements stated directly in this conversation (see §5).
4. A user-supplied reference image (`IMG_2543.jpg`) specifying a `.cursor`/`.claude`-based "AI-Assisted SDLC Repository" folder pattern, which this repo's structure now follows exactly (`README.md`, `STRUCTURE_MANIFEST.json`).

---

## 2. Entities, identifiers, and timestamp semantics

Carried from V1 (not re-derived — V1's domain entities are the domain V2 operates on):

| Entity class | Identifier scheme | Timestamp semantics | Status |
|---|---|---|---|
| Inject | Numbered inject ID, dimension-tagged (84 injects / 13 dimensions per V1 README) | Not independently re-verified this pass | Derivation (from prior exploration) |
| Batch record (GxP workflow) | Batch/lot identifiers per `case/SOURCE_SYSTEM_FACT_PACK.md` | Event-time vs report-time distinction is a named V1 concern (per `submission/evaluation/graders/temporal_unit_grader.py`'s existence) | Derivation — grader's existence is fact; its exact rules not read this pass |
| PV case (pharmacovigilance workflow) | Case identifiers; duplicate-detection and clock semantics are explicit eval categories (`submission/evaluation/datasets/S07_pv_duplicate_clock_terminology_listednes.json`) | PV "clock" (onset/reporting clock) is explicitly a graded dimension | Fact — filename confirms this is a tested concern, exact rules not read |
| Supply/shortage option | Not independently inspected this pass | Unknown | **Missing** — needs acquisition (see backlog) |

**V2-specific new entities** (do not yet exist in V1, introduced by the agentic redesign — these are **assumptions/derivations pending Stage 06 DDD**, not facts):
- Agent (planner, retriever, per-workflow domain agents, critic/verifier) — assumption, to be formalized in Stage 06/10.
- Agent run / trace (LangSmith run ID) — assumption.
- Cache entry (Redis key, TTL, risk tier) — assumption.
- MCP tool call (tool name, authorization scope) — assumption.

---

## 3. Evidence ownership and authority

| Data class | Source of truth (V1) | Carries to V2? |
|---|---|---|
| Regulatory/compliance boundaries | `case/REGULATORY_BOUNDARY_PACK.md` | Yes — unchanged; V2 adds EU AI Act / ISO 42001 on top (new, V2-only obligation, see Stage 19) |
| Business case / stakeholder needs | `case/INTEGRATED_CASE.md`, `case/STAKEHOLDER_PACK.md` | Yes — unchanged |
| Source-system facts | `case/SOURCE_SYSTEM_FACT_PACK.md` | Yes — unchanged |
| Evaluation requirements (12 categories, release gates) | `evaluation/EVALUATION_PLAN.md` | Yes — inherited as the floor; V2 extends with agent-specific categories (Stage 14, `prompts/18_eval_ai_cache.md`) |
| Submission/scoring rubric | `requirements/ASSESSMENT_RUBRIC.csv`, `SCORING_MODEL.md` | **Unknown** — V1's rubric was written for a document-and-single-shot-app deliverable; whether/how it applies to a multi-agent V2 deliverable is an open question (see backlog item EAB-1) |
| Repo/folder structure convention | User-supplied reference image (`IMG_2543.jpg`) | Yes — V2's structure is authoritative per this image, already implemented (`README.md`, `STRUCTURE_MANIFEST.json`) |
| SDD stage sequence & runtime stack (LangGraph/LangSmith/Redis) | User's explicit instructions in this conversation | Yes — recorded in `SPEC_DRIVEN_DEVELOPMENT.md` §0; **not yet ratified as an ADR** (planned Stage 08, ADR-0001) |

---

## 4. Material inconsistencies, gaps, and conflicts

1. **No V2-specific case pack exists yet.** V1's `case/` pack was written for a single-shot decision-support app, not a multi-agent system. It does not address agent authority boundaries, inter-agent handoff, or cache/observability concerns. This is a **gap**, not a conflict — carried into the backlog.
2. **Rubric applicability unknown.** V1's `requirements/ASSESSMENT_RUBRIC.csv` and `SCORING_MODEL.md` were scoped to V1's 30 numbered artefacts. V2 has 21 stages and 23 prompts, a superset. Whether V2 should produce a new rubric or extend V1's is unresolved.
3. **No conflict yet observed between the reference-image repo pattern and V1's document lifecycle** — they compose cleanly (confirmed by the folder mapping in `SPEC_DRIVEN_DEVELOPMENT.md` §3), but this has not been stress-tested against real stage content yet (only Stage 00 scaffolding exists).

---

## 5. Stakeholder decisions and decision horizons

| Decision | Status | Source |
|---|---|---|
| V2 domain = same three governed pharma workflows as V1 (GxP batch review, PV intake/signal support, supply-shortage/cold-chain planning), re-architected as multi-agent | **Decided** | User, this conversation |
| Runtime stack: LangGraph (orchestration), LangSmith (observability/evals), Redis (caching) | **Decided** | User, this conversation ("we need multi agents, governance, control and observability as well, use lang graph, lang smith etc") |
| Repo pattern: `.claude`-based (not `.cursor`) 15-section AI-Assisted SDLC scaffold | **Decided** | User, this conversation + `IMG_2543.jpg` |
| Sequencing: process discovery → SCQA → DDD → C4 → ADR → SDD-internal stages → app build last | **Decided** | User, this conversation ("app building is last first we need Process discovery scqa, ddd, c4, adr, sdd then move to the app building") |
| Method: Spec-Driven Development, one branch per stage | **Decided** | User, original request |
| Whether V2 targets the same workshop/rubric audience as V1, or a different audience (e.g. production engineering team) | **Pending** | Not yet asked — affects how formal/rubric-bound later artefacts need to be |
| Whether V2 must remain synthetic-data-only like V1 | **Assumed carried forward** (stated as a non-negotiable in `README.md`), not yet explicitly re-confirmed by user for V2 | Assumption |

---

## 6. Constraints register

| Constraint | Type | Source | Carries to V2? |
|---|---|---|---|
| Synthetic data only, no real PHI/PII | Regulatory/privacy | V1 `README.md`, `LICENSE_AND_USE.md` | Assumed yes (not yet re-confirmed by user for V2) |
| No agent may make a terminal safety/release/allocation decision | Regulatory/safety (GxP) | V1 case pack + rubric | Yes — carried explicitly into V2 `README.md` non-negotiables |
| Offline-capable / no cloud dependency assumed | Technical | V1 `README.md`, `run_capstone.*` | **Unknown for V2** — LangGraph/LangSmith/Redis introduce real infrastructure dependencies V1 didn't have; V1's "offline-compatible" framing may not transfer as-is. Flagged as open question, not yet resolved. |
| EU AI Act / ISO 42001 compliance | Regulatory (new) | User's explicit request | Yes — new obligation, not present in V1 at all |
| Multi-agent governance/control/observability | Technical/operational (new) | User's explicit request | Yes — new obligation |

---

## 7. Current-state workflow sketch (as observed, not redesigned)

V1's as-observed workflow (from case pack + prior exploration, **not independently re-verified line-by-line this pass — mark as derivation**):

1. Participant receives the V1 package (injects, data, knowledge, case pack).
2. Participant runs the discovery→SCQA→PRD→DDD→features→C4→ADR→tech-design→DMAIC→tasks→build→assurance→proposal prompt pipeline (`prompts/01`–`13`), producing artefacts under `submission/artefacts/`.
3. Participant builds a decision-support app (`submission/app` and/or `submission/app-advanced`) implementing the three governed workflows as single-shot request/response flows (evidenced by `submission/app-advanced`'s route structure: `workflow-a|b|c|d|e/`, `injects/`, `evaluation/`, `tour/` — no agent-orchestration code present in this route list).
4. Participant runs the eval harness (`submission/evaluation/runner.py`) against the 12 required categories and produces a scorecard.
5. Participant prepares a final defense per `requirements/FINAL_DEFENCE.md`.

**V2's workflow is not yet designed** — that is explicitly out of scope for Discovery (see Constraints below) and is the subject of Stages 02–04 (current/interim/final state) and Stage 10 (agentic architecture).

---

## 8. Fact / derivation / assumption / question register

| # | Item | Class | Note |
|---|---|---|---|
| 1 | V1 has 143 CSV files under `data/` | **Fact** | Direct count, this session |
| 2 | V1 has 32 files under `knowledge/` | **Fact** | Direct count, this session |
| 3 | V1's eval harness is a from-scratch deterministic grader system, not a third-party library | **Fact** | Directory listing confirms grader files; `.deepeval/` confirmed near-empty by prior exploration |
| 4 | V1's `submission/app-advanced` has no multi-agent orchestration code | **Derivation** | Inferred from route list; component-level code not read this pass |
| 5 | V1 has 84 injects across 13 dimensions | **Derivation** (from prior exploration summary; not re-verified against `data/injects.json` directly this pass) | |
| 6 | V2 must use LangGraph, LangSmith, Redis | **Fact** (as a stated decision, not a technical necessity) | User's explicit instruction |
| 7 | V2's rubric/scoring approach will mirror V1's | **Assumption** | Not confirmed; flagged as open question (backlog EAB-1) |
| 8 | V2 remains synthetic-data-only and offline-compatible like V1 | **Assumption** | Not explicitly re-confirmed for V2; offline-compatibility in particular is in tension with LangSmith (a hosted service) — flagged (backlog EAB-2) |
| 9 | Does V2 need a new/updated case pack reflecting multi-agent-specific stakeholder concerns? | **Question** | Open — backlog EAB-3 |
| 10 | Does the V1 workshop audience (FDE capstone participants) remain the V2 audience, or does V2 target a different audience (e.g. production rollout team)? | **Question** | Open — backlog EAB-4 |

---

## 9. Top ten investigation hypotheses (ranked by impact on framing/design)

1. **H1 (highest impact):** V2's LangSmith dependency breaks V1's "offline-compatible" non-negotiable unless a local-only fallback mode is designed — this could force an ADR-level architecture split (hosted vs air-gapped deployment).
2. **H2:** V1's 12 required eval categories are necessary but not sufficient for a multi-agent system — new categories (agent authorization, loop/runaway-cost, cache-staleness) are required, confirmed by the gap between V1's `EVALUATION_PLAN.md` categories and known multi-agent failure modes.
3. **H3:** V1's rubric/scoring model (180 points, 30 artefacts) will need either extension or a parallel V2-specific rubric, since V2 has more stages (21) and different artefact types (agent contracts, cache design, threat models).
4. **H4:** The three governed workflows' *domain* logic (GxP rules, PV clock semantics, supply constraints) is unchanged by the agentic redesign — only the *delivery mechanism* changes. If true, this significantly de-risks DDD (Stage 06): bounded contexts carry forward, only agent/tool boundaries are new.
5. **H5:** V1's prohibited-terminal-action boundary (no release/reject/allocation decisions) is the single hardest constraint to preserve in a multi-agent design, because multi-agent systems are more prone to "emergent" authority creep across handoffs than a single-shot app.
6. **H6:** Redis caching interacts dangerously with V1's authority/freshness rules (stale-authorization, supersession) — a cache hit could serve an answer based on since-superseded evidence. This is flagged explicitly in `prompts/18_eval_ai_cache.md`'s cache-correctness-eval requirement.
7. **H7:** The reference-image repo pattern (`.claude`-based, 15-section) and V1's document-lifecycle pattern compose without structural conflict (already demonstrated in Stage 00), but stage content volume may be much larger than V1's per-artefact templates, given agent/tool/cache/security additions.
8. **H8:** Token economics (Stage 15) will be the first hard numeric constraint the design hits, since multi-agent systems multiply LLM calls per user request; this should be estimated early (Stage 04, final-state) rather than discovered late.
9. **H9:** EU AI Act risk classification (Stage 19) likely lands V2 in a high-risk-adjacent category given GxP/PV domain + human-oversight requirements already designed into V1 — this should be validated early since it could impose documentation obligations on *every* earlier stage retroactively.
10. **H10:** V1's static `app/` (inject explorer) and `submission/app-advanced/` (Next.js reference) are both **out of scope to reuse as V2's app** — V2's Stage 20 app is a new build on the agentic architecture, not a port of either.

---

## 10. AI FDE input sufficiency score

| AI FDE input | Score | What exists | What is missing |
|---|---|---|---|
| Business context | **Strong** | V1's full case pack (`case/`), regulatory boundary pack, stakeholder pack — directly reusable since the domain is unchanged | V2-specific stakeholder concerns for a multi-agent system (who owns agent authority decisions?) not yet captured |
| User workflow | **Partial** | V1's as-observed workflow is documented (via prior exploration + rubric/prompt structure); the *current* V1 solution's workflow (single-shot app) is understood at a high level | V2's target agentic workflow does not exist yet (by design — that's Stages 02–04, 10) |
| Constraints | **Partial** | GxP/regulatory/privacy constraints carry forward directly from V1 | New V2 constraints (offline-vs-hosted tension, token/cost budgets, EU AI Act obligations) are named but not yet quantified |
| Evidence (data, logs, research) | **Strong** | 143 CSVs, 32 knowledge docs, 15 public eval fixtures, full contract schemas all exist and are directly inspectable | No agent-run logs/traces exist yet (nothing has been built) — expected at this stage, not a gap |
| Stakeholder needs | **Strong** | Stakeholder pack + user's direct, explicit instructions in this conversation | Formal executive/sponsor sign-off on the V2 scope pivot (single-shot → multi-agent) not evidenced — reasonable to treat the user's instructions as sufficient authority for a workshop/capstone context |

**Overall framing mode: `decision-ready`**

Rationale: the domain (business context, evidence, stakeholder needs) is strong and carries forward almost entirely unchanged from V1's well-evidenced case. The two `Partial` inputs (user workflow, constraints) are partial specifically because V2's *target* state is intentionally not yet designed — that is deferred to Stages 02–04 by design, not because evidence is missing that Discovery should have obtained. Per the rule of thumb (default to `hypothesis` if Evidence or User workflow is Missing, or 2+ are Missing): neither is **Missing** (both are Partial or better), so `decision-ready` stands. The SCQA narrative (Stage 01→02) can be written mainly from facts/derivations without inventing unlabeled facts.

---

## 11. Evidence acquisition backlog

| ID | Item needed | Likely owner/source | Blocks | Priority |
|---|---|---|---|---|
| EAB-1 | Confirm whether V2 reuses/extends V1's `ASSESSMENT_RUBRIC.csv`/`SCORING_MODEL.md` or needs its own | User/sponsor | Stage 21 (final defense pack framing) | Blocks production (not design) |
| EAB-2 | Resolve offline-compatibility vs. hosted-LangSmith tension — will V2 support an air-gapped/local-only mode? | User/architecture decision | Stage 04 (final state), Stage 08 (ADR) | Blocks design |
| EAB-3 | Determine if a V2-specific case/stakeholder pack addendum is needed for multi-agent-specific concerns (agent authority ownership, HITL role definitions) | User/domain SME | Stage 06 (DDD), Stage 16 (governance) | Blocks design |
| EAB-4 | Confirm V2's audience: same FDE workshop participants as V1, or a different audience (e.g., production engineering) | User | Stage 21 (documentation/defense framing), overall tone of all stages | Blocks framing |
| EAB-5 | Re-verify prior-exploration derivations (item 5 in §8, inject count/dimension count) against `data/injects.json` directly | Whoever executes Stage 02 (current-state) | Stage 02 (current state) | Blocks design (low severity — informational) |
| EAB-6 | Quantify realistic token/cost budgets per workflow before Stage 04 commits to a specific agent count/topology | Architecture owner (Stage 10/15) | Stage 04, Stage 15 | Blocks design |

---

## Lean / DMAIC lens

See `dmaic_lens.md` (this folder) for the full Define→Measure→Analyze→Improve→Control cycle.

## Waste registers

See `waste_register_downtime.md` and `waste_register_ai_specific.md` (this folder).
