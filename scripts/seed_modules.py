"""Seed PostgreSQL module records from institution adapters."""

from __future__ import annotations

import argparse
import os
from collections.abc import Iterable
from adapters.base import InstitutionAdapter
from adapters.ntu import NTUCourseRegAdapter
from adapters.nus import NUSModRegAdapter
from schemas.interfaces import Module, SourceType


def iter_modules(adapters: Iterable[InstitutionAdapter]) -> Iterable[Module]:
    """Yield modules from each configured adapter."""
    for adapter in adapters:
        yield from adapter.get_modules()


def seed_modules(
    dry_run: bool = True,
    database_url: str | None = None,
    source_type: SourceType = "course_catalogue",
) -> list[Module]:
    """Seed module records with temporal source typing.

    The `source_type` column supports temporal decay rules in
    `plugins.temporal_tagger`, distinguishing job posts, industry reports,
    course catalogues, and alumni patterns.
    """
    adapters: list[InstitutionAdapter] = [NUSModRegAdapter(), NTUCourseRegAdapter()]
    modules = list(iter_modules(adapters))
    if dry_run:
        for module in modules:
            print(f"{module.faculty}:{module.code} {module.title} source_type={source_type}")
        return modules

    _write_modules(database_url or os.getenv("DATABASE_URL"), modules, source_type)
    return modules


def _write_modules(
    database_url: str | None,
    modules: list[Module],
    source_type: SourceType,
) -> None:
    """Create extensions, create table, and upsert module records."""
    if not database_url:
        raise RuntimeError("DATABASE_URL is required when --write is used.")
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("psycopg is required to write module seed data.") from exc

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS modules (
                    id TEXT PRIMARY KEY,
                    code TEXT NOT NULL,
                    title TEXT NOT NULL,
                    faculty TEXT NOT NULL,
                    description TEXT NOT NULL,
                    prereqs TEXT[] NOT NULL DEFAULT '{}',
                    semesters TEXT[] NOT NULL DEFAULT '{}',
                    source_type TEXT NOT NULL DEFAULT 'course_catalogue',
                    embedding vector(8)
                )
                """
            )
            for module in modules:
                cur.execute(
                    """
                    INSERT INTO modules (
                        id, code, title, faculty, description, prereqs,
                        semesters, source_type, embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                    ON CONFLICT (id) DO UPDATE SET
                        code = EXCLUDED.code,
                        title = EXCLUDED.title,
                        faculty = EXCLUDED.faculty,
                        description = EXCLUDED.description,
                        prereqs = EXCLUDED.prereqs,
                        semesters = EXCLUDED.semesters,
                        source_type = EXCLUDED.source_type,
                        embedding = EXCLUDED.embedding
                    """,
                    (
                        module.id,
                        module.code,
                        module.title,
                        module.faculty,
                        module.description,
                        module.prereqs,
                        module.semesters,
                        source_type,
                        _semantic_stub_vector(module),
                    ),
                )
        conn.commit()


def _semantic_stub_vector(module: Module) -> str:
    """Return a deterministic vector literal placeholder for module search."""
    seed_text = f"{module.code} {module.title} {module.description}"
    seed = sum(ord(char) for char in seed_text) or 1
    values = [((seed + index) % 100) / 100 for index in range(8)]
    return "[" + ",".join(f"{value:.2f}" for value in values) + "]"


def main(argv: list[str] | None = None) -> None:
    """Parse CLI arguments and seed module records."""
    parser = argparse.ArgumentParser(description="Seed PivotMap module records.")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write records to PostgreSQL instead of printing them.",
    )
    parser.add_argument(
        "--source-type",
        choices=["job_post", "industry_report", "course_catalogue", "alumni_pattern"],
        default="course_catalogue",
        help="Source type stored with seeded modules.",
    )
    args = parser.parse_args(argv)
    seed_modules(dry_run=not args.write, source_type=args.source_type)  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
