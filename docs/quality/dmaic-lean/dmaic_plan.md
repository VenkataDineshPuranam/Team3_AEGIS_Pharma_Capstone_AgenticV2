# DMAIC Plan — Consolidated (Stage 09)

**Executes:** `prompts/09_lean_dmaic.md` §A
**Builds on:** [`lens_rollup.md`](lens_rollup.md) — nine prior lenses, reconciled
**Artifact status: `stable`**

> **Mode: MEASURE-FIRST.** Framing mode is `decision-ready` (`discovery.md` §10), but the
> scarce-data rule fires on the *other* condition: the programme's baselines are almost
> entirely **Unknown**. Every number produced in Stages 01–08 is either counted from files
> (249 tracked files, 7 designed hops, 143 V2 datasets) or explicitly Unknown (token cost,
> latency, eval pass rate, cache hit rate). **Nothing has been measured from a running
> system, because no system has run.** Instrumentation and evidence acquisition therefore
> outrank feature scale-out in Improve, and no agent/retrieval/cache scale-out is scheduled
> ahead of Measure capability.

---

## Define

**The improvement problem.** V2 delivers governed pharma decision-support as a single-shot,
document-driven exercise: one prompt in, one JSON contract out, graded post-hoc. It is safe
but cannot exercise the operational realities of a multi-agent, tool-using, cached,
continuously observed system. V3 re-architects the same three governed workflows — GxP Batch
Review, PV Intake, Supply-Shortage Planning — as a **governed, observable, multi-agent
system**, additively: the domain, the prohibitions, and the eval floor carry over unchanged;
the agent topology, tool contracts, governance layer, cache, and observability are new.

**Scope of improvement** (aligned to `scqa.md`'s Answer and the final state's §6 exclusions):

| In scope | Out of scope — permanently |
|---|---|
| Multi-agent orchestration for the 3 governed workflows | Any write integration to a brownfield system |
| Governance/policy enforcement as code, not prompting | Autonomous terminal decisions in any workflow |
| Evidence authority as a deterministic gate | Cross-workflow agent chaining (ADR-008) |
| Token/cost measurement, then control | V2 workflows D/E (no stated requirement) |
| Trace + audit observability | Re-litigating the settled V2 domain model |

**The improvement thesis, one sentence:** sequence governance and domain before architecture,
architecture before implementation, and *measurement* before scale — because every high-
severity waste in the merged register (authority leakage, stale evidence, token
multiplication) is caused by composing agents faster than the controls that bound them.

**What Define does not cover.** There are no feature-level acceptance criteria in this repo
(gap G2 — no feature-spec stage). Define is therefore anchored to workflow prohibitions and
ADR thresholds, which are stricter and already ratified.

## Measure

### Current-state metrics — what is actually known today

| Metric | Value | Class | Source |
|---|---|---|---|
| Tracked files in repo | 249 | Fact (counted) | `current_state_assessment.md` |
| Stages complete | 8 of 21 | Fact | `STAGES.md` |
| Implementation | **Zero** — `apps/`, `services/`, `packages/`, `tests/` are stubs | Fact | Stage 05 |
| Evidence records produced | **Zero** — all 9 `evidence/` subfolders empty | Fact | Stage 05 |
| ADRs accepted | 9 of 9 | Fact | `docs/adr/` |
| Architecture review | `pass` | Fact | `architecture_review.md` |
| Designed hop count, Batch Review common path | **7** container/component crossings one-way | Derivation (designed, never measured) | `c4/dmaic_lens.md` |
| Sync-call depth | 3 | Derivation | `c4/dmaic_lens.md` |
| Policy Engine fan-out | 4 consumers | Derivation | `c4/dmaic_lens.md` |
| Containers in target design | 9 | Fact | `c4_containers.md` |
| Unconsumed reference material | 29 files in `eval-ai-cache/` | Fact | Stage 05 |

### Unknown baselines — listed explicitly, not estimated

