# Prompt 19 — Performance Tuning (Redis, Cache, Token Economics)

**Maps to:** STAGES.md Stage 15 (`stage-15-performance-tuning`)
**Lifecycle stage:** Build/Tune (quality infrastructure)
**Framework derived:** V2 addition, drawing on `eval-ai-cache/` runbooks (Windows Cursor Redis Caching Runbook, OpenTelemetry Brownfield Implementation Runbook).
**Core question:** What does each workflow cost (latency, tokens, $) and where is the budget being spent?
**Prerequisites:** Prompt 18 (cache design + baseline metrics).

---

## Produce

1. **Token economics model** — per workflow (GxP batch review, PV intake, supply planning): tokens in/out per agent turn, number of turns to completion, $ cost per run at current model pricing, and the target budget.
2. **Redis tuning** — cache hit-rate target per workflow, eviction policy, memory sizing, and a plan for what happens on cache-cluster failure (degraded mode, not silent full-price fallback with no alert).
3. **Latency budget breakdown** — per node in the LangGraph graph (Prompt 14): target p50/p95 latency, and which nodes are the critical path.
4. **Denial-of-wallet guardrail** — a hard ceiling (per user, per workflow, per day) that trips a hook (Prompt 16) before cost runs away.

### Lean / DMAIC lens (thin, this stage is itself the Improve/Control step for cost)

1. Which token/retrieval waste category (Prompt 01/04 registers) does each tuning change target?
2. Control: the dashboard/alert (feeds Prompt 21 observability) that catches regression in cost or latency after this tuning.

---

## Exit criteria

- [ ] Token economics model exists per workflow with actual measured numbers, not estimates only.
- [ ] Cache hit-rate target is set and measured against Prompt 18's baseline.
- [ ] Denial-of-wallet ceiling is implemented as an enforced hook, not a documented policy only.

---

## Output

Write under `docs/quality/performance/`, `infra/` **and mirror** to `workshop/participant-output/19-performance-tuning/`:

- `token_economics.md`
- `redis_tuning.md`
- `latency_budget.md`
- `denial_of_wallet_guardrail.md`
- `dmaic_lens.md` (thin)
