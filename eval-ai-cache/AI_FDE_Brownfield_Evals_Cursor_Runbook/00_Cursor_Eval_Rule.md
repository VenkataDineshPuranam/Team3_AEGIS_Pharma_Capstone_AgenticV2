# Prompt 00 — Create Cursor Eval Rule

Run this once in Cursor Agent.

```text
Create a Cursor Project Rule at:

.cursor/rules/ai-fde-evals.mdc

The rule governs all evaluation-engineering work in this repository.

Include these mandatory rules:

1. Treat the repository as an unfamiliar brownfield production codebase.

2. Never assume architecture, business rules, AI capabilities, RAG,
   agents, tools, human approval, or requirements without repository evidence.

3. Reuse the existing:
   - language
   - package manager
   - build system
   - testing framework
   - mocks
   - fixtures
   - CI conventions

4. Do not introduce MCP.

5. Do not require:
   - external eval SaaS
   - external observability platforms
   - OpenTelemetry Collector
   - Docker unless already required by the repo
   - new infrastructure solely for evals

6. Prefer repo-local deterministic evaluation.

7. Grader priority:
   deterministic > rule based > statistical > semantic > human.

8. Never use an LLM judge when deterministic validation is sufficient.

9. Never allow Cursor's narrative opinion itself to constitute an eval PASS.

10. Every PASS/FAIL must point to reproducible evidence.

11. Never fabricate:
    - expected results
    - business thresholds
    - costs
    - token usage
    - telemetry
    - retrieved evidence
    - approvals
    - performance measurements.

12. Use these states where appropriate:
    PASS
    FAIL
    REVIEW
    NOT_APPLICABLE
    NOT_OBSERVABLE
    THRESHOLD_NOT_DEFINED
    BLOCKED_BY_ENVIRONMENT

13. Never convert NOT_OBSERVABLE into PASS.

14. Never average hard-gate failures into an overall score.

15. Critical security, safety, authority or mandatory-approval violations
    override aggregate scores.

16. Use mocks/stubs/fixtures for destructive scenarios.
    Never attack or mutate real external systems.

17. Preserve existing application behavior unless fixing a confirmed defect.

18. Before fixing anything:
    reproduce the failure and record evidence.

19. Every confirmed defect that is fixed must receive a regression test.

20. After remediation:
    rerun affected tests plus the complete regression suite.

21. Keep eval artifacts under /evals wherever practical.

22. Generated reports must remain evidence-based and distinguish:
    OBSERVED FACT
    INFERENCE
    SYNTHETIC TEST
    PROVISIONAL THRESHOLD
    UNVERIFIED ASSUMPTION

23. Protect secrets and sensitive data.
    Never write real credentials into datasets or reports.

24. Every eval run must record:
    repository commit/version
    configuration
    dataset version
    commands
    exit codes
    test results
    gate decisions.

25. Final production-readiness decisions must be one of:
    READY
    READY_WITH_CONDITIONS
    NOT_READY
    INSUFFICIENT_EVIDENCE

Make the rule concise and operational.
Do not modify application source code.
```
