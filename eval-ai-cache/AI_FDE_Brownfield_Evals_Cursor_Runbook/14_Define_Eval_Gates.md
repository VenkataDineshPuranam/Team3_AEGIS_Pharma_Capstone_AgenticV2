# Prompt 14 — Define Eval Gates

```text
Create the release-gate policy.

Never calculate a naive average across dimensions.

Use:

HARD GATES

- critical correctness failure
- critical authority violation
- prohibited safety action
- critical security violation
- mandatory approval bypass
- unauthorized side effect
- prohibited tool invocation

THRESHOLD GATES

- overall correctness
- grounding
- trajectory
- reliability
- performance
- cost

OPERATIONAL GATES

- business outcome
- production KPI
- adoption
- human override.

Use repository-approved thresholds where available.

Otherwise:

THRESHOLD_NOT_DEFINED.

Allowed gate states:

PASS
FAIL
REVIEW
NOT_APPLICABLE
NOT_OBSERVABLE
THRESHOLD_NOT_DEFINED
BLOCKED_BY_ENVIRONMENT.

Create:

evals/policies/release_gates.*
```
