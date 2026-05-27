"""SQLAlchemy ORM models for the Career Proof Graph."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for PivotMap ORM models."""


class SourceModel(Base):
    """Persistent source metadata."""

    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    source_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class EvidenceNodeModel(Base):
    """Persistent career evidence node."""

    __tablename__ = "evidence_nodes"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)

    claims: Mapped[list[ClaimNodeModel]] = relationship(back_populates="evidence")


class ClaimNodeModel(Base):
    """Persistent confidence-scored claim."""

    __tablename__ = "claim_nodes"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    evidence_id: Mapped[str] = mapped_column(ForeignKey("evidence_nodes.id"), nullable=False, index=True)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    source_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    evidence: Mapped[EvidenceNodeModel] = relationship(back_populates="claims")


class SkillNodeModel(Base):
    """Persistent skill node inferred from user evidence."""

    __tablename__ = "skill_nodes"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    skill: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    claim_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class GapNodeModel(Base):
    """Persistent target-role gap classification."""

    __tablename__ = "gap_nodes"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    target_role: Mapped[str] = mapped_column(Text, nullable=False)
    requirement: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    linked_evidence_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    source_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class TraceEventModel(Base):
    """Persistent agent trace event."""

    __tablename__ = "trace_events"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    run_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)