| # | Baseline | Unknown since | First becomes measurable | Blocks |
|---|---|---|---|---|
| U1 | **Token / cost per workflow run** | Stage 01 (EAB-6) | Interim state, assumption 6 | Stage 15; topology confirmation |
| U2 | Latency per workflow run | Stage 01 | Interim state | Stage 15 SLOs |
| U3 | Eval pass rate on V2's 12 categories | Stage 01 | Stage 14 harness on the interim slice | Release gating |
| U4 | Cache hit rate | N/A (no cache) | Final state only — cache is excluded from interim by design | Stage 15 |
| U5 | Actual hop count vs. the designed 7 | Stage 03 | Interim state, assumption 7 | Stage 12 drift finding |
| U6 | Added latency from the ADR-005 Policy Engine hop | Stage 04 | Interim state | ADR-005 revisit trigger |
| U7 | HITL escalation rate and reviewer load | Stage 01 | Final state (needs all 3 workflows) | Stage 16 risk-tiering |
| U8 | V2's own eval scorecard numbers | Stage 01 | Deliberately never read — out of scope (ADR-002) | Nothing |

**U1 is the disproportionate one.** It has been Unknown since Stage 01, it was the stated
precondition for locking agent topology, and that precondition was **not met** — ADR-008 was
accepted without it (see `lens_rollup.md` C3). Its first real value comes from the interim
state.

### Target metrics

Absolute targets — non-negotiable, zero-tolerance, from ADRs and workflow prohibitions:

| Target | Threshold | Owning decision | Verified at |
|---|---|---|---|
| Prohibited-action findings | **Zero**, and the block must occur at the **schema** layer | ADR-004 | Interim assumption 1; Stage 14 evals; Stage 18 red-team |
| Citations of `untrusted` / `superseded` evidence | **Zero** | ADR-003 | Interim assumption 2; Stage 14 |
| Cross-graph agent invocations | **Zero** | ADR-008 | Stage 18 red-team |
| HITL routing rate, PV + Supply | **100%** | DDD §11 | Stage 14/16 |
| HITL timeout outcome | **No action**, never auto-proceed | DDD §11 | Interim assumption 3 |
| Policy Engine unreachable | Request **refused** (fails closed) | ADR-005 | Interim assumption 5 |
| Correctness gates with any single dependency disabled | **All pass** (capability may degrade) | ADR-007 | Interim assumption 4 |
| Audit-store write success while LangSmith healthy | **100%** | ADR-006 | Stage 17 |
| `AgentAuthorityExceeded` events | **Zero**, alert on any nonzero | DDD Control | Stage 17 dashboard |

Comparative targets — **cannot be set now**; setting them now would be guessing:

| Target | Set at | Anchored to |
|---|---|---|
| Token/cost budget per graph and per node | Stage 15, using U1 | Interim measurement, not estimate |
| Latency SLO per workflow | Stage 15, using U2 | Interim measurement |
| Cache hit-rate target | Stage 15 | Post-cache measurement |
| Fast-eval-subset runtime budget | Stage 14 | Developer-velocity observation |
| Hop-count tolerance band around 7 | Stage 12 | U5 |

## Analyze

Root causes, each traced to the register rows it explains
([`waste_register_downtime.md`](waste_register_downtime.md),
[`waste_register_ai_specific.md`](waste_register_ai_specific.md)):

| # | Root cause | Explains | Class |
|---|---|---|---|
| **RC-1** | **Prohibition was expressible in the data model.** The failure mode is not an agent choosing to act — it is a schema that can *represent* release/reject/allocation at all. Prompting cannot fix a representable state | D-rows 1–2; the whole ADR-004 layer stack | Derivation, from DDD analysis — **assumption until interim assumption 1 runs** |
| **RC-2** | **Authority was treated as content, not status.** If a document's trustworthiness is judged by reading it, a document can assert its own trustworthiness — the prompt-injection path | AI-Retrieval, AI-Model rows | **Fact** — verified against V2's `authority_grader.py`, which defines `_MUST_NOT_CITE = {"untrusted","superseded"}` |
| **RC-3** | **Composition outruns control.** Each added agent turn multiplies tokens, hops, and handoff surfaces; without per-graph bounds this grows super-linearly with workflow count | AI-Token, D-Transportation, D-Overproduction | Derivation — magnitude Unknown (U1) |
| **RC-4** | **Simultaneous risk introduction makes failure ambiguous.** Cache + agents + governance at once means a failure cannot be attributed | D-Inventory, D-Defects | Derivation — the interim state is the countermeasure |
| **RC-5** | **Compliance obligations attached to vendor-owned surfaces.** Audit retention on a SaaS SLA is an availability/retention risk dressed as observability | AI-Observability | Derivation — resolved by ADR-006 |
| **RC-6** | **Reference material already in the repo goes unread.** 29 `eval-ai-cache/` files, 32 V2 knowledge docs, V2 fixtures — re-deriving these is pure Overproduction | D-Overproduction (NAB-3, NAB-4) | **Fact** — counted at Stage 05 |
| **RC-7** | **Method-vs-practice drift in the SDD scaffold itself.** `plans/active/` empty, ADR-009 absent from the decision index and architecture review | NAB-2; `lens_rollup.md` C4 | **Fact** — verified this stage |

