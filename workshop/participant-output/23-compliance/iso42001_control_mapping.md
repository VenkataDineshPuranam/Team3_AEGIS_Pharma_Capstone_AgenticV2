# ISO/IEC 42001 Control Mapping (Stage 19)

**Executes:** `prompts/23_compliance.md` §2 — map this repo's actual artifacts to ISO 42001 AI
management system clauses.
**Rule followed:** every row below points to a real artifact; where no artifact exists, the
cell says so and the gap is registered in `gap_assessment.md`, per the exit criterion "every
clause in scope has a mapped artefact or an open gap with an owner."

---

| ISO 42001 clause (representative) | Mapped artifact | Operating evidence (not just the doc) |
|---|---|---|
| **Context of the organization / interested parties** (4) | `docs/product/discovery/discovery.md`, `case/STAKEHOLDER_PACK.md` (V2, verified) | N/A — foundational/documentary clause, no runtime evidence expected |
| **Leadership / roles & responsibilities** (5) | `hitl_control_model.md` §3 (bounded-context owners), `control_ownership.md` (Stage 16, per-policy owners) | Roles are real (verbatim from V2's stakeholder pack), not invented — `hitl_control_model.md` §1 |
| **Risk management** (6.1) | `security/threat-models/threat_catalogue.md`, `residual_risk_register.md` (Stage 18) | **Real**: 3 of 12 threats actually attacked against the running system, not just modeled (`T-01`, `T-06`, `T-11` abuse cases) |
| **AI system impact assessment** | `eu_ai_act_risk_classification.md` (this stage) | Reasoned, not yet legally validated — see Gap G-1 |
| **Data governance** | `discovery.md`, `ontology.md`/`kg_schema.md` (Stage 13), `conflict_authority_rules.md` | **Real**: 32-doc `knowledge/` corpus SHA-256-verified and live-ingested into Neo4j (Stage 20a); K-006/K-007 supersession pair verified live |
| **AI system design & development controls** | `langgraph_design.md`, `failure_and_loop_guards.md`, `packages/domain/`, `services/` (the actual code, Stage 20a) | **Real**: 108+ tests, 3 real routing bugs found and fixed by exercising the running code |
| **Third-party/supplier relationships** | **No artifact.** `security/sbom/README.md` is an empty scaffold; no dependency pinning exists anywhere in this repo | **Gap G-2** — named in Stage 18's `residual_risk_register.md` §3 already, re-flagged here since it's directly an ISO 42001 clause, not just a security nice-to-have |
| **Resource management (compute, data, human)** | `docs/quality/performance/token_economics.md`, `denial_of_wallet_guardrail.py` | **Real, partially**: the guard exists and is now wired (Stage 18 fix); ceiling is in-process only, doesn't survive restart (residual risk, not a gap in the clause mapping itself) |
| **Human oversight** | `hitl_control_model.md`, `failure_and_loop_guards.md` §5 (four-tier ladder) | **Real**: `test_assumption_3` exercises the timeout path against a live model; 99 real `AgentRun` records, zero silent auto-completions |
| **Transparency & provision of information to users** | ADR-003 (citation requirement), `DecisionSupportOutput`'s `claims[].cites` | **Real**: every draft this session's tests produced carries citations traceable to real `evidence_id`s |
| **Incident management** | `evidence/incidents/README.md` (empty scaffold) | **Gap G-3** — no incident-response procedure exists yet; `AI_INCIDENT_RESPONSE.md` (K-004) is a real V2 knowledge doc the system can *cite* but the *organization's own* incident procedure for this system doesn't exist |
| **Logging / record-keeping** | `services/integration/audit_store.py`, `escalation_override_log_design.md` | **Real** — 99+ `AgentRun` records confirmed in `evidence/audit_store.sqlite3`. **Found and fixed this stage**: `HumanOverrideRecorded` had a schema and unit tests but was never actually written by the running graph (0 rows at start of this stage). `hitl_interrupt` now calls `write_human_override`/`write_hitl_expired`, verified against a real live run producing a real row. **Known simplification**: justification is a placeholder string — no structured approver-input surface exists yet (Stage 20b / `apps/web`) |
| **Monitoring, measurement, analysis, evaluation** | `dashboards.md`, `alerting.md` (Stage 17) | Designed, not populated — no live dashboard exists yet (`dashboards.md` §3 already states this honestly) |
| **Internal audit** | **No artifact.** No internal-audit procedure or schedule exists | **Gap G-5** |
| **Management review** | **No artifact.** | **Gap G-6** — no operating organization exists yet to conduct one; structurally premature, not neglected |
| **Continual improvement** | `dmaic-lean/` (Stage 09), every stage's `dmaic_lens.md` | **Real** — this is the one clause the whole programme's DMAIC discipline maps to directly, and it operates continuously (every stage this session added a Control section) |

## Clauses this system genuinely cannot satisfy yet, and why that's honest, not a failure

Several rows above (internal audit, management review, incident management) require an
**operating organization**, not more code or documents — this project has built the AI
management system's technical controls extensively, but there is no company running this
system yet to audit, review, or respond to an incident with. Recorded as gaps with the correct
owner (an org, not an engineer) rather than invented procedures with no one to execute them.
