# DMAIC Lens — Stage 10 (Agentic Architecture)

**Thin lens** (Improve + Control focus, per `prompts/14_agentic_architecture.md`).
Governed by `docs/quality/dmaic-lean/` — the consolidated registers, not the per-stage copies.

## Define

The design question at graph granularity: **which structure exists specifically so that
splitting one governed decision across multiple turns cannot produce an outcome the
single-shot V1 design could never have produced?** Answer: the two-LLM-node / nine-
deterministic-node ratio, and the absence of any edge from generated text to a caller that
does not pass the guard, the Critic, the guard again, and a human.

## Measure

Architectural counts for this graph, all derived from the design (none measured — no run has
happened):

| Metric | Value | Note |
|---|---|---|
| LLM nodes | **2** of 11 | Synthesis + Critic. Every control is deterministic |
| Legal LLM calls per run, happy path | **2** | Cap is 6 (G1) |
| Structural caps set numerically | **8** (G1–G8) | Derived from graph shape, not measurement |
| Safety ceilings set numerically | **3** (C1, C2, C4) | Provisional; replaced by measured budgets at Stage 15 |
| Guard invocations per run | **2** | Both sides of the Critic |
| Container/component crossings, common path | **7** — unchanged | Matches the C4 baseline; this design added no hop |
| Agents | **4** | Exactly DDD §10; none added |

The hop count matching 7 is the one worth stating: the graph could easily have added a hop
(a planner, a policy re-check per node) and did not. Interim assumption 7 now has something
specific to test.

## Analyze

**Which waste does multi-agent splitting actually remove, vs. risk adding?** The prompt asks
this directly, and the honest answer is *less than the framing suggests*.

| | Assessment |
|---|---|
| **Removes** | **Non-utilised talent (N1)** — real: three prohibition sets held by three specialists rather than one generalist. **Defects (D1)** — real, but the removal comes from the *deterministic* nodes and the schema, not from having multiple agents |
| **Adds** | **Token (AI-1)** — the Critic doubles the LLM calls on the happy path, from 1 to 2. That is a **100% increase over a single-shot design** for the verification benefit. **Context (AI-7)** — the Critic needs the draft plus the evidence set serialized to it. **Transportation (T1)** — two extra component crossings vs. a single-shot call |

**So: the multi-agent split is a net cost in three waste categories to buy one defect
control.** That trade is defensible only because the defect it controls is the highest-severity
one in the register (a prohibited terminal action in a GxP/PV system) — and it is worth
recording plainly rather than presenting multi-agent architecture as a free improvement. It is
not. If interim assumption 6 shows the Critic pass is a large share of run cost, the honest
options are a cheaper Critic model or a risk-tiered Critic, **not** removing the check.

**Where the real improvement actually came from.** Not from the agents: from making the
controls deterministic. Nine of eleven nodes cannot hallucinate, and the four prohibited-field
sets cannot be represented at all. A single-shot design with the same schema and the same gates
would capture most of the safety benefit — what multi-agent adds is the *verification* step and
per-context specialization.

**Two design choices that removed waste rather than adding it:**
- **No planner agent** (`agent_roster.md` §4) — a plan that is a constant does not need a model
  to derive it. Avoided one LLM call and one state re-serialization per run.
- **Critic scope strictly complementary to the deterministic gates** (BC-6) — the Critic does
  not re-check what a type or a lookup enforces, which would have been designed-in token waste
  on every run (register row E3).

## Improve

The graph is the Improve artifact. What it implements from `build_constraints_from_lean.md`:
**BC-1** (guard day one, twice per run), **BC-2** (status filter inside the retrieval tool),
**BC-4** (agents designed against an ontology contract, not raw RAG), **BC-5** (closed reason-code
enum; no retry without a diagnosis), **BC-6** (Critic complementary), **BC-7** (budget counters
in the base state schema — emitted from the first run, not retrofitted), **BC-9** (single
shared state), **BC-11** (no cross-graph edge, condition, or field), **BC-12** (timeout ⇒ no
action; `approver_roles` as a list so Supply's dual approval is representable).

## Correction record

**Found by cross-verification, not by initial design review.** The original edge table in
`langgraph_design.md` §2 routed a first-occurrence `PROHIBITION_ADJACENT` Critic verdict to
`synthesize` (the generic "new reason code ⇒ retry" rule), contradicting
`failure_and_loop_guards.md` §4's explicit rule that this code must go straight to `blocked`,
never retried. Since `PROHIBITION_ADJACENT` can only be assigned when `guard1`'s pattern match
already missed the draft, the uncorrected routing would have let the graph ask the model to
retry — i.e., rephrase — a near-miss on the highest-severity control in the system, on exactly
the runs where the cheaper deterministic layer had already failed. **Fixed**: `critic_verify`
now has an unconditional `PROHIBITION_ADJACENT ⇒ blocked` edge, checked before the retry and
escalate branches. Recorded here per this programme's standing practice of flagging and fixing
errors openly rather than quietly (the ADR-003 precedent, `docs/adr/dmaic_lens.md`).

## Control

Loop guards and budgets as Control metrics, not hopes — `failure_and_loop_guards.md` §7 lists
the counters and alert thresholds. The three that matter most:

1. **`cap_exceeded` / `ceiling_exceeded` = zero.** Non-zero means a structural cap did not
   hold, which is a graph defect, not a cost event.
2. **`abstention_rate` alerting on a *drop*.** A system that abstains less is not improving; it
   is getting less cautious. This is the metric most likely to be misread as good news.
3. **`ProhibitedActionBlocked` = zero, with the caveat that zero proves nothing** until
   Stage 18 deliberately triggers it (interim assumption 1).

**Revisit triggers added by this stage:**

- If the Critic pass proves a large share of measured run cost (U1), revisit *Critic model
  choice or risk-tiering* — never Critic removal.
- If `no_progress` terminations are common, the reason-code enum is too coarse; widen it before
  loosening G2.
- If PV's reporting-clock reconstruction cannot be expressed as either a tool node or a
  synthesis node (a gap flagged openly in `langgraph_design.md` §7), the base state schema
  needs revisiting at 20b — the first concrete test of RR-2.
