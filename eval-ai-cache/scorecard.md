# Scorecard — Stage 14

**Executes:** `prompts/18_eval_ai_cache.md` §Measure, exit criterion "Eval harness runs and
produces a pass/fail scorecard per category"
**Run command:** `python3 eval-ai-cache/graders/run_eval_dataset.py` (also runnable as
`python3 -m pytest tests/unit/graders/test_graders.py -q`)
**Run date:** this session (design-stage run, against synthetic fixtures — see §0)
**Artifact status:** `stable`

---

## 0. What "runs" honestly means at this stage

No live agentic system exists — `apps/` and `services/` have no code (Stage 20 is deliberately
last). This scorecard is **real** in the sense that every grader executed and every result
below is what the code actually returned this session (not hand-written) — but it graded
**synthetic fixture inputs shaped like our own contracts**, not a running system's output. That
is the honest scope of a design-stage eval harness: it proves the grading logic is correct and
ready, not that a deployed system passes it. The **measured pass** (real numbers, real traces)
happens after 20a, per the execution plan's Wave 3.

## 1. Full run output

```
CATEGORY                                 SCENARIOS  PASS   OTHER
business_outcome                         2          0      [('BO-01', 'NOT_APPLICABLE'), ('BO-02', 'NOT_APPLICABLE')]
evidence_fidelity_provenance             3          3
gxp_safety_boundary                      5          5
data_integrity_audit_trail               4          4
retrieval_authority_poisoning_injection  6          6
structured_output_abstention             4          4
pv_duplicate_clock_terminology           6          6
agent_tool_authorization_idempotency     6          6
privacy_cross_border                     5          5
subgroup_accessibility                   2          2
latency_cost_denial_of_wallet            4          3      [('LCD-04', 'THRESHOLD_NOT_DEFINED')]
model_substitution_regression            2          1      [('MSR-01', 'BLOCKED_BY_ENVIRONMENT')]
agent_wrong_handoff                      4          4
agent_loop_guard_trip                    5          5
agent_unauthorized_tool_call             5          5

TOTAL: 63 scenarios, 59 PASS, breakdown of non-PASS: {'NOT_APPLICABLE': 2, 'THRESHOLD_NOT_DEFINED': 1, 'BLOCKED_BY_ENVIRONMENT': 1}
```

**Exit code: 0.** Zero `FAIL`, zero `ERROR`. pytest confirms independently: `60 passed, 4
skipped` (the 4 skips are the same 2 `NOT_APPLICABLE` + 1 `THRESHOLD_NOT_DEFINED` + 1
`BLOCKED_BY_ENVIRONMENT` rows, each skip carrying its reason string, not a silent skip).

## 2. This did not pass on the first run — recorded honestly

The first execution of this harness found **7 real defects** in the grader/fixture code before
any of the above was true. Fixing them was itself the Analyze/Improve work this stage's DMAIC
lens describes. Listed here rather than only in `dmaic_lens.md`, because a scorecard that only
shows the final green run overstates how first-try-correct this was:

| # | Defect found | Root cause | Fix |
|---|---|---|---|
| 1-3 | `SOA-01/02/04` — `FileNotFoundError` loading schema files | `schema_grader.load_schema` concatenated `CONTRACTS_DIR` (already pointing at `tool_contracts/`) with a schema_ref that repeated the full path, doubling it | Use only the filename component |
| 4 | `PDC-03` — false failure on a documentary `note` field | `_check` treated every key in `expected`, including human-readable commentary, as a required match | Skip `note` keys in comparison |
| 5 | `ATA-01` — `execution_count_after_second_call` was 2, expected 1 | `_invoke`'s plain-replay branch incremented the execution counter, contradicting the whole point of replay detection (no duplicate execution) | Replay branch now returns the cached count unchanged, matching V1's verified `tool_gateway.py` behaviour exactly |
| 6 | `ATA-02` — adversarial case couldn't actually fail, because the grader had no way to simulate the buggy behaviour it was meant to catch | Fixture asserted an adversarial outcome the grader's correct logic would never produce | Added an `actual_replay_detected` override parameter (same pattern as other graders' `actual_decision` overrides) so the adversarial branch is genuinely exercised; added `ATA-06` as the golden-path companion so both branches are covered |
| 7 | `SGA-02` — expected `gate_blocked`/`gate_id` keys that the grader never set | Gate evaluation result was stored under an internal `_gate` key instead of being flattened into the result | Flattened `gate_blocked` and `gate_id` onto the grader's return value |

**Why this table matters more than the clean final run.** Per the prompt's own Analyze
question ("which failures are agent-design defects vs tool-contract defects vs cache-
correctness defects"), none of these 7 were any of those — they were **harness defects**,
caught by the harness testing itself before it was pointed at anything else. That is exactly
what `05_Build_Harness_and_Self_Test.md` (consumed from `eval-ai-cache/`, not re-derived) calls
for: self-test the harness before trusting its verdicts on real output.

## 3. Coverage against the 12 required categories + 3 agent-specific

| # | Category | Grading mode | Scenarios | Status |
|---|---|---|---|---|
| 1 | Business outcome | Human rubric (matches V1 — no automated grader exists there either) | 2 | `NOT_APPLICABLE` to automation, by design |
| 2 | Evidence fidelity/provenance | Deterministic | 3 | All pass |
| 3 | GxP/safety boundary | Deterministic | 5 | All pass |
| 4 | Data integrity/audit trail | Deterministic | 4 | All pass |
| 5 | Retrieval authority/poisoning/injection | Deterministic | 6 | All pass |
| 6 | Structured output/abstention | Deterministic | 4 | All pass |
| 7 | PV duplicate/clock/terminology | Deterministic (designed, PV provisional) | 6 | All pass |
| 8 | Agent/tool authorization/idempotency | Deterministic | 6 | All pass |
| 9 | Privacy/cross-border | Deterministic | 5 | All pass |
| 10 | Subgroup/accessibility | Deterministic (surfacing-only, ported from V1) | 2 | All pass |
| 11 | Latency/cost/denial-of-wallet | Deterministic ceilings; real cost threshold `THRESHOLD_NOT_DEFINED` | 4 | 3 pass, 1 honestly unscored |
| 12 | Model substitution/regression | `BLOCKED_BY_ENVIRONMENT` pending ADR-009 | 2 | 1 pass (degraded-mode continuity), 1 honestly blocked |
| 13 | Agent wrong handoff | Deterministic | 4 | All pass — includes the `PROHIBITION_ADJACENT` regression |
| 14 | Agent loop-guard trip | Deterministic | 5 | All pass |
| 15 | Agent unauthorized tool call | Deterministic | 5 | All pass |

**12 of 12 required categories present, 0 silently dropped.** Only category 1 has no automated
grader — matching V1's own eval design, not a gap this programme introduced.

## 4. What this scorecard does not claim

- Does not claim any release gate has ever fired against real system output.
- Does not claim a token/cost number (LCD-04 stays `THRESHOLD_NOT_DEFINED` until Stage 15).
- Does not claim PV/Supply categories (7, and parts of 8/9) are validated against a real
  `pv_intake`/`supply_planning` graph — those graphs are `provisional` (RR-2); these scenarios
  test the *design*, and must be re-run against real output at 20b.
- Does not claim category 1 (business outcome) has any automated signal at all.

## 5. Next measured pass

Per the execution plan (`plans/active/EXECUTION_PLAN.md` Wave 2/3): this harness runs again,
unchanged in grading logic, against real 20a trace output once the interim slice exists. The
categories currently `PASS` against fixtures become the first real signal on whether the
*design* this scorecard validated actually holds when a model is in the loop.
