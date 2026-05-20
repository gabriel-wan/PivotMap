"""Shared dataclass contracts for PivotMap proof graphs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

ProofStatus = Literal["matched", "weak", "missing"]
EvidenceStrength = Literal["strong", "weak"]
SourceType = Literal[
    "job_post",
    "industry_report",
    "course_catalogue",
    "alumni_pattern",
]


@dataclass(frozen=True)
class Module:
    """Institution module record used by adapters and module validation."""

    id: str
    code: str
    title: str
    faculty: str
    description: str
    prereqs: list[str] = field(default_factory=list)
    semesters: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ModuleDetail(Module):
    """Detailed module metadata with syllabus and learning outcomes."""

    syllabus_url: str | None = None
    learning_outcomes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FacultyTree:
    """Faculty structure returned by institution adapters."""

    faculty_name: str
    departments: list[str] = field(default_factory=list)
    modules: list[Module] = field(default_factory=list)


@dataclass(frozen=True)
class SourcedClaim:
    """A claim with source provenance and temporal metadata."""

    claim: str
    source_url: str
    published_at: datetime
    retrieved_at: datetime
    confidence: float
    source_type: SourceType | None = None
    uncertainty_note: str | None = None


@dataclass(frozen=True)
class JDRequirement:
    """A structured requirement extracted from a job description."""

    skill: str
    importance: float
    category: str
    confidence: float
    sources: list[SourcedClaim] = field(default_factory=list)


@dataclass(frozen=True)
class VerifiedSkillClaim:
    """Verifier output keyed to a skill before proof mapping."""

    skill: str
    confidence: float
    sources: list[SourcedClaim] = field(default_factory=list)
    conflict_detected: bool = False
    conflict_note: str | None = None


@dataclass(frozen=True)
class StudentEvidence:
    """Evidence from a student's profile, transcript, or portfolio."""

    type: str
    title: str
    skills_proven: list[str] = field(default_factory=list)
    strength: EvidenceStrength = "weak"


@dataclass(frozen=True)
class ProofNode:
    """A requirement-to-evidence mapping in a proof graph."""

    requirement: JDRequirement
    status: ProofStatus
    evidence: list[StudentEvidence] | None = None
    gap_action: str | None = None
    resume_bullet: str | None = None
    sources: list[SourcedClaim] = field(default_factory=list)


@dataclass(frozen=True)
class ProofGraph:
    """Complete living proof graph for one user and one job description."""

    user_id: str
    jd_text: str
    version: int
    created_at: datetime
    nodes: list[ProofNode] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    diff_from_prev: dict | None = None