**Analyses resting on assumptions — flagged, per the prompt's constraint.** RC-1, RC-3, RC-4
and RC-5 are *design-time derivations with no execution evidence behind them*. They are
plausible and internally consistent, and every one of them is scheduled for a specific
interim-state test. None of them may be described as "fixed" before that test runs. RC-2, RC-6
and RC-7 rest on verified file evidence.

**The one analysis that changed a decision.** RC-2 came from reading V2's actual 66-line
grader rather than inferring behaviour from filenames — and it found an error in this
programme's own DDD model, which had claimed `superseded` documents were citable with a flag.
That correction is the precedent for the standing rule: never claim V2 behaviour without
verifying V2 code.

## Improve

Ordered. **Instrumentation and evidence acquisition come first** — the scarce-data rule.

### Tier 1 — Measure capability (must precede any scale-out)

| # | Action | Removes | Owner stage | Cross-link |
|---|---|---|---|---|
| I-1 | Token/cost accounting per node and per graph run, emitted from the first run of the interim slice | AI-Token (U1, EAB-6) | 17 instrumentation, 20 implementation | `evidence_acquisition_backlog.md` EAB-6 |
| I-2 | Trace instrumentation via **OpenTelemetry** as the layer, LangSmith + Azure Monitor as backends, with redaction rules defined *before* first trace is written | AI-Observability (PII over-capture) | 17 | ADR-006, ADR-009 |
| I-3 | Hop-count and latency instrumentation on the common path, comparable to the designed 7 | D-Transportation (U5, U6) | 17 | `c4/dmaic_lens.md` |
| I-4 | Assumption-test harness for interim §3's seven assumptions | RC-1, RC-2, RC-4 | 14 | `interim_state.md` §3 |
| I-5 | Consume `eval-ai-cache/`'s 29 files (24-part brownfield-evals runbook, Redis, OTel) instead of re-deriving | D-Overproduction (RC-6, NAB-4) | 14, 15, 17 | Stage 05 §6 |

### Tier 2 — Structural waste removal (design already decided; must be built as specified)

