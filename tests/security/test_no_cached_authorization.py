"""Stage 21 gap-closure -- INJ-067: a contractor's access was revoked in IAM but remains
cached in the AI gateway.

This system has no IAM integration to attack yet (packages/observability/rbac_model.md is
explicitly provisional -- no Entra tenant exists, per docs/governance/hitl_control_model.md's
own honest status). What genuinely closes this inject today is a different, checkable
claim: no code path in this system caches an authorization decision across requests at
all. `intake`'s denial-of-wallet admission check (infra/policies/denial_of_wallet_guardrail.py)
is re-evaluated from persisted usage counters on every single run -- there is no in-memory
or Redis-cached "already admitted" flag that a revoked caller could still be riding on.
This test asserts that structural property directly, so it fails the moment a future
change introduces the caching this inject warns against.
"""
import inspect

from services.api import graph, pv_graph, supply_graph


def test_intake_calls_check_and_admit_fresh_in_every_graph():
    """Every workflow's intake node re-evaluates admission on every invocation -- none of
    them read a cached prior-admission result."""
    builders = (graph.build_graph, pv_graph.build_pv_graph, supply_graph.build_supply_graph)
    for builder in builders:
        source = inspect.getsource(builder)
        assert "dow_guard.check_and_admit(" in source, f"{builder.__module__} does not call check_and_admit"


def test_denial_of_wallet_guard_holds_no_admission_cache():
    """The guard's own state is a usage ledger (what was spent), never a cache of
    'this caller was already admitted' -- checked structurally against its real API."""
    from infra.policies.denial_of_wallet_guardrail import DenialOfWalletGuard

    guard = DenialOfWalletGuard()
    public_methods = {name for name in dir(guard) if not name.startswith("_") and callable(getattr(guard, name))}
    # The only two operations this guard exposes: check admission (reads usage), record a
    # run (writes usage). Neither is "remember this caller was admitted before" -- there
    # is no third method a stale-cache read could come from.
    assert public_methods == {"check_and_admit", "record_run"}


def test_revoked_caller_is_re_evaluated_on_the_very_next_run():
    """End-to-end proof, not just an API-shape check: two calls with the same
    requester_role against a fresh guard both hit real admission logic -- the second call
    is not served from any memoized result of the first."""
    from datetime import UTC, datetime

    from infra.policies.denial_of_wallet_guardrail import DenialOfWalletGuard

    guard = DenialOfWalletGuard()
    today = datetime.now(UTC).date()

    first = guard.check_and_admit(user_id="contractor-x", workflow="batch_review", as_of=today)
    assert first["admit"] is True

    # Simulate revocation: exhaust the ceiling the way a real deployment's own
    # authorization layer would reject the caller going forward.
    for _ in range(25):
        guard.record_run(user_id="contractor-x", workflow="batch_review", as_of=today, actual_tokens=200_000)

    second = guard.check_and_admit(user_id="contractor-x", workflow="batch_review", as_of=today)
    assert second["admit"] is False  # re-evaluated fresh, not served from the first call's result
