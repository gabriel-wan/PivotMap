# PivotMap Implementation Checkpoints

This document compares the current build against the intended hackathon implementation and turns the remaining work into checkpoints.

Legend:

- `[x]` shipped enough for demo use
- `[~]` partially shipped, usable but not complete
- `[ ]` not shipped yet

## Current Build Snapshot

PivotMap currently has a real vertical slice:

- Next.js frontend with command hero, light/dark mode, text-first evidence capture, JD targeting, proof graph view, trace panel, and resume proof preview.
- FastAPI backend with `/capture/voice`, `/capture/resume`, `/target/jd`, `/graph/{user_id}`, and `/health`.
- Career Proof Graph schema with sources, evidence, claims, skills, gaps, and trace events.
- PostgreSQL persistence for graph nodes, including idempotent source upsert by `source_url`.
- Demo fixture and deterministic local fallback for judge reliability.
- MiroMind API client path using `MIROMIND_API_KEY`.
- Agent graph config and skill prompt files exist, but the backend is not yet executing that configured multi-agent graph directly.

The biggest remaining gap is not UI. The biggest gap is making MiroFlow visibly central: registered plugins, staged agent execution, trace events, and proof graph persistence should clearly come from the agent pipeline instead of a single model/fallback graph.

## Plan Comparison

### Frontend

- `[x]` Command hero for the pitch entry point.
- `[x]` Typed rotating command placeholder.
- `[x]` Light/dark toggle.
- `[x]` Text-yap input that behaves like Voice Yap without real audio.
- `[x]` JD targeting form.
- `[x]` Proof map view with evidence, claims, skills, and gaps.
- `[x]` Trace panel display.
- `[x]` Resume proof preview.
- `[~]` STAR bullet output. Current preview uses claim text as bullets; it does not yet guarantee STAR structure.
- `[~]` Resume capture in UI. Backend endpoint exists, but frontend does not expose a distinct resume-upload/cold-start flow.
- `[ ]` Real audio capture and Whisper upload.

### Backend

- `[x]` FastAPI app and health endpoint.
- `[x]` `POST /capture/voice`.
- `[x]` `POST /capture/resume`.
- `[x]` `POST /target/jd`.
- `[x]` `GET /graph/{user_id}`.
- `[x]` Demo mode fixture path.
- `[x]` Local fallback graph when API key or live model call fails.
- `[x]` Safe startup logging for API-key presence.
- `[x]` PostgreSQL persistence for graph nodes.
- `[x]` Idempotent source persistence by unique `source_url`.
- `[~]` Live MiroMind call. API wiring exists, but output quality depends on one JSON-generation request.
- `[x]` JD targeting against stored user graph. The endpoint now loads existing evidence, claims, skills, and sources before mapping a JD and returns new gap nodes linked to stored proof.
- `[ ]` Streaming trace event endpoint.
- `[ ]` Request/response schema validation against `schemas/roadmap-schema.json` before persistence.
- `[ ]` Real file upload handling for resumes.

### MiroFlow / Agent Graph

- `[x]` Agent graph config exists at `config/pivotmap_agent.yaml`.
- `[x]` Skill prompt files exist for `jd_parser`, `planner`, `research`, `verifier`, `module_validator`, `proof_mapper`, and `synthesiser`.
- `[x]` Plugin-style modules exist for `module_db_query` and `temporal_tagger`.
- `[~]` Trace events exist in graph payloads and UI.
- `[~]` MiroFlow is visible in copy and architecture, but not yet visibly running as the backend orchestration engine.
- `[ ]` Backend executes the configured agent graph stages in order.
- `[ ]` Backend emits staged trace events from actual planner/research/verifier/proof_mapper/synthesiser execution.
- `[ ]` Registered `proof_store_write` and `proof_store_query` plugin functions.
- `[ ]` Research/verifier path that gathers and cross-checks live external sources.

### Data Model

- `[x]` `Source`.
- `[x]` `EvidenceNode`.
- `[x]` `ClaimNode`.
- `[x]` `SkillNode`.
- `[x]` `GapNode`.
- `[x]` `TraceEvent`.
- `[x]` ORM models for all graph entities.
- `[x]` JSON schema fixture coverage.
- `[~]` Confidence language supports `verified`, `supported`, `user-attested`, `weak`, and `missing`.
- `[~]` Source linking works by IDs, but richer citation display is still light.
- `[ ]` Versioned graph/run history for comparing proof score over time.
- `[ ]` pgvector similarity search.

### Institution / Evidence Plugins

- `[x]` NUS adapter exists.
- `[x]` NTU adapter stub/example exists.
- `[x]` Module DB query plugin exists.
- `[x]` Temporal tagger plugin exists.
- `[~]` NUSMods enrichment exists as demo/static adapter logic, not robust live scraping.
- `[ ]` GitHub import.
- `[ ]` LinkedIn import.
- `[ ]` Alumni path scraping.
- `[ ]` SG market demand scoring.

## Endpoint Checkpoints

### `POST /capture/voice`

