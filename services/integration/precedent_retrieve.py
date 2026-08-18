"""precedent.retrieve -- implements packages/contracts/tool_contracts/precedent_retrieve.schema.json.

Called after batch.reconcile, never before. ADR-003 filter lives in the Cypher (status IN
approved|draft). STORE_UNAVAILABLE and empty results are valid: the graph continues without
precedents and never treats either as a disposition.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import date

from pydantic import BaseModel, ConfigDict

from packages.domain.evidence import EvidenceItem
from packages.domain.kg.client import session
from services.integration.evidence_retrieve import register_run_evidence_ids

_PER_RUN_CEILING = 1
_CITABLE_STATUSES = ("approved", "draft")


class ToolError(Exception):
    def __init__(self, code: str, meaning: str):
        self.code = code
        self.meaning = meaning
        super().__init__(f"{code}: {meaning}")


class PrecedentRetrieveInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: str
    finding_categories: list[str]
    finding_hash: str
    policy_contract_version: str


@dataclass
class _RunCallTracker:
    counts: dict[str, int] = field(default_factory=dict)

    def check_and_increment(self, run_id: str) -> None:
        used = self.counts.get(run_id, 0)
        if used >= _PER_RUN_CEILING:
            raise ToolError("RATE_LIMITED", "A second call was attempted for the same run_id.")
        self.counts[run_id] = used + 1


_call_tracker = _RunCallTracker()

_QUERY = """
MATCH (e:EvidenceItem)
WHERE e.authority = 'human_precedent'
  AND e.source_workflow = 'batch_review'
  AND e.status IN $citable_statuses
  AND e.source_run_id <> $run_id
  AND (
    ($finding_hash <> '' AND e.finding_hash = $finding_hash)
    OR any(cat IN $finding_categories WHERE cat IN coalesce(e.finding_categories, []))
  )
RETURN e
"""


def _effective_date(value) -> date:
    if hasattr(value, "to_native"):
        return value.to_native()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def retrieve(
    run_id: str,
    finding_categories: list[str],
    finding_hash: str,
    policy_contract_version: str,
    *,
    session_cm=None,
) -> dict:
    """Matches precedent_retrieve.schema.json's input/output shape exactly."""
    if not run_id or not policy_contract_version:
        raise ToolError("POLICY_VERSION_MISMATCH", "Missing required input fields.")

    PrecedentRetrieveInput(
        run_id=run_id,
        finding_categories=list(finding_categories),
        finding_hash=finding_hash or "",
        policy_contract_version=policy_contract_version,
    )
    _call_tracker.check_and_increment(run_id)

    start = time.monotonic()
    if not finding_categories and not finding_hash:
        return {
            "items": [],
            "tool_accounting": {"latency_ms": int((time.monotonic() - start) * 1000)},
        }

    cm = session_cm or session
    try:
        with cm() as s:
            records = list(
                s.run(
                    _QUERY,
                    run_id=run_id,
                    finding_hash=finding_hash or "",
                    finding_categories=list(finding_categories),
                    citable_statuses=list(_CITABLE_STATUSES),
                )
            )
    except Exception as exc:  # noqa: BLE001 -- connection/driver errors map to STORE_UNAVAILABLE
        raise ToolError("STORE_UNAVAILABLE", str(exc)) from exc

    latency_ms = int((time.monotonic() - start) * 1000)
    items = []
    for record in records:
        node = record["e"]
        items.append(
            EvidenceItem(
                evidence_id=node["evidence_id"],
                source=node["source_file"],
                status=node["status"],
                effective_date=_effective_date(node["effective_date"]),
                jurisdiction=node.get("jurisdiction"),
                supersedes=None,
                content_excerpt=node.get("content_excerpt") or "",
            )
        )

    register_run_evidence_ids(run_id, [item.evidence_id for item in items])
    return {
        "items": [item.model_dump(mode="json") for item in items],
        "tool_accounting": {"latency_ms": latency_ms},
    }
