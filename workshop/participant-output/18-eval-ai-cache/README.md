# eval-ai-cache

Stage 14 — eval harness, eval dataset, and cache design. Also holds the pre-seeded
`AI_FDE_Brownfield_Evals_Cursor_Runbook/` (24-part methodology, consumed rather than
re-derived this stage — NAB-4/trigger T-7) and two unconsumed runbooks (OpenTelemetry, Redis
caching) reserved for Stages 15/17.

| Document | Answers |
|---|---|
| [eval_dataset/](eval_dataset/) | 63 scenarios across 15 categories (12 required + 3 agent-specific), grounded in real `knowledge/` IDs and Stage 10-13 designs |
| [graders/](graders/) | Executable Python graders — self-contained (no `apps/`/`services/` code exists yet), the same functions Stage 20 wires to real service calls |
| [graders/run_eval_dataset.py](graders/run_eval_dataset.py) | The harness entry point — `python3 eval-ai-cache/graders/run_eval_dataset.py` |
| [cache_design.md](cache_design.md) | Exact-match + semantic strategy, cache keys, do-not-cache list, TTL — **not built**; cache is excluded from the interim slice by design |
| [cache_correctness_evals.md](cache_correctness_evals.md) | 8 executed checks proving a cache hit can never serve stale-authority evidence, once a cache exists to wire them into |
| [scorecard.md](scorecard.md) | Real run output: 63 scenarios, 0 FAIL, 0 ERROR — plus the 7 harness defects found and fixed getting there |
| [dmaic_lens.md](dmaic_lens.md) | Full DMAIC — this stage sets Measure/Control for the whole agentic system |

Release-gate policy lives in [`quality/gates/`](../quality/gates/); test wrapper in
[`tests/unit/graders/`](../tests/unit/graders/).

**What "the harness runs" means here:** every grader executes against synthetic fixtures shaped
like our own contracts — real code, real results, but not a live agentic system (none exists;
Stage 20 is last). The measured pass against real trace output happens after 20a.
