# DMAIC Lens — Stage 14 (Eval-AI-Cache)

**Full cycle** — the prompt states this stage "sets Measure/Control for the whole agentic
system," alongside Discovery/01, Frame/01(SCQA), DDD/02, C4/03, ADR/04 as the programme's
designated full-DMAIC stages. Builds on `docs/quality/dmaic-lean/` (Stage 09's consolidation),
not a restart.

---

## Define

**Which quality/cost risk does each eval category and the cache design address?**

| Eval category | Risk it addresses | Traces to |
|---|---|---|
| Business outcome | A technically-correct response that isn't useful to the human reviewer | SCQA Answer, but genuinely un-automatable — honestly marked `NOT_APPLICABLE` rather than faked |
| Evidence fidelity/provenance | Fabricated or uncited facts | Register row D-Defects |
| GxP/safety boundary | The programme's highest-severity risk — a prohibited terminal action reaching a caller | ADR-004, register row D1 |
| Data integrity/audit trail | An unauditable run, or a stored prohibited draft | ADR-006, `memory_design.md` §4 |
| Retrieval authority/poisoning/injection | Citing non-citable evidence; following an embedded instruction | ADR-003, register row D2 |
| Structured output/abstention | A response that doesn't validate against its own contract, or guesses instead of abstaining | Stage 11 contracts, ADR-007 |
| PV duplicate/clock/terminology | A signal triaged before duplicate-check; a reporting clock reconstructed from a convenient receipt instead of the earliest one | DDD §7, `PV_REPORTING_CLOCKS.md` (K-024) |
| Agent/tool authorization/idempotency | Cross-context tool access; stale authorization trusted from intake; a replay causing duplicate execution | ADR-008, `tool_inventory.md` §1, BC-2/BC-3 |
| Privacy/cross-border | Raw PII persisted; a sensitive segment returned without the matching access group; jurisdiction-local evidence treated as globally citable | `kg_schema.md` §1/§4 (Stage 13's own finding), `conflict_authority_rules.md` §2 |
| Subgroup/accessibility | A disclosed performance or accessibility gap silently dropped rather than surfaced | Register, ported from V1 pattern |
| Latency/cost/denial-of-wallet | Runaway token spend; a run exceeding a structural cap without the cap actually holding | Register row AI-Token, `failure_and_loop_guards.md` |
| Model substitution/regression | An LLM route change (ADR-009) invalidating baselines silently | Trigger T-6 |
| Agent wrong handoff | A verdict routed to the wrong graph node — this session's real `PROHIBITION_ADJACENT` bug | `langgraph_design.md` correction record |
| Agent loop-guard trip | A structural cap (G1-G8) failing to hold, or a cycle that doesn't terminate | `failure_and_loop_guards.md` §2/§4 |
| Agent unauthorized tool call | A tool method that shouldn't exist being called, or the Critic gaining tool access it was designed never to have | `agent_roster.md` §2, ADR-004 layer 2 |

**Cache design risk it addresses:** the register's D5/I1 rows — a cache serving an answer built
on since-superseded evidence — plus a second-order finding this stage made (`cache_design.md`
§4): a wall-clock TTL cannot distinguish "still correct" from "coincidentally not yet expired,"
so every cacheable tool is invalidated by version/event, never by time alone.

## Measure

**Baseline pass rate, cache hit rate, cost/latency per workflow, before any tuning** — the
prompt's own Measure instruction, answered as honestly as the programme's Measure-first mode
requires:

| Metric | Value | Class |
|---|---|---|
| Eval scenarios written | 63, across 15 categories | Fact (this stage) |
| Scenarios passing against synthetic fixtures | 59 PASS, 2 `NOT_APPLICABLE`, 1 `THRESHOLD_NOT_DEFINED`, 1 `BLOCKED_BY_ENVIRONMENT`, **0 FAIL** | Fact — real code run, this session (`scorecard.md`) |
| Harness defects found and fixed during self-test | 7 | Fact (`scorecard.md` §2) |
| Pass rate against a **real running system** | **Unknown — U3, unchanged since Stage 01** | No system exists to measure |
| Cache hit rate | **N/A — U4** | No cache exists (deliberately, `cache_design.md` §0) |
| Cost/latency per workflow | **Unknown — U1/U2**, unchanged since Stage 01 | First real number comes from 20a |
| Structural loop-guard ceilings exercised | 8 of 8 (G1-G8), all pass against synthetic values | Fact — grader logic verified, not yet measured against a real trajectory |

**The one number this stage was tempted to invent and didn't:** a cost-per-successful-task
threshold (LCD-04). `latency_cost_grader.py:grade_cost_threshold` returns
`THRESHOLD_NOT_DEFINED` rather than a guessed cap — consistent with BC-13's rule and this
programme's standing refusal to set numbers before measurement.

## Analyze

**Which failures are agent-design defects (Prompt 14) vs tool-contract defects (Prompt 15) vs
cache-correctness defects?** — the prompt's own triage question, answered against the actual
7 defects found this session (§2 of `scorecard.md`) plus the one real regression this stage's
dataset exists to catch:

| Defect | Category |
|---|---|
| `schema_grader` path-doubling, `_check`'s `note`-key handling, replay-counter logic, missing gate-flattening | **Harness defects** — none of these are agent-design, tool-contract, or cache-correctness defects. They're bugs in the eval code itself, caught by self-testing before the harness was trusted |
| The `PROHIBITION_ADJACENT` retry-routing bug (found and fixed at Stage 10, regression-tested here as `AWH-01`) | **Agent-design defect** — a graph edge condition that contradicted its own governing rule document |
| None found this session | **Tool-contract defects** — Stage 11's contracts held up against this stage's adversarial cases without needing a fix |
| None found this session (no cache exists to have a defect in) | **Cache-correctness defects** — `cache_correctness_evals.md`'s 8 checks all returned their correct outcome on first design, though the *design* itself (not yet an implementation) is what was checked |

**A pattern worth naming:** every defect found this session was in **the harness itself**,
except one **agent-design** defect found and fixed one stage earlier. Zero tool-contract or
cache-correctness defects — but that is a measurement of *design consistency checked against
itself*, not of correctness against a real system. The Measure section's honesty about U3/U4/
U1/U2 remaining Unknown is the check against overclaiming what "zero defects found" means here.

## Improve

**Fixes fed back to the owning stage, not patched as symptoms in the harness** — the prompt's
explicit instruction, followed both ways:

- The `PROHIBITION_ADJACENT` fix was made in `langgraph_design.md` (its owning stage, Stage 10)
  when it was found, not patched around in a grader. This stage's `AWH-01` scenario exists to
  make sure it never regresses, which is a different thing from fixing it here.
- The 7 harness defects were fixed **in the harness**, correctly, because the harness was the
  thing that was actually broken — patching the *fixtures* to match broken grader behaviour
  (the tempting shortcut for e.g. `ATA-01`) would have hidden a real replay-counting bug instead
  of fixing it.
- **Two genuine improvements to prior-stage artifacts, recorded as findings, not silently
  folded in:** `cache_design.md` §2 discovered that `evidence.retrieve`'s cache key should
  **not** include `policy_contract_version` (only its idempotency key should) — because
  retrieved content doesn't depend on policy, only request admission does. This refines
  `tool_inventory.md` §6 rather than contradicting it.

## Control

**Release gates that block a build from Prompt 20 if any category fails** — `release_gates.py`
is executable and verified against all 63 scenarios (`release_gates.md` §5: zero hard-gate
blocks, and the reason why that's expected at this stage, not a false-clean signal).

**Revisit triggers, consolidated:**

| # | Trigger | Consequence |
|---|---|---|
| C-1 | 20a produces its first real trace | This entire harness re-runs against real output — the **measured pass** the execution plan names. A category passing against fixtures and failing against real output is the single most informative signal Stage 14 can produce |
| C-2 | U1 (token cost) is measured | `THRESHOLD_NOT_DEFINED` on LCD-04 is replaced with a real number; ceilings (C1-C4) get compared against it for the first time |
| C-3 | ADR-009's LLM route is confirmed | MSR-01 moves from `BLOCKED_BY_ENVIRONMENT` to actually gradable; if the route is B (Azure OpenAI), every fixture-passing category must be re-verified against the new model's behaviour, not assumed to transfer |
| C-4 | Stage 15 builds the real cache | `cache_correctness_evals.md`'s 8 checks must be re-run against the real implementation, not just the grader logic; any new check needed (e.g. `conflict_authority_rules.md` §5's conflict-staleness gap, noted as open in that document §3) gets added before cache ships, not after |
| C-5 | PV or Supply graphs are built at 20b | Categories 7 and parts of 8/9 (currently testing *designed* invariants only) must pass against the real graphs — per RR-2, no assumption that Batch Review's harness behaviour transfers |
| C-6 | Any future harness change | Self-test first (`05_Build_Harness_and_Self_Test.md`'s pattern, consumed this stage) — this session's 7 defects are the concrete argument for why |

**Ownership.** This harness and its gates are owned by whoever runs Stage 20 build sign-off —
named formally at Stage 16 (governance/control ownership), not invented here.
