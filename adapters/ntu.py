"""NTU module evidence adapter stub."""

from __future__ import annotations

from adapters.base import InstitutionAdapter
from schemas.interfaces import EvidenceNode


class NTUCourseRegAdapter(InstitutionAdapter):
    """Adapter for NTU module catalogue evidence."""

    institution_code = "NTU"

    def get_modules(self) -> list[EvidenceNode]:
        """Return representative NTU modules as evidence nodes."""
        return [
            EvidenceNode(
                id="module-ntu-sc1003",
                user_id="system",
                kind="module",
                title="SC1003 Introduction to Computational Thinking",
                description="Introduces computational problem solving and programming.",
                source_ids=["source-ntu-sc1003"],
                metadata={"institution": "NTU", "faculty": "College of Computing and Data Science"},
            ),
            EvidenceNode(
                id="module-ntu-bc2407",
                user_id="system",
                kind="module",
                title="BC2407 Analytics I: Visual and Predictive Techniques",
                description="Covers visual analytics and predictive modelling.",
                source_ids=["source-ntu-bc2407"],
                metadata={"institution": "NTU", "faculty": "Nanyang Business School"},
            ),
        ]

    def get_module_detail(self, code: str) -> EvidenceNode:
        """Return a detailed NTU module evidence node."""
        modules = {module.title.split(" ", 1)[0]: module for module in self.get_modules()}
        return modules.get(
            code.upper(),
            EvidenceNode(
                id=f"module-ntu-{code.lower()}",
                user_id="system",
                kind="module",
                title=f"{code.upper()} Unknown NTU Module",
                description="No scaffolded module details are available.",
                metadata={"institution": "NTU"},
            ),
        )

    def get_faculty_structure(self) -> dict[str, object]:
        """Return a compact NTU faculty hierarchy."""
        return {
            "institution": self.institution_code,
            "faculties": {
                "College of Computing and Data Science": ["Computer Science"],
                "Nanyang Business School": ["Business Analytics"],
            },
        }
