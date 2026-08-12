# C4 Level 1 — System Context — Stage 03

**Executes:** `prompts/06_c4.md`
**Builds on:** `docs/architecture/ddd/domain_model.md`, `context_map.md` (Stage 02)
**Artifact status: `provisional`** (inherits from DDD, per prompt rule: C4 inherits DDD's
status unless new evidence justifies an upgrade — no such evidence exists yet).

---

## The system

**AEGIS-PHARMA Agentic Decision-Support System (V3)** — a governed, multi-agent system
providing decision support (never terminal decisions) for GxP batch review, PV intake, and
supply-shortage planning.

## People / roles

| Role | Relationship to system | Status |
|---|---|---|
| QA Reviewer | HITL approver for Batch Review outputs | Named as a role type; real accountable person **TBD** (EAB-3) |
| PV Safety Physician / Qualified Person | HITL approver for PV Intake outputs (100% of causality/seriousness/reportability determinations) | TBD (EAB-3) |
| Supply Chain Lead | HITL approver for Supply Planning option sets (100%) | TBD (EAB-3) |
| Compliance/Risk Officer | Owns the Governance & Oversight policy contract | TBD (EAB-3) |
| FDE/Engineering team | Builds, operates, and extends the system across Stages 10–21 | This session's operator |

## External systems

Drawn directly from V2's `case/SOURCE_SYSTEM_FACT_PACK.md` (a real, if fictional, brownfield
landscape — "no system is universally authoritative"):

| External system group | Feeds which workflow | Integration direction |
|---|---|---|
| Manufacturing (ERP, MES, eBR, historian, PAT, warehouse) | Batch Review | **Read-only** — evidence source |
| Laboratory (LIMS, CDS, instrument PCs, notebooks) | Batch Review | **Read-only** |
| Quality (eQMS, document management, training, supplier quality) | Batch Review | **Read-only** |
| Safety (global safety DB, affiliate inboxes, vendor feeds, literature, call centre) | PV Intake | **Read-only** |
| Supply (serialization, logistics, cold-chain, CMO portals) | Supply Planning | **Read-only** |
| Existing AI platform (gateway, model endpoints, vector store, tools, evaluator — per `case/SOURCE_SYSTEM_FACT_PACK.md`'s "AI platform" domain row, noted as having "bundled vendor, stale entitlements, mutable manifests and weak cost controls") | Cross-cutting | **Not reused** — V3 is a deliberate replacement of this landscape's AI-platform row, not an integration with it (this session's explicit build-separate decision) |
| LLM provider (Anthropic Claude API) | All three core workflows | Outbound call — V3 depends on it; must have a documented degraded/AI-disabled path if unavailable (inherited V2 non-negotiable) |
| LangSmith | Observability/eval, cross-cutting | Outbound, hosted — **this is the concrete tension named in Stage 01 (EAB-2, offline-compatibility)**; see Boundary & Degraded Mode below |

**No external system in this list has a write integration.** Every arrow into V3 is
read-only evidence flow; every arrow out of V3 to these systems does not exist — this is the
system-level enforcement of the DDD prohibited-action boundary (`domain_model.md` §7's
schema-level constraint has a matching architecture-level constraint here: there is no
container in this system with outbound write capability to any brownfield source system).

## Context diagram (narrative)

```
[Manufacturing/Lab/Quality systems] ──read-only──┐
[Safety systems] ───────────────────read-only────┤
[Supply systems] ───────────────────read-only────┼──▶ ┌───────────────────────────────┐
                                                        │  AEGIS-PHARMA Agentic          │
[LLM provider (Anthropic)] ◀──────outbound calls──────▶│  Decision-Support System (V3)   │
[LangSmith] ◀──────────────outbound traces (redacted)─▶│  (this system)                  │
                                                        └───────────────┬───────────────┘
                                                                        │ decision-support
                                                                        │ output only —
                                                                        │ never a terminal
                                                                        │ action
                                                                        ▼
                                            [QA Reviewer] [PV Safety Physician] [Supply Chain Lead]
                                              (human sign-off, per DDD §11 — TBD names, EAB-3)
```
