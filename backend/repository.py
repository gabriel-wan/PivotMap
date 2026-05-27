"""Persistence helpers for Career Proof Graph API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import (
    ClaimNodeModel,
    EvidenceNodeModel,
    GapNodeModel,
    SkillNodeModel,
    SourceModel,
    TraceEventModel,
)

GraphPayload = dict[str, list[dict[str, Any]] | str]


def store_graph(session: Session, graph: dict[str, Any]) -> None:
    """Upsert all graph entities in a Career Proof Graph payload."""
    for source in graph.get("sources", []):
        session.merge(
            SourceModel(
                id=source["id"],
                source_url=source["source_url"],
                source_type=source["source_type"],
                title=source["title"],
                published_at=_parse_datetime(source.get("published_at")),
                retrieved_at=_parse_datetime(source["retrieved_at"]),
                extra=source.get("metadata", {}),
            )
        )

    for evidence in graph.get("evidence_nodes", []):
        session.merge(
            EvidenceNodeModel(
                id=evidence["id"],
                user_id=evidence["user_id"],
                kind=evidence["kind"],
                title=evidence["title"],
                description=evidence["description"],
                source_ids=evidence.get("source_ids", []),
                created_at=_parse_datetime(evidence["created_at"]),
                extra=evidence.get("metadata", {}),
            )
        )

    for claim in graph.get("claim_nodes", []):
        session.merge(
            ClaimNodeModel(
                id=claim["id"],
                evidence_id=claim["evidence_id"],
                claim_text=claim["claim_text"],
                confidence_status=claim["confidence_status"],
                confidence_score=claim["confidence_score"],
                source_ids=claim.get("source_ids", []),
                created_at=_parse_datetime(claim["created_at"]),
            )
        )

    for skill in graph.get("skill_nodes", []):
        session.merge(
            SkillNodeModel(
                id=skill["id"],
                user_id=skill["user_id"],
                skill=skill["skill"],
                category=skill["category"],
                confidence_score=skill["confidence_score"],
                evidence_ids=skill.get("evidence_ids", []),
                claim_ids=skill.get("claim_ids", []),
                created_at=_parse_datetime(skill["created_at"]),
            )
        )

    for gap in graph.get("gap_nodes", []):
        session.merge(
            GapNodeModel(
                id=gap["id"],
                user_id=gap["user_id"],
                target_role=gap["target_role"],
                requirement=gap["requirement"],
                status=gap["status"],
                recommended_action=gap.get("recommended_action"),
                linked_evidence_ids=gap.get("linked_evidence_ids", []),
                source_ids=gap.get("source_ids", []),
                created_at=_parse_datetime(gap["created_at"]),
            )
        )

    for event in graph.get("trace_events", []):
        session.merge(
            TraceEventModel(
                id=event["id"],
                user_id=event["user_id"],
                run_id=event["run_id"],
                stage=event["stage"],
                message=event["message"],
                created_at=_parse_datetime(event["created_at"]),
                extra=event.get("metadata", {}),
            )
        )

    session.commit()


def load_graph_for_user(session: Session, user_id: str) -> dict[str, Any]:
    """Load a user's graph entities from the database."""
    evidence = session.scalars(
        select(EvidenceNodeModel).where(EvidenceNodeModel.user_id == user_id)
    ).all()
    source_ids = {source_id for node in evidence for source_id in node.source_ids}
    claims = session.scalars(
        select(ClaimNodeModel).join(EvidenceNodeModel).where(EvidenceNodeModel.user_id == user_id)
    ).all()
    for claim in claims:
        source_ids.update(claim.source_ids)
    skills = session.scalars(select(SkillNodeModel).where(SkillNodeModel.user_id == user_id)).all()
    gaps = session.scalars(select(GapNodeModel).where(GapNodeModel.user_id == user_id)).all()
    for gap in gaps:
        source_ids.update(gap.source_ids)
    traces = session.scalars(select(TraceEventModel).where(TraceEventModel.user_id == user_id)).all()
    sources = (
        session.scalars(select(SourceModel).where(SourceModel.id.in_(source_ids))).all()
        if source_ids
        else []
    )
    return graph_payload(
        user_id=user_id,
        sources=[source_to_dict(source) for source in sources],
        evidence_nodes=[evidence_to_dict(node) for node in evidence],
        claim_nodes=[claim_to_dict(node) for node in claims],
        skill_nodes=[skill_to_dict(node) for node in skills],
        gap_nodes=[gap_to_dict(node) for node in gaps],
        trace_events=[trace_to_dict(node) for node in traces],
    )


