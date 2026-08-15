# Conversation Summary — Session Handoff

**Purpose:** paste/reference this file at the start of a new chat to restore full context of
*this session's* work without re-reading the transcript. For the living project-state doc
(updated every stage), see `PROJECT_SUMMARY.md` — this file is the narrative of how this
session got there: what was asked, what was decided, what was found, what's still open.

**Session scope:** Stages 09–15 of the 21-stage SDD build (started the session already past
Stage 08). Repo: `Project_AEGIS_Pharma_AI_FDE_Capstone_Workshop_Ready_v3_claude_Agentic`.
Working branch progression: `stage-08-graphical` → `stage-09-dmaic-lean` → ... →
`stage-15-performance-tuning` (current, **HEAD** — see §14 below, this branch has
**uncommitted work**). Stages 09–14 are committed and fast-forwarded through
`stage-21-documentation`; `main` deliberately NOT kept in sync (standing repo rule).

> ⚠️ **Immediate next action for a new session, before anything else:** Stage 15's five files
> exist on disk (`git status` on `stage-15-performance-tuning` shows them untracked) but were
> **never committed or mirrored to `workshop/participant-output/19-performance-tuning/`**. See
> §14 "Not yet done" for the exact commit/mirror steps — do this first, don't re-derive Stage 15
> content from scratch.

---

## 1. Stage 09 — DMAIC/Lean Workbook (`docs/quality/dmaic-lean/`)

User asked to run Stage 09. Produced 6 artifacts reconciling nine prior per-stage
`dmaic_lens.md` files and five register pairs into one governing set:
`lens_rollup.md`, `dmaic_plan.md`, `waste_register_downtime.md`,
`waste_register_ai_specific.md`, `build_constraints_from_lean.md`, `structural_reopen.md`.

