# Interim State — Transition Architecture — Stage 06

**Executes:** `prompts/03_prd_vision.md` (transition-state scope)
**Builds on:** Stage 05 current state; DDD `domain_model.md` §14–15; ADR-004/007/008
**Artifact status: `stable`** (DDD and C4 both `stable`; EAB-2/EAB-3 closed)

---

## 1. Why an interim state exists at all

Current state (Stage 05): design complete through ADR, **zero implementation**. Final state
(Stage 07): three governed workflows running as multi-agent graphs with full governance,
caching, observability, security, and compliance evidence.

Going directly from one to the other would mean proving every risky assumption
simultaneously — agent handoff safety, cache correctness, HITL routing, token economics,
degraded-mode behavior — with no way to isolate which one failed. The interim state exists
to **prove the riskiest assumptions at the smallest possible scale** before the design is
replicated across three workflows.

This is the direct application of DDD §14's "minimum governed workflow" and the SCQA
Answer's sequencing principle (`docs/product/scqa/scqa.md`): prove the narrowest agentic
slice is safe before composing agents further.

## 2. What the interim state is

**One workflow — Batch Review — running end-to-end as a real multi-agent graph.**

Batch Review is the recommended pilot per DDD §15, on evidence: Stage 01's sufficiency
scoring rated its evidence base **Strong**, and V2's most directly applicable graders
(`authority_grader.py`, `temporal_unit_grader.py` — both verified at Stage 04) are
evidence/authority-oriented, which is Batch Review's core concern.

### In scope for the interim state

| Component | Interim scope | Full scope deferred to |
|---|---|---|
| Domain agents | **One** — Batch-Review Agent | PV-Intake, Supply-Planning agents (final) |
| Critic/Verifier | Yes — required, since it is the prohibited-action checkpoint | — |
| HITL interrupt | Yes — **EU Qualified Person** is the named approver for Batch Review (EAB-3 closed) | Approvers for the other two workflows (final) |
| MCP tools | **Two** — Evidence Retrieval (scoped) + Reconciliation | Duplicate-Check, Option-Generation (final) |
| Governance/Policy Engine | Yes — Prohibited-Action Guard must exist from day one (ADR-004) | Full policy register (Stage 16) |
| Evidence & Provenance | Yes — with the ADR-003 status gate (`untrusted`/`superseded` non-citable) | Full ontology/semantic layer (Stage 13) |
| Redis cache | **No** — deliberately excluded | Final (Stage 14/15) |
| LangSmith | Yes — tracing from the start, so there is trace data to reason about | Full dashboards/alerting (Stage 17) |
| Audit/Evidence Log Store | Yes — minimal, but present (ADR-006 says it must not be an afterthought) | Full retention/compliance (Stage 19) |

### Deliberately excluded from the interim state, with reasons

- **Redis cache.** Caching adds the stale-authority correctness risk (ADR-003 guardrail,
  `discovery.md` H6) on top of the agent-correctness risk. Introducing both at once makes
  failures ambiguous. Cache lands only after the uncached path is proven correct.
- **The other two workflows.** Replicating an unvalidated pattern three times is
  Overproduction waste; the pattern must be proven once first.
- **Cross-workflow anything.** ADR-008 forbids cross-graph agent calls permanently, so
  there is nothing to prototype here.

## 3. What the interim state must prove before the final state begins

These are the exit criteria — the interim state's entire purpose:

| # | Assumption under test | Pass condition |
|---|---|---|
| 1 | Prohibited actions are structurally unrepresentable (ADR-004) | A red-team attempt to produce a batch release/reject recommendation fails at the **schema** layer, not merely by model refusal |
| 2 | Evidence authority gating works (ADR-003) | Zero citations of `untrusted`/`superseded` documents; an embedded instruction in a retrieved document does not change agent behavior |
| 3 | HITL routing and default-safe timeout work (DDD §11) | Escalation fires as designed; a timed-out approval results in **no action**, never auto-proceed |
| 4 | Degraded mode is safe (ADR-007) | With the LLM provider disabled, the deterministic path still runs and the system abstains rather than guessing; with LangSmith disabled, requests still succeed and audit records still write |
| 5 | Policy Engine fails **closed** (ADR-005) | With the Policy Engine unreachable, requests are refused, not passed through |
| 6 | Token economics are knowable (EAB-6) | Actual measured tokens/cost per Batch Review run — the number that has been "Unknown" since Stage 01 |
| 7 | Hop count matches design (C4 `dmaic_lens.md`) | Measured path ≈ the 7-crossing baseline, or a documented reason why not |

Assumption 6 matters disproportionately: **it is the first point in the whole programme
where a real cost number exists.** Every token/cost decision so far has been explicitly
marked Unknown. If measured cost is far off expectation, the final state's agent topology
should change *before* it is built three times over, not after.

## 4. Sequencing: which stages produce the interim state

| Stage | Contribution to the interim state |
|---|---|
| 10 (agentic architecture) | The Batch-Review graph design, state schema, HITL interrupt points |
| 11 (MCP) | The two interim tools' contracts |
| 12 (skills/hooks) | The Prohibited-Action Guard as an enforced hook (not an instruction) |
| 13 (ontology/KG) | Enough semantic layer for scoped, status-aware retrieval |
| 14 (eval-ai-cache) | The eval harness and the assumption-tests in §3 — **the cache half of this stage is deferred to the final state** |
| 16 (governance) | Policy register, HITL routing rules |
| 17 (observability) | LangSmith tracing sufficient to answer §3's questions |
| 20 (implementation) | The actual code — still last |

Note that Stage 15 (performance/Redis) and Stage 19 (compliance) contribute **nothing** to
the interim state by design: there is no cache to tune, and compliance evidence requires a
system that has actually run.

## 5. Risks specific to the interim state

1. **Single-approver validation.** The interim state exercises HITL with one named approver
   role (EU Qualified Person). It proves the *mechanism*, but the other two workflows' routing
   — notably Supply Planning's dual Supply-Chain-VP-plus-Quality approval — is untested until
   the final state.
2. **Single-workflow bias.** Batch Review's evidence-reconciliation shape may not generalize
   to PV's duplicate/clock semantics or Supply's option-ranking. Mitigation: Stage 07's final
   state must explicitly re-check each interim conclusion against the other two workflows
   rather than assuming transfer.
3. **Proving correctness uncached, then adding cache.** The cache is introduced *after*
   correctness is proven, which means cache-correctness becomes a distinct, separately-tested
   risk (Stage 14's cache-correctness evals) rather than a confound.

---

## Lean / DMAIC lens

See `dmaic_lens.md` (this folder).
