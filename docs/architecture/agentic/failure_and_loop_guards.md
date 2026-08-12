# Failure & Loop Guards — Stage 10

**Executes:** `prompts/14_agentic_architecture.md` §5 and its Control lens
**Artifact status:** `stable` for the `batch_review` graph, except the HITL timeout (§5), which
is marked `provisional` and named as an open item for Stage 16

---

## 1. Resolving an apparent conflict between two stage requirements

Stage 10's exit criteria say **"loop guards and budgets are numeric, not aspirational."**
Stage 09's constraint BC-13 says numeric token budgets are deferred to Stage 15 because setting
them now would be guessing.

Both are right, because they are about different things. This design separates them:

| Kind | Set now? | Basis | Example |
|---|---|---|---|
| **Structural caps** | **Yes, numeric now** | Derived from the graph's own shape — how many LLM calls the design *can* make is a property of the design, not of measurement | Max 2 agent↔critic loops |
| **Safety ceilings** | **Yes, numeric now, provisional** | A kill-switch set far above any plausible run and far below denial-of-wallet. Does not require knowing typical cost — only that a run 50× larger than the design allows is definitionally broken | 150k tokens/run |
| **Performance budgets** | **No — Stage 15** | Requires U1/U2, measured at 20a | p95 cost per run |

A ceiling is not a budget. The ceiling says "this run has gone insane, stop it"; the budget
says "this run cost more than it should." Only the second needs data.

## 2. Structural caps — `batch_review` (20a)

| # | Guard | Value | Derivation |
|---|---|---|---|
| G1 | Max **LLM calls** per run | **6** | 3 synthesis attempts (initial + 2 retries) + 3 critic passes. The graph cannot construct a 7th |
| G2 | Max **agent↔critic loops** | **2** (3 total attempts) | Two rejections with distinct reason codes is already an ambiguous case; a third attempt is guessing |
| G3 | Max **retrieval broadenings** | **1** | Scope-preserving only. If one broadening within the bounded context does not yield sufficient evidence, the honest answer is abstention |
| G4 | Max **tool calls** per run | **8** | 2 retrieve + 1 reconcile + headroom for retries. Anything above is a loop |
| G5 | Max **graph steps** (supersteps) | **40** | ~3× the longest legal path (13 nodes incl. retries). Catches cycles the specific guards miss |
| G6 | Max **wall clock**, excluding HITL | **300 s** | Excludes the interrupt, which is measured in hours |
| G7 | Per-LLM-call **timeout** | **60 s** | Below G6 so a hung call cannot consume the whole budget |
| G8 | Max **concurrent runs per requester** | **3** | Denial-of-wallet blunt instrument until Stage 15 sets a real quota |

**These are compile-time properties where possible.** G1–G3 are enforced by the graph's edge
conditions, not by a runtime counter check that a node could skip — the edge from
`critic_verify` back to `synthesize` simply does not exist once `llm_calls >= 6`.

## 3. Safety ceilings — provisional, replaced by measured budgets at Stage 15

| # | Ceiling | Value | Why this number is defensible without measurement |
|---|---|---|---|
| C1 | **Tokens per run** (in + out, all nodes) | **150,000** | The design allows 6 LLM calls; even at a generous ~25k tokens of context each, a legal run cannot exceed this. A run that does has escaped its structural caps |
| C2 | **Tokens per single LLM call** | **40,000** | Bounds a single runaway context assembly |
| C3 | **Cost per run** | **not set** | Deliberately absent — cost is route-dependent (ADR-009 decision 1) and would be a guess. C1 bounds it indirectly |
| C4 | **Runs per requester per hour** | **20** | Blunt denial-of-wallet guard; Stage 15 replaces it with a real quota |

**On breach: the run terminates as `abstained` with reason `ceiling_exceeded`, and the breach
is an alert, not a log line.** A ceiling breach means a structural cap failed, which is a
defect in the graph — the interesting signal is not the cost, it is that G1–G5 did not hold.

**Replacement condition:** at Stage 15, C1/C2/C4 are replaced by budgets derived from 20a's
measured distribution (U1). The ceilings do not disappear — a budget bounds the normal, a
ceiling bounds the insane, and a mature system keeps both.

## 4. No-progress and cycle detection (BC-5 — no blind retry)

**The rule that makes a retry legitimate:** every retry must carry a **reason code from a
closed enum**, recorded in `critic_reason_codes[]`, and must be *different* from every prior
code in that run. A retry without a diagnosis is a blind retry, and the graph has no edge for
it.

| Reason code | Meaning | Retry allowed? |
|---|---|---|
| `MISSING_CITATION` | A claim has no supporting citation | Yes — actionable |
| `CITATION_UNRESOLVED` | A citation does not match an item in state | Yes |
| `CLAIM_EXCEEDS_EVIDENCE` | A claim asserts more than the cited evidence supports | Yes |
| `ABSTENTION_EXPECTED` | Evidence insufficient but output did not abstain | Yes |
| `CONTRACT_VIOLATION` | Output does not conform to `DecisionSupportOutput` | Yes, once |
| `PROHIBITION_ADJACENT` | Output reads as a disposition signal | **No** — straight to `blocked`, never retried. Retrying a prohibited-action-adjacent draft is asking the model to rephrase its way past a control |

