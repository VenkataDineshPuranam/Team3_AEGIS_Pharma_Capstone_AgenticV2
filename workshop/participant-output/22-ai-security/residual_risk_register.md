# Residual Risk Register — Stage 18

**Executes:** `prompts/22_ai_security_threat_modeling.md`'s exit criterion: "residual risk
register exists for anything not fully mitigated."

---

## 1. Paraphrased-compliance evasion of `prohibited_action_guard`'s literal string match

**Threat:** T-01. **Rating: Medium.**

The guard (`prohibited_action_guard.py`) matches a fixed list of banned terms/phrases
(`security/policies/policy_contract.v1.json`). A model that complies with an injection but
phrases it without any literal banned term (e.g. "this batch meets all conditions to proceed
to the next stage" instead of "recommend release") would not be caught.

**Why not fixed in this stage:** closing this properly needs either a semantic classifier
(itself a new LLM call, with its own injection/reliability surface — the same problem one
level down) or a much larger banned-phrase list maintained adversarially (an arms race, not a
structural fix). Neither is a good fit for a stage whose own governing principle (ADR-004) is
"prefer structural unrepresentability over pattern-matching where possible" — but the
*terminal decision fields* are already structurally absent (layers 1+2); this residual risk is
specifically about *prose reaching a human*, where layer 3 (pattern match) is already the
documented, accepted weaker layer (`dmaic_lens.md` from Stage 10 already names this: "layer 3
pattern-matches natural language, which is inherently softer — not a defect, an honest limit").

**Revisit trigger:** if Stage 18's red-team (this stage, ongoing into 20b) or a future audit
observes an actual paraphrased-compliance incident, escalate to a dedicated Critic check for
disposition-adjacent *meaning*, not just literal terms — a new prompt instruction to the
Critic specifically, verified by its own eval category.

## 2. Denial-of-wallet ceiling is in-process only

**Threat:** T-11. **Rating: Medium**, down from **effectively unmitigated** at the start of
this stage (the guard existed but was never called from the graph — fixed this session).

**Why not fixed further in this stage:** a shared, cross-instance ceiling needs a shared store
(Redis or the audit store per ADR-006) — Redis doesn't exist until Stage 20b by design (Stage
15 deferred it). Building a shared-store dependency into 20a would violate the interim slice's
explicit "no Redis" scope.

**Revisit trigger:** Stage 20b, when Redis is added — migrate `DenialOfWalletGuard`'s
in-memory dict to the shared store as a stated exit criterion of that stage, not an afterthought.

## 3. No dependency supply-chain control exists

**Threat:** T-10. **Rating: Open — no control at all**, not merely partial.

This repo has no `requirements.txt`, `pyproject.toml`, or lockfile pinning dependency
versions — every package this session installed (`anthropic`, `openai`, `neo4j`, `langgraph`,
`pydantic`, `jsonschema`, `python-dotenv`) was installed ad hoc via `pip3 install`, with no
recorded version pins, no SBOM, and no integrity verification. `security/sbom/` exists as an
empty directory (Stage 03 scaffolding) and has never been populated.

**Why not fixed in this stage:** out of scope for a red-team pass against application logic —
this is a build/release-engineering gap, not a threat-modeling one, and fixing it properly
(pinning, SBOM generation, a `pyproject.toml`) is a discrete piece of work that touches every
file this session created.

**Revisit trigger:** should be closed **before** Stage 20b adds more dependencies (Redis
client, any PV/Supply-specific packages), not after. Recommended as an explicit Stage 20b
prerequisite, not merely "eventually."

## 4. Stale-authorization replay (T-08) is untested, not merely low-risk

**Rating: Untested**, distinct from the other rows — this isn't a known gap with a bounded
risk, it's a control whose existence has never been exercised because only one policy version
(`v1`) exists. The schema declares `POLICY_VERSION_MISMATCH` and the design
(`failure_and_loop_guards.md` §5.3, condition E4) depends on this working, but nothing in this
repo has ever created a `v2` policy contract to test against.

**Revisit trigger:** the first time `security/policies/policy_contract.v2.json` (or any
version bump) is created for a real reason, add a negative test proving a run judged against
`v1` cannot proceed once `v2` is in force.

## 5. Data-exfiltration redaction (T-09) has no PII source to test against yet

**Rating: Untested, design-only.** `trace_redaction_and_retention.md`'s ruleset (Stage 17) has
never been exercised in code — `batch_review` genuinely has no PII/PHI fields to leak (PV
Intake is where case narratives and patient references live).

**Revisit trigger:** first PV Intake build (Stage 20b) — the redaction ruleset must be wired
and tested against real PHI-shaped fixture data before that graph is considered `stable`, not
assumed to inherit `batch_review`'s clean bill of health.
