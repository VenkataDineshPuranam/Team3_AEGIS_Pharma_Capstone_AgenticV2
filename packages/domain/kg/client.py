"""Neo4j connection -- backs the Stage 13 semantic layer (docs/architecture/ontology/
kg_schema.md). One driver, read from env at call time (not import time) so tests can run
without a live database until they actually need one.

This module holds no query logic -- see kg/ingest.py (writes) and
services/integration/evidence_retrieve.py (the only reader, per ADR-003/BC-2: filtering
happens inside the tool, never as a caller-side post-filter).
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from neo4j import Driver, GraphDatabase


class Neo4jNotConfigured(RuntimeError):
    """Raised when NEO4J_URI/NEO4J_PASSWORD are unset -- distinct from a connection
    failure, so callers (and tests) can tell 'not set up yet' from 'set up but down'."""


def get_driver() -> Driver:
    uri = os.environ.get("NEO4J_URI", "")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "")
    if not uri or not password or "xxxxxxxx" in uri:
        raise Neo4jNotConfigured(
            "NEO4J_URI / NEO4J_PASSWORD not set in .env -- see .env.example for AuraDB setup."
        )
    return GraphDatabase.driver(uri, auth=(user, password))


@contextmanager
def session() -> Iterator["neo4j.Session"]:  # noqa: F821
    driver = get_driver()
    try:
        with driver.session() as s:
            yield s
    finally:
        driver.close()
