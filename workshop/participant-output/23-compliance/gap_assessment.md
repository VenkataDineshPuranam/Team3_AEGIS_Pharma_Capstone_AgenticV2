# Gap Assessment (Stage 19)

**Executes:** `prompts/23_compliance.md` §3
**Rule:** every gap has an owner and a target stage/branch — no gap is left dangling without
one, per the exit criterion.

---

| ID | Gap | Owner | Target |
|---|---|---|---|
| **G-1** | EU AI Act risk tier is a reasoned classification, not a legal determination — whether this system is a "safety component" under Article 6(1) turns on the regulatory status of the products/processes it supports, which requires legal/regulatory authority this project doesn't have | Chief Quality Officer (AI-management-system owner, `hitl_control_model.md` §3) + external regulatory counsel | Before any real deployment; not a Stage 20b code task |
| **G-2** | Zero dependency supply-chain control (no lockfile, no pinning, no SBOM) — re-flagged from Stage 18's `residual_risk_register.md` §3, now also an ISO 42001 clause gap in its own right | Engineering/Platform | Before Stage 20b adds more dependencies |
| **G-3** | No incident-management procedure exists for this system (`evidence/incidents/` is an empty scaffold) — distinct from `AI_INCIDENT_RESPONSE.md` (K-004), which is domain reference material the system can *cite*, not this system's own operating procedure | CISO (`hitl_control_model.md` §3) | Stage 20b, before any real deployment |
| **G-4** | ~~`HumanOverrideRecorded` never written by the running graph~~ — **CLOSED this stage**: `hitl_interrupt` now writes it, verified against a real run | Engineering/Platform | Closed |
| **G-5** | No internal-audit procedure or schedule | Chief Quality Officer | Requires an operating organization; structurally premature before Stage 20b |
| **G-6** | No management-review cadence | Chief Quality Officer | Requires an operating organization; structurally premature |
| **G-7** | Dashboards (Stage 17) are designed, not populated — no live monitoring exists yet | Architecture owner | Stage 20b, once real traffic exists to monitor |
| **G-8** | PV Intake and Supply Planning have zero operational evidence — every compliance claim in this stage that cites "real evidence" is scoped to Batch Review only | Engineering/Platform | Stage 20b |
| **G-9** | Guard paraphrase-evasion (re-flagged from Stage 18) — a compliant model response that avoids literal banned terms wouldn't be caught by `prohibited_action_guard.py` | Governance & Oversight | Needs a design decision (semantic check vs. expanded list), not scheduled |
| **G-10** | Approver justification on `HumanOverrideRecorded` is a placeholder string — no real approver-input UI exists to capture an actual justification | Engineering/Platform (`apps/web`) | Stage 20b |

## What this stage did NOT find as a gap, worth stating explicitly

- **Human oversight structure itself** — fully real, verified against 99+ actual runs, not a
  gap.
- **Evidence-authority gating (ADR-003)** — real, verified via both Stage 18's red-team and
  this session's own contract tests.
- **Continual improvement discipline** — the one ISO 42001 clause this whole 19-stage
  programme has satisfied continuously, not just at this stage.
