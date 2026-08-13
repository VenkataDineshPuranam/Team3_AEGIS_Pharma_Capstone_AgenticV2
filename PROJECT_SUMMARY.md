# PROJECT SUMMARY — Context Handoff

> **Purpose:** paste/reference this file at the start of a new chat to restore full context
> without re-reading the repo. Kept current as stages complete.
> **Last updated:** end of Stage 20a (interim slice build). Stages 16, 17, and 20a (interim)
> were completed in the same session that also fixed a stale-doc gap here — this file had not
> been updated since Stage 15 despite three more stages landing on top of it.

---

## 1. What this project is

**Project AEGIS-PHARMA V3** — an agentic AI evolution of the V2 pharma FDE capstone.
V2 delivered governed pharma decision-support as a **single-shot** app (one request in, one
JSON-contracted response out, graded by a deterministic harness). V3 re-architects the same
three governed workflows as a **governed, observable, multi-agent system**.

**Repo:** `/Users/puranamdinesh/Documents/FDE/Project_AEGIS_Pharma_AI_FDE_Capstone_Workshop_Ready_v3_claude_Agentic`
**V2 (read-only reference, gitignored):** `./Project_AEGIS_Pharma_AI_FDE_Capstone_Workshop_Ready_v2_claude/`

### The three governed workflows (unchanged from V2, verbatim prohibitions)

| Workflow | Does | **Must NEVER do** |
|---|---|---|
| **A — GxP Batch Review** | Reconcile batch genealogy, lab results, deviations, CAPA, validation state, release-packet completeness | Release, reject, reprocess, relabel, or recall a batch |
| **B — PV Intake & Signal Support** | Intake, duplicate detection, terminology normalization, reporting-clock reconstruction, listedness | Make final seriousness / causality / expectedness / reportability / signal-confirmation decisions |
| **C — Supply-Shortage & Cold-Chain Planning** | Generate traceable, non-executing options | Change inventory status, reserve, allocate, ship, or initiate recall |

### Non-negotiables (inherited)
Synthetic data only · decision **support** only, never terminal decisions · full evidence
provenance · GxP/privacy boundaries enforced by the governance layer, **not by prompting**.

---

## 2. Method & repo structure

**Spec-Driven Development**, 21 stages, **one git branch per stage**, app built **last**
(Stage 20). Lean + DMAIC block at every stage. SDD reference material:
`/Users/puranamdinesh/Documents/FDE-training/Day-27/1785208772944-Deck/`
(layered specs, each doc answers exactly one question, "nothing written twice").

Repo follows a `.claude`-based AI-Assisted SDLC scaffold: `.claude/ docs/ plans/ apps/
services/ packages/ tests/ quality/ security/ infra/ deploy/ ops/ evidence/ templates/
workshop/` + V2 carry-overs (`prompts/ knowledge/ evaluation/ runbooks/ eval-ai-cache/`).

