"""Ingests knowledge/knowledge_catalog.csv into Neo4j as `EvidenceItem` nodes plus
`supersedes` edges -- Stage 20a's scope of docs/architecture/ontology/kg_schema.md SS1-2
(EvidenceItem node type; `supersedes` edge type). Batch-review-only node types
(Batch, Deviation, ...) are seeded separately from synthetic fixtures (Phase 2.5) --
this script owns only the real, SHA-256-verified evidence corpus.

Idempotent: uses MERGE, safe to re-run. Run directly: `python -m packages.domain.kg.ingest`
"""
from __future__ import annotations

import csv
import logging
from datetime import UTC, datetime
from pathlib import Path

from packages.domain.kg.client import session

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = REPO_ROOT / "knowledge" / "knowledge_catalog.csv"

# kg_schema.md SS2: supersedes is populated ONLY from this column, normalized from
# filename to evidence_id at ingestion -- never re-derived from a document's own prose.
_MERGE_EVIDENCE_ITEM = """
MERGE (e:EvidenceItem {evidence_id: $evidence_id})
SET e.source_file = $file,
    e.authority = $authority,
    e.effective_date = CASE WHEN $effective IS NULL THEN null ELSE date($effective) END,
    e.status = $status,
    e.trust = $trust,
    e.jurisdiction = $jurisdiction,
    e.content_hash = $sha256,
    e._provenance_source_dataset = $prov_source_dataset,
    e._provenance_ingested_at = $prov_ingested_at,
    e._provenance_ingestion_run_id = $prov_ingestion_run_id,
    e._provenance_source_row_hash = $prov_source_row_hash
"""
# Neo4j property values must be primitives or arrays thereof -- kg_schema.md SS3's
# `_provenance` block is a documented logical grouping, stored here as four scalar
# properties with a shared `_provenance_` prefix rather than a nested map.

_MERGE_SUPERSEDES_EDGE = """
MATCH (newer:EvidenceItem {evidence_id: $newer_id})
MATCH (older:EvidenceItem {evidence_id: $older_id})
MERGE (newer)-[:supersedes]->(older)
"""


def _filename_to_evidence_id(rows: list[dict], filename: str) -> str | None:
    for row in rows:
        if row["file"] == filename:
            return row["doc_id"]
    return None


def run_ingestion() -> dict[str, int]:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"Catalog not found: {CATALOG_PATH}")

    with CATALOG_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    ingestion_run_id = f"ingest-{datetime.now(UTC).isoformat()}"
    nodes_written = 0
    edges_written = 0

    with session() as s:
        for row in rows:
            s.run(
                _MERGE_EVIDENCE_ITEM,
                evidence_id=row["doc_id"],
                file=row["file"],
                authority=row["authority"],
                effective=None if row["effective"] == "unknown" else row["effective"],
                status=row["status"],
                trust=row["trust"],
                jurisdiction=row["jurisdiction"] or None,
                sha256=row["sha256"],
                prov_source_dataset="knowledge_catalog.csv",
                prov_ingested_at=datetime.now(UTC).isoformat(),
                prov_ingestion_run_id=ingestion_run_id,
                prov_source_row_hash=row["sha256"],
            )
            nodes_written += 1

        for row in rows:
            if not row["supersedes"]:
                continue
            older_id = _filename_to_evidence_id(rows, row["supersedes"])
            if older_id is None:
                logger.warning(
                    "supersedes column on %s references unknown file %s -- skipping edge",
                    row["doc_id"],
                    row["supersedes"],
                )
                continue
            s.run(_MERGE_SUPERSEDES_EDGE, newer_id=row["doc_id"], older_id=older_id)
            edges_written += 1

    return {"nodes": nodes_written, "supersedes_edges": edges_written}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_ingestion()
    print(f"Ingested {result['nodes']} EvidenceItem nodes, {result['supersedes_edges']} supersedes edges.")
