# Gen AI Boundaries — Stage 02 (DDD)

**Artifact status:** `provisional` (inherits from `domain_model.md`)

Extracted/expanded from `domain_model.md` §8–13 for standalone reference (the prompt's
required `gen_ai_boundaries.md` output: rules vs AI, RAG, agents, HITL, audit, eval intent).

## Rules vs. AI reasoning

| Decision | Rules (deterministic) | AI reasoning (probabilistic) |
|---|---|---|
| Is this action prohibited? | **Always rules** — schema-level unrepresentability + runtime hook (Stage 16), never AI judgment | Never |
| Is this evidence source authoritative? | **Always rules** — document status lookup (`approved`/`superseded`/`untrusted`/`draft`/jurisdiction-local) | Never — no "the AI decides this document seems trustworthy" |
| Is this a duplicate PV case? | Threshold/rule component **if** V2's existing logic is rule-based (unconfirmed — verify against `submission/evaluation/graders/` in Stage 06/07) | Candidate-matching/ranking may be AI-assisted, final duplicate flag should remain rule-gated pending verification |
| How should reconciled evidence be summarized for a human reviewer? | N/A | **AI** — natural-language synthesis |
| Which shortage options rank highest given already-filtered constraints? | Constraint filtering is rules | Ranking within the filtered set may be AI |

## RAG design

- Retrieval is **scoped per bounded context** — a domain agent never retrieves outside its
  own workflow's evidence scope.
- Routed through the Evidence & Provenance context's semantic layer (Stage 13 dependency).
- **Out of retrieval scope, by construction, not by instruction:** any `untrusted`-status
  document (V2's poisoned-trap knowledge entries) must be filtered before it ever enters a
  domain agent's context window.
- Cross-workflow retrieval (e.g. a Batch Review agent reading PV evidence) is out of scope
  entirely — if a workflow genuinely needs cross-context evidence, that need routes through
  Evidence & Provenance's shared model, never a direct cross-context RAG call.

## Agent responsibilities

See `domain_model.md` §10 for the full named-agent table (Batch-Review Agent, PV-Intake
Agent, Supply-Planning Agent, Critic/Verifier Agent) with tools, authority limits, and
escalation conditions. Summary principle: **each domain agent is structurally incapable of
its workflow's prohibited action** — the constraint lives in the aggregate schema and the
tool's write capability, not in a prompt instruction alone.

## HITL & decision ownership

See `domain_model.md` §11. Summary: three named-but-TBD approver roles (blocked on EAB-3),
100% HITL routing for PV causality/seriousness/reportability and for any Supply Planning
option set (neither of these two workflows has any output that bypasses a human), and an
explicit default-safe rule: **HITL timeout means no action, never "proceed as AI
recommended."**

## Evidence & audit trail

Every domain agent output carries: evidence citations with authority status, a
confidence/abstention field, and an `AgentRun` record (LangSmith trace ID). This satisfies
both V2's inherited evidence standard and V3's new EU AI Act / ISO 42001 requirements
(Stage 19) — the same audit record serves both purposes, it is not duplicated
infrastructure.

## Evaluation intent (DDD vocabulary)

See `domain_model.md` §13 for example eval cases phrased in this document's terms. The
governing principle for Stage 14: eval cases should assert facts about domain
events/aggregates (e.g. "no `AgentAuthorityExceeded` event may appear in any trace"), not
about implementation details, so the eval suite stays meaningful even if the underlying
agent implementation changes.
