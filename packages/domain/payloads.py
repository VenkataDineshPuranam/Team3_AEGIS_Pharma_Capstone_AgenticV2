"""Per-workflow domain payloads -- Stage 20a Phase 1.

Executes langgraph_design.md SS3's "what this schema deliberately cannot express" table
(ADR-004 layer 1). `extra="forbid"` on every model here is load-bearing, not decoration:
a caller cannot smuggle `release_recommended`, `causality`, `allocated_quantity`, or any
other disposition field through even if a node tried, because pydantic raises on
construction rather than silently dropping the extra key.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ReconciliationFinding(BaseModel):
    """Mirrors batch_reconcile.schema.json's `findings[]` shape exactly -- structural
    completeness/conflict status only, never a disposition. See that schema's own
    `what_this_schema_cannot_express` list."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: Literal[
        "genealogy",
        "lab_results",
        "environmental_monitoring",
        "deviations",
        "capa",
        "change_control",
        "validation_state",
        "supplier_evidence",
        "release_packet_completeness",
        # Added closing INJ-027 (Stage 21 gap-closure): process-analytical-technology
        # model/recipe version sync is a distinct evidence category from change_control --
        # a PAT model can drift independently of a formally logged change record.
        "process_analytical",
    ]
    status: Literal["complete", "gap", "conflict"]
    evidence_ids: tuple[str, ...]
    gap_description: str | None = None


