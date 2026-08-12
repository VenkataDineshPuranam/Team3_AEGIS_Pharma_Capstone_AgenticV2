# AI-Specific Waste Register — Governing Consolidation (Stage 09)

**Executes:** `prompts/09_lean_dmaic.md` §C — the eight AI-FDE waste categories
**Supersedes as the working register:** the five prior stage copies. **This is the register
Stages 10–21 work from.**
**Artifact status: `stable`**

> Same standing caveat as the DOWNTIME register: **nothing here has been measured on a running
> system.** "Treatment decided" ≠ "waste removed." Each row names what proves it.

---

## 1. Token waste

| Field | Content |
|---|---|
| **Where it appears** | Every agent turn, every tool-result summarization, every Critic/Verifier pass consumes tokens V2's single-shot call never spent. Multiplied by workflow count and by any retry loop |
| **Obs/Hyp** | **Hypothesized** — magnitude is baseline **U1**, Unknown since Stage 01 (EAB-6) |
| **Magnitude** | **Highest-magnitude AI waste in the register**, and the only one with no number at all |
| **Impact** | Direct cost; denial-of-wallet exposure; potentially forces a topology change |
| **Treatment** | (a) ADR-008 caps structural multiplication — one graph per workflow, no cross-graph chains; (b) per-graph and per-node step/token **bound mechanism** built at Stage 10; (c) **numeric** budgets set at Stage 15 from measured data, never estimated; (d) denial-of-wallet guard at Stage 20 |
| **Proof** | Interim assumption 6 — the first real cost number in the programme |
| **Honest gap** | Topology (ADR-008) was locked **before** this number existed, contrary to Stage 01's stated precondition. Mitigated only by ADR-008 being conservative in the cost-reducing direction. Trigger **T-3** reopens it if the measurement lands badly |

## 2. Retrieval waste

| Field | Content |
|---|---|
| **Where it appears** | Unbounded, unranked, cross-context retrieval — an agent pulling documents from outside its workflow, or pulling non-citable documents and spending tokens ranking them |
| **Obs/Hyp** | **Hypothesized** (design-time); the underlying authority rule is **Fact**, verified in V2's `authority_grader.py` |
| **Magnitude** | Medium-high |
| **Impact** | Cost **and** quality — irrelevant context degrades answers; non-citable context is an integrity failure (D2) |
| **Treatment** | Per-bounded-context RAG scoping (`gen_ai_boundaries.md`); `untrusted`/`superseded` filtered **at the retrieval boundary, before ranking**, not after generation (ADR-003); ontology/semantic layer as the retrieval interface rather than raw RAG |
| **Proof** | Interim assumption 2; Stage 14 evals |

## 3. Model waste

| Field | Content |
|---|---|
| **Where it appears** | Two distinct failure modes: (a) **blind retry** — re-running a failed tool call or generation without diagnosing why; (b) **asking the model to judge what a lookup can decide** — e.g. whether a document is trustworthy, whether units match, whether an identity resolves |
| **Obs/Hyp** | (a) **Hypothesized**; (b) **resolved by design** — ADR-003 makes authority a deterministic status lookup |
| **Magnitude** | Medium |
| **Impact** | Cost, latency, and — for (b) — a prompt-injection surface, since a model asked to judge trustworthiness can be told what to think |
| **Treatment** | (a) explicit retry/backoff/diagnosis rules, **no blind retry** — this item had lost its owner in the stage resequencing (gap G3) and is **assigned to Stage 10** here; (b) rules-before-LLM: deterministic gates own every check that a lookup can answer |
| **Proof** | (a) Stage 14 retry-behaviour tests; (b) interim assumption 2 |

## 4. Human-review waste

| Field | Content |
|---|---|
| **Where it appears** | Over-routing (reviewer capacity spent on low-risk cases) or under-routing (safety risk). Also: approvers reconstructing context manually because the trace and the approval request are not linked |
| **Obs/Hyp** | **Hypothesized** — real escalation rates are baseline **U7**, unmeasurable until all three workflows run |
| **Magnitude** | Medium-high |
| **Impact** | Reviewer capacity; safety risk if miscalibrated |
| **Treatment** | **PV and Supply stay at 100% routing — this is a regulatory requirement, not waste to optimize away.** Only Batch Review is a risk-tiering candidate, at Stage 16, calibrated against measured rates. Named accountable roles: EU Qualified Person (Batch, esc. Chief Quality Officer); Global Head of Pharmacovigilance (PV, esc. CMO, Patient Safety Rep holds an advisory veto); Supply Chain VP **plus** a Quality co-approver where quality status is implicated. **Manufacturing VP is explicitly not a batch approver.** HITL timeout ⇒ no action |
| **Proof** | Interim assumption 3 (mechanism); Stage 16 (calibration) |
| **Note** | The interim state proves the mechanism with **one** approver role only. Supply's dual-approval path is untested until the final state |

