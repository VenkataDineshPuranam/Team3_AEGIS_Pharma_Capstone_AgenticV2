# AI-Specific Waste Register — Stage 02 (DDD), updated from Frame/SCQA

**DDD-stage update:** carried forward from `docs/product/scqa/waste_register_ai_specific.md`.
Two rows refined with domain-level findings (see `dmaic_lens.md` Analyze):
- **Retrieval / Context** — the per-bounded-context RAG scoping in `gen_ai_boundaries.md`
  (each domain agent retrieves only from its own workflow's evidence, routed through
  Evidence & Provenance) is now the concrete, named mitigation for both rows, not just a
  general intent.
- **Integration** — the Governance-as-open-host-service design choice (`context_map.md`)
  deliberately accepts *more* Integration surface (a separate policy contract to maintain)
  in exchange for removing Defects risk; this is a conscious trade-off, not an oversight —
  flagged for re-evaluation at Stage 04 (ADR) if the integration overhead proves costly.

No entries added or removed at DDD level; all Stage 01/02(SCQA) findings still hold.

Eight categories per `prompts/01_discovery.md`: Token, Retrieval, Model, Human-review,
Evaluation, Integration, Context, Observability. Each: where/how it appears, evidence
trace, magnitude, impact, recommended treatment.

| Category | Where/how it appears | Evidence trace | Magnitude | Impact | Recommended treatment |
|---|---|---|---|---|---|
| **Token** | Multi-agent designs multiply LLM calls per user request versus V1's single-shot call. Every agent turn, every tool-result summarization, every critic/verifier pass consumes tokens V1 never spent. | Hypothesized — no V2 agent exists yet to measure; the *risk* is a direct consequence of the multi-agent decision (`discovery.md` §5) | High — named explicitly as the top Stage 15 concern (`prompts/19_performance_tuning.md`) | Direct cost impact, denial-of-wallet risk | Token/cost budget per node (Stage 08 §I2 technical design), denial-of-wallet hook (Stage 20 governance) |
| **Retrieval** | If agents query raw documents instead of the planned semantic layer (Stage 13), retrieval could pull unranked, unbounded context — a waste category V1's simpler retrieval (if any existed in the single-shot app) likely didn't stress as hard. | Hypothesized | Medium-high | Cost + quality (irrelevant context degrades answer quality) | Ontology/semantic layer (Stage 13) as the retrieval interface, not raw RAG |
| **Model** | Risk of "blind retry" — an agent retrying a failed tool call or a failed generation without diagnosing why, burning model calls without fixing the root cause. Flagged generically in `prompts/08_technical_design.md`'s DMAIC lens ("error/retry rules that avoid blind Model waste"). | Hypothesized | Medium | Cost + latency | Explicit retry/backoff and diagnosis rules in Stage 08 technical design |
| **Human-review** | V1's rubric-driven, single-shot design likely routes many/most outputs through human review by default (safe but expensive). A poorly-designed V2 HITL model (Stage 16) could either (a) over-route to human review, wasting reviewer time on low-risk cases, or (b) under-route, creating safety risk. | Hypothesized — V1's actual HITL routing logic not read this pass | Medium-high | Reviewer capacity + safety risk if miscalibrated | Risk-tiered HITL design (Stage 16), calibrated against actual case risk, not blanket routing |
| **Evaluation** | Running the full 12+ eval categories (V1's floor) plus V2's new agent-specific categories (Stage 14) on every change, without a fast-feedback subset, could make evaluation itself a bottleneck ("evaluation waste" — metrics that don't affect release decisions, per `prompts/12_assurance.md`'s DMAIC lens). | Hypothesized | Medium | Developer velocity | Eval-AI-Cache harness (Stage 14) should define a fast-subset vs full-regression split |
| **Integration** | Each new MCP tool server (Stage 11) is an integration point that can silently drift from its contract. V1 had no MCP integrations to manage at all — this is a wholly new waste surface. | Fact of new surface (V1 has zero MCP integrations; V2 will have N > 0) | Medium | Reliability | Tool contract tests (`tests/contract/`), versioned MCP schemas (Stage 11) |
| **Context** | Reconstructing domain state at every agent turn (instead of using LangGraph's shared state schema properly) would be a direct context-waste failure mode unique to multi-agent systems. | Hypothesized | Medium-high | Cost + correctness (state drift between agents) | LangGraph state schema as the single source of truth (Stage 10/08 §I2), not per-agent ad-hoc context reconstruction |
| **Observability** | V1 had no agent traces to observe (single-shot request/response, evaluated post-hoc by the grader harness). V2 introduces LangSmith tracing (Stage 17) specifically to close this gap — but a poorly-scoped tracing design (too much/too little captured) is itself a new waste risk (noise burying signal, or PII leaking into traces). | New surface (fact: V1 has no agent-trace observability at all); risk of miscalibration is hypothesized | Medium | Debuggability + privacy risk if over-captured | Tracing design with explicit redaction rules (Stage 17), reviewed against governance policy register (Stage 16) |

**Note:** as with the DOWNTIME register, most entries are hypothesized risk categories
introduced by the multi-agent redesign itself, since V2 has no running system yet. Several
categories that are entirely new relative to V1 (Integration, Observability) are marked
as facts-of-new-surface rather than hypothesized magnitude, since their *existence* as a
new concern is certain even though their *severity* is not yet measurable.
