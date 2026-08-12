# DMAIC Lens — Stage 02 (DDD)

**Full cycle** (DDD is a designated full-DMAIC stage, alongside Discovery/01, Frame/01(SCQA),
C4/03, ADR/04). Builds on Stage 01's full DMAIC output, does not restart from a blank page.

## Define

Restated at domain-model granularity: which bounded-context boundaries exist specifically to
contain a named waste or defect risk? Answer: the Batch Review / PV Intake / Supply Planning
split (peer contexts, no direct coupling) exists specifically to contain the **Defects**
risk named in Stage 01 (H5 — authority leaking across a handoff) by ensuring no domain agent
ever needs to reason in another workflow's vocabulary. The Governance & Oversight
open-host-service relationship exists specifically to prevent that same defect risk at the
policy level — a single, independently-owned policy contract instead of three
locally-interpreted copies of "don't do the prohibited thing."

## Measure

Which domain invariants are (or should be) instrumented so a violation is measurable, not
just theoretically prevented?
- `Batch` aggregate schema must be checked (Stage 20 implementation, Stage 14 eval) to
  confirm it structurally cannot carry a release/reject field — measurable via schema
  validation, not just code review.
- Every `AgentRun` should be queryable for `AgentAuthorityExceeded` events — a count that
  should always measure zero; Stage 17 (observability) is where this becomes an actual
  dashboard metric, not just a domain-model aspiration.
- HITL routing rate for PV/Supply (should measure at 100% per §11) — measurable once
  Stage 20 exists.

## Analyze

Do Stage 01's root-cause findings still hold at domain-model level? **Yes, confirmed, with
one addition:** Stage 01 named the prohibited-decision boundary as the highest-risk
regression surface (H5) but treated it generically. At domain-model granularity, the
specific mechanism is now clear: **the risk is not "agents might decide to do the prohibited
thing" — it's "the data model might let them represent it even accidentally."** This is a
refinement from behavioral risk (agent reasoning) to structural risk (schema design), which
changes where the control belongs — from prompt instructions to aggregate/tool-contract
design. This is the domain model's central Improve contribution (below).

RAG/agent boundary risks (per `prompts/04_ddd.md`'s prompt): unbounded/unscoped retrieval
would directly cause the Retrieval and Context waste categories from Stage 01's AI-specific
register; the per-context RAG scoping in `gen_ai_boundaries.md` is the direct mitigation.
Domain ambiguities that would cause Extra processing/Motion if left unresolved: the
"agent" term collision (domain vs. Claude Code build-time agents) — resolved this stage by
explicit naming convention (§3 of `domain_model.md`).

## Improve

The domain model itself is the Improve artifact. Specific modeling choices and the waste/
defect they treat:
- **Prohibited action as unrepresentable schema state** (not just an unrecommended one) —
  treats the Defects waste category by making the highest-severity failure mode structurally
  impossible rather than merely discouraged.
- **Per-context RAG scoping + shared Evidence & Provenance kernel** — treats Retrieval and
  Context waste by bounding what any single agent call can pull in, while avoiding
  duplicated evidence-authority logic across three contexts (which would itself be a
  Motion/Extra-processing waste).
- **Governance as an open-host service, not a shared kernel** — deliberately chosen over the
  simpler shared-kernel pattern specifically so policy can't be locally weakened; the
  trade-off accepted is an extra integration point (Integration waste) in exchange for
  removing a much larger Defects risk. This trade-off should be revisited at Stage 04 (ADR)
  if Integration overhead proves costly in practice.

## Control

Which domain invariants need a runtime check/monitor so a violation is caught, not just
documented (provisional; firmed up at Stage 09 consolidation and Stage 12 assurance)?
- `AgentAuthorityExceeded` event count — must be a Stage 17 dashboard metric with a zero
  baseline and an alert on any nonzero reading.
- HITL routing-rate for PV/Supply — must measure 100%; any drop below 100% is a Stage 12/14
  release-gate failure, not a tuning parameter.
- Schema-level prohibited-action unrepresentability — needs a Stage 14 contract test (not
  just a design review) confirming the actual implemented schema, once it exists at Stage 20,
  matches this document's invariant.

## Waste register updates

See `waste_register_downtime.md` and `waste_register_ai_specific.md` (this folder) —
carried forward from Stage 01/SCQA and refined with the domain-level findings above.
