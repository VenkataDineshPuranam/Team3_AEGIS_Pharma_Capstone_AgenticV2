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

## 5. HITL timeout ladder

`hitl_control_model.md` establishes the behaviour (**timeout ⇒ no action, never auto-proceed**)
and names the escalation roles, but sets no durations. This section sets them, as a **four-tier
ladder** per workflow. Tiers are configuration, not code — Stage 16 confirms the values with
each accountable role, and changing one is a config change with an audit entry, not a
redeployment.

### 5.1 The ladder

| Tier | What happens | Changes who may approve? |
|---|---|---|
| **T0** | Interrupt fires. Primary approver role notified | — |
| **T1 — reminder** | Primary re-notified. Escalation role notified **for awareness only** | **No** |
| **T2 — escalation** | Escalation role becomes an **additional** eligible approver, *if the §5.3 conditions hold* | **Adds** one; never removes or replaces the primary |
| **T3 — expiry** | `hitl_status = timed_out`, terminal state `abstained`, reason `hitl_timeout`. **No action taken** | Approval is no longer possible; resubmission required |

**The ladder only ever widens who may say yes. It never lowers what "yes" requires, and no
tier auto-approves.** T3 is silence resolving to nothing, which is the whole point of the
default-safe rule.

### 5.2 Durations

| Workflow | Clock | T1 reminder | T2 escalation | T3 expiry | Why this shape |
|---|---|---|---|---|---|
| **Batch Review** | Business hours, approver's regional calendar | **8 bh** | **16 bh** | **24 bh** (≈3 business days) | Batch evidence review is not hour-critical, but a request must not sit for a week. A business-hours clock stops a Friday submission from expiring unseen over a weekend |
| **PV Intake** | **Wall clock — does not pause** | **4 h** | **8 h** | **24 h** | Safety clocks do not observe weekends. The window is set deliberately short so that human review of a *decision-support output* can never become the reason a downstream reporting clock is missed. See the verification note below |
| **Supply Planning** | Business hours | **8 bh** | **16 bh** (Quality leg only — see §5.4) | **24 bh** | Shortage planning is time-sensitive but produces non-executing options; nothing degrades because an option set expired |

**Verification note (PV).** The 24 h expiry is chosen on a *principle* — the system must never
sit on the critical path of a regulatory reporting clock — not by deriving it from a specific
clock. The actual expedited-reporting windows in scope must be **verified against V1's PV
material** (`knowledge/`, and whatever the PV reporting-clock fixtures encode) at Stage 13/14
before this value is finalized. Per the ADR-002 standing rule, this document does not assert V1
clock semantics it has not read. If a verified clock turns out to be shorter than 24 h for any
case class, this expiry drops below it.

### 5.3 Escalation conditions — "if we can do it at that time"

At T2 the graph **attempts** escalation. It proceeds only if **all** of these hold, evaluated
at that moment rather than at submission:

| # | Condition | Why |
|---|---|---|
| E1 | An escalation role is **named** for this workflow | Supply's primary leg has none — see §5.4. No named role, no escalation |
| E2 | The escalation role has an **active assignment right now** (Entra group membership checked at escalation time) | "Current authorization at execution time" is a required operating property. An empty or lapsed role assignment is not an approver |
| E3 | The pending output's `guard_verdict` is `clear` and no `PROHIBITION_ADJACENT` reason code is present | A blocked or prohibition-adjacent draft is never approvable **by anyone**. Escalation must not become a path to a higher-ranked yes on something the guard rejected |
| E4 | `policy_contract_version` is still in force | If policy changed mid-wait, the run is judged under a version nobody approved. Abstain and ask for resubmission (`langgraph_design.md` §4 resume semantics) |
| E5 | The escalation role's own stated authority **covers this decision** | See §5.4. Escalation transfers approval of the *AI output*, never the primary's regulatory authority |

If any condition fails, **escalation is skipped silently to the approver but recorded loudly to
the audit store** (`hitl_escalation_skipped` with the failing condition). The run stays pending
with the primary approver and proceeds to T3 on schedule. A failed escalation never shortens or
extends the ladder.

### 5.4 Who the escalation role is, per workflow

| Workflow | Primary | T2 escalation role | Authority basis |
|---|---|---|---|
| **Batch Review** | EU Qualified Person | **Chief Quality Officer** | The CQO's stated authority is "quality-system policy and risk acceptance," which covers accepting the risk of releasing a reconciliation summary. It does **not** cover batch certification — and does not need to, because the system never certifies. **Manufacturing VP remains ineligible at every tier** |
| **PV Intake** | Global Head of Pharmacovigilance | **Chief Medical Officer** | Stated authority: "clinical governance and escalation." The **Patient Safety Representative holds an advisory veto** — see below |
| **Supply Planning** | Supply Chain VP **and** Quality co-approver | **Quality leg only:** EU QP → Chief Quality Officer. **Supply leg: no escalation** | V1's stakeholder pack names no escalation role above the Supply Chain VP. Rather than invent one, the supply leg simply cannot escalate and expires at T3 |

**The Patient Safety Representative's advisory veto is not an approval path.** It may be
registered at any tier and forces `hitl_status = rejected` immediately. It can never count
toward an approval, and it is not weakened by escalation — a CMO approval does not override a
registered veto.

**Supply's dual approval survives escalation intact.** At T2 the Quality leg's eligible set
becomes {EU QP, CQO}; the supply leg stays {Supply Chain VP}. **Two approvals are still
required.** One approval plus one escalated-but-unfilled leg is still pending, and
**partial approval is not approval** — it expires to no action like any other incomplete
approval.

### 5.5 What T3 produces

- `hitl_status = timed_out`, `terminal_state = abstained`, `abstention_reason = hitl_timeout`.
- Audit: `AgentRun` closed, plus a `HumanOverrideRecorded`-adjacent entry recording **that no
  decision was made and by which roles it was not made** — the absence is the record.
- The requester is told **"no decision was made; resubmit"** — explicitly *not* "the system
  found nothing," which a reader could mistake for a clean result.
- Escalation-role notification of the expiry, so a lapsed approval is visible to the person
  accountable for the queue rather than dying quietly.
- **No cached or partial output is released.** The reconciliation work is discarded; a
  resubmission re-runs it against evidence that is current at that time, which also removes any
  chance of serving a conclusion built on since-superseded evidence.

### 5.6 Control metrics for the ladder (feeds Stage 17)

| Metric | Expected | Alert on |
|---|---|---|
| `hitl_escalated` rate | Low | A rise — approvers are not being reached at T0/T1 |
| `hitl_escalation_skipped` by condition | **Zero for E2** | Any E2 skip means a role assignment is empty or lapsed, which is a governance defect, not a scheduling one |
| `hitl_timed_out` rate | Low | A rise means approver capacity, not system correctness |
| Approvals arriving **at T2 by the escalation role** | Low | A sustained rise means the primary role is effectively not staffed — the ladder is masking an org problem it should be exposing |
| Any approval recorded after T3 | **Zero** | Any occurrence means expiry is not enforced |

The fourth row is the one worth watching. A ladder that quietly routes most approvals to the
escalation role has not solved a latency problem; it has moved accountability away from the
role the stakeholder pack assigned it to.

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
