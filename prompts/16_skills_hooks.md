# Prompt 16 — Skills & Hooks

**Maps to:** STAGES.md Stage 12 (`stage-12-skills-hooks`)
**Lifecycle stage:** Design (agent capability packaging)
**Framework derived:** V3 addition — Claude Code skills/hooks conventions.
**Core question:** What reusable skills do agents draw on, and what lifecycle hooks enforce governance outside agent prompting?
**Prerequisites:** Prompt 14 (agent roster), Prompt 15 (tool contracts).

---

## Produce

1. **Skill index** (`.claude/skills/skills.md`) — one skill per reusable capability (e.g. "grade evidence provenance," "run release-gate check"), each with trigger condition and which agent(s)/stage(s) use it.
2. **Hook index** (`.claude/hooks/hooks.md`) — one row per lifecycle hook (pre-tool-call, post-tool-call, session-start, etc.), each stating the governance control it enforces (must link to `docs/governance/` or `security/policies/`) and confirming it does **not** depend on agent prompt compliance alone.
3. **Skill vs hook boundary** — explicit rule for when a behavior belongs in a skill (agent-invoked, advisory) vs a hook (system-enforced, cannot be skipped by the agent).

### Lean / DMAIC lens (thin)

1. Which hook removes a Human-review or Evaluation waste category by automating a check that was manual?
2. Which skill removes Token/Context waste by packaging a reusable retrieval/formatting pattern instead of re-deriving it per agent turn?

---

## Exit criteria

- [ ] Every governance-critical control (prohibited decision, PII redaction, HITL gate) is implemented as a **hook**, not only described in a skill or system prompt.
- [ ] `.claude/skills/skills.md` and `.claude/hooks/hooks.md` are non-empty and cross-reference `docs/governance/`.

---

## Output

Write under `.claude/skills/skills.md`, `.claude/hooks/hooks.md` **and mirror notes** to `workshop/participant-output/16-skills-hooks/`:

- `skills.md`
- `hooks.md`
- `skill_vs_hook_boundary.md`
- `dmaic_lens.md` (thin)
