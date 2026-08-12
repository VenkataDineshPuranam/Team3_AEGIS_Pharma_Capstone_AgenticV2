# Prompt 01 — Repo Reconnaissance

Use a fresh Cursor chat.

```text
Act as a Senior AI Forward Deployed Engineer.

Perform a READ-ONLY deep reconnaissance of this brownfield repository.

Do not modify anything.

Determine:

A. REPOSITORY
- purpose
- business domain
- languages
- frameworks
- build/package system
- application entry points
- configuration
- dependencies

B. EXECUTION
- how application starts
- major workflows
- inputs
- outputs
- state
- side effects
- external dependencies

C. AI
Determine whether each is PRESENT / ABSENT / UNCLEAR:

- LLM
- prompt
- system instructions
- embeddings
- RAG
- vector search
- agents
- tools/functions
- memory
- AI-generated structured output
- human approval
- model routing
- retries/fallbacks

D. TESTING
Identify existing:

- unit tests
- integration tests
- E2E tests
- API tests
- security tests
- performance tests
- fixtures
- mocks
- datasets
- regression tests
- CI tests

E. OBSERVABILITY
Identify existing ability to observe:

- input
- output
- retrieved evidence
- tool calls
- tool parameters
- errors
- retries
- approvals
- side effects
- latency
- tokens
- model calls
- cost

F. WORKFLOW MAP

Trace each material business workflow:

Input
→ validation
→ business logic
→ AI if present
→ retrieval if present
→ tools/API
→ approval
→ side effects
→ output.

G. SYSTEM UNDER EVALUATION

Define explicit boundaries for what should be evaluated.

For every conclusion provide repository file/path evidence.

Return:

repo_summary
architecture
workflow_inventory
AI_surface
existing_test_inventory
observability_inventory
risk_inventory
evalability_gaps
recommended_system_under_evaluation

No changes.
```