**Key findings from reconciling, not just merging:**
- **24 distinct wastes merged, 11 still open.**
- **Mode = Measure-first**, not because framing is `hypothesis` (it's `decision-ready`) but
  because every real baseline (token cost, latency, eval pass rate, hop count) is Unknown —
  nothing has ever run.
- **Three findings no single prior lens contained:**
  1. Stage 01's stated precondition ("quantify token cost before locking agent topology") was
     **not met** — ADR-008 was accepted with cost still Unknown. Recorded as accepted debt
     (RR-1) with revisit trigger **T-3**.
  2. "Blind retry" (a Model-waste item) had lost its owner in the stage resequencing —
     reassigned to Stage 10 (BC-5).
  3. Ontology-vs-agent build ordering was resolved in practice (Stage 10 designs against a
     *contract*, Stage 13 fills it in) but never written down — now BC-4.
- **Structural gate: `cleared`** — no Improve action reopens C4/ADRs/contracts. Two
  *documentation* defects recorded instead: ADR-009 missing from `decision_index.md` and
  `architecture_review.md` (both still say "8 ADRs"); NAB-2 (`plans/active/` empty).
- **12 must-fix-before-build constraints (BC-1…BC-12)** became binding input to Stage 10, with
  a recommended task order: guard + state schema + graph isolation first.
- **10 revisit triggers (T-1…T-10)**, two stop-the-line (T-1/T-2 = interim assumptions 1/2).

## 2. Execution Plan (`plans/active/EXECUTION_PLAN.md`)

User asked to "also create an execution plan." Central structural finding: **Stage 09 put the
programme in Measure-first mode, but nothing becomes measurable until code runs at Stage 20.**
Resolution: **Stage 20 splits into 20a (Batch Review interim slice, no cache) → Gate M →
20b (PV + Supply + cache).** Stages 14/15/17/19 each get a design pass (before 20a) and a
measured pass (after). Wave 2 reordered so governance (16) and eval/observability design
(14/17) land before the slice runs. Named 5 human decisions, the binding one: **LLM route**
(ADR-009, Claude via Azure AI Foundry vs Azure OpenAI) must resolve before 20a, since design is
route-independent but measurements aren't (trigger T-6).

## 3. Stage 10 — Agentic Architecture (`docs/architecture/agentic/`)

Five artifacts: `agent_roster.md`, `langgraph_design.md`, `memory_design.md`,
`failure_and_loop_guards.md`, `dmaic_lens.md`.

**Design: 11 nodes, 2 are LLM nodes** (domain-agent synthesis + Critic/Verifier). Every control
is deterministic (schema, status lookup, pattern match, edge condition).

- **No planner agent** — the workflow sequence is a constant; a planner would be a new
  authority surface and pure token waste.
- **No long-term agent memory** — a remembered conclusion has no citable source/status; it
  would be a second, unaudited cache.
- **DMAIC lens states plainly:** the multi-agent split is a *net cost* in three waste
  categories (Token/Context/Transportation) to buy one defect control (the Critic doubles
  happy-path LLM calls, 1→2) — accepted because the defect is the highest-severity one in the
  register, not because it's efficient.
- **Numeric guards split into two kinds:** structural caps (G1–G8, derived from graph shape,
  set now) vs. safety ceilings (C1–C4, provisional placeholders) vs. performance budgets
  (deferred to Stage 15, need real data).
- Status split: `batch_review` graph `stable`; `pv_intake`/`supply_planning` `provisional`
  (RR-2 — designed by analogy, must be re-checked at 20b, not assumed to transfer).
- Two open gaps flagged honestly: HITL timeout **duration** not yet set; PV's reporting-clock
  reconstruction has no assigned node.

### 3a. Follow-up: HITL timeout implemented as a four-tier escalation ladder

User: *"implement the time out and it should move to higher authority at a later stage if we
can do it at that time."* Replaced the single placeholder deadline with **T0 (interrupt) → T1
(reminder) → T2 (conditional escalation) → T3 (expiry, no action)** in
`failure_and_loop_guards.md` §5. Key properties:
- Escalation only **widens** who may approve — never replaces the primary, never auto-approves.
- T2 only proceeds if **5 conditions hold at that moment** (E1–E5): an escalation role is
  named; that role has a **live** Entra assignment right now (not at submission); the draft is
  still guard-clear; the policy version is still current; the role's own authority actually
  covers the decision. Any failed condition → audit-logged skip, run stays with primary.
- **Supply's planning leg has no escalation role at all** — V1's stakeholder pack names none
  above the Supply Chain VP; inventing one was explicitly rejected. Supply's dual approval
  survives escalation intact (both legs still required).
- PV's advisory veto (Patient Safety Rep) sits outside the ladder — registrable at any tier,
  never overridden.
- PV's 24h expiry is a stated *principle* (never sit on a reporting clock), explicitly flagged
  as needing verification against V1's real PV clock material before being treated as final.
- State schema gained `hitl_tier`, `hitl_required_legs`/`hitl_approved_legs` (append-only),
  `veto_recorded`; `approver_roles` documented as append-only widening.

## 4. Cross-verification pass (user: "cross verify your work")

User asked: *"Is this the optimised solution? Do we have any blind spots till now, cross
verify your work."* Response:
- **Not "optimized"** — optimization requires measured alternatives; nothing has run yet. What
  exists is "defensible under uncertainty," not tuned.
- **Found and fixed a real bug** by comparing `failure_and_loop_guards.md`'s stated rule
  against `langgraph_design.md`'s actual edge table: a first-occurrence `PROHIBITION_ADJACENT`
  Critic verdict was routable to a retry (`synthesize`) instead of straight to `blocked`,
  contradicting the documented rule. Dangerous specifically because that code only fires when
  the cheaper `guard1` pattern-match has already missed a draft — retrying would ask the model
  to rephrase a near-miss on the system's highest-severity control. **Fixed**: added an
  unconditional `PROHIBITION_ADJACENT ⇒ blocked` edge, checked first. Recorded as a correction
  in `dmaic_lens.md` per the ADR-003 precedent (flag and fix errors openly).
- Named a softer, honest limitation: ADR-004's "structurally unrepresentable" claim is airtight
  for schema-absence layers (1–2) but **layer 3 (the guard) pattern-matches natural language**,
  which is inherently softer — not a defect, an honest limit, closed only by Stage 18 red-team.
- Listed already-tracked opens (nothing adversarially tested yet; U1 unmeasured; PV
  reporting-clock gap; LLM route open) and confirmed several things checked-and-consistent.

## 5. Stage 11 — MCP Tool Contracts (`services/integration/`, `packages/contracts/tool_contracts/`)

7 tool operations, 6 server registrations, **all read-only**. Key design decision: **one MCP
server per bounded context for `evidence.retrieve`**, with `scope` **absent from the input
schema entirely** (fixed at server-binding time, not agent-supplied) — applying ADR-004's
"don't rely on the caller passing the right value" one layer down, to tools.
`prohibited_write_enforcement.md` walks a 3-layer defense argument through a worked example on
`supply.generate_options`. Caching finding for Stage 15: "read-only ⇒ cacheable" is wrong for
`pv.duplicate_check` (data changes as new cases arrive) and `supply.generate_options` (depends
on the most volatile data in the system) — both marked do-not-cache-by-default.

**Operational-safety decision (repeated at every later stage touching `.claude/`):**
`.claude/mcp.json`'s `mcpServers` stays `{}`. These are registrations for the *deployed* V2
runtime (Stage 20), not this coding session — populating real commands now would make this
repo's own Claude Code session try to launch nonexistent processes on startup. User confirmed
mid-session: *"For mcp if we need we use the available mcps."*

## 6. Stage 12 — Skills & Hooks (`.claude/skills/skills.md`, `.claude/hooks/hooks.md`, `.claude/skill_vs_hook_boundary.md`)

Catalogued Stage 10's 9 deterministic nodes as hook bindings (session-start, pre-tool-call,
post-tool-call, pre-output ×2, on-interrupt, post-run) and named 4 runtime domain-agent skills
+ 4 build-process skills for the 2 LLM nodes.

