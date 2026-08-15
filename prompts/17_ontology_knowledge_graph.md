# Prompt 17 — Ontology, Knowledge Graph & Semantic Layer

**Maps to:** STAGES.md Stage 13 (`stage-13-ontology-kg`)
**Lifecycle stage:** Design (domain semantics)
**Framework derived:** V2 addition, built directly on Prompt 04's ubiquitous language and bounded contexts.
**Core question:** What is the formal, machine-usable model of domain concepts and their relationships, and how do agents query it?
**Prerequisites:** Prompt 04 DDD (ubiquitous language, entities, invariants).

---

## Produce

1. **Ontology** — formal classes/relationships derived from the DDD ubiquitous language (e.g. Batch, Deviation, AdverseEventCase, ShortageOption; relationships like `caused_by`, `evidences`, `supersedes`). State what is explicitly **out of scope** to avoid over-modeling.
2. **Knowledge graph schema** — node/edge types, properties, and provenance fields (every edge must be traceable to a source document/system per Prompt 01 evidence authority).
3. **Semantic layer** — the query interface agents use (e.g. a retrieval tool contract in Prompt 15) so agents query concepts, not raw tables; maps ontology classes to underlying data sources.
4. **Conflict/authority resolution rules** — when two sources disagree on a fact, which the graph encodes as authoritative (must match Prompt 01's evidence-ownership register, not invent new rules).

### Lean / DMAIC lens (thin)

1. Which retrieval waste (unbounded, unranked context dumps) does the semantic layer eliminate versus raw RAG over documents?
2. Which domain invariants (Prompt 04) does the ontology make machine-checkable that were previously only documented?

---

## Exit criteria

- [ ] Every ontology class traces to a DDD entity/value object; no orphan classes.
- [ ] Every KG edge type has a stated provenance/authority rule.
- [ ] Semantic layer query contract is ready to become an MCP tool (Prompt 15) or retrieval component (Prompt 14).

---

## Output

Write under `docs/architecture/ontology/` and `packages/domain/` **and mirror** to `workshop/participant-output/17-ontology-kg/`:

- `ontology.md` (or `.ttl`/`.owl` if formalized)
- `kg_schema.md`
- `semantic_layer_query_contract.md`
- `conflict_authority_rules.md`
- `dmaic_lens.md` (thin)
