# Prompt 18 — Eval-AI-Cache (Eval Harness + Response Cache)

**Maps to:** STAGES.md Stage 14 (`stage-14-eval-ai-cache`)
**Lifecycle stage:** Design + Build (quality infrastructure)
**Framework derived:** V3 addition, drawing directly on the `eval-ai-cache/AI_FDE_Brownfield_Evals_Cursor_Runbook/` reference library (24-stage brownfield evals methodology) already seeded in this repo.
**Core question:** How do we know an agent response is good enough to ship, and when is it safe to reuse a cached one?
**Prerequisites:** Prompt 08 technical design (contracts), Prompt 14 (agent design), Prompt 15 (tool contracts).

---

## Produce

1. **Eval dataset** — scenario suites covering the 12 required categories carried from V2's `evaluation/EVALUATION_PLAN.md` (business outcome, evidence fidelity/provenance, GxP/safety boundary, data integrity, retrieval authority/poisoning/injection, structured-output/abstention, PV duplicate/clock/terminology, agent/tool authorization/idempotency, privacy/cross-border, subgroup/accessibility, latency/cost, model substitution/regression) — extended with agent-specific cases (wrong handoff, loop-guard trip, unauthorized tool call).
2. **Eval harness** — deterministic graders per category (reuse V2's `submission/evaluation/graders/` pattern as a starting point), release gates, and a LangSmith-backed regression suite.
3. **Cache design** — exact-match and semantic-cache strategy: cache key derivation, embedding model for semantic match, similarity threshold, TTL per workflow risk tier, and an explicit **do-not-cache list** (anything touching a prohibited-decision path, anything with stale-authorization risk).
4. **Cache correctness evals** — tests proving a cache hit never serves a stale-authority or superseded-evidence answer (this is the failure mode unique to caching in a regulated domain).

### Lean / DMAIC lens (full — this stage sets Measure/Control for the whole agentic system)

1. **Define** — which quality/cost risk does each eval category and the cache design address?
2. **Measure** — baseline pass rate, cache hit rate, cost/latency per workflow, before any tuning.
3. **Analyze** — which failures are agent-design defects (Prompt 14) vs tool-contract defects (Prompt 15) vs cache-correctness defects?
4. **Improve** — fixes fed back to the owning stage (do not patch symptoms in the harness).
5. **Control** — release gates that block a build from Prompt 20 if any category fails.

---

## Exit criteria (handoff to Prompt 19)

- [ ] Eval harness runs and produces a pass/fail scorecard per category.
- [ ] Cache do-not-cache list is enforced in code, not just documented.
- [ ] Cache correctness evals exist and pass.
- [ ] Release gates are wired to block Stage 20 build sign-off on failure.

---

## Output

Write under `eval-ai-cache/`, `quality/gates/`, `tests/` **and mirror** to `workshop/participant-output/18-eval-ai-cache/`:

- `eval_dataset/*.json`
- `graders/*`
- `release_gates.md`
- `cache_design.md`
- `cache_correctness_evals.md`
- `scorecard.md`
- `dmaic_lens.md` (full)