class BatchPayload(BaseModel):
    """batch_review's domain_payload extension. No field here can represent
    release/reject/reprocess/relabel/recall -- ADR-004 layer 1, ratified again by
    batch_reconcile.schema.json's own `what_this_schema_cannot_express` list."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    batch_id: str
    reconciliation_complete: bool
    findings: tuple[ReconciliationFinding, ...]


class DuplicateCandidate(BaseModel):
    """Mirrors pv_duplicate_check.schema.json's `candidates[]` shape exactly -- a
    structural similarity score only, never a duplicate determination as a final safety
    conclusion (that schema's own `what_this_schema_cannot_express`)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    candidate_case_id: str
    similarity_score: float
    matched_fields: tuple[
        Literal["patient_identifiers", "product", "event_date", "reporter", "narrative_similarity"], ...
    ]
    # Stage 21 gap-closure (INJ-037): which intake channel this candidate came from, so a
    # cluster spanning a patient programme, a literature vendor and a call centre can be
    # represented as one cluster rather than three independent near-misses. Informational
    # only -- it does not change how similarity_score is computed or interpreted.
    source_channel: Literal[
        "patient_programme", "literature_vendor", "call_centre", "direct_report", "social_media", "other"
    ] | None = None


class NormalizationSuggestion(BaseModel):
    """Mirrors pv_normalize_terminology.schema.json's `suggestions[]` shape. Always a
    suggestion, never applied -- `applied` is fixed False at the schema layer there; this
    model has no field that could represent 'applied: true' either."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    normalized_term: str
    confidence: float
    terminology_source: str


class AwarenessDateRecord(BaseModel):
    """Stage 21 gap-closure (INJ-038): one channel's own record of when the organization
    first became aware of a case. PV_REPORTING_CLOCKS.md's rule (K-024) -- exercised by
    eval-ai-cache/graders/pv_duplicate_clock_grader.py -- is that the reporting clock
    starts at the EARLIEST of these across channels, never the last-processed one. This
    model carries the raw per-channel dates; the earliest is computed, never asserted by a
    single channel's own record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    channel: str
    awareness_date: date


class ListednessSource(BaseModel):
    """Stage 21 gap-closure (INJ-040): one authority document's own expectedness
    statement for this event/product pair. Surfaced so a human can see the investigator
    brochure, core data sheet and local label disagree -- this model has no field that
    could assert a single reconciled 'expectedness' conclusion (security/policies/
    policy_contract.v1.json bans that field/term outright for pv_intake)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_document: str
    status: Literal["expected", "unexpected", "not_stated"]


class DisproportionalitySignal(BaseModel):
    """Stage 21 gap-closure (INJ-044): a computed statistical ratio, presented as
    evidence for a human's own judgment -- never a signal determination. The
    policy_contract's `signal_confirmed` ban stays exactly as strict as before: this model
    has no boolean/confirmed-shaped field, only the raw metric value and how it moved
    under different suppression/exposure assumptions, which is the instability itself
    that INJ-044 asks a human to be shown."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric: Literal["PRR", "ROR", "EBGM"]
    value: float
    value_range_under_alternate_assumptions: tuple[float, float]
    stability_note: str


class PVPayload(BaseModel):
    """pv_intake's domain_payload extension. No field here can represent a causality,
    seriousness, expectedness, or reportability determination -- ADR-004 layer 1, matching
    pv_duplicate_check.schema.json's and pv_normalize_terminology.schema.json's own
    what_this_schema_cannot_express constraints. `duplicate_suspected` is a triage signal
    only, never a final safety conclusion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    case_id: str
    duplicate_suspected: bool
    comparison_window_version: str
    candidates: tuple[DuplicateCandidate, ...]
    normalization_suggestions: tuple[NormalizationSuggestion, ...]
    terminology_table_version: str
    # --- Stage 21 gap-closures, all informational/evidence-only (never a determination) ---
    awareness_dates: tuple[AwarenessDateRecord, ...] = ()  # INJ-038
    meddra_versions_used: tuple[str, ...] = ()  # INJ-039 -- >1 entry means an unreconciled version mismatch
    listedness_sources: tuple[ListednessSource, ...] = ()  # INJ-040
    sensitive_segment_flags: tuple[str, ...] = ()  # INJ-041, e.g. "pregnancy_exposure", "paediatric"
    reporter_identifiability: Literal["identifiable", "unidentifiable", "not_stated"] | None = None  # INJ-042
    related_quality_record_ids: tuple[str, ...] = ()  # INJ-043 -- cross-reference only, never a causal link
    disproportionality_signal: DisproportionalitySignal | None = None  # INJ-044


class ColdChainExcursion(BaseModel):
    """Stage 21 gap-closure (INJ-051): a cold-chain lane exception, surfaced as evidence
    for a human to judge -- never a disposition on the shipment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    logger_id: str
    exceeded_range: bool
    pallet_association_disputed: bool
    note: str


class ShortageRootCause(BaseModel):
    """Stage 21 gap-closure (INJ-054): informational context on why an option's supply
    is constrained. Never a decision about whether to source elsewhere."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    supplier_type: Literal["sole_source", "multi_source"]
    recovery_estimate_weeks: int | None = None


class CMOCapacityConflict(BaseModel):
    """Stage 21 gap-closure (INJ-055): informational flag that a CMO's promised capacity
    for this option overlaps another sponsor's window. The agent may rank around this;
    it has no field to resolve the conflict itself."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    competing_sponsor_count: int
    window_overlap: bool


class OverlapInformation(BaseModel):
    """Stage 21 gap-closure (INJ-058): shared-component/equipment/route information for
    triage, deliberately never a `recall_scope` -- that field cannot exist anywhere in
    this schema (ADR-004 layer 1/2, see this class's sibling docstring below). This is the
    honest way to surface 'these lots share X but not Y' for a human without the system
    ever determining which lots are affected."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    shared_components: tuple[str, ...] = ()
    shared_equipment: tuple[str, ...] = ()
    shared_distribution_routes: tuple[str, ...] = ()


class ShortageOption(BaseModel):
    """Mirrors supply_generate_options.schema.json's `options[]` shape exactly. No field
    here is `allocated_quantity`, `reserved_for`, `ship_to`, `release_authorization`, or
    `recall_scope` -- that schema's own what_this_schema_cannot_express list states no
    future change may add one without a new ADR, not just a schema PR. The Stage 21
    fields below are all informational triage data for a human, structurally incapable
    of expressing any of those five banned concepts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    option_id: str
    description: str
    constraints_satisfied: tuple[str, ...]
    cold_chain_evidence_ids: tuple[str, ...]
    transport_notes: str
    cold_chain_excursion: ColdChainExcursion | None = None  # INJ-051
    serialization_status: Literal["aggregated", "aggregation_gap", "not_applicable"] | None = None  # INJ-052
    counterfeit_review_flag: Literal["consistent", "inconsistent_print_history", "not_reviewed"] | None = None  # INJ-053
    shortage_root_cause: ShortageRootCause | None = None  # INJ-054
    cmo_capacity_conflict: CMOCapacityConflict | None = None  # INJ-055
    customs_status: Literal["consistent", "description_mismatch", "not_applicable"] | None = None  # INJ-057
    overlap_information: OverlapInformation | None = None  # INJ-058


class ConstraintSet(BaseModel):
    """Mirrors supply_generate_options.schema.json's `constraint_set` object exactly
    (additionalProperties: false there too)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    market_authorization_scope: tuple[str, ...] = ()
    cold_chain_requirements: tuple[str, ...] = ()
    trial_demand_reservations: tuple[str, ...] = ()
    compassionate_use_constraints: tuple[str, ...] = ()
    cmo_capacity_window: str | None = None


class SupplyPayload(BaseModel):
    """supply_planning's domain_payload extension. The Supply-Planning Agent may rank and
    explain within `options`; it cannot widen the constraint-filtered set (agent_roster.md
    SS2) and has no field to write an allocation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    product_id: str
    options: tuple[ShortageOption, ...]
    constraint_set: ConstraintSet
    inventory_snapshot_version: str
    # Stage 21 gap-closure (INJ-056): informational triage signals only -- e.g.
    # "trial_demand_present", "compassionate_use_present", "cross_market_conflict".
    # SUPPLY_ALLOCATION_ETHICS.md (K-029) requires these be VISIBLE, not resolved by
    # this system; there is no field anywhere in this payload that resolves them.
    allocation_ethics_flags: tuple[str, ...] = ()


# =============================================================================
# Stage 21 -- three new governed workflows, closing D02/D03/D07's OUT_OF_SCOPE
# injects by building the same decision-support pattern used by the three
# original workflows: structural completeness/conflict findings only, no
# disposition field representable anywhere (ADR-004 layer 1). Each mirrors
# ReconciliationFinding/BatchPayload's exact shape -- the proven template.
# =============================================================================


class ResearchFinding(BaseModel):
    """research_review's finding shape. No field here is `model_qualified`,
    `intended_use_approved`, or `target_validated` -- a discovery/preclinical model's
    qualification for portfolio use, and whether a target is validated, are conclusions
    that belong to a human Research/Portfolio reviewer, never this system."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: Literal[
        "assay_comparability",
        "compound_identity",
        "cohort_representativeness",
        "image_integrity",
        "model_qualification_evidence",
        "target_evidence_concordance",
    ]
    status: Literal["complete", "gap", "conflict"]
    evidence_ids: tuple[str, ...]
    gap_description: str | None = None


class ResearchPayload(BaseModel):
    """research_review's domain_payload extension (D02: assay drift, compound genealogy
    collision, omics cohort bias, preclinical image manipulation, unqualified research
    model, target-evidence conflict). No field can represent a qualification/validation
    determination -- ADR-004 layer 1, matching research_reconcile.schema.json's own
    what_this_schema_cannot_express list."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    research_id: str
    reconciliation_complete: bool
    findings: tuple[ResearchFinding, ...]


