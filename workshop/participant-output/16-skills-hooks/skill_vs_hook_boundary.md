# Skill vs. Hook Boundary — Stage 12

**Executes:** `prompts/16_skills_hooks.md` §3

---

## 1. The rule

**A behavior belongs in a hook if a governance failure would result from an agent choosing not
to do it — correctly or incorrectly, deliberately or not. It belongs in a skill if the worst
outcome of skipping it is a worse answer, not a governed failure.**

Equivalently, and more operationally: **ask whether the check must run even when the model that
would perform it is unreachable, degraded, adversarially prompted, or simply wrong.** If yes,
it's a hook — because a hook is a node the graph passes through regardless of what any LLM
call decided, versus a skill, which is content an LLM call *may* draw on and could in principle
ignore, misapply, or be steered away from.

This is not a new principle — it is `agent_roster.md` §5's Critic-scope rule ("if a check can
be expressed as a lookup, a type, or a pattern match, the Critic does not perform it")
generalized from "what the Critic does" to "what belongs in a hook at all."

## 2. The test, applied

Three questions, in order. The first `yes` decides it.

1. **Can this be expressed as a lookup, a type constraint, a pattern match, or a clock?**
   If yes → **hook**. (Evidence status, prohibited-action shape, HITL timeout, credential
   presence — all four pass this test, which is why all four are hooks in `hooks.md`.)
2. **If this step were skipped entirely, would a prohibited terminal action, a citation of
   non-citable evidence, an unauthorized write, or a silent auto-approval become possible?**
   If yes → **hook**, even if it also requires some judgement (in which case: a hook for the
   part that's a lookup, plus a skill for the part that requires judgement — see §3).
3. **Does getting this right require reading and weighing an argument (does this claim, in
   natural language, actually follow from the cited evidence)?**
   If yes and neither 1 nor 2 applied → **skill**, always paired with a hook that checks the
   *shape* of the skill's output afterward (§3).

## 3. The pattern that appears everywhere in this design: paired skill + hook, not either/or

The three highest-stakes checks in this system are **not** single-mechanism decisions — each
pairs a skill (for the judgement) with a hook (for the shape), and the pairing is the control,
not either half alone:

| Judgement (skill) | Shape check (hook) | Why both are needed |
|---|---|---|
| `critic-verify-decision-support-output`: does this claim actually follow from its citations? | `prohibited_action_guard`, run **after** the Critic returns a verdict | The Critic's own verdict is itself model output — trusting it unchecked would just move the "trust a model" problem one step later. The hook re-checks the *shape* of whatever the Critic approved, independent of whether the Critic's reasoning was sound |
| `synthesize-batch-reconciliation`: write a citation-complete summary | `evidence_gate` (post-tool-call) + `prohibited_action_guard` (pre-output, first pass) | The synthesis skill is asked to write well; it is never trusted to have avoided a prohibited-action shape or an uncited claim on its own — both are separately, deterministically checked |
| `synthesize-pv-triage` / `synthesize-supply-ranking`: prioritize / rank within a set | `hitl_route` → `hitl_interrupt` (100% routing, both workflows) | Even a perfectly-reasoned triage or ranking is never load-bearing on its own — the hook guarantees a human sees it regardless of how good the skill's output was |

**The general shape: no skill's output is ever the last check on itself.** Every skill in
`skills.md` §1 has at least one hook downstream of it in `hooks.md` §1 that does not read the
skill's reasoning, only its output's shape.

## 4. Worked misclassification — what it would look like to get this wrong

To make the boundary concrete rather than abstract, here is a plausible design that **fails**
the test, and why:

**Rejected design:** "Have the Critic's skill include an instruction to refuse if the draft
looks like a release/reject recommendation" — i.e., fold the prohibited-action check into the
`critic-verify-decision-support-output` skill's prompt, and skip the separate
`prohibited_action_guard` hook.

**Why it fails question 1 immediately:** whether a draft's *shape* matches a prohibited-action
pattern is a pattern match, not a judgement call — it does not need an LLM to decide, and
asking one to decide it anyway means the highest-severity control in the entire system (D1 in
`../../../docs/quality/dmaic-lean/waste_register_downtime.md`) would depend on a model correctly
following an instruction under adversarial pressure (a poisoned evidence document, a
jailbreak attempt) exactly once, with no independent check. This is precisely the H5 risk named
in Stage 01 (`docs/product/discovery/discovery.md` §9) and precisely what ADR-004 exists to
rule out. **The correct design keeps the guard as a hook, running before and after the skill,
and never asks the skill to be its own check.**

## 5. Verification against the actual index

Cross-checked, not asserted: every governance-critical item named in `hooks.md`'s own
pre-existing convention text — "blocking a terminal safety/release decision, redacting PII
before a tool call, requiring HITL sign-off before a high-risk tool executes" — has a **hook**
row in `hooks.md` §1 (`prohibited_action_guard`; the redaction binding; `hitl_route`/
`hitl_interrupt`), and **no equivalent row exists in `skills.md`**. This satisfies the exit
criterion directly: every governance-critical control is implemented as a hook, not only
described in a skill or system prompt.