- `[x]` Accepts `user_id` and `transcript`.
- `[x]` Returns graph-shaped payload.
- `[x]` Persists graph in normal mode.
- `[x]` Falls back safely when API key/live call fails.
- `[~]` Extracts claims through live model path.
- `[ ]` Deterministic local extractor that produces 2-4 specific claims from transcript.
- `[ ]` Real audio upload and transcription.

### `POST /capture/resume`

- `[x]` Accepts `user_id` and `resume_text`.
- `[x]` Returns graph-shaped payload.
- `[x]` Persists graph in normal mode.
- `[~]` Useful for typed resume cold start.
- `[ ]` Resume file upload.
- `[ ]` Frontend cold-start resume upload flow.

### `POST /target/jd`

- `[x]` Accepts `user_id`, `jd_text`, optional `company`, and `student_profile`.
- `[x]` Returns graph-shaped payload with gap nodes.
- `[x]` Persists graph in normal mode.
- `[~]` Produces matched/weak/missing states in demo fixture.
- `[x]` Loads existing user graph before mapping.
- `[~]` Explicit requirement extraction step. Deterministic fallback extracts known career keywords; live model path still handles richer interpretation.
- `[x]` Requirement-to-evidence matcher using stored claims and skills.
- `[ ]` JD context research and source-backed company interpretation.

### `GET /graph/{user_id}`

- `[x]` Loads persisted evidence, claims, skills, gaps, sources, and trace events.
- `[x]` Returns demo fixture in demo mode.
- `[~]` Source joins work through JSON `source_ids`.
- `[ ]` Sorting/version filtering by run.
- `[ ]` Graph summary endpoint for dashboard counters.

## Build Order Checkpoints

### Checkpoint 1 - Demo UI And Mock Graph

- `[x]` Command hero.
- `[x]` Proof console below hero.
- `[x]` Proof graph visualization.
- `[x]` Resume proof preview.
- `[x]` Light/dark mode.
- `[x]` Fixed-height demo panels to avoid jarring layout shifts.

### Checkpoint 2 - Text-Yap Capture

- `[x]` Textarea-based evidence capture.
- `[x]` Submit to `/capture/voice`.
- `[x]` Display returned graph.
- `[~]` Claim extraction. Live model can produce graph JSON, fallback is generic.
- `[ ]` Rule-based local extractor for reliable offline demos.

### Checkpoint 3 - STAR Bullet Generation

- `[~]` Resume preview shows claim-derived bullets.
- `[ ]` Backend returns explicit `resume_bullets` or STAR bullet metadata.
- `[ ]` Bullets include situation/task/action/result structure where possible.
- `[ ]` Unsupported/user-attested bullets are labeled honestly.

### Checkpoint 4 - JD Targeting

- `[x]` JD editor.
- `[x]` Submit to `/target/jd`.
- `[x]` Matched/weak/missing graph display in demo fixture.
- `[~]` Live model path can generate graph JSON.
- `[ ]` Requirement extraction separate from proof mapping.
- `[ ]` Stored evidence loaded before mapping.
- `[ ]` Roadmap actions tied to missing/weak requirements.

### Checkpoint 5 - Trace Panel

- `[x]` Trace events render in the proof panel.
- `[x]` Demo fixture has planner/verifier/synthesiser events.
- `[~]` Local fallback emits one generic trace event.
- `[ ]` Live run emits planner, research, verifier, proof_mapper, and synthesiser events.
- `[ ]` Optional server-sent events or polling for live trace updates.

### Checkpoint 6 - Persistence

- `[x]` PostgreSQL models.
- `[x]` Alembic migration.
- `[x]` Store graph payload.
- `[x]` Load graph by user.
- `[x]` Source upsert by `source_url`.
- `[x]` Repository test for repeated source URL.
- `[ ]` Run/version grouping for multiple graph generations.
- `[ ]` Merge policy for repeated evidence/claims beyond source URL reuse.

### Checkpoint 7 - NUSMods / Module Enrichment

- `[x]` NUS adapter exists.
- `[x]` Module DB query plugin exists.
- `[x]` Seed script exists.
- `[~]` Demo module evidence works.
- `[ ]` Backend calls module enrichment during capture or JD mapping.
- `[ ]` UI shows which skills came from modules versus user-attested experiences.

### Checkpoint 8 - Real MiroFlow Orchestration

- `[x]` Config and skill prompt files exist.
- `[~]` MiroMind client can call a model for graph JSON.
- `[ ]` Backend executes the MiroFlow graph from `config/pivotmap_agent.yaml`.
- `[ ]` Registered tools are called from agent stages.
- `[ ]` Trace events are generated by each real stage.
- `[ ]` Verifier handles conflicts and weak evidence explicitly.

### Checkpoint 9 - Optional Audio And Uploads

- `[ ]` Audio recording control.
- `[ ]` Audio upload endpoint.
- `[ ]` Whisper/transcription integration.
- `[ ]` Resume PDF/text upload.
- `[ ]` File parsing errors shown clearly in UI.

## Acceptance Test Checkpoints

### Voice/Text Yap

