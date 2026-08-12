# Prompt 12 — Performance + Cost Evals

```text
Implement PERFORMANCE and COST evaluation without adding
external infrastructure.

Use existing application/test instrumentation.

Measure where observable:

end-to-end latency
p50
p95
p99

model latency
retrieval latency
tool latency

throughput where meaningful

retry overhead.

Capture AI resource consumption where available:

input tokens
output tokens
cached tokens

model calls
retrieval calls
tool calls
retries.

Preferred FinOps metric:

cost_per_successful_business_task.

Only calculate monetary cost if reliable pricing information is
already available to the application/eval environment.

Otherwise report:

token consumption
model calls
tool calls

and:

COST_NOT_CALCULABLE.

Do not fabricate pricing.

If there is no documented SLO/budget:

THRESHOLD_NOT_DEFINED.

Still establish a baseline.

Generate performance and cost reports.
```
