# Threat Catalogue — Stage 18

**Executes:** `prompts/22_ai_security_threat_modeling.md` §1
**Consumes:** `langgraph_design.md` (graph shape), `tool_contracts/*.schema.json` (Stage 11),
`kg_schema.md` (Stage 13), the running Stage 20a code (`services/`, `packages/`)
**Artifact status:** `stable` for `batch_review`; threats specific to PV/Supply (multi-agent
handoff, cross-workflow) are named but marked `not yet buildable` — those graphs don't exist

---

## 0. What's different now: this is the first security stage with a system to attack

Every threat below is checked against the actual Stage 20a code, not just the design. Three
threats (T-01, T-06, T-09) were **actually exercised**, not just modeled — see
`abuse_cases/` and `residual_risk_register.md` §2 for what that produced, including one real
control gap (T-09) found and fixed during this stage, not merely catalogued.

## 1. Threats

| ID | Threat | Entry point | New because multi-agent/tool-using? |
|---|---|---|---|
| **T-01** | Indirect prompt injection via a downstream free-text field | `batch_reconcile`'s `gap_description` (confirmed reaches the synthesis prompt — `content_excerpt` confirmed it does NOT) | Yes — V2's single-shot app had no tool-output-to-prompt pipeline for an agent to reason over |
| **T-02** | Direct prompt injection (attacker controls the request itself) | `intake` — the `requester_role`/workflow fields | No — exists in any LLM-facing system, not multi-agent-specific |
| **T-03** | Tool abuse / excessive agency — a node calls a tool outside its authorized scope | Any MCP-shaped call in `services/integration/` | Yes — a single-shot app has no tool-calling surface at all |
| **T-04** | Cache poisoning | N/A — no cache exists in 20a (Stage 15 deferred it to 20b) | Would be, once built |
| **T-05** | Agent-to-agent trust exploitation (a downstream agent trusts an upstream agent's output uncritically) | Synthesis → Critic handoff | Yes — this is exactly why the Critic re-checks rather than trusting `synthesize` |
| **T-06** | Evidence-authority bypass — citing `untrusted`/`superseded` content | `evidence.retrieve` | Yes — V2 had a flat document store, not a status-gated retrieval tool an agent queries |
| **T-07** | Memory/context poisoning across runs | N/A — no cross-run agent memory exists (`memory_design.md` §2, deliberate) | Would be, if that design decision were ever reversed |
| **T-08** | Stale-authorization replay (a request judged against an old policy version) | `policy_contract_version` field, `evidence.retrieve`/`batch.reconcile` | Yes — only meaningful once multiple policy versions exist; 20a has exactly one (`v1`) |
| **T-09** | Data exfiltration via tool output — PII/PHI or credentials leaking through a trace or response | Any span (`tracing_design.md`), any tool response | Partially new — the redaction design (Stage 17) exists but has no PII source to redact yet in `batch_review` (PV is where PHI actually lives) |
| **T-10** | Supply-chain compromise — a dependency (Neo4j driver, `anthropic`/`openai` SDKs, MCP servers) is compromised | Any external package | Not multi-agent-specific, but the blast radius is wider (one compromised dep reaches every node) |
| **T-11** | Denial-of-wallet — unbounded run volume/cost | `intake` (admission) | Yes — a single-shot app has one call per request; an agent loop can retry itself into real cost, which is exactly what Groq's unreliable Critic demonstrated this session (6 LLM calls on a single request, hitting G1) |
| **T-12** | Cross-graph authority leak (an agent bound to one workflow reaches another workflow's data/tools) | Server-credential boundary (`rbac_model.md` §4) | Yes — this is precisely the multi-agent failure mode ADR-004's context names (`discovery.md` §9 H5) |

## 2. Threats not yet buildable (PV/Supply don't exist)

| ID | Threat | Why deferred |
|---|---|---|
| T-13 | PV duplicate-check gaming (submitting near-duplicate cases to evade dedup) | `pv_intake` graph unbuilt |
| T-14 | Supply option-ranking manipulation via poisoned constraint data | `supply_planning` graph unbuilt |
| T-15 | Supply's dual-approval bypass (one leg approves, attacker forges the second) | No Supply HITL implementation exists to attack |

Recorded here so Stage 20b's red-team pass has a starting list rather than starting cold.
