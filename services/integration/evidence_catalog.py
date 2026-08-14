"""Read-only evidence catalog -- Stage 21, backing the Evidence Explorer.

WHY THIS IS NOT services/integration/evidence_retrieve.py, and must never become it:

`evidence_retrieve` is a governed tool. Its Cypher filters untrusted/superseded items out
inside the query, so there is no code path by which a non-citable item reaches a run
(ADR-003, BC-2). That property is load-bearing and unchanged by this module.

This module answers a different question, for a human rather than for a graph: "what does
the corpus contain, and what may I rely on?" Answering it honestly REQUIRES returning the
untrusted and superseded items -- a page that silently omits them cannot show an
investigator that a document they remember is now superseded, which is exactly the
question an evidence explorer exists to answer.

The two are kept apart by construction, not by discipline:
  - Nothing in this module is called from any graph, any node, or any tool. Its only
    caller is the read-only HTTP endpoint.
  - It returns `EvidenceCatalogItem`, NOT `packages.domain.evidence.EvidenceItem`. That
    domain type structurally cannot hold a non-citable status (its `CitableStatus` Literal
    permits only approved/draft), so a catalog row cannot be passed off as retrieved
    evidence anywhere downstream -- construction would raise.
  - `citable` is computed from the same rule evidence_retrieve enforces, imported from
    there rather than restated, so the two cannot drift into disagreeing about what is
    usable.
"""
from __future__ import annotations

from typing import Any

from packages.domain.kg.client import Neo4jNotConfigured, session
from services.integration.evidence_retrieve import _CITABLE_STATUSES


class CatalogUnavailable(RuntimeError):
    """Neo4j unreachable or unconfigured. Surfaced to the caller as an explicit
    unavailable state -- the Explorer says the knowledge graph is unreachable, rather
    than rendering an empty corpus that looks like "no evidence exists"."""


# `superseded_by` is read from the graph's own `supersedes` edge, never inferred from a
# status string: an item can be marked superseded without the newer document having been
# ingested yet, and those are different facts. OPTIONAL MATCH keeps the first case
# reporting superseded_by = null rather than dropping the row.
_LIST_QUERY = """
MATCH (e:EvidenceItem)
OPTIONAL MATCH (newer:EvidenceItem)-[:supersedes]->(e)
OPTIONAL MATCH (e)-[:supersedes]->(older:EvidenceItem)
RETURN e AS e,
       newer.evidence_id AS superseded_by,
       older.evidence_id AS supersedes
ORDER BY e.evidence_id
"""


def _to_item(record: Any) -> dict:
    node = record["e"]
    effective = node.get("effective_date")
    return {
        "evidence_id": node.get("evidence_id"),
        "source": node.get("source_file") or "",
        "status": node.get("status") or "unknown",
        # The single rule, imported from the governed tool rather than restated here.
        # NOTE this correctly reports `local_approved` as NOT citable: evidence_retrieve's
        # citable set is exactly ("approved", "draft"), and its own docstring records that
        # the local_approved distinction is not yet exercised. Reporting it as citable here
        # would make this page disagree with what retrieval actually does.
        "citable": node.get("status") in _CITABLE_STATUSES,
        "authority": node.get("authority"),
        "jurisdiction": node.get("jurisdiction"),
        "effective_date": effective.isoformat() if hasattr(effective, "isoformat") else effective,
        "supersedes": record["supersedes"],
        "superseded_by": record["superseded_by"],
        # Provenance: the ingestion-time SHA-256 of the source document
        # (kg_schema.md SS3's _provenance block). Shown so a reviewer can verify the
        # document they are looking at is the one that was ingested.
        "content_hash": node.get("content_hash"),
        "provenance": {
            "source_dataset": node.get("_provenance_source_dataset"),
            "ingested_at": node.get("_provenance_ingested_at"),
            "ingestion_run_id": node.get("_provenance_ingestion_run_id"),
        },
        "content_excerpt": "",  # not ingested into the KG -- see list_catalog's docstring
    }


def list_catalog() -> list[dict]:
    """Every EvidenceItem node, citable or not.

    `content_excerpt` is always empty here, and that is a fact about the corpus rather
    than an omission by this function: packages/domain/kg/ingest.py stores the catalog
    row's metadata and content HASH, never the document body. There is no excerpt to
    return, so none is invented -- the UI states that document text is not held in the
    knowledge graph rather than showing a blank field that reads as missing data.
    """
    try:
        with session() as s:
            return [_to_item(r) for r in s.run(_LIST_QUERY)]
    except Neo4jNotConfigured as exc:
        raise CatalogUnavailable(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 -- driver/connection errors all mean "cannot read"
        raise CatalogUnavailable(str(exc)) from exc


def get_many(evidence_ids: list[str]) -> dict[str, dict]:
    """Catalog rows for specific ids, keyed by id -- what a run's detail page uses to show
    the authority/status behind the evidence_ids its audit record holds. Missing ids are
    simply absent from the result; the caller reports them as unresolved rather than
    substituting a placeholder row."""
    if not evidence_ids:
        return {}
    try:
        with session() as s:
            records = s.run(
                """
                MATCH (e:EvidenceItem) WHERE e.evidence_id IN $ids
                OPTIONAL MATCH (newer:EvidenceItem)-[:supersedes]->(e)
                OPTIONAL MATCH (e)-[:supersedes]->(older:EvidenceItem)
                RETURN e AS e, newer.evidence_id AS superseded_by, older.evidence_id AS supersedes
                """,
                ids=evidence_ids,
            )
            return {item["evidence_id"]: item for item in (_to_item(r) for r in records)}
    except Neo4jNotConfigured as exc:
        raise CatalogUnavailable(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise CatalogUnavailable(str(exc)) from exc


def catalog_stats() -> dict:
    """Counts by status -- the Explorer's summary strip and the System Health page's
    knowledge-graph section. Measured, never asserted."""
    try:
        with session() as s:
            rows = list(s.run("MATCH (e:EvidenceItem) RETURN e.status AS status, count(*) AS n"))
            edges = s.run("MATCH ()-[r:supersedes]->() RETURN count(r) AS n").single()["n"]
    except Neo4jNotConfigured as exc:
        raise CatalogUnavailable(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise CatalogUnavailable(str(exc)) from exc

    by_status = {r["status"]: r["n"] for r in rows}
    return {
        "by_status": by_status,
        "total": sum(by_status.values()),
        "citable_total": sum(n for s, n in by_status.items() if s in _CITABLE_STATUSES),
        "supersedes_edges": edges,
    }
