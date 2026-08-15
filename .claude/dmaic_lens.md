# DMAIC Lens — Stage 12 (Skills & Hooks)

**Thin lens** (per `prompts/16_skills_hooks.md`). Governed by `docs/quality/dmaic-lean/` — the
consolidated registers, not a restart.

## Define

Which behaviors, formalized as skills vs. hooks, remove a named waste — and does the
skill/hook split itself remove waste or just relabel Stage 10's design?

## Measure

| Metric | Value |
|---|---|
| Runtime domain-agent skills catalogued | 4 (`stable`: 1, `provisional`: 3) |
| Build-process skills catalogued | 4 (3 usable today, 1 blocked on Stage 14) |
| Hook bindings catalogued | 9, covering all 11 Stage-10 nodes except the 2 LLM nodes themselves |
| Governance-critical controls with a hook (not just a skill) | **3 of 3** — guard, redaction, HITL (§5, `skill_vs_hook_boundary.md`) |
| Skills with no downstream hook checking their output shape | **0 of 4** (§3, boundary doc) |

## Analyze — the two Lean questions this prompt asks directly

**Which hook removes a Human-review or Evaluation waste category by automating a check that
was manual?** None of these hooks *automates a previously-manual check* — there was no prior
manual process, since V1 was single-shot and had no agent handoffs to check. What they do
instead is **prevent a waste category from being introduced in the first place** by the
multi-agent redesign: the `pre-tool-call` credential check and `post-tool-call` evidence gate
exist specifically because splitting evidence retrieval across bounded contexts *created* a
cross-context leakage risk V1 never had (register row D1/D2). This reframes the Lean question
correctly for this program: Stage 12's hooks are waste-*prevention*, not waste-*removal* —
there is no baseline process to have removed waste from.

**Which skill removes Token/Context waste by packaging a reusable retrieval/formatting pattern
instead of re-deriving it per agent turn?** `critic-verify-decision-support-output` is the
clearest case: one skill, shared across all three graphs, reasoning only over the common
`DecisionSupportOutput` contract. The counterfactual — three workflow-specific critic prompts,
each re-deriving citation-completeness logic in its own vocabulary — would be exactly the
Motion/Extra-processing waste `agent_roster.md` §2 already rejected when it chose one shared
Critic role over three. Packaging it as a named, versioned skill (rather than an inline prompt
fragment repeated per graph) is what keeps that design decision enforceable rather than just
stated.

## Improve

The four documents are the Improve artifact. What they implement:
**exit criterion 1** (every governance-critical control is a hook — verified, not asserted,
in `skill_vs_hook_boundary.md` §5); **exit criterion 2** (`skills.md` and `hooks.md` are
non-empty and cross-reference `docs/governance/`).

**A design choice this stage made that Stage 10 left implicit:** Stage 10's `langgraph_design.md`
already had nine deterministic nodes and two LLM nodes; this stage's actual contribution is
the **pairing rule** in `skill_vs_hook_boundary.md` §3 — no skill's output is ever the last
check on itself. That rule wasn't written down anywhere before this stage, even though Stage
10's design already followed it (the guard runs both before and after the Critic). Naming the
rule explicitly is what makes it a constraint on *future* design changes, not just an
observation about the current one.

## Control

**Revisit triggers added by this stage:**

- If any future skill is added without a downstream hook checking its output shape, that
  violates §3 of `skill_vs_hook_boundary.md` and should block merge, not just get flagged in
  review.
- `security/policies/` is cited by several hook rows as a forward reference with no content
  yet (Stage 16). If Stage 16 introduces a policy that a hook needs to check and no hook
  binding exists for it, that's a gap in *this* file to fix, not a reason for Stage 16 to
  invent its own separate enforcement mechanism (same non-duplication argument
  `prohibited_write_enforcement.md` §6 made for Stage 16 generally).
- The three build-process skills marked "usable today" (§2 of `skills.md`) but not yet
  materialized as real `.claude/skills/<name>/` folders are a standing, low-cost opportunity —
  not a defect. Worth promoting if any of them gets invoked by name more than once.
