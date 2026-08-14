"""Stage 21 gap-closure -- INJ-083: vendor exit deadline with incomplete export formats.
See evidence/quality-gates/vendor_exit_export_check.py.
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "evidence" / "quality-gates"))

from vendor_exit_export_check import run_all_checks  # noqa: E402

pytestmark = pytest.mark.skipif(
    not os.environ.get("NEO4J_PASSWORD") or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
    reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured (audit store check needs it initialized)",
)


def test_every_governed_record_type_has_a_working_export_path():
    results = run_all_checks()
    for key in ("audit_store", "evidence_corpus", "tool_contracts", "governance_policy"):
        assert results[key]["exportable"] is True


def test_gaps_are_stated_explicitly_not_hidden():
    """The honest half of this check -- what is NOT yet portable is named, not omitted."""
    results = run_all_checks()
    assert len(results["not_yet_covered"]) > 0
    assert any("LangSmith" in item for item in results["not_yet_covered"])
