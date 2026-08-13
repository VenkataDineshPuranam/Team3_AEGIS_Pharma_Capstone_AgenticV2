"""Per-workflow domain payloads -- Stage 20a Phase 1.

Executes langgraph_design.md SS3's "what this schema deliberately cannot express" table
(ADR-004 layer 1). `extra="forbid"` on every model here is load-bearing, not decoration:
a caller cannot smuggle `release_recommended`, `causality`, `allocated_quantity`, or any
other disposition field through even if a node tried, because pydantic raises on
construction rather than silently dropping the extra key.
"""
from __future__ import annotations

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


class NormalizationSuggestion(BaseModel):
    """Mirrors pv_normalize_terminology.schema.json's `suggestions[]` shape. Always a
    suggestion, never applied -- `applied` is fixed False at the schema layer there; this
    model has no field that could represent 'applied: true' either."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    normalized_term: str
    confidence: float
    terminology_source: str


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


class ShortageOption(BaseModel):
    """Mirrors supply_generate_options.schema.json's `options[]` shape exactly. No field
    here is `allocated_quantity`, `reserved_for`, `ship_to`, `release_authorization`, or
    `recall_scope` -- that schema's own what_this_schema_cannot_express list states no
    future change may add one without a new ADR, not just a schema PR."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    option_id: str
    description: str
    constraints_satisfied: tuple[str, ...]
    cold_chain_evidence_ids: tuple[str, ...]
    transport_notes: str


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
