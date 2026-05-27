"""Seed module evidence into the Career Proof Graph database."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from datetime import UTC, datetime

from adapters.base import InstitutionAdapter
from adapters.ntu import NTUCourseRegAdapter
from adapters.nus import NUSModRegAdapter
from backend.db import SessionLocal
from backend.models import EvidenceNodeModel, SourceModel
from schemas.interfaces import EvidenceNode


def iter_module_evidence(adapters: Iterable[InstitutionAdapter]) -> Iterable[EvidenceNode]:
    """Yield module evidence from each configured institution adapter."""
    for adapter in adapters:
        yield from adapter.get_modules()


def seed_modules(dry_run: bool = True) -> list[EvidenceNode]:
    """Seed module evidence nodes and sources through the ORM."""
    adapters: list[InstitutionAdapter] = [NUSModRegAdapter(), NTUCourseRegAdapter()]
    modules = list(iter_module_evidence(adapters))
    if dry_run:
        for module in modules:
            print(f"{module.id}: {module.title}")
        return modules

    with SessionLocal() as session:
        retrieved_at = datetime.now(UTC)
        for module in modules:
            for source_id in module.source_ids:
                session.merge(
                    SourceModel(
                        id=source_id,
                        source_url=_source_url(module.title),
                        source_type="course_catalogue",
                        title=module.title,
                        published_at=None,
                        retrieved_at=retrieved_at,
                        extra=module.metadata,
                    )
                )
            session.merge(
                EvidenceNodeModel(
                    id=module.id,
                    user_id=module.user_id,
                    kind=module.kind,
                    title=module.title,
                    description=module.description,
                    source_ids=module.source_ids,
                    created_at=module.created_at,
                    extra=module.metadata,
                )
            )
        session.commit()
    return modules


def _source_url(title: str) -> str:
    """Return a deterministic public catalogue URL for a module title."""
    code = title.split(" ", 1)[0]
    if code.startswith("BT") or code.startswith("IS"):
        return f"https://nusmods.com/courses/{code}"
    return f"https://www.ntu.edu.sg/education/course-registration?course={code}"


def main(argv: list[str] | None = None) -> None:
    """Parse CLI arguments and seed module evidence."""
    parser = argparse.ArgumentParser(description="Seed PivotMap module evidence.")
    parser.add_argument("--write", action="store_true", help="Write records to PostgreSQL.")
    args = parser.parse_args(argv)
    seed_modules(dry_run=not args.write)


if __name__ == "__main__":
    main()
