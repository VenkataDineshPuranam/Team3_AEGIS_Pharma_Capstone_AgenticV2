# Structural Change Gate (Stage 09)

**Executes:** `prompts/09_lean_dmaic.md` §E — required before Stage 10 may begin
**Artifact status: `stable`**

---

## 1. Reopen required?

**`no`** — for structural purposes. **Gate decision: `cleared`.**

No Improve action in [`dmaic_plan.md`](dmaic_plan.md) and no constraint in
[`build_constraints_from_lean.md`](build_constraints_from_lean.md) requires a change to C4
structure, to an accepted ADR's decision, or to a technical contract. Every Tier-2 action
(I-6 … I-12) **implements** a decision that is already ratified; none amends one.

## 2. Each Improve action tested against the gate

| Action | Touches C4 structure? | Amends an ADR? | Changes a contract? | Verdict |
|---|---|---|---|---|
| I-1 token accounting | No — instrumentation inside existing containers | No | No | Clear |
| I-2 OTel + redaction | No — ADR-009 already names OTel as the instrumentation layer | No | No | Clear |
| I-3 hop/latency instrumentation | No | No | No | Clear |
| I-4 assumption-test harness | No — test asset | No | No | Clear |
| I-5 consume `eval-ai-cache/` | No | No | No | Clear |
| I-6 Prohibited-Action Guard day one | No — the component already exists in `c4_components.md` | No — implements ADR-004 | No | Clear |
| I-7 status gate at retrieval boundary | No — placement *within* the Evidence Retrieval tool | No — implements ADR-003 | Constrains the tool contract Stage 11 will *write*; does not change an existing one | Clear |
| I-8 shared-state schema | No | No — implements ADR-001 | The schema does not exist yet | Clear |
| I-9 per-graph bounds | No | No — implements ADR-008 | No | Clear |
| I-10 retry/diagnosis rules | No | No | No | Clear |
| I-11 ontology contract-first (BC-4) | **Checked carefully** — this is a *sequencing* constraint between Stages 10 and 13, not a new element or relationship | No | Defines a contract that does not exist yet | Clear |
| I-12 versioned MCP schemas | No | No | Stage 11 writes them | Clear |
| I-13 … I-16 (Tier 3) | No — deferrals | No | No | Clear |
| I-17 … I-19 (Tier 4) | No | No | No | Clear — but see §3 |

## 3. Documentation reopens — not structural, but recorded

These are defects in the **record**, not in the design. They do not gate Stage 10.

| ID | Defect | Evidence | Recommended fix | Owner |
|---|---|---|---|---|
| **D1** | **ADR-009 (Azure platform) is absent from `decision_index.md` and from `architecture_review.md`.** Both still state "8 ADRs"; the repo holds 9. ADR-009 amends ADR-001 and ADR-007 and carries an open sub-decision | Verified this stage: no occurrence of "009" in either file | Add ADR-009 to the index with its open sub-decision flagged; add a note to the review recording that the platform binding was accepted after the `pass` and does not change the verdict, because ADR-009's own guardrail keeps Azure APIs out of domain and agent logic | Stage 21, or immediately |
| **D2** | `plans/active/` is empty while `SPEC_DRIVEN_DEVELOPMENT.md` says stage specs live there (NAB-2) | Stage 05 | **Correct the method doc.** `prompts/` already are the per-stage spec; duplicating them would violate "nothing written twice" | Stage 21 |

**Why D1 is not a structural reopen.** ADR-009's status is `accepted`; its decision is a
sponsor directive, and it substitutes platform-managed services for the generic ones ADR-001
already named (Redis → Azure Cache for Redis, owned audit store → Blob with WORM). No
container, relationship, or contract changes. The architecture review's `pass` verdict stands.
What is wrong is that the index does not list it — a traceability defect, which matters for
Stage 21's defense pack and is therefore recorded rather than fixed silently.

## 4. Status flips

**None.** No ADR moves to `proposed` or `superseded`. The architecture review stays `pass`.

## 5. The open item that is *not* a reopen

**ADR-009's LLM-route sub-decision** (Route A: Claude via Azure AI Foundry, recommended;
Route B: Azure OpenAI) is open but is **not** a structural reopen trigger: no design reasoning
depends on the model family. What depends on it is **measurement** — Route B invalidates every
eval baseline and token measurement taken under Route A (trigger T-6). Practical consequence
for Stage 10: proceed; the graph design is route-independent. Practical consequence for
Stage 14: do not treat baselines as final until the route is confirmed.

## 6. Conditions that *would* force a reopen later

Recorded so the gate can be re-run rather than re-derived:

| Trigger | Would reopen |
|---|---|
| **T-1** — interim assumption 1 fails (prohibited action representable) | ADR-004, and the aggregate/tool contracts. **Stop the line** |
| **T-2** — interim assumption 2 fails (authority gate leaks) | ADR-003, and the Evidence Retrieval contract. **Stop the line** |
| **T-3** — measured token cost far above expectation | ADR-008 topology, before it is replicated to three workflows |
| **T-4** — Policy Engine hop materially inflates latency | ADR-005 |
| **T-5** — hard air-gap requirement emerges | ADR-001 and ADR-007; C4's hosted dependencies |

---

## Gate decision

**`cleared`.** Stage 10 (agentic architecture) may begin. It inherits
[`build_constraints_from_lean.md`](build_constraints_from_lean.md) §A as binding design input
and the handoff ordering at the end of that document.
