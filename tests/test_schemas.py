"""Tests for Career Proof Graph schema contracts."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from schemas.interfaces import ClaimNode, EvidenceNode, GapNode, Source


def test_career_graph_dataclasses_are_json_ready() -> None:
    """Core graph dataclasses should serialize to expected primitive fields."""
    source = Source(
        id="source-test",
        source_url="https://example.com",
        source_type="portfolio",
        title="Portfolio",
        published_at=None,
        retrieved_at=datetime.now(UTC),
    )
    evidence = EvidenceNode(
        id="evidence-test",
        user_id="user-test",
        kind="project",
        title="Dashboard project",
        description="Built a dashboard.",
        source_ids=[source.id],
    )
    claim = ClaimNode(
        id="claim-test",
        evidence_id=evidence.id,
        claim_text="Built a dashboard.",
        confidence_status="user-attested",
        confidence_score=0.7,
        source_ids=[source.id],
    )
    gap = GapNode(
        id="gap-test",
        user_id="user-test",
        target_role="Product Analyst",
        requirement="Dashboard storytelling",
        status="weak",
        recommended_action="Add a public case study.",
        linked_evidence_ids=[evidence.id],
    )

    assert asdict(claim)["evidence_id"] == evidence.id
    assert asdict(gap)["status"] == "weak"


def test_demo_fixture_uses_new_model() -> None:
    """The demo fixture should contain only Career Proof Graph collections."""
    fixture_path = Path(__file__).parent / "fixtures" / "demo_proof_graph.json"
    graph = json.loads(fixture_path.read_text(encoding="utf-8"))

    assert graph["sources"]
    assert graph["evidence_nodes"]
    assert graph["claim_nodes"]
    assert graph["skill_nodes"]
    assert graph["gap_nodes"]
    assert graph["trace_events"]
    assert "nodes" not in graph
