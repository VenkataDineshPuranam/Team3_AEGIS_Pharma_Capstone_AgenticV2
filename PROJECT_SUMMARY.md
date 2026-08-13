# PROJECT SUMMARY — Context Handoff

> **Purpose:** paste/reference this file at the start of a new chat to restore full context
> without re-reading the repo. Kept current as stages complete.
> **Last updated:** end of Stage 12 (Skills & Hooks).

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

## 3. Status: 12 of 21 stages complete

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
| 13 | **Ontology-KG** | `stage-13-ontology-kg` | **← NEXT** |
| 14–15 | Eval-AI-Cache · Performance (Redis, token economics) | | not started |
| 16–19 | Governance/Control · Observability · AI Security · Compliance | | not started |
| 20–21 | Implementation (app, LAST) · Documentation | | not started |

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

## 7. Tech stack (ADR-001 + ADR-009 Azure)

| Concern | Choice |
|---|---|
| Orchestration | **LangGraph** on **Azure Container Apps** (AKS if scale demands) |
| LLM inference | **⚠️ OPEN:** Route A = **Claude via Azure AI Foundry (recommended)**; Route B = Azure OpenAI. Route A keeps the model variable fixed while the platform changes. **Confirm before Stage 20.** Verify region availability at implementation time |
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
| **ADR-009 §Open** | **LLM route: Azure AI Foundry (Claude) vs Azure OpenAI** | Stage 14 eval baselines, Stage 20 |
| NAB-2 | `plans/active/` empty while method doc says specs go there. Recommended fix: **correct the method doc** (prompts already are the spec; duplicating violates "nothing written twice") | Doc accuracy only |
| NAB-3 | Copy V2's `knowledge/` (32 docs) + `evaluation/` fixtures locally, or keep as cross-repo reference? | Stages 13, 14 |
| NAB-4 | **`eval-ai-cache/` (29 files) is entirely unconsumed** — 24-part brownfield-evals runbook + Redis + OpenTelemetry runbooks. Stages 14/15/17 must draw on it, not re-derive | Stages 14, 15, 17 |
| EAB-6 | Token/cost budgets still Unknown — first measured in the interim state | Stage 15 |
| **S09-D1** | **ADR-009 absent from `decision_index.md` and `architecture_review.md`** (both still state "8 ADRs"). Traceability defect, not a design defect — review verdict `pass` stands | Stage 21 defense pack |

**Closed:** EAB-2 (air-gap → cloud-connected confirmed), EAB-3 (approvers named), NAB-1.

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

---

## 10. Working style established in this project

- Ground claims in **evidence with file paths**; classify fact / derivation / assumption / question.
- Mark artifact status honestly (`provisional` vs `stable`) rather than overclaiming.
- **Flag disagreements and errors openly** — the ADR-003 correction is the precedent.
- Record known limitations rather than papering over them (e.g. ADR-007's air-gap note).
- Don't add scope without a stated requirement (V2 workflows D/E were explicitly rejected).
