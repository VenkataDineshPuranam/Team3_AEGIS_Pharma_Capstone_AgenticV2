# SCQA & Minto Pyramid — Stage 02 (Frame)

**Executes:** `prompts/02_scqa_minto.md`
**Builds on:** `docs/product/discovery/evidence_register.md` (Stage 01)

---

## 0. Narrative class

- **Narrative class:** `decision-ready` (matches Stage 01's declared framing mode; no
  upgrade needed).
- **Evidence boundary:** This narrative may claim what is directly evidenced in the V2
  repository (domain, constraints, eval floor, rubric structure) and what the user has
  explicitly decided in this conversation (runtime stack, repo pattern, sequencing). It may
  **not** claim specifics of a target agent topology, tool count, or performance numbers —
  those remain open for Stages 03–15.
- **Top blocking acquisition items:** None block this narrative at `decision-ready`; EAB-2
  (offline/hosted tension) and EAB-6 (token budgets) are the two backlog items most likely
  to force a *later* stage back to `provisional` if unresolved by Stage 04/08.

---

## A. SCQA Narrative

### Situation

Project AEGIS-PHARMA V2 is a complete, evidence-grounded FDE capstone: 84 injects across
13 dimensions, 143 CSV datasets, 32 knowledge/policy documents, a deliberately defective
starter codebase, and a 30-artefact/180-point rubric, all built around three governed
pharma decision-support workflows — GxP batch-review evidence reconciliation,
pharmacovigilance intake/signal support, and supply-shortage/cold-chain option planning
(`case/INTEGRATED_CASE.md`, `evidence_register.md` §1). V2's solution pattern is
**single-shot**: one governed request in, one JSON-contracted response out, evaluated by a
from-scratch deterministic grader harness against 12 required categories
(`evaluation/EVALUATION_PLAN.md`, `submission/evaluation/graders/`). This pattern is
well-governed and thoroughly evidenced, but it does not exercise multi-step agent
reasoning, tool use, inter-agent handoff, response caching, or continuous runtime
observability — none of which V2 needed, because it was never designed to have them.

### Complication

The user has decided V3 must become an **agentic AI system**: multiple LangGraph-orchestrated
agents collaborating (with governance, control, and observability layers), using MCP tools,
a Redis-backed cache, and LangSmith-based tracing/evals — while performing the *same* three
governed workflows under the *same* non-negotiables (synthetic data only; no agent makes a
terminal safety/release/allocation decision; full evidence provenance)
(`evidence_register.md` §5, `README.md` non-negotiables). This is a compound problem across
several dimensions simultaneously:

- **Technical:** multi-agent orchestration, tool contracts, and shared state did not exist
  in V2 and must be designed from a domain model (`docs/architecture/ddd/`) that itself
  needs re-examination for agent/authority boundaries, not rewriting.
- **Governance/regulatory:** the single hardest constraint to preserve — no prohibited
  terminal decision — is *more* fragile in a multi-agent design, because authority can leak
  across an agent handoff in a way a single-shot app cannot exhibit (`evidence_register.md`
  §9, H5).
- **Operational/cost:** multi-agent designs multiply LLM calls per request; token/cost
  economics were never a first-order concern in V2 and must become one before agent
  topology is locked (`evidence_register.md` §9, H8; §11, EAB-6).
- **Data/caching:** introducing a response cache creates a new failure mode V2's authority/
  freshness rules never had to guard against — a cache hit silently serving an answer based
  on since-superseded evidence (`evidence_register.md` §9, H6).
- **Compliance (new):** V3 additionally takes on EU AI Act and ISO 42001 obligations that
  V2 never carried, likely landing the three governed workflows in a high-risk-adjacent
  classification given the GxP/PV domain plus required human oversight
  (`evidence_register.md` §9, H9).
- **Infrastructure (new, unresolved):** LangSmith is a hosted service; V2 was framed as
  offline-compatible. Whether V3 preserves that framing, splits into hosted/air-gapped
  modes, or abandons it, is not yet decided (`evidence_register.md` §11, EAB-2).

