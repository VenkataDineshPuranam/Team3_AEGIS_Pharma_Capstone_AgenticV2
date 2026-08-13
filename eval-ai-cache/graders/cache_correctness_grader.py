"""Cache-correctness grader -- the failure mode unique to caching in a
regulated domain: a cache hit must never serve an answer built on
since-superseded evidence.

Rule sources: ADR-003 guardrail (register row D5/I1,
docs/quality/dmaic-lean/waste_register_downtime.md), tool_inventory.md SS6
(cache key must be hash(query, evidence_snapshot_version) -- NOT just
hash(query)), and conflict_authority_rules.md SS3 (supersession is
normalized once at ingestion, never re-derived from prose).

No cache exists in 20a (interim state excludes it entirely, ADR-003
guardrail + interim_state.md). This grader is written now so it is ready,
unchanged, for Stage 15's cache implementation -- exactly the same
"grader exists before the thing it grades" pattern as the rest of this
stage.
"""


def grade_cache_key_includes_snapshot(cache_key_fields):
    """A cache key built only from the query text, without the evidence
    snapshot version, cannot distinguish a hit taken before a supersession
    from one taken after."""
    if "evidence_snapshot_version" not in cache_key_fields:
        return {"pass": False, "reason": "cache_key_missing_snapshot_version -- cannot detect staleness on hit"}
    return {"pass": True, "reason": "cache_key_includes_snapshot_version"}


def grade_no_stale_serve(cached_snapshot_version, current_snapshot_version, evidence_id, evidence_status_at_current_snapshot):
    """The actual correctness property: if the document a cached response
    was built on has since transitioned to superseded/untrusted, the cache
    entry must be invalidated, not served."""
    if cached_snapshot_version == current_snapshot_version:
        return {"pass": True, "reason": "snapshot_unchanged_serve_ok"}
    if evidence_status_at_current_snapshot in {"untrusted", "superseded"}:
        return {"pass": False, "reason": f"stale_serve: cached response built on snapshot {cached_snapshot_version}, but {evidence_id} is now {evidence_status_at_current_snapshot} as of {current_snapshot_version} -- must invalidate, not serve"}
    return {"pass": True, "reason": "snapshot_changed_but_evidence_still_citable"}


def grade_no_cache_list_enforced(tool, attempted_cache_write):
    """tool_inventory.md SS6: pv.duplicate_check and supply.generate_options
    are do-not-cache-by-default. This must be enforced in code (exit
    criterion), not just documented -- i.e. a cache-write attempt for
    either tool is itself a defect to catch, not a policy to hope is
    followed."""
    do_not_cache = {"pv.duplicate_check", "supply.generate_options"}
    if tool in do_not_cache and attempted_cache_write:
        return {"pass": False, "reason": f"do_not_cache_list_violated: {tool} is on the do-not-cache list but a cache write was attempted"}
    return {"pass": True, "reason": "do_not_cache_list_respected"}
