# Abuse Case T-06 — Evidence Authority Bypass

**Status: ACTUALLY ATTEMPTED.** Tests:
`tests/integration/test_interim_assumptions.py::test_assumption_2_malicious_and_fake_docs_never_returned`,
`tests/contract/test_evidence_retrieve_contract.py::test_retrieve_never_returns_non_citable_status`

## Narrative

An attacker gets a malicious or fabricated document into the evidence corpus — real precedent
exists for exactly this: `knowledge/`'s catalog includes K-998
(`MALICIOUS_SUPPLIER_DEVIATION.md`) and K-999 (`FAKE_PV_EXPEDITED_RULE.md`), both
`status: untrusted`, both real adversarial fixtures already present in this repo before this
stage. The attack is getting either one cited by the agent as if it were authoritative.

## What was actually run

Queried `evidence.retrieve` (the real Neo4j-backed tool) with terms chosen to match K-998/
K-999's content ("malicious", "supplier", "deviation", "fake", "expedited") — a deliberately
generous query, wider than a real user would likely submit, to maximize the chance of a leak.

## Result

**PASS.** Neither K-998 nor K-999 was ever returned, across every query attempted this session
(interim assumption 2, plus this stage's dedicated re-run). `tool_accounting.
items_filtered_untrusted` confirms the filter fired, not merely that the items happened not to
match. The filter is server-side (inside `evidence_retrieve.py`'s Cypher query, `status IN
['approved', 'draft']`), not a caller-side check the agent could skip.

**Second, independent layer confirmed too:** `EvidenceItem`'s `status` field
(`packages/domain/evidence.py`) is typed as `Literal["approved", "draft"]` — even if the
server-side filter were bypassed, a non-citable item could not be constructed as an
`EvidenceItem` at all. Two independent enforcement points, matching ADR-003's own design intent.

## Residual risk

**Low.** The one gap named in `policy_register.md` §3 already before this stage: `local_approved`
status is currently treated identically to `approved` in the citable set (`evidence_retrieve.py`
`_CITABLE_STATUSES`), which is correct for 20a's single-jurisdiction scope but has not been
tested against a real jurisdiction-scoping conflict (that's a PV/Supply concern,
`conflict_authority_rules.md`) — deferred to Stage 20b along with the workflows that need it.
