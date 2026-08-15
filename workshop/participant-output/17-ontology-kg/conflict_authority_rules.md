# Conflict / Authority Resolution Rules — Stage 13

**Executes:** `prompts/17_ontology_knowledge_graph.md` §4
**Must match:** Stage 01's evidence-ownership register — **not invent new rules**
**Artifact status:** `stable`

---

## 0. Constraint check before writing anything else

The prompt is explicit: these rules must match Prompt 01's evidence-ownership register, not
invent new ones. Every rule below cites the prior artifact it comes from. **Nothing in this
document is a new policy decision** — it is the existing rule set, made precise enough for a
knowledge-graph query to execute mechanically.

## 1. The citability rule — verbatim from ADR-003, re-derived from real data this stage

**A document with `status ∈ {untrusted, superseded}` is never citable, full stop.** No flag, no
downgrade-and-include.

- **Source:** ADR-003 (`../../../docs/adr/ADR-003-evidence-authority-deterministic-gate.md`), which
  itself corrected a wrong DDD assumption after reading V1's actual
  `authority_grader.py`: `_MUST_NOT_CITE = {"untrusted", "superseded"}`.
- **This stage's independent confirmation:** `knowledge_catalog.csv`'s `trust` column (§4,
  `ontology.md` §5.3) encodes exactly this — every `untrusted` and `superseded` row's `trust`
  value matches its `status`, i.e. there is no row where a `superseded`/`untrusted` document
  gets a more permissive `trust` value. The rule is confirmed twice now: once against the
  grader code (Stage 04), once against the catalog data (this stage).

**`draft` is citable.** This is the rule everyone tends to get wrong by pattern-matching
"draft sounds unapproved" — the grader's own set is exactly two statuses, not three.
`RESEARCH_NOTE_UNAPPROVED.md` (`K-026`, `status = draft`) **can** be cited; it should carry a
lower-confidence qualifier in synthesis output, but citing it is not a violation the way citing
`K-999` (`FAKE_PV_EXPEDITED_RULE.md`, `untrusted`) would be.

## 2. The jurisdiction rule — `local_approved` is not second-class within its jurisdiction

**Source:** `hitl_control_model.md` §5 — *"Global standardization vs. local jurisdictional
authority... the evidence layer must respect local authority rather than flattening it."* This
document makes that principle mechanical:

- A document with `status = local_approved` and `jurisdiction = X` is **fully citable** for any
  query scoped to jurisdiction `X` — its `trust` value is `approved` (verified,
  `ontology.md` §5.3), not a discount.
- A `local_approved` document is **not citable** for a query outside its jurisdiction, and — the
  part worth stating explicitly because it's easy to get backwards — **a `Global` document does
  not automatically override a jurisdiction-local one for matters within that jurisdiction's
  scope.** They are parallel authorities within their respective scopes, not a strict hierarchy.
  Only an explicit `supersedes` edge (§3) establishes precedence; jurisdiction scope alone never
  does.
- **Worked example, grounded in real data:** `LOCAL_WORK_INSTRUCTION_DE.md` (`K-016`,
  `jurisdiction = DE`) governs German local workflow detail. A `Global` policy on the same
  general topic does not silently supersede it — `K-016`'s own text states *"[it] does not
  override global safety or Quality authority"*, which is a **scope boundary the document
  declares about itself** (workflow detail vs. safety/quality authority), not a jurisdiction
  hierarchy. The two coexist because they govern different scopes, not because one outranks the
  other.

## 3. The supersession rule — normalize at ingestion, never re-derive from prose

**Source:** `kg_schema.md` §2's `supersedes` edge provenance requirement, `ADR-003`'s
supersession guardrail.

- `EvidenceItem.supersedes_id` is populated **only** from `knowledge_catalog.csv`'s
  `supersedes` column at ingestion.
- **Finding from real data, worth recording as a rule, not just a note:** the source column
  stores a **filename** (`BATCH_RELEASE_POLICY_OLD.md`), not a `doc_id`. The KG schema
  normalizes this to `evidence_id` (`K-007`) once, at ingestion. **No downstream component —
  not the semantic layer, not a skill, not an agent — may re-parse a document's prose to infer
  a supersession relationship.** If a document's text claims to supersede something the catalog
  doesn't record, that claim is exactly the kind of self-declared-authority the ADR-003
  guardrail exists to reject (content never gets to assert its own authority, including its
  own supersession status).
- **Transitivity is not assumed.** If A supersedes B and B supersedes C, this schema does not
  automatically treat A as superseding C — each `supersedes_id` is a single-hop pointer, and
  `knowledge_catalog.csv` has no case exercising a chain deeper than one hop in the current
  corpus. Chain resolution, if ever needed, is an explicit open item, not a default behavior to
  assume works correctly untested.

## 4. Temporal applicability — bounded by what the data actually has

**Source:** DDD ubiquitous language, "Evidence authority... temporal applicability."

- Every `EvidenceItem` has `effective_date`. A query scoped to an as-of date `D` excludes any
  item where `effective_date > D`.
- **What this rule does not do, stated honestly:** V1's data has no expiry-date field —
  temporal invalidity is expressed entirely through the `status` transition to `superseded`,
  not through a computed validity window. This document does **not** invent an expiry range.
  A document remains `approved` indefinitely until a later document explicitly supersedes it in
  the catalog. If a future stage needs a time-bounded validity window, that's a new rule
  requiring its own decision — not something this stage backfills from silence in the data.

## 5. Conflicting evidence that isn't a status conflict — the case ADR-003 doesn't cover

Sources can disagree on a **fact** while both being fully citable (e.g. two `LabResult` rows
for the same `Batch` with different `status` — `LR-88 = OOS_LIMS`, a different result
`pass`). This is not an authority conflict; it's a factual discrepancy between two
equally-citable pieces of evidence.

- **Source of the handling rule:** DDD's own domain event `EvidenceConflictDetected`
  (`domain_model.md` §6) — *"two sources disagree; must not be silently resolved."*
- **This document's contribution:** the KG schema surfaces this as a **query-time signal**, not
  a resolution. When a query returns two `EvidenceItem`- or fact-bearing nodes with the same
  key subject (e.g. same `batch_id` + same `test`) and differing values, the response marks
  both as returned with a `conflict_detected: true` flag rather than picking one. **No ranking,
  recency, or authority rule silently resolves a factual conflict between two citable
  sources** — only a `supersedes` edge (§3) or an explicit human reconciliation
  (`batch.reconcile`'s `status: "conflict"` finding, `batch_reconcile.schema.json`) does.

## 6. Summary table — every rule's single source of truth

| Rule | Source (not invented here) |
|---|---|
| `untrusted`/`superseded` never citable | ADR-003, verified against `authority_grader.py` (Stage 04) and `knowledge_catalog.csv` (this stage) |
| `draft` is citable, with a confidence qualifier | ADR-003's exact `_MUST_NOT_CITE` set (only two statuses, not three) |
| Jurisdiction-local ≠ subordinate to global | `hitl_control_model.md` §5 |
| Supersession only from catalog data, never from prose | ADR-003 (content never self-declares authority) + `kg_schema.md` §2 |
| No invented expiry window | Absence of the field in V1's actual data (`ontology.md` §5) |
| Factual conflicts flagged, never silently resolved | DDD `domain_model.md` §6, `EvidenceConflictDetected` |
