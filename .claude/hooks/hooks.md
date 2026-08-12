# hooks.md — Hook Index

Lifecycle hooks bound in `.claude/hooks.json`. Populated in **Stage 12**
(`stage-12-skills-hooks`).

| Hook event | Purpose | Enforces |
|---|---|---|
| _(none yet — scaffold only)_ | | |

## Conventions
- Hooks are the enforcement point for governance rules that must never depend on
  agent prompting alone (e.g., blocking a terminal safety/release decision, redacting
  PII before a tool call, requiring HITL sign-off before a high-risk tool executes).
- Every hook must be traceable to a control in `docs/governance/` or `security/policies/`.
