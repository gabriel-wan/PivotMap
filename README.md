# PivotMap

PivotMap is an AI-powered career proof-mapping tool built on MiroFlow, MiroMind's open-source deep research agent framework. It turns sources, evidence, claims, skills, gaps, and trace events into a Career Proof Graph that students can reuse across applications.

Live demo: TODO: add deployed demo link.

## Quickstart

```bash
docker compose up
```

The compose stack starts:

- PostgreSQL with pgvector support on port `5432`
- FastAPI backend on port `8000`
- Next.js frontend on port `3000`

## Repository Layout

- `adapters/`: Institution-specific module catalogue adapters.
- `skills/`: MiroFlow skill prompts for planning, research, verification, module validation, and synthesis.
- `schemas/`: Shared Python dataclasses and JSON schema for the Career Proof Graph.
- `plugins/`: MiroFlow registered tools used by the agent graph.
- `config/`: PivotMap agent graph configuration.
- `scripts/`: Utilities such as module database seeding.
- `tests/`: Pytest coverage and fixtures.

## Adding An Institution Adapter

1. Create a new file in `adapters/`, for example `adapters/smu.py`.
2. Subclass `InstitutionAdapter` from `adapters.base`.
3. Implement `get_modules()`, `get_module_detail(code: str)`, and `get_faculty_structure()`.
4. Return the shared dataclasses from `schemas.interfaces`.
5. Add tests in `tests/test_adapters.py`.
6. Document source URLs, rate limits, and any terms-of-use constraints in the adapter docstring.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution workflow.
