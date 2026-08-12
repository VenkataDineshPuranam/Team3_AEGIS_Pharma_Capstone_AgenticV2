# DMAIC Lens — Stage 04 (ADR)

**Full cycle.** ADR is the last designated full-DMAIC stage in the 01/02/03/04 set, and the
natural point to make Control concrete via revisit triggers.

## Define

Which ADR exists specifically to resolve a named waste or risk trade-off?

| ADR | Waste/risk it resolves |
|---|---|
| 003 | **Defects** — evidence-integrity failure; also Model waste (AI asked to judge trustworthiness it cannot verify) |
| 004 | **Defects** — the highest-severity failure mode (prohibited terminal action) |
| 005 | **Defects** — policy drift across contexts; accepts Integration waste in exchange |
| 006 | **Observability** — compliance evidence coupled to a third-party SLA |
| 007 | **Defects** — silent unsafe behavior on dependency failure |
| 008 | **Defects** — generalist-agent authority blurring; also Transportation (avoids agent-to-agent chains) |
| 001, 002 | Neither resolves a waste directly — both are scope/direction decisions recorded for traceability. Flagged honestly per the prompt's instruction to reject or flag ADRs that don't map to a root cause. |

## Measure

Metric and threshold that would prove each measurable decision right or wrong:

| ADR | Metric | Threshold |
|---|---|---|
| 003 | Eval cases citing `untrusted`/`superseded` docs | **Zero** citations; any occurrence = release-gate failure |
| 004 | `AgentAuthorityExceeded` events; schema-level contract test | **Zero** events; contract test must pass |
| 005 | Added latency from the extra Policy Engine hop (against `c4/dmaic_lens.md`'s 7-hop baseline) | To be set at Stage 15; if it becomes a material share of the latency budget, the ADR's revisit trigger fires |
| 006 | Audit-store write success rate while LangSmith healthy | 100% — proves the two sinks haven't silently collapsed into one |
| 007 | Eval pass rate with each dependency disabled in turn | All **correctness** gates pass (capability may degrade) |
| 008 | Cross-graph agent invocations | **Zero** — enforced structurally, verified by Stage 18 red-team |

## Analyze

Which ADRs explicitly prevent a named waste? 003 and 004 both push a check from
probabilistic (model judgment) to deterministic (schema/status lookup) — the classic
rules-before-LLM move that prevents Defects and Model waste simultaneously.

Which decisions risk *new* waste?
- **005** knowingly adds Integration waste (one more service, one more hop) and a new
  availability dependency — accepted only because it fails closed.
- **006** adds duplication (two sinks) — accepted because the alternative couples a
  regulatory obligation to a vendor SLA.
- **007** adds test burden (every fallback path needs coverage) — this is real Extra
  processing, accepted because untested fallbacks are worse than no fallbacks.

Architecture-review open issues that are really waste risks: EAB-2 remaining unresolved is
itself a Waiting/rework risk — if the sponsor later demands air-gap, everything built on
ADR-001 becomes rework. That is precisely why `architecture_review.md` names it a blocker to
escalate early rather than at Stage 20.

## Improve

The ADR set is the Improve artifact. Confirmed: every ADR except 001 and 002 maps to a
specific waste/root cause from Stages 01–03's registers (table under Define). 001 and 002 are
flagged as direction-setting rather than waste-resolving — recorded for decision traceability,
not claimed as improvements they aren't.

**The most valuable Improve this stage produced was not an ADR at all** — it was the
verification that produced ADR-003 and corrected a wrong DDD assumption. That correction
cost ~66 lines of reading and prevented an evidence-integrity rule from being built wrong
through three more stages.

## Control

Validation and revisit triggers are recorded per ADR (required field in each file). The
Control commitments that carry forward to Stage 09's consolidation and Stage 12's rollup:

1. Every `proposed` ADR must be re-examined when EAB-3 closes (that is what would allow DDD
   → `stable`, and therefore these → `accepted`).
2. ADR-007's revisit trigger is the sharpest in the set: sponsor confirmation of an air-gap
   requirement reopens ADR-001 entirely.
3. ADR-002's guardrail — *no claim of matching V2 behavior without verifying V2 code* — is
   now a standing rule for all later stages, with ADR-003 as the precedent for why.

## Waste registers

See `waste_register_downtime.md` and `waste_register_ai_specific.md` (this folder) — closed
out with ADR-level treatment decisions.
