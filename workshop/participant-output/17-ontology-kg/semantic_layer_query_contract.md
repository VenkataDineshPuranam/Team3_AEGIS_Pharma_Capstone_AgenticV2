# Semantic Layer Query Contract — Stage 13

**Executes:** `prompts/17_ontology_knowledge_graph.md` §3
**Builds on:** `kg_schema.md` (this folder),
`../../../packages/contracts/tool_contracts/evidence_retrieve.schema.json` (Stage 11)
**Artifact status:** `stable` for Batch Review; `provisional` for PV/Supply

---

## 1. This document fills BC-4, not replaces `evidence_retrieve.schema.json`

Stage 10 designed the graph *against an ontology contract that didn't exist yet* ("BC-4:
agents designed against an ontology contract, not raw RAG — Stage 10 designs against a
contract, Stage 13 fills it in"). Stage 11 then built `evidence.retrieve`'s I/O schema without
specifying *what a query term actually resolves against*. This document is that missing
specification — it does not change `evidence_retrieve.schema.json`'s wire format at all.

**Exit criterion check:** "semantic layer query contract is ready to become an MCP tool
(Prompt 15) or retrieval component (Prompt 14)" — satisfied by construction, since it's written
as the resolution semantics of a tool contract that already exists, not a new tool.

## 2. What a query term resolves against

`evidence_retrieve.schema.json`'s `input.query.terms` (Stage 11) is free-text or structured
search terms. This document specifies that the server resolves each term against the KG, not
raw document text:

1. **Concept match** — a term matching a node type or a node's key property (e.g. `"NCB204-B24071"`
   matches `Batch.batch_id`) returns that node and everything reachable via a **single hop** of
   its bounded-context-scoped edges (§3 — this is the retrieval-scope boundary, not a search
   depth limit).
2. **Relationship match** — a term matching an edge type (e.g. `"supersedes"`,
   `"has_duplicate_candidate"`) returns the edges of that type touching any node otherwise in
   scope, with both endpoints.
3. **Text match against `EvidenceItem` content** — a term with no concept/relationship match
   falls back to full-text search over `EvidenceItem.source_file` content, scoped to
   `EvidenceItem` nodes only (never over case-data nodes like `ICSRCase`, which are not prose
   documents to search — they're structured facts to look up).

**Ranking within the candidate set happens after this resolution, inside the tool** —
consistent with `evidence_retrieve.schema.json`'s existing contract (returns `sufficient: bool`
and lets `evidence_gate` make the sufficiency call). This document does not introduce ranking
logic; it only specifies what gets ranked.

## 3. The single-hop rule and why it's the retrieval-scope boundary, not an arbitrary limit

**A query resolves at most one hop from its matched node(s), always staying within the caller's
bounded context.** This is not a performance tuning choice — it's the concrete implementation
of `agent_roster.md`'s scoped-retrieval requirement and `tool_inventory.md` §1's "no tool
retrieves across bounded contexts."

Worked example, Batch Review: a query matching `Batch(batch_id="NCB204-B24071")` returns that
node plus its directly-connected `MaterialGenealogyRecord`, `LabResult`, `ReleasePacketItem`
nodes (one hop) — but **does not** walk a second hop from `LabResult` to `OOSInvestigation`
automatically. A second hop requires a second query (bounded by the retrieval-broadening cap,
`failure_and_loop_guards.md` G3: at most one broadening per run). This keeps a single retrieval
call's context size bounded and auditable — an unbounded multi-hop traversal would be exactly
the "unranked, unbounded context dump" the prompt's own Lean question (§4 below) asks the
semantic layer to eliminate.

**The one node type this rule cannot simply apply to: `PortfolioProduct`.** Because it's a
cross-workflow hub (`kg_schema.md` §5), a naive one-hop rule from a `Batch` node would reach
`PortfolioProduct`, and a naive second hop from *there* would reach `ICSRCase` and `Shipment`
nodes belonging to other workflows entirely. **Resolution: `PortfolioProduct` is a
hop-terminator.** A query may resolve *to* `PortfolioProduct` (its own properties are
returned), but a single-hop traversal never continues *through* it to reach another workflow's
nodes. This is enforced at the server level (`evidence-retrieval-batch`, `-pv`, `-supply` are
separate processes, per `tool_inventory.md` §1) — each server's graph view simply does not
include the other two workflows' node types on the far side of `PortfolioProduct`, so there is
nothing to traverse into even if the hop rule were misapplied. Two independent enforcement
mechanisms for the same boundary, consistent with this programme's pattern of not relying on a
single layer (`prohibited_write_enforcement.md` §2).

## 4. Authority resolution happens inside this layer, before the tool response — restated precisely

`evidence_retrieve.schema.json`'s output schema already states the `untrusted`/`superseded`
filter runs inside the tool. This document specifies *where in the resolution pipeline*:

```
query terms
  → concept/relationship/text match against the KG (§2)
  → single-hop expansion within bounded context (§3)
  → citability filter: drop any EvidenceItem where status ∈ {untrusted, superseded}
    (conflict_authority_rules.md §1 — the exact ADR-003 rule, not a new one)
  → jurisdiction/effective-date filter (conflict_authority_rules.md §3)
  → sufficiency assessment
  → response (evidence_retrieve.schema.json's output shape)
```

**The citability filter runs before the caller ever sees a candidate item — not as a
post-processing step the agent or the graph applies.** This is the same claim
`evidence_retrieve.schema.json` already makes; this pipeline shows it's structurally the
*second* step after KG resolution, not bolted on afterward.

## 5. What this contract explicitly does not do

| Not done here | Why | Where it belongs |
|---|---|---|
| Change `evidence_retrieve.schema.json`'s wire format | This document specifies resolution semantics, not a new interface | — |
| Rank results by relevance beyond citability/sufficiency | Ranking-within-a-bounded-set is the synthesis skill's job for Supply (`synthesize-supply-ranking`), not the retrieval layer's | `skills.md` §1 |
| Cache query results | Explicitly deferred — `tool_inventory.md` §6 already marked this conditional on Stage 15's invalidation design | Stage 15 |
| Compose the `ShortageOption` value object | That's `supply.generate_options`'s job, consuming this layer's output | `supply_generate_options.schema.json` |

## 6. Lean lens — which retrieval waste this eliminates vs. raw RAG

Direct answer to the prompt's own Lean question:

**Unbounded/unranked context dumps, specifically:** raw RAG over `../../../knowledge/*.md` would return
whole documents or arbitrary chunks matching a keyword, with no structural guarantee that a
`superseded` document's *chunk* doesn't slip through a chunk-level filter that only checked the
whole-document status. The single-hop KG rule (§3) plus the pipeline ordering (§4) guarantee
two things raw RAG cannot: (1) the result set is bounded by *graph structure*, not by a
similarity-score cutoff that could return zero or a thousand results depending on the corpus;
(2) citability is a **node property check**, not a text-similarity artifact — a `superseded`
document cannot pass the filter by having a highly relevant-sounding chunk, because the filter
never looks at chunk content, only at the node's `status` field.

**What this doesn't eliminate:** token cost of the retrieved content itself once it passes the
filter — that's still bounded by evidence volume, not by this layer's design. Measured at
Stage 15 (U1), same as every other token question in this programme.
