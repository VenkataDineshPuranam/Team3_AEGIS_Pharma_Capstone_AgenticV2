# Prompt 21 — Eval Integrity / Anti-Cheating Audit

```text
Audit the complete evaluation implementation for false confidence.

Look specifically for:

tests that always pass

hard-coded expected outputs

graders reading labels improperly

test-specific production logic

ignored exceptions

skipped tests

disabled security tests

overly broad mocks

fake telemetry

fabricated token/cost information

synthetic data represented as production evidence

NOT_OBSERVABLE represented as PASS

thresholds invented without authority

aggregate scores hiding hard-gate failures

unexecuted tests represented as successful

report values not traceable to raw result files.

Validate links between:

case
execution
grader
gate
report.

Fix defects in the EVAL SYSTEM if found.

Do not weaken application requirements.

Run harness self-tests again.

Produce:

eval_integrity_audit.md.
```