### Question

**How should Project AEGIS-PHARMA be re-architected as a governed, observable, multi-agent
system that preserves V2's domain correctness and prohibited-decision boundary while adding
LangGraph orchestration, MCP tool use, Redis caching, and LangSmith observability — without
inventing an architecture before the domain, governance, and cost constraints that must
shape it are established?**

### Answer (decision-ready, capability-level)

**V3 should proceed as an additive re-architecture, not a domain rewrite:** carry V2's
domain model, constraints, and evaluation floor forward unchanged as the substrate, and
layer a governed multi-agent capability on top of it — sequencing the work so that
governance/authority boundaries (DDD, Stage 06) and cost/architecture constraints (final
state, Stage 04; token economics, Stage 15) are established *before* any agent topology or
tool contract is locked, and before any application code is written (Stage 20, deliberately
last). This is a capability-level recommendation: it does not preselect the number of
agents, the specific LangGraph graph shape, or specific MCP tool names — those are Stage 10
and Stage 11 decisions, made once the domain/governance/cost inputs this Answer depends on
are stable.

**Desired outcomes / what "good" looks like:**
- Every one of V2's three governed workflows has a working multi-agent implementation that
  passes V2's original 12 eval categories *and* V3's new agent-specific categories
  (Stage 14) with zero regressions on the prohibited-decision boundary.
- Token/cost per workflow run is known and bounded *before* the system ships, not
  discovered after.
- Every governance boundary (prohibited decision, PII handling, HITL) is enforced by a hook
  or policy check independent of agent prompting, not by instruction alone.
- EU AI Act risk classification and ISO 42001 control mapping exist with evidence, not just
  as an end-of-project addendum.

**Measurable outcomes** (baselines marked known vs unknown, per `evidence_register.md` §2 DMAIC Measure):
- Eval pass rate on V2's 12 categories: **baseline unknown** (V2's actual scorecard was not
  read this pass) — must be established at Stage 02→14 transition.
- Token/cost per workflow run: **unknown**, target to be set at Stage 04/15.
- Cache hit rate: **unknown** (no cache exists yet), target set at Stage 15.
- Prohibited-decision boundary violations in eval/red-team testing: **target is zero**,
  non-negotiable, measured at Stage 14 (eval-ai-cache) and Stage 18 (security).

**Audience:** whoever is driving this repository's build (the user, in an FDE/workshop-style
engineering capacity) plus any future reviewer of the stage artefacts (per the
`.claude`-based repo pattern's `evidence/` folder, designed for exactly this kind of review).

**Decision horizon:** this Answer governs Stages 02 through 19 (all design/governance/eval
stages); it is revisited at Stage 04 (final state) once cost/architecture constraints are
quantified, and again at Stage 08 (ADR-0001, runtime stack ratification).

**Evidence boundary / authority boundary:** this Answer rests on the V2 evidence cited above
and the user's explicit decisions recorded in `evidence_register.md` §5. It does not rest on
any measured V3 performance data, because none exists yet.

**Explicit exclusions (what this decision does NOT cover):**
- Does not select the specific number or names of agents (Stage 10).
- Does not select specific MCP tool implementations (Stage 11).
- Does not resolve the offline/hosted tension (EAB-2) — that is an open question this
  Answer inherits, not resolves; it is explicitly deferred to Stage 04/08.
- Does not commit to a specific EU AI Act risk tier (Stage 19) — only asserts that
  classification work must happen with evidence, not be assumed.

---

## B. Minto Pyramid view of the Answer

### 1. Governing answer

**Re-architect additively: preserve V2's domain/constraints/eval floor unchanged; layer
governed multi-agent capability on top; resolve governance and cost constraints before any
agent topology is locked; build the app last.**

### 2. MECE key supporting points

1. **Domain continuity reduces risk.** The three governed workflows' business rules (GxP,
   PV, supply) are unchanged by the delivery-mechanism shift from single-shot to
   multi-agent — re-deriving them from scratch would be pure waste (Overproduction/Extra
   processing, per `waste_register_downtime.md`).
