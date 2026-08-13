# DMAIC Lens — Stage 17 (Observability, design pass)

**Thin lens**, per `prompts/21_observability.md`: "Which Observability-waste entries (Prompt
01/04/06 registers) does this design close out?"

## Define

`waste_register_ai_specific.md` §8 named Observability waste with three faces: (a) traces too
noisy or too thin to reconstruct a run, (b) PII captured into traces — a governance breach, not
mere waste, (c) compliance-critical audit records living only on a vendor-owned surface. This
stage's question is narrow: does the design in `tracing_design.md`/`trace_redaction_and_
retention.md`/`dashboards.md`/`alerting.md` actually close these, or just restate the problem?

## Measure

| Waste-register face | Closed by | How |
|---|---|---|
| (a) Too noisy / too thin | `tracing_design.md` §2 | One span per node execution, bound to `langgraph_design.md`'s existing 11 nodes and `hooks.md`'s 10 hook bindings — no new nodes invented, no node left untraced. A retried node produces a new span, so the full loop history is reconstructable |
| (b) PII captured into traces | `trace_redaction_and_retention.md` §2–3 | One mechanical redaction path applied before write, both sinks. Approver identity, guard-blocked draft text, PV case narrative, `SensitiveSegment` content all stripped by rule, never by model judgment |
| (c) Audit records on a vendor-owned surface | `tracing_design.md` §6, `rbac_model.md` §4 | Audit store is its own container (ADR-006) with its own managed identity and WORM policy (ADR-009) — `finalize` writes it independent of LangSmith health |

**New this stage, not in the original register:** the RBAC gap surfaced when starting this
stage (zero RBAC mentions anywhere prior) and the severity-taxonomy gap (severity asserted ad
hoc across `failure_and_loop_guards.md`, no shared scale) were folded in at the user's request.
Both are now closed by `rbac_model.md` and `alerting.md` §1 respectively — neither was a named
waste-register entry, but both were real gaps this stage was the right place to close, since
tracing needs actor identity (RBAC) and alerting needs a shared severity vocabulary regardless.

## Analyze

The one thing worth stating plainly: **this design closes all three named waste faces without
adding a single new control.** Every span, every redaction rule, every alert threshold traces
to a node, hook, or metric that already existed in Stage 10/12's design. That is the expected
shape for an observability stage — it should make existing behavior explainable, not invent
new behavior to explain.

## Improve

No prior artifact changed. `rbac_model.md` and the severity taxonomy in `alerting.md` §1 are
net-new designs (not improvements to something that existed), added because they were
identified as gaps, not because Stage 10–16 got something wrong.

## Control

- **Standard**: every future node or hook added to the graph must get a `tracing_design.md` §2
  row and (if alert-worthy) an `alerting.md` §3 row in the same stage it's added — not
  deferred, per the "redaction rules before the first trace" precedent (BC-8) generalized to
  the whole trace schema.
- **Proof obligation carried forward**: `waste_register_ai_specific.md`'s own proof criterion
  — "audit-write success = 100% while LangSmith is healthy" — remains unmeasured until 20a.
  This design specifies how it will be measured (`dashboards.md`), not the measurement itself.
- **T-6 dependency, restated**: `alerting.md`'s one real threshold (cost/run vs. Stage 15
  budget) is Route-A-derived; per `waste_register_ai_specific.md`'s platform-dependency note,
  it must be re-measured, not assumed, if the LLM route resolves to Route B.
