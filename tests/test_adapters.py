"""Tests for institution adapters."""

from adapters.base import InstitutionAdapter
from adapters.ntu import NTUCourseRegAdapter
from adapters.nus import NUSModRegAdapter
from schemas.interfaces import FacultyTree, ModuleDetail


def test_adapters_implement_contract() -> None:
    """Institution adapters should return shared schema dataclasses."""
    adapters: list[InstitutionAdapter] = [NUSModRegAdapter(), NTUCourseRegAdapter()]

    for adapter in adapters:
        modules = adapter.get_modules()
        assert modules
        assert modules[0].faculty
        assert isinstance(adapter.get_module_detail(modules[0].code), ModuleDetail)
        assert isinstance(adapter.get_faculty_structure(), FacultyTree)
