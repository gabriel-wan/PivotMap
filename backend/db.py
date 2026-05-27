"""Database engine and session setup for PivotMap."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://pivotmap:pivotmap@localhost:5432/pivotmap")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for FastAPI dependency injection."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
