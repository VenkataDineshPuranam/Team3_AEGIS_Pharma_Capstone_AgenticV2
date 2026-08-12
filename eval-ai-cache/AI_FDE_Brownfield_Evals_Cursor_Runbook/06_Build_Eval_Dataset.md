# Prompt 06 — Build Eval Dataset

```text
Create the initial evaluation dataset.

Use repository evidence plus explicitly marked synthetic scenarios.

Include:

NORMAL / GOLDEN
EDGE
BOUNDARY
INVALID INPUT
HISTORICAL REGRESSION
ADVERSARIAL
FAILURE / OUTAGE
BUSINESS WORKFLOW

And where applicable:

GROUNDING
AUTHORITY CONFLICT
SAFETY
AGENT TRAJECTORY
HUMAN APPROVAL

Each case must include where applicable:

case_id
description
workflow
input
expected_behavior

required_facts
prohibited_behavior

required_sources
authority_requirement

allowed_tools
prohibited_tools

approval_requirement

expected_side_effects

thresholds

severity
graders
gate_type
provenance
synthetic

Never manufacture business truth.

Use:

synthetic: false

only when supported by repository evidence.

Validate every dataset against EvalCase contract.
```
