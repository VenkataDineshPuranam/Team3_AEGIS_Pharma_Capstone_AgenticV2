# ADR-010 — Cross-run human precedent is evidence, not agent memory

**Status:** `accepted`
**Evidence basis:** Derivation from `docs/architecture/agentic/memory_design.md` §2
(no long-term agent memory) and ADR-003 (citability is a deterministic status gate).

## Context

`memory_design.md` forbids long-term agent memory because a remembered conclusion is
uncitable, does not supersede when its source does, and can accumulate implied authority
from "the QP approved a similar case." HITL justifications already persist in
`human_override_recorded` but agents cannot read them, so every `batch_review` pack
starts cold.

Reopening cross-run recall requires an ADR. This one carves a narrow exception that
keeps every existing rail.

## Decision

Cross-run recall of human HITL decisions is allowed **only** as `EvidenceItem` nodes
retrieved by a hashed, read-only, batch-review-only tool (`precedent.retrieve`), called
after `batch.reconcile` and before `synthesize`.

- **Citable actions:** `rejected` only. Approvals remain audit-only and are never minted.
- **Status:** `draft` (already in the retrieve citable enum). No new status value.
- **Jurisdiction v1:** `EU` — the only minting role is EU Qualified Person.
- **Identity:** role only, never a person name.
- **Idempotency:** `evidence_id = HP-{source_run_id}`; MERGE, not create.
- **Supersession v1:** append-only. Quality may later set `status=superseded`; ADR-003
  then excludes the item from retrieve automatically.
- **HITL:** unchanged. Timeout is still no action. A cited precedent is not a disposition.

## Alternatives considered

- **Vector memory / embeddings of justifications** — rejected: no `status`, no
  `supersedes` edge, no jurisdiction, and no way for ADR-003 to filter.
- **Add `"precedent"` to `evidence.retrieve` terms** — rejected: retrieve runs before
  reconcile, so it cannot match on finding category; it would dump every QP rejection
  into every run.
- **Mint approvals as positive authority** — rejected: that is the exact leak
  `memory_design.md` §2.3 names.

## Consequences

- **Easier:** similar-gap refusals become citable on the next pack without a planner or
  a new authority surface.
- **Harder:** Neo4j must be reachable to mint or retrieve; mint failure must not undo
  the human decision (best-effort after `write_human_override`).
- **Riskier:** a synthesizer could paraphrase a refusal into "reject the batch." Mitigated
  by the existing prohibited-action guard, prompt wording, and `precedent_authority_grader`.

## Guardrails

- No graph other than `batch_review` may import `precedent_retrieve` or `precedent_mint`.
- `precedent.retrieve` has no write method in its contract (`read_only: true`).
- Approvals and timeouts never mint.
