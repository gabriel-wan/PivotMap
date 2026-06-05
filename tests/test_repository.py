"""Tests for Career Proof Graph persistence helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from backend.models import Base, EvidenceNodeModel, SourceModel
from backend.repository import store_graph


def test_store_graph_reuses_sources_by_url() -> None:
    """Repeated fallback/demo sources should not violate source_url uniqueness."""
    session = _session()
    first_graph = _graph(source_id="source-first", evidence_id="evidence-first")
    second_graph = _graph(source_id="source-second", evidence_id="evidence-second")

    store_graph(session, first_graph)
    store_graph(session, second_graph)

    source_count = session.scalar(select(func.count()).select_from(SourceModel))
    second_evidence = session.get(EvidenceNodeModel, "evidence-second")

    assert source_count == 1
    assert second_evidence is not None
    assert second_evidence.source_ids == ["source-first"]
    assert second_graph["sources"][0]["id"] == "source-first"
    assert second_graph["evidence_nodes"][0]["source_ids"] == ["source-first"]


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _graph(source_id: str, evidence_id: str) -> dict:
    now = datetime.now(UTC).isoformat()
    return {
        "user_id": "user-test",
        "sources": [
            {
                "id": source_id,
                "source_url": "https://pivotmap.local/demo",
                "source_type": "voice",
                "title": "Captured career evidence",
                "published_at": now,
                "retrieved_at": now,
                "metadata": {"task": "capture_voice"},
            }
        ],
        "evidence_nodes": [
            {
                "id": evidence_id,
                "user_id": "user-test",
                "kind": "voice",
                "title": "Captured career evidence",
                "description": "I built a dashboard.",
                "source_ids": [source_id],
                "created_at": now,
                "metadata": {},
            }
        ],
        "claim_nodes": [],
        "skill_nodes": [],
        "gap_nodes": [],
        "trace_events": [],
    }