**The rule this stage actually added:** no skill's output is ever the last check on itself —
every skill has a downstream hook checking its output's *shape*, never trusting the skill's own
reasoning. Worked counterexample: folding the prohibited-action check into the Critic's own
prompt (skip the separate guard hook) would fail, because it makes the system's
highest-severity control depend on a model resisting a jailbreak exactly once with no
independent check.

Named 4 build-process skills (`grade-evidence-provenance`, `verify-against-source-not-filename`,
`reconcile-dmaic-lens`, `run-release-gate-check`) — 3 usable today, deliberately not
materialized as real skill folders yet (flagged as a low-cost future promotion, not a gap).

Same operational call: `.claude/hooks.json` stays `hooks: {}`.

## 7. Q&A interlude — "what agents/skills/hooks/MCPs are we using?"

Answered with tables: **4 agent roles** (Batch-Review, PV-Intake, Supply-Planning,
Critic/Verifier — one Critic instance per graph, not shared), **8 skills** (4 runtime + 4
build-process), **9 hook bindings**, **7 MCP tools / 6 servers**. Clarified nothing is "live" —
all Stage 10–12 design, implemented at Stage 20. Also clarified this session has no project-level
MCP connections active (separate from the V2 design question).

## 8. "Why does the other team use only one agent?" comparison

User pasted another team's rationale for a single-loop design (agents do near-zero generative
work — annotation only — over a deterministic core; centralizing controls in one shared gateway
avoids drift risk). Before responding, **verified their specific technical claims against real
source** rather than accepting them at face value:
- Confirmed `trajectory_grader.py` and `tool_gateway.py` are real, in V1's own
  `submission/src/services/` — V1's actual reference app already has **two named agents**
  (`evidence-summarizer`, `duplicate-similarity-scorer`) behind **one shared gateway** handling
  authority limits, idempotency/replay, and disposition-write prohibition centrally.
