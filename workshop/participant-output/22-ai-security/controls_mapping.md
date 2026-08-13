# Controls Mapping — Stage 18

**Executes:** `prompts/22_ai_security_threat_modeling.md` §3
**Format:** threat → control → negative test → residual risk rating

---

| Threat | Control | Negative test | Residual risk |
|---|---|---|---|
| T-01 Indirect prompt injection | `prohibited_action_guard.py` (ADR-004 layer 3), fixed-string banned-terms match | `tests/security/test_prompt_injection_red_team.py` — **actually run against a live model** | **Medium** — paraphrased compliance could evade a literal-string guard; see `T-01_indirect_prompt_injection.md` |
| T-02 Direct prompt injection | `intake`'s structural admission (role/workflow are typed fields, not free text the model interprets); no user-supplied text reaches a system prompt in 20a's scope | Covered by `test_state.py`'s type-construction tests | Low — 20a has no free-text request field yet; revisit once a real request API exists (20b) |
| T-03 Tool abuse / excessive agency | Per-tool schema validation (Stage 11 contracts), `EVIDENCE_ID_NOT_IN_RUN` check (evidence must trace to this run's own retrieval) | `test_evidence_id_not_in_run_is_rejected` (`tests/contract/test_batch_reconcile_contract.py`) | Low — structurally enforced, tested |
| T-04 Cache poisoning | N/A — no cache exists | N/A | N/A until 20b |
| T-05 Agent-to-agent trust exploitation | Critic re-verifies every `synthesize` output independently; guard runs twice (before and after Critic) | `test_guard_blocks_a_disposition_signal`, full graph tests | Low |
| T-06 Evidence authority bypass | Server-side status filter in `evidence_retrieve.py` (ADR-003) + type-level `CitableStatus` constraint (two independent layers) | `test_assumption_2_malicious_and_fake_docs_never_returned` — **actually run** | Low — see `T-06_evidence_authority_bypass.md` |
| T-07 Memory/context poisoning | No cross-run memory exists by design (`memory_design.md` §2) | N/A — nothing to poison | N/A, structurally |
| T-08 Stale-authorization replay | `policy_contract_version` required on every tool call; schema declares `POLICY_VERSION_MISMATCH` | **Not exercised** — only one policy version (`v1`) exists in 20a | **Untested** — needs a second policy version to test meaningfully; deferred |
| T-09 Data exfiltration via trace/tool output | Redaction ruleset (`trace_redaction_and_retention.md` §2) — design exists, no code wired yet in 20a (no PII source in `batch_review`) | Not tested — no PII field exists to test against in this workflow | **Untested, design-only** — real test needs PV Intake (has PHI fields) |
| T-10 Supply-chain compromise | None beyond standard dependency pinning (not yet formalized — no `requirements.txt`/lockfile exists in this repo) | None | **Open — no control yet.** See `residual_risk_register.md` §3 |
| T-11 Denial of wallet | `DenialOfWalletGuard`, now wired into `intake`/`finalize` (**fixed this stage** — was previously unwired) | `infra/policies/test_denial_of_wallet_guardrail.py` (module-level, 7/7) + full graph regression suite (integration-level, confirms wiring) | **Medium** — in-process only, doesn't survive restart/scale-out; see `T-11_denial_of_wallet.md` |
| T-12 Cross-graph authority leak | Structural: only one graph (`batch_review`) exists, so there is no second graph to leak to yet; `rbac_model.md` §4 designs the service-plane isolation for when PV/Supply exist | Not testable yet — no second graph | N/A until 20b, at which point this becomes the highest-priority re-test |

## Exit-criteria check against `prompts/22`

- [x] Every threat category has a control and a residual-risk rating (see table)
- [x] Every write-capable MCP tool has a documented abuse case — **N/A**: zero write-capable
      tools exist in this system by design (ADR-004 layer 2); this is stated explicitly rather
      than left as an unchecked box
- [x] Residual risk register exists for anything not fully mitigated — see
      `residual_risk_register.md`
