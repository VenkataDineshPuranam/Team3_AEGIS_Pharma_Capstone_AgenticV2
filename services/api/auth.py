"""FastAPI auth boundary -- resolves a bearer token to a live user_store.Session, or
raises. This is the ONE place request handlers ask "who is this," replacing the old
pattern where `claimed_identity` was an unverified string the client supplied and the API
never checked (see the removed docstring in schemas.DecideRequest for what that used to
say).

Kept intentionally thin: this module does not decide whether an action is PERMITTED
(that's user_store.approver_string_for, called from main.py's decide_run) -- it only
establishes identity, matching the existing "the API is a boundary, not a control" rule
main.py's own module docstring states.
"""
from __future__ import annotations

from fastapi import Header, HTTPException

from services.integration import user_store


def require_user(authorization: str | None = Header(default=None)) -> user_store.Session:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or malformed Authorization header.")
    token = authorization.removeprefix("Bearer ").strip()
    conn = user_store.get_connection()
    try:
        session = user_store.resolve_session(conn, token)
    finally:
        conn.close()
    if session is None:
        raise HTTPException(401, "Session is invalid or has expired. Please log in again.")
    return session
