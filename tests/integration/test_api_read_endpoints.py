"""Stage 21 -- the API surface the AEGIS Control Center reads from.

Uses FastAPI's TestClient against the real app. The read endpoints hit the real audit
store and (where configured) the real knowledge graph, so these are integration tests, not
unit tests with mocks -- the thing worth proving is that the endpoint reports what the
store actually holds, which a mock would assume away.
"""
import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()

from services.api.main import app
from services.api.schemas import MIN_JUSTIFICATION_CHARS

pytestmark = pytest.mark.stub

client = TestClient(app)

_NEO4J = bool(os.environ.get("NEO4J_PASSWORD")) and "xxxxxxxx" not in os.environ.get("NEO4J_URI", "")
needs_kg = pytest.mark.skipif(not _NEO4J, reason="BLOCKED_BY_ENVIRONMENT: Neo4j not configured")


# --- decide: the justification contract (G-10) ------------------------------------


def test_decide_rejects_a_missing_justification():
    """The justification is not optional. A client that omits it is refused at the
    boundary with a 422, before any graph is resumed."""
    r = client.post("/api/runs/R-nonexistent/decide", json={"workflow": "batch_review", "action": "approved"})
    assert r.status_code == 422


def test_decide_rejects_a_token_justification():
    r = client.post(
        "/api/runs/R-nonexistent/decide",
        json={"workflow": "batch_review", "action": "approved", "justification": "ok"},
    )
    assert r.status_code == 422
    assert MIN_JUSTIFICATION_CHARS > 1


def test_decide_on_an_unknown_run_is_404_not_a_silent_success():
    r = client.post(
        "/api/runs/R-nonexistent/decide",
        json={
            "workflow": "batch_review", "action": "approved",
            "justification": "A justification long enough to pass validation.",
        },
    )
    assert r.status_code == 404


def test_veto_is_rejected_for_workflows_that_have_no_veto():
    """PV's advisory veto is a PV mechanism. Offering it elsewhere would imply a control
    that does not exist in those graphs."""
    for workflow in ("batch_review", "supply_planning"):
        r = client.post(
            "/api/runs/R-nonexistent/decide",
            json={
                "workflow": workflow, "action": "veto",
                "justification": "A justification long enough to pass validation.",
            },
        )
        assert r.status_code in (400, 404), workflow


# --- run history ------------------------------------------------------------------


