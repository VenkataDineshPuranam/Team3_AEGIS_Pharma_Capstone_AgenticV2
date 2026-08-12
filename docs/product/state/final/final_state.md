# Final State — Target Agentic Architecture — Stage 07

**Executes:** `prompts/03_prd_vision.md` (target-state scope)
**Builds on:** Stage 06 interim state; DDD/C4/ADR (Stages 02–04)
**Artifact status: `provisional`** (inherits from DDD/C4; several elements below are
conditional on ADRs still marked `proposed`)

---

## 1. Definition of the final state

All three governed workflows — **GxP Batch Review, PV Intake, Supply-Shortage Planning** —
running as separate LangGraph graphs in a single deployment (ADR-008), each with its own
domain agent, Critic/Verifier, scoped evidence retrieval, and named human approver; under a
shared Governance/Policy Engine, Evidence & Provenance layer, Redis cache, LangSmith
observability, and owned audit store; with EU AI Act / ISO 42001 compliance evidence
produced from actual system operation rather than asserted.

## 2. What "done" means — target-state properties

Derived from V2's `case/INTEGRATED_CASE.md` §5 "required operating properties" (inherited
verbatim, not reinvented) plus V3's additions:

| Property | Inherited from V2 | V3-specific addition |
|---|---|---|
| Purpose limitation, least privilege, current authorization | Yes | Enforced per-agent via tool capability (ADR-004) |
| Evidence authority, temporal applicability, provenance | Yes | Deterministic status gate incl. `superseded` (ADR-003) |
| Structured outputs, abstention | Yes | Abstention on unretrieved evidence (ADR-007) |
| Human review | Yes | 100% routing for PV/Supply; default-safe timeout |
| Idempotency, bounded steps | Yes | Per-graph step/token budgets |
| Cost and token budgets | Yes | Measured, not estimated — carried from interim state |
| Checkpointing, rollback, kill switch | Yes | LangGraph checkpointing (ADR-001) |
| Degraded mode, AI-disabled continuity | Yes | Reframed as degraded-mode-safe (ADR-007) |
| Auditability | Yes | Owned audit store separate from traces (ADR-006) |
| — | — | **Multi-agent authority containment** (no cross-graph calls, ADR-008) |
| — | — | **Cache correctness** under supersession (ADR-003 guardrail) |
| — | — | **EU AI Act / ISO 42001 evidence** (Stage 19) |

## 3. Target architecture (summary — full detail in `docs/architecture/c4/`)

Nine containers per `c4_containers.md`: Web/Admin App, Orchestrator API (three graphs),
Agent Workers, MCP Tool Servers, Evidence & Provenance / Semantic Layer,
Governance/Policy Engine, Redis Cache, LangSmith (external), Audit/Evidence Log Store.

**Four domain agents** across three graphs: Batch-Review, PV-Intake, Supply-Planning, plus
a Critic/Verifier pattern applied within each graph.

**Four MCP tools:** Evidence Retrieval (shared, scoped per context), Reconciliation,
Duplicate-Check, Option-Generation — the last three each bound to one workflow, and none
carrying a write capability to any brownfield system.

## 4. Delta from the interim state

| Dimension | Interim | Final |
|---|---|---|
| Workflows | 1 (Batch Review) | 3 |
| Domain agents | 1 + Critic | 3 + Critic per graph |
| MCP tools | 2 | 4 |
| Cache | None | Redis, tiered TTL by risk, with cache-correctness evals |
| HITL approvers | Placeholder role | **Named accountable people (requires EAB-3 closed)** |
| Observability | Tracing only | Dashboards, alerting, SLOs (Stage 17) |
| Compliance | None | Risk classification + control mapping + evidence index (Stage 19) |
| Security | Design only | Threat model + negative tests executed (Stage 18) |
| Token economics | First measurement | Budgets enforced, denial-of-wallet ceiling (Stage 15) |

## 5. Conditions that must hold before the final state can be declared complete

These are hard gates, not aspirations:

1. **All seven interim-state assumptions passed** (`../interim/interim_state.md` §3). If
   assumption 1 or 2 failed, the design itself is invalid, not just incomplete.
2. **EAB-3 closed** — real named approvers exist for all three workflows. The placeholder
   must not survive; a governed system with an unnamed approver is not governed.
3. **EAB-2 resolved** — air-gap requirement confirmed or excluded. If air-gap is required,
   ADR-001 reopens and this final state is materially wrong.
4. **DDD and C4 upgraded from `provisional` to `stable`** — which conditions 2 and 3 enable.
5. **The four `proposed` ADRs (005–008) resolved to `accepted` or superseded** — a final
   state resting on unratified decisions is not final.
6. **Zero prohibited-action findings** across evals (Stage 14) and red-team (Stage 18).
7. **Compliance evidence produced from real runs** (Stage 19) — not documented intent.

## 6. Explicitly out of scope for the final state

- Any write integration to a brownfield source system — permanently, not "phase 2."
- Autonomous terminal decisions in any workflow — permanently.
- Cross-workflow agent chaining (ADR-008).
- Workflows D/E that appear in some V2 material (clinical trial context, discovery/
  translational science). V2's own mandate names **three** mandatory workflows; the extras
  seen in V2's eval datasets (`S13`, `S14`) were extensions from a prior participant run, not
  part of the required scope. V3 targets the three mandatory workflows only — adding the
  others would be scope expansion without a stated requirement.

## 7. Known risks carried into the final state

1. **Single-workflow generalization risk** (from interim §5.2) — Batch Review's shape may not
   transfer to PV's duplicate/clock semantics or Supply's option ranking. **This stage's
   mitigation:** each interim conclusion must be explicitly re-checked per workflow, not
   assumed to transfer. That re-check is a Stage 20 acceptance condition.
2. **Shared blast radius** (ADR-008, accepted residual) — one deployment serving all three.
3. **Vendor concentration** — V2's own source-system pack flags "bundled vendor, stale
   entitlements, weak cost controls" as a known organizational failure pattern; V3's stack
   (ADR-001) concentrates on Anthropic + LangSmith. Mitigation is the degraded-mode design
   (ADR-007), not vendor diversity — an honest limitation to record rather than paper over.

---

## Lean / DMAIC lens

See `dmaic_lens.md` (this folder).
