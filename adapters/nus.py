"""NUS ModReg adapter stub.

This module intentionally avoids live scraping in the scaffold. The class shape
matches the production adapter contract so real ModReg fetching can be added
behind the same interface.
"""

from __future__ import annotations

from adapters.base import InstitutionAdapter
from schemas.interfaces import FacultyTree, Module, ModuleDetail


class NUSModRegAdapter(InstitutionAdapter):
    """Adapter for the National University of Singapore ModReg catalogue."""

    institution_code = "NUS"

    def get_modules(self) -> list[Module]:
        """Return representative NUS modules."""
        return [
            Module(
                id="nus-bt2102",
                code="BT2102",
                title="Data Management and Visualisation",
                faculty="School of Computing",
                description="Introduces data management, querying, and visualisation.",
                prereqs=[],
                semesters=["1", "2"],
            ),
            Module(
                id="nus-bt3103",
                code="BT3103",
                title="Application Systems Development for Business Analytics",
                faculty="School of Computing",
                description="Applies analytics systems design to business problems.",
                prereqs=["BT2102"],
                semesters=["1"],
            ),
            Module(
                id="nus-is1128",
                code="IS1128",
                title="Information Systems Leadership and Communication",
                faculty="School of Computing",
                description="Builds information systems foundations and communication.",
                prereqs=[],
                semesters=["1", "2"],
            ),
        ]

    def get_module_detail(self, code: str) -> ModuleDetail:
        """Return scaffolded module detail for a NUS module code."""
        modules = {module.code: module for module in self.get_modules()}
        module = modules.get(
            code.upper(),
            Module(
                id=f"nus-{code.lower()}",
                code=code.upper(),
                title="Unknown NUS Module",
                faculty="Unknown Faculty",
                description="No scaffolded details available.",
            ),
        )
        return ModuleDetail(
            id=module.id,
            code=module.code,
            title=module.title,
            faculty=module.faculty,
            description=module.description,
            prereqs=module.prereqs,
            semesters=module.semesters,
            syllabus_url="https://www.nus.edu.sg/modreg/",
            learning_outcomes=[
                "Apply analytical methods to structured problems.",
                "Communicate evidence-backed recommendations.",
            ],
        )

    def get_faculty_structure(self) -> FacultyTree:
        """Return a compact NUS faculty hierarchy."""
        return FacultyTree(
            faculty_name="School of Computing",
            departments=[
                "Information Systems and Analytics",
                "Computer Science",
            ],
            modules=self.get_modules(),
        )
