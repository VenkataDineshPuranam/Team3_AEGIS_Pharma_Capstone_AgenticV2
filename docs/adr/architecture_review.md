# Architecture Review / Defense — Stage 04

**Review status: `conditional`**

Per `prompts/07_adrs.md`: under `provisional` DDD/C4, prefer `conditional` unless evidence
supports `pass`. DDD and C4 are both `provisional` (EAB-3 open), so `conditional` is the
correct outcome — with named conditions below.

## Defensibility checks

| Check | Result | Notes |
|---|---|---|
| C4 map matches DDD bounded contexts | **Pass** | Every container in `c4_containers.md` maps to a named context; the three core contexts remain peers with no direct coupling, and ADR-008 enforces that at the deployment level |
| Material trade-offs have ADRs | **Pass** | 8 ADRs cover runtime stack, build strategy, evidence authority, prohibited actions, governance placement, audit storage, degraded mode, and deployment topology. Two candidates deliberately deferred (MCP auth, cache topology) with stated reasons |
| Trust, authority, privacy, degraded-mode, prohibited writes visible on the map | **Pass** | `boundary_and_degraded_mode.md` covers all five explicitly; zero write integrations to brownfield systems |
| Gen AI / HITL / rules boundaries placed on the map | **Pass** | `gen_ai_boundaries.md` (DDD) + `c4_components.md` (HITL interrupt handler, Prohibited-Action Guard, per-tool write constraints) |
| Out-of-scope not smuggled into containers | **Pass, with one flag** | The 9-container design exceeds DDD's strict "minimum governed workflow," but each addition (Redis, LangSmith, separate audit store) is justified against a specific named risk rather than added speculatively — this tension is disclosed honestly in `c4/dmaic_lens.md` Analyze rather than hidden |

## Open issues

### Blockers (must resolve before the stage they block)

1. **EAB-2 / ADR-007 — air-gap requirement unconfirmed.** If the sponsor requires true
   offline operation, ADR-001's entire stack reopens. Blocks: nothing today, but blocks
   Stage 20 build if unresolved by then. **Escalate at Stage 21 sponsor review at the
   latest — earlier if convenient.**
2. **EAB-3 — no real HITL/context owners named.** Keeps DDD and therefore C4/ADRs
   `provisional`. Blocks Stage 16 (governance) from naming actual approvers.

### Accept as residual risk

3. **Shared blast radius from single-deployment topology (ADR-008)** — accepted; revisit
   trigger documented in the ADR.
4. **Three-layer redundancy for prohibited-action enforcement (ADR-004)** — accepted
   deliberately; the maintenance cost is the point, not an oversight.
5. **Dual-sink audit/trace duplication (ADR-006)** — accepted; Control check defined in
   `c4/dmaic_lens.md`.

## Correction issued this stage

**ADR-003 corrected a DDD error.** `domain_model.md` §8 had asserted that `superseded`
documents may be cited with a flag. Verification against V2's `authority_grader.py`
(`_MUST_NOT_CITE = {"untrusted", "superseded"}`) proved this wrong: superseded documents are
non-citable, exactly like untrusted. The DDD document has been corrected accordingly (a
Prompt 04 revision, as the ADR prompt's constraints require rather than silently changing
the model). **This is direct evidence that the ADR-002 residual risk — V3 drifting from V2's
actual verified behavior — is real, and that verification catches it.**

## Go-forward decision

**Proceed to the technical-design layer (`prompts/08_technical_design.md`)** under these
named conditions:

1. Technical design must treat ADR-005/006/007/008 as `proposed`, not settled — contracts
   derived from them carry the same provisional status.
2. EAB-2 must be escalated to the sponsor before Stage 20 begins.
3. Any further claim about matching V2 behavior must be verified against V2 code/data, per
   ADR-002's guardrail — not inferred from filenames. The ADR-003 correction is the
   precedent.
