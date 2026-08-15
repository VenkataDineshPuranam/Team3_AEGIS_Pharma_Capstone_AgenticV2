# Denial-of-Wallet Guardrail — Stage 15

**Executes:** `prompts/19_performance_tuning.md` §4
**Implementation:** [`infra/policies/denial_of_wallet_guardrail.py`](../../../infra/policies/denial_of_wallet_guardrail.py)
**Tests:** [`tests/unit/policies/test_denial_of_wallet_guardrail.py`](../../../tests/unit/policies/test_denial_of_wallet_guardrail.py) — **7/7 passing, executed this session**
**Exit criterion:** "implemented as an enforced hook, not a documented policy only" — **true**,
verified by running the tests, not asserted

---

## 1. Why this guardrail could be built now, when token_economics.md and latency_budget.md couldn't be measured

Every other Stage 15 document hit the same wall: a **target** (cost, latency) requires U1/U2,
which don't exist before 20a. A **denial-of-wallet ceiling** is different in kind — it isn't a
tuned target at all, it's a circuit breaker sized from numbers that already exist:
`failure_and_loop_guards.md`'s C1 (150,000 tokens/run) and C4 (20 runs/requester/hour), plus
verified current pricing (`token_economics.md` §2). No measurement of *typical* usage is needed
to compute a *worst-case* bound — that's exactly the structural-ceiling-vs-measured-budget
distinction this programme has used since Stage 10.

## 2. The derivation, spelled out

```
DAILY_RUN_CEILING     = 20        (same number as C4, reinterpreted as a daily backstop —
                                    a requester tripping the hourly breaker repeatedly would
                                    already hit this before it could matter independently)
MAX_TOKENS_PER_RUN    = 150,000   (= C1, failure_and_loop_guards.md)
OUTPUT_PRICE          = $15/MTok  (Sonnet 5 output rate — the model token_economics.md §2
                                    recommends for 20a; output-only pricing is the more
                                    expensive, conservative side of Sonnet 5's $3/$15 split)

MAX_DAILY_SPEND_USD   = 20 × (150,000 / 1,000,000) × 15  =  $45.00
                        per (user, workflow) per day
```

**Every input is either an already-ratified structural cap or verified public pricing.** No new
number was invented for this document — it's arithmetic on numbers Stage 10 and this stage's
own §2 already established.

## 3. What "enforced" means here, concretely

`DenialOfWalletGuard.check_and_admit()` is called **before** a run is admitted (the intended
binding point: the `intake` node, `langgraph_design.md` §1 — the same node that already binds
current authorization). Two independent checks, either of which blocks admission:

1. **Run-count ceiling** — has this (user, workflow, day) already recorded ≥ 20 runs?
2. **Spend ceiling** — would admitting this run, priced at the **worst-case** token estimate
   (not a hopeful guess), push cumulative spend for the day over $45?

**Fail-safe direction matches ADR-005.** The admit check always prices a run at
`MAX_TOKENS_PER_RUN` unless the caller supplies a real pre-run estimate — it can reject a run
that would have cost less than the worst case, never admit one that costs more. Same
conservative bias as every other guard in this programme.

`DenialOfWalletGuard.record_run()` is called **after** a run completes, with its *real* token
usage — this is what makes the ceiling self-correcting rather than punitively worst-case for
every subsequent run: a cheap run leaves more real headroom for the next one.

## 4. Test coverage, run this session

| Test | Proves |
|---|---|
| `test_ceiling_values_match_documented_derivation` | The three constants match the derivation above exactly — a silent drift between code and doc would fail this |
| `test_admits_within_ceiling` | Golden path |
| `test_run_count_ceiling_trips_at_21st_run` | **The ceiling actually trips** — not just returns a number |
| `test_spend_ceiling_trips_before_run_count_on_expensive_runs` | The two checks are independent; expensive runs can trip spend before run-count |
| `test_ceilings_are_scoped_per_user_and_workflow_independently` | One user/workflow exhausting its ceiling doesn't block another — a real cross-tenant isolation bug this test would have caught |
| `test_ceilings_reset_per_day` | No permanent lockout — the ceiling is a daily backstop, not a ban |
| `test_admit_check_is_worst_case_conservative_by_default` | The fail-safe direction (§3) actually holds in code, not just in the docstring |

**7/7 passing.** Run yourself: `python3 -m pytest tests/unit/policies/ -v`.

## 5. Binding into the hook system (Stage 12)

Added as a new row in `../../../.claude/hooks/hooks.md` §1 — a **pre-tool-call**-class hook, binding at
`intake`, alongside the existing authorization check. Cross-referenced there, not duplicated;
see that file for the full hook index this joins.

## 6. What this is not

- **Not a replacement for C1/C4.** Those remain the per-run structural caps. This is an
  aggregate, cross-run ceiling — the two operate at different scopes and both stay.
- **Not a measured budget.** $45/day is a worst-case bound computed from worst-case inputs.
  The real typical daily spend per user is almost certainly a small fraction of this, exactly
  as `token_economics.md` §3 notes for the per-run ceiling. Replaced by a measured figure at
  the Stage 15 measured pass, per BC-13/14 — the replacement condition is the same one
  `failure_and_loop_guards.md` §3 already states for C1/C2/C4.
- **Not yet wired to a shared store.** The in-process dict is sufficient for this stage's
  self-test, matching the precedent set by V1's own `tool_gateway.py` idempotency cache
  (verified pattern, consumed at Stage 14). A real deployment needs this backed by Redis or the
  audit store so the ceiling holds across restarts and horizontally-scaled instances — noted
  in the module docstring as a Stage 20 implementation requirement, not resolved here.

## 7. Revisit trigger

If Stage 15's measured pass shows typical daily spend per user is a large fraction of $45 (not
a small one), that's a signal the ceiling was sized too tightly against real usage patterns —
raise it, using measured data, rather than loosening the worst-case derivation logic itself.
