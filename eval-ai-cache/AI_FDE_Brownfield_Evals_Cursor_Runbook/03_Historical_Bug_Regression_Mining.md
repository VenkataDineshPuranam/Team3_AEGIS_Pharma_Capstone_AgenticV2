# Prompt 03 — Mine Existing Bugs & Regressions

```text
Perform a read-only brownfield regression mining exercise.

Inspect available:

- existing tests
- git history
- bug-fix commits
- regression tests
- TODO/FIXME comments
- issue references
- release notes
- failure fixtures
- security fixes
- error handling
- known limitations

Identify historical or strongly evidenced failure modes.

For each create:

regression_id
source_evidence
workflow
trigger
historical_failure
expected_behavior
severity
eval_dimension
recommended_gate

Do not claim a historical defect without evidence.

Separately propose synthetic regression candidates and mark:

synthetic: true

Do not modify files.
```