- Found **no 25-step bound**, no `F7`, `T-013`, or `ADR-014` anywhere in V1's code — flagged
  these as the other team's own fork-specific artifacts, not shared V1 ground truth.
- **Rebutted the "duplicated fail-closed controls" risk using our own verified design**: our
  Governance/Policy Engine is one shared container (ADR-005), the Prohibited-Action Guard is
  one implementation shared as a compile-time template (`agent_roster.md` §6) — not duplicated
  per graph. Their agent-to-agent-messaging risk doesn't arise for us either, since ADR-008
  already forbids cross-graph calls structurally.
- **Honest concession:** their argument rests on their agents doing much less (pure annotation)
  than ours (real synthesis/triage/ranking) — a different premise, not a mistake on either
  side. Recommended we draft an ADR (like their apparent ADR-014) naming the trigger conditions
  under which a single-loop design would become sufficient for us too — **not yet done**, user
  said to continue with stages instead.

## 9. Stage 13 — Ontology / Knowledge Graph (`docs/architecture/ontology/`)

Departed from prior stages by reading V1's actual `data/*.csv` and `knowledge/*.md` directly
rather than working from prior-stage prose alone (the `grade-evidence-provenance` /
`verify-against-source-not-filename` skills, actually exercised for the first time).

- **NAB-3 half-resolved**: copied V1's `knowledge/` (32 policy docs) + `knowledge_catalog.csv`
  into this repo's own `knowledge/`, SHA-256-verified against the catalog's own hashes.
  `data/`/`evaluation/` fixtures stay cross-repo, left for Stage 14 (Overproduction argument).
  Not a reopening of ADR-002 — domain reference data, not application code.
- **17 classes, 14 edge types**, grounded against real V1 CSV schemas.
- **Two findings surfaced only by checking real data:**
  1. `SensitiveSegment` (pregnancy/minor case segments, restricted `access_group`) — a
     governance boundary DDD's original pass never named. Flows backward as a gap in a
     `stable` Stage 02 artifact, recorded honestly. PV-Intake Agent's evidence scope needs an
     access-group check nothing in Stage 10/11 currently models.
  2. `Deviation` has **no `batch_id` foreign key anywhere** in V1's own relationship model —
     Stage 20's `batch.reconcile` will need a defined matching heuristic, not a lookup.
- Semantic layer fills **BC-4** exactly: specifies what `evidence.retrieve`'s query terms
  resolve against (KG concept/relationship/text match, single-hop, bounded by context).
  `PortfolioProduct` is the one cross-workflow hub node — deliberately a **hop-terminator** so
  a naive second hop can't leak across workflows (enforced two independent ways).
- Conflict/authority rules all traced to an existing decision, none invented: ADR-003
  citability rule re-confirmed independently against real catalog data; `local_approved` docs
  fully citable within their jurisdiction, never subordinate to `Global` by jurisdiction alone;
  `supersedes` populated only from the catalog's own column (a filename, normalized once at
  ingestion), never re-derived from a document's own prose.

## 10. Stage 14 — Eval-AI-Cache (`eval-ai-cache/`, `quality/gates/`, `tests/unit/graders/`)

Full DMAIC stage (sets Measure/Control for the whole system). Different in kind from prior
stages: **wrote and actually ran real Python code**, not just markdown design.

- Consumed `eval-ai-cache/AI_FDE_Brownfield_Evals_Cursor_Runbook/` (gate-state vocabulary:
  PASS/FAIL/REVIEW/NOT_APPLICABLE/NOT_OBSERVABLE/THRESHOLD_NOT_DEFINED/BLOCKED_BY_ENVIRONMENT;
  hard/threshold/operational gate taxonomy) rather than re-deriving it (NAB-4/T-7).
- Verified V1's actual `submission/evaluation/graders/*.py` (8 real graders) and
  `tool_gateway.py` first, then **independently re-derived** grader logic against our own
  contracts (ADR-002 — pattern reuse, not code reuse).
