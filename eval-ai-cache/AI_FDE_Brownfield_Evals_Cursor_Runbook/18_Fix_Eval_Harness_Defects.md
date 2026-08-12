# Prompt 18 — Fix Eval Harness Defects

```text
Now address confirmed defects in:

eval harness
grader
dataset
fixture
configuration

only where the RCA classified them as such.

Do not modify application behavior to compensate for a bad eval.

For every harness change:

explain defect
reproduce defect
fix defect
add harness self-test
rerun affected eval.

Verify that no grader contains logic that simply recognizes
test case IDs or expected answers.

Run all harness self-tests afterward.
```
