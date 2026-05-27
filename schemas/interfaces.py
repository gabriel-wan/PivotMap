"""Application-facing contracts for the PivotMap Career Proof Graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

SourceType = Literal[
    "job_post",
    "industry_report",
    "course_catalogue",
    "alumni_pattern",
    "portfolio",
    "resume",
    "voice",
]
EvidenceKind = Literal["module", "experience", "project", "resume", "voice"]
ConfidenceStatus = Literal["verified", "supported", "user-attested", "weak", "missing"]
GapStatus = Literal["matched", "weak", "missing"]


@dataclass(frozen=True)
class Source:
    """A retrievable source used to support evidence, claims, skills, or gaps."""

    id: str
    source_url: str
    source_type: SourceType
    title: str
    published_at: datetime | None
    retrieved_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceNode:
    """A stored piece of career evidence from modules, work, projects, or uploads."""

    id: str
    user_id: str
    kind: EvidenceKind
    title: str
    description: str
    source_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ClaimNode:
    """A confidence-scored claim extracted from an evidence node."""

    id: str
    evidence_id: str
    claim_text: str
    confidence_status: ConfidenceStatus
    confidence_score: float
    source_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class SkillNode:
    """A skill inferred from claim and evidence nodes."""

    id: str
    user_id: str
    skill: str
    category: str
    confidence_score: float
    evidence_ids: list[str] = field(default_factory=list)
    claim_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class GapNode:
    """A target-role requirement classified against the user's proof graph."""

    id: str
    user_id: str
    target_role: str
    requirement: str
    status: GapStatus
    recommended_action: str | None
    linked_evidence_ids: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class TraceEvent:
    """A visible agent or system event emitted during graph construction."""

    id: str
    user_id: str
    run_id: str
    stage: str
    message: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)
