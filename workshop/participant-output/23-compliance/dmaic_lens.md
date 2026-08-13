# DMAIC Lens — Stage 19 (Compliance)

**Thin lens**, per `prompts/23`: this stage is Control/verification, not new Improve.

## Define

Which compliance gap, if any, traces back to a Control action promised earlier (Prompt 09/12/
20) but not yet closed? Answer: **G-4** (`HumanOverrideRecorded` never written by the running
graph) traces directly to `dmaic_plan.md`'s Control standard "audit-store write success = 100%
while LangSmith is healthy" — that standard was stated at Stage 09/17 but never checked against
the actual running graph until this stage did.

## Measure

10 gaps identified (G-1…G-10). **1 closed during this stage** (G-4, fixed and verified against
a real run). 2 structurally premature, not neglected (G-5, G-6 — no operating organization
exists). 1 is a legal question this project cannot close itself (G-1).

## Analyze

The pattern repeats from Stage 18: a control documented as "implemented" (schema +
unit-tested) had never actually been wired into the running graph. This is now the **second**
instance of the same root cause (Stage 18: denial-of-wallet; Stage 19: `HumanOverrideRecorded`)
— worth naming as a pattern, not two unrelated bugs: **unit tests of a standalone module prove
the module works, not that anything calls it.** Every remaining Stage 20b integration point
should get an integration-level test alongside its unit test, not instead of one.

## Improve

G-4 fixed directly in this stage (not deferred) — `hitl_interrupt` now writes
`HumanOverrideRecorded`/`HitlExpired`. Everything else recorded as a gap with an owner, per
this stage's own constraint against inventing scope beyond compliance verification.

## Control

- **New standing check, going forward**: before any stage claims a control "operates," it must
  point to a specific `evidence/` record or a passing integration test — this stage's own
  evidence index (`compliance_evidence_index.md`) is now the reference format for what that
  looks like.
- **Revisit trigger**: the moment PV Intake exists (Stage 20b), G-8 (zero PV/Supply evidence)
  must be re-evaluated — nothing in this stage's evidence transfers to those workflows
  automatically (RR-2, same rule as every other stage).