- **63 real scenarios across 15 categories** (12 required + 3 agent-specific: wrong-handoff,
  loop-guard-trip, unauthorized-tool-call), grounded in real `knowledge/` IDs (K-999 fake PV
  rule, K-998 malicious deviation doc, K-006/K-007 supersession pair, real batch/case IDs).
- Graders are **self-contained** (no `apps/`/`services/` code exists yet) — each embeds the
  deterministic rule it checks, sourced from the specific Stage 09–13 document that defines it.
- **Ran the harness against itself before trusting it — found and fixed 7 real defects:**
  schema-loader path doubling; a `_check` helper treating documentary `note` fields as required
  matches; a replay counter that incorrectly incremented on plain replays (contradicting V1's
  own verified gateway behavior — fixed to match exactly); an adversarial fixture whose failure
  branch the grader had no way to actually produce (added an `actual_replay_detected` override
  parameter, plus a golden-path companion scenario); a gate-result flattening miss. All
  recorded in `scorecard.md` §2, not hidden behind the final clean run.
- **Category 13 (`agent_wrong_handoff`) is a regression suite** for the real
  `PROHIBITION_ADJACENT` bug fixed earlier this session — `AWH-01` asserts the fix holds.
- **Final run: 63 scenarios, 0 FAIL, 0 ERROR.** pytest: 60 passed, 4 skipped (each skip carries
  an honest reason — 2 `NOT_APPLICABLE` for the human-rubric category, 1
  `THRESHOLD_NOT_DEFINED` for the cost cap, 1 `BLOCKED_BY_ENVIRONMENT` for the LLM-route
  dependency — never silent).
- Cache design (`cache_design.md`): **not built**, per `interim_state.md`. Key refinement to
  Stage 11: `evidence.retrieve`'s cache key omits `policy_contract_version` (content doesn't
  depend on policy, only admission does — the idempotency key still needs it). Do-not-cache
  list enforced via an executable grader. 8/8 cache-correctness checks executed correctly,
  including the exact scenario the prompt names (a hit on `K-007` after it transitions to
  `superseded` is caught, not served).
- Release gates independently re-derived from our own ADRs/DDD invariants, not copied from
  V1's 10 gates — full traceability table in `release_gates.md`.

---

## 10a. Stage 15 — Performance Tuning (`docs/quality/performance/`, `infra/policies/`) — WRITTEN, NOT COMMITTED

All five files exist on disk on branch `stage-15-performance-tuning`; `git status` there shows
them **untracked**. No commit, no fast-forward to 16–21, no mirror to
`workshop/participant-output/19-performance-tuning/` has happened yet — that is the literal
first thing to do in a new session (see §14 for the exact list).

**Same honesty split as every measurement-dependent stage:** the prompt's exit criteria ask for
"actual measured numbers," but nothing has run (20a hasn't happened) — U1 (token/cost) and U2
(latency) are unchanged since Stage 01. Distinguished per document what's real vs. still Unknown:

- **`token_economics.md`** — the cost *model* (formula: 2 LLM nodes only, per
  `langgraph_design.md`) is real; **pricing is real and verified** — loaded the `claude-api`
  skill and pulled current Anthropic pricing (Opus 5 $5/$25 per MTok, Sonnet 5 $3/$15,
  confirmed Azure AI Foundry/ADR-009 Route A bills at the same first-party rates) rather than
  recalling stale numbers. **Actual token volume per run is still Unknown.** Recommended (not
  decided) starting model for 20a: Sonnet 5, on cost/capability fit — Opus only if quality
  doesn't clear the bar. Ceilings restated as worst-case dollar bounds (C1=150k tokens →
  ≈$2.25/run on Sonnet), explicitly not a typical-cost estimate.
