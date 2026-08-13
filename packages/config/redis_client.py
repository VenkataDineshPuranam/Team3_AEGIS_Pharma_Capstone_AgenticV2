"""Redis client -- Stage 20b Phase 5. Native `redis` client, never MCP
(redis_tuning.md SS0's explicit rule -- MCP is not the production cache transport).
REDIS_URL from .env (Redis Cloud this session); one interface so a future swap to Azure
Cache for Redis (ADR-009's deployment target) is a config change, not a code change --
same pattern as packages/config/llm_client.py's provider swap.
"""
from __future__ import annotations

import os

import redis


class RedisNotConfigured(RuntimeError):
    pass


def get_client() -> redis.Redis:
    url = os.environ.get("REDIS_URL", "")
    if not url:
        raise RedisNotConfigured("REDIS_URL not set in .env.")
    return redis.from_url(url, decode_responses=True, socket_connect_timeout=3, socket_timeout=3)
