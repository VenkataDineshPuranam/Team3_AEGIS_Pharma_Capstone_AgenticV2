# ADR-002 — V2 is built separately from V1, not on top of `submission/`

**Status:** `accepted`
**Evidence basis:** Fact (explicit user decision, this session) + derivation (V1 structural
constraints, verified below).

## Context

V1 contains reusable assets: a deterministic eval harness (9 graders, 14 scenario datasets,
release-gate policies under `submission/evaluation/`), a completed Next.js reference app
(`submission/app-advanced/`), and 4 JSON response contracts. The question was whether V2
should extend these or start clean.

V1's structure constrains reuse: `case/`, `data/`, `knowledge/`, `evaluation/`,
`requirements/`, `starter/`, `templates/` are hash-checked immutable challenge evidence
(`tools/verify_package.py` against `FILE_HASHES.csv`); only `submission/` is writable. So
"build on top" would specifically mean "build inside V1's `submission/`."

## Decision

**V2 is an independent codebase.** V1 is a read-only evidence and reference source only —
cited for domain facts, never imported as code. Nothing from `submission/` is reused.

## Alternatives considered

- **Extend `submission/`** — rejected. It would couple V2's LangGraph/MCP design to a stack
  chosen for a single-shot app and never validated against multi-agent needs, and it forces
  V2's branch-per-stage operational structure inside V1's single-participant workspace
  layout. The genuinely net-new work (orchestration, agent state, tool contracts) has
  nothing to reuse from V1 regardless; only ~20–30% peripheral material (fixtures,
  contracts, UI shell) would have transferred.

## Drivers

Avoiding legacy-stack coupling; incompatible repo paradigms; the core agentic work being
non-transferable either way.

## Consequences

- **Easier:** clean architecture unconstrained by prior choices; V2's structure stays
  coherent.
- **Harder:** V2 must rebuild eval-harness equivalents (Stage 14) and UI scaffolding
  (Stage 20) that V1 already had in some form.
- **Riskier — and this is the material one:** V2's domain model risks drifting from what
  V1's evaluation actually enforces, because nothing structurally ties them together.
  **This risk already materialized once** — see ADR-003, where verification found the DDD
  model had mis-stated V1's superseded-document rule.

## Guardrails

V1's immutable directories are never modified. V2 must not silently assume V1 behavior —
any V2 rule claiming to match V1 must cite verified V1 code or data, not a filename
inference.

## Validation

Stage 14's eval suite must cover the same 12 required categories as V1's
`evaluation/EVALUATION_PLAN.md` (as a floor), extended with agent-specific cases.

## Revisit triggers

If Stage 14 or Stage 20 finds that rebuilding a V1 asset costs materially more than
adapting it, re-open this decision for that specific asset rather than wholesale.
