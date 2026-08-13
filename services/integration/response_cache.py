"""Response cache -- Stage 20b Phase 5. Implements eval-ai-cache/cache_design.md (Stage 14)
+ docs/quality/performance/redis_tuning.md (Stage 15):

  - Only a guard-and-Critic-CLEARED DecisionSupportOutput is ever cached -- never a raw
    draft, never a blocked/rejected one (redis_tuning.md SS2: "only validated AI outputs
    enter the cache").
  - Cache key includes the evidence_ids used, NEVER policy_contract_version (content
    doesn't depend on policy, only admission does -- Stage 14's own refinement to Stage 11).
  - Cluster-failure degraded mode: Redis unreachable -> bypass, never a hard failure
    (ADR-007). `get`/`set` below swallow connection errors and return/no-op rather than
    raising into the graph.
  - **The specific correctness scenario this design exists to catch**: a cache hit on
    evidence that has since transitioned to `superseded` must be caught, not served
    (ADR-003 guardrail). `get()` re-validates every cached evidence_id's CURRENT status
    against Neo4j before returning a hit -- a stale cache entry is treated as a miss, not
    silently served.
"""
from __future__ import annotations

import hashlib
import json

from packages.config.redis_client import get_client
from packages.domain.evidence import Claim
from packages.domain.kg.client import Neo4jNotConfigured, session
from packages.domain.state import DecisionSupportOutput

_TTL_SECONDS = 3600  # volatile-lru eviction handles memory pressure; TTL is the fallback (redis_tuning.md SS4)


def cache_key(workflow: str, evidence_ids: list[str]) -> str:
    """Never includes policy_contract_version -- content doesn't depend on policy
    (cache_design.md's refinement to Stage 11's evidence.retrieve key)."""
    digest = hashlib.sha256(",".join(sorted(evidence_ids)).encode()).hexdigest()[:16]
    return f"response_cache:{workflow}:{digest}"


def _evidence_ids_still_citable(evidence_ids: list[str]) -> bool:
    """Re-checks CURRENT status in Neo4j -- the actual ADR-003 guardrail check. A cached
    entry built when K-006 was approved must miss once K-006 (or anything it cites)
    transitions to superseded/untrusted, even though the cache entry itself never changed."""
    if not evidence_ids:
        return False
    try:
        with session() as s:
            result = s.run(
                "MATCH (e:EvidenceItem) WHERE e.evidence_id IN $ids "
                "RETURN e.evidence_id AS id, e.status AS status",
                ids=evidence_ids,
            )
            statuses = {r["id"]: r["status"] for r in result}
    except Neo4jNotConfigured:
        return False
    if set(statuses) != set(evidence_ids):
        return False  # an id disappeared entirely -- treat as stale, not a hit
    return all(status in ("approved", "draft") for status in statuses.values())


_HITS_KEY = "response_cache:_stats:hits"
_MISSES_KEY = "response_cache:_stats:misses"


def get(workflow: str, evidence_ids: list[str]) -> DecisionSupportOutput | None:
    try:
        client = get_client()
        raw = client.get(cache_key(workflow, evidence_ids))
    except Exception:  # noqa: BLE001 -- ADR-007: bypass, never fail the run (covers RedisNotConfigured too)
        return None

    if raw is None or not _evidence_ids_still_citable(evidence_ids):
        # A stale (superseded-evidence) entry counts as a miss, not a hit -- it was never
        # served, which is exactly the metric a "stale-serve count (must be zero)" panel
        # (dashboards.md SS1) needs: this counter and that guarantee are the same event.
        try:
            client.incr(_MISSES_KEY)
        except Exception:  # noqa: BLE001
            pass
        return None

    try:
        client.incr(_HITS_KEY)
    except Exception:  # noqa: BLE001
        pass

    data = json.loads(raw)
    claims = tuple(Claim(text=c["text"], cites=tuple(c["cites"])) for c in data["claims"])
    return DecisionSupportOutput(summary=data["summary"], claims=claims)


def hit_rate_stats() -> dict:
    try:
        client = get_client()
        hits = int(client.get(_HITS_KEY) or 0)
        misses = int(client.get(_MISSES_KEY) or 0)
    except Exception:  # noqa: BLE001 -- ADR-007
        return {"hits": None, "misses": None, "hit_rate": None, "status": "REDIS_UNAVAILABLE"}
    total = hits + misses
    return {"hits": hits, "misses": misses, "hit_rate": (hits / total) if total else None}


def set_cleared(workflow: str, evidence_ids: list[str], draft: DecisionSupportOutput) -> None:
    """Only ever called AFTER guard2 clears -- never on a raw or blocked draft."""
    try:
        client = get_client()
        client.set(cache_key(workflow, evidence_ids), json.dumps(draft.model_dump()), ex=_TTL_SECONDS)
    except Exception:  # noqa: BLE001 -- ADR-007: bypass, never fail the run (covers RedisNotConfigured too)
        return
