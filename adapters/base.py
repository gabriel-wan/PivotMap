"""Base adapter contract for institution evidence sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from schemas.interfaces import EvidenceNode


class InstitutionAdapter(ABC):
    """Abstract interface implemented by all institution adapters."""

    institution_code: str

    @abstractmethod
    def get_modules(self) -> list[EvidenceNode]:
        """Return institution modules as evidence nodes."""

    @abstractmethod
    def get_module_detail(self, code: str) -> EvidenceNode:
        """Return a detailed module evidence node for a single module code."""

    @abstractmethod
    def get_faculty_structure(self) -> dict[str, Any]:
        """Return institution faculty structure metadata."""
