# Ontology — Stage 13

**Executes:** `prompts/17_ontology_knowledge_graph.md` §1
**Builds on:** DDD `domain_model.md` §3/§7 (ubiquitous language, aggregates), `knowledge/`
(copied and hash-verified this stage — see `knowledge/README.md`)
**Artifact status:** `stable` for Batch Review and Evidence & Provenance classes;
`provisional` for PV Intake and Supply Planning classes (same split as every prior stage —
RR-2: designed by analogy, unchecked until 20b)

---

## 0. Grounding discipline

Every class below traces to either a DDD aggregate/value object (exit criterion 1) or a real
field observed in the copied `knowledge/` corpus — not an invented schema. Where V2's own data
contains a genuine gap or inconsistency, it's stated as a finding, not smoothed over (§5).

## 1. Core classes

### 1.1 Evidence & Provenance (shared kernel — grounds all three workflows)

| Class | Traces to | Properties (verified against `knowledge_catalog.csv`) |
|---|---|---|
| **EvidenceItem** | DDD §7 `EvidenceItem` value object | `evidence_id` (V2: `doc_id`, e.g. `K-024`), `source_file`, `authority` (e.g. "NovaCura Global Policy", "External/untrusted upload"), `effective_date`, `status` (enum, §1.4), `trust` (derived citability signal — see §1.4), `jurisdiction` (e.g. `Global`, `DE`), `supersedes` (pointer), `content_hash` (SHA-256, verified at ingestion — see §5.3) |

**`EvidenceItem` is the single most load-bearing class in this ontology.** Every other class's
provenance requirement (§2) resolves through it. Its schema here is not designed from DDD prose
alone — it is read directly off `knowledge_catalog.csv`'s actual columns
(`doc_id,file,authority,effective,status,trust,jurisdiction,supersedes,sha256`), which is a
stronger grounding than the ubiquitous-language table DDD produced before this data was
examined this closely.

### 1.2 Batch Review (`stable`)

| Class | Traces to | Grounded by (V2 `data/*.csv`) |
|---|---|---|
| **Batch** | DDD §7 `Batch` aggregate root | `batches.csv`: `batch_id`, `product_id`, `site`, `status` (operational status only — see §5.1), `manufacture_date` |
| **MaterialGenealogyRecord** | DDD §2 "genealogy" (Batch Review scope) | `material_genealogy.csv`: `batch_id`, `material_lot`, `relation` (`consumed`, `missing_branch`), `source` |
| **LabResult** | DDD §2 "lab results" | `lab_results.csv`: `result_id`, `batch_id`, `test`, `value`, `unit`, `spec`, `status` (`pass`, `OOS_LIMS`) |
| **OOSInvestigation** | DDD §2 "deviations" scope | `oos_investigations.csv`: `investigation_id`, `result_id`, `lims_state`, `stats_state`, `notebook_state`, `final_state` — three independently-tracked sub-states before a `final_state`, which is itself a reconciliation target, not a single source field |
| **ReleasePacketItem** | DDD §2 "release-packet completeness" | `release_packets.csv`: `batch_id`, `packet_item`, `status` (`present`/`missing`) |
| **Deviation** | DDD §2 "deviations" | `deviations.csv`: `deviation_id`, `taxonomy`, `status` (`open`/`closed`), `capa` (pointer), `similarity_to` (pointer) |
| **CAPARecord** | DDD §2 "CAPA" | `capa_records.csv`: `capa_id`, `action`, `effectiveness_check`, `result` |

**What `Batch` cannot express (verified, not restated from memory):** `batches.csv`'s own
`status` column only ever contains operational values (`pending_review`, `quality_hold` in the
observed case data) — never a disposition. This is independent confirmation, from the actual
V2 fixture data rather than from DDD's prose alone, of DDD §7's invariant that `Batch` has no
`release_recommended`/`reject_recommended` field: **the field that would carry a disposition
does not exist in V2's own schema either.**

### 1.3 PV Intake (`provisional`)

| Class | Traces to | Grounded by |
|---|---|---|
| **ICSRCase** | DDD §7 `PVCase` aggregate root (V2 calls it an ICSR case) | `icsr_cases.csv`: `case_id`, `source`, `product`, `event`, `country`, `awareness_date`, `language`, `patient_key` |
| **DuplicateCandidate** | DDD §7 "Duplicate-check must complete before `SignalTriaged`" | `duplicate_candidates.csv`: `case_a`, `case_b`, `similarity`, `reason` — modeled as an **edge type**, not a class (§2) |
| **SafetyReceipt** | DDD §2 "reporting-clock reconstruction" | `safety_receipts.csv`: `case_id`, `channel`, `receipt` (timestamp) — one case has multiple receipts across channels; `PV_REPORTING_CLOCKS.md` (K-024) requires reconstructing chronology from **every** receipt, not the first or the most convenient one |
| **SensitiveSegment** | DDD §2 privacy boundary (new, not in original DDD table — found grounding it) | `sensitive_segments.csv`: `case_id`, `segment` (e.g. `pregnancy`, `minor`), `access_group` (e.g. `PV_PREGNANCY`) — **governance-restricted**, see §5.2 |
| **ListednessSource** | DDD §2 "listedness evidence" | `listedness_sources.csv`: `product`, `source`, `risk`, `listed` (yes/no) |

