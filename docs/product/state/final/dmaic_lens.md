# DMAIC Lens — Stage 07 (Final State)

**Thin lens** (Improve focus).

## Define

Specify the target end-state precisely enough that "done" is testable rather than a matter
of opinion — and so that the gap between interim and final is a known, sequenced delta
rather than an open-ended build.

## Measure

The final state's completion is measured by seven hard gates (`final_state.md` §5), not by
feature count. Two of them (EAB-2, EAB-3) are **currently open and outside this programme's
control** — they need sponsor/user input. That is the single most important measured fact
about the final state today: **it cannot be declared complete regardless of how much
building happens, until two questions are answered by a human.**

## Analyze

Which waste does defining the final state this way prevent?
- **Overproduction** — §6's explicit out-of-scope list (no write integrations ever, no
  workflows D/E, no cross-workflow chaining) prevents scope creep that would otherwise be
  rationalized later as "we're already close."
- **Defects** — gates 6 and 7 make zero-prohibited-action findings and real compliance
  evidence completion conditions, so neither can be quietly deferred.

Specifically analyzed and rejected: adding V1's workflows D/E (clinical trial, discovery
science). They appear in V1's eval datasets (`S13`, `S14`) but V1's own mandate names three
mandatory workflows; the extras came from a prior participant run. Including them would be
scope expansion without a requirement — textbook Overproduction.

## Improve

The final-state definition is the Improve artifact. Its most substantive contribution is
**making incompleteness explicit**: rather than describing an idealized end-state, it names
the two human-input blockers (EAB-2, EAB-3) and four unratified ADRs that stand between the
current design and a defensible final system. A final-state document that omitted those
would be more comfortable and less true.

## Control

Revisit triggers:
- If EAB-2 resolves toward a hard air-gap requirement, this document is materially wrong and
  must be rewritten alongside a reopened ADR-001.
- Interim-state assumption 6 (token cost) landing far off expectation should revise §3's
  agent topology before Stage 20 builds it.
- Gate 2 (named approvers) must be verified at Stage 16, not assumed satisfied by then.