- **`SPEC_DRIVEN_DEVELOPMENT.md`** — method + full stage table (each stage's driving prompt)
- **`STAGES.md`** — live status tracker
- **`plans/active/EXECUTION_PLAN.md`** — delivery plan for stages 10–21: four waves, the
  **20a/20b split around Gate M** (measurement only exists once code runs), the 5 decisions
  that need a human, and local-first environment guidance
- **`prompts/`** — 23 prompts: 01–13 adapted from V2, 14–23 new for V3-only concerns.
  `ADAPTATION_NOTES.md` records what changed and why.

### Git conventions (important)
- Work happens on the stage branch; downstream branches are **fast-forwarded** after each commit.
- **`main` is deliberately NOT kept in sync** (standing user instruction) — it sits at `57d0b92`.
- Sync command used: `for b in $(git branch --format='%(refname:short)' | grep '^stage-' | grep -vE '^stage-0[1-N]-'); do git branch -f "$b" <current-branch>; done`
- Outputs are written to `docs/...` **and mirrored** to `workshop/participant-output/NN-name/`.

---

## 3. Status: 17 of 21 stages complete, plus the Stage 20a interim slice built and running

| # | Stage | Branch | Status |
|---|---|---|---|
| 01 | Discovery + SCQA | `stage-01-discovery-scqa` | stable |
| 02 | **DDD** | `stage-02-ddd` | stable |
| 03 | **C4** | `stage-03-c4` | stable |
| 04 | **ADR** | `stage-04-adr` | stable — 9 ADRs, all accepted; review = **pass** |
| 05 | Current state | `stage-05-current-state` | stable |
| 06 | Interim state | `stage-06-interim-state` | stable |
| 07 | Final state | `stage-07-final-state` | stable |
| 08 | Graphical views | `stage-08-graphical` | stable |
| 09 | **DMAIC/Lean workbook** | `stage-09-dmaic-lean` | stable — 9 lenses reconciled; gate `cleared` |
| 10 | **Agentic arch (LangGraph)** | `stage-10-agentic-architecture` | stable for `batch_review`; provisional for PV/Supply |
| 11 | **MCP tool contracts** | `stage-11-mcp` | stable for batch tools; provisional for PV/Supply tools |
| 12 | **Skills & Hooks** | `stage-12-skills-hooks` | stable for `batch_review` bindings; provisional for PV/Supply |
| 13 | **Ontology-KG** | `stage-13-ontology-kg` | stable for Batch/Evidence classes; provisional for PV/Supply |
| 14 | **Eval-AI-Cache** | `stage-14-eval-ai-cache` | stable — 63 scenarios, 0 FAIL/ERROR |
| 15 | **Performance tuning** | `stage-15-performance-tuning` | stable — cost/latency models awaiting U1/U2; denial-of-wallet ceiling enforced (7/7 tests) |
| 16 | **Governance & Control** | `stage-16-governance-control` | stable — 13 policies (P-01…P-13) registered, all traced to an existing ADR/BC/hook; 3 (HITL timeout/escalation/veto) flagged with no executable eval yet |
| 17 | **Observability** | `stage-17-observability` | stable — 11-node tracing design, RBAC model (new — no prior RBAC coverage existed), severity taxonomy (SEV-1…4), redaction ruleset. **Gap:** never actually cites `eval-ai-cache/`'s OpenTelemetry Brownfield Runbook (NAB-4 not fully closed for this stage) |
| 18 | AI Security | `stage-18-ai-security` | not started — needs a running system to red-team; unblocked now that 20a exists |
| 19 | Compliance | `stage-19-compliance` | not started — needs evidence from real runs |
| **20a** | **Implementation — interim slice** (`batch_review` only) | `stage-20-repo-implementation` | **built and running** — real code for the first time since Stage 14. 6/7 interim assumptions pass (1 correctly `NOT_OBSERVABLE`); results are **provisional** (run on Groq, dev-only substitute; Route A/Claude re-run still owed per ADR-009). 3 real routing bugs found and fixed. See `docs/product/state/interim/interim_state_results.md` |
| 20b | Implementation — full build (+PV, +Supply, +Redis) | | not started |
| 21 | Documentation | `stage-21-documentation` | not started |

**Note:** stages were resequenced early on — DDD/C4/ADR moved *before* current/interim/final
state, per the user's explicit ordering (discovery → SCQA → DDD → C4 → ADR → … → app last).

---

## 4. Architecture decisions (all 9 accepted)

| ADR | Decision |
|---|---|
| **001** | Runtime stack: LangGraph (orchestration) + LangSmith (traces/evals) + Redis (cache) |
| **002** | **V3 built fully separately from V2** — V2 is read-only evidence only, no code reuse |
| **003** | Evidence authority is a **deterministic status gate**; **`untrusted` AND `superseded` are both non-citable**. Content never self-declares authority (prompt-injection catch) |
| **004** | Prohibited actions are **structurally unrepresentable** — 3 layers: aggregate schema has no such field, tool has no such method, runtime guard. Not a prompt instruction |
| **005** | Governance/Policy Engine = **separate container**, **fails closed** |
| **006** | Audit store **separate from LangSmith** (compliance retention ≠ vendor SLA) |
| **007** | **"Degraded-mode-safe", not "offline-capable"** — every hosted dep has a safe fallback. Air-gapped GxP-network variant recorded as a known limitation |
| **008** | **One deployment, one graph per workflow, NO cross-graph agent calls** |
| **009** | **Azure** is the target platform (see §7) |

### ADR-003 origin — worth remembering
Verifying V2's actual grader code (`submission/evaluation/graders/authority_grader.py`,
66 lines) **found an error in our own DDD model**: it had claimed `superseded` docs could be
cited with a flag; V2 defines `_MUST_NOT_CITE = {"untrusted", "superseded"}`. Corrected.
**Standing rule since:** never claim V2 behavior from a filename inference — verify against
V2 code/data.

---

## 5. Domain model (Stage 02, stable)