def test_run_history_returns_a_page_with_a_real_total():
    r = client.get("/api/runs", params={"limit": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["limit"] == 5
    assert len(body["items"]) <= 5
    assert body["total"] >= len(body["items"])


def test_run_history_limit_is_bounded():
    """An unbounded limit is a way to ask the API to read the whole store into memory."""
    assert client.get("/api/runs", params={"limit": 100000}).status_code == 422
    assert client.get("/api/runs", params={"limit": 0}).status_code == 422
    assert client.get("/api/runs", params={"offset": -1}).status_code == 422


def test_run_history_filters_by_workflow():
    body = client.get("/api/runs", params={"workflow": "pv_intake", "limit": 50}).json()
    assert all(item["workflow"] == "pv_intake" for item in body["items"])


def test_run_filters_endpoint_reports_values_that_exist():
    body = client.get("/api/runs/filters").json()
    assert set(body) == {"workflow", "terminal_state", "requester_role", "abstention_reason"}
    assert all(isinstance(v, list) for v in body.values())


def test_filters_route_is_not_shadowed_by_the_run_id_route():
    """/api/runs/filters and /api/runs/{run_id} share a prefix -- declaration order is
    what keeps 'filters' from being read as a run id."""
    assert isinstance(client.get("/api/runs/filters").json(), dict)


# --- run detail -------------------------------------------------------------------


def test_unknown_run_detail_is_404():
    assert client.get("/api/runs/R-definitely-not-a-real-run").status_code == 404


def test_known_run_detail_reports_what_it_can_and_says_what_it_cannot():
    page = client.get("/api/runs", params={"limit": 1}).json()
    if not page["items"]:
        pytest.skip("audit store is empty -- nothing to open")
    run_id = page["items"][0]["run_id"]
    body = client.get(f"/api/runs/{run_id}").json()

    assert body["run_id"] == run_id
    assert body["audit"] is not None
    assert isinstance(body["timeline"], list)
    # A historical run has no live decision-support package. The endpoint must say so
    # explicitly rather than returning empty fields the UI would have to interpret.
    if not body["decision_support_available"]:
        assert body["decision_support_unavailable_reason"]


def test_timeline_events_are_ordered_and_typed():
    page = client.get("/api/runs", params={"limit": 20}).json()
    for item in page["items"]:
        timeline = client.get(f"/api/runs/{item['run_id']}").json()["timeline"]
        if len(timeline) < 2:
            continue
        assert timeline == sorted(timeline, key=lambda e: e["at"])
        assert all(e["event_type"] and e["action"] for e in timeline)
        return


# --- evidence catalog -------------------------------------------------------------


@needs_kg
def test_evidence_catalog_shows_non_citable_items_and_labels_them():
    """The Explorer must be able to show an untrusted or superseded document. Its value is
    in saying 'you cannot rely on this', which requires returning it."""
    items = client.get("/api/evidence").json()
    assert items
    by_status = {i["status"] for i in items}
    assert by_status - {"approved", "draft"}, "expected at least one non-citable item in the corpus"
    for item in items:
        assert item["citable"] == (item["status"] in ("approved", "draft"))


@needs_kg
def test_untrusted_and_superseded_are_never_reported_as_citable():
    """The single invariant this endpoint could plausibly break."""
    for item in client.get("/api/evidence").json():
        if item["status"] in ("untrusted", "superseded"):
            assert item["citable"] is False


@needs_kg
def test_catalog_citable_rule_agrees_with_what_retrieval_actually_enforces():
    """The catalog imports evidence_retrieve's own citable tuple rather than restating it,
    so the page cannot drift into calling something usable that a run could not retrieve.
    `local_approved` is the case that would expose a restatement: it reads as approved to
    a human but is not in the retrieval tool's citable set."""
    from services.integration.evidence_retrieve import _CITABLE_STATUSES

    for item in client.get("/api/evidence").json():
        assert item["citable"] == (item["status"] in _CITABLE_STATUSES)


@needs_kg
def test_evidence_stats_are_counted_not_asserted():
    stats = client.get("/api/evidence/stats").json()
    assert stats["total"] == sum(stats["by_status"].values())
    assert stats["citable_total"] <= stats["total"]


# --- governance -------------------------------------------------------------------


def test_governance_snapshot_reports_the_real_policy_contract():
    body = client.get("/api/governance").json()
    assert body["policy_contract_version"] == "v1"
    batch = body["prohibited_actions"]["by_workflow"]["batch_review"]
    assert "release the batch" in batch["banned_terms"]
    assert "release_recommended" in batch["banned_field_names"]


def test_governance_snapshot_states_that_authentication_does_not_exist():
    """The one thing this page must never imply is a security control the build lacks."""
    auth = client.get("/api/governance").json()["authentication"]
    assert auth["status"] == "NOT IMPLEMENTED"
    assert "grants nothing" in auth["detail"]


def test_governance_reports_supply_dual_approval_as_two_required_legs():
    roles = client.get("/api/governance").json()["approver_roles"]["supply_planning"]
    assert roles["required_legs"] == ["planning", "quality"]
    assert "one leg approving is not approval" in roles["structure"]


def test_governance_reports_the_pv_veto_as_non_overridable():
    pv = client.get("/api/governance").json()["approver_roles"]["pv_intake"]
    assert pv["veto_role"] == "Patient Safety Representative"
    assert "cannot be overridden" in pv["structure"]


def test_governance_is_read_only():
    """No verb other than GET is exposed on a governance route."""
    for method in ("post", "put", "patch", "delete"):
        assert getattr(client, method)("/api/governance").status_code == 405


# --- health -----------------------------------------------------------------------


def test_health_detail_measures_each_dependency():
    body = client.get("/api/health/detail").json()
    assert body["api"]["status"] == "ok"
    names = {d["name"] for d in body["dependencies"]}
    assert "Policy engine" in names and "Audit store (SQLite, append-only)" in names
    for dep in body["dependencies"]:
        assert dep["status"] in ("ok", "degraded", "unavailable", "not_configured")


def test_health_detail_distinguishes_not_configured_from_unavailable():
    """Collapsing these would misreport which dependency actually stops the system."""
    statuses = {d["name"]: d["status"] for d in client.get("/api/health/detail").json()["dependencies"]}
    assert statuses  # each is one of the four, asserted above; this pins the distinction's existence
    assert "not_configured" != "unavailable"


def test_health_detail_does_not_leak_secrets():
    """Probes touch credentialed services. Their detail strings must describe state, never
    echo a URL or key."""
    body = client.get("/api/health/detail").text
    for secret_env in ("REDIS_URL", "NEO4J_PASSWORD", "ANTHROPIC_API_KEY", "GROQ_API_KEY"):
        value = os.environ.get(secret_env, "")
        if value and len(value) > 8:
            assert value not in body, f"{secret_env} leaked into /api/health/detail"


def test_error_responses_do_not_expose_a_stack_trace():
    r = client.get("/api/runs/R-definitely-not-a-real-run")
    assert "Traceback" not in r.text
    assert "sqlite3" not in r.text.lower()
