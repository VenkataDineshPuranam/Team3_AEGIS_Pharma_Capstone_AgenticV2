# Interim State — Assumption Test Results (Stage 20a)

**Executes:** `interim_state.md` §3 — the seven assumption tests, now run for the first
time against real code.
**Run against:** `LLM_PROVIDER=groq` (`llama-3.1-8b-instant`), real Neo4j (AuraDB), real
Anthropic-format graph (`services/api/graph.py`).
**Status: PROVISIONAL.** Per ADR-009's "Model hosting route" section and
`packages/config/llm_client.py`'s own docstring, Groq is a dev-only substitute used while
`ANTHROPIC_API_KEY` was unavailable this session (user directive: "Use grok api"). Every
result below must be **re-run under `LLM_PROVIDER=anthropic` (Route A)** before it replaces
this document's "Unknown"/provisional status anywhere else in the repo (`token_economics.md`,
`dmaic_plan.md` trigger T-6).

Test suite: `tests/integration/test_interim_assumptions.py`. Run: `pytest
tests/integration/test_interim_assumptions.py -v -s`.

---

## Results

| # | Assumption | Result | Provider dependence |
|---|---|---|---|
| 1 | Prohibited actions structurally unrepresentable (ADR-004) | **PASS** — `BatchPayload(..., release_recommended=True)` raises at construction, before any model runs | Provider-independent (type system only) |
| 2 | Evidence authority gating (ADR-003) | **PASS** — K-998/K-999 (real adversarial fixtures, `untrusted`) never returned by `evidence.retrieve` for any matching query; server-side filter confirmed via `tool_accounting.items_filtered_untrusted` | Provider-independent (malicious content never reaches the model — filtered at the tool layer) |
| 3 | HITL routing / default-safe timeout (DDD §11) | **PASS**, after fixing a real bug this session — `hitl_interrupt` was not setting `terminal_state` on the `timed_out` decision, so `finalize`'s fallback silently mislabeled a timeout as `"completed"`. Fixed directly in the node (`services/api/graph.py`) | Provider-independent (pure state machine) |
| 4 | Degraded mode is safe (ADR-007) | **PASS** — simulated LLM outage (`ConnectionError` from both `synthesize`/`critic`) produces `abstained`/`degraded_mode`, with the deterministic `domain_payload` (9 reconciliation findings) surviving into the terminal state | Provider-independent (LLM is disabled entirely in this test) |
| 5 | Policy Engine fails closed (ADR-005) | **PASS** — unreachable policy contract → `refused`/`fail_closed`, confirmed both at the `policy_engine` unit level and via the full graph | Provider-independent (no LLM call happens before `policy_load`) |
| 6 | Token economics knowable (EAB-6) | **PASS, but PROVISIONAL** — first real, non-"Unknown" number this programme has ever produced. Observed across runs: `llm_calls` 2–6 (happy path 2, retry loops up to the G1 cap of 6), total tokens ~4,456–6,203 per run under Groq's `llama-3.1-8b-instant` | **PROVISIONAL** — must be re-measured under Claude before replacing `token_economics.md`'s Unknown |
| 7 | Hop count matches design (C4 `dmaic_lens.md`, 7-crossing baseline) | **NOT_OBSERVABLE** | This 20a build runs everything in-process except Neo4j and the LLM API call — a count here would not reflect the real deployed topology (Stage 20 containers, real network hops) and would misrepresent the assumption if reported as a number |

## Finding worth flagging beyond the pass/fail table

**A small/cheap model (Groq `llama-3.1-8b-instant`) is not reliably able to perform the
Critic's citation-discipline role.** Observed directly this session: the Critic
false-rejected a factually correct, fully-cited draft multiple times in a row
(`CLAIM_EXCEEDS_EVIDENCE`, `CITATION_UNRESOLVED`), on both the "clean" and "gap" synthetic
batches, hitting the G1 retry cap (6 LLM calls) rather than approving on the first or second
attempt. This is not a code defect — the loop guards, cap, and abstention behavior all worked
exactly as designed, catching an unreliable model rather than looping forever. It is,
however, direct evidence for **why ADR-009 requires the model variable to stay fixed while
the platform variable moves** (Route A's whole rationale): a weaker model doesn't just
produce worse prose, it changes the *shape* of the run (more retries, more cost, more cap
hits) in a way that would corrupt any conclusion drawn from Groq-measured numbers if they were
mistaken for Route A's real behavior.

## Bugs found and fixed this session, via this test suite

Three real correctness bugs were caught only because a real (if imperfect) model actually
exercised paths the deterministic `StubLLM` never did:

1. **Cap-exceeded and blocked-via-`PROHIBITION_ADJACENT` routes reached `finalize` without
   ever setting `terminal_state`**, so the fallback (`terminal_state or "completed"`) silently
   mislabeled both as `"completed"`. Fixed: added dedicated `abstain_cap` and
   `blocked_terminal` nodes.
2. **Approval detection used an empty `critic_reason_codes` list as its signal**, but that
   list accumulates across the whole run — after any prior rejection, a genuine later
   approval was misrouted using a stale reason code, wasting a retry. Fixed: route on
   `critic_verdict` directly.
3. **The HITL timeout path never set `terminal_state`** — the single highest-stakes bug of
   the three, since it affects BC-12 (timeout must never auto-proceed) directly. A timeout
   was silently finalizing as `"completed"`. Fixed: `hitl_interrupt` now sets
   `terminal_state`/`abstention_reason` explicitly for both the `timed_out` and
   approved/rejected branches, not left to `finalize`'s fallback.

## What this document does not claim

This is **not** Gate M's evaluation — that's a separate decision against Stage 09's named
triggers, using these results as input. This is also not a replacement for
`token_economics.md`'s Unknown status, which stays Unknown until a Route A re-run produces the
number that actually counts.
