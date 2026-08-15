# Architecture Review / Defense — Stage 04

**Review status: `pass`** (upgraded from `conditional` when both blockers closed)

This review was originally `conditional` because DDD and C4 were `provisional` and four ADRs
were `proposed`, pending two open backlog items. **Both are now closed:**
- **EAB-3** — accountable HITL approvers named from V1's `case/STAKEHOLDER_PACK.md`
  (see [`../governance/hitl_control_model.md`](../governance/hitl_control_model.md)). DDD → `stable`.
- **EAB-2** — sponsor confirmed cloud-connected operation. ADR-007 ratified, C4 → `stable`.

All 9 ADRs are `accepted`, with no open sub-decisions (ADR-009's LLM-hosting route, added at
Stage 16, confirmed **Route A** ahead of Stage 20a); no artifact rests on an unconfirmed
assumption. `pass` is now the evidence-supported outcome.

## Defensibility checks

| Check | Result | Notes |
|---|---|---|
| C4 map matches DDD bounded contexts | **Pass** | Every container in `c4_containers.md` maps to a named context; the three core contexts remain peers with no direct coupling, and ADR-008 enforces that at the deployment level |
| Material trade-offs have ADRs | **Pass** | 9 ADRs cover runtime stack, build strategy, evidence authority, prohibited actions, governance placement, audit storage, degraded mode, deployment topology, and cloud platform. Two candidates deliberately deferred (MCP auth, cache topology) with stated reasons |
| Trust, authority, privacy, degraded-mode, prohibited writes visible on the map | **Pass** | `boundary_and_degraded_mode.md` covers all five explicitly; zero write integrations to brownfield systems |
| Gen AI / HITL / rules boundaries placed on the map | **Pass** | `gen_ai_boundaries.md` (DDD) + `c4_components.md` (HITL interrupt handler, Prohibited-Action Guard, per-tool write constraints) |
| Out-of-scope not smuggled into containers | **Pass, with one flag** | The 9-container design exceeds DDD's strict "minimum governed workflow," but each addition (Redis, LangSmith, separate audit store) is justified against a specific named risk rather than added speculatively — this tension is disclosed honestly in `c4/dmaic_lens.md` Analyze rather than hidden |

## Open issues

### Blockers

**None remaining.** Both former blockers are closed:

1. ~~EAB-2 / ADR-007 — air-gap requirement~~ — **closed.** Sponsor confirmed cloud-connected
   operation. The air-gapped production variant is recorded as a known limitation in ADR-007
   rather than silently dropped, so a future reader evaluating this as a production design
   sees the constraint.
2. ~~EAB-3 — no real HITL/context owners~~ — **closed.** Named from V1's existing stakeholder
   pack, including the negative constraint that Manufacturing VP is explicitly not a batch
   approver.

### Accept as residual risk

3. **Shared blast radius from single-deployment topology (ADR-008)** — accepted; revisit
   trigger documented in the ADR.
4. **Three-layer redundancy for prohibited-action enforcement (ADR-004)** — accepted
   deliberately; the maintenance cost is the point, not an oversight.
5. **Dual-sink audit/trace duplication (ADR-006)** — accepted; Control check defined in
   `c4/dmaic_lens.md`.

## Correction issued this stage

**ADR-003 corrected a DDD error.** `domain_model.md` §8 had asserted that `superseded`
documents may be cited with a flag. Verification against V1's `authority_grader.py`
(`_MUST_NOT_CITE = {"untrusted", "superseded"}`) proved this wrong: superseded documents are
non-citable, exactly like untrusted. The DDD document has been corrected accordingly (a
Prompt 04 revision, as the ADR prompt's constraints require rather than silently changing
the model). **This is direct evidence that the ADR-002 residual risk — V2 drifting from V1's
actual verified behavior — is real, and that verification catches it.**

## Go-forward decision

**Proceed to the technical-design layer (`prompts/08_technical_design.md`) and Stages 09+
without conditions on artifact status.** All 9 ADRs are ratified and DDD/C4 are `stable`
(ADR-009 added at Stage 16; its LLM-route sub-decision resolved to Route A ahead of
Stage 20a).

Two standing rules carry forward (obligations, not blockers):

1. **Any claim about matching V1 behavior must be verified against V1 code/data**, per
   ADR-002's guardrail — never inferred from filenames. The ADR-003 correction is the
   precedent for why this rule exists.
2. **Interim-state assumptions 1 and 2 remain stop-the-line conditions** — if
   prohibited-action or evidence-authority enforcement fails in practice, ADR-004 or ADR-003
   is invalidated and the design must be reopened regardless of this `pass`.
