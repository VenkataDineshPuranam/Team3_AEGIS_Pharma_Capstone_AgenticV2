# skills.md — Skill Index

**Executes:** `prompts/16_skills_hooks.md` §1
**Builds on:** `../../../docs/architecture/agentic/agent_roster.md`, `../../../packages/contracts/tool_contracts/`
**Artifact status:** `stable` for Batch Review skills; `provisional` for PV/Supply skills
(same split as `agent_roster.md` — RR-2)

---

## 0. Two categories, and why they're both "skills" in the same sense

A **skill**, per Claude Code's own convention (this repo's method scaffold), is a packaged,
reusable set of instructions loaded into a turn when a trigger condition is met — agent-invoked
and advisory, as opposed to a hook, which is system-enforced and cannot be skipped
(`skill_vs_hook_boundary.md`). Two distinct sets of "agents" draw on skills in this repo, and
both belong in this index because the pattern is identical even though the invoker differs:

| Category | Who invokes it | When it exists |
|---|---|---|
| **Runtime domain-agent skills** (§1) | The LangGraph `synthesize`/`critic_verify` LLM nodes designed in `../../../docs/architecture/agentic/langgraph_design.md` | Implemented at Stage 20; **designed, not built, here** |
| **Build-process skills** (§2) | Claude Code sessions carrying out later SDD stages (this one included) | Some are usable **today** — Claude Code already exists; nothing here waits on Stage 20 |

**No skill in either category performs a governance-critical check.** Every governance-critical
control (prohibited decision, PII redaction, HITL gate) is a **hook**
(`.claude/hooks/hooks.md`) — that separation is the whole point of §0 and is verified in
`skill_vs_hook_boundary.md`.

---

## 1. Runtime domain-agent skills

One skill per LLM-node usage pattern from `agent_roster.md` §2/§5. Each is a packaged prompt +
procedure the node's LLM call draws on — **advisory in the sense that a skill shapes what the
model attempts, never in the sense that its output is trusted without a hook checking it.**

