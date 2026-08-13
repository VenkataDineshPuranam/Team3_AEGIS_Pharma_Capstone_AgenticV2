# Token Economics — Stage 15

**Executes:** `prompts/19_performance_tuning.md` §1
**Builds on:** `docs/architecture/agentic/langgraph_design.md` (state schema, node inventory),
`docs/architecture/agentic/failure_and_loop_guards.md` (G1–G8, C1–C4), ADR-009 (Azure), Stage 14
`scorecard.md`
**Artifact status:** `stable` **as a model** — the formula, structure, and pricing inputs are
real and verified; **usage volume is not** — U1 (tokens/cost per run) is still Unknown, exactly
as flagged since Stage 01. This document does not close that gap; nothing can, short of running
20a.

---

## 0. What "measured numbers, not estimates" can honestly mean before 20a runs

The exit criterion asks for actual measured numbers. Two of the three inputs to a cost model
**are** measurable today without a running system; the third genuinely is not:

| Input | Measurable pre-20a? | Status here |
|---|---|---|
| **Pricing** ($/MTok per model) | Yes — public, verified against `claude-api` skill's live-cached table, not recalled from memory | **Real, current numbers** (§2) |
| **Structural token ceilings** (max calls, max tokens/run) | Yes — derived from the graph's own shape, same as `failure_and_loop_guards.md` C1/C2 | **Real, already set** (Stage 10) |
| **Actual tokens consumed per run** (turns to completion, tokens in/out per turn) | **No** — depends on real evidence volume, real model behavior, real retry rates | **Unknown — U1**, first measured at 20a |

This document builds the **model** (formula + verified pricing) that turns a future measured
token count into a dollar figure. It does not invent the token count.

## 1. The formula

```
cost_per_run = Σ over LLM nodes (synthesize, critic_verify) of:
    (tokens_in[node] / 1,000,000 × price_input[model])
  + (tokens_out[node] / 1,000,000 × price_output[model])

turns_to_completion = 1 (happy path) to 6 (G1 structural cap, failure_and_loop_guards.md)
```

Grounded in `langgraph_design.md`: exactly **2 LLM nodes** exist (`synthesize`,
`critic_verify`) — every other node is deterministic and contributes zero LLM token cost. This
is a real, verified structural fact, not an estimate: `dmaic_lens.md` (Stage 10) counted 2 of
11 nodes as LLM nodes and confirmed no other node calls a model.

## 2. Pricing — verified against the current Anthropic pricing table, not recalled

Per-million-token pricing, current as of this session (source: `claude-api` skill's cached
model table, itself sourced from `platform.claude.com/docs/en/pricing`):

| Model | Input $/MTok | Output $/MTok |
|---|---|---|
| Claude Opus 5 | $5.00 | $25.00 |
| Claude Sonnet 5 | $3.00 ($2.00 intro through 2026-08-31) | $15.00 ($10.00 intro) |
| Claude Haiku 4.5 | $1.00 | $5.00 |

**Route confirmed applicable to ADR-009 Route A.** Claude on Microsoft Foundry (Azure AI
Foundry, the ADR-009 recommended route) is billed through the Microsoft Marketplace **at
standard first-party API rates** — the table above applies unchanged if Route A is confirmed.
This closes one small piece of ADR-009's uncertainty: whichever model tier is chosen, the
*pricing* doesn't change between first-party Claude API and Azure AI Foundry. **What still
depends on the Route A/B decision:** if the sponsor picks Route B (Azure OpenAI), this entire
pricing table is void and must be replaced — this is exactly trigger T-6.

**Model not yet chosen for this system.** Nothing in Stages 01–14 selected which Claude model
tier (Opus/Sonnet/Haiku) the `synthesize` and `critic_verify` nodes should run on. This is a
genuine open decision, not an oversight — model tier is a cost/quality tradeoff that needs the
same Measure-first discipline as everything else. **Recommendation, not a decision:** run 20a's
first measurements on **Claude Sonnet 5** (per-token cost 3–5× lower than Opus, more than
sufficient capability for the two well-scoped tasks these nodes perform — citation-complete
synthesis over an already-reconciled candidate set, and shape/citation verification against a
common contract) and only escalate to Opus if measured quality (Stage 14's eval pass rate)
doesn't clear the bar at Sonnet. This keeps the first real cost number as informative as
possible without presupposing the expensive tier.

## 3. Structural ceilings, restated as a cost bound — not a budget

From `failure_and_loop_guards.md` §3 (already set at Stage 10, restated here in dollar terms
using the verified pricing above — this is arithmetic on existing numbers, not a new estimate):

| Ceiling | Value | Worst-case cost (Sonnet 5, at list price) | Worst-case cost (Opus 5) |
|---|---|---|---|
| C1 — tokens/run | 150,000 | 150,000/1,000,000 × avg($3,$15) ≈ **$1.35** | ≈ **$2.25** |
| C2 — tokens/single call | 40,000 | 40,000/1,000,000 × avg($3,$15) ≈ **$0.36** | ≈ **$0.60** |

**This is a ceiling, not an expected cost.** A run that actually costs $1.35 on Sonnet has
already tripped C1 — that's an alert-worthy structural-cap breach per `failure_and_loop_guards.md`
§6, not a normal outcome. The real expected cost per run is almost certainly a small fraction of
this, since the happy path is 2 LLM calls, not the 6-call cap. **That fraction is exactly U1**,
and inventing it here would be the guess this programme has refused to make since Stage 01.

## 4. Turns to completion

| Path | LLM calls | Basis |
|---|---|---|
| Happy path | 2 | `langgraph_design.md`: 1 `synthesize` + 1 `critic_verify` approval, no retries |
| One retry (new, non-adjacent reason code) | 4 | +1 `synthesize`, +1 `critic_verify` |
| Maximum before structural cap | 6 | G1, `failure_and_loop_guards.md` §2 |

No number here is invented — each is a direct count from the graph's own edge conditions
(`langgraph_design.md` §2), corrected this session for the `PROHIBITION_ADJACENT` routing fix
(a `PROHIBITION_ADJACENT` verdict now terminates at 1–2 calls via `blocked`, never consuming
retry budget — slightly *lowering* worst-case spend on that path, a small positive side effect
of the bug fix worth noting).

## 5. Target budget — explicitly not set

Per BC-13 (`build_constraints_from_lean.md`) and the prompt's own exit criterion structure, a
numeric per-run dollar **target** cannot be set from this document. It requires U1. **What this
document commits to instead:** the target, once set at the measured pass (post-20a), will be
expressed as a fraction of the C1 ceiling (e.g. "p95 cost should sit below 20% of the structural
ceiling, or the ceiling itself is miscalibrated") — a relationship, not a number, until real data
exists to anchor it.

## 6. What changes at the measured pass

| Item | Design-pass value (this document) | Measured-pass replacement |
|---|---|---|
| Model tier | Recommended: Sonnet 5, pending 20a quality check | Confirmed choice, with eval pass-rate evidence |
| Tokens in/out per node | Unknown (U1) | Real distribution from 20a traces |
| Cost per run (p50/p95) | Bounded above by §3, not estimated | Real numbers |
| Target budget | Expressed as a fraction of ceiling | A real dollar figure |
