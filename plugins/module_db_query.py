"""MiroFlow tool for retrieving module evidence nodes."""

from __future__ import annotations

import os
from dataclasses import asdict
from difflib import SequenceMatcher
from typing import Any

from schemas.interfaces import EvidenceNode

try:
    from miroflow import register
except ImportError:  # pragma: no cover - local scaffold fallback

    def register(func: Any) -> Any:
        """Fallback decorator used when MiroFlow is not installed."""
        return func


@register
def module_db_query(query: str, database_url: str | None = None) -> dict[str, Any]:
    """Find the best module evidence node for a suggested module name or code."""
    node = _query_postgres(query, database_url or os.getenv("DATABASE_URL")) or _query_demo_rows(query)
    if node is None:
        return {"evidence_node": None, "gap_note": "no institutional pathway found"}
    return {"evidence_node": asdict(node), "gap_note": None}


def _query_postgres(query: str, database_url: str | None) -> EvidenceNode | None:
    """Query PostgreSQL evidence nodes with pg_trgm similarity."""
    if not database_url:
        return None
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        return None

    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT id, user_id, kind, title, description, source_ids, created_at, metadata
                    FROM evidence_nodes
                    WHERE kind = 'module'
                      AND similarity(title || ' ' || description, :query) >= 0.4
                    ORDER BY similarity(title || ' ' || description, :query) DESC
                    LIMIT 1
                    """
                ),
                {"query": query},
            ).mappings().first()
        if row:
            return EvidenceNode(
                id=row["id"],
                user_id=row["user_id"],
                kind=row["kind"],
                title=row["title"],
                description=row["description"],
                source_ids=list(row["source_ids"] or []),
                created_at=row["created_at"],
                metadata=dict(row["metadata"] or {}),
            )
    except Exception:
        return None
    return None


def _query_demo_rows(query: str) -> EvidenceNode | None:
    """Fuzzy-match local module evidence when PostgreSQL is unavailable."""
    rows = _demo_rows()
    ranked = sorted(rows, key=lambda row: _score(query, f"{row.title} {row.description}"), reverse=True)
    best = ranked[0] if ranked else None
    if best and _score(query, f"{best.title} {best.description}") >= 0.4:
        return best
    return None


def _demo_rows() -> list[EvidenceNode]:
    """Return representative module evidence rows."""
    return [
        EvidenceNode(
            id="module-nus-bt2102",
            user_id="system",
            kind="module",
            title="BT2102 Data Management and Visualisation",
            description="Data analysis, querying, dashboards, and visualisation.",
            source_ids=["source-nusmods-bt2102"],
            metadata={"institution": "NUS"},
        ),
        EvidenceNode(
            id="module-nus-bt3103",
            user_id="system",
            kind="module",
            title="BT3103 Application Systems Development for Business Analytics",
            description="Business analytics applications and product data workflows.",
            source_ids=["source-nusmods-bt3103"],
            metadata={"institution": "NUS"},
        ),
    ]


def _score(query: str, candidate: str) -> float:
    """Return a fuzzy match score between query and candidate text."""
    normalized_query = query.casefold().strip()
    normalized_candidate = candidate.casefold().strip()
    if not normalized_query:
        return 0.0
    if normalized_query in normalized_candidate:
        return 1.0
    return SequenceMatcher(None, normalized_query, normalized_candidate).ratio()
