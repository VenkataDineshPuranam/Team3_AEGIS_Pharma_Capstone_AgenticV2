"""Unit tests for services/integration/precedent_retrieve.py -- no Neo4j required."""
from contextlib import contextmanager
from datetime import date

import pytest
from pydantic import ValidationError

from services.integration.precedent_retrieve import PrecedentRetrieveInput, ToolError, retrieve, _call_tracker


class _FakeNode(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class _FakeSession:
    def __init__(self, records=None, error=None):
        self.records = records or []
        self.error = error
        self.calls = []

    def run(self, query, **kwargs):
        self.calls.append((query, kwargs))
        if self.error is not None:
            raise self.error
        return self.records


def _cm(fake):
    @contextmanager
    def inner():
        yield fake
    return inner


@pytest.fixture(autouse=True)
def _reset_tracker():
    _call_tracker.counts.clear()
    yield
    _call_tracker.counts.clear()


def test_input_model_forbids_disposition_fields():
    with pytest.raises(ValidationError):
        PrecedentRetrieveInput(
            run_id="R-1",
            finding_categories=["genealogy"],
            finding_hash="abc",
            policy_contract_version="v1",
            auto_approved=True,  # type: ignore[call-arg]
        )


def test_empty_categories_returns_empty_without_store():
    fake = _FakeSession(error=RuntimeError("should not query"))
    result = retrieve("R-empty", [], "", "v1", session_cm=_cm(fake))
    assert result["items"] == []
    assert fake.calls == []


def test_category_overlap_returns_citable_item():
    node = _FakeNode(
        {
            "evidence_id": "HP-R-prior",
            "source_file": "human_precedent/R-prior.md",
            "status": "draft",
            "effective_date": date(2026, 8, 1),
            "jurisdiction": "EU",
            "content_excerpt": "Genealogy incomplete.",
        }
    )
    fake = _FakeSession(records=[{"e": node}])
    result = retrieve("R-now", ["genealogy"], "abc", "v1", session_cm=_cm(fake))
    assert result["items"][0]["evidence_id"] == "HP-R-prior"
    assert result["items"][0]["status"] == "draft"
    assert "auto_approved" not in result
    kwargs = fake.calls[0][1]
    assert kwargs["citable_statuses"] == ["approved", "draft"]
    assert "superseded" not in kwargs["citable_statuses"]


def test_store_unavailable_maps_to_schema_error():
    fake = _FakeSession(error=RuntimeError("connection refused"))
    with pytest.raises(ToolError) as exc:
        retrieve("R-down", ["genealogy"], "abc", "v1", session_cm=_cm(fake))
    assert exc.value.code == "STORE_UNAVAILABLE"


def test_second_call_in_same_run_is_rate_limited():
    fake = _FakeSession(records=[])
    retrieve("R-once", ["genealogy"], "abc", "v1", session_cm=_cm(fake))
    with pytest.raises(ToolError) as exc:
        retrieve("R-once", ["genealogy"], "abc", "v1", session_cm=_cm(fake))
    assert exc.value.code == "RATE_LIMITED"
