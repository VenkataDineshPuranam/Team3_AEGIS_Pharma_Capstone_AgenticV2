# Board & Portfolio Context — Stage 21 gap-closure (INJ-001, INJ-002, INJ-003, INJ-004, INJ-005)

**Executes:** closes five D01 injects that are business-strategy questions, not technical
failure modes: a board-mandated lead-time compression target (INJ-001), conflicting
departmental success metrics (INJ-002), the no-AI counterfactual challenge (INJ-003), a
patent-cliff acceleration pressure (INJ-004), and an acquired-biotech integration
(INJ-005).

## Why this is a document, not code

Every other inject closed at Stage 21 got a fixture, a tool, a test, or a governance rule
— something a script can run and get a pass/fail from. These three cannot honestly get
that treatment. "The board wants release lead time down 14%" is not a bug in this system;
it is a fact about the organization AEGIS operates inside. No code path "covers" a board
KPI target any more than a car's cruise control "covers" the driver's decision about which
route to take. The only honest way to close a business-strategy inject is to show that the
governed system's own design has already reasoned through the tension it creates — which
is what this document is for.

## INJ-001 — 14% release lead-time compression, without weakening Quality authority

The board's ask has two halves that are usually in tension: go faster, and do not touch
who certifies. AEGIS's actual architecture resolves this by construction rather than by
trading one against the other:

- **Where AEGIS removes time**: the slow part of batch review is rarely the QP's own
  judgment — it is the mechanical work of walking genealogy, lab results, environmental
  monitoring, deviations, CAPA, change control, validation state, and supplier evidence to
  find out whether anything is missing or contradictory *before* a human ever opens the
  file. That reconciliation is exactly what `batch.reconcile` does today, deterministically,
  in milliseconds, over real evidence (`services/integration/batch_reconcile.py`).
- **Where AEGIS refuses to remove time**: certification itself. `packages/domain/payloads.py`'s
  `BatchPayload`/`ReconciliationFinding` cannot represent a release/reject/reprocess/
  relabel/recall determination — not "won't," *cannot*, per ADR-004's three independent
  layers. The 14% has to come entirely from the reconciliation-and-triage side, because
  the certification side has no lever this system is willing to build one for.

This is falsifiable, not a promise: any future feature proposing to speed up certification
itself (rather than what feeds into it) would have to reopen ADR-004, which is exactly the
friction this system's own design intends that proposal to meet.

## INJ-004 — patent-cliff urgency accelerating a new indication

Urgency pressure on a regulated pathway is precisely the condition under which shortcuts
get proposed and precisely the condition this system's governance layer is built not to
bend under. Two structural facts hold regardless of how much commercial pressure exists:

- The denial-of-wallet ceiling (`infra/policies/denial_of_wallet_guardrail.py`) and the
  evidence-authority gate (ADR-003) apply identically under time pressure and without it —
  neither has a "priority" override, and none was added for this document. Urgency cannot
  purchase a bypass because no purchase mechanism exists.
- `regulatory_completeness` (Stage 21, D07) exists to make submission-readiness gaps
  visible *earlier*, not to make them disappear — it surfaces IDMP identity conflicts,
  labeling divergence, and eCTD sequence gaps as structured findings a human resolves,
  the same reconciliation pattern as batch review. Accelerating a submission timeline
  means finding out about a gap in week 2 instead of week 14, not skipping the check.

## INJ-005 — acquired-biotech integration, incompatible identifiers and quality processes

An acquisition introduces exactly the kind of identity-conflict scenario `research_review`
(Stage 21, D02) was built to surface: `compound_identity` findings exist precisely because
two organizations' local codes can collide with different underlying structures — this is
not a hypothetical, it is fixture `R-003` in this repository, reconciled and audited
end-to-end today. The acquired organization's quality processes being on a different
system is a real integration project outside this application's boundary (a new source
system feeding evidence, not a new capability this LangGraph app needs); what AEGIS commits
to is that once evidence from the acquired system enters the knowledge graph
(`packages/domain/kg/ingest.py`'s same hash-verified ingestion path, not a bespoke one),
every governance layer already built — evidence authority, prohibited-action guards, HITL
— applies to it without modification.

## INJ-002 — conflicting departmental success metrics

Manufacturing rewards throughput, Quality rewards deviation containment, Supply rewards
service level, Clinical rewards database-lock speed — four metrics that can each be
optimized against the others' interest. AEGIS's own architecture is deliberately not a
fifth lever any one department could point at those metrics: `ADR-008` requires one graph
per workflow with no cross-workflow agent call, so there is no single "AEGIS score" a
department could push on to trade another department's outcome away. Each workflow's
findings are scoped to its own evidence and its own accountable human role
(`docs/governance/hitl_control_model.md`) — a Supply Chain VP reading `supply_planning`'s
output cannot use it to pressure a Quality decision in `batch_review`, because the two
runs share no state and no agent. This does not resolve the four departments' incentive
conflict — that is a real compensation/KPI-design decision outside any system's
authority — but it closes the part of the inject that is about AEGIS itself: this system
cannot be the mechanism by which one department's metric quietly overrides another's.

## INJ-003 — the no-AI counterfactual

A process-excellence team's claim that workflow redesign and master-data repair could
deliver most of the benefit without AI deserves a real answer, not a dismissal. Here is
the honest one: they would be right about a real portion of the benefit, and AEGIS's own
design already concedes exactly which portion.

- **What workflow redesign and master-data repair alone WOULD fix**: duplicate or
  malformed records, inconsistent naming across systems, slow manual routing. All of that
  is upstream of AEGIS entirely — cleaning `knowledge/knowledge_catalog.csv`-equivalent
  source data, or redesigning who reviews what in which order, needs no LLM and no graph.
- **What redesign alone CANNOT fix, which is what the six governed tools actually add**:
  reconciling structured findings across many evidence categories deterministically and
  citably in the time it takes to answer an API call (`batch.reconcile`,
  `research.reconcile`, `clinical.integrity_check`, `regulatory.completeness_check`,
  `pv.duplicate_check`, `supply.generate_options` — all read-only, all evidence-cited,
  verified by `security/sbom/verify_sbom.py`'s sibling manifest check in
  `services/integration/tool_manifest.py`), plus a structured, append-only audit record
  of who reviewed what and why (`services/integration/audit_store.py`) that a
  process-redesign project does not produce as a byproduct.

The honest comparison is: redesign fixes the inputs, AEGIS fixes the reconciliation and
accountability layer on top of them, and neither substitutes for the other. A real
no-AI-baseline measurement (V1's own `data/no_ai_baselines.csv` concept) is the correct
instrument to quantify this precisely — this document states the structural argument for
why some benefit survives a no-AI counterfactual and some does not, which is what a
tabletop inject asks for; a dollar figure requires the same real-usage measurement (U1)
`docs/quality/performance/token_economics.md` §0 already refuses to invent.

## What this document is not

It is not a business case, a cost-benefit analysis, or a project plan for any of these
three scenarios — those require real organizational decisions (headcount, timeline,
integration scope) this document has no authority to make. What it closes is narrower and
honest: for each of the three board-level pressures the V1 tabletop exercise named, this
system's actual, already-built design has a real, checkable answer for the technical half
of the tension, and states plainly where the answer is organizational rather than
technical.
