# EU AI Act — Risk Classification (Stage 19)

**Executes:** `prompts/23_compliance.md` §1
**Evidence basis:** Derivation, reasoned from this repo's own ADRs/design + V2's
`case/REGULATORY_BOUNDARY_PACK.md` (real source, read this stage — "research anchors, not
legal conclusions. Participants must determine applicability").
**Status: reasoned classification, not a legal determination.** Per the boundary pack's own
framing, this document states the reasoning transparently so a qualified legal/regulatory
reviewer can check it — it does not substitute for one. Recorded as an open item in
`gap_assessment.md` §1, not silently treated as closed.

---

## 1. The boundary pack's own questions, answered against this system

| Question (`REGULATORY_BOUNDARY_PACK.md`) | Answer, with citation |
|---|---|
| Does it create/modify/maintain/archive/retrieve/transmit a regulated record? | **Retrieves and reads** regulated evidence (`evidence.retrieve`, read-only per ADR-004 layer 2); **never writes** to any regulated system — no write-capable tool exists anywhere in this design |
| Does it influence product quality, trial integrity, participant safety, PV, labeling, release, or recall? | It **informs** a human who makes that decision — it does not itself decide. `Batch`/`ShortageOption`/PV output schemas structurally cannot represent a disposition (ADR-004 layer 1, `packages/domain/payloads.py`) |
| Is the output advisory, workflow-supporting, determinative, or executed through tools? | **Advisory only.** `DecisionSupportOutput` (the only thing `synthesize` can produce) has no field capable of representing a determination — confirmed at the type level, not merely a policy statement |
| Which human role remains accountable, and what evidence must they inspect? | Named, not generic: EU Qualified Person (Batch Review), Global Head of PV (PV Intake), Supply Chain VP + Quality co-approver (Supply) — `hitl_control_model.md` §2. They inspect the cited evidence and the reconciliation findings, both structured and traceable |
| What validation/assurance/change-control/retention approach is proportionate? | Stage 14's eval harness (63 scenarios), Stage 18's red-team (3 real attacks attempted), audit trail retention (structure fixed, duration open — `memory_design.md` §5) |
| What is prohibited even if technically possible? | Batch release/reject/reprocess/relabel/recall; PV causality/seriousness/reportability determination; Supply allocation/reservation/shipment — enumerated in ADR-004, enforced at three independent layers |

## 2. Reasoning toward a classification

The EU AI Act's risk tiers turn substantially on whether a system is a "safety component" of
a product already subject to sectoral conformity-assessment legislation (Article 6(1)), or
whether it falls under one of Annex III's explicitly listed high-risk use cases (biometrics,
critical infrastructure, education, employment, essential services/credit, law enforcement,
migration, justice/democratic processes — none of which name pharmaceutical manufacturing,
pharmacovigilance, or supply planning directly).

**This system's own design characteristics, all independently verified this session or
earlier stages, point toward the system being decision-support rather than a safety
component in its own right:**

1. **No autonomous terminal action is representable** (ADR-004, three independent layers,
   verified live this session against a real model — `security/abuse-cases/T-01_indirect_
   prompt_injection.md`).
2. **Human oversight is structural, not incidental** — every run with a work product routes
   through a named, accountable human role before anything leaves the system
   (`hitl_control_model.md`, `failure_and_loop_guards.md` §5). Verified this session: 99 real
   `AgentRun` records exist, none reaching a terminal `completed` state without either an
   explicit HITL resolution or a documented abstention.
3. **Transparency is built in**, not bolted on — every claim in a draft output must cite
   real, retrievable evidence (ADR-003), traceable via `evidence_id`.
4. **Logging/technical documentation exists as a structural requirement**, not a
   nice-to-have — `finalize`'s audit write is not optional (verified: zero `AgentRun`-less
   completions across every real run this session produced).

**Provisional reasoning, stated as reasoning, not fact:** the system likely does **not** meet
Annex III's enumerated high-risk categories directly. Whether it is a "safety component" under
Article 6(1) turns on whether the *product it supports* (a GxP batch, a PV signal, a supply
allocation) is itself subject to sectoral safety legislation in a way that makes an AI
decision-support tool touching that workflow a regulated safety component — **this is
precisely the kind of determination the boundary pack says participants must make, and this
project has not made it with legal authority.** Recorded as **Gap G-1** in
`gap_assessment.md`.

## 3. What follows regardless of final tier (transparency + human oversight obligations)

Independent of the final risk-tier determination, the Act's baseline obligations for any AI
system interacting with the workflows here (transparency to affected persons, human
oversight, technical documentation, logging) are **already satisfied by design**, per §1's
table — these obligations do not wait on the classification question being resolved, and this
system was built to satisfy them regardless of tier (a deliberate design choice traceable to
ADR-004/005/006, not a compliance-driven retrofit).

## 4. Per-workflow note

**Batch Review** is the only workflow with real operational evidence (Stage 20a). PV Intake
and Supply Planning are `provisional` by design (RR-2) — this classification's reasoning
extends to them structurally (the same ADR-004/hitl_control_model.md invariants apply), but
has **no operational evidence** behind it for those two workflows, unlike Batch Review's 99
real runs. Stated honestly, not assumed to transfer.
