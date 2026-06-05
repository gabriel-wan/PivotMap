"""FastAPI entrypoint for the PivotMap Career Proof Graph API."""

from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.db import get_session
from backend.miro_client import MODEL_NAME, MiroMindClient
from backend.repository import graph_payload, load_graph_for_user, store_graph

logger = logging.getLogger("pivotmap.backend")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Log safe runtime configuration for demo/live debugging."""
    demo_mode = _demo_mode()
    logger.info(
        "pivotmap_startup DEMO_MODE=%s MIROMIND_API_KEY_present=%s model=%s mode=%s",
        os.getenv("DEMO_MODE", "false"),
        bool(os.getenv("MIROMIND_API_KEY")),
        MODEL_NAME,
        "fixture" if demo_mode else "live",
    )
    yield


app = FastAPI(title="PivotMap Career Proof Graph API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VoiceCaptureRequest(BaseModel):
    """Request body for text-first voice capture."""

    user_id: str = Field(..., min_length=1)
    transcript: str = Field(..., min_length=1)


class ResumeCaptureRequest(BaseModel):
    """Request body for resume capture."""

    user_id: str = Field(..., min_length=1)
    resume_text: str = Field(..., min_length=1)


class JDTargetRequest(BaseModel):
    """Request body for JD targeting."""

    user_id: str = Field(..., min_length=1)
    jd_text: str = Field(..., min_length=1)
    company: str | None = None
    student_profile: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict[str, str]:
    """Return backend health status."""
    return {"status": "ok"}


@app.post("/capture/voice")
async def capture_voice(
    payload: VoiceCaptureRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Capture a transcript into Career Proof Graph nodes."""
    graph = _demo_graph(payload.user_id) if _demo_mode() else await MiroMindClient().generate_graph(
        "capture_voice",
        payload.model_dump(),
    )
    return _persist_unless_demo(session, graph)


@app.post("/capture/resume")
async def capture_resume(
    payload: ResumeCaptureRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Capture resume text into Career Proof Graph nodes."""
    graph = _demo_graph(payload.user_id) if _demo_mode() else await MiroMindClient().generate_graph(
        "capture_resume",
        payload.model_dump(),
    )
    return _persist_unless_demo(session, graph)


@app.post("/target/jd")
async def target_jd(
    payload: JDTargetRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Map a target job description against the user's proof graph."""
    if _demo_mode():
        graph = _demo_graph(payload.user_id)
    else:
        existing_graph = load_graph_for_user(session, payload.user_id)
        model_payload = payload.model_dump()
        model_payload["existing_graph"] = _targeting_context(existing_graph)
        generated_graph = await MiroMindClient().generate_graph("target_jd", model_payload)
        graph = _targeting_response(payload.user_id, existing_graph, generated_graph)
    return _persist_unless_demo(session, graph)


@app.get("/graph/{user_id}")
def get_graph(user_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return all Career Proof Graph nodes for a user."""
    if _demo_mode():
        return _demo_graph(user_id)
    return load_graph_for_user(session, user_id)


def _persist_unless_demo(session: Session, graph: dict[str, Any]) -> dict[str, Any]:
    """Persist normal-mode graph output while keeping demo mode immediate."""
    if _demo_mode():
        return graph
    store_graph(session, graph)
    return graph


def _demo_mode() -> bool:
    """Return whether deterministic demo mode is enabled."""
    return os.getenv("DEMO_MODE", "false").casefold() == "true"


def _demo_graph(user_id: str = "demo-nus-business-y3") -> dict[str, Any]:
    """Load the Career Proof Graph demo fixture."""
    fixture_path = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "demo_proof_graph.json"
    if fixture_path.exists():
        graph = json.loads(fixture_path.read_text(encoding="utf-8"))
        return _with_user_id(graph, user_id)
    return graph_payload(user_id=user_id)


def _with_user_id(graph: dict[str, Any], user_id: str) -> dict[str, Any]:
    """Return demo graph data with a consistent requested user ID."""
    graph["user_id"] = user_id
    for collection in ["evidence_nodes", "skill_nodes", "gap_nodes", "trace_events"]:
        for node in graph.get(collection, []):
            node["user_id"] = user_id
    return graph


def _targeting_context(existing_graph: dict[str, Any]) -> dict[str, Any]:
    """Return stored proof nodes relevant to a fresh JD mapping run."""
    return graph_payload(
        user_id=str(existing_graph["user_id"]),
        sources=existing_graph.get("sources", []),
        evidence_nodes=existing_graph.get("evidence_nodes", []),
        claim_nodes=existing_graph.get("claim_nodes", []),
        skill_nodes=existing_graph.get("skill_nodes", []),
        gap_nodes=[],
        trace_events=[],
    )


def _targeting_response(
    user_id: str,
    existing_graph: dict[str, Any],
    generated_graph: dict[str, Any],
) -> dict[str, Any]:
    """Combine stored proof context with only the new JD run outputs."""
    return graph_payload(
        user_id=user_id,
        sources=_dedupe_by_id(
            [
                *existing_graph.get("sources", []),
                *generated_graph.get("sources", []),
            ]
        ),
        evidence_nodes=_dedupe_by_id(
            [
                *existing_graph.get("evidence_nodes", []),
                *generated_graph.get("evidence_nodes", []),
            ]
        ),
        claim_nodes=_dedupe_by_id(
            [
                *existing_graph.get("claim_nodes", []),
                *generated_graph.get("claim_nodes", []),
            ]
        ),
        skill_nodes=_dedupe_by_id(
            [
                *existing_graph.get("skill_nodes", []),
                *generated_graph.get("skill_nodes", []),
            ]
        ),
        gap_nodes=generated_graph.get("gap_nodes", []),
        trace_events=generated_graph.get("trace_events", []),
    )


def _dedupe_by_id(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate graph nodes by ID while preserving first-seen order."""
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for node in nodes:
        node_id = str(node.get("id", ""))
        if not node_id or node_id in seen:
            continue
        seen.add(node_id)
        deduped.append(node)
    return deduped
