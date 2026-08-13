"""pv.normalize_terminology -- implements
packages/contracts/tool_contracts/pv_normalize_terminology.schema.json exactly, over the
synthetic PV case fixtures. `applied` is always False -- the schema fixes this value (not
merely a default) so a caller cannot construct a response claiming the suggestion was
applied. This implementation returns a Python dict literal with applied=False for the same
reason, not a variable that could drift.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "synthetic" / "pv_cases"


class ToolError(Exception):
    def __init__(self, code: str, meaning: str):
        self.code = code
        self.meaning = meaning
        super().__init__(f"{code}: {meaning}")


def _find_fixture_by_source_text(source_text: str) -> dict | None:
    for path in FIXTURES_DIR.glob("*.json"):
        data = json.loads(path.read_text())
        if data.get("source_text") == source_text:
            return data
    return None


def normalize_terminology(run_id: str, source_text: str, source_language: str | None = None) -> dict:
    """Matches pv_normalize_terminology.schema.json's input/output shape exactly. Pure
    function of (source_text, terminology_table_version) per the schema's own idempotency
    guarantee -- looked up from the fixture matching this exact text."""
    if not run_id or not source_text:
        raise ToolError("UNSUPPORTED_LANGUAGE", "Missing required input fields.")

    start = time.monotonic()
    fixture = _find_fixture_by_source_text(source_text)
    latency_ms = int((time.monotonic() - start) * 1000)

    if fixture is None:
        # Schema's own declared behavior: unsupported/unmatched text returns empty
        # suggestions, letting the agent flag for human normalization -- never guessed.
        return {
            "suggestions": [],
            "terminology_table_version": "meddra-27.0",
            "applied": False,
            "tool_accounting": {"latency_ms": latency_ms},
        }

    return {
        "suggestions": fixture["normalization_suggestions"],
        "terminology_table_version": fixture["terminology_table_version"],
        "applied": False,
        "tool_accounting": {"latency_ms": latency_ms},
    }
