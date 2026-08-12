# Prompt 20 — Governance & Control

**Maps to:** STAGES.md Stage 16 (`stage-16-governance-control`)
**Lifecycle stage:** Design + Build (control plane)
**Framework derived:** V3 addition, formalizing Prompt 04's rules/AI/HITL boundaries into an enforced policy layer independent of any single agent.
**Core question:** What stops an agent from crossing a governed boundary, enforced outside the agent's own reasoning?
**Prerequisites:** Prompt 04 (rules vs AI vs HITL), Prompt 14 (agent roster), Prompt 16 (hooks).

---

## Produce

1. **Policy register** — one entry per governed boundary (prohibited terminal decisions, PII handling, GxP write restrictions): the rule, which hook(s) enforce it, and the test that proves enforcement (link to Prompt 18 eval suite).
2. **HITL control model** — who (role) approves what, escalation path, and timeout/default-safe behavior if no human responds.
3. **Escalation & override log design** — how a human override is recorded, by whom, with what justification (audit trail requirement).
4. **Control ownership** — named owner per policy, revisit trigger (mirrors DMAIC Control from Prompt 09/12).

### Lean / DMAIC lens (thin — this stage *is* Control for the whole system)

1. Every policy here should trace to a Control action already flagged in Prompts 01/04/06/09/12 — consolidate, do not invent new ones without a traced root cause.

---

## Exit criteria

- [ ] Every prohibited-decision boundary (from DDD) has a policy entry, an enforcing hook, and a passing eval test.
- [ ] HITL timeout/default-safe behavior is defined for every interrupt point in Prompt 14's graph.
- [ ] Override log design exists and is auditable (feeds compliance evidence, Prompt 23).

---

## Output

Write under `docs/governance/`, `security/policies/` **and mirror** to `workshop/participant-output/20-governance-control/`:

- `policy_register.md`
- `hitl_control_model.md`
- `escalation_override_log_design.md`
- `control_ownership.md`
- `dmaic_lens.md` (thin)
