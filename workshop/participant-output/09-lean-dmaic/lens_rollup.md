# Lens Roll-Up — Stages 01–08

**Executes:** `prompts/09_lean_dmaic.md` §0 (required first output)
**Artifact status: `stable`**

This is the reconciliation step, not a restart. Eight prior `dmaic_lens.md` files exist; this
document lists them, merges what they found, records where they disagreed, and names the gaps
that the rest of Stage 09 must close.

---

## 1. Prior lenses (all read this pass)

| Stage | Lens file | Depth | DMAIC focus | Top finding |
|---|---|---|---|---|
| 01 Discovery | [dmaic_lens.md](../../../docs/product/discovery/dmaic_lens.md) | **Full** | All five | V2's single-shot architecture is the root cause of the gap V3 exists to close; token/cost baseline **Unknown** |
| 02 SCQA/Frame | [dmaic_lens.md](../../../docs/product/scqa/dmaic_lens.md) | **Full** | Analyze | Sequencing (governance before architecture, architecture before app) is not one mitigation among many — it is the unifying mechanism behind almost every named risk |
| 02 DDD | [dmaic_lens.md](../../../docs/architecture/ddd/dmaic_lens.md) | **Full** | Analyze/Improve | The Defects risk is **structural, not behavioural**: "the data model might let an agent represent the prohibited action," not "an agent might choose it" |
| 03 C4 | [dmaic_lens.md](../../../docs/architecture/c4/dmaic_lens.md) | **Full** | Measure | **7 container/component crossings** on the common Batch Review path — the programme's only architectural number that is designed rather than guessed |
| 04 ADR | [dmaic_lens.md](../../../docs/adr/dmaic_lens.md) | **Full** | Control | Every ADR except 001/002 maps to a named waste; 001/002 flagged honestly as direction-setting, not waste-resolving |
| 05 Current state | [dmaic_lens.md](../../../docs/product/state/current/dmaic_lens.md) | Thin | Measure | 249 tracked files, **zero implementation**, zero evidence records; `eval-ai-cache/`'s 29 files unconsumed |
| 06 Interim state | [dmaic_lens.md](../../../docs/product/state/interim/dmaic_lens.md) | Thin | Analyze/Improve | The interim state is where the Unknown baselines finally become measurable; staged transition treats Overproduction and ambiguous-failure Defects |
| 07 Final state | [dmaic_lens.md](../../../docs/product/state/final/dmaic_lens.md) | Thin | Improve | The final state's most substantive contribution is **making incompleteness explicit** (open gates named rather than idealized away) |
| 08 Graphical | *(none)* | **Missing** | — | See §4, gap G1 |

**Mapping note.** `prompts/09_lean_dmaic.md` refers to prompts 01–08 (Discovery, SCQA, PRD,
DDD, Feature Specs, C4, ADR, Technical Design). This repo resequenced its stages
(`SPEC_DRIVEN_DEVELOPMENT.md` §3), so the actual set of prior lenses is the nine rows above.
Two prompt-level lenses have **no counterpart stage in this repo**: Feature Specs (prompt 05)
and Technical Design (prompt 08). Their content was not skipped — it was absorbed elsewhere
(DDD §14–15 carries the governed-slice scope; ADR-001/003/004/008 and
`c4_components.md` carry the technical contracts) — but there are no feature-level acceptance
criteria to align Measure targets against. That is gap G2 below, and it is the reason the
DMAIC plan's Measure section ties targets to **interim-state assumptions and ADR thresholds**
rather than to feature ACs.

## 2. Merged waste list (deduped)

Every waste named across all nine lenses and the five register pairs, collapsed to one row per
distinct finding. The full carried registers live in
[`waste_register_downtime.md`](waste_register_downtime.md) and
[`waste_register_ai_specific.md`](waste_register_ai_specific.md).

