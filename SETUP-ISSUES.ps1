# PivotMap Issues Creation Script
# Requires: gh auth login completed

$OWNER = "gabriel-wan"
$REPO = "PivotMap"
$REPO_PATH = "$OWNER/$REPO"

Write-Host "=== Creating PivotMap Issues ===" -ForegroundColor Green
Write-Host "Repository: https://github.com/$REPO_PATH`n"

# Issue 1
gh issue create --title "Set up MiroFlow agent graph skeleton" --body "Bootstrap MiroFlow project structure with YAML agent graph and five SKILL.md stubs.

Tasks:
- Clone MiroFlow, install via uv sync
- Create config/pivotmap_agent.yaml with all five agent nodes
- Create stub SKILL.md for: planner, jd_parser, research, verifier, synthesiser
- Run smoke test trace with dummy task
- Commit .env.example with API key placeholder

Acceptance Criteria:
- uv run main.py trace exits without error
- All five SKILL.md files present and parseable
- No hardcoded API keys committed" --label "phase-1,type:chore,comp:agent,priority:critical" --milestone "1.2 - Agent Skeleton" 2>$null
Write-Host "  Issue #1: Set up MiroFlow agent graph skeleton"

# Issue 2
gh issue create --title "Implement JD parser agent" --body "Build JD parser SKILL.md and plugin. Extracts structured skill requirements from raw JD text.

Tasks:
- Write skills/jd_parser/SKILL.md with prompt and output schema
- Define JDRequirement Pydantic model
- Implement extraction with importance + category classification
- Write tests/test_jd_parser.py with three sample JDs

Acceptance Criteria:
- Extracts >= 80% of named skills from test JDs
- Importance classification correct for required vs preferred
- Valid JSON output for all test cases" --label "phase-1,type:feature,comp:agent,priority:high" --milestone "1.2 - Agent Skeleton" 2>$null
Write-Host "  Issue #2: Implement JD parser agent"

# Issue 3
gh issue create --title "Implement research agent with temporal tagging" --body "Build research agent using MiroFlow web_search + web_fetch. Register temporal_tagger plugin.

Tasks:
- Write skills/research/SKILL.md with multi-hop search prompt
- Register plugins/temporal_tagger.py via @register decorator
- Extract published_at from meta tags, JSON-LD, byline patterns
- Fallback to retrieved_at with date_uncertain flag
- Define SourcedClaim Pydantic model
- Write tests/test_research_agent.py with mocked web_fetch

Acceptance Criteria:
- published_at populated for >= 70% of test fixtures
- date_uncertain correctly flagged
- Sub-task produces >= 5 SourcedClaim objects" --label "phase-2,type:feature,comp:agent,priority:high" --milestone "2.1 - Research & Verification" 2>$null
Write-Host "  Issue #3: Implement research agent with temporal tagging"

# Issue 4
gh issue create --title "Implement verifier agent" --body "Build verifier agent. Cross-checks SourcedClaim objects, produces confidence scores and conflict nodes.

Tasks:
- Write skills/verifier/SKILL.md
- Implement source independence check (same domain = not independent)
- Define VerifiedClaim model
- Implement conflict detection
- Write tests/test_verifier.py with confirmed, low-confidence, conflict fixtures

Acceptance Criteria:
- 3-source -> confidence >= 0.85, low_confidence false
- 1-source -> low_confidence true
- Contradictory -> conflict_note populated" --label "phase-2,type:feature,comp:agent,priority:high" --milestone "2.1 - Research & Verification" 2>$null
Write-Host "  Issue #4: Implement verifier agent"

# Issue 5
gh issue create --title "Implement proof mapper and synthesiser" --body "Build proof mapper and synthesiser. Classifies each JD requirement as matched/weak/missing against student evidence.

Tasks:
- Define ProofNode and ProofGraph Pydantic models
- Implement semantic matching via pgvector (coordinate with Teammate C)
- Implement keyword fallback when similarity < 0.6
- Write skills/synthesiser/SKILL.md
- Write tests/test_proof_mapper.py with fixture pairs

