# Prompt 19 — Repeatability / Flakiness

```text
Perform EVAL REPEATABILITY assessment.

Rerun relevant non-destructive evals multiple times where model
or stochastic behavior can change results.

Identify:

stable passes
stable failures
flaky tests
model variability
timing variability
environment variability.

Do not hide flakiness inside averages.

Classify unstable cases:

FLAKY_EVAL
FLAKY_APPLICATION
EXPECTED_MODEL_VARIANCE
ENVIRONMENT_VARIANCE.

Where appropriate replace weak equality checks with valid deterministic
invariants without weakening the intended requirement.

Generate:

repeatability_results.json
flaky_cases.csv
repeatability_summary.md.
```
