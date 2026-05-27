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
    graph = _demo_graph(payload.user_id) if _demo_mode() else await MiroMindClient().generate_graph(
        "target_jd",
        payload.model_dump(),
    )
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
