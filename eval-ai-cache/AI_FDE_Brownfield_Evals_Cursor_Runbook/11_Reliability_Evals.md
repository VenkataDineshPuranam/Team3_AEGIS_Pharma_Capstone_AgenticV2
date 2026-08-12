# Prompt 11 — Reliability Evals

```text
Implement controlled RELIABILITY evaluation.

Use mocks/stubs/fixtures.

Test relevant failures:

invalid input
malformed AI output

LLM timeout
LLM error
rate limiting

empty retrieval
retrieval timeout
stale evidence

API 4xx
API 5xx
API timeout

database failure

tool failure
partial tool response

authentication failure

retry exhaustion

malformed configuration
missing configuration

Test:

retry
backoff if applicable
fallback
graceful degradation
escalation
safe termination.

Detect:

fabricated output after dependency failure
infinite retry
duplicate side effect
partial state corruption
silent failure.

Generate reliability results.

Do not fix yet.
```