## 5. Evaluation waste

| Field | Content |
|---|---|
| **Where it appears** | Running V2's 12 categories plus V3's agent-specific categories on every change, with no fast-feedback subset; or tracking metrics that never affect a release decision |
| **Obs/Hyp** | **Hypothesized** — no suite has ever run (baseline **U3**) |
| **Magnitude** | Medium |
| **Impact** | Developer velocity; and, if metrics are decorative, false assurance |
| **Treatment** | Fast-subset vs. full-regression split at Stage 14; every eval must map to a gate that can fail a release. **Consume `eval-ai-cache/`'s 24-part brownfield-evals runbook rather than re-deriving it** (trigger T-7). Note the opposing constraint: ADR-007 requires correctness gates to pass under **every** dependency-failure mode, so the full suite is genuinely large — the split is about feedback speed, not about running less |
| **Proof** | Stage 14 |

## 6. Integration waste

| Field | Content |
|---|---|
| **Where it appears** | Each MCP tool server is a contract that can silently drift. V2 had **zero** MCP integrations; V3 will have four (Evidence Retrieval, Reconciliation, Duplicate-Check, Option-Generation) — two of them in the interim state |
| **Obs/Hyp** | **Fact of new surface** (V2 has zero, V3 has N>0); severity hypothesized |
| **Magnitude** | Medium |
| **Impact** | Reliability; silent behavioural drift is the dangerous form |
| **Treatment** | Versioned MCP schemas + contract tests in `tests/contract/` (Stage 11). Separately, ADR-005 **knowingly adds** integration surface (the Policy Engine as its own container) to remove policy-drift Defects risk — accepted because it fails closed |
| **Proof** | Stage 11 contract tests; interim assumption 5 for the fail-closed behaviour |

## 7. Context waste

| Field | Content |
|---|---|
| **Where it appears** | Reconstructing domain state at every agent turn instead of using LangGraph's shared state schema — the multi-agent-specific failure mode. Also state drift between an agent and its Critic |
| **Obs/Hyp** | **Hypothesized** |
| **Magnitude** | Medium-high — it compounds with Token waste, since every reconstruction is re-sent |
| **Impact** | Cost **and** correctness (agents reasoning over divergent state) |
| **Treatment** | LangGraph shared-state schema as the single source of truth (ADR-001); no per-agent ad-hoc context assembly; schema designed at Stage 10 |
| **Proof** | Stage 10 design review; Stage 17 traces showing state size per turn |

## 8. Observability waste

| Field | Content |
|---|---|
| **Where it appears** | Three faces: (a) traces so noisy the signal is buried, or so thin that a run cannot be reconstructed; (b) **PII captured into traces** — a privacy failure, not merely waste; (c) compliance-critical audit records living only on a vendor-owned surface |
| **Obs/Hyp** | (a),(b) **Hypothesized**; (c) **fact of new surface** — V2 had no agent traces at all |
| **Magnitude** | Medium; (b) is a governance breach if realized |
| **Impact** | Debuggability, privacy, regulatory retention |
| **Treatment** | **OpenTelemetry as the instrumentation layer** so the backend stays swappable (LangSmith + Azure Monitor/App Insights); **redaction rules defined before the first trace is written**, not retrofitted; audit store **owned and separate** from LangSmith — Azure Blob with WORM immutability (ADR-006, ADR-009) |
| **Proof** | Stage 17; audit-write success = 100% while LangSmith is healthy — proving the two sinks have not silently collapsed into one |

---

## Cross-cutting notes

**The two categories that changed most since Stage 01.** *Model waste* split into two
mechanisms and had one of them (blind retry) rescued from ownerlessness. *Observability*
gained an explicit privacy face — over-capture is not just noise, it is a governance breach.

**The category that has not moved at all.** *Token waste* has had the same status since
Stage 01: highest magnitude, no number. Every subsequent stage deferred it. The interim state
is where that ends — or where the topology reopens.

**Platform dependency.** ADR-009's open LLM-route sub-decision touches this register directly:
Route B (Azure OpenAI) preserves every treatment decision above but invalidates every
*measured* baseline taken under Route A (trigger T-6). Measure late enough that the numbers
are taken under the route that ships.
