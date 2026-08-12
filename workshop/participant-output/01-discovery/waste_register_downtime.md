# DOWNTIME Waste Register — Stage 01 (Discovery)

Assessed against V2's current-state workflow (as-observed, `evidence_register.md` §7) and
the transition to V3. Each entry: observed vs hypothesized, magnitude, impact,
VA/business-required-NVA/pure-waste classification, and eliminate/simplify action.

| Category | Observed/Hypothesized | Description | Magnitude | Impact | Classification | Action |
|---|---|---|---|---|---|---|
| **Defects** | Hypothesized | Multi-agent handoffs introduce a new defect class V2 never had: an agent silently exceeding its authority limit at a context-boundary crossing (e.g. agent A hands to agent B without carrying forward a "prohibited-decision" flag). | Unknown until Stage 10 exists | High — could reintroduce a prohibited terminal decision through a handoff gap | Pure waste (rework/incident risk) | Design DDD (Stage 06) to make authority limits explicit per agent, not inferred from context |
| **Overproduction** | Hypothesized | Risk of over-building agent topology (more agents/tools than the three workflows need) before token/cost budgets are quantified (EAB-6). | Unknown | Medium — direct cost impact (Stage 15) | Pure waste if realized | Quantify budgets before Stage 04 locks topology |
| **Waiting** | Observed (in V2's process, not V3's product) | V2's document-lifecycle pipeline (13 sequential prompts) is inherently sequential; each stage waits on the prior stage's exit criteria. This is by design (evidence-gated), not accidental. | Low-medium — expected process latency | Low — this is intentional governance, not waste to eliminate | Business-required NVA | No action — this is the SDD method itself (see `SPEC_DRIVEN_DEVELOPMENT.md` §2) |
| **Non-utilised talent** | Hypothesized | If V3's agent design routes every decision through a single generalist agent instead of specialist agents per bounded context, domain-specific reasoning quality may suffer (analogous to "non-utilised talent" — the specialist capability exists in the model but isn't invoked). | Unknown until Stage 10 | Medium | Potential pure waste | Stage 10 to justify agent specialization decisions against this risk |
| **Transportation** | Hypothesized | Each additional agent hop (planner → domain agent → critic → HITL) is a "transportation" cost — data/context must move and be re-serialized at each hop. | Unknown, directly measurable once Stage 10 graph exists | Medium — architecture-visible (see C4 DMAIC lens, Stage 07) | Pure waste if hop count exceeds necessity | C4 Stage 07 DMAIC lens explicitly measures hop count as a Transportation proxy |
| **Inventory** | Hypothesized | Cached responses (Stage 14/15) are a form of "inventory" — stored answers waiting to be reused. Stale inventory (cache serving superseded evidence) is the specific risk V2's authority/freshness rules did not have to consider. | Unknown until Stage 14 | High — directly named as a required cache-correctness eval in `prompts/18_eval_ai_cache.md` | Pure waste if stale-cache serving occurs | Cache correctness evals (Stage 14) are the control |
| **Motion** | Observed | V2's prompt pipeline requires the same evidence-citation discipline restated at every stage (each prompt re-declares "cite facts, label assumptions"). This repetition is deliberate friction to keep evidence discipline, not wasted motion. | Low | Low | Business-required NVA | No action |
| **Extra processing** | Hypothesized | If V3's ontology/semantic layer (Stage 13) is not ready before agents need to query domain concepts, agents may fall back to ad-hoc raw-document RAG, then need rework once the semantic layer lands — extra processing from sequencing risk. | Unknown | Medium | Pure waste if realized | Sequence Stage 13 before Stage 10 is finalized, or design Stage 10 agents against the ontology contract from the start |

**Note:** most entries here are **hypothesized**, not observed, because V3's actual system
does not exist yet (by design — Discovery precedes architecture). This register will be
refined with observed findings at Stages 04 (final state), 06 (DDD), and 07 (C4), per the
carry-forward instruction in each of those prompts.