- **`redis_tuning.md`** — **actually read** the pre-seeded
  `eval-ai-cache/.../Windows Cursor Redis Caching Runbook.docx` (NAB-4/T-7, previously
  unconsumed) in full via docx XML extraction. Key finding consumed: the runbook's own
  engineering-plane-vs-data-plane split (MCP is for a human/Cursor to *inspect* Redis at
  dev-time; the deployed app must use a **native Redis client**, never MCP, at runtime) —
  applied as a new rule for this system, distinct from Stage 11's domain-agent MCP tool
  servers (different use of "MCP" entirely, flagged explicitly so the two aren't conflated.
  Second finding: Stage 14's cache design never said *where in the pipeline* caching happens
  relative to the Prohibited-Action Guard/Critic — fixed: never cache a draft, only a
  guard-and-Critic-cleared response (no cache built yet, so this is a constraint for whenever
  synthesis-output caching is proposed, not implemented now). Cluster-failure alerting gap also
  found and fixed: correctness-on-failure was already specified (ADR-007, bypass to no-cache),
  but *alerting* on that bypass was never specified anywhere until this document.
- **`latency_budget.md`** — per-node ceilings from real Stage 10 numbers (G6/G7 timeouts,
  the 7-hop/3-sync-depth baseline from `c4/dmaic_lens.md`). p50/p95 targets explicitly deferred.
  Stated once, plainly, that HITL wait is out of scope for a "latency" budget — folding a
  governance timescale into a performance target would be a category error.
- **`denial_of_wallet_guardrail.md` + `infra/policies/denial_of_wallet_guardrail.py`** — the one
  Stage 15 deliverable that's actually **built and tested**, not just designed, because a
  worst-case ceiling (unlike a typical-cost target) needs no measurement — only already-ratified
  inputs. Derivation: `DAILY_RUN_CEILING=20` (reuses C4's hourly figure as a deliberately
  conservative daily backstop) × `MAX_TOKENS_PER_RUN=150,000` (=C1) × verified Sonnet 5 output
  price ($15/MTok) = **$45.00/user/workflow/day**. Two independent checks (run-count, spend),
  fail-safe direction matches ADR-005 (worst-case estimate by default, never a hopeful guess).
  **7/7 tests passing**, run this session (`tests/unit/policies/test_denial_of_wallet_guardrail.py`)
  — proves per-user/per-workflow isolation, daily reset, and that the ceiling actually trips, not
  just returns a number. Wired into `.claude/hooks/hooks.md` as a new **pre-tool-call** hook row
  at `intake`, explicitly marked as the only row in that table backed by a real executable + test.
- **`dmaic_lens.md`** (thin) — names *why* the guardrail could ship this stage while the cost/
  latency targets couldn't (worst-case bound vs. measured central tendency — same distinction
  `failure_and_loop_guards.md` §1 already drew for per-run guards, found to apply at the
  denial-of-wallet scope too).

## 11. Current state (as of end of this session)

- **14 of 21 stages fully committed and merged forward**; Stage 15 (Performance Tuning) is
  **written but uncommitted** on `stage-15-performance-tuning` — see §10a and §14.
- Last committed stage branch tip: `stage-14-eval-ai-cache` @ `a366bcd`.
- `PROJECT_SUMMARY.md` is kept current through Stage 14 only — it does **not** yet reflect
  Stage 15 (that update also didn't happen — fold it into the same next-session pass as the
  commit/mirror work).
- **Next stage after 15 is committed: 16 (Governance & Control)**.

## 12. Standing rules established or reinforced this session

1. **Never populate `.claude/mcp.json` or `.claude/hooks.json` with live entries** pointing at
   code that doesn't exist yet — would make this coding session itself try to launch/run
   nonexistent processes. Register for real only at Stage 20.
