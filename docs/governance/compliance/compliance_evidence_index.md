# Compliance Evidence Index (Stage 19)

**Executes:** `prompts/23_compliance.md` §4 — links to `evidence/` and other real records
proving each control actually operated, not just documented. Per this stage's own constraint:
**do not claim a control operates without pointing to proof.**

---

## 1. Real evidence that exists right now

| Control claimed | Proof | How to verify it yourself |
|---|---|---|
| Audit trail is written on every completed run (ADR-006) | `evidence/audit_store.sqlite3`, table `agent_run` — **99+ real rows** as of this stage, spanning Stage 20a's build and Stage 18's red-team | `sqlite3 evidence/audit_store.sqlite3 "SELECT COUNT(*) FROM agent_run"` |
| HITL decisions are recorded (BC-12, `escalation_override_log_design.md`) | `evidence/audit_store.sqlite3`, table `human_override_recorded` — populated starting this stage (Gap G-4 fix) | Same DB, `SELECT * FROM human_override_recorded` |
| Evidence-authority gating holds under real querying (ADR-003) | `tests/contract/test_evidence_retrieve_contract.py`, `tests/integration/test_interim_assumptions.py::test_assumption_2_*` — both run against the live Neo4j instance, not mocked | `pytest tests/contract/test_evidence_retrieve_contract.py -v` |
| Prohibited-action guard holds under a real attack (ADR-004 layer 3) | `security/abuse-cases/T-01_indirect_prompt_injection.md`, `tests/security/test_prompt_injection_red_team.py` | `pytest tests/security/ -v -s` |
| Fail-closed policy engine (ADR-005/BC-3) | `tests/unit/governance/test_governance.py::test_policy_engine_fails_closed_*`, `tests/integration/test_batch_review_graph.py::test_policy_engine_unreachable_refuses_closed` | `pytest tests/unit/governance -v` |
| Denial-of-wallet ceiling now actually admits/refuses runs (Stage 18 fix) | `services/api/graph.py` `intake`/`finalize`, `infra/policies/test_denial_of_wallet_guardrail.py` (module-level, 7/7) | `pytest infra/policies -v` — note: module test only; graph-integration proof is the fact `intake` now calls it, confirmed by the passing full regression suite |
| Traces are actually captured (Stage 17 design → real operation) | LangSmith project `aegis-pharma-v3` — real run IDs queried via the LangSmith API this session (e.g. `019ff9ed-...` runs for `finalize`, `hitl_interrupt`, `route_after_hitl`) | `smith.langchain.com`, project `aegis-pharma-v3`, or the LangSmith API |
| Knowledge graph reflects the real, SHA-256-verified `knowledge/` corpus | Neo4j AuraDB instance `f3509efd` — 32 `EvidenceItem` nodes, 1 `supersedes` edge, verified live this session | `packages/domain/kg/ingest.py`, or query the instance directly |
| Test suite as a whole | 108+ tests, `pytest tests/ -q` | Run it |

## 2. Evidence `evidence/` subfolders that remain empty scaffolds

| Folder | Status | Why |
|---|---|---|
| `evidence/releases/` | Empty | No release has happened — Stage 20a is an interim slice, not a release |
| `evidence/deployments/` | Empty | No deployment has happened — everything ran locally against dev infra |
| `evidence/incidents/` | Empty | Correctly empty — no incident has occurred; also no incident *procedure* exists (Gap G-3) |
| `evidence/operations/` | Empty | No operating organization exists yet |
| `evidence/requirements/` | Empty | Requirements evidence lives in `docs/product/discovery/` and the `prompts/` themselves — not duplicated here (NAB-2 precedent: don't write the same thing twice) |
| `evidence/security/` | Empty | Stage 18's real evidence lives in `security/threat-models/` and `security/abuse-cases/` — arguably `evidence/security/` should point there rather than duplicate; recorded as a documentation-organization note, not a new gap |
| `evidence/quality-gates/` | Empty | Real gate evidence is `quality/gates/release_gates.py` + `scorecard.md` (Stage 14) — same duplication note as above |
| `evidence/ai-assisted-changes/` | Empty | No process exists yet for logging which changes were AI-assisted vs. human — this entire project has been AI-assisted throughout (this session included), and there is no running log of that fact anywhere. Worth naming honestly rather than leaving implicit |

## 3. What this index does not claim

- PV Intake and Supply Planning have **zero rows in any evidence table** — every "real"
  claim in §1 is Batch Review only (Gap G-8, `gap_assessment.md`).
- Token-economics evidence exists but is **provisional** (Groq, not Claude) — see
  `interim_state_results.md`; not re-cited as if it were Route A evidence.
- Dashboards/alerting (Stage 17) have **no live evidence** — designed, not operating
  (Gap G-7).