### 1.4 Supply Planning (`provisional`)

**No single V2 class maps to `ShortageOption` directly** — and that's correct, not a gap.
DDD §7 already defines `ShortageOption` as a **synthesized value object**, not a stored record;
the semantic layer's job (§3, `semantic_layer_query_contract.md`) is to compose it from these
underlying, independently-grounded classes:

| Class | Traces to | Grounded by |
|---|---|---|
| **PortfolioProduct** | DDD §2 (implicit — the shared product concept every workflow references) | `portfolio_products.csv`: `product_id`, `modality`, `stage`, `patent_months`, `primary_market`, `risk` |
| **Shipment** | DDD §2 "transport" | `shipments.csv`: `shipment_id`, `product`, `lots`, `lane`, `status` (`quarantine`, `customs_hold`), `logger`, `pallet` |
| **InventoryPosition** | DDD §2 "inventory, quality status" | `inventory.csv`: `product`, `market`, `quality_status` (`released`, `quarantine`), `units` |
| **CMOCapacityWindow** | DDD §2 "CMO capacity" | `cmo_capacity.csv`: `cmo`, `window`, `capacity_batches`, `promised_NTG`, `promised_other_sponsor` |
| **AllocationConstraint** | DDD §2 "allocation policy" | `allocation_constraints.csv`: `constraint` (e.g. `quality_released_only`), `priority` (`hard`/`high`) |

`ShortageOption` itself remains exactly what DDD §7 says: an immutable value object, always
paired with its constraint set, with **no `allocated_quantity`-shaped field anywhere in this
ontology** — confirmed again here because none of the five grounding classes above has one
either. `supply.generate_options`'s contract (`packages/contracts/tool_contracts/`) is what
actually composes a `ShortageOption` from these classes at query time.

## 2. Relationships

| Relationship | From → To | Provenance basis | Observed in V2 data? |
|---|---|---|---|
| `evidences` | `EvidenceItem` → any core-context class | The generic citation edge every `DecisionSupportOutput` claim must resolve through | Designed — the generic pattern V2's own graders check for, not a single fixture row |
| `supersedes` | `EvidenceItem` → `EvidenceItem` | `knowledge_catalog.csv`'s `supersedes` column | **Yes** — `K-006` (`BATCH_RELEASE_EVIDENCE_POLICY.md`) supersedes `K-007` (`BATCH_RELEASE_POLICY_OLD.md`) |
| `consumed_by` | Material lot → `Batch` | `material_genealogy.csv` (`relation = consumed`) | **Yes** |
| `evaluates` | `LabResult` → `Batch` | `RELATIONSHIP_MODEL.csv`: `lab_results.csv.batch_id → batches.csv.batch_id` | **Yes** |
| `investigates` | `OOSInvestigation` → `LabResult` | `RELATIONSHIP_MODEL.csv`: `oos_investigations.csv.result_id → lab_results.csv.result_id` | **Yes** |
| `documents` | `ReleasePacketItem` → `Batch` | `RELATIONSHIP_MODEL.csv`: `release_packets.csv.batch_id → batches.csv.batch_id` | **Yes** |
| `remediated_by` | `Deviation` → `CAPARecord` | `RELATIONSHIP_MODEL.csv`: `deviations.csv.capa → capa_records.csv.capa_id` (optional) | **Yes** |
| `similar_to` | `Deviation` → `Deviation` | `deviations.csv.similarity_to` (optional, self-referential) | **Yes** |
| `has_duplicate_candidate` | `ICSRCase` ↔ `ICSRCase` | `duplicate_candidates.csv` (`case_a`, `case_b`) | **Yes** |
| `has_receipt` | `ICSRCase` → `SafetyReceipt` | `RELATIONSHIP_MODEL.csv`: `safety_receipts.csv.case_id → icsr_cases.csv.case_id` | **Yes** |
| `has_sensitive_segment` | `ICSRCase` → `SensitiveSegment` | `RELATIONSHIP_MODEL.csv` (declared as `required`, with one declared exception — `PV-1020` is a deliberately absent restricted stub) | **Yes** |
| `evidences_listedness_of` | `ListednessSource` → `PortfolioProduct` | `RELATIONSHIP_MODEL.csv`: `listedness_sources.csv.product → portfolio_products.csv.product_id` | **Yes** |
| `ships` | `Shipment` → `PortfolioProduct` | `RELATIONSHIP_MODEL.csv` | **Yes** |
| `constrains` | `AllocationConstraint` → `ShortageOption` (synthesized, not stored) | DDD §7 "always paired with its constraint set" | Designed |