| # | Waste (merged) | First named | Refined at | Still open? |
|---|---|---|---|---|
| 1 | Authority leaking across an agent handoff (Defects) | 01 | 02 DDD → structural, not behavioural; 04 → ADR-004 | **Yes** — untested until interim assumption 1 runs |
| 2 | Evidence-integrity failure: citing `untrusted`/`superseded` (Defects) | 04 (via ADR-003) | — | **Yes** — interim assumption 2 |
| 3 | Over-built agent topology before cost is known (Overproduction) | 01 | 06 → one workflow first | **Yes** — depends on EAB-6 |
| 4 | Sequential stage-gate latency (Waiting) | 01 | 03 → async Agent Workers removes the addressable part | No — business-required NVA, accepted |
| 5 | HITL wait (Waiting) | 01 | 03, 04 | No — regulatory, accepted |
| 6 | Generalist agent wasting specialist capability (Non-utilised talent) | 01 | 04 → ADR-008 | No — resolved by design |
| 7 | Per-hop context re-serialization (Transportation) | 01 | 03 → **measured: 7 crossings** | Partly — designed, not measured in a running system |
| 8 | Stale cache serving superseded evidence (Inventory) | 01 | 04 → ADR-003 guardrail; 06 → cache excluded from interim | **Yes** — deferred to Stage 14/15 |
| 9 | Repeated evidence-citation discipline (Motion) | 01 | — | No — deliberate friction, no action |
| 10 | Ontology arriving after agents need it (Extra processing) | 01 | — | **Yes** — sequencing risk, see §5 contradiction C1 |
| 11 | Fallback-path test burden (Extra processing) | 04 | — | No — accepted with ADR-007 |
| 12 | Token multiplication across agent turns (Token) | 01 | 02 SCQA → the category sequencing exists to control; 04 → budgets deferred | **Yes** — EAB-6, still Unknown |
| 13 | Unbounded/unscoped retrieval (Retrieval) | 01 | 02 DDD → per-context RAG scoping | Partly — designed, unimplemented |
| 14 | Blind retry burning model calls (Model) | 01 | — | **Yes** — no owning stage assigned; see gap G3 |
| 15 | Asking the model to judge trustworthiness (Model) | 04 | — | No — ADR-003 makes it a deterministic lookup |
| 16 | HITL over-routing or under-routing (Human-review) | 01 | 04 → 100% routing for PV/Supply is regulatory, not waste | Partly — Batch Review risk-tiering deferred to Stage 16 |
| 17 | Full eval suite as a velocity bottleneck (Evaluation) | 01 | 04 → fast-subset split deferred | **Yes** — Stage 14 |
| 18 | MCP tool contract drift (Integration) | 01 | 04 | **Yes** — Stage 11 |
| 19 | Extra hop from the separate Policy Engine (Integration) | 02 DDD | 04 → ADR-005 accepts it knowingly | No — accepted, with a revisit trigger |
| 20 | Per-agent context reconstruction (Context) | 01 | 04 → LangGraph shared state is the single source | Partly — Stage 10 must design the schema |
| 21 | Trace miscalibration: noise, or PII over-capture (Observability) | 01 | 03 → separate audit store; 04 → ADR-006 | **Yes** — Stage 17 |
| 22 | Compliance evidence coupled to a vendor SLA (Observability) | 03 | 04 → ADR-006 | No — resolved by design |
| 23 | Re-deriving material already in `eval-ai-cache/` (Overproduction) | 05 | — | **Yes** — NAB-4, Stages 14/15/17 |
| 24 | Duplicating prompts into `plans/active/` (Overproduction) | 05 | — | **Yes** — NAB-2, doc fix |

24 distinct findings; **11 still open**, 5 partly open, 8 closed by design decisions.

## 3. Where the lenses disagreed — reconciled

