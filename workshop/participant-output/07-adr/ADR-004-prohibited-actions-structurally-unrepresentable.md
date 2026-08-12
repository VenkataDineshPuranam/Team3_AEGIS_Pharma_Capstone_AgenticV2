# ADR-004 — Prohibited terminal actions are structurally unrepresentable, not merely disallowed

**Status:** `accepted`
**Evidence basis:** Fact (V2's prohibited-action lists are verbatim in
`case/INTEGRATED_CASE.md` §4 and `CLAUDE.md`) + derivation (multi-agent authority-leak risk,
`discovery.md` §9 H5).

## Context

Each workflow has a distinct prohibited terminal action: batch release/reject/reprocess/
relabel/recall (A); final seriousness/causality/expectedness/reportability/signal
confirmation (B); inventory status change/reservation/allocation/shipment/recall (C). A
multi-agent design creates a failure mode a single-shot app structurally cannot exhibit —
authority leaking across an agent handoff (`discovery.md` H5).

The DDD Analyze step refined this: the risk is not "an agent decides to do the prohibited
thing," it is "**the data model lets it represent one**."

## Decision

Enforce prohibition at three independent structural layers, none of which is a prompt
instruction:

1. **Aggregate schema** — `Batch` has no release/reject field; `ShortageOption` has no
   allocation-quantity field; PV output has no causality/seriousness/reportability field.
   The prohibited output is not expressible in the type system.
2. **Tool capability** — the Supply-Planning MCP tool has no allocation/reservation write
   method; no container has any write integration to a brownfield source system
   (`c4_context.md`).
3. **Runtime guard** — the Governance/Policy Engine's Prohibited-Action Guard checks every
   agent output before it can pass the Critic/Verifier node.

## Alternatives considered

- System-prompt instruction only — rejected: fails exactly under the multi-agent handoff
  conditions this system introduces, and is untestable.
- Runtime guard only (no schema constraint) — rejected: a guard is a single point of
  failure; schema-level unrepresentability cannot be bypassed by a code path that forgets to
  call the guard.

## Drivers

GxP/regulatory non-negotiable; multi-agent authority-leak risk; testability.

## Consequences

- **Easier:** the highest-severity failure mode becomes a type error rather than a
  behavioral risk; eval assertions become concrete schema checks.
- **Harder:** three layers to maintain in sync; deliberate redundancy, not duplication to
  refactor away.
- **Riskier:** none — strictly narrowing.

## Guardrails

No future stage may add a field or tool method that makes a prohibited action
representable, "for completeness" or for a UI convenience.

## Validation

Stage 14 contract test asserting the implemented schemas structurally lack these fields; a
red-team attempt (Stage 18) to induce a prohibited output must fail at the schema layer, not
merely be refused by the model.

## Revisit triggers

Only if a workflow's regulatory boundary itself changes (would require re-reading
`case/REGULATORY_BOUNDARY_PACK.md` and a DDD revision first).
