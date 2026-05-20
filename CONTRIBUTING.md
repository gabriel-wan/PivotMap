# Contributing To PivotMap

## Add A New InstitutionAdapter

1. Create a branch from `dev`.
2. Add a new adapter file under `adapters/`, named after the institution code in lowercase.
3. Import `InstitutionAdapter` from `adapters.base` and shared dataclasses from `schemas.interfaces`.
4. Define a class named after the source system, for example `SMUBiddingAdapter`.
5. Implement `get_modules() -> list[Module]`.
6. Implement `get_module_detail(code: str) -> ModuleDetail`.
7. Implement `get_faculty_structure() -> FacultyTree`.
8. Keep network calls isolated inside private helper methods so tests can mock them.
9. Document source URLs, expected response formats, rate limits, and terms-of-use constraints in the module docstring.
10. Add representative fixtures for the adapter under `tests/fixtures/` if needed.
11. Add pytest coverage for the adapter contract and at least one module-detail lookup.
12. Run `pytest tests/` before opening a pull request.

## Adapter Contract

All adapters must return the shared dataclasses from `schemas.interfaces`; do not return raw scraper payloads from public adapter methods. If an institution source is incomplete or ambiguous, preserve the uncertainty in nullable fields or adapter-specific docstrings rather than inventing data.

## Pull Request Checklist

- The adapter subclasses `InstitutionAdapter`.
- Public methods have type hints and docstrings.
- Tests pass with `pytest tests/`.
- New dependencies are justified in the pull request description.
- Source access respects the institution website's terms and rate limits.
