# ontology

Stage 13 — domain ontology, knowledge graph schema, semantic layer design.

| Document | Answers |
|---|---|
| [ontology.md](ontology.md) | 17 classes and their relationships, grounded against `../../../knowledge/` and V1's real fixture-data schema, not DDD prose alone |
| [kg_schema.md](kg_schema.md) | Node/edge types, properties, and the provenance requirement on every edge |
| [semantic_layer_query_contract.md](semantic_layer_query_contract.md) | How a query term resolves against the graph — fills the ontology contract Stage 10 designed against (BC-4) and Stage 11's `evidence.retrieve` needed |
| [conflict_authority_rules.md](conflict_authority_rules.md) | Citability, jurisdiction, supersession, and factual-conflict rules — every one traced to an existing decision, none invented here |
| [dmaic_lens.md](dmaic_lens.md) | Which invariants this stage made machine-checkable (thin lens) |

**Status:** `stable` for Batch Review + Evidence & Provenance; `provisional` for PV/Supply
(RR-2). Two findings surfaced by grounding against real data rather than prose: a governance
boundary (`SensitiveSegment`/access-group) DDD's original pass missed, and an unFK'd
`Deviation`↔`Batch` link that Stage 20's reconciliation logic will need a heuristic for.
