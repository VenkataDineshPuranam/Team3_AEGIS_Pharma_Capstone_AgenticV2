"""pv.duplicate_check -- implements
packages/contracts/tool_contracts/pv_duplicate_check.schema.json exactly, over the
synthetic PV case fixtures (tests/fixtures/synthetic/pv_cases/*.json). Stage 20b's
minimal real-data substitute for V1's cross-repo PV case data (NAB-3), same pattern as
batch_reconcile.py.

DDD domain_model.md SS7: this must complete before SignalTriaged (i.e. before synthesize)
-- enforced as a graph edge (services/api/pv_graph.py), not by this tool refusing
out-of-order calls, since the tool has no way to observe graph state (the schema's own
description says so explicitly).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from services.integration.evidence_retrieve import get_run_evidence_ids

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "synthetic" / "pv_cases"


class ToolError(Exception):
    def __init__(self, code: str, meaning: str):
        self.code = code
        self.meaning = meaning
        super().__init__(f"{code}: {meaning}")


def _load_fixture(case_id: str) -> dict:
    path = FIXTURES_DIR / f"{case_id}.json"
    if not path.exists():
        raise ToolError("COMPARISON_STORE_UNAVAILABLE", f"No fixture for case_id {case_id!r}.")
    return json.loads(path.read_text())


def duplicate_check(run_id: str, case_id: str, case_summary_evidence_ids: list[str]) -> dict:
    """Matches pv_duplicate_check.schema.json's input/output shape exactly."""
    if not run_id or not case_id or not case_summary_evidence_ids:
        raise ToolError("COMPARISON_STORE_UNAVAILABLE", "Missing required input fields.")

    retrieved = get_run_evidence_ids(run_id)
    unknown = [eid for eid in case_summary_evidence_ids if eid not in retrieved]
    if unknown:
        raise ToolError(
            "COMPARISON_STORE_UNAVAILABLE",
            f"evidence_ids {unknown} were not returned by this run's own retrieval call.",
        )

    start = time.monotonic()
    fixture = _load_fixture(case_id)
    latency_ms = int((time.monotonic() - start) * 1000)

    return {
        "duplicate_suspected": fixture["duplicate_suspected"],
        "comparison_window_version": fixture["comparison_window_version"],
        "candidates": fixture["candidates"],
        "tool_accounting": {"latency_ms": latency_ms},
        # Stage 21 gap-closure fields (INJ-038/039/040/041/042/043/044) -- all optional,
        # sourced straight from the fixture with safe empty/None defaults so PV-001/PV-002
        # (which predate these fields) are unaffected.
        "awareness_dates": fixture.get("awareness_dates", []),
        "meddra_versions_used": fixture.get("meddra_versions_used", []),
        "listedness_sources": fixture.get("listedness_sources", []),
        "sensitive_segment_flags": fixture.get("sensitive_segment_flags", []),
        "reporter_identifiability": fixture.get("reporter_identifiability"),
        "related_quality_record_ids": fixture.get("related_quality_record_ids", []),
        "disproportionality_signal": fixture.get("disproportionality_signal"),
    }
