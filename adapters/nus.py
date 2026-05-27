"""NUS module evidence adapter stub."""

from __future__ import annotations

from adapters.base import InstitutionAdapter
from schemas.interfaces import EvidenceNode


class NUSModRegAdapter(InstitutionAdapter):
    """Adapter for NUS module catalogue evidence."""

    institution_code = "NUS"

    def get_modules(self) -> list[EvidenceNode]:
        """Return representative NUS modules as evidence nodes."""
        return [
            EvidenceNode(
                id="module-nus-bt2102",
                user_id="system",
                kind="module",
                title="BT2102 Data Management and Visualisation",
                description="Introduces data management, querying, dashboards, and visualisation.",
                source_ids=["source-nusmods-bt2102"],
                metadata={"institution": "NUS", "faculty": "School of Computing", "semesters": ["1", "2"]},
            ),
            EvidenceNode(
                id="module-nus-bt3103",
                user_id="system",
                kind="module",
                title="BT3103 Application Systems Development for Business Analytics",
                description="Applies analytics systems design to business problems.",
                source_ids=["source-nusmods-bt3103"],
                metadata={"institution": "NUS", "faculty": "School of Computing", "semesters": ["1"]},
            ),
            EvidenceNode(
                id="module-nus-is1128",
                user_id="system",
                kind="module",
                title="IS1128 Information Systems Leadership and Communication",
                description="Builds information systems foundations and communication.",
                source_ids=["source-nusmods-is1128"],
                metadata={"institution": "NUS", "faculty": "School of Computing", "semesters": ["1", "2"]},
            ),
        ]

    def get_module_detail(self, code: str) -> EvidenceNode:
        """Return a detailed NUS module evidence node."""
        modules = {module.title.split(" ", 1)[0]: module for module in self.get_modules()}
        return modules.get(
            code.upper(),
            EvidenceNode(
                id=f"module-nus-{code.lower()}",
                user_id="system",
                kind="module",
                title=f"{code.upper()} Unknown NUS Module",
                description="No scaffolded module details are available.",
                metadata={"institution": "NUS"},
            ),
        )

    def get_faculty_structure(self) -> dict[str, object]:
        """Return a compact NUS faculty hierarchy."""
        return {
            "institution": self.institution_code,
            "faculties": {
                "School of Computing": [
                    "Information Systems and Analytics",
                    "Computer Science",
                ]
            },
        }
