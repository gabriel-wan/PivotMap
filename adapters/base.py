"""Base adapter contract for institution module catalogues."""

from __future__ import annotations

from abc import ABC, abstractmethod

from schemas.interfaces import FacultyTree, Module, ModuleDetail


class InstitutionAdapter(ABC):
    """Abstract interface implemented by all institution adapters."""

    institution_code: str

    @abstractmethod
    def get_modules(self) -> list[Module]:
        """Return a lightweight list of modules available at the institution."""

    @abstractmethod
    def get_module_detail(self, code: str) -> ModuleDetail:
        """Return detailed information for a single module code."""

    @abstractmethod
    def get_faculty_structure(self) -> FacultyTree:
        """Return the faculty, school, department, and programme hierarchy."""
