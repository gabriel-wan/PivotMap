"""NTU CourseReg adapter stub."""

from __future__ import annotations

from adapters.base import InstitutionAdapter
from schemas.interfaces import FacultyTree, Module, ModuleDetail


class NTUCourseRegAdapter(InstitutionAdapter):
    """Adapter for the Nanyang Technological University CourseReg catalogue."""

    institution_code = "NTU"

    def get_modules(self) -> list[Module]:
        """Return representative NTU modules."""
        return [
            Module(
                id="ntu-sc1003",
                code="SC1003",
                title="Introduction to Computational Thinking",
                faculty="College of Computing and Data Science",
                description="Introduces computational problem solving and programming.",
                prereqs=[],
                semesters=["1", "2"],
            ),
            Module(
                id="ntu-bc2407",
                code="BC2407",
                title="Analytics I: Visual and Predictive Techniques",
                faculty="Nanyang Business School",
                description="Covers visual analytics and predictive modelling.",
                prereqs=[],
                semesters=["1"],
            ),
        ]

    def get_module_detail(self, code: str) -> ModuleDetail:
        """Return scaffolded module detail for an NTU module code."""
        modules = {module.code: module for module in self.get_modules()}
        module = modules.get(
            code.upper(),
            Module(
                id=f"ntu-{code.lower()}",
                code=code.upper(),
                title="Unknown NTU Module",
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
            syllabus_url="https://www.ntu.edu.sg/education/course-registration",
            learning_outcomes=[
                "Use data to support business decisions.",
                "Communicate analytical recommendations.",
            ],
        )

    def get_faculty_structure(self) -> FacultyTree:
        """Return a compact NTU faculty hierarchy."""
        return FacultyTree(
            faculty_name="College of Computing and Data Science",
            departments=["Computer Science", "Business Analytics"],
            modules=self.get_modules(),
        )