- `[x]` `/capture/voice` returns graph payload in demo mode.
- `[~]` Normal mode persists returned graph.
- `[ ]` Sample transcript produces 2-4 specific structured claims.
- `[ ]` Generated STAR bullets reference extracted claims.
- `[ ]` Unsupported claims are not marked `verified`.

### JD Targeting

- `[x]` `/target/jd` returns gap nodes in demo mode.
- `[x]` Demo fixture includes `matched`, `weak`, and `missing`.
- `[ ]` JD requirements link back to stored evidence or claim nodes after a previous capture run.
- `[ ]` Missing requirements include concrete roadmap actions.
- `[ ]` Live research failure shows `source unavailable`, not fake citations.

### Trace Panel

- `[x]` Trace events render in UI.
- `[x]` Demo fixture includes planner, verifier, and synthesiser.
- `[ ]` Normal live run emits planner, research, verifier, proof_mapper, and synthesiser events.
- `[ ]` Trace events are chronological and grouped by `run_id`.

### Persistence

- `[x]` First run creates graph nodes.
- `[x]` Repeated source URL does not crash persistence.
- `[x]` Graph retrieval returns confidence labels and source metadata.
- `[x]` Second JD targeting run reuses nodes from the first capture run as input.
- `[ ]` Persisted graph supports multiple runs without losing useful history.

### NUSMods Adapter

- `[x]` Adapter tests exist.
- `[x]` Module detail returns an `EvidenceNode`.
- `[ ]` Capture/JD flow invokes NUS module enrichment automatically.
- `[ ]` Adapter failure does not block the proof pipeline.

## Recommended Next Checkpoints

### Next 1 - Make JD Targeting Use Existing Graph

Goal: turn `/target/jd` from "generate a graph for this JD" into "load the user's existing graph, then map this JD against it."

Tasks:

- `[x]` In `target_jd`, call `load_graph_for_user(session, payload.user_id)` before MiroMind generation.
- `[x]` Pass existing evidence, claims, skills, and sources into the MiroMind payload.
- `[x]` Update prompt/system instructions to require linked evidence IDs in gap nodes.
- `[x]` Add a test: capture evidence, target JD, then assert gap nodes link to earlier evidence.

### Next 2 - Add A Deterministic Local Extractor

Goal: make the no-API fallback impressive instead of generic.

Tasks:

- `[ ]` Parse transcript/resume text into 2-4 claim candidates using simple patterns.
- `[ ]` Infer skills from keywords such as SQL, dashboards, analytics, experiments, stakeholder, Python.
- `[ ]` Generate confidence labels as `user-attested` or `weak` unless a known source/plugin supports them.
- `[ ]` Generate stronger local trace events: planner, verifier, synthesiser.

### Next 3 - Make MiroFlow Visible

Goal: judges should see why this is not a single LLM call.

Tasks:

- `[ ]` Create backend orchestration function with explicit stages: planner, research, verifier, proof_mapper, synthesiser.
- `[ ]` Emit one trace event per stage.
- `[ ]` Call `module_db_query` when a module code appears.
- `[ ]` Call `temporal_tagger` when source text/URLs are present.
- `[ ]` Add UI labels that distinguish `verified`, `supported`, `user-attested`, `weak`, and `missing`.

### Next 4 - STAR Bullet Contract

Goal: make resume output feel like the product promise.

Tasks:

- `[ ]` Add `resume_bullets` to API payload metadata or a dedicated response field.
- `[ ]` Include `claim_ids`, `confidence_status`, and `source_ids` per bullet.
- `[ ]` Render bullets with source-backed labels in the resume preview.
- `[ ]` Test that weak/user-attested bullets are not shown as fully verified.

### Next 5 - Demo Hardening

Goal: make the hackathon demo reliable.

Tasks:

- `[ ]` Add a "demo seed" button or script that creates one full graph for `demo-nus-business-y3`.
- `[ ]` Add backend startup log for `DEMO_MODE`, API key presence, and DB URL host.
- `[ ]` Add frontend empty/error states for backend unavailable.
- `[ ]` Add README demo script with exact commands.

## Cut For Hackathon

- `[ ]` Full Discovery Mode.
- `[ ]` Alumni career path scraping.
- `[ ]` SG market demand scoring.
- `[ ]` Club/society recommendation.
- `[ ]` Full semester-long memory beyond a simple persisted proof graph.
- `[ ]` Real GitHub/LinkedIn imports unless core flow finishes early.

## Hackathon Definition Of Done

PivotMap is demo-ready when this flow works repeatably:

1. User enters a project/transcript/resume note.
2. Backend extracts specific claims and confidence labels.
3. Evidence persists under the demo user.
4. User pastes a JD.
5. Backend loads existing proof graph and maps JD requirements to evidence.
6. UI shows matched, weak, and missing proof.
7. Trace panel shows planner, research/plugin, verifier, proof mapper, and synthesiser stages.
8. Resume preview shows source-backed bullets and gap actions.

That is the tight version of the pitch: PivotMap turns messy student evidence into a persistent proof graph, then uses MiroFlow to tell you which career claims will survive scrutiny.
