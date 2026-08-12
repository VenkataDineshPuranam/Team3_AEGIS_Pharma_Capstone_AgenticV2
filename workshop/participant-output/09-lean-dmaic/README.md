# dmaic-lean

Stage 09 — the consolidated DMAIC/Lean workbook. This reconciles the nine prior per-stage
`dmaic_lens.md` files and five register pairs into **one** governing set that Stages 10–21
work from.

| Document | Answers |
|---|---|
| [lens_rollup.md](lens_rollup.md) | What did Stages 01–08 already find, where did they disagree, and what did they miss? |
| [dmaic_plan.md](dmaic_plan.md) | Define → Measure → Analyze → Improve → Control for the programme |
| [waste_register_downtime.md](waste_register_downtime.md) | The 8 DOWNTIME wastes, with owners and proofs |
| [waste_register_ai_specific.md](waste_register_ai_specific.md) | The 8 AI-FDE wastes, with owners and proofs |
| [build_constraints_from_lean.md](build_constraints_from_lean.md) | Must-fix-before-build vs. fix-in-pilot vs. accept-as-residual-risk |
| [structural_reopen.md](structural_reopen.md) | Does any Improve action reopen C4/ADRs/contracts? **Gate: `cleared`** |

**Mode: Measure-first.** No V3 system has run; every baseline that matters (token cost,
latency, eval pass rate, cache hit rate) is Unknown. Instrumentation therefore outranks
feature scale-out, and nothing in these documents claims a waste is *fixed* — each has an
owning decision and a scheduled proof, which is not the same thing.

The per-stage lenses under `docs/product/` and `docs/architecture/` remain as the historical
record. Where they and these documents differ, **these govern**.