**`caused_by` is explicitly dropped from this ontology, despite the prompt's own example.**
The prompt's illustrative list (`caused_by`, `evidences`, `supersedes`) is not a requirement to
include all three — it's an example of the *kind* of relationship the ontology should express.
`deviations.csv`'s `taxonomy` field names a deviation *category* (e.g. `mixing_time`), not a
causal chain, and no V2 dataset links a deviation to a verified root cause independent of its
CAPA's `action` text. Modeling a `caused_by` edge here would be inventing a relationship the
evidence doesn't support — exactly the over-modeling risk §3 of the prompt warns against.

## 3. Explicitly out of scope

Stated to avoid over-modeling, per the prompt's own instruction:

| Out of scope | Why |
|---|---|
| Clinical trial entities (`subjects.csv`, `clinical_trials.csv`, `consents.csv`, …) | Workflows D/E were rejected at Stage 07 as scope expansion without a stated requirement. Their relationship rows exist in V2's `RELATIONSHIP_MODEL.csv` but are not part of this ontology |
| A `caused_by` edge type | §2 — no grounded basis; would be invented |
| An `allocated_quantity`-shaped property on any class | ADR-004 layer 1 — structurally excluded, not merely unmodeled |
| Governance/audit entities (`agent_runs.csv`, `audit_trails.csv`, `access_logs.csv`) | These describe the **system observing itself** (Stage 17's concern), not domain knowledge the agents reason over. Modeling them here would blur the ontology/observability boundary |
| A full expiry-date range on `EvidenceItem` | §5.3 — V2's data has no such field; modeling one would invent temporal semantics beyond what's evidenced |

## 4. Semantic layer and conflict rules

Covered in the two companion documents this stage produces:
[`semantic_layer_query_contract.md`](semantic_layer_query_contract.md) and
[`conflict_authority_rules.md`](conflict_authority_rules.md).

## 5. Findings from grounding against real data (not assumptions)

### 5.1 `Deviation` has no `batch_id` in V2's own schema

`deviations.csv`'s columns are `deviation_id,taxonomy,status,capa,similarity_to` — **no
`batch_id` column**, and `RELATIONSHIP_MODEL.csv` has no row linking `deviations.csv` to
`batches.csv`. This is worth stating plainly rather than assuming a clean foreign key exists:
**the deviation-to-batch link is not a guaranteed structured join in V2's own data model.** A
`batch.reconcile` call that needs to associate a deviation with a batch must do so through
other evidence (site, date, product overlap) — which is precisely the kind of reconciliation
work DDD §8 assigns to the deterministic `reconcile` tool, not to model judgment, but it means
the tool's actual matching logic (Stage 20) needs a defined heuristic, not just a foreign-key
lookup. **Flagged as an open design item for Stage 20**, not resolved here.

### 5.2 `SensitiveSegment` is a governance boundary the original DDD table didn't name

`sensitive_segments.csv` (`pregnancy`, `minor` segments with restricted `access_group`s) has no
counterpart in DDD's original entity table (`domain_model.md` §7) — it was found while
grounding this ontology against real data, not carried forward from a prior stage. This is a
genuine gap the earlier, prose-only DDD pass didn't surface. **Consequence:** the PV-Intake
Agent's evidence scope (`gen_ai_boundaries.md` §9) needs an access-group check in addition to
the bounded-context scope it already has — a case's sensitive segments must not enter a
synthesis prompt unless the requesting context has the matching `access_group`. Recorded as a
build constraint for Stage 16 (governance policy register) and Stage 20, since neither
`langgraph_design.md` nor `evidence_retrieve.schema.json` currently model an access-group
filter distinct from bounded-context scope.

### 5.3 `trust` is a derived field, not a duplicate of `status` — verified from the actual data

`knowledge_catalog.csv`'s `status` and `trust` columns differ in exactly one observed row:
`K-016` (`LOCAL_WORK_INSTRUCTION_DE.md`) has `status = local_approved` but `trust = approved`.
Every other row has identical `status`/`trust` values. This confirms, from data rather than
inference, that **`trust` is `status` normalized for citability**: a jurisdiction-local
approval is fully citable (`trust = approved`) within its jurisdiction scope — it is not a
second-class status. `conflict_authority_rules.md` §2 makes this the formal rule.

### 5.4 Integrity verification performed, not assumed

Every copied file's SHA-256 was checked against `knowledge_catalog.csv`'s own `sha256` column
at copy time (three spot-checked, all matched: `K-001`, `K-024`, `K-998`). This is the
`grade-evidence-provenance` build-process skill (`.claude/skills/skills.md` §2), applied to
this stage's own inputs — the first time that skill has actually been exercised rather than
just named.
