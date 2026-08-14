"""Stage 22 -- login functionality. Verifies user_store's credential check, session
lifecycle, and the role-to-approver-string authorization map that main.decide_run now
enforces before a request reaches any graph."""
import time

import pytest

from services.integration import user_store


@pytest.fixture()
def conn(tmp_path):
    db_path = tmp_path / "users.sqlite3"
    c = user_store.get_connection(db_path)
    user_store.create_user(c, "u1", "Test User", "EU Qualified Person", "correct-horse")
    yield c
    c.close()


def test_login_with_correct_password_succeeds(conn):
    session = user_store.login(conn, "u1", "correct-horse")
    assert session.user_id == "u1"
    assert session.role == "EU Qualified Person"


def test_login_with_wrong_password_is_rejected(conn):
    with pytest.raises(user_store.InvalidCredentials):
        user_store.login(conn, "u1", "wrong-password")


def test_login_with_unknown_user_id_gives_the_same_error_as_wrong_password(conn):
    # Deliberately indistinguishable -- see user_store.login's own comment.
    with pytest.raises(user_store.InvalidCredentials, match="Invalid user_id or password."):
        user_store.login(conn, "nonexistent", "anything")


def test_password_is_never_stored_in_plaintext(conn):
    row = conn.execute("SELECT password_hash FROM app_user WHERE user_id = 'u1'").fetchone()
    assert "correct-horse" not in row[0]


def test_a_resolved_session_matches_the_logged_in_user(conn):
    session = user_store.login(conn, "u1", "correct-horse")
    resolved = user_store.resolve_session(conn, session.token)
    assert resolved is not None
    assert resolved.user_id == "u1"


def test_an_unknown_token_resolves_to_none(conn):
    assert user_store.resolve_session(conn, "not-a-real-token") is None


def test_logout_invalidates_the_session(conn):
    session = user_store.login(conn, "u1", "correct-horse")
    user_store.logout(conn, session.token)
    assert user_store.resolve_session(conn, session.token) is None


def test_an_expired_session_resolves_to_none_and_is_deleted(conn, monkeypatch):
    session = user_store.login(conn, "u1", "correct-horse")
    # Force expiry by rewriting the row's expires_at into the past.
    conn.execute(
        "UPDATE app_session SET expires_at = '2000-01-01T00:00:00+00:00' WHERE token = ?",
        (session.token,),
    )
    conn.commit()
    assert user_store.resolve_session(conn, session.token) is None
    row = conn.execute("SELECT * FROM app_session WHERE token = ?", (session.token,)).fetchone()
    assert row is None  # deleted, not just treated as invalid -- no stale row lingers


@pytest.mark.parametrize(
    "role,workflow,leg,expected",
    [
        ("EU Qualified Person", "batch_review", None, "EU Qualified Person"),
        ("EU Qualified Person", "supply_planning", "quality", "EU Qualified Person"),
        ("EU Qualified Person", "supply_planning", "planning", None),  # QP cannot approve the planning leg
        ("Safety physician", "pv_intake", None, "Global Head of Pharmacovigilance"),
        ("Supply governance", "supply_planning", "planning", "Supply Chain VP"),
        ("Head of Preclinical Research", "research_review", None, "Head of Preclinical Research"),
        ("Clinical Trial Medical Monitor", "clinical_integrity", None, "Clinical Trial Medical Monitor"),
        ("Head of Regulatory Affairs", "regulatory_completeness", None, "Head of Regulatory Affairs"),
        ("Auditor", "batch_review", None, None),  # read-only role, no decide permission anywhere
        ("Quality reviewer", "batch_review", None, None),
        ("Unblinding authority", "clinical_integrity", None, None),  # reviews, never decides
    ],
)
def test_approver_string_for_matches_the_role_boundary_table(role, workflow, leg, expected):
    assert user_store.approver_string_for(role, workflow, leg) == expected


def test_only_safety_physician_may_register_a_pv_veto():
    assert user_store.can_veto("Safety physician", "pv_intake") is True
    assert user_store.can_veto("Auditor", "pv_intake") is False
    assert user_store.can_veto("Safety physician", "batch_review") is False


def test_unblinding_authority_is_excluded_from_supply_planning_visibility():
    visible = user_store.visible_workflows("Unblinding authority")
    assert visible is not None
    assert "supply_planning" not in visible
    assert "clinical_integrity" in visible


def test_every_other_role_has_no_visibility_restriction():
    assert user_store.visible_workflows("Auditor") is None
    assert user_store.visible_workflows("EU Qualified Person") is None
