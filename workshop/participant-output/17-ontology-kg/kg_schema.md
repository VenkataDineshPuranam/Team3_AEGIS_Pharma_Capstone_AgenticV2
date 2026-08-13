# Knowledge Graph Schema — Stage 13

**Executes:** `prompts/17_ontology_knowledge_graph.md` §2
**Builds on:** `ontology.md` (this folder)
**Artifact status:** `stable` for Batch Review + Evidence & Provenance node/edge types;
`provisional` for PV/Supply

---

## 1. Node types

One node type per `ontology.md` class, plus the required properties. Every node carries
`_provenance` (§3) regardless of type — not repeated per row below.

| Node type | Key property | Other properties | Bounded context |
|---|---|---|---|
| `EvidenceItem` | `evidence_id` | `source_file`, `authority`, `effective_date`, `status`, `trust`, `jurisdiction`, `supersedes_id`, `content_hash` | Evidence & Provenance |
| `Batch` | `batch_id` | `product_id`, `site`, `operational_status`, `manufacture_date` | Batch Review |
| `MaterialGenealogyRecord` | `(batch_id, material_lot)` composite | `relation`, `source` | Batch Review |
| `LabResult` | `result_id` | `batch_id`, `test`, `value`, `unit`, `spec`, `status` | Batch Review |
| `OOSInvestigation` | `investigation_id` | `result_id`, `lims_state`, `stats_state`, `notebook_state`, `final_state` | Batch Review |
| `ReleasePacketItem` | `(batch_id, packet_item)` composite | `status` | Batch Review |
| `Deviation` | `deviation_id` | `taxonomy`, `status` | Batch Review |
| `CAPARecord` | `capa_id` | `action`, `effectiveness_check`, `result` | Batch Review |
| `ICSRCase` | `case_id` | `source`, `product_id`, `event`, `country`, `awareness_date`, `language`, `patient_key_ref` | PV Intake |
| `SafetyReceipt` | `(case_id, channel, receipt_ts)` composite | — | PV Intake |
| `SensitiveSegment` | `(case_id, segment)` composite | `access_group` | PV Intake (governance-restricted, §4) |
| `ListednessSource` | `(product_id, source)` composite | `risk`, `listed` | PV Intake |
| `PortfolioProduct` | `product_id` | `modality`, `stage`, `patent_months`, `primary_market`, `risk` | Supply Planning (shared hub — see §5) |
| `Shipment` | `shipment_id` | `product_id`, `lots`, `lane`, `status`, `logger_ref`, `pallet` | Supply Planning |
| `InventoryPosition` | `(product_id, market)` composite | `quality_status`, `units` | Supply Planning |
| `CMOCapacityWindow` | `(cmo, window)` composite | `capacity_batches`, `promised_ntg`, `promised_other_sponsor` | Supply Planning |
| `AllocationConstraint` | `constraint` | `priority` | Supply Planning |

**`patient_key_ref` and `logger_ref`, not `patient_key`/`logger`.** V2's raw `patient_key`
column is a pseudonymization key, not a display value — the KG schema stores a *reference*,
never the key itself, in line with `../../../knowledge/PRIVACY_AND_PSEUDONYMISATION.md` (K-020). This is
a schema-level decision this stage makes, not one carried forward from a prior document.

## 2. Edge types

Every edge from `ontology.md` §2, with its **provenance requirement** — the exit criterion
this document exists to satisfy ("every KG edge type has a stated provenance/authority rule").

