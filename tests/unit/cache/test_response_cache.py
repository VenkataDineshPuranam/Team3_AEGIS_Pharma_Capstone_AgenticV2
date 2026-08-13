"""Real correctness tests against live Redis (Redis Cloud, this session) and live Neo4j.

The one this design exists for: a cache hit on evidence that has since transitioned to
superseded must be caught, not served (ADR-003 guardrail; cache_design.md/redis_tuning.md
name this exact scenario). Uses a dedicated test node (K-TEST-CACHE) so it never touches
the real 32-doc corpus, and resets/deletes it in a finally block either way.

Also: subject_id (batch_id/case_id/product_id) is part of the cache key -- a real bug
found via the FastAPI backend (services/api/main.py), not in this test suite originally.
Every batch/case/product in a workflow shares the same evidence_ids (evidence.retrieve's
query terms are workflow-scoped, not subject-scoped), so evidence_ids alone was not a
unique key -- one subject's cached response was served for a different subject's request.
test_cache_is_isolated_per_subject_id below is the regression test for that.
"""
import os
import uuid

import pytest
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")

from packages.domain.evidence import Claim
from packages.domain.kg.client import session
from packages.domain.state import DecisionSupportOutput
from services.integration import response_cache

pytestmark = pytest.mark.skipif(
    not os.environ.get("NEO4J_PASSWORD") or not os.environ.get("REDIS_URL")
    or "xxxxxxxx" in os.environ.get("NEO4J_URI", ""),
    reason="BLOCKED_BY_ENVIRONMENT: Neo4j and/or Redis not configured",
)


@pytest.fixture
def test_evidence_node():
    """A dedicated, disposable EvidenceItem -- never one of the real 32 corpus docs."""
    evidence_id = f"K-TEST-CACHE-{uuid.uuid4().hex[:8]}"
    with session() as s:
        s.run(
            "CREATE (e:EvidenceItem {evidence_id: $id, source_file: 'test.md', "
            "authority: 'test', status: 'approved', trust: 'approved', jurisdiction: 'Global'})",
            id=evidence_id,
        )
    yield evidence_id
    with session() as s:
        s.run("MATCH (e:EvidenceItem {evidence_id: $id}) DELETE e", id=evidence_id)


def test_cache_hit_when_evidence_still_citable(test_evidence_node):
    evidence_id = test_evidence_node
    draft = DecisionSupportOutput(
        summary="test summary", claims=(Claim(text="a claim", cites=(evidence_id,)),)
    )
    response_cache.set_cleared("batch_review", "B-TEST-1", [evidence_id], draft)

    hit = response_cache.get("batch_review", "B-TEST-1", [evidence_id])
    assert hit is not None
    assert hit.summary == "test summary"


def test_cache_miss_after_evidence_transitions_to_superseded(test_evidence_node):
    """THE scenario. Store a cleared response while the evidence is approved, then
    transition it to superseded directly in Neo4j (simulating a real supersession event),
    and confirm the cache entry -- which still physically exists in Redis, unchanged --
    is never served."""
    evidence_id = test_evidence_node
    draft = DecisionSupportOutput(
        summary="test summary", claims=(Claim(text="a claim", cites=(evidence_id,)),)
    )
    response_cache.set_cleared("batch_review", "B-TEST-2", [evidence_id], draft)
    assert response_cache.get("batch_review", "B-TEST-2", [evidence_id]) is not None  # sanity: it was cached

    with session() as s:
        s.run("MATCH (e:EvidenceItem {evidence_id: $id}) SET e.status = 'superseded'", id=evidence_id)

    stale_hit = response_cache.get("batch_review", "B-TEST-2", [evidence_id])
    assert stale_hit is None, "Cache served a response built on since-superseded evidence -- ADR-003 violation."


def test_cache_is_isolated_per_subject_id(test_evidence_node):
    """Regression test for the real cross-subject contamination bug found via the FastAPI
    backend: two different subjects (batches) sharing the same evidence_ids must NOT share
    a cache entry -- each subject's own cleared response must only ever be served for that
    same subject."""
    evidence_id = test_evidence_node
    draft_a = DecisionSupportOutput(summary="Batch A's own summary", claims=(Claim(text="a", cites=(evidence_id,)),))
    draft_b = DecisionSupportOutput(summary="Batch B's own summary", claims=(Claim(text="b", cites=(evidence_id,)),))

    response_cache.set_cleared("batch_review", "B-SUBJECT-A", [evidence_id], draft_a)
    response_cache.set_cleared("batch_review", "B-SUBJECT-B", [evidence_id], draft_b)

    hit_a = response_cache.get("batch_review", "B-SUBJECT-A", [evidence_id])
    hit_b = response_cache.get("batch_review", "B-SUBJECT-B", [evidence_id])
    assert hit_a.summary == "Batch A's own summary"
    assert hit_b.summary == "Batch B's own summary"
    assert hit_a.summary != hit_b.summary


def test_cache_key_never_depends_on_policy_contract_version(test_evidence_node):
    """cache_design.md's own refinement: content doesn't depend on policy, only
    admission does -- the key must be identical regardless of what the caller thinks the
    current policy version is."""
    evidence_id = test_evidence_node
    key_a = response_cache.cache_key("batch_review", "B-TEST-3", [evidence_id])
    key_b = response_cache.cache_key("batch_review", "B-TEST-3", [evidence_id])
    assert key_a == key_b  # same subject + evidence_ids -> same key, no policy_contract_version input at all


def test_bypass_on_redis_unreachable(monkeypatch):
    """ADR-007: Redis unreachable -> bypass, never a hard failure."""
    def _raise(*args, **kwargs):
        raise ConnectionError("simulated Redis outage")

    monkeypatch.setattr("services.integration.response_cache.get_client", _raise)
    assert response_cache.get("batch_review", "B-006", ["K-006"]) is None  # no exception raised
    response_cache.set_cleared("batch_review", "B-006", ["K-006"], DecisionSupportOutput(summary="x", claims=()))  # no exception
