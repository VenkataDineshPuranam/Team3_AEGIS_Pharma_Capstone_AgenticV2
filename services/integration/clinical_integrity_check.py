"""clinical.integrity_check -- implements
packages/contracts/tool_contracts/clinical_integrity_check.schema.json exactly, over the
synthetic clinical fixtures (tests/fixtures/synthetic/clinical/*.json). Stage 21's
minimal real-data substitute, same pattern as services/integration/batch_reconcile.py.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from services.integration.evidence_retrieve import get_run_evidence_ids

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "synthetic" / "clinical"


class ToolError(Exception):
    def __init__(self, code: str, meaning: str):
        self.code = code
        self.meaning = meaning
        super().__init__(f"{code}: {meaning}")


def _load_fixture(protocol_id: str) -> dict:
    path = FIXTURES_DIR / f"{protocol_id}.json"
    if not path.exists():
        raise ToolError("EVIDENCE_ID_NOT_IN_RUN", f"No fixture for protocol_id {protocol_id!r}.")
    return json.loads(path.read_text())


def integrity_check(run_id: str, protocol_id: str, evidence_ids: list[str], policy_contract_version: str) -> dict:
    """Matches clinical_integrity_check.schema.json's input/output shape exactly."""
    if not run_id or not protocol_id or not evidence_ids or not policy_contract_version:
        raise ToolError("POLICY_VERSION_MISMATCH", "Missing required input fields.")

    retrieved = get_run_evidence_ids(run_id)
    unknown = [eid for eid in evidence_ids if eid not in retrieved]
    if unknown:
        raise ToolError(
            "EVIDENCE_ID_NOT_IN_RUN",
            f"evidence_ids {unknown} were not returned by this run's own retrieval call.",
        )

    start = time.monotonic()
    fixture = _load_fixture(protocol_id)
    findings = fixture["findings"]

    for finding in findings:
        cited = set(finding["evidence_ids"])
        if not cited.issubset(set(evidence_ids)):
            raise ToolError(
                "EVIDENCE_ID_NOT_IN_RUN",
                f"Finding for category {finding['category']!r} cites evidence outside this call's evidence_ids.",
            )

    reconciliation_complete = all(f["status"] == "complete" for f in findings)
    latency_ms = int((time.monotonic() - start) * 1000)

    return {
        "reconciliation_complete": reconciliation_complete,
        "findings": findings,
        "tool_accounting": {"latency_ms": latency_ms},
    }
