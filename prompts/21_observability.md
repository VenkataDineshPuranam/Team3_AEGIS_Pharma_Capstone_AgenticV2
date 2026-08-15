# Prompt 21 — Observability (LangSmith, OpenTelemetry, Dashboards)

**Maps to:** STAGES.md Stage 17 (`stage-17-observability`)
**Lifecycle stage:** Build (control plane)
**Framework derived:** V2 addition, drawing on `eval-ai-cache/`'s OpenTelemetry Brownfield Implementation Runbook.
**Core question:** Can we explain, after the fact, exactly what every agent did and why?
**Prerequisites:** Prompt 14 (agent/graph design), Prompt 18 (eval baseline metrics), Prompt 19 (performance budgets).

---

## Produce

1. **Tracing design** — LangSmith project/run structure: what is traced per agent turn (inputs, tool calls, outputs, latency, token counts, HITL interrupts), and OpenTelemetry span structure for cross-service correlation.
2. **Dashboards** — cost, latency, eval-score trend, cache hit-rate, guardrail-trip rate (per Prompt 19/20 metrics).
3. **Alerting** — thresholds that page/notify on eval regression, cost spike, guardrail trip, latency SLO breach (feeds `ops/alerts/`, `ops/slo/`).
4. **Trace retention & privacy** — what is redacted before a trace is stored (must not leak PII/PHI into trace logs — cross-check against Prompt 20 policy register).

### Lean / DMAIC lens (thin)

1. Which Observability-waste entries (Prompt 01/04/06 registers — "logs/metrics with no owner") does this design close out?

---

## Exit criteria

- [ ] Every agent node in Prompt 14's graph emits a trace with tool calls and HITL events visible.
- [ ] Dashboards exist for cost, latency, eval score, cache hit-rate, guardrail-trip rate.
- [ ] Trace redaction is verified against the governance policy register (Prompt 20).

---

## Output

Write under `packages/observability/`, `ops/dashboards/`, `ops/alerts/` **and mirror** to `workshop/participant-output/21-observability/`:

- `tracing_design.md`
- `dashboards.md`
- `alerting.md`
- `trace_redaction_and_retention.md`
- `dmaic_lens.md` (thin)
