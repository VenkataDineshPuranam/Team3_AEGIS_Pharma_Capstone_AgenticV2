# Prompt 05 — Build Harness + Self-Test

```text
Implement the approved /evals harness.

Do not refactor production code.

Reuse existing libraries first.

Do not install additional packages unless the existing stack cannot
implement a required capability.

If a dependency would be required:
STOP that capability and mark:

BLOCKED_BY_DEPENDENCY

rather than installing automatically.

The execution record must support where applicable:

case_id
workflow_id

input
expected_behavior
actual_output

evidence
retrieved_documents
citations

tools_called
tool_arguments
tool_results
trajectory

approval_required
approval_requested
approval_received
authorized_approver

side_effects

retries
exceptions
fallbacks

start_time
end_time
latency

input_tokens
output_tokens
cached_tokens
model_calls
tool_calls
estimated_cost

business_result

grader_results
gate_results

For unavailable evidence write:

NOT_OBSERVABLE

Never fabricate it.

Create harness self-tests and execute only those self-tests.

Report:

files_created
files_modified
commands_executed
test_results
unresolved_gaps.
```