2. **The prohibited-decision boundary is the highest-risk regression surface**, specifically
   *because* multi-agent handoffs create a new place for authority to leak that a
   single-shot app structurally cannot exhibit — so DDD's agent-boundary work (Stage 06)
   must precede any orchestration code.
3. **Cost is a hard constraint multi-agent designs hit first and hardest** — token
   multiplication across agent turns is a named, evidenced risk (`waste_register_ai_specific.md`,
   Token row) that must be quantified before topology is locked, not discovered after
   build.
4. **Caching introduces a genuinely new correctness risk** (stale-authority answers) that
   V2's rules never had to address — cache design cannot be bolted on after the fact; it
   needs explicit correctness evals from Stage 14 onward.
5. **New compliance obligations (EU AI Act, ISO 42001) are additive to, not a replacement
   for, V2's existing regulatory boundary pack** — they require evidence, not assertion, and
   should be worked continuously (Stage 19) rather than retrofitted at the end.
6. **Sequencing discovery → SCQA → DDD → C4 → ADR → agentic-specific design → app-last is
   itself the risk-reduction strategy** — it is not incidental process; it is how this
   Answer avoids the single biggest failure mode of agentic rebuilds (designing the graph
   before the domain).

### 3. Support under each point

| Point | Support (fact/derivation) | Labeled assumption (if any) |
|---|---|---|
| 1 | V2's `case/` pack, `evaluation/EVALUATION_PLAN.md`, and 143-CSV/32-doc knowledge base directly describe unchanged domain rules (Fact, `evidence_register.md` §1) | Assumes no domain-rule changes were separately requested — none observed in this conversation |
| 2 | H5 in `evidence_register.md` §9 (derivation); DDD Stage 06 prompt already requires naming agent authority limits explicitly (`prompts/04_ddd.md` §10, as adapted) | — |
| 3 | Token waste named explicitly as highest-magnitude AI-specific risk (`waste_register_ai_specific.md`, Token row); `prompts/19_performance_tuning.md` exists specifically for this | Magnitude is hypothesized, not measured — flagged |
| 4 | Cache-correctness eval requirement is written directly into `prompts/18_eval_ai_cache.md` (Fact — prompt content) | — |
| 5 | User's explicit instruction to cover EU AI Act/ISO 42001 (Fact, this conversation) | Risk-tier classification itself is not yet determined — explicitly excluded from this Answer |
| 6 | User's explicit sequencing instruction (Fact, this conversation); SDD method documented in `SPEC_DRIVEN_DEVELOPMENT.md` | — |

---

## C. Framing handoff pack

- **Decision question locked for PRD/DDD:** "What domain model, agent/authority
  boundaries, and governance rules must be in place before any agent topology or tool
  contract is designed?" — this is now the driving question for Stage 03 (interim state)
  through Stage 06 (DDD).
- **Success metrics for later PRD/DMAIC Measure/Control:** eval pass rate (baseline
  unknown), token/cost per workflow (unknown), cache hit rate (unknown), prohibited-decision
  violations (target zero) — see Answer §"Measurable outcomes" above.
- **Open questions that block design:** EAB-2 (offline/hosted), EAB-3 (case-pack addendum
  for agent authority ownership), EAB-6 (token budgets) — must be resolved or explicitly
  assumed by Stage 04.
- **Provisional marking:** Stages 03 onward may proceed as `stable`-track (not forced to
  `provisional`) given the `decision-ready` framing mode — **except** any sub-decision that
  depends specifically on EAB-2 or EAB-6 must be marked `provisional` until those resolve.

---

## Lean / DMAIC lens

See `dmaic_lens.md` (this folder).

## Waste registers (updated from Stage 01)

See `waste_register_downtime.md` and `waste_register_ai_specific.md` (this folder).
