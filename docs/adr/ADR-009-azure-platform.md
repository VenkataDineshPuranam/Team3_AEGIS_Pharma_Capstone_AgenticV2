# ADR-009 — Azure is the target cloud platform

**Status:** `accepted` (platform choice) with **one open sub-decision** — the model-hosting
route, flagged in §Open question below.
**Evidence basis:** Fact (explicit user/sponsor directive) — not a technical derivation.
**Amends:** [ADR-001](ADR-001-runtime-stack.md) (runtime stack) and
[ADR-007](ADR-007-degraded-mode-safe-not-offline-capable.md) (degraded-mode model).

## Context

ADR-001 selected LangGraph / LangSmith / Redis without naming a hosting platform, and
ADR-007 established that V3 runs cloud-connected. The sponsor has now directed **Azure** as
the platform. This is a directive, recorded for traceability, not a decision derived from
comparison.

## Decision

Target **Microsoft Azure**. Component mapping:

| Concern | ADR-001 (platform-neutral) | Azure realization |
|---|---|---|
| Orchestration | LangGraph | **Unchanged** — LangGraph is a library, not a service; hosted on **Azure Container Apps** (or AKS if scale/network policy demands) |
| Compute — API + workers | Orchestrator API, Agent Workers | Azure Container Apps (separate apps, so the async worker scales independently per `c4_containers.md`) |
| LLM inference | Anthropic Claude API | **Open sub-decision — see below** |
| Cache | Redis | **Azure Cache for Redis** — direct substitution, no design change |
| Observability | LangSmith | LangSmith retained (SaaS, permitted under ADR-007) **plus Azure Monitor / Application Insights** for platform-level telemetry. OpenTelemetry remains the instrumentation layer, so the trace backend stays swappable |
| Audit / evidence store (ADR-006) | "Owned store, separate from LangSmith" | **Azure Blob Storage with immutability (WORM) policies**, optionally Azure SQL for queryable metadata |
| Secrets | — | **Azure Key Vault** |
| Identity, roles, approver authorization | — | **Microsoft Entra ID** |
| Network isolation | — | VNet integration, Private Endpoints for Redis/Storage/model endpoint |

## Two consequences that improve earlier decisions

1. **Entra ID strengthens the HITL control model.** The named approver roles closed in
   EAB-3 (EU Qualified Person, Global Head of Pharmacovigilance, Supply Chain VP + Quality
   co-approver) become **Entra ID groups with role assignments**, so "current authorization
   checked at execution time" — a V2 required operating property that was previously only a
   design statement — becomes enforceable infrastructure. Supply Planning's dual-approval
   requirement maps to requiring membership in two distinct groups.
2. **Blob immutability strengthens ADR-006.** The audit store's requirement to be
   independent and retention-governed is far better served by WORM-policy Blob Storage than
   by an application-managed database, and it directly supports the Stage 19 compliance
   evidence requirement.

## Open question — model hosting route (needs confirmation)

"Use Azure" does not by itself determine where inference runs. Two routes:

| Route | Notes |
|---|---|
| **A — Claude via Azure AI Foundry (recommended)** | Keeps the Claude models the design assumes, inside the Azure boundary (billing, networking, governance). Preserves ADR-003/004 reasoning unchanged, since model behavior is unchanged. |
| **B — Azure OpenAI (GPT models)** | Fully Azure-native, but changes the model family. Would require re-validating prompt behavior, abstention characteristics, and the eval baselines at Stage 14 — none of the design reasoning depends on a specific model, but the *measured* results would all need re-running. |

**Recommendation: Route A**, because it changes the platform without changing the model
variable at the same time — keeping one variable fixed while the other moves is what makes
the interim state's assumption tests interpretable. **Confirm before Stage 20.**

Model availability on any given Azure service changes over time; verify current availability
in the target region at implementation time rather than trusting this document's snapshot.

## Azure is the DEPLOYMENT target, not a DEVELOPMENT requirement

Only **LLM inference** genuinely requires an outbound cloud call. Every other component runs
locally, so development and the entire interim state do **not** need Azure:

| Component | Local development |
|---|---|
| LangGraph orchestration | Runs in-process — it is a library, not a service |
| Redis cache | `docker run redis` (interim state excludes cache anyway) |
| Audit/evidence store | Local Postgres or SQLite; swap for Blob WORM at deploy |
| Observability | OpenTelemetry → local collector (e.g. Jaeger); LangSmith optional |
| Entra ID / Key Vault | Stubbed behind the same interface; real bindings at deploy |
| LLM inference | **Outbound API call required** — the one hard dependency |

**Therefore: develop locally (Docker Compose + one API key), deploy to Azure.** The interim
state's seven assumption tests (`docs/product/state/interim/interim_state.md` §3) can all be
run on a laptop — which is faster to iterate and incurs no Azure spend until deployment.
Stage 20 must not treat Azure as a prerequisite to writing or testing code.

This also keeps ADR-007's degraded-mode design honest: if the local path works with stubs for
every hosted dependency, the fallbacks are real rather than theoretical.

## Alternatives considered

Not applicable — this is a sponsor directive. Recorded for traceability per the ADR prompt's
requirement that direction-setting decisions be captured even when not derived.

## Consequences

- **Easier:** enterprise identity, secrets, immutable audit storage, and network isolation
  come from the platform rather than being built; the compliance story (Stage 19) is
  materially stronger.
- **Harder:** couples the deployment to one cloud; Azure Container Apps' constraints may
  eventually force AKS.
- **Riskier:** deepens the vendor-concentration risk already recorded in ADR-001 and
  `final_state.md` §7.3 — now Microsoft *and* the model provider.

## Guardrails

OpenTelemetry stays the instrumentation layer so the trace backend remains swappable. No
Azure-specific API may leak into domain or agent logic — platform bindings live in
`packages/config` and `infra/`, keeping the domain model (Stage 02) platform-neutral.

## Validation

Stage 20: deploy the interim-state slice to Azure Container Apps and confirm Entra ID
group membership actually gates HITL approval; confirm Blob immutability policy is active on
the audit container.

## Revisit triggers

If the model-hosting route changes (Route A ↔ B), Stage 14's eval baselines must be re-run —
they are model-specific measurements, not model-independent facts.