**Bounded contexts:** 3 core (Batch Review, PV Intake, Supply Planning) — **peers, no direct
coupling**; 2 supporting (Evidence & Provenance = shared kernel; Governance & Oversight =
**open-host service**, deliberately not a shared kernel so policy can't be locally weakened);
1 generic (Agent Orchestration).

**Domain agents:** Batch-Review, PV-Intake, Supply-Planning, + **Critic/Verifier** per graph.
A single generalist agent was explicitly **rejected** — it would have to hold all three
distinct prohibition sets at once.

**Key invariants:** `Batch` has no release/reject field · `ShortageOption` has no
`allocated_quantity` field · PV output has no causality/seriousness/reportability field ·
Supply tool has no allocation write method · zero write integrations to any brownfield system.

### Named HITL approvers (EAB-3, closed — taken verbatim from V2's `case/STAKEHOLDER_PACK.md`)

| Workflow | Approver | Their stated authority |
|---|---|---|
| A | **EU Qualified Person** (esc: Chief Quality Officer) | "Final certification remains human-only" |
| B | **Global Head of Pharmacovigilance** (esc: CMO; Patient Safety Rep has advisory veto) | "Final safety decisions remain human-only" |
| C | **Supply Chain VP** **+ Quality co-approver** where quality status is implicated | "Planning; regulated execution needs approvals" |

- **Manufacturing VP is explicitly NOT a batch approver** — "operations, never independent batch release".
- Accountability attaches to **roles, not individuals** (survives turnover; ISO 42001 expectation).
- HITL timeout ⇒ **no action**, never auto-proceed.

---

## 6. Transition plan

- **Current state:** design complete through Stage 08; **zero implementation**; 249 tracked files.
- **Interim state:** **ONE workflow (Batch Review) end-to-end.** Cache **deliberately excluded**
  (don't introduce stale-authority risk alongside agent-correctness risk). Prohibited-Action
  Guard present **day one** (can't be retrofitted). Must prove **7 assumptions**, incl.
  assumption 6 = **first real token/cost measurement** (Unknown since Stage 01) and
  assumptions 1–2 = **stop-the-line** (prohibited-action + evidence-authority enforcement).
- **Final state:** 3 workflows, 4 MCP tools, cache, dashboards/SLOs, threat model executed,
  compliance evidence from real runs. **3 of 7 completion gates still open** — all require
  the system to actually run.

---

## 6b. Lean/DMAIC consolidation (Stage 09, `docs/quality/dmaic-lean/`)

Nine prior `dmaic_lens.md` files + five register pairs reconciled into **one governing set**
(`lens_rollup.md`, `dmaic_plan.md`, two registers, `build_constraints_from_lean.md`,
`structural_reopen.md`). **24 distinct wastes merged; 11 still open.**

- **Mode = Measure-first.** Framing is `decision-ready`, but *every* baseline that matters is
  Unknown — nothing has ever been measured on a running system. Instrumentation outranks
  feature scale-out; no waste is described as "fixed," only as "decided, proof scheduled."
- **Three findings no single prior lens contained:**
  1. **C3 / RR-1** — Stage 01 said quantify token cost *before* locking topology. It wasn't:
     ADR-008 was accepted with cost still Unknown. Now an explicit accepted debt with revisit
     trigger **T-3** (bad interim cost number ⇒ reopen ADR-008 before building 3×).
  2. **G3** — "blind retry" (Model waste) lost its owner in the stage resequencing; assigned
     to Stage 10 (BC-5).
  3. **C1** — ontology-vs-agent ordering was resolved in practice but never written: Stage 10
     designs against an ontology **contract**, Stage 13 fills it in (BC-4).
- **12 must-fix-before-build constraints (BC-1…BC-12)** are binding input to Stage 10, with a
  recommended task order: guard + state schema + graph isolation first, then contract-first
  retrieval / retry rules / Critic scope, then instrumentation before any node is "done."
- **10 revisit triggers T-1…T-10** are now programme-level, incl. two stop-the-line ones
  (interim assumptions 1 and 2).
- **Structural gate: `cleared`** — no Improve action reopens C4, an ADR, or a contract.
  Two *documentation* defects recorded instead: **ADR-009 is missing from `decision_index.md`
  and `architecture_review.md`** (both still say "8 ADRs"), and NAB-2.

**Execution plan** (`plans/active/EXECUTION_PLAN.md`, not a stage spec): Stage 20 splits into
**20a (Batch Review interim slice, no cache) → Gate M → 20b (full build)**, because every
Unknown baseline becomes measurable only once code runs. Governance (16) and eval/observability
*design* passes (14/17) are sequenced **before** 20a; their *measured* passes come after.
5 human decisions named, the binding one being the **LLM route** (ADR-009) before 20a runs.

## 6c. Agentic architecture + MCP (Stages 10–11, `docs/architecture/agentic/`, `services/integration/`)

**Stage 10 — LangGraph design.** 11 nodes, **2 of them LLM nodes** (domain-agent synthesis +
Critic/Verifier); every control is deterministic (schema, status lookup, pattern match, edge
condition). Two decisions made and justified, not defaulted into: **no planner agent** (the
sequence is a constant; a planner would be a new authority surface and pure token waste) and
**no long-term agent memory** (a remembered conclusion has no citable source/status — it would
be a second, unaudited cache). DMAIC lens states plainly that **the multi-agent split is a net
token/context/transportation cost to buy one defect control** (the Critic doubles happy-path
LLM calls, 1→2) — most of the actual safety benefit comes from the deterministic nodes and the
absent schema fields, not from having multiple agents.

**HITL timeout = a four-tier escalation ladder** (T0 interrupt → T1 reminder → T2 conditional
escalation → T3 expiry/no-action), not a single deadline. Escalation only **widens** who may
approve (adds a role, never replaces or auto-approves) and only proceeds if, checked at that
moment: an escalation role is named for the workflow, that role has a **live** authorization
right now, the draft is still guard-clear, the policy version is still current, and the role's
own authority covers the decision. Any failed condition ⇒ audit-logged skip, run stays with the
primary on schedule. **Supply's planning leg has no escalation role at all** (V2's stakeholder
pack names none above the Supply Chain VP — not invented here) and its dual approval survives
escalation intact (both legs still required). PV's advisory veto (Patient Safety Rep) sits
outside the ladder — registrable at any tier, never overridden.

**Status split:** `batch_review` graph = `stable` (20a slice). `pv_intake`/`supply_planning` =
`provisional`, designed by analogy — RR-2/T-10 require re-checking, not assuming transfer.
Open gap flagged, not papered over: PV's reporting-clock reconstruction fits neither a tool
node nor a synthesis node yet (20b).

**Stage 11 — MCP tool contracts.** 7 tool operations across 6 server registrations. **Every
tool is read-only** — the real design question was retrieval-scope enforcement, not
read/write. Decision: **one server per bounded context for `evidence.retrieve`, with `scope`
absent from the input schema entirely** (fixed at server-binding time, not agent-supplied) —
applying ADR-004's "don't rely on the caller passing the right value" one layer down, to tools.
`prohibited_write_enforcement.md` walks the three-layer argument (schema/tool-method/runtime
guard) through a worked example on `supply.generate_options`, the contract closest to a write.

**Caching finding for Stage 15:** "read-only ⇒ cacheable" is wrong for two tools —
`pv.duplicate_check` (a case can become a duplicate as new cases arrive) and
`supply.generate_options` (inventory/quality status are the most volatile data in the system;
a stale cached option set can recommend against inventory that no longer exists). Both marked
do-not-cache-by-default pending an invalidation design.

`.claude/mcp.json` deliberately left with `mcpServers: {}` — registering commands for
unimplemented servers would make this repo's own Claude Code session try to launch nonexistent
processes. Per standing instruction: **register only real, needed MCP servers**, not
speculative ones; Stage 20 populates it for real when server code exists.

**Stage 12 — Skills & Hooks** (`.claude/skills/skills.md`, `.claude/hooks/hooks.md`,
`.claude/skill_vs_hook_boundary.md`). Catalogued Stage 10's 9 deterministic nodes as hook
bindings (session-start, pre-tool-call, post-tool-call, pre-output, on-interrupt, post-run) and
named 4 runtime domain-agent skills + 4 build-process skills for the 2 LLM nodes. **The rule
this stage adds, not just relabels:** no skill's output is ever the last check on itself —
every skill (e.g. the Critic's judgement) has a downstream hook checking its output's *shape*,
never trusting the skill's own reasoning. Worked counterexample in
`skill_vs_hook_boundary.md` §4 shows why folding the prohibited-action check into the Critic's
prompt (skip the separate guard hook) would fail: it makes the highest-severity control in the
system depend on a model correctly resisting a jailbreak exactly once, with no independent
check — precisely the H5 risk from Stage 01.

Same operational-safety call as Stage 11's `mcp.json`: **`.claude/hooks.json` stays
`hooks: {}`.** These bindings govern the *deployed* V3 runtime (Stage 20), not this coding
session — populating real PreToolUse/PostToolUse commands now, before the scripts exist, would
make this repo's own Claude Code session try to run nonexistent hooks on every tool call.

**Correction applied same session:** cross-verifying `failure_and_loop_guards.md` against
`langgraph_design.md`'s actual edge table found a real contradiction — a first-occurrence
`PROHIBITION_ADJACENT` Critic verdict was routable back to `synthesize` for a retry, when the
rule required it go straight to `blocked`, never retried. Dangerous specifically because that
code only fires when the cheaper `guard1` pattern-match has already missed a draft — retrying
would ask the model to rephrase a near-miss on the system's highest-severity control. Fixed:
`critic_verify` now has an unconditional `PROHIBITION_ADJACENT ⇒ blocked` edge, checked first.

## 6d. Ontology / Knowledge Graph (Stage 13, `docs/architecture/ontology/`)

**NAB-3 half-resolved.** V2's `knowledge/` (32 policy docs) + `knowledge_catalog.csv` (the
provenance/status/trust/supersession index) copied into this repo's own `knowledge/` and
SHA-256-verified against the catalog's own hashes. V2's `data/`/`evaluation/` fixture half
stays cross-repo, left for Stage 14 on the Overproduction argument (copying unused fixtures now
would be waste). Reasoning: a gitignored, 983MB sibling directory isn't reproducible for anyone
cloning only this repo, and this stage is the first that needs a stable source to build a KG
schema against. Not a reopening of ADR-002 ("no code reuse") — this is domain reference data,
not application code.

**17 classes, 14 edge types, grounded against V2's actual CSV schemas** (`batches.csv`,
`icsr_cases.csv`, `knowledge_catalog.csv`, etc.), not derived from DDD prose alone. Two findings
surfaced only by checking real data:

1. **`SensitiveSegment`** (`pregnancy`/`minor` case segments with restricted `access_group`s) —
   a governance boundary DDD's original entity table never named. Flows *backward* as a gap in
   Stage 02, recorded honestly rather than silently patched. Consequence: the PV-Intake Agent's
   evidence scope needs an access-group check in addition to bounded-context scope — currently
   unmodeled in `langgraph_design.md` or the MCP contracts; assigned to Stage 16/20.
2. **`Deviation` has no `batch_id` foreign key anywhere in V2's own relationship model.** The
   deviation-to-batch link that `batch.reconcile` needs isn't a guaranteed structured join —
   Stage 20 will need a defined matching heuristic (site/date/product overlap), not a lookup.

**Semantic layer fills BC-4** (Stage 10 designed agents against an ontology contract that
didn't exist yet) and specifies exactly what Stage 11's `evidence.retrieve` query terms resolve
against: KG concept/relationship/text match, single-hop bounded by context, `PortfolioProduct`
as a hop-terminator (it's the one cross-workflow hub node, so a naive second hop would leak
across workflows — blocked by both the hop rule and by each context having its own server
process, `tool_inventory.md` §1).

**Conflict/authority rules — every one traced to an existing decision, none invented:** the
ADR-003 citability rule re-confirmed independently against real catalog data (not just Stage
04's grader-code reading); `local_approved` documents are fully citable within their
jurisdiction, never subordinate to a `Global` document by jurisdiction alone — only an explicit
`supersedes` edge establishes precedence; `supersedes` is populated only from the catalog's own
column (which stores a filename, not a key — normalized once at ingestion), never re-derived
from a document's prose claiming to supersede something.

## 6e. Eval-AI-Cache (Stage 14, `eval-ai-cache/`, `quality/gates/`, `tests/unit/graders/`)

**Full DMAIC stage** (sets Measure/Control for the whole agentic system). Consumes
`eval-ai-cache/AI_FDE_Brownfield_Evals_Cursor_Runbook/` rather than re-deriving it (NAB-4/T-7)
— gate-state vocabulary (`PASS`/`FAIL`/`REVIEW`/`NOT_APPLICABLE`/`NOT_OBSERVABLE`/
`THRESHOLD_NOT_DEFINED`/`BLOCKED_BY_ENVIRONMENT`) and hard/threshold/operational gate taxonomy
both taken from it directly. Grader **patterns** (not code — ADR-002) verified against V2's
actual `submission/evaluation/graders/*.py` and `tool_gateway.py` first.

**63 real scenarios, 15 categories (12 required + 3 agent-specific), executed this session —
0 FAIL, 0 ERROR.** Honestly scoped: this is a design-pass run against synthetic fixtures shaped
like our own contracts, since no `apps/`/`services/` code exists yet (Stage 20 last) — not a
live-system run. 2 `NOT_APPLICABLE` (business outcome, human-rubric, matches V2's own
un-automated category), 1 `THRESHOLD_NOT_DEFINED` (cost-per-task cap — U1 still Unknown,
refused to guess), 1 `BLOCKED_BY_ENVIRONMENT` (model-substitution check pending ADR-009's route
decision). Verify with `python3 eval-ai-cache/graders/run_eval_dataset.py` or
`pytest tests/unit/graders/ -q`.

**The harness found 7 real defects in itself before it was trusted** (`scorecard.md` §2) —
a schema-path doubling, a replay-counter that incorrectly incremented on plain replays
(contradicting V2's own verified `tool_gateway.py` behavior), an adversarial fixture whose
"bad" branch the grader had no way to actually produce, and 3 more. All fixed; recorded rather
than hidden behind the final green run, since a scorecard showing only the clean pass
overstates first-try correctness.

**Agent-specific category 13 (`agent_wrong_handoff`) is the regression suite for the real
`PROHIBITION_ADJACENT` routing bug** found and fixed at Stage 10 — `AWH-01` asserts the fix
holds: a first-occurrence `PROHIBITION_ADJACENT` verdict must route straight to `blocked`,
never to a retry.

**Cache design (`cache_design.md`) — not built,** per `interim_state.md`'s deliberate exclusion.
Cache key = `hash(query, evidence_snapshot_version)`, never a plain wall-clock TTL (a TTL can't
distinguish "still correct" from "coincidentally not yet expired"); do-not-cache list
(`pv.duplicate_check`, `supply.generate_options`, both from Stage 11) enforced via an executable
grader, not just documentation. **Cache-correctness evals: 8 checks, all executed and correct**
(`cache_correctness_evals.md`) — including the exact scenario the prompt names: a cache hit on
`K-007` (the real `BATCH_RELEASE_POLICY_OLD.md` supersession pair) after it transitions to
`superseded` is caught, not served.

**Release gates independently re-derived from our own ADRs**, not copied from V2's 10 gates
(ADR-002) — traceability table maps every gate to its owning ADR/DDD invariant and grader.

## 6f. Performance Tuning (Stage 15, `docs/quality/performance/`, `infra/policies/`)

Same honesty split as every measurement-dependent stage: cost/latency **targets** need U1/U2
(Unknown since Stage 01, first measurable at 20a); what's real is stated as real, what isn't is
left explicitly open rather than guessed.

**Token economics — real, verified pricing, no invented usage numbers.** Loaded the `claude-api`
skill (standing trigger for any Claude/Anthropic pricing discussion) rather than recalling
stale figures: Opus 5 $5/$25 per MTok, Sonnet 5 $3/$15, and confirmed Azure AI Foundry
(ADR-009 Route A) bills at the same first-party rates — closing one small piece of ADR-009's
open question. Recommended (not decided) starting model for 20a: Sonnet 5. Cost model is exact
(2 LLM nodes only, per `langgraph_design.md`); actual token volume per run is still Unknown.

**Redis tuning — consumed the pre-seeded runbook in full** (NAB-4/T-7, previously unread).
Key finding: the runbook's own engineering-plane/data-plane split means the deployed app must
use a **native Redis client, never MCP**, at runtime — a new rule, distinct from Stage 11's
unrelated domain-agent MCP tool servers. Also found and fixed a real gap in Stage 14's cache
design: it never specified *where in the pipeline* caching happens relative to the
Prohibited-Action Guard/Critic — now fixed (never cache a draft, only a guard-and-Critic-cleared
response). Cluster-failure *alerting* (as opposed to correctness-on-failure, already specified)
was also missing and is now specified. No cache is built — unchanged from Stage 14.

**Denial-of-wallet guardrail — the one Stage 15 deliverable that's actually built and tested,
not just designed.** A worst-case ceiling needs no measurement, only already-ratified inputs:
`DAILY_RUN_CEILING=20` (reuses C4) × `MAX_TOKENS_PER_RUN=150,000` (=C1) × verified Sonnet 5
output price = **$45.00/user/workflow/day**. Fail-safe direction matches ADR-005. **7/7 tests
passing** (`tests/unit/policies/test_denial_of_wallet_guardrail.py`), proving per-user/
per-workflow isolation, daily reset, and that the ceiling actually trips. Wired into
`.claude/hooks/hooks.md` as a tenth hook row (pre-tool-call, at `intake`) — the only row in that
table backed by a real executable + test rather than only a design reference.

## 6g. Governance & Control (Stage 16, `docs/governance/`, `security/policies/`)

**13 governed boundaries (P-01…P-13) consolidated, none invented** — every entry traces to an
existing ADR (004/005/006/008), a Build Constraint (BC-1/3/5/8/12/17), or a `hooks.md` binding
that already existed. The exercise itself surfaced a real gap the individual documents hadn't
made visible: P-07/P-08/P-09 (HITL timeout, escalation, PV advisory veto) are `stable` in
design but have **no executable eval** yet — they need a running interrupt/clock, which
Stage 14's fixture-based harness can't simulate. Recorded honestly, not hidden behind the
9-of-13-covered figure.

`hitl_control_model.md` was **extended, not overwritten** (per its own instruction) with a new
§7 confirming the Stage 10 timeout-ladder durations against the named roles — "confirmed" here
means checked for internal consistency, not signed off by an actual person (no operating org
exists yet). New revisit trigger **T-11**: re-confirm every role/duration against a live Entra
assignment at first real deployment.

`escalation_override_log_design.md` designs three distinct audit record shapes
(`HitlEscalation`, `HumanOverrideRecorded`, `HitlExpired`) — deliberately kept separate so "the
system widened who may approve" is never conflated with "a human actually decided," which BC-12
depends on staying distinguishable.

## 6h. Observability (Stage 17, `packages/observability/`, `ops/`)

**Tracing design binds one span per node/hook that already existed** in `langgraph_design.md`/
`hooks.md` — no new control invented, only made explainable. Actor identity
(`actor_plane`/`actor_role`/`actor_id`) added to every span, closing a gap that existed between
the RBAC model and the trace schema.

**Two additions beyond the stage's original prompt scope**, added at explicit user request
after a gap review mid-session:
- **`rbac_model.md`** — zero RBAC coverage existed anywhere in the repo before this. Names both
  a human plane (extends `hitl_control_model.md` with system-access roles it never covered —
  Compliance Reviewer, Platform Operator) and a service plane (one managed identity per
  container, mapped 1:1 onto ADR-008's "zero cross-graph calls" as Azure RBAC role scoping),
  both on Entra ID (ADR-009).
- **Severity taxonomy** (`alerting.md` §1) — SEV-1 (stop the line) through SEV-4 (dashboard-only),
  replacing severity language that was previously asserted ad hoc and inconsistently across
  `failure_and_loop_guards.md`.

**Known gap, not silently closed:** this stage's own prompt says it should draw on
`eval-ai-cache/`'s OpenTelemetry Brownfield Runbook — none of `packages/observability/`'s docs
actually cite it. Flagged in §8 below.

## 6i. Implementation — Interim Slice (Stage 20a, `packages/`, `services/`, `tests/`)

**First stage to produce and run real application code**, not design documents, since
Stage 14's eval harness. Scope exactly matches `EXECUTION_PLAN.md` Wave 3: `batch_review` only,
no Redis, no PV/Supply.

- **`packages/domain/`** — `GovernedState`, `EvidenceItem`, `BatchPayload`,
  `DecisionSupportOutput`. ADR-004 layer 1 enforced with pydantic `extra="forbid"`: a
  disposition field (`release_recommended`, etc.) cannot be constructed, not just disallowed by
  convention — proven by a red-team-style test that tries and fails at construction time.
- **`packages/domain/kg/`** — the Stage 13 semantic layer, actually built on **Neo4j** (a
  technology no prior ADR had selected — added at user request this session), ingesting the
  real 32-doc `knowledge/` corpus with SHA-256 provenance. K-006 supersedes K-007 (a real pair
  in the catalog) verified live: querying for K-007 after ingestion never returns it.
- **`services/integration/`** — `evidence_retrieve.py`/`batch_reconcile.py` contract-validated
  against the real Stage 11 JSON schemas; `policy_engine.py` (fails closed, ADR-005),
  `prohibited_action_guard.py` (ADR-004 layer 3), `evidence_gate.py` (ADR-003 second check),
  `hitl_route.py` (four-tier ladder), `audit_store.py` (append-only SQLite, veto cannot be
  superseded — enforced at the write layer, not by convention).
- **`services/api/graph.py`** — the full 11-node `batch_review` LangGraph. LLM provider is
  swappable via one interface (`packages/config/llm_client.py`) — Anthropic (Route A, the only
  provider whose results count) or Groq (dev-only, provisional, used this session per user
  instruction while the Anthropic key was being corrupted in transit twice).

**Results: 6 of 7 interim assumptions (`interim_state.md` §3) PASS**, one correctly
`NOT_OBSERVABLE` (hop count needs Stage 20's real deployed topology, not this in-process
build). Full writeup: `docs/product/state/interim/interim_state_results.md`.

**Three real routing bugs found and fixed**, all only because a live model (even an unreliable
one) exercised paths the deterministic stub test never did:
1. Cap-exceeded and `PROHIBITION_ADJACENT`-blocked routes reached `finalize` without setting
   `terminal_state`, silently mislabeling both as `"completed"`.
2. Approval detection used an empty `critic_reason_codes` list as its signal, but that list
   accumulates across the whole run — a genuine approval after a prior rejection was misrouted
   using a stale reason code.
3. **The HITL timeout path never set `terminal_state`** — the highest-stakes of the three,
   since it directly affects BC-12 ("timeout ⇒ no action, never auto-proceed"). A timeout was
   silently finalizing as `"completed"`. Fixed directly in the `hitl_interrupt` node.

**Finding beyond pass/fail:** Groq's small model (`llama-3.1-8b-instant`) repeatedly
false-rejected a correctly-cited draft, hitting the G1 retry cap (6 LLM calls) rather than
approving quickly. Not a code defect — the loop guards worked exactly as designed — but direct
evidence for ADR-009's own rationale (keep the model variable fixed while the platform moves):
a weaker model changes the *shape* of a run, not just its prose quality.

## 7. Tech stack (ADR-001 + ADR-009 Azure)

| Concern | Choice |
|---|---|
| Orchestration | **LangGraph** on **Azure Container Apps** (AKS if scale demands) |
| LLM inference | **CONFIRMED — Route A: Claude via Azure AI Foundry.** Dev/20a calls the Anthropic API directly (one client interface, `packages/config/llm_client.py`); Foundry is the deployment-time binding behind the same interface. **20a's actual runs used Groq (dev-only, provisional) at user's direction while the Anthropic key was being sorted** — Route A itself is unchanged and still the only provider whose results count toward the real exit criteria. Verify region availability at implementation time |
| Cache | **Azure Cache for Redis** |
| Observability | **LangSmith** + **Azure Monitor/App Insights**; **OpenTelemetry** as the instrumentation layer so the backend stays swappable |
| Audit/evidence store | **Azure Blob Storage with immutability (WORM)** + optional Azure SQL for queryable metadata |
| Secrets | **Azure Key Vault** |
| Identity / approver authorization | **Microsoft Entra ID** — approver roles become Entra groups, making "current authorization at execution time" enforceable infra; Supply's dual approval = membership in two groups |

**Guardrail:** no Azure-specific API may leak into domain or agent logic — platform bindings
live in `packages/config` and `infra/`.

### Azure is the DEPLOYMENT target, not a DEVELOPMENT requirement
**Only LLM inference needs cloud.** LangGraph is a library; Redis runs in Docker; audit store
can be local Postgres/SQLite; OTel can point at a local collector; Entra ID/Key Vault are
stubbable. **Develop locally (Docker Compose + one API key), deploy to Azure.** The whole
interim state — including all 7 assumption tests — runs on a laptop, with no Azure spend
until deployment. Stage 20 must not treat Azure as a prerequisite for writing/testing code.

---

## 8. Open items

| ID | Item | Blocks |
|---|---|---|
| NAB-2 | `plans/active/` empty while method doc says specs go there. Recommended fix: **correct the method doc** (prompts already are the spec; duplicating violates "nothing written twice") | Doc accuracy only |
| NAB-3 | Copy V2's `knowledge/` (32 docs) + `evaluation/` fixtures locally, or keep as cross-repo reference? — **half-resolved**: `knowledge/` copied and SHA-256 verified (Stage 13), now also live-ingested into Neo4j (Stage 20a). `data/`/`evaluation/` fixtures still cross-repo | Stage 20b |
| **NAB-4 (partial)** | `eval-ai-cache/`'s OpenTelemetry Brownfield Runbook (`eval-ai-cache/*OpenTelemetry Brownfield Implementation Runbook.docx`) was **never actually cited or consumed** by Stage 17's `packages/observability/` docs, despite the stage's own prompt saying it should draw on it. Stages 14/15 did consume their respective parts of `eval-ai-cache/`; Stage 17 did not | Should be revisited before Stage 20b's real dashboards/alerting are built |
| **P-07/P-08/P-09 eval gap** | HITL timeout/escalation/veto (Stage 16 `policy_register.md`) are `stable` in design but have no executable Stage 14 eval — need a running interrupt/clock, which the fixture harness can't simulate | Stage 18 (red-team the running slice) is the natural place to close this |
| **20a results provisional** | Interim-assumption results (`interim_state_results.md`) were run under Groq (dev-only), not Claude. Token-economics number (assumption 6) is real but not the Route A number | Must re-run under `LLM_PROVIDER=anthropic` before Gate M can evaluate real evidence |
| Stale checkpointer warning | LangGraph's `MemorySaver` deserializes our custom pydantic types (`EvidenceItem`, `BatchPayload`, etc.) via an unregistered-type fallback that "will be blocked in a future version" | Register `allowed_msgpack_modules` or add custom serializers before upgrading LangGraph |

**Closed:** EAB-2 (air-gap → cloud-connected confirmed), EAB-3 (approvers named), NAB-1,
**ADR-009's LLM route** (confirmed Route A), **S09-D1** (ADR-009 now listed in both
`decision_index.md` and `architecture_review.md`, "9 ADRs" not "8").

---

## 9. Known risks carried forward

1. **Single-workflow generalization** — Batch Review's shape may not transfer to PV's
   duplicate/clock semantics or Supply's option ranking. Each interim conclusion must be
   **re-checked per workflow**, not assumed to transfer (Stage 20 acceptance condition).
2. **Shared blast radius** — one deployment serves all three graphs (ADR-008, accepted).
3. **Vendor concentration** — now Microsoft *and* the model provider. V2's own source-system
   pack flags "bundled vendor, weak cost controls" as a known org failure pattern.
4. **Cache staleness under supersession** — a cache hit must never serve an answer built on
   since-superseded evidence (ADR-003 guardrail; Stage 14 cache-correctness evals).
5. **Neo4j added without an ADR.** Stage 20a's semantic-layer implementation uses Neo4j
   (AuraDB) at user request — no prior ADR selected a graph database technology; Stage 13's
   `kg_schema.md` specifies the ontology, not a storage engine. Widens the vendor-concentration
   risk in item 3 by one more provider. Should get a real ADR before Stage 20b if the choice is
   meant to persist past this interim slice.
6. **Provisional-provider results in the repo.** `interim_state_results.md`'s numbers were
   measured under Groq, not Claude — a reader skimming only the pass/fail table without the
   provisional caveat could mistake them for Route A evidence.

---

## 10. Working style established in this project

- Ground claims in **evidence with file paths**; classify fact / derivation / assumption / question.
- Mark artifact status honestly (`provisional` vs `stable`) rather than overclaiming.
- **Flag disagreements and errors openly** — the ADR-003 correction is the precedent.
- Record known limitations rather than papering over them (e.g. ADR-007's air-gap note).
- Don't add scope without a stated requirement (V2 workflows D/E were explicitly rejected).
