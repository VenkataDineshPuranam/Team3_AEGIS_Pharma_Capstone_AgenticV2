# DMAIC Lens — Stage 06 (Interim State)

**Thin lens** (Analyze/Improve focus).

## Define

The improvement problem at transition granularity: going from zero implementation to a
three-workflow multi-agent system in one step would make every risky assumption fail
ambiguously. The interim state exists to isolate them.

## Measure

The interim state is where the programme's longest-standing **Unknown** baselines finally
become measurable — this is its main Measure contribution:

| Baseline | Status since | Becomes measurable at |
|---|---|---|
| Token/cost per workflow run | Unknown since Stage 01 | Interim state (assumption 6) |
| Actual hop count vs. the 7-crossing design | Designed at Stage 03, never measured | Interim state (assumption 7) |
| Eval pass rate | Unknown since Stage 01 | Interim state (Stage 14's harness) |
| Cache hit rate | N/A | **Not** the interim state — deliberately deferred |

## Analyze

Which waste does staging the work this way prevent?
- **Overproduction** — replicating an unvalidated agent pattern across three workflows.
- **Defects** — introducing cache (stale-authority risk) and agent-correctness risk
  simultaneously, making failures ambiguous.
- **Rework/Extra processing** — discovering after building three workflows that the token
  economics force a different topology.

Which waste does it risk *adding*? **Waiting** — the final state cannot begin in earnest
until the interim state's seven assumptions are tested. This is accepted as
business-required NVA: it is the same class as the HITL wait and the sequential prompt
pipeline, i.e. deliberate governance latency, not accidental delay.

## Improve

The staged transition *is* the improvement. The specific choices and what each treats:
- **One workflow first (Batch Review, on evidence)** — treats Overproduction.
- **Cache excluded until correctness is proven** — treats Defects/ambiguous-failure risk.
- **Prohibited-Action Guard present from day one** — the one thing explicitly *not* staged,
  because ADR-004's whole argument is that this control cannot be retrofitted safely.
- **Measure token cost before scaling** — treats the Token waste category that has been
  flagged as highest-magnitude since Stage 01 but never quantified.

## Control

Revisit triggers:
- If interim assumption 6 (token cost) comes in materially above expectation, Stage 07's
  final-state topology must be revised **before** Stage 20 builds it three times.
- If assumption 1 or 2 fails (prohibited-action or evidence-authority enforcement), that is a
  stop-the-line event — it invalidates ADR-004 or ADR-003 respectively, and the final state
  cannot proceed on the current design.
- The placeholder HITL approver must not survive into the final state; Stage 07's exit
  criteria must check this explicitly.