**C1 — Ontology sequencing.** Stage 01's DOWNTIME register (Extra processing) says *"sequence
Stage 13 before Stage 10 is finalized, or design Stage 10 agents against the ontology contract
from the start."* The stage order in `SPEC_DRIVEN_DEVELOPMENT.md` §3 puts agentic architecture
at 10 and ontology at 13 — the opposite order. Stage 06's interim state resolves this in
practice ("Stage 13 provides enough semantic layer for scoped, status-aware retrieval") but
never states which of Stage 01's two options was taken.
**Reconciled here: option (b).** Stage 10 designs agents against an ontology *contract*, and
Stage 13 fills it in. This is recorded as a build constraint, not left implicit — see
[`build_constraints_from_lean.md`](build_constraints_from_lean.md) BC-4.

**C2 — Minimalism vs. operational completeness.** DDD §14 argues for a "minimum governed
workflow"; C4 lands on 9 containers. `c4/dmaic_lens.md` and `architecture_review.md` both
disclose the tension rather than hiding it, and the interim state effectively resolves it by
running a **reduced** container set (no Redis, minimal audit store). **Reconciled: not a
contradiction** — DDD's minimalism governs the interim state, C4's completeness governs the
final state. Recorded so the difference is deliberate rather than a drift finding at Stage 12.

**C3 — Token budgets: which stage owns them?** Stage 01 says "quantify before Stage 04 locks
topology." Stage 04 did **not** quantify — it deferred numeric budgets to Stage 15, and
Stage 06 moved first measurement into the interim state. So Stage 01's stated precondition was
**not met**, and the topology (ADR-008) was locked without a cost number.
**Reconciled honestly: this is an accepted, un-mitigated sequencing debt, not a closed item.**
ADR-008's constraints (one graph per workflow, no cross-graph calls) are conservative in the
cost-reducing direction, which is why locking early was tolerable — but if interim assumption
6 measures cost far above expectation, ADR-008 is the decision that gets revisited. Carried
into the DMAIC plan's Control section as an explicit revisit trigger.

**C4 — ADR count.** `architecture_review.md` and `decision_index.md` both state **8 ADRs**;
the repo now holds **9** (ADR-009 Azure, added after the review passed). ADR-009 amends
ADR-001 and ADR-007 and carries an open sub-decision (LLM route). **Reconciled: a documentation
defect, not a design defect** — logged in [`structural_reopen.md`](structural_reopen.md) as a
documentation reopen (D1).

## 4. Gaps in the prior lenses

| ID | Gap | Consequence | Handled where |
|---|---|---|---|
| **G1** | Stage 08 (graphical views) produced no `dmaic_lens.md` | Minor — diagrams are views over stable sources and introduce no new waste. Assessed and closed here rather than back-filled: writing a lens for a view layer would itself be Overproduction | Closed in this document |
| **G2** | No feature-spec stage exists, so there are **no feature ACs** to tie Measure targets to | Measure targets must anchor to interim assumptions and ADR thresholds instead | [`dmaic_plan.md`](dmaic_plan.md) §Measure |
| **G3** | "Blind retry" (Model waste) was assigned to *prompt* 08 technical design, which has no stage in this repo — so it currently has **no owner** | A real, unowned waste item | Assigned to Stage 10 in [`build_constraints_from_lean.md`](build_constraints_from_lean.md) BC-5 |
| **G4** | Thin lenses (05–07) carry no waste registers of their own | Their findings existed only in prose | Folded into the merged registers this stage |
| **G5** | No lens ever measured **anything about a running system** — every number in the programme is designed, counted from files, or Unknown | The whole Measure column is pre-execution | Stated plainly in `dmaic_plan.md`; drives the Measure-first ordering |

## 5. What this roll-up changes

Three things this reconciliation produced that no single prior lens contained:

1. **C3** — the token-budget precondition from Stage 01 was silently not met. Now explicit,
   with a named revisit trigger on ADR-008.
2. **G3** — a waste item ("blind retry") had lost its owner in the resequencing. Now assigned.
3. **C1** — the ontology/agent ordering was resolved in practice but never written down. Now a
   build constraint.