| Edge type | From | To | Provenance requirement |
|---|---|---|---|
| `evidences` | `EvidenceItem` | any core-context node | The citing `AgentRun` must record the `evidence_id`; an `evidences` edge with no resolvable `AgentRun` back-reference is a schema violation, not just an incomplete record |
| `supersedes` | `EvidenceItem` | `EvidenceItem` | Populated **only** from `knowledge_catalog.csv`'s `supersedes` column at ingestion, normalized from filename to `evidence_id` (§5.2 — the raw column is a filename, not a key) |
| `consumed_by` | material lot (property of `MaterialGenealogyRecord`) | `Batch` | `material_genealogy.csv`, `relation = consumed` only — `missing_branch` rows produce **no edge**, and their absence is itself the finding a `batch.reconcile` gap check surfaces |
| `evaluates` | `LabResult` | `Batch` | `RELATIONSHIP_MODEL.csv` FK rule: `lab_results.csv.batch_id → batches.csv.batch_id`, `required` |
| `investigates` | `OOSInvestigation` | `LabResult` | `RELATIONSHIP_MODEL.csv` FK rule, `required` |
| `documents` | `ReleasePacketItem` | `Batch` | `RELATIONSHIP_MODEL.csv` FK rule, `required` |
| `remediated_by` | `Deviation` | `CAPARecord` | `RELATIONSHIP_MODEL.csv` FK rule, `optional` — **absence is valid** (an open deviation has no CAPA yet) |
| `similar_to` | `Deviation` | `Deviation` | `RELATIONSHIP_MODEL.csv` FK rule, `optional`, self-referential |
| `has_duplicate_candidate` | `ICSRCase` | `ICSRCase` | `duplicate_candidates.csv`; **must always carry `similarity` and `reason` properties** — an edge with a score but no reason fails `pv.duplicate_check`'s own contract (`../../../packages/contracts/tool_contracts/pv_duplicate_check.schema.json`: `matched_fields` required) |
| `has_receipt` | `ICSRCase` | `SafetyReceipt` | `RELATIONSHIP_MODEL.csv` FK rule, `required` |
| `has_sensitive_segment` | `ICSRCase` | `SensitiveSegment` | `RELATIONSHIP_MODEL.csv` FK rule, `required`, with **one declared exception** (`PV-1020` deliberately has no segment row — a stub case; the semantic layer must not error on this, per `RELATIONSHIP_MODEL.csv`'s own `declared_exception` rule type, distinct from a missing-data defect) |
| `evidences_listedness_of` | `ListednessSource` | `PortfolioProduct` | `RELATIONSHIP_MODEL.csv` FK rule, `required` |
| `ships` | `Shipment` | `PortfolioProduct` | `RELATIONSHIP_MODEL.csv` FK rule, `required` |
| `constrains` | `AllocationConstraint` | synthesized `ShortageOption` | Not a stored edge — computed at query time by `supply.generate_options`; recorded here so the semantic layer's query contract (§3) has a name for it |

**`declared_exception` vs. `required`-but-missing is a real distinction this schema must
preserve.** V2's own `RELATIONSHIP_MODEL.csv` already makes this distinction (e.g.
`sensitive_segments.csv,case_id,icsr_cases.csv,case_id,declared_exception,"PV-1020 is a
deliberately absent restricted case stub"`). A KG ingestion process that treats every missing
required edge as a data-quality defect would flag `PV-1020` incorrectly. The schema carries an
`exception_reason` property on any edge type with a declared exception, so ingestion can
distinguish "known, documented gap" from "silent data loss."

## 3. Provenance — the field every node carries

Per the prompt's requirement ("every edge must be traceable to a source document/system"),
extended here to **every node**, not just edges, because a node with no source is just as
untraceable as an edge with none:

```
_provenance: {
  source_dataset: string        # e.g. "batches.csv" or "K-024" for a knowledge doc
  ingested_at: datetime
  ingestion_run_id: string      # correlates to the AgentRun or ETL job that created this node
  source_row_hash: string       # for CSV-sourced nodes: hash of the source row, for drift detection
}
```

**This property block is why `EvidenceItem`'s `content_hash` (§1) is not redundant with
`_provenance.source_row_hash`.** `content_hash` is the SHA-256 of the *document itself*
(verified against `knowledge_catalog.csv` in `ontology.md` §5.4) — it answers "has this
document's content changed since it was approved." `_provenance.source_row_hash` answers "has
the KG's own record of this node drifted from its source dataset." They check different
failure modes: document tampering vs. ingestion drift.

## 4. Access-group property — the finding from `ontology.md` §5.2, made structural here

`SensitiveSegment.access_group` is not just a data field — the KG schema requires it to be
checked **before** any query result containing a `SensitiveSegment` node (or an `ICSRCase` node
reached via a `has_sensitive_segment` edge) is returned to a caller. This is stated here as a
schema-level requirement so Stage 16's policy register has something concrete to bind an
enforcement rule to, rather than inventing the check from scratch.

## 5. `PortfolioProduct` as a cross-workflow hub — checked against ADR-008, not a violation

`PortfolioProduct` is referenced by Batch Review (`Batch.product_id`), PV Intake
(`ICSRCase.product_id`, `ListednessSource.product_id`), and Supply Planning (`Shipment`,
`InventoryPosition`) — the only node type that appears in all three workflows' evidence.

**This does not violate ADR-008 (no cross-graph agent calls).** ADR-008 constrains *agent
invocation*, not *shared reference data*. A `batch_review` graph run and a `supply_planning`
graph run can each independently retrieve `PortfolioProduct` facts through their own
bounded-context-scoped `evidence.retrieve` server (`tool_inventory.md` §1) — **the KG schema
allows a shared node type; the tool-server design still forbids one graph's retrieval call from
reaching another graph's evidence server.** Verified against `tool_inventory.md`'s own
enforcement rule rather than assumed compatible.

## 6. What Stage 20 must not do

- Store `patient_key` (raw) or any PII/PHI value directly on a KG node — only pseudonymized
  references, per §1.
- Treat a `declared_exception` row as a data-quality alert.
- Create an `evidences` edge without a resolvable `AgentRun` back-reference.
- Populate `supersedes` from anything other than `knowledge_catalog.csv`'s own column,
  normalized to `evidence_id` at ingestion (§2) — not re-derived from document text.
