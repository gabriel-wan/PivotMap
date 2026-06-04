# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What PivotMap Is

PivotMap turns scattered career evidence (modules, internships, projects, resumes, voice transcripts) plus a target job description into a **Career Proof Graph**: sources → evidence → claims → skills → gaps, with a trace of how the graph was built. It is built on MiroFlow (MiroMind's deep-research agent framework). The frontend renders the graph and a source-backed "what to show next" roadmap.

## Commands

```bash
# Full stack (Postgres + seed + backend + frontend) via Docker
docker compose up

# Backend only (expects DATABASE_URL; defaults to local Postgres)
PYTHONPATH=. uvicorn backend.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev   # next dev on :3000

# Tests (CI runs exactly this)
PYTHONPATH=. pytest tests/
PYTHONPATH=. pytest tests/test_api.py::test_health   # single test

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "describe change"   # autogen reads backend.models.Base.metadata

# Seed module evidence (dry-run prints; --write persists)
PYTHONPATH=. python scripts/seed_modules.py          # dry run
PYTHONPATH=. python scripts/seed_modules.py --write

# Agent-graph skeleton (uv) — smoke-test the MiroFlow graph with a dummy task
uv sync                          # core deps + .venv (fast)
uv sync --extra miroflow         # also pull MiroFlow (run-agent) from git (heavy)
uv run main.py trace             # validates pivotmap_agent.yaml + every SKILL.md, exits 0
```

`PYTHONPATH=.` (or `PYTHONPATH=/app` in Docker) is required everywhere — modules import as top-level packages (`backend`, `adapters`, `schemas`, `plugins`), not via an installed package.

Two toolchains coexist: **pip + `requirements.txt`** drives Docker and CI; **uv + `pyproject.toml`/`uv.lock`** drives the agent-graph layer (`main.py trace`) and pulls MiroFlow via the optional `miroflow` extra. `pyproject.toml` mirrors `requirements.txt`, so a `uv` env can run the whole app too. `pyproject` marks the project `package = false` (it's a flat app, not an installable wheel).

CI (`.github/workflows/ci.yml`) only runs pytest, on PRs targeting `dev` and `main`. There is no Python linter configured. Branch from `dev` for feature work (see CONTRIBUTING.md).

## The Career Proof Graph contract (central to everything)

One payload shape flows through the entire system — backend responses, DB persistence, the agent output, and the frontend all speak it. It is defined in three places that **must stay in sync**:

- [schemas/interfaces.py](schemas/interfaces.py) — frozen dataclasses + the `Literal` enums (`SourceType`, `EvidenceKind`, `ConfidenceStatus`, `GapStatus`). These are the source of truth for field names and allowed values.
- [schemas/roadmap-schema.json](schemas/roadmap-schema.json) — JSON Schema for the same payload (`additionalProperties: false`), used as the agent's `output_schema`.
- [backend/models.py](backend/models.py) — SQLAlchemy ORM. Note ORM stores the `metadata` JSON column under the attribute name `extra` (SQLAlchemy reserves `metadata`); serializers in `repository.py` map `extra` ↔ `metadata`.

The canonical payload has top-level keys: `user_id`, `sources`, `evidence_nodes`, `claim_nodes`, `skill_nodes`, `gap_nodes`, `trace_events`. Build it via `graph_payload(...)` in [backend/repository.py](backend/repository.py); never hand-assemble these dicts. If you add or rename a field, update all three layers plus the demo fixture (`tests/fixtures/demo_proof_graph.json`).

Graph relationships: `claim.evidence_id` → evidence; `skill.evidence_ids`/`claim_ids` → those nodes; `gap.linked_evidence_ids` → evidence; most nodes carry `source_ids`. Gaps are classified `matched` / `weak` / `missing` — this drives the frontend roadmap UI.

## Backend architecture & two execution modes

[backend/main.py](backend/main.py) is a thin FastAPI layer. Three capture/target endpoints (`/capture/voice`, `/capture/resume`, `/target/jd`) plus `/graph/{user_id}` and `/health`. Every request resolves through one of two modes:

- **Demo/fixture mode** (`DEMO_MODE=true`): returns `tests/fixtures/demo_proof_graph.json` with the requested `user_id` stamped in, and does **not** persist. Used for the deterministic demo and most tests. The frontend defaults to demo unless `NEXT_PUBLIC_DEMO_MODE=false`.
- **Live mode**: calls `MiroMindClient.generate_graph()`, then persists via `store_graph()`.

[backend/miro_client.py](backend/miro_client.py) wraps the MiroMind API (OpenAI-compatible, `base_url=https://api.miromind.ai/v1`). It is defensively layered: missing API key, missing `openai`, or any API error all fall back to `_local_graph()` — a deterministic in-process graph — so the app never hard-fails. It parses both OpenAI object responses and MiroMind SSE-style streamed strings, and tolerates fenced/prose-wrapped JSON (`_first_json_object` balances braces). When touching this file, preserve the fallback-on-everything behavior; tests assert the SSE and wrapped-JSON parsers directly.

Persistence (`store_graph`) uses `session.merge` (upsert by id) across all six tables in one transaction. `load_graph_for_user` collects sources transitively from the user's evidence/claim/gap `source_ids`.

## The agent graph (design vs. what currently ships)

[config/pivotmap_agent.yaml](config/pivotmap_agent.yaml) describes the intended MiroFlow pipeline and is effectively the **feature roadmap** for the agent layer:

```
jd_parser → planner → research ×4 (parallel) → verifier → module_validator → proof_mapper → synthesiser
```

Each node maps to a prompt in `skills/<node>/SKILL.md`. Key designed behaviors: planner spawns 4 parallel research tracks and retries (max 2) any track returning < 3 sourced claims; verifier scores confidence by source count (≥2 confirmed, ==1 low-confidence, contradiction → conflict node); proof_mapper classifies into matched/weak/missing; synthesiser emits the `roadmap-schema.json` payload.

**Important:** the shipping backend does *not* yet run this multi-node graph — `MiroMindClient` makes a single chat-completion call asking for the full graph JSON. The YAML graph + `skills/` prompts are the target architecture being built toward. The root [main.py](main.py) `trace` command (uv) is the current skeleton: it loads this YAML, validates every referenced SKILL.md is present/parseable, and walks the nodes with a dummy task — but does not yet execute the nodes through MiroFlow. Two MiroFlow tools already exist as the building blocks: [plugins/module_db_query.py](plugins/module_db_query.py) (pg_trgm similarity over module evidence, with a fuzzy in-memory fallback) and [plugins/temporal_tagger.py](plugins/temporal_tagger.py) (extracts `published_at` from HTML/JSON-LD and tags source freshness). Both use a `register` decorator that no-ops when MiroFlow isn't installed.

## Institution adapters

[adapters/](adapters/) ingests institution module catalogues into the graph. All adapters subclass `InstitutionAdapter` ([adapters/base.py](adapters/base.py)) and **must return shared dataclasses from `schemas.interfaces`, never raw scraper payloads**. Current adapters (`nus.py`, `ntu.py`) are stubs returning representative modules. `scripts/seed_modules.py` pulls `get_modules()` from each adapter and persists module-kind `EvidenceNode`s + their sources. To add an institution, see CONTRIBUTING.md — keep network calls in private helpers so tests can mock them, and document source URLs / rate limits / terms-of-use in the adapter docstring.

## Frontend

Next.js 14 (pages router) + React 18 + Tailwind v4 + `reactflow`. The whole app is essentially [frontend/pages/index.tsx](frontend/pages/index.tsx) (a single landing/console page) plus two graph renderers in [frontend/components/](frontend/components/): `ProofGraphCanvas.tsx` (reactflow node graph) and `TimelineView.tsx` (roadmap). It POSTs to the backend (`NEXT_PUBLIC_API_URL`, default `http://localhost:8000`) and renders whatever Career Proof Graph comes back. CORS in `backend/main.py` allows only localhost:3000 — add origins there for other hosts.

## Conventions

- Python 3.12, `from __future__ import annotations` at the top of every module, type hints + docstrings on public functions. Schema dataclasses are `frozen=True`. Datetimes are timezone-aware UTC (`datetime.now(UTC)`), serialized as ISO strings at the API boundary.
- Tests run almost entirely in demo mode via `monkeypatch.setenv("DEMO_MODE", "true")` against FastAPI `TestClient` — they need no database. Follow that pattern for new endpoint tests.

# PivotMap Action Plan

## Product Thesis

PivotMap is a persistent career proof graph for students.

It is not a generic resume generator. It turns messy student evidence into structured, confidence-scored proof that can be reused across resumes, job applications, and interviews.

The wedge is low-friction evidence capture:

- speak about what you did
- upload existing material
- connect institution context such as modules
- paste a target JD

All of those inputs write into the same proof store. The graph compounds over time, and MiroFlow makes that compounding useful through registered tools, verification, and visible agent orchestration.

## Hackathon MVP

The hackathon product should center on one golden path:

1. Student yaps about a project or experience.
2. MiroFlow extracts concrete claims.
3. Verifier labels each claim as `verified`, `supported`, `user-attested`, `weak`, or `missing`.
4. Evidence nodes are saved into the proof graph.
5. Student pastes a JD.
6. MiroFlow researches the JD context.
7. Proof map shows matched, weak, and missing evidence.
8. Student receives resume bullets and a gap roadmap.

This is the clearest demonstration of product value and MiroFlow-native architecture.

## Rose, Thorns, Buds

### Rose

- The new direction is tighter because the proof graph is the product spine.
- Voice Yap is the strongest demo moment: raw student ramble becomes structured career evidence.
- Honest scoring is differentiated: PivotMap says which claims will survive scrutiny.
- Live agent trace makes MiroFlow visible instead of hiding it behind a spinner.

### Thorns

- The full feature list is too broad for the hackathon.
- Discovery mode, alumni scraping, and market demand scoring are data-heavy and can sink the build.
- "Verified" must be used carefully. Some evidence is only user-attested or weakly supported.
- NUS-specific features need to be framed as first adapters, not the whole product.

### Buds

- Pitch line: "Anyone can generate a resume bullet. PivotMap tells you whether it will survive scrutiny."
- Institution adapters can make the product globally scalable.
- The proof store can become a long-term career memory graph after the hackathon.
- STAR interview generation becomes natural once proof nodes exist.

## Feature Priority

### Must Ship

- Voice Yap or text-yap capture to structured claims.
- STAR bullet generation from captured evidence.
- JD targeting mode with proof map.
- Live agent trace panel.
- Honest confidence labels.
- Lightweight persistent proof graph.

### Should Ship

- Resume upload as cold start.
- NUSMods module adapter as one proof-enrichment plugin.
- Basic graph visualization.

### Nice To Have

- STAR interview generator.
- GitHub or LinkedIn profile import.
- More institution adapters.

### Cut For Hackathon

- Full Discovery Mode.
- Alumni career path scraping.
- SG market demand scoring.
- Club or society recommendation.
- Full multi-semester career memory beyond a simple persisted proof graph.

## Judge Demo Script

1. Open with the command hero: "Modify my resume to fit this LinkedIn post."
2. Paste or type a 30-second yap transcript about a hackathon.
3. Show MiroFlow trace:
   - planner extracts claims
   - research agent finds context
   - verifier labels confidence
   - synthesiser creates STAR bullets
4. Show the proof graph update with new evidence nodes.
5. Paste a JD.
6. Show MiroFlow researching company-specific skill meaning.
7. Show matched, weak, and missing proof.
8. End on a resume bullet plus roadmap action.

## Judging Alignment

### Product Value

Students forget, undersell, or cannot articulate what they have done. PivotMap lowers the friction to capture proof and turns it into reusable career evidence.

### Engineering Execution

The build demonstrates a real agent pipeline, registered tools, confidence labels, trace output, and persistence.

### AI-Native Authenticity

The product would be weaker as a single LLM call. MiroFlow adds planner decomposition, source-aware research, verification, plugin calls, and stateful graph updates.

### Global Scalability

NUSMods is the first institution adapter. The same architecture can support other universities, job markets, and evidence sources.

# PivotMap Implementation Plan

## Architecture

PivotMap should ship as a thin frontend over a MiroFlow-backed proof pipeline.

### Frontend

- Command hero for the pitch entry point.
- Voice Yap entry as typed transcript first, with real audio optional.
- JD targeting form.
- Proof map view with matched, weak, and missing states.
- Live agent trace panel showing planner, research, verifier, and synthesiser events.
- Resume proof preview with generated bullets and roadmap actions.

### Backend

- FastAPI owns HTTP endpoints and demo orchestration.
- MiroFlow skills perform planning, research, verification, proof mapping, and synthesis.
- Registered plugins provide institution and evidence tools.
- Proof graph state persists in PostgreSQL, with pgvector reserved for similarity search.

### MiroFlow Agent Graph

Core agents:

- `planner`: decomposes yaps, resumes, and JDs into tasks.
- `research`: gathers live context and sources.
- `verifier`: labels confidence and flags weak or conflicting claims.
- `proof_mapper`: maps requirements to stored evidence.
- `synthesiser`: creates STAR bullets, proof graph JSON, and roadmap actions.

Core plugins:

- `get_nus_module_detail(code)`: enriches module nodes with syllabus and skill context.
- `module_db_query(query)`: retrieves known module records.
- `temporal_tagger(html, url, source_type)`: extracts source metadata.
- `proof_store_write(node)`: writes evidence, claim, skill, and gap nodes.
- `proof_store_query(user_id, filters)`: retrieves graph nodes for mapping.

## Minimum Data Model

### Source

- `source_url`
- `source_type`
- `title`
- `published_at`
- `retrieved_at`

### EvidenceNode

- `id`
- `user_id`
- `kind`: `module`, `experience`, `project`, `resume`, `voice`
- `title`
- `description`
- `source_ids`
- `created_at`

### ClaimNode

- `id`
- `evidence_id`
- `claim_text`
- `confidence_status`: `verified`, `supported`, `user-attested`, `weak`, `missing`
- `confidence_score`
- `source_ids`

### SkillNode

- `id`
- `skill`
- `category`
- `confidence_score`
- `evidence_ids`

### GapNode

- `id`
- `target_role`
- `requirement`
- `status`: `matched`, `weak`, `missing`
- `recommended_action`
- `linked_evidence_ids`

## Endpoint Contracts

### `POST /capture/voice`

Input:

- `user_id`
- `transcript`

Output:

- extracted claims
- confidence labels
- generated STAR bullets
- created proof graph node IDs
- trace events

### `POST /capture/resume`

Input:

- `user_id`
- resume text or uploaded file

Output:

- extracted evidence nodes
- extracted claim nodes
- inferred skill nodes
- confidence labels

### `POST /target/jd`

Input:

- `user_id`
- `jd_text`
- optional `company`

Output:

- requirement breakdown
- proof map nodes
- matched / weak / missing summary
- generated resume bullets
- roadmap actions
- trace events

### `GET /graph/:user_id`

Output:

- evidence nodes
- claim nodes
- skill nodes
- gap nodes
- source metadata

## Build Order

1. Mock proof graph and UI states.
2. Text-yap input that behaves like Voice Yap without real audio.
3. Claim extraction from transcript.
4. STAR bullet generation.
5. JD targeting against stored claims.
6. Live trace panel with staged events.
7. Persist proof graph nodes in PostgreSQL.
8. Add NUSMods enrichment plugin.
9. Optional real Whisper/audio upload.
10. Optional resume upload cold start.

## Acceptance Tests

### Voice/Text Yap

- Given a sample transcript, system returns 2-4 structured claims.
- Each claim receives a confidence label.
- Generated STAR bullets reference the extracted claims.
- Unsupported claims are not marked as fully verified.

### JD Targeting

- Given a stored proof graph and a sample JD, system returns matched, weak, and missing requirements.
- Each matched requirement links back to at least one evidence or claim node.
- Missing requirements include roadmap actions.

### Trace Panel

- A run emits planner, research, verifier, and synthesiser events.
- Trace events are readable in chronological order.
- Failed live research produces `source unavailable`, not fake citations.

### Persistence

- A first run creates proof graph nodes for a demo user.
- A second JD targeting run can reuse nodes from the first run.
- Graph retrieval returns nodes with confidence labels and source metadata.

### NUSMods Adapter

- At least one module code enriches an evidence node with skills.
- Adapter failure does not block the rest of the proof pipeline.

## Implementation Defaults

- Start with typed transcript instead of real audio.
- Use deterministic demo fixtures for judge reliability.
- Use honest confidence language: `verified`, `supported`, `user-attested`, `weak`, `missing`.
- Keep Discovery Mode out of the hackathon demo.
- Frame NUS as the first institution adapter, not the product boundary.
