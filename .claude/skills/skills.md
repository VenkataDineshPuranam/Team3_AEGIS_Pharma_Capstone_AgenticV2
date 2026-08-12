# skills.md — Skill Index

Reusable Claude Code / agent skills for this repo. Populated in **Stage 12**
(`stage-12-skills-hooks`). Each row will link to a skill folder under `.claude/skills/<name>/`.

| Skill | Purpose | Used by stage(s) |
|---|---|---|
| _(none yet — scaffold only)_ | | |

## Conventions
- One skill per folder, with its own `SKILL.md` frontmatter (name, description, trigger conditions).
- Skills that call MCP tools must reference the tool contract in `packages/contracts/`.
- Skills that touch governed workflows (GxP/PV/supply) must declare which `governance-control`
  policy gate they run under (see `docs/governance/`).
