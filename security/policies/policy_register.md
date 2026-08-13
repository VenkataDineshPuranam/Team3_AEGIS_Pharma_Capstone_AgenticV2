# Policy Register — Security-Scoped Pointer

**Canonical source:** [`docs/governance/policy_register.md`](../../docs/governance/policy_register.md)
(this file does not duplicate it — `hooks.md` §4 names `security/policies/` as a forward
reference that Stage 16 must resolve; this file is that resolution).

This location exists for tooling and reviewers that specifically scope to `security/` (e.g.
Stage 18's red-team, Stage 19's compliance evidence index) without needing to traverse
`docs/governance/`. The full register — including HITL/escalation/ownership context that is
governance, not security, scoped — lives at the canonical path above.

## Security-relevant subset (fail-closed / access-control / prohibited-action boundaries)

| Policy ID | Boundary | Enforcing hook | Fail mode |
|---|---|---|---|
| P-01 | Prohibited terminal decisions | `prohibited_action_guard` (×2) | Blocked, never silently dropped |
| P-02 | Evidence authority | `evidence_gate` | Hard stop on non-citable evidence |
| P-03 | Cross-graph tool access | server-credential check | No credential ⇒ no path forward |
| P-05 | Governance/Policy Engine availability | `policy_load` | **Fail closed** — refuse, never fail open (ADR-005, BC-3) |
| P-10 | PII/PHI redaction before write | trace/audit redaction | Redact before write; discard blocked-draft text (ADR-006) |

Full rule text, source ADRs, and proving evals: see the canonical register.
