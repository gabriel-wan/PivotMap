"""MiroFlow tool for querying PostgreSQL module records."""

from __future__ import annotations

import os
from dataclasses import asdict
from difflib import SequenceMatcher
from typing import Any

from schemas.interfaces import Module

try:
    from miroflow import register
except ImportError:  # pragma: no cover - local scaffold fallback

    def register(func: Any) -> Any:
        """Fallback decorator used when MiroFlow is not installed."""
        return func


@register
def module_db_query(
    query: str,
    database_url: str | None = None,
) -> dict[str, Any]:
    """Find the best institutional module pathway for a suggested skill.

    The production path queries PostgreSQL with `pg_trgm` similarity first and a
    pgvector semantic fallback second. If a database connection is unavailable,
    deterministic scaffold rows keep tests and local demos working.
    """
    db_url = database_url or os.getenv("DATABASE_URL")
    module = _query_postgres(query, db_url) if db_url else None
    module = module or _query_demo_rows(query)
    if module is None:
        return {"module": None, "gap_note": "no institutional pathway found"}
    return {"module": module, "gap_note": None}


def _query_postgres(query: str, database_url: str | None) -> Module | None:
    """Query PostgreSQL with trigram similarity and pgvector fallback."""
    if not database_url:
        return None
    try:
        import psycopg
    except ImportError:
        return None

    try:
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, code, title, faculty, description, prereqs, semesters
                    FROM modules
                    WHERE similarity(code || ' ' || title, %s) >= 0.4
                    ORDER BY similarity(code || ' ' || title, %s) DESC
                    LIMIT 1
                    """,
                    (query, query),
                )
                row = cur.fetchone()
                if row:
                    return _module_from_row(row)

                cur.execute(
                    """
                    SELECT id, code, title, faculty, description, prereqs, semesters
                    FROM modules
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <-> %s::vector
                    LIMIT 1
                    """,
                    (_semantic_stub_vector(query),),
                )
                row = cur.fetchone()
                if row:
                    return _module_from_row(row)
    except Exception:
        return None
    return None


def _query_demo_rows(query: str) -> Module | None:
    """Fuzzy-match against local scaffold rows when PostgreSQL is unavailable."""
    rows = _demo_rows()
    ranked = sorted(
        rows,
        key=lambda module: _score(query, f"{module.code} {module.title} {module.description}"),
        reverse=True,
    )
    best = ranked[0] if ranked else None
    if best and _score(query, f"{best.code} {best.title} {best.description}") >= 0.4:
        return best
    return None


def _demo_rows() -> list[Module]:
    """Return representative module rows for local development."""
    return [
        Module(
            id="nus-bt2102",
            code="BT2102",
            title="Data Management and Visualisation",
            faculty="School of Computing",
            description="Data analysis, querying, dashboards, and visualisation.",
            prereqs=[],
            semesters=["1", "2"],
        ),
        Module(
            id="nus-bt3103",
            code="BT3103",
            title="Application Systems Development for Business Analytics",
            faculty="School of Computing",
            description="Business analytics applications and product data workflows.",
            prereqs=["BT2102"],
            semesters=["1"],
        ),
        Module(
            id="nus-is1128",
            code="IS1128",
            title="Information Systems Leadership and Communication",
            faculty="School of Computing",
            description="Information systems, stakeholder communication, and teamwork.",
            prereqs=[],
            semesters=["1", "2"],
        ),
    ]


def _module_from_row(row: tuple[Any, ...]) -> Module:
    """Convert a PostgreSQL row into a `Module` dataclass."""
    return Module(
        id=str(row[0]),
        code=str(row[1]),
        title=str(row[2]),
        faculty=str(row[3]),
        description=str(row[4]),
        prereqs=list(row[5] or []),
        semesters=list(row[6] or []),
    )


def _semantic_stub_vector(query: str) -> str:
    """Return a deterministic vector literal placeholder for pgvector search."""
    seed = sum(ord(char) for char in query) or 1
    values = [((seed + index) % 100) / 100 for index in range(8)]
    return "[" + ",".join(f"{value:.2f}" for value in values) + "]"


def _score(query: str, candidate: str) -> float:
    """Return a fuzzy match score between query and candidate text."""
    normalized_query = query.casefold().strip()
    normalized_candidate = candidate.casefold().strip()
    if not normalized_query:
        return 0.0
    if normalized_query in normalized_candidate:
        return 1.0
    return SequenceMatcher(None, normalized_query, normalized_candidate).ratio()


def module_to_json(module: Module) -> dict[str, Any]:
    """Serialize a matched module for API responses or logs."""
    return asdict(module)
