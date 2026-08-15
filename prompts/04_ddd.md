# Prompt 04 — Domain-Driven Design for Gen AI (Design — Domain)

**Lifecycle stage:** Design (domain)  
**Framework derived:** DDD — Domain-Driven Design stages for Gen AI  
**Core question:** What business meaning and rules must the system respect?  
**Prerequisites:** Prompt 01 evidence register; Prompt 02 SCQA/Minto; Prompt 03 PRD/scope.  
**Primary output type:** Domain model, context boundaries, and Gen AI governance boundaries (may be provisional).

---

## Intent

Derive the **DDD framework** from evidence, the framed question, and the PRD. Model the **business**, then define where **hard rules**, **AI reasoning**, **RAG**, **agents**, and **HITL** fit — before feature specs and C4 boxes.

Theme from the reference: *From domain meaning to governed Gen AI delivery.*

If Prompt 02 narrative class is `hypothesis` (or PRD is provisional), mark all domain outputs **provisional**, prefer **rules + HITL** over autonomous AI, and use pilot/refine stages to name what evidence would stabilize the model.

---

## Entry criteria

- Prompt 02 has one bounded decision question and a capability-level answer (or experiment).
- Prompt 03 PRD has in-scope / out-of-scope (stable or provisional).
- Narrative class (`decision-ready` | `hypothesis`) is known.
- Ambiguous business terms from discovery are available to resolve into ubiquitous language.

---

## Produce

**Artifact status (required):** `stable` | `provisional`  
Use `provisional` when narrative class is `hypothesis`, or when critical ubiquitous-language / SoT questions remain open.

Work through these stages (adapt depth to evidence; do not skip governance stages):

### Domain foundation

1. **Frame business problem** — restate the Prompt 02/03 ask in domain terms (respect PRD scope).
2. **Identify domain & subdomains** — core, supporting, and generic.
3. **Build ubiquitous language** — shared vocabulary; list ambiguous/overloaded terms and resolutions (or “unresolved — provisional”).
4. **Define bounded contexts** — each with business owner and decisions they own (owners may be TBD if scarce stakeholders — flag).
5. **Create context map** — relationships (e.g. upstream/downstream, conformist, anti-corruption layer, shared kernel).
6. **Run event storming (or equivalent)** — domain events the system must be aware of.
7. **Model entities, value objects, aggregates & invariants** — responsibilities and rules that must always hold.

### Gen AI boundary design

8. **Separate rules from AI reasoning** — deterministic business logic vs probabilistic AI outputs; what AI must never decide alone.
9. **Design RAG from DDD artefacts** — what is retrieved, from which artefacts/sources, and what is out of retrieval scope.
10. **Design agent responsibilities** — tasks per agent; authority limits; stop conditions. **(V2, multi-agent):** name each agent explicitly (e.g. planner, retriever, domain-workflow agents A/B/C, critic/verifier), state which bounded context each agent is authoritative for, and note where agent-to-agent handoff crosses a context boundary (that crossing is where an anti-corruption layer or explicit contract is required — carry it into Prompt 08 and `docs/architecture/agentic/`).
11. **Define HITL & decision ownership** — when humans intervene; who owns the decision.
12. **Design evidence & audit trail** — what must be recorded for transparency and review.
13. **Define evaluation using DDD vocabulary** — domain-true success/failure cases and metrics (offline eval intent).

### Governed path

14. **Minimum governed workflow** — smallest controlled flow that delivers the framed outcome.
15. **Pilot / refine notes** — what will be learned in pilot and what would change the domain model (required emphasis in `provisional` mode; **executed** in Prompt 11 `pilot_learnings.md`).
16. **Production readiness concerns (domain view)** — domain ownership, unresolved boundary risks, handover risks (not full C4; **executed** in Prompt 12 `production_readiness.md` / Prompt 13).

Also produce:

- anti-corruption requirements (guard against misleading source-specific language);
- boundary risks and unresolved questions for Prompt 05/06;
- link back to Prompt 01 evidence acquisition backlog items that would de-provisionalize this model.

### Lean / DMAIC lens (spine — FULL at this stage)

**DMAIC focus this stage:** run the **full** Define → Measure → Analyze → Improve → Control cycle, building on Prompts 01/02's registers — do not restart from a blank page. DDD is a designated full-DMAIC stage (with Discovery/01, Frame/02, C4/06, ADR/07).

In `dmaic_lens.md`, record the full cycle:

1. **Define** — restate the improvement problem at domain-model granularity: which bounded-context boundaries exist specifically to contain a named waste or defect risk?
2. **Measure** — which domain invariants are (or should be) instrumented so a violation is measurable, not just theoretically prevented?
3. **Analyze** — root cause, at the domain level: which invariants/rules remove **Defects** (hallucinations, bad decisions) vs leaving them to the model? Where does **HITL** prevent human-review waste (review everything) while still catching high-risk cases? RAG/agent boundaries: risks of retrieval/token/context waste if unbounded? Domain ambiguities that would cause Extra processing / Motion if left unresolved?
4. **Improve** — the domain model itself is the Improve artifact: which specific modeling choices (aggregate boundaries, invariants, anti-corruption layers) are the treatment for a root cause identified above?
5. **Control** — which domain invariants need a runtime check/monitor so a violation is caught, not just documented?

Update, do not restart:

- **DOWNTIME waste register** (`waste_register_downtime.md`) — carried from Prompts 01/02, refined with domain-level findings.
- **AI-specific waste register** (`waste_register_ai_specific.md`) — same.

---

## Exit criteria (handoff to Prompt 05)

- [ ] Artifact status (`stable` | `provisional`) is stated.
- [ ] Ubiquitous language and bounded contexts are explicit (unresolved terms listed).
- [ ] Rules vs AI vs HITL boundaries are written down.
- [ ] If `provisional`: AI autonomy is minimized; HITL/rules cover domain-critical decisions.
- [ ] RAG/agent responsibilities (if applicable) map to domain artefacts, not tech fashion.
- [ ] Domain is **not** organized around technical layers or dataset names.
- [ ] Domain language is ready for Feature Specifications (Prompt 05).
- [ ] Full `dmaic_lens.md` (Define/Measure/Analyze/Improve/Control) and updated waste registers are complete (feeds Prompt 09 consolidation).

---

## Constraints

- Do not produce feature-flow documents, C4 diagrams, or ADRs except as brief open questions.
- Do not choose vendors/models unless forced by an evidence-backed constraint (then flag for ADR).
- Do not treat dataset or API names as the domain model.
- Do not treat a provisional model as production-ready domain truth.
- Do not expand beyond PRD in-scope / out-of-scope without updating Prompt 03.
- Full DMAIC and full waste registers ARE required at this stage; what remains deferred to Prompt 09 is cross-stage *consolidation*, not the first full pass.

---

## Output

Write under `docs/architecture/ddd/` **and mirror** to `workshop/participant-output/04-ddd/`:

- `domain_model.md` (include artifact status)
- `context_map.md`
- `gen_ai_boundaries.md` (rules vs AI, RAG, agents, HITL, audit, eval intent)
- `dmaic_lens.md` (full Define/Measure/Analyze/Improve/Control)
- `waste_register_downtime.md` (updated)
- `waste_register_ai_specific.md` (updated)
