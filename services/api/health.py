"""Dependency health for degraded-mode banners (ADR-007)."""
from __future__ import annotations

from typing import Any


def collect() -> dict[str, Any]:
    return {
        "status": "ok",
        "workflows": ["batch_review", "pv_intake", "supply_planning"],
        "dependencies": {
            "llm": _llm(),
            "policy_engine": _policy(),
            "redis": _redis(),
            "neo4j": _neo4j(),
            "checkpointer": {"ok": True, "detail": "in-process MemorySaver"},
            "langsmith": {"ok": True, "detail": "hosted tracing optional; audit store is source of truth"},
        },
    }


def _llm() -> dict[str, Any]:
    try:
        from packages.config.llm_client import get_llm

        get_llm()
        return {"ok": True, "detail": "client constructed"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "detail": str(exc), "mode": "degraded_mode"}


def _policy() -> dict[str, Any]:
    try:
        from services.integration.policy_engine import load_policy_contract

        load_policy_contract("v1")
        return {"ok": True, "detail": "policy_contract.v1 loaded"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "detail": str(exc), "mode": "fail_closed"}


def _redis() -> dict[str, Any]:
    try:
        from packages.config.redis_client import get_client

        client = get_client()
        client.ping()
        return {"ok": True, "detail": "ping ok"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "detail": str(exc), "mode": "no_cache"}


def _neo4j() -> dict[str, Any]:
    try:
        from packages.domain.kg.client import session

        with session() as s:
            s.run("RETURN 1 AS n").single()
        return {"ok": True, "detail": "connected"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "detail": str(exc), "mode": "abstain_on_retrieve"}
