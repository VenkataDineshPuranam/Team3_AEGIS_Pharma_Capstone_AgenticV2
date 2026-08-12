# Prompt 23 — Compliance (EU AI Act, ISO 42001)

**Maps to:** STAGES.md Stage 19 (`stage-19-compliance`)
**Lifecycle stage:** Verify (compliance)
**Framework derived:** V3 addition.
**Core question:** Does the system satisfy the applicable EU AI Act obligations and ISO 42001 AI management system requirements, with evidence?
**Prerequisites:** Prompts 04/14/20/22 (domain boundaries, agent design, governance, security) — compliance is verification, not new design.

---

## Produce

1. **EU AI Act risk classification** — classify each of the three governed workflows (GxP batch review, PV intake, supply planning) under the Act's risk tiers; state the reasoning (decision-support only, no autonomous terminal action — per the DDD prohibited-action boundary) and obligations that follow (transparency, human oversight, technical documentation, logging).
2. **ISO 42001 control mapping** — map this repo's actual artefacts to ISO 42001 AI management system clauses (e.g. risk management → `security/threat-models/`; data governance → `docs/product/discovery/discovery.md`; human oversight → `docs/governance/hitl_control_model.md`).
3. **Gap assessment** — obligations/clauses with no corresponding artefact or control yet; owner and target stage/branch to close each gap.
4. **Compliance evidence index** — links into `evidence/ai-assisted-changes/` and other `evidence/` subfolders proving each control actually operated (not just documented).

### Lean / DMAIC lens (thin — this stage is Control/verification, not new Improve)

1. Which compliance gap, if any, traces back to a Control action promised earlier (Prompt 09/12/20) but not yet closed?

---

## Exit criteria (handoff to Prompt 20/13's final defense pack)

- [ ] Risk classification is stated with reasoning, not asserted.
- [ ] Every ISO 42001 clause in scope has a mapped artefact or an open gap with an owner.
- [ ] Compliance evidence index links to actual `evidence/` records, not just plans.

---

## Constraints

- Do not classify a workflow as lower-risk than its actual decision-support scope to avoid obligations.
- Do not claim a control operates without pointing to `evidence/` proof.

---

## Output

Write under `docs/governance/compliance/`, `evidence/` **and mirror** to `workshop/participant-output/23-compliance/`:

- `eu_ai_act_risk_classification.md`
- `iso42001_control_mapping.md`
- `gap_assessment.md`
- `compliance_evidence_index.md`
- `dmaic_lens.md` (thin)
