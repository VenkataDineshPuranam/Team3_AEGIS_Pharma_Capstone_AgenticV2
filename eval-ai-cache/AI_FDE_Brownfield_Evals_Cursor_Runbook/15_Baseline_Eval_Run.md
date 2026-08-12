# Prompt 15 — Baseline Eval Run

```text
Execute BASELINE EVALUATION.

Do not fix anything during this run.

Run:

1 harness self-tests
2 existing repository test suite
3 correctness
4 grounding
5 authority
6 safety
7 security
8 trajectory
9 human oversight
10 reliability
11 performance
12 cost
13 business outcome
14 historical regression
15 gate engine.

Record:

git commit/hash
environment
runtime
eval dataset version
configuration
commands executed
exit codes
start/end timestamps.

Preserve all failures.

Generate:

baseline_run_manifest.json
baseline_results.jsonl
baseline_failures.csv
baseline_gate_results.json.

Summarize:

PASS
FAIL
REVIEW
NOT_APPLICABLE
NOT_OBSERVABLE
THRESHOLD_NOT_DEFINED.

Do not remediate.
```