Acceptance Criteria:
- Strong match -> status: matched, evidence populated
- Partial -> status: weak, gap_note populated
- No match -> status: missing, action populated" --label "phase-2,type:feature,comp:agent,priority:high" --milestone "2.2 - Proof Mapper" 2>$null
Write-Host "  Issue #5: Implement proof mapper and synthesiser"

# Issue 6
gh issue create --title "Write agent integration test - full pipeline trace" --body "Full E2E integration test from JD + profile through to ProofGraph. Primary CI gate for main merges.

Tasks:
- Create tests/integration/test_full_pipeline.py
- Mock: web_search, web_fetch, module_db_query, pgvector_search
- Use demo fixture: Grab Product Analyst JD + NUS Business Year 2 profile
- Assert ProofGraph with >= 1 matched, >= 1 weak, >= 1 missing node
- Assert all VerifiedClaim sources have retrieved_at
- Assert no hallucinated module codes
- Assert runtime < 60s" --label "phase-3,type:test,comp:agent,priority:critical" --milestone "3.1 - Integration & Testing" 2>$null
Write-Host "  Issue #6: Write agent integration test"

# Issue 7
gh issue create --title "Bootstrap Next.js app with Tailwind and React Flow" --body "Scaffold Next.js 14 frontend with TypeScript, Tailwind dark theme, React Flow.

Tasks:
- create-next-app with typescript + tailwind + app router
- Install @xyflow/react
- Configure Tailwind dark mode
- Add blank ReactFlow canvas at /
- Add Prettier + ESLint
- Set NEXT_PUBLIC_API_URL in .env.local

Acceptance Criteria:
- npm run dev starts without error
- Canvas renders at localhost:3000
- ESLint passes 0 errors" --label "phase-1,type:chore,comp:frontend,priority:critical" --milestone "1.1 - Repo & Infrastructure" 2>$null
Write-Host "  Issue #7: Bootstrap Next.js app"

# Issue 8
gh issue create --title "Build student profile and JD input forms" --body "Dual-input onboarding UI: JD upload panel and student profile form.

Tasks:
- Create components/JDInput.tsx - textarea + PDF upload
- Create components/ProfileForm.tsx - school, major, year, modules, projects
- Wire submit to POST /api/analyse
- Add loading spinner and disabled state
- Add form validation

Acceptance Criteria:
- Both forms validate correctly
- Submit fires POST with correct body
- Loading state visible
- Validation blocks empty required fields" --label "phase-1,type:feature,comp:frontend,priority:high" --milestone "1.2 - Agent Skeleton" 2>$null
Write-Host "  Issue #8: Build student profile and JD input forms"

# Issue 9
gh issue create --title "Build proof graph canvas with colour-coded nodes" --body "Core proof graph visualisation using React Flow + dagre. Nodes colour-coded by proof status.

Tasks:
- Install dagre
- Create components/ProofGraph.tsx accepting ProofGraph prop
- Implement ProofNode custom component with status colour
- Implement dagre auto-layout
- Wire node click to evidence panel
- Handle empty state

Acceptance Criteria:
- Matched = green, weak = amber, missing = red
- Node click sets selected state
- Dagre layout non-overlapping
- Renders demo fixture correctly" --label "phase-2,type:feature,comp:frontend,priority:critical" --milestone "2.3 - Frontend Graph Canvas" 2>$null
Write-Host "  Issue #9: Build proof graph canvas"

# Issue 10
gh issue create --title "Build evidence side panel" --body "Evidence panel opens on proof node click. Shows sources, confidence, gap note, recommended action.

Tasks:
- Create components/EvidencePanel.tsx
- Status badge with colour
- Confidence % with progress bar
- Source list with published_at and URL
- gap_note and action block for weak/missing
- low_confidence warning
- Close on outside click / X

Acceptance Criteria:
- Opens/closes correctly
- All three status types render correctly
- Sources with date and domain
- Gap note and action for weak/missing" --label "phase-2,type:feature,comp:frontend,priority:high" --milestone "2.3 - Frontend Graph Canvas" 2>$null
Write-Host "  Issue #10: Build evidence side panel"

