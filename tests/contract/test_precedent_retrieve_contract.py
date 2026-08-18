"""Contract checks for precedent.retrieve -- schema shape, not a live store."""
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "packages" / "contracts" / "tool_contracts" / "precedent_retrieve.schema.json"


def test_schema_is_read_only_batch_review_and_forbids_extras():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema["read_only"] is True
    assert schema["owning_context"] == "Batch Review"
    assert schema["input"]["additionalProperties"] is False
    assert schema["output"]["additionalProperties"] is False
    banned = " ".join(schema["what_this_schema_cannot_express"]).lower()
    assert "disposition" in banned
    assert "auto_approved" in banned
    assert "cross-workflow" in banned


def test_sample_output_matches_schema():
    schema = json.loads(SCHEMA_PATH.read_text())
    sample = {
        "items": [
            {
                "evidence_id": "HP-R-prior",
                "source": "human_precedent/R-prior.md",
                "status": "draft",
                "effective_date": "2026-08-01",
                "jurisdiction": "EU",
                "supersedes": None,
                "content_excerpt": "Genealogy incomplete.",
            }
        ],
        "tool_accounting": {"latency_ms": 3},
    }
    validate(instance=sample, schema=schema["output"])


def test_output_cannot_carry_disposition_fields():
    schema = json.loads(SCHEMA_PATH.read_text())
    sample = {
        "items": [],
        "tool_accounting": {"latency_ms": 0},
        "reject_recommended": True,
    }
    with pytest.raises(ValidationError):
        validate(instance=sample, schema=schema["output"])