| Skill | Purpose | Trigger condition | Used by (node) | Reads (per tool contract) | Status |
|---|---|---|---|---|---|
| `synthesize-batch-reconciliation` | Turn `batch.reconcile`'s structured findings into a citation-complete prose summary, flagging deviations/gaps in language a human reviewer can act on | `evidence_gate` passed and `reconcile` returned findings | `synthesize` (`batch_review` graph) | `batch_reconcile.schema.json` output | `stable` |
| `synthesize-pv-triage` | Prioritize/triage PV signals and produce terminology-normalization suggestions with confidence, never applying them | `evidence_gate` passed, `pv.duplicate_check` complete (hard ordering, DDD §7) | `synthesize` (`pv_intake` graph) | `pv_duplicate_check.schema.json`, `pv_normalize_terminology.schema.json` | `provisional` |
| `synthesize-supply-ranking` | Rank and explain candidate options **within** the constraint-filtered set `supply.generate_options` returns — never widen the set | `evidence_gate` passed and `generate_options` returned a non-empty set | `synthesize` (`supply_planning` graph) | `supply_generate_options.schema.json` output | `provisional` |
| `critic-verify-decision-support-output` | The judgement checks that require reading prose: every claim carries a resolvable citation, no claim exceeds its cited evidence, abstention is used where evidence is insufficient (`agent_roster.md` §5's "requires reading the argument" row) | Any `draft_output` with `guard_verdict = clear` | `critic_verify`, **one shared skill, all three graphs** | The common `DecisionSupportOutput` contract only — no workflow vocabulary | `stable` (Batch Review is the only graph that can currently produce a draft to verify) |

**Why the Critic uses one shared skill and the domain agents don't.** The Critic reasons only
over the common `DecisionSupportOutput` contract by design (`agent_roster.md` §2) — it never
needs workflow-specific vocabulary, so one skill genuinely covers all three graphs. A shared
domain-agent skill would recreate the generalist-agent problem DDD §10 explicitly rejected.

**None of these four skills references a tool contract shaped like a write.** All inputs are
the read-only outputs catalogued in `../../../packages/contracts/tool_contracts/` — a skill drawing on a
tool contract inherits that contract's `what_this_schema_cannot_express` guarantee for free; it
cannot ask a model to reason about a field that isn't there.

## 2. Build-process skills

Reusable procedures for the humans/Claude Code sessions carrying out Stages 12–21 of this SDD
programme. Named after the prompt's own two examples, plus the two more that fall directly out
of governing rules already in force. **Two of these are usable today** — they do not wait on
Stage 20, because Claude Code is the tool executing them, not the deployed system.

| Skill | Purpose | Trigger condition | Used by stage(s) | Usable today? |
|---|---|---|---|---|
| `grade-evidence-provenance` | Verify a claim in a stage artifact is backed by a real citation with the correct authority status — the same check `authority_grader.py` performs on V1 outputs, applied here to *this programme's own documents* rather than to the deployed system's outputs | Before marking any artifact `stable` that asserts a fact about V1 behaviour | 02, 04, 09–19 (any stage citing V1 material) | **Yes** — this is the exact discipline behind the ADR-003 correction (`docs/adr/dmaic_lens.md`) and the standing ADR-002 rule; formalizing it as a named, invokable skill makes it repeatable instead of ad hoc |
| `run-release-gate-check` | Execute the eval categories and gates defined in `quality/gates/` against a build artifact or, once it exists, a real run | Stage 14 eval harness invocation; Stage 12 (assurance) rollup | 14, 12, 21 | No — `quality/gates/` has no gate definitions until Stage 14 |
| `reconcile-dmaic-lens` | The exact procedure used to write `../../../docs/quality/dmaic-lean/lens_rollup.md` — read every prior stage's lens, merge findings, flag contradictions rather than silently picking one | Any future re-consolidation of DMAIC lenses (e.g. if Stage 20 forces revisiting Stage 09) | 09, and any stage that reopens it | **Yes** — the procedure exists in the Stage 09 artifact; this entry names it so it isn't re-derived from scratch next time |
| `verify-against-source-not-filename` | Before asserting V1 (or any external system's) behaviour, read the actual code/data cited, not the filename or a prior summary of it | Any claim of the form "V1 does X" | All stages that reference V1 material | **Yes** — this is the ADR-002 standing rule, named as a skill so it is invoked rather than remembered |

**`grade-evidence-provenance`, `reconcile-dmaic-lens`, and `verify-against-source-not-filename`
are usable immediately**, in the sense that a future Claude Code session working this repo can
be asked to "run `grade-evidence-provenance` on Stage 13's ontology claims" and the procedure
above is enough to execute it. **They are not implemented as loadable `.claude/skills/<name>/`
folders this stage** — see §3.

## 3. What this stage deliberately does not create

**No `.claude/skills/<name>/SKILL.md` folders exist yet**, for either category, even though
three of the four build-process skills are genuinely usable today. Two different reasons,
stated separately so neither is mistaken for the other:

- **Runtime domain-agent skills (§1)** cannot be materialized as real artifacts before the
  LangGraph nodes that load them exist — Stage 20, deliberately last. Creating them now would
  be exactly the kind of "designed reported as built" overclaim the programme's status-honesty
  rule forbids.
- **Build-process skills (§2)** *could* be materialized now — this is a genuine option, not a
  hard blocker like the runtime skills. Deferred anyway, to keep Stage 12's output matching
  what the prompt asks for (an index) rather than silently expanding scope into tooling nobody
  requested. **Flagged as a low-cost future improvement**, not a gap: the next session that
  needs `grade-evidence-provenance` repeatedly can promote it from this table to a real skill
  folder in a few minutes, using this table as the spec.

## 4. Cross-references

- Tool contracts a skill may read: `../../../packages/contracts/tool_contracts/`.
- Governance gate a workflow-touching skill runs under: `../../../docs/governance/hitl_control_model.md`
  (named approvers); `../../../docs/governance/` more broadly once Stage 16 populates it further.
- The boundary rule separating this file from `hooks.md`: `../skill_vs_hook_boundary.md`.
