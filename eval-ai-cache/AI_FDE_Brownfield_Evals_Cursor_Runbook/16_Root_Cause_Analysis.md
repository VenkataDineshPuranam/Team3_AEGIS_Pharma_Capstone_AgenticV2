# Prompt 16 — Root Cause Analysis

```text
Perform ROOT CAUSE ANALYSIS for every baseline failure.

Classify each as:

APPLICATION_DEFECT

EVAL_HARNESS_DEFECT

TEST_DATA_DEFECT

MISSING_REQUIREMENT

MISSING_OBSERVABILITY

ENVIRONMENT_FAILURE

EXTERNAL_DEPENDENCY_FAILURE

EXPECTED_BEHAVIOR.

For every real defect provide:

failure ID
reproduction
root cause
affected code
severity
business impact
security/safety impact
recommended fix
tests required
regression case required.

Deduplicate failures that share one root cause.

Produce:

evals/reports/root_cause_analysis.md

and a prioritized remediation backlog.

Do not change code yet.
```