class ClinicalFinding(BaseModel):
    """clinical_integrity's finding shape. No field here is `protocol_deviation_disposition`,
    `unblinding_action`, or `eligibility_final_determination` -- those are clinical/
    medical-monitor decisions, never this system's to make."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: Literal[
        "protocol_version_conformance",
        "eligibility_criteria",
        "randomization_integrity",
        "blinding_integrity",
        "consent_status",
        "device_data_integrity",
        "endpoint_adjudication",
        "site_integrity",
    ]
    status: Literal["complete", "gap", "conflict"]
    evidence_ids: tuple[str, ...]
    gap_description: str | None = None


class ClinicalPayload(BaseModel):
    """clinical_integrity's domain_payload extension (D03: protocol-version divergence,
    eligibility ambiguity, randomization outage, unblinding risk, eConsent mismatch,
    device clock skew, endpoint adjudication backlog, site inspection risk). No field can
    represent a clinical/medical disposition -- ADR-004 layer 1."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    protocol_id: str
    reconciliation_complete: bool
    findings: tuple[ClinicalFinding, ...]


class RegulatoryFinding(BaseModel):
    """regulatory_completeness's finding shape. No field here is
    `variation_classification_final`, `submission_ready`, or `regulatory_determination`
    -- those are Regulatory Affairs decisions, never this system's to make."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: Literal[
        "identity_consistency",
        "labeling_consistency",
        "commitment_tracking",
        "sequence_completeness",
        "variation_classification_evidence",
        "inspection_readiness",
    ]
    status: Literal["complete", "gap", "conflict"]
    evidence_ids: tuple[str, ...]
    gap_description: str | None = None


class RegulatoryPayload(BaseModel):
    """regulatory_completeness's domain_payload extension (D07: IDMP identity conflict,
    labeling divergence, commitment deadline ambiguity, eCTD sequence gap, variation
    classification dispute, inspection request surge). No field can represent a
    regulatory determination -- ADR-004 layer 1."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    submission_id: str
    reconciliation_complete: bool
    findings: tuple[RegulatoryFinding, ...]
