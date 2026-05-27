"""Create Career Proof Graph tables.

Revision ID: 0001_career_proof_graph
Revises:
Create Date: 2026-05-27
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision = "0001_career_proof_graph"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create pgvector/pg_trgm extensions and graph tables."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=80), primary_key=True),
        sa.Column("source_url", sa.Text(), nullable=False, unique=True),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
    )
    op.create_index("ix_sources_source_type", "sources", ["source_type"])

    op.create_table(
        "evidence_nodes",
        sa.Column("id", sa.String(length=80), primary_key=True),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_ids", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
    )
    op.create_index("ix_evidence_nodes_user_id", "evidence_nodes", ["user_id"])
    op.create_index("ix_evidence_nodes_kind", "evidence_nodes", ["kind"])
    op.execute("ALTER TABLE evidence_nodes ADD COLUMN embedding vector(8)")
    op.execute(
        "CREATE INDEX ix_evidence_nodes_title_trgm "
        "ON evidence_nodes USING gin ((title || ' ' || description) gin_trgm_ops)"
    )

    op.create_table(
        "claim_nodes",
        sa.Column("id", sa.String(length=80), primary_key=True),
        sa.Column("evidence_id", sa.String(length=80), sa.ForeignKey("evidence_nodes.id"), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("confidence_status", sa.String(length=40), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("source_ids", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_claim_nodes_evidence_id", "claim_nodes", ["evidence_id"])
    op.create_index("ix_claim_nodes_confidence_status", "claim_nodes", ["confidence_status"])

    op.create_table(
        "skill_nodes",
        sa.Column("id", sa.String(length=80), primary_key=True),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("skill", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("evidence_ids", sa.JSON(), nullable=False),
        sa.Column("claim_ids", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_skill_nodes_user_id", "skill_nodes", ["user_id"])
    op.create_index("ix_skill_nodes_category", "skill_nodes", ["category"])
    op.execute("ALTER TABLE skill_nodes ADD COLUMN embedding vector(8)")
    op.execute("CREATE INDEX ix_skill_nodes_skill_trgm ON skill_nodes USING gin (skill gin_trgm_ops)")

    op.create_table(
        "gap_nodes",
        sa.Column("id", sa.String(length=80), primary_key=True),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("target_role", sa.Text(), nullable=False),
        sa.Column("requirement", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("recommended_action", sa.Text(), nullable=True),
        sa.Column("linked_evidence_ids", sa.JSON(), nullable=False),
        sa.Column("source_ids", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_gap_nodes_user_id", "gap_nodes", ["user_id"])
    op.create_index("ix_gap_nodes_status", "gap_nodes", ["status"])

    op.create_table(
        "trace_events",
        sa.Column("id", sa.String(length=80), primary_key=True),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=120), nullable=False),
        sa.Column("stage", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
    )
    op.create_index("ix_trace_events_user_id", "trace_events", ["user_id"])
    op.create_index("ix_trace_events_run_id", "trace_events", ["run_id"])
    op.create_index("ix_trace_events_stage", "trace_events", ["stage"])


def downgrade() -> None:
    """Drop graph tables and indexes."""
    op.drop_table("trace_events")
    op.drop_table("gap_nodes")
    op.drop_table("skill_nodes")
    op.drop_table("claim_nodes")
    op.drop_table("evidence_nodes")
    op.drop_table("sources")