| # | Action | Removes | Owner stage |
|---|---|---|---|
| I-6 | Prohibited-Action Guard as an enforced hook, present **day one** — not retrofitted | D-Defects (RC-1) | 12, 16 |
| I-7 | Evidence status gate at the **retrieval boundary**, before ranking | AI-Retrieval, D-Defects (RC-2) | 11, 13 |
| I-8 | LangGraph shared-state schema as the single source of truth; no per-agent context reconstruction | AI-Context | 10 |
| I-9 | Per-graph step and token bounds (numbers set at Stage 15 from I-1's data; the *bound mechanism* built at Stage 10) | AI-Token (RC-3) | 10, then 15 |
| I-10 | Explicit retry/backoff/diagnosis rules — no blind retry | AI-Model (gap G3) | 10 |
| I-11 | Ontology **contract** defined before agents are built against it; contract filled in at Stage 13 | D-Extra-processing (C1) | 10 → 13 |
| I-12 | Versioned MCP schemas + contract tests in `tests/contract/` | AI-Integration | 11 |

### Tier 3 — Deferred by design (do not pull forward)

| # | Item | Why deferred | Lands at |
|---|---|---|---|
| I-13 | Redis cache | Adds stale-authority risk on top of agent-correctness risk; failures become ambiguous | Final state / 14–15 |
| I-14 | Workflows B and C | Replicating an unvalidated pattern is Overproduction | Final state |
| I-15 | Batch Review HITL risk-tiering | Needs U7 (real escalation rates); PV/Supply stay at 100% routing regardless | 16 |
| I-16 | Fast-subset vs full-regression eval split | Needs an actual suite runtime to split | 14 |

### Tier 4 — Documentation accuracy (cheap, unblocks nothing, but keeps the record true)

| # | Item | Action |
|---|---|---|
| I-17 | NAB-2 — `plans/active/` empty vs. method doc | **Correct the method doc.** `prompts/` already are the per-stage spec; duplicating them violates "nothing written twice" |
| I-18 | ADR-009 missing from `decision_index.md` and `architecture_review.md` | Add it; note its open LLM-route sub-decision |
| I-19 | NAB-3 — copy V2 `knowledge/` + fixtures locally, or keep cross-repo | Decide before Stage 13 |

## Control

### Standards that hold regardless of stage

1. **Prohibition enforcement is structural, never prompt-based** (ADR-004's three layers:
   absent schema field, absent tool method, runtime guard).
2. **Authority is a status lookup, never a model judgement** (ADR-003). Content never
   self-declares authority.
3. **Fail closed.** Policy Engine unreachable ⇒ refuse. HITL timeout ⇒ no action.
4. **No claim of V2 behaviour without reading V2 code** (ADR-002 guardrail, RC-2 precedent).
5. **Status honesty.** Artifacts are marked `provisional` until their dependencies are
   `stable`; "designed" is never reported as "measured."

### Monitoring ownership — named for Assurance (Stage 12/21)

| Signal | Threshold | Instrumented at | Owning role |
|---|---|---|---|
| `AgentAuthorityExceeded` events | Zero; alert on any | 17 | Governance & Oversight context owner |
| `untrusted`/`superseded` citations | Zero | 14 evals + 17 traces | Evidence & Provenance kernel owner |
| HITL routing rate, PV/Supply | 100% | 16 + 17 | Workflow approver roles: Global Head of PV; Supply Chain VP + Quality co-approver |
| HITL timeout outcomes | Always "no action" | 16 | As above |
| Batch Review approvals | EU Qualified Person only (esc. Chief Quality Officer). **Manufacturing VP is explicitly not an approver** | 16 | EU QP role |
| Audit-store write success while LangSmith healthy | 100% | 17 | Audit store owner |
| Token/cost per run vs. budget | Budget set at 15 from U1 | 15 + 17 | Architecture owner |
| Cache serving superseded evidence | Zero | 14 cache-correctness evals | Stage 14 owner |

Accountability attaches to **roles, not individuals**, so controls survive turnover
(ISO 42001 expectation) — see `hitl_control_model.md`.

### Revisit triggers

| # | Trigger | Consequence |
|---|---|---|
| **T-1** | Interim assumption **1** fails (prohibited action representable) | **Stop the line.** ADR-004 invalidated; design reopens. Not a bug fix |
| **T-2** | Interim assumption **2** fails (authority gate leaks) | **Stop the line.** ADR-003 invalidated |
| **T-3** | Interim assumption **6** (U1) measures far above expectation | Revisit **ADR-008** topology *before* it is built three times — this is the debt from `lens_rollup.md` C3 coming due |
| **T-4** | ADR-005's extra hop becomes a material share of the latency budget | ADR-005 revisit trigger fires |
| **T-5** | Sponsor later requires a hard air-gap | ADR-007 and ADR-001 reopen; the known limitation becomes a blocker |
| **T-6** | LLM route resolves to **Azure OpenAI** rather than Claude via Foundry | All Stage 14 eval baselines must be re-run; design reasoning survives, measurements do not |
| **T-7** | Stage 14 begins with `eval-ai-cache/` still unconsumed | That stage must justify in its Measure step why it is deriving rather than reusing |
| **T-8** | Stage 16 begins and the interim placeholder approver is still in place | Release-gate failure — named approvers exist and must be used |
| **T-9** | Implemented hop count exceeds 7 without a documented reason | Stage 12 assurance finding |
| **T-10** | Any Batch Review interim conclusion is applied to PV or Supply without re-checking | Stage 20 acceptance-condition violation (the single-workflow generalization risk) |