def graph_payload(
    user_id: str,
    sources: list[dict[str, Any]] | None = None,
    evidence_nodes: list[dict[str, Any]] | None = None,
    claim_nodes: list[dict[str, Any]] | None = None,
    skill_nodes: list[dict[str, Any]] | None = None,
    gap_nodes: list[dict[str, Any]] | None = None,
    trace_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the canonical Career Proof Graph API payload."""
    return {
        "user_id": user_id,
        "sources": sources or [],
        "evidence_nodes": evidence_nodes or [],
        "claim_nodes": claim_nodes or [],
        "skill_nodes": skill_nodes or [],
        "gap_nodes": gap_nodes or [],
        "trace_events": trace_events or [],
    }


def source_to_dict(source: SourceModel) -> dict[str, Any]:
    """Serialize a source model."""
    return {
        "id": source.id,
        "source_url": source.source_url,
        "source_type": source.source_type,
        "title": source.title,
        "published_at": _format_datetime(source.published_at),
        "retrieved_at": _format_datetime(source.retrieved_at),
        "metadata": source.extra,
    }


def evidence_to_dict(node: EvidenceNodeModel) -> dict[str, Any]:
    """Serialize an evidence node model."""
    return {
        "id": node.id,
        "user_id": node.user_id,
        "kind": node.kind,
        "title": node.title,
        "description": node.description,
        "source_ids": node.source_ids,
        "created_at": _format_datetime(node.created_at),
        "metadata": node.extra,
    }


def claim_to_dict(node: ClaimNodeModel) -> dict[str, Any]:
    """Serialize a claim node model."""
    return {
        "id": node.id,
        "evidence_id": node.evidence_id,
        "claim_text": node.claim_text,
        "confidence_status": node.confidence_status,
        "confidence_score": node.confidence_score,
        "source_ids": node.source_ids,
        "created_at": _format_datetime(node.created_at),
    }


def skill_to_dict(node: SkillNodeModel) -> dict[str, Any]:
    """Serialize a skill node model."""
    return {
        "id": node.id,
        "user_id": node.user_id,
        "skill": node.skill,
        "category": node.category,
        "confidence_score": node.confidence_score,
        "evidence_ids": node.evidence_ids,
        "claim_ids": node.claim_ids,
        "created_at": _format_datetime(node.created_at),
    }


def gap_to_dict(node: GapNodeModel) -> dict[str, Any]:
    """Serialize a gap node model."""
    return {
        "id": node.id,
        "user_id": node.user_id,
        "target_role": node.target_role,
        "requirement": node.requirement,
        "status": node.status,
        "recommended_action": node.recommended_action,
        "linked_evidence_ids": node.linked_evidence_ids,
        "source_ids": node.source_ids,
        "created_at": _format_datetime(node.created_at),
    }


def trace_to_dict(node: TraceEventModel) -> dict[str, Any]:
    """Serialize a trace event model."""
    return {
        "id": node.id,
        "user_id": node.user_id,
        "run_id": node.run_id,
        "stage": node.stage,
        "message": node.message,
        "created_at": _format_datetime(node.created_at),
        "metadata": node.extra,
    }


def _parse_datetime(value: str | datetime | None) -> datetime | None:
    """Parse API datetimes into Python datetimes."""
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _format_datetime(value: datetime | None) -> str | None:
    """Format a datetime for JSON responses."""
    if value is None:
        return None
    return value.isoformat()
