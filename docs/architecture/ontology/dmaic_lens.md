# DMAIC Lens — Stage 13 (Ontology / Knowledge Graph)

**Thin lens** (per `prompts/17_ontology_knowledge_graph.md`). Governed by
`docs/quality/dmaic-lean/` — the consolidated registers, not a restart.

## Define

Which domain invariants does the ontology make machine-checkable that were previously only
documented — the prompt's own second Lean question, answered directly rather than deferred.

## Measure

| Metric | Value |
|---|---|
| Ontology classes | 17 (7 Batch Review/Evidence, 5 PV, 5 Supply) |
| Classes grounded against real V2 fixture data, not DDD prose alone | 16 of 17 (`ShortageOption` is deliberately synthesized, not stored — `ontology.md` §1.4) |
| Edge types with a stated FK-based provenance rule | 10 of 14 (the rest are designed/computed, explicitly marked) |
| Findings from grounding that DDD's prose-only pass missed | 2 (`SensitiveSegment`'s access-group boundary; `Deviation` has no `batch_id` FK) |
| `knowledge/` files copied and hash-verified | 33 (32 policy docs + `knowledge_catalog.csv`) |

## Analyze — the two Lean questions this prompt asks directly

**Which retrieval waste does the semantic layer eliminate vs. raw RAG?** Answered fully in
`semantic_layer_query_contract.md` §6: the single-hop KG-structural bound replaces a
similarity-score cutoff (which can return zero or a thousand chunks depending on corpus
density), and citability becomes a **node property check** instead of a text-similarity
artifact — a `superseded` document cannot pass the filter by having a relevant-sounding chunk,
because the filter never reads chunk content.

**Which domain invariants does the ontology make machine-checkable?** Three, concretely:

1. **"`Batch` has no disposition field"** — DDD stated this as a schema *design intent*.
   Grounding against `batches.csv`'s real columns (`ontology.md` §5.1) confirms it's also true
   of V2's own operational data, independently. Once the KG schema is implemented (Stage 20),
   a query for a disposition-shaped property on `Batch` fails at the type level, not at review
   time.
2. **"`untrusted`/`superseded` are never citable"** — previously enforced only inside
   `evidence.retrieve`'s implementation (Stage 11, trust-me-it's-in-the-code). The KG schema
   makes it a **node property check any query can run**, independently of the tool's own code
   path — a second, structurally independent verification point, which is exactly this
   programme's habit of not relying on one layer.
3. **"A duplicate candidate must carry a reason, not just a score"** — `kg_schema.md` §2 ties
   the `has_duplicate_candidate` edge's required properties directly to
   `pv_duplicate_check.schema.json`'s existing contract requirement (`matched_fields`
   required). Previously this was a schema field requirement on one tool's output; now it's
   also a graph-edge invariant, checkable independent of that tool.

## Improve

The four documents are the Improve artifact, filling **BC-4** (Stage 10's ontology contract,
designed against but not populated until now). What grounding against real V2 data — rather
than working from DDD's prose alone — actually changed:

- **Found, not assumed:** `SensitiveSegment` (`ontology.md` §5.2) — a governance boundary DDD's
  original entity table never named, because DDD was written before this data was read this
  closely. This is a genuine addition to the domain model, flowing *backward* from Stage 13 to
  a gap in Stage 02, recorded honestly as a finding rather than silently patched into DDD.
- **Found, not assumed:** the `Deviation`–`Batch` link has no clean foreign key in V2's data
  (§5.1) — meaning `batch.reconcile`'s actual matching logic (Stage 20) needs a defined
  heuristic, not a lookup. Previously this would have been discovered during implementation,
  the expensive place to discover a data-model gap.
- **Confirmed, not re-derived:** the ADR-003 citability rule, checked a second time against
  `knowledge_catalog.csv`'s actual `trust`/`status` columns rather than re-trusting the Stage 04
  reading of `authority_grader.py`. Same result, independent confirmation — this is the
  `verify-against-source-not-filename` build-process skill (`.claude/skills/skills.md`),
  exercised for the second time this stage.

**NAB-3 partially resolved.** `knowledge/` (32 docs + catalog) copied and hash-verified
locally, closing the half of NAB-3 that blocked this stage. The `data/`/`evaluation/` fixture
half is explicitly left open for Stage 14, on the Overproduction argument (`knowledge/README.md`).

## Control

**Revisit triggers added by this stage:**

- If Stage 16's policy register does not add an access-group check for `SensitiveSegment`
  nodes (`kg_schema.md` §4), that's a gap traceable directly to this stage's finding, not a new
  Stage 16 discovery — Stage 16 should cite `ontology.md` §5.2, not re-derive it.
- If Stage 20's `batch.reconcile` implementation needs a `Deviation`–`Batch` matching heuristic,
  it must be documented as a design decision (which fields, what confidence threshold), not
  left implicit in code — `ontology.md` §5.1 is the open item it resolves.
- If a future document's prose claims a supersession relationship the catalog doesn't record,
  that is a contract violation to reject, not a signal to update the KG (`conflict_authority_rules.md` §3).
- `EvidenceConflictDetected` handling (§5, `conflict_authority_rules.md`) has no owner assigned
  yet for the human-reconciliation path beyond `batch.reconcile`'s `status: "conflict"` finding
  — PV and Supply's equivalent conflict-handling is untested until 20b, same RR-2 caveat as
  every other PV/Supply design in this programme.