2. **Never claim another system's (V1's, or another team's) behavior without reading its actual
   code/data** — verify, don't infer from filenames or pasted descriptions. Caught real,
   consequential findings twice this session (V1's real agent/gateway shape; V1's actual grader
   patterns) and once nearly avoided a bad rebuttal (the other team's 25-step/ADR-014 claims).
3. **Flag and fix errors openly, immediately, when found** — the `PROHIBITION_ADJACENT` bug and
   the 7 eval-harness defects were fixed in place and recorded, not smoothed over.
4. **Status honesty**: never report "designed" as "measured," never fake a pass/fail result —
   use `NOT_APPLICABLE`/`THRESHOLD_NOT_DEFINED`/`BLOCKED_BY_ENVIRONMENT` rather than a guessed
   number or a silent skip.
5. **PV/Supply artifacts are `provisional` throughout** — designed by analogy to Batch Review,
   explicitly not assumed to transfer (RR-2), re-checked only when actually built at 20b.

## 13. Not yet done (raised, not actioned)

- ADR-009 still missing from `decision_index.md`/`architecture_review.md` (S09-D1, cosmetic,
  offered but not applied unless requested).
- No ADR yet documenting "why 3 agents, not 1" with named revisit triggers (raised in the
  other-team comparison, §8 above; recommended, not written).
- PV reporting-clock reconstruction has no assigned graph node (Stage 20 open item).
- LLM route (ADR-009 sub-decision) still open — blocks final baseline-taking at 20a.

## 14. IMMEDIATE next action for a new session — finish committing Stage 15

The repo is mid-stage. Do this **before** starting Stage 16 or anything else:

1. `git branch --show-current` should show `stage-15-performance-tuning`; `git status --short`
   should show these five untracked files (do not re-derive their content — read them, they're
   already correct and complete):
   - `docs/quality/performance/token_economics.md`
   - `docs/quality/performance/redis_tuning.md`
   - `docs/quality/performance/latency_budget.md`
   - `docs/quality/performance/denial_of_wallet_guardrail.md`
   - `docs/quality/performance/dmaic_lens.md`
   - plus `infra/policies/denial_of_wallet_guardrail.py`, `tests/unit/policies/test_denial_of_wallet_guardrail.py`
   - plus a **modified** `.claude/hooks/hooks.md` (new pre-tool-call row added — nine bindings
     became ten; confirm the diff is exactly that one added row before committing)
2. Re-run `python3 -m pytest tests/unit/policies/ -v` to reconfirm 7/7 before committing (should
   be instant — pure in-memory logic, no external deps).
3. Mirror all five `docs/quality/performance/*.md` files to
   `workshop/participant-output/19-performance-tuning/` (create the dir), fixing relative links
   the same way every prior stage's mirror step did (`sed` the `../../../` path rewrites — see
   any prior stage's mirroring commands in this repo's git log for the exact pattern used).
4. Update `STAGES.md` and `PROJECT_SUMMARY.md`: Stage 15 → stable (with the honest caveat: cost/
   latency *targets* remain Unknown pending 20a; only the denial-of-wallet ceiling is enforced
   and measured-in-the-sense-of-tested). Bump "X of 21 stages complete" to 15.
5. Commit (one commit, following this session's established message style — see `git log` on
   this branch for Stage 09–14's commit message shape: what was built, what was found/fixed,
   what's honestly still open, `Co-Authored-By: Claude ... <noreply@anthropic.com>` trailer).
6. Fast-forward stage branches 16–21 to the new commit:
   `for b in $(git branch --format='%(refname:short)' | grep '^stage-' | grep -vE '^stage-(0[1-9]|1[0-5])-'); do git branch -f "$b" stage-15-performance-tuning; done`
7. Then proceed to Stage 16 (Governance & Control) per `plans/active/EXECUTION_PLAN.md` — Wave 2,
   already-designed policy register content (`policy_register.md`, `hitl_control_model.md`
   extension, `escalation_override_log_design.md`, `control_ownership.md`) per
   `prompts/20_governance_control.md`.

Do **not** skip straight to Stage 16 with Stage 15 left uncommitted — every prior stage in this
session was committed and fast-forwarded before moving on; leaving one dangling breaks that
pattern and risks the work being lost or duplicated by a future session that doesn't know it's
there.
