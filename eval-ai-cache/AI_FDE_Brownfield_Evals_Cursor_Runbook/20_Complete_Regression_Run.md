# Prompt 20 — Complete Regression Run

```text
Run the COMPLETE regression suite after remediation.

Run:

existing repository tests
harness self-tests
all 11 applicable eval families
historical regressions
new defect regressions
security adversarial suite
reliability suite
gate engine.

Compare:

BASELINE
vs
POST_REMEDIATION.

Identify:

fixed
unchanged
regressed
new failure.

Any newly introduced regression is a release blocker until classified.

Generate:

post_remediation_results.jsonl
regression_comparison.csv
post_remediation_gate_results.json.
```
