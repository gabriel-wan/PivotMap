"""API tests for the Career Proof Graph backend."""

from __future__ import annotations

import asyncio
from collections.abc import Generator
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.db import get_session
from backend.main import app
from backend.miro_client import MiroMindClient, _extract_response_content, _parse_json_content
from backend.models import Base
from backend.repository import store_graph


def test_health() -> None:
    """Health endpoint should return ok."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_capture_voice_demo_mode(monkeypatch) -> None:
    """Voice capture should return demo graph in demo mode."""
    monkeypatch.setenv("DEMO_MODE", "true")
    client = TestClient(app)

    response = client.post(
        "/capture/voice",
        json={"user_id": "demo-nus-business-y3", "transcript": "I analysed product funnels."},
    )

    assert response.status_code == 200
    assert response.json()["evidence_nodes"]


def test_capture_resume_demo_mode(monkeypatch) -> None:
    """Resume capture should return demo graph in demo mode."""
    monkeypatch.setenv("DEMO_MODE", "true")
    client = TestClient(app)

    response = client.post(
        "/capture/resume",
        json={"user_id": "demo-nus-business-y3", "resume_text": "Product analytics internship."},
    )

    assert response.status_code == 200
    assert response.json()["claim_nodes"]


def test_target_jd_demo_mode(monkeypatch) -> None:
    """JD targeting should return gap nodes in demo mode."""
    monkeypatch.setenv("DEMO_MODE", "true")
    client = TestClient(app)

    response = client.post(
        "/target/jd",
        json={"user_id": "demo-nus-business-y3", "jd_text": "Grab Product Analyst"},
    )

    assert response.status_code == 200
    statuses = {node["status"] for node in response.json()["gap_nodes"]}
    assert {"matched", "weak", "missing"}.issubset(statuses)


def test_target_jd_normal_mode_maps_against_stored_graph(monkeypatch) -> None:
    """JD targeting should reuse persisted proof graph nodes in normal fallback mode."""
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.delenv("MIROMIND_API_KEY", raising=False)
    session_factory = _sqlite_session_factory()
    seed_session = session_factory()
    store_graph(seed_session, _stored_proof_graph())
    seed_session.close()

    def override_session() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_session
    try:
        client = TestClient(app)
        response = client.post(
            "/target/jd",
            json={
                "user_id": "user-test",
                "jd_text": "We need SQL dashboard analytics plus user research.",
                "company": "Acme Product Analyst",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    graph = response.json()
    assert any(node["id"] == "evidence-dashboard" for node in graph["evidence_nodes"])
    assert any(
        gap["status"] == "matched" and gap["linked_evidence_ids"] == ["evidence-dashboard"]
        for gap in graph["gap_nodes"]
    )
    assert any(
        gap["requirement"] == "research"
        and gap["status"] == "missing"
        and gap["linked_evidence_ids"] == []
        for gap in graph["gap_nodes"]
    )


def test_get_graph_demo_mode(monkeypatch) -> None:
    """Graph retrieval should return the new graph payload."""
    monkeypatch.setenv("DEMO_MODE", "true")
    client = TestClient(app)

    response = client.get("/graph/demo-nus-business-y3")

    assert response.status_code == 200
    assert response.json()["user_id"] == "demo-nus-business-y3"
    assert "nodes" not in response.json()


def test_local_target_jd_fallback_links_existing_evidence(monkeypatch) -> None:
    """No-key JD fallback should map requirements against existing graph context."""
    monkeypatch.delenv("MIROMIND_API_KEY", raising=False)

    graph = asyncio.run(
        MiroMindClient().generate_graph(
            "target_jd",
            {
                "user_id": "user-test",
                "jd_text": "SQL dashboard work and research skills required.",
                "company": "Acme Product Analyst",
                "existing_graph": _stored_proof_graph(),
            },
        )
    )

    assert graph["evidence_nodes"][0]["id"] == "evidence-dashboard"
    assert any(
        gap["status"] == "matched" and gap["linked_evidence_ids"] == ["evidence-dashboard"]
        for gap in graph["gap_nodes"]
    )
    assert any(
        gap["requirement"] == "research"
        and gap["status"] == "missing"
        and gap["linked_evidence_ids"] == []
        for gap in graph["gap_nodes"]
    )


def test_validation_error_for_missing_required_fields(monkeypatch) -> None:
    """Missing required request fields should produce validation errors."""
    monkeypatch.setenv("DEMO_MODE", "true")
    client = TestClient(app)

    response = client.post("/target/jd", json={"user_id": "demo-nus-business-y3"})

    assert response.status_code == 422


def test_miromind_sse_content_parser() -> None:
    """MiroMind SSE-style strings should parse into assistant content."""
    response = "\n".join(
        [
            'data: {"choices":[{"delta":{"role":"assistant"}}]}',
            'data: {"choices":[{"delta":{"content":"{\\"user_id\\": \\"u1\\", "}}]}',
            'data: {"choices":[{"delta":{"content":"\\"sources\\": []}"}}]}',
            "data: [DONE]",
        ]
    )

    content = _extract_response_content(response)
    graph = _parse_json_content(content)

    assert graph == {"user_id": "u1", "sources": []}


def test_miromind_wrapped_json_parser() -> None:
    """Model prose or fenced responses should still yield the first JSON object."""
    content = 'Here is the graph:\n```json\n{"user_id": "u2", "gap_nodes": []}\n```'

    graph = _parse_json_content(content)

    assert graph == {"user_id": "u2", "gap_nodes": []}


def _sqlite_session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def _stored_proof_graph() -> dict:
    now = datetime.now(UTC).isoformat()
    return {
        "user_id": "user-test",
        "sources": [
            {
                "id": "source-portfolio",
                "source_url": "https://example.com/dashboard",
                "source_type": "portfolio",
                "title": "Analytics dashboard case study",
                "published_at": None,
                "retrieved_at": now,
                "metadata": {},
            }
        ],
        "evidence_nodes": [
            {
                "id": "evidence-dashboard",
                "user_id": "user-test",
                "kind": "project",
                "title": "SQL analytics dashboard",
                "description": "Built a SQL dashboard for product funnel analytics.",
                "source_ids": ["source-portfolio"],
                "created_at": now,
                "metadata": {},
            }
        ],
        "claim_nodes": [
            {
                "id": "claim-dashboard",
                "evidence_id": "evidence-dashboard",
                "claim_text": "Built a SQL dashboard for product analytics.",
                "confidence_status": "supported",
                "confidence_score": 0.9,
                "source_ids": ["source-portfolio"],
                "created_at": now,
            }
        ],
        "skill_nodes": [
            {
                "id": "skill-sql",
                "user_id": "user-test",
                "skill": "SQL analytics dashboard",
                "category": "analytics",
                "confidence_score": 0.9,
                "evidence_ids": ["evidence-dashboard"],
                "claim_ids": ["claim-dashboard"],
                "created_at": now,
            }
        ],
        "gap_nodes": [],
        "trace_events": [],
    }
