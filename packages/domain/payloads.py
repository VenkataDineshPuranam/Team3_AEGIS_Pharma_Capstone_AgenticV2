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