# Issue 11
gh issue create --title "Build roadmap timeline and export" --body "Horizontal roadmap timeline below graph canvas. Prove/Learn/Build/Apply lanes. JSON export button.

Tasks:
- Create components/RoadmapTimeline.tsx
- Four action lanes: Prove / Learn / Build / Apply
- Action block: label, skill tag, estimated time
- JSON export download button

Acceptance Criteria:
- All four lanes render correctly
- Export downloads valid JSON
- Renders with >= 8 roadmap actions" --label "phase-3,type:feature,comp:frontend,priority:medium" --milestone "3.2 - Demo & Open-Source" 2>$null
Write-Host "  Issue #11: Build roadmap timeline and export"

# Issue 12
gh issue create --title "Docker Compose and PostgreSQL + pgvector setup" --body "docker-compose.yml with postgres+pgvector, Redis, FastAPI, Next.js. Initial Alembic migration.

Tasks:
- Write docker-compose.yml with db, redis, api, frontend services
- Add healthcheck on db
- Enable pgvector extension in init script
- Install Alembic, write initial migration
- Tables: users, roadmaps (JSONB), proof_nodes, sources, modules
- skills column as vector(1536) on modules

Acceptance Criteria:
- docker compose up starts without error
- alembic upgrade head runs cleanly
- pgvector extension active
- All five tables present" --label "phase-1,type:chore,comp:db,priority:critical" --milestone "1.1 - Repo & Infrastructure" 2>$null
Write-Host "  Issue #12: Docker Compose and PostgreSQL setup"

# Issue 13
gh issue create --title "FastAPI skeleton with /api/analyse endpoint stub" --body "Bootstrap FastAPI app. /api/analyse returns mock ProofGraph so frontend can develop independently.

Tasks:
- Install fastapi, uvicorn, pydantic, sqlalchemy, asyncpg, alembic
- Create api/main.py with CORS for localhost:3000
- Define AnalyseRequest and StudentProfile models
- POST /api/analyse -> mock ProofGraph response
- GET /api/roadmap/{id} -> DB query
- GET /api/health

Acceptance Criteria:
- /api/analyse returns mock ProofGraph 200
- /api/health returns 200
- CORS allows localhost:3000
- Validation rejects missing jd_text" --label "phase-1,type:chore,comp:api,priority:critical" --milestone "1.1 - Repo & Infrastructure" 2>$null
Write-Host "  Issue #13: FastAPI skeleton"

# Issue 14
gh issue create --title "Build InstitutionAdapter and NUS module scraper" --body "Define InstitutionAdapter ABC and implement NUSAdapter scraping NUSMods API.

Tasks:
- Define adapters/base.py with InstitutionAdapter ABC
- Implement adapters/nus.py scraping nusmods.com API
- Map to Module schema, upsert to modules table
- Add scripts/seed_modules.py
- Write adapters/ntu.py stub
- Write tests/test_nus_adapter.py with mocked HTTP

Acceptance Criteria:
- seed_modules.py populates modules table
- Module codes/titles parsed correctly
- NTU stub present with TODO
- CONTRIBUTING.md documents adapter interface" --label "phase-1,type:feature,comp:scraper,priority:high" --milestone "1.3 - Data Layer Core" 2>$null
Write-Host "  Issue #14: Build InstitutionAdapter and NUS scraper"

# Issue 15
gh issue create --title "Implement pgvector embeddings for module-skill matching" --body "Generate embeddings for modules table. Register module_db_query plugin for MiroFlow.

Tasks:
- Add embedding generation to seed_modules.py
- Register plugins/module_db_query.py via @register
- Cosine similarity query returning top-3 modules
- Define ModuleMatch model
- Write tests/test_module_db_query.py with 5 mock modules
- Agree interface with Teammate A in schemas/interfaces.py

Acceptance Criteria:
- Embedding generation runs for >= 10 modules
- Top-3 correctly ranked by similarity
- Plugin callable from agent graph
- Interface agreed in schemas/interfaces.py" --label "phase-2,type:feature,comp:db,priority:high" --milestone "2.2 - Proof Mapper" 2>$null
Write-Host "  Issue #15: Implement pgvector embeddings"

