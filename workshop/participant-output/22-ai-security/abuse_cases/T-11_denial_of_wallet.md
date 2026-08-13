# Abuse Case T-11 — Denial of Wallet

**Status: ACTUALLY ATTEMPTED, and found a real unfixed gap this stage closed.**

## Narrative

An attacker (or a malfunctioning caller, or — as it turned out, an unreliable model) submits
enough runs, or triggers enough retry loops, to run up real cost before anyone notices. Stage
15 built and unit-tested a real ceiling
(`infra/policies/denial_of_wallet_guardrail.py`, 7/7 tests passing) months before this stage —
but a guard that exists and a guard that's actually wired into the running system are different
claims.

## What was actually run — and what it found

Reading `services/api/graph.py` as it stood at the start of this stage: the `intake` node
**never called** `DenialOfWalletGuard.check_and_admit`, and `finalize` never called
`record_run`. `hooks.md`'s hook-index table lists this guard as `stable — implemented and
tested`, which is true of the standalone module, but the claim reads as though it were wired
into the graph. It wasn't. This is exactly the class of finding Stage 18's own Analyze step
asks for: "which threats have a negative test today vs none" — this one had a negative test
for the *module*, and zero test coverage for the *integration point*, and nobody had noticed
because nothing had exercised the real graph with an LLM before this session.

**Made concrete by this session's own Groq run**: the interim-assumption tests
(`interim_state_results.md`) recorded a single request hitting **6 LLM calls** (the G1 cap)
because Groq's small model repeatedly false-rejected valid drafts. That is denial-of-wallet
pressure from an unreliable model, not an attacker — and the ceiling that should catch a
pattern of this wasn't connected to anything.

## Fix applied this stage

`services/api/graph.py`: `intake` now calls `check_and_admit` and routes to `refuse` if the
ceiling is exceeded (new conditional edge, `intake` → `refuse`/`policy_load`); `finalize` now
calls `record_run` with the real measured token usage (not the worst-case estimate) for every
non-refused terminal state. Confirmed the existing 107-test suite still passes after the
change, and re-ran the full interim-assumption suite (still 6/7 PASS, 1 `NOT_OBSERVABLE`).

## Residual risk

**Medium.** The guard is now wired, but per its own docstring it's an **in-process, per-run
in-memory dict** — the ceiling resets on process restart and does not hold across
horizontally-scaled instances. `denial_of_wallet_guardrail.py`'s own docstring already names
the fix (a shared store, Redis or the audit store) as a Stage 20b concern once Redis exists.
Recorded here again because this stage is what confirmed the gap is live, not just documented.
