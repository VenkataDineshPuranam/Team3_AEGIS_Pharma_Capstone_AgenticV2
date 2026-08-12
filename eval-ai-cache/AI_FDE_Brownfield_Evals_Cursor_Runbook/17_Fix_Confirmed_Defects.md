# Prompt 17 — Fix Confirmed Defects

```text
Remediate confirmed defects from the approved RCA.

Rules:

1. Fix confirmed defects only.
2. Use smallest safe change.
3. Do not perform unrelated refactoring.
4. Preserve public interfaces unless defect resolution requires otherwise.
5. Do not weaken an eval to make code pass.
6. Do not remove adversarial tests.
7. Do not lower thresholds merely to obtain PASS.
8. Do not suppress exceptions merely to obtain PASS.
9. Do not hard-code test answers.
10. Do not change golden expected values unless the original expectation
    was proven wrong.

For each application defect:

BEFORE FIX:
reproduce failing eval.

IMPLEMENT:
minimal fix.

AFTER FIX:
run affected existing tests.

CREATE:
permanent regression test.

RUN:
affected eval dimension.

If failure remains:
investigate rather than masking it.

At completion report:

files_changed
root_causes_fixed
regression_tests_added
remaining_failures.
```
