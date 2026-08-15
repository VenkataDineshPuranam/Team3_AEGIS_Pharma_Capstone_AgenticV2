# DMAIC Lens — Stage 18 (AI Security)

**Full DMAIC**, per `prompts/22`: security is a designated full-DMAIC stage alongside
Discovery/Frame/DDD/C4/ADR — not a thin lens.

## Define

Which attack surface is new because this system is multi-agent/tool-using, versus V1's
single-shot app? Answer, concretely, from `threat_catalogue.md`: T-01 (indirect injection via
a tool's downstream output), T-03 (tool abuse — no tool-calling surface existed before), T-05
(agent-to-agent trust — the Critic exists specifically because a second agent shouldn't trust
the first), T-11 (denial-of-wallet via retry loops, not just per-request cost), and T-12
(cross-graph authority leak, the exact multi-agent failure mode ADR-004's own context names).
Everything else in the catalogue exists in any LLM-facing system and isn't new to this
architecture.

## Measure

**Which threats have a negative test today vs none — the actual count, not an estimate:**

| Coverage | Count | Threats |
|---|---|---|
| Actually attempted against the running system | 3 | T-01, T-06, T-11 |
| Structurally covered by existing tests (not a live attack, but a real assertion) | 3 | T-02, T-03, T-05 |
| N/A — feature doesn't exist to attack | 3 | T-04 (no cache), T-07 (no cross-run memory), T-12 (no second graph) |
| Untested, real gap | 3 | T-08 (only one policy version exists), T-09 (no PII source in `batch_review`), T-10 (no supply-chain control at all) |

**9 of 12 threats have some form of test evidence; 3 have none.** This is the honest
denominator — not "12 threats catalogued, therefore covered."

## Analyze

**Root cause per gap:**
- T-08 (stale-policy replay untested): root cause is sequencing, not neglect — a second policy
  version has never had a reason to exist yet. Not a defect, a genuinely premature test.
- T-09 (redaction untested): root cause is scope — `batch_review` has no PII field. Same
  category as T-08: premature, not neglected.
- T-10 (no supply-chain control): root cause is a real process gap — no dependency pinning was
  ever set up, for any stage, including this one. Unlike T-08/T-09 this isn't "not yet
  relevant," it's overdue now (real packages are installed and running).

**The one finding that changes the picture most:** `hooks.md` (Stage 12) listed
`denial_of_wallet_guardrail.py` as `stable — implemented and tested`, which was true of the
module in isolation but silently implied graph integration that had never happened. This is
the specific failure mode Stage 12's own rule exists to prevent — "no skill's output is ever
the last check on itself" — except here it was a *documentation* claim with no independent
check on whether the claim matched the running code. Nothing caught it until a stage
whose whole job is checking claims against running code actually ran.

## Improve

- **T-11 fixed directly**: `intake`/`finalize` now call `DenialOfWalletGuard.
  check_and_admit`/`record_run`. Confirmed via the full 107-test regression suite plus a
  targeted re-run of the interim-assumption suite (unchanged: 6/7 PASS, 1 `NOT_OBSERVABLE`).
- **T-01/T-06 evidence produced, no code change needed** — both controls held under a real
  attack attempt; residual risk recorded honestly (paraphrase evasion for T-01) rather than
  claiming a clean pass closes the question.
- **Not fixed in this stage, explicitly** (per `residual_risk_register.md`): T-10 (supply-chain
  pinning — a release-engineering task, not a threat-model fix) and the paraphrase-evasion gap
  in T-01 (needs a design decision about semantic checking, not a quick patch).

## Control

- **New standard**: any claim in `hooks.md` or `policy_register.md` that a control is
  "implemented and tested" must specify *tested at what level* — module-level and
  graph-integration-level are different claims, and this stage found they'd been conflated
  once already.
- **Monitoring**: T-11's guard now emits through the same `intake`/`finalize` path every run
  takes — Stage 17's dashboards (`dashboards.md`) already have a cost/latency panel; the
  admit/refuse decision should get its own counter there (not built this stage — a Stage 17
  follow-up, not a new Stage 18 deliverable).
- **Revisit triggers**, consolidated from `residual_risk_register.md`: T-10 before Stage 20b
  adds more dependencies; T-08/T-09 the first time a second policy version or PV Intake
  respectively actually exist; T-12 becomes the highest-priority re-test the moment a second
  graph exists.