**Repeated code ⇒ escalate, do not retry.** If the Critic returns a code already in the list,
the run routes to `hitl_route` with the code and both drafts attached. The human sees what the
system could not resolve, which is more useful than a third attempt.

**Cycle detection:** a fingerprint of `(evidence_ids, draft_output_hash, critic_reason_code)`
is recorded each loop. An identical fingerprint on consecutive iterations means the retry
changed nothing — terminate as `abstained`, reason `no_progress`, regardless of remaining
budget. This catches the case where the model "fixes" the output by rewording it.

## 5. HITL timeout — the one number this stage will not invent

`hitl_control_model.md` establishes the behaviour (**timeout ⇒ no action, never
auto-proceed**) and the escalation roles, but no duration. A batch-review approval window is a
GxP operational parameter belonging to the accountable role, not to this document.

**Proposed for 20a only, explicitly provisional:**

| Step | Proposed | Confirm with |
|---|---|---|
| First escalation notice | 24 h | EU Qualified Person (Batch) |
| `timed_out` ⇒ no action | 72 h | Chief Quality Officer |

**Open item for Stage 16:** confirm both durations per workflow with the accountable roles.
PV and Supply may need different windows — a PV reporting clock is a regulatory constraint,
not an SLA preference, and Supply's dual approval needs a rule for the case where one approver
responds and the other does not. **Partial approval is not approval**; the run stays pending
and times out to no action.

## 6. Failure taxonomy — what the graph does when it cannot make progress

| Failure | Terminal state | Alert? | Rationale |
|---|---|---|---|
| Evidence insufficient after one broadening | `abstained` / `insufficient_evidence` | No | The designed, correct outcome. Frequent abstention is a signal about the evidence base, not a defect |
| Tool unreachable | `abstained` / `dependency_unavailable` | Yes (ops) | Never guess on unretrieved evidence |
| LLM provider unreachable | `abstained` / `degraded_mode` **with the deterministic partial result attached** | Yes (ops) | ADR-007: the rules-only path still produces auditable findings |
| Policy Engine unreachable | `refused` / `fail_closed` | Yes | ADR-005. Refuse, do not pass through |
| Guard blocked a draft | `blocked` | **Yes — governance** | `ProhibitedActionBlocked`. Rare by design; each one is reviewed |
| Non-citable evidence found past the retrieval boundary | `refused` / `gate_defect` | **Yes — stop-the-line class** | The ADR-003 filter failed. The run is untrustworthy and so is every concurrent run |
| No progress / cycle | `abstained` / `no_progress` | No | Working as designed |
| Structural cap hit | `abstained` / `cap_exceeded` | Yes (engineering) | The design should rarely reach its own caps; frequent hits mean the caps or the graph are wrong |
| Safety ceiling hit | `abstained` / `ceiling_exceeded` | **Yes — defect** | A cap failed to hold |
| `AgentAuthorityExceeded` observed | `refused` | **Yes — stop-the-line class** | Should never fire. Any occurrence is a Stage 12 and Stage 18 finding |

**One invariant across every row: the system never truncates and answers.** There is no
failure mode whose response is a partial answer presented as complete. Abstention is always a
valid terminal state, and it is the default direction of failure.

## 7. Control metrics these guards produce (feeds Stage 17)

Every guard emits a counter, so runaway behaviour is a dashboard line rather than a hope:

| Metric | Expected | Alert on |
|---|---|---|
| `llm_calls` per run | 2 (the happy path: one synthesis, one critic) | p95 ≥ 5 — the graph is retrying a lot |
| `critic_reject_rate` by reason code | Low, and dominated by `MISSING_CITATION` if anything | Any `PROHIBITION_ADJACENT` occurrence |
| `abstention_rate` by reason | Non-zero is healthy | A sudden drop — that means the system got *less* cautious |
| `cap_exceeded` / `ceiling_exceeded` | **Zero** | Any |
| `gate_defect`, `AgentAuthorityExceeded`, `ProhibitedActionBlocked` | **Zero** | Any — each is an incident |
| `hitl_timed_out` rate | Low | A rise means approvers are overloaded, not that the system is wrong |
| Tokens per run distribution | — | Feeds U1 at 20a; no threshold until Stage 15 |

**Note on the zero-expected metrics.** Their absence is not proof of safety — it may mean the
control is not wired. Stage 18's red-team must *deliberately trigger* `ProhibitedActionBlocked`
and confirm it fires, which is exactly interim assumption 1 (DDD §6 makes this same point about
the event's existence being the control signal).
