# Prompt 04 — Design the Eval Harness

```text
Design a minimal repo-local eval harness.

Reuse the repository's existing testing ecosystem.

Do NOT introduce another framework unless unavoidable.

Target structure:

evals/
  README.md

  contracts/
    eval_case
    execution_record
    grader_result
    gate_result

  datasets/
    golden/
    edge/
    adversarial/
    authority/
    failure/
    regression/
    business/

  adapters/

  graders/
    correctness/
    grounding/
    authority/
    safety/
    security/
    trajectory/
    reliability/
    human_oversight/
    performance/
    cost/
    business_outcome/

  policies/
    prohibited_actions
    authority
    human_approval
    release_gates

  runners/

  fixtures/

  reports/

  tests/

Requirements:

- independently runnable
- deterministic where possible
- repo local
- CI compatible
- machine readable
- no production-system mutation
- no external eval service
- no MCP
- no external telemetry collector
- explain every failure
- preserve raw evidence

Define:

EvalCase contract
ExecutionRecord contract
GraderResult contract
GateResult contract
RunManifest contract.

Show proposed implementation before making changes.

Identify any unavoidable application instrumentation.

Prefer zero application changes.
```
