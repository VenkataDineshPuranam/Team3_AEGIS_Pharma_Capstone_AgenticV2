# Latency Budget — Stage 15

**Executes:** `prompts/19_performance_tuning.md` §3
**Builds on:** `../../../docs/architecture/agentic/langgraph_design.md`, `../../../docs/architecture/c4/dmaic_lens.md`
(7-hop baseline), `failure_and_loop_guards.md` G6/G7
**Artifact status:** `stable` (structure); **targets are ceilings, not measured p50/p95** — U2
(latency per workflow) is Unknown, same status since Stage 01

---

## 0. What can be stated honestly before 20a

Same discipline as `token_economics.md` §0: the **critical path** and **structural timeout
ceilings** are real, derived facts. **p50/p95 targets are not** — they require U2, measured
only once 20a runs. This document is the latency equivalent of the token-economics model: a
real structure, waiting on a real number.

## 1. Per-node breakdown — critical path for `batch_review`

Every node from `langgraph_design.md`, classified by whether it sits on the synchronous
critical path (per `c4/dmaic_lens.md`'s "sync-call depth: 3" finding) or can run off it:

| # | Node | Kind | On critical path? | Ceiling | Basis |
|---|---|---|---|---|---|
| 1 | `intake` | deterministic | Yes | ≤ 50 ms | In-process validation, no external call |
| 2 | `policy_load` | deterministic | Yes | ≤ 200 ms | One network hop to Governance/Policy Engine (ADR-005) |
| 3 | `retrieve` | tool | Yes | ≤ 2,000 ms | Per-call, from `evidence_retrieve.schema.json` — bounded by the retrieval store, not measured yet |
| 4 | `evidence_gate` | deterministic | Yes | ≤ 50 ms | In-process check over already-retrieved items |
| 5 | `reconcile` | tool | Yes | ≤ 2,000 ms | Same class as retrieve — structured tool call |
| 6 | `synthesize` | **LLM** | Yes | ≤ 60,000 ms (G7, per-call timeout) | `failure_and_loop_guards.md` §2 — the one number already fixed, because it's a structural cap, not a performance target |
| 7 | `prohibited_action_guard` (×2) | deterministic | Yes | ≤ 50 ms each | Pattern match over generated text, in-process |
| 8 | `critic_verify` | **LLM** | Yes | ≤ 60,000 ms (G7) | Same as `synthesize` |
| 9 | `hitl_route` | deterministic | Yes | ≤ 100 ms | Role resolution, in-process + Entra lookup |
| 10 | `hitl_interrupt` | durable interrupt | **No** | Not applicable | Measured in hours/days (`failure_and_loop_guards.md` §5 escalation ladder), not a latency figure — see §3 |
| 11 | `finalize` | deterministic | Yes | ≤ 300 ms | Audit write, must complete before response returns (ADR-006) |

**Sum of critical-path ceilings, excluding HITL wait:** ≈ 124.65 seconds worst case (dominated
entirely by the two 60-second LLM timeouts). This is the **G6 wall-clock ceiling** from
`failure_and_loop_guards.md` — restated here as 300 seconds excluding HITL, which already
accounts for retries up to the G1/G2 caps, not just one pass.

## 2. Why the critical path is only 3 hops deep, restated with a source

`c4/dmaic_lens.md`'s own measurement: *"Sync-call depth: 3 (Web App → Orchestrator →
MCP Tool Server is the deepest synchronous chain in the common path)."* The `batch_review`
graph's actual node count (11) is higher than that hop count because most nodes execute
**within** the Orchestrator process — the 7-hop, 3-sync-depth figures describe
container/component boundary crossings, not in-process function calls. This document doesn't
recompute that number; it confirms the graph design (Stage 10) didn't add a crossing beyond
what Stage 03 measured, which is exactly what `dmaic_lens.md` (Stage 10) flagged as worth
checking and found unchanged.

## 3. HITL wait is explicitly out of scope for a latency target

The escalation ladder (`failure_and_loop_guards.md` §5) already sets its own timing — T0→T1 at
8 business hours, T3 expiry at 24 business hours (Batch) — and that is a **governance**
timescale, not a performance one. Folding it into a "latency" budget would be a category
error: nothing in Stage 15's mandate is about making human approval faster, and doing so would
contradict the "silence must never be treated as approval" design principle. **Stated once,
explicitly, so no future stage mistakes HITL wait for a performance defect to fix.**

## 4. What counts as the critical path for `pv_intake` / `supply_planning`

Both graphs are `provisional` (RR-2). Their node shape mirrors `batch_review`'s spine
(`agent_roster.md` §6), so the **same per-node ceiling classes apply provisionally** — but two
concrete differences are already known and must not be silently assumed away at 20b:

- **PV's 100% HITL routing** means every run reaches `hitl_interrupt` — this doesn't change the
  *pre-approval* latency budget, but it means the HITL-wait exclusion in §3 applies to
  literally every PV run, not the subset that self-resolves in Batch Review.
- **Supply's dual approval** (`failure_and_loop_guards.md` §5.4) means the wait until *both*
  legs approve can be longer than a single-approver wait — still excluded from the performance
  budget per §3, but worth flagging as a materially different HITL-wait shape, not a smaller
  version of Batch's.

## 5. Target p50/p95 — explicitly deferred

Per BC-14 (`build_constraints_from_lean.md`) and the same reasoning as `token_economics.md` §5:
no p50/p95 target is set here. What this document commits to instead: the target, once set,
will be expressed relative to the ceilings in §1 (e.g. "p95 end-to-end excluding HITL should sit
well under the ~125s worst-case ceiling — if it approaches it, either the ceiling is
miscalibrated or retries are firing far more than the happy-path design assumes").

## 6. What changes at the measured pass

| Item | Design-pass value (this document) | Measured-pass replacement |
|---|---|---|
| Per-node latency | Ceiling (upper bound) | Real p50/p95 per node, from 20a traces |
| Critical-path total | Worst-case sum (~125s) | Real end-to-end distribution |
| Hop count vs. the 7-crossing baseline | Designed, unmeasured (interim assumption 7) | Measured — feeds trigger T-9 if it deviates |
| Bottleneck node | Unknown | Identified from real span data (`span.model_request_start/end` if the runtime uses Claude Agent SDK conventions, or equivalent OTel spans per Stage 17) |
