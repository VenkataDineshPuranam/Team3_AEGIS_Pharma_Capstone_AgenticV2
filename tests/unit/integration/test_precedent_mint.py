"""Unit tests for services/integration/precedent_mint.py -- no Neo4j required."""
from contextlib import contextmanager

from packages.domain.payloads import ReconciliationFinding
from services.integration.precedent_mint import (
    evidence_id_for,
    finding_categories,
    finding_hash,
    mint_rejection,
)


def _finding(category: str, status: str) -> ReconciliationFinding:
    return ReconciliationFinding(category=category, status=status, evidence_ids=("K-006",))


class _FakeSession:
    def __init__(self):
        self.runs: list[tuple[str, dict]] = []

    def run(self, query, **kwargs):
        self.runs.append((query, kwargs))
        return []


def test_finding_hash_ignores_complete_and_is_order_independent():
    a = [_finding("genealogy", "gap"), _finding("lab_results", "complete"), _finding("capa", "conflict")]
    b = [_finding("capa", "conflict"), _finding("genealogy", "gap")]
    assert finding_hash(a) == finding_hash(b)
    assert finding_hash(a)
    assert finding_categories(a) == ["capa", "genealogy"]


def test_finding_hash_empty_when_all_complete():
    findings = [_finding("genealogy", "complete")]
    assert finding_hash(findings) == ""
    assert finding_categories(findings) == []


def test_mint_skips_approve_timeout_and_empty_findings():
    fake = _FakeSession()

    @contextmanager
    def cm():
        yield fake

    assert mint_rejection(action="approved", workflow="batch_review", run_id="R-1", findings=[_finding("genealogy", "gap")], session_cm=cm) is None
    assert mint_rejection(action="timed_out", workflow="batch_review", run_id="R-1", findings=[_finding("genealogy", "gap")], session_cm=cm) is None
    assert mint_rejection(action="rejected", workflow="pv_intake", run_id="R-1", findings=[_finding("genealogy", "gap")], session_cm=cm) is None
    assert mint_rejection(action="rejected", workflow="batch_review", run_id="R-1", findings=[_finding("genealogy", "complete")], session_cm=cm) is None
    assert fake.runs == []


def test_mint_merge_is_idempotent_same_evidence_id():
    fake = _FakeSession()

    @contextmanager
    def cm():
        yield fake

    findings = [_finding("genealogy", "gap")]
    first = mint_rejection(action="rejected", workflow="batch_review", run_id="R-gap", findings=findings, justification="Genealogy incomplete.", session_cm=cm)
    second = mint_rejection(action="rejected", workflow="batch_review", run_id="R-gap", findings=findings, justification="Genealogy incomplete.", session_cm=cm)
    assert first == second == evidence_id_for("R-gap")
    assert len(fake.runs) == 2
    assert fake.runs[0][1]["evidence_id"] == fake.runs[1][1]["evidence_id"] == "HP-R-gap"
    assert fake.runs[0][1]["authority"] == "human_precedent"
    assert fake.runs[0][1]["status"] == "draft"
    assert "Alice" not in str(fake.runs[0][1])
    assert fake.runs[0][1]["jurisdiction"] == "EU"


def test_mint_neo4j_failure_does_not_raise():
    class Boom:
        def run(self, *args, **kwargs):
            raise RuntimeError("neo4j down")

    @contextmanager
    def cm():
        yield Boom()

    assert mint_rejection(action="rejected", workflow="batch_review", run_id="R-x", findings=[_finding("genealogy", "gap")], session_cm=cm) is None
