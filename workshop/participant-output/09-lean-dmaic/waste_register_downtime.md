# DOWNTIME Waste Register — Governing Consolidation (Stage 09)

**Executes:** `prompts/09_lean_dmaic.md` §B
**Supersedes as the working register:** the five prior stage copies
(`product/discovery/`, `product/scqa/`, `architecture/ddd/`, `architecture/c4/`, `adr/`).
Those remain as the per-stage record; **this is the single register Stages 10–21 work from.**
**Artifact status: `stable`**

Columns: where observed (current and/or proposed system), **observed vs hypothesized**,
impact, classification, and the eliminate/simplify action with its owner.

> **Standing caveat.** No V3 system has ever run. Rows marked *hypothesized* are design-time
> risk assessments, not measurements. Per `prompts/09_lean_dmaic.md`'s constraint, **no row
> below is described as fixed** — rows have owning decisions and scheduled proofs, which is
> not the same thing.

---

## D — Defects

| # | Where | Obs/Hyp | Impact | Class | Action | Owner |
|---|---|---|---|---|---|---|
| D1 | **Proposed** — agent handoff at a context boundary drops the authority constraint, letting a terminal decision (release/reject/allocate/reportability) be produced | **Hypothesized** | **Highest severity in the register** — a prohibited terminal decision is a GxP/PV incident, not a bug | Pure waste | Structural unrepresentability, 3 layers: no schema field, no tool method, runtime guard (ADR-004). Proof = interim assumption 1, blocking at the **schema** layer, not by model refusal | Stages 12, 16, 20 |
| D2 | **Proposed** — an answer is built on `untrusted` or `superseded` evidence; or retrieved content carries an embedded instruction that changes agent behaviour | **Hypothesized** (the *rule* is Fact — V2's `authority_grader.py` defines `_MUST_NOT_CITE = {"untrusted","superseded"}`) | High — evidence integrity is the core V2 inheritance | Pure waste | Deterministic status gate at the retrieval boundary, applied **before** ranking; content never self-declares authority (ADR-003). Proof = interim assumption 2 | Stages 11, 13, 14 |
| D3 | **Proposed** — policy interpreted locally and differently in each of the three contexts (policy drift) | **Hypothesized** | Medium-high — divergence is silent until an incident | Pure waste | Governance as an **open-host service**, not a shared kernel, in a separate container that **fails closed** (ADR-005). Proof = interim assumption 5 | Stage 16 |
| D4 | **Proposed** — a dependency fails and the system guesses instead of abstaining | **Hypothesized** | High — a confident wrong answer is worse than no answer | Pure waste | Degraded-mode-safe: every hosted dependency has a defined safe fallback; abstain rather than guess (ADR-007). Proof = interim assumption 4 | Stages 17, 20 |
| D5 | **Proposed** — cache returns an answer built on since-superseded evidence | **Hypothesized** | High | Pure waste | Cache keys must incorporate document status; never serve as-if-cached when the cache is unavailable. **Cache excluded from the interim state entirely** so this risk is isolated | Stages 14, 15 |

## O — Overproduction

| # | Where | Obs/Hyp | Impact | Class | Action | Owner |
|---|---|---|---|---|---|---|
| O1 | **Proposed** — building more agents/tools than the three workflows need, before cost is known | **Hypothesized** | Medium — direct cost, plus rework if topology must change | Pure waste if realized | ADR-008 constrains topology (one graph per workflow, no generalist agent, no cross-graph calls). **Note the honest gap:** the stated precondition (quantify cost first) was not met — see `lens_rollup.md` C3, trigger T-3 | Stage 10 |
| O2 | **Proposed** — replicating an unvalidated agent pattern across three workflows | **Hypothesized** | Medium-high — 3× the rework | Pure waste if realized | Interim state runs **one** workflow (Batch Review) end-to-end first | Stages 10–20 |
| O3 | **Current** — 29 files of directly applicable material in `eval-ai-cache/` (24-part brownfield-evals runbook + Redis + OTel runbooks) sit unconsumed; V2's 32 knowledge docs and fixtures likewise | **Observed** (counted at Stage 05) | Medium — re-deriving what is already written | Pure waste | Stages 14/15/17 must consume, not re-derive (NAB-4). Trigger T-7 enforces it | Stages 14, 15, 17 |
| O4 | **Current** — method doc says stage specs go in `plans/active/`; the directory is empty because `prompts/` already serve that role | **Observed** | Low — documentation accuracy only | Pure waste (if resolved by duplicating) | **Correct the method doc, do not duplicate the prompts** (NAB-2) — duplicating would violate "nothing written twice" | Stage 21 |
| O5 | **Current** — scope pressure to add V2's workflows D/E (clinical trial, discovery science), which appear in V2 eval datasets `S13`/`S14` | **Observed** (the material exists; the pressure is real) | Medium | Pure waste | Explicitly excluded: V2's mandate names **three** mandatory workflows; the extras came from a prior participant run | Closed at Stage 07 |

## W — Waiting

| # | Where | Obs/Hyp | Impact | Class | Action | Owner |
|---|---|---|---|---|---|---|
| W1 | **Current** — the SDD pipeline is sequential; each stage waits on the prior stage's exit criteria | **Observed** | Low | **Business-required NVA** | None. This is the method working as designed | — |
| W2 | **Proposed** — HITL approval wait | **Hypothesized** | Medium latency, zero optionality | **Business-required NVA** — regulatory | Not optimized away. Only the *timeout behaviour* is controlled: timeout ⇒ **no action**, never auto-proceed. Proof = interim assumption 3 | Stage 16 |
| W3 | **Proposed** — a long-running Supply Planning option search blocks the synchronous request path | **Hypothesized** | Medium | Pure waste (the addressable part of Waiting) | Agent Workers as a container distinct from Orchestrator API | Stages 10, 20 |
| W4 | **Programme** — the final state cannot begin in earnest until the interim state's seven assumptions are tested | **Observed** (a planned wait) | Medium schedule impact | **Business-required NVA** — deliberate governance latency, same class as W1/W2 | Accepted. This is what makes failures attributable | — |

## N — Non-utilised talent

| # | Where | Obs/Hyp | Impact | Class | Action | Owner |
|---|---|---|---|---|---|---|
| N1 | **Proposed** — a single generalist agent would have to hold all three distinct prohibition sets at once, and none of the three domain vocabularies well | **Hypothesized** | Medium — quality and authority-blurring | Potential pure waste | Specialist domain agent per bounded context + a Critic/Verifier per graph. Generalist explicitly **rejected** at Stage 02 | Closed at Stage 04 (ADR-008) |
| N2 | **Proposed** — named approvers (EU QP, Global Head of PV, Supply Chain VP + Quality) spend attention on low-risk routine cases rather than genuine exceptions | **Hypothesized** — real rates are Unknown (U7) | Medium — reviewer capacity | Pure waste if miscalibrated | Risk-tiering for **Batch Review only**, at Stage 16, calibrated against measured escalation rates. PV and Supply stay at 100% routing regardless — that is regulatory, not a tuning parameter | Stage 16 |

## T — Transportation

| # | Where | Obs/Hyp | Impact | Class | Action | Owner |
|---|---|---|---|---|---|---|
| T1 | **Proposed** — context is re-serialized at each container/component crossing on the common path | **Designed and counted: 7 crossings** one-way for Batch Review; never measured in a running system | Medium | Partly VA (each hop exists for a control), pure waste above necessity | 7 is the baseline; exceeding it in implementation without a documented reason is a Stage 12 assurance finding (T-9). Proof = interim assumption 7 | Stages 12, 17 |
| T2 | **Proposed** — ADR-005's separate Policy Engine knowingly adds one hop | **Hypothesized** magnitude (U6) | Low-medium latency | Business-required NVA — bought a Defects reduction (D3) | Accepted with a revisit trigger if it becomes a material share of the latency budget (T-4) | Stage 15 |
| T3 | **Proposed** — agent-to-agent chains across workflows would multiply movement | **Hypothesized** | Medium | Pure waste | Structurally prevented: zero cross-graph invocations (ADR-008), red-teamed at Stage 18 | Stage 18 |

## I — Inventory

| # | Where | Obs/Hyp | Impact | Class | Action | Owner |
|---|---|---|---|---|---|---|
| I1 | **Proposed** — cached responses are stored answers awaiting reuse; stale ones are toxic inventory (see D5 for the correctness face of the same risk) | **Hypothesized** | High | Pure waste if stale serving occurs | Cache deliberately **not built** until the uncached path is proven correct; then cache-correctness evals at Stage 14 | Stages 14, 15 |
| I2 | **Proposed** — unreviewed agent outputs queueing at the HITL gate | **Hypothesized** — depends on U7 | Medium | Pure waste above the necessary queue | Measure escalation rate before tuning; do not pre-optimize a queue that may not exist | Stage 16 |
| I3 | **Current** — zero evidence records exist; all 9 `evidence/` subfolders are empty | **Observed** | Not waste today — correct, since nothing has run | — | Becomes a Stage 19 concern only after real runs | Stage 19 |

## M — Motion

| # | Where | Obs/Hyp | Impact | Class | Action | Owner |
|---|---|---|---|---|---|---|
| M1 | **Current** — every prompt restates the evidence-citation discipline ("cite facts, label assumptions") | **Observed** | Low | **Business-required NVA** — deliberate friction that preserves evidence discipline | None | — |
| M2 | **Proposed** — an operator switching between the app, traces, the audit store, and the approval channel to reconstruct what an agent did | **Hypothesized** | Medium — debuggability and approver experience | Pure waste if realized | Trace-to-audit correlation IDs so one run is followable end-to-end without manual reconstruction | Stage 17 |

## E — Extra processing

| # | Where | Obs/Hyp | Impact | Class | Action | Owner |
|---|---|---|---|---|---|---|
| E1 | **Proposed** — agents built against ad-hoc raw-document RAG, then reworked when the semantic layer lands at Stage 13 | **Hypothesized** | Medium | Pure waste if realized | **Resolved this stage** (`lens_rollup.md` C1): Stage 10 designs against an ontology **contract**; Stage 13 fills it in. Recorded as BC-4 | Stages 10, 13 |
| E2 | **Proposed** — every ADR-007 fallback path needs its own test coverage | **Hypothesized** | Medium test burden | **Accepted extra processing** — untested fallbacks are worse than no fallbacks | Build the coverage; do not trim it | Stage 14 |
| E3 | **Proposed** — duplicate validation: the Critic/Verifier re-checking what the deterministic gates already enforce | **Hypothesized** | Low-medium token and latency cost | Pure waste if it occurs | Critic scope must be defined as *complementary* to the deterministic gates, not overlapping — a Stage 10 design constraint (BC-6) | Stage 10 |
| E4 | **Proposed** — two audit sinks (ADR-006) mean records are written twice | **Hypothesized** | Low | **Accepted duplication** — the alternative couples a regulatory obligation to a vendor SLA | Verify the two sinks have not silently collapsed into one (100% audit-write success while LangSmith is healthy) | Stage 17 |

---

## Change log against the prior registers

- **No categories added or removed.** All eight DOWNTIME categories carry forward.
- **Rows split for ownership:** the prior single Defects row is now D1–D5, each with its own
  proof; Overproduction is now O1–O5; Extra processing E1–E4.
- **New rows this stage:** O4 (method-doc drift), O5 (scope-creep pressure, closed), W4
  (programme-level planned wait), I3 (empty evidence store — correctly not waste), M2
  (operator context reconstruction), E3 (Critic overlap), E4 (dual-sink duplication).
- **Reclassified:** E1 moves from "open sequencing risk" to "resolved by BC-4."
- **Honesty note added:** O1 records that Stage 01's stated precondition for locking topology
  was not met.
