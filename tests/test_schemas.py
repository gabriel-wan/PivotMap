"""Tests for PivotMap schemas."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from schemas.interfaces import JDRequirement, ProofGraph, ProofNode


def test_proof_node_status_values() -> None:
    """Proof nodes should support the required status values."""
    requirement = JDRequirement(
        skill="Translate product data into recommendations",
        importance=0.9,
        category="analytics",
        confidence=0.85,
    )
    graph = ProofGraph(
        user_id="student-test",
        jd_text="Product Analyst",
        version=1,
        created_at=datetime.utcnow(),
        nodes=[ProofNode(requirement=requirement, status="weak")],
        edges=[],
    )

    assert asdict(graph)["nodes"][0]["status"] == "weak"


def test_mock_fixture_is_valid_json_shape() -> None:
    """The demo proof graph fixture should contain required top-level fields."""
    fixture_path = Path(__file__).parent / "fixtures" / "mock_proof_graph.json"
    graph = json.loads(fixture_path.read_text(encoding="utf-8"))

    statuses = [node["status"] for node in graph["nodes"]]
    assert "Grab Singapore" in graph["jd_text"]
    assert statuses.count("matched") >= 3
    assert statuses.count("weak") >= 2
    assert statuses.count("missing") >= 2
