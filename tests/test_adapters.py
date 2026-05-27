"""Tests for institution adapters."""

from adapters.base import InstitutionAdapter
from adapters.ntu import NTUCourseRegAdapter
from adapters.nus import NUSModRegAdapter
from schemas.interfaces import EvidenceNode


def test_adapters_return_module_evidence_nodes() -> None:
    """Institution adapters should return Career Proof Graph evidence nodes."""
    adapters: list[InstitutionAdapter] = [NUSModRegAdapter(), NTUCourseRegAdapter()]

    for adapter in adapters:
        modules = adapter.get_modules()
        assert modules
        assert isinstance(adapter.get_module_detail(modules[0].title.split(" ", 1)[0]), EvidenceNode)
        assert adapter.get_faculty_structure()["institution"]
