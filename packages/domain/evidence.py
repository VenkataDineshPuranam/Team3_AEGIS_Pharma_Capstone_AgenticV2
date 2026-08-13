"""Evidence value objects -- Stage 20a Phase 1.

Executes langgraph_design.md SS3's `evidence` field and evidence_retrieve.schema.json's
output shape. Every item that reaches GovernedState.evidence has already passed the
untrusted/superseded filter server-side (ADR-003) -- this type only accepts the two
citable statuses, so a non-citable item cannot round-trip through this model even if a
caller tried to construct one directly.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

# Only "approved" and "draft" are citable (ADR-003). "untrusted" and "superseded" are
# filtered server-side in evidence_retrieve and never appear here -- there is no field
# value that could represent them, matching the schema's own enum.
CitableStatus = Literal["approved", "draft"]


class EvidenceItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    evidence_id: str
    source: str
    status: CitableStatus
    effective_date: date
    jurisdiction: str | None = None
    supersedes: str | None = None
    content_excerpt: str = ""


class Claim(BaseModel):
    """A single cited assertion inside a DecisionSupportOutput. Mirrors the shape the
    Stage 14 evidence_authority_grader.py already validates against (`cites` must resolve
    to evidence_ids present in the run's own retrieved set)."""

    model_config = ConfigDict(frozen=True)

    text: str
    cites: tuple[str, ...] = ()
