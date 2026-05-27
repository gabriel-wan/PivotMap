"""API tests for the Career Proof Graph backend."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.main import app
from backend.miro_client import _extract_response_content, _parse_json_content


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


def test_get_graph_demo_mode(monkeypatch) -> None:
    """Graph retrieval should return the new graph payload."""
    monkeypatch.setenv("DEMO_MODE", "true")
    client = TestClient(app)

    response = client.get("/graph/demo-nus-business-y3")

    assert response.status_code == 200
    assert response.json()["user_id"] == "demo-nus-business-y3"
    assert "nodes" not in response.json()


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
