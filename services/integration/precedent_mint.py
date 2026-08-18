"""Mint a human-precedent EvidenceItem after a batch_review HITL rejection (ADR-010).

Not a tool. Not called from synthesize. Best-effort after `write_human_override`: a Neo4j
failure logs and returns None; it must not undo the human decision.

Approvals and timeouts never mint. Person names never land on the node.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, date, datetime
from typing import Iterable

from packages.domain.kg.client import session
from packages.domain.payloads import ReconciliationFinding

logger = logging.getLogger(__name__)

_GAP_STATUSES = frozenset({"gap", "conflict"})
JUSTIFICATION_MAX = 500
_SOURCE_WORKFLOW = "batch_review"


def _as_finding(item: ReconciliationFinding | dict) -> tuple[str, str]:
    if isinstance(item, ReconciliationFinding):
        return item.category, item.status
    return item["category"], item["status"]


def open_findings(findings: Iterable[ReconciliationFinding | dict]) -> list[tuple[str, str]]:
    """gap/conflict (category, status) pairs only. complete and batch_id are excluded."""
    pairs = [_as_finding(f) for f in findings]
    return sorted((category, status) for category, status in pairs if status in _GAP_STATUSES)


def finding_categories(findings: Iterable[ReconciliationFinding | dict]) -> list[str]:
    return sorted({category for category, _status in open_findings(findings)})


def finding_hash(findings: Iterable[ReconciliationFinding | dict]) -> str:
    pairs = open_findings(findings)
    if not pairs:
        return ""
    payload = json.dumps(pairs, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def evidence_id_for(source_run_id: str) -> str:
    return f"HP-{source_run_id}"


def _excerpt(justification: str) -> str:
    text = (justification or "").strip()
    return text[:JUSTIFICATION_MAX]


_MERGE = """
MERGE (e:EvidenceItem {evidence_id: $evidence_id})
SET e.source_file = $source_file,
    e.authority = $authority,
    e.effective_date = date($effective),
    e.status = $status,
    e.trust = $trust,
    e.jurisdiction = $jurisdiction,
    e.content_hash = $content_hash,
    e.finding_hash = $finding_hash,
    e.finding_categories = $finding_categories,
    e.source_run_id = $source_run_id,
    e.source_workflow = $source_workflow,
    e.action = $action,
    e.content_excerpt = $content_excerpt,
    e._provenance_source_dataset = $prov_source_dataset,
    e._provenance_ingested_at = $prov_ingested_at,
    e._provenance_ingestion_run_id = $prov_ingestion_run_id,
    e._provenance_source_row_hash = $prov_source_row_hash
"""


def mint_rejection(
    *,
    action: str,
    workflow: str,
    run_id: str,
    findings: Iterable[ReconciliationFinding | dict] = (),
    justification: str = "",
    session_cm=None,
) -> str | None:
    """MERGE `HP-{run_id}` when a EU QP rejects a batch_review pack with open findings.

    Returns the evidence_id on success, None when skipped or when Neo4j fails.
    """
    if action != "rejected" or workflow != _SOURCE_WORKFLOW or not run_id:
        return None
    categories = finding_categories(findings)
    digest = finding_hash(findings)
    if not categories or not digest:
        return None

    excerpt = _excerpt(justification)
    eid = evidence_id_for(run_id)
    content_hash = hashlib.sha256(f"{digest}:{excerpt}".encode("utf-8")).hexdigest()
    cm = session_cm or session
    try:
        with cm() as s:
            s.run(
                _MERGE,
                evidence_id=eid,
                source_file=f"human_precedent/{run_id}.md",
                authority="human_precedent",
                effective=date.today().isoformat(),
                status="draft",
                trust="draft",
                jurisdiction="EU",
                content_hash=content_hash,
                finding_hash=digest,
                finding_categories=categories,
                source_run_id=run_id,
                source_workflow=_SOURCE_WORKFLOW,
                action="rejected",
                content_excerpt=excerpt,
                prov_source_dataset="human_override",
                prov_ingested_at=datetime.now(UTC).isoformat(),
                prov_ingestion_run_id=run_id,
                prov_source_row_hash=digest,
            )
    except Exception:  # noqa: BLE001 -- mint must not undo the human decision
        logger.exception("precedent mint failed for run_id=%s; HITL decision stands", run_id)
        return None
    return eid