# Issue 16
gh issue create --title "Wire /api/analyse to real agent pipeline and persist ProofGraph" --body "Replace stub response with real MiroFlow pipeline. Persist ProofGraph to roadmaps table.

Tasks:
- Import MiroFlow agent graph from FastAPI (coordinate with Teammate A)
- Run in BackgroundTasks to avoid timeout
- Return 202 with roadmap_id immediately
- Upsert ProofGraph to roadmaps table on completion
- Implement GET /api/roadmap/{id}
- Write tests/test_api_pipeline.py

Acceptance Criteria:
- POST returns 202 with roadmap_id
- ProofGraph persisted to DB
- GET returns ProofGraph when ready
- Concurrent requests do not share state" --label "phase-2,type:feature,comp:api,priority:critical" --milestone "2.2 - Proof Mapper" 2>$null
Write-Host "  Issue #16: Wire /api/analyse to real pipeline"

# Issue 17
gh issue create --title "Set up GitHub Actions CI pipeline" --body "Two workflows: ci.yml (pytest + ESLint), docker.yml (compose build on PR to main).

Tasks:
- Create .github/workflows/ci.yml with pytest + lint jobs
- PostgreSQL service container for DB tests
- Create .github/workflows/docker.yml with compose up + health check
- Add pytest.ini
- Confirm both workflows pass on test PR

Acceptance Criteria:
- ci/pytest and ci/lint appear on all PRs
- Both must be green before merge
- Docker workflow passes on main PRs" --label "phase-1,type:chore,comp:ci,priority:critical" --milestone "1.1 - Repo & Infrastructure" 2>$null
Write-Host "  Issue #17: Set up GitHub Actions CI pipeline"

# Issue 18
gh issue create --title "Publish roadmap-schema.json open-source spec" --body "Publish ProofGraph JSON Schema as standalone open-source spec.

Tasks:
- Finalise ProofGraph/ProofNode into schemas/roadmap-schema.json (JSON Schema draft-07)
- Write schemas/README.md with field documentation
- Add schemas/example-output.json for demo case
- Write tests/test_schema_validation.py
- Link from main README

Acceptance Criteria:
- example-output.json validates against schema
- All fields documented
- Linked from README" --label "phase-3,type:docs,comp:schema,priority:high" --milestone "3.2 - Demo & Open-Source" 2>$null
Write-Host "  Issue #18: Publish roadmap-schema.json"

# Issue 19
gh issue create --title "Write CONTRIBUTING.md and adapter documentation" --body "CONTRIBUTING.md with Add your university as primary contribution path. README quickstart.

Tasks:
- Write CONTRIBUTING.md: Add university, Add role vertical, Add agent skill
- Add 5-minute quickstart to README
- Add architecture diagram link
- Add Powered by MiroFlow badge

Acceptance Criteria:
- University guide clear enough to follow unassisted
- README quickstart works on clean clone
- MiroFlow attribution present" --label "phase-3,type:docs,comp:scraper,priority:high" --milestone "3.2 - Demo & Open-Source" 2>$null
Write-Host "  Issue #19: Write CONTRIBUTING.md"

# Issue 20
gh issue create --title "Pre-compute and freeze demo case for Demo Day" --body "Pre-run pipeline on demo case. Add DEMO_MODE flag so Demo Day runs from fixture, not live API.

Tasks:
- Run pipeline on Grab PA JD + NUS Business Y2 profile
- Save to data/fixtures/demo-output.json
- Add DEMO_MODE=true flag to FastAPI
- Add demo mode banner to frontend
- Verify < 2s load in demo mode
- Validate against schema

Acceptance Criteria:
- DEMO_MODE returns fixture < 2s
- Frontend renders correctly from fixture
- Validates against schema
- Demo banner visible" --label "phase-3,type:chore,comp:agent,priority:critical" --milestone "3.2 - Demo & Open-Source" 2>$null
Write-Host "  Issue #20: Pre-compute demo case"

Write-Host "`nAll 20 issues created!" -ForegroundColor Green
Write-Host "View at: https://github.com/$REPO_PATH/issues`n"
