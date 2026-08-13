# DMAIC Lens — Stage 15 (Performance Tuning)

**Thin lens** (per `prompts/19_performance_tuning.md` — "this stage is itself the
Improve/Control step for cost"). Governed by `docs/quality/dmaic-lean/` — the consolidated
registers, not a restart.

## Define

Which token/retrieval waste category does each tuning change target — the prompt's own first
Lean question, answered per document produced this stage:

| Document | Waste category targeted | How |
|---|---|---|
| `token_economics.md` | AI-Token (highest-magnitude, no number since Stage 01) | Builds the cost *model* (formula + verified pricing) so the first real measurement at 20a converts directly into a dollar figure, without a second design pass needed |
| `redis_tuning.md` | D5/I1 — Inventory (stale cache) | Extends Stage 14's cache-correctness design with a placement rule (cache only guard-and-Critic-cleared output) the prior stage's design left implicit |
| `latency_budget.md` | Transportation (T1, `waste_register_downtime.md`) | Converts the Stage 03 hop-count baseline into per-node ceilings, so a future latency regression has a specific node to blame, not just a total |
| `denial_of_wallet_guardrail.md` | AI-Token, denial-of-wallet specifically | The one document this stage that is Control, not just Define — an enforced circuit breaker, not a target |

## Measure

| Metric | Value | Class |
|---|---|---|
| Token/cost model built | Yes — formula + verified pricing | Fact (this stage) |
| Actual tokens/cost per run (U1) | **Still Unknown** | Unchanged since Stage 01 — this stage could not close it, by design |
| Latency ceilings set | Yes, per node | Fact — derived from existing structural caps (G6/G7) and the C4 hop-count baseline |
| Actual latency per workflow (U2) | **Still Unknown** | Unchanged since Stage 01 |
| Denial-of-wallet ceiling | **$45.00/user/workflow/day**, derived and computed | Fact — arithmetic on already-ratified numbers (C1, C4, verified pricing), not a guess |
| Guardrail tests passing | 7/7 | Fact — executed this session |
| Cache hit-rate target (U4) | **Still N/A** | No cache exists; unchanged |

**The one metric this stage actually moved: 0 → 1 enforced, tested denial-of-wallet control.**
Every other Stage 15 deliverable is a model or a structure waiting on 20a, honestly stated as
such rather than padded with invented numbers.

## Analyze

Why could the denial-of-wallet guardrail be finished this stage while the cost/latency targets
could not? Because it doesn't need a *typical* number — it needs a *worst-case* one, and every
input to a worst-case bound was already ratified (C1, C4, Stage 10; pricing, verified this
session). A target needs measured central tendency; a ceiling needs only a defensible upper
bound. This is the same distinction `failure_and_loop_guards.md` §1 drew for the per-run
guards (structural caps set now, budgets set later) — this stage found it applies at the
denial-of-wallet scope too, not just the per-run one.

**Root cause of why U1/U2 are still Unknown after 15 stages of design work:** by design. The
whole programme has been Measure-first since Stage 09, and the interim slice (20a) is the
first point any of these numbers can exist. Stage 15 arriving before 20a and still not having
real numbers is not a Stage 15 defect — it is the execution plan (`plans/active/EXECUTION_PLAN.md`
Wave 4) working exactly as designed: Stage 15's *measured pass* comes after 20a/20b, not now.

## Improve

The four documents plus the guardrail implementation are the Improve artifact. What's real
enough to ship now: the cost model, the latency structure, and — the one item that's actually
enforced, not just designed — the denial-of-wallet ceiling.

**A genuine improvement to a prior stage's design, not just this stage's own output:**
`redis_tuning.md` §2 found that Stage 14's cache design never specified *where* in the pipeline
caching should sit relative to the Prohibited-Action Guard and the Critic. Extending it (never
cache a draft, only a guard-and-Critic-cleared response) closes a gap before any future stage
tries to design synthesis-output caching against an ambiguous prior spec.

## Control

Which dashboard/alert catches a regression in cost or latency after this tuning — the prompt's
own second Lean question:

| Signal | Threshold | Owner (Stage 17) |
|---|---|---|
| `denial_of_wallet.admission_denied` rate | Any sustained rate above near-zero | Alert — either genuine abuse or the ceiling is miscalibrated |
| `cache.error` / `cache.bypass` (once Stage 15's measured pass builds the cache) | Sustained non-zero | Alert, per `redis_tuning.md` §5 — a silent full-price fallback is exactly the failure mode this stage's own prompt named |
| Tokens/run vs. C1 (150,000) | Any occurrence | Alert — a structural cap failing to hold is a graph defect (`failure_and_loop_guards.md` §6), same class as before |
| Per-node latency vs. `latency_budget.md` §1 ceilings | Sustained breach on any node | Identifies the bottleneck node directly, not just a total-latency alert |

**Revisit triggers, consolidated:**

- **T-3 comes due here.** If 20a's measured token cost (U1) lands far above what C1's
  worst-case bound implied was "insane," that's the ADR-008 topology revisit trigger from
  Stage 09 — this stage's cost model is what makes that comparison possible the moment real
  data exists.
- If measured daily spend per user is a large fraction of the $45 ceiling (not a small one),
  raise the ceiling using measured data — never loosen the worst-case derivation logic itself
  (`denial_of_wallet_guardrail.md` §7).
- If ADR-009's LLM route resolves to Route B (Azure OpenAI), the entire pricing table in
  `token_economics.md` §2 is void and must be replaced before any of these documents' numbers
  can be trusted — trigger T-6, unchanged.
