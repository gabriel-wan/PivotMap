"""FastAPI backend for PivotMap analysis requests."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from schemas.interfaces import ProofGraph

app = FastAPI(title="PivotMap API")


class AnalyseRequest(BaseModel):
    """Request payload for JD and student profile analysis."""

    jd_text: str = Field(..., min_length=1)
    student_profile: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict[str, str]:
    """Return backend health status."""
    return {"status": "ok"}


@app.post("/api/analyse")
def analyse(payload: AnalyseRequest) -> dict[str, Any]:
    """Analyse a JD and student profile into a serialized ProofGraph."""
    if os.getenv("DEMO_MODE", "false").casefold() == "true":
        return _load_demo_graph()

    graph = _run_miroflow_agent(payload.jd_text, payload.student_profile)
    return _serialize_graph(graph)


def _run_miroflow_agent(jd_text: str, student_profile: dict[str, Any]) -> ProofGraph | dict[str, Any]:
    """Invoke the MiroFlow graph, with a deterministic scaffold fallback."""
    try:
        from miroflow import run_agent_graph
    except ImportError:
        graph = _load_demo_graph()
        graph["jd_text"] = jd_text
        graph["user_id"] = str(student_profile.get("user_id", graph["user_id"]))
        return graph

    return run_agent_graph(
        config_path="config/pivotmap_agent.yaml",
        inputs={
            "jd_text": jd_text,
            "student_profile": student_profile,
        },
    )


def _load_demo_graph() -> dict[str, Any]:
    """Load the pre-computed demo fixture."""
    fixture_path = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "mock_proof_graph.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def _serialize_graph(graph: ProofGraph | dict[str, Any]) -> dict[str, Any]:
    """Serialize a ProofGraph dataclass or graph-like dictionary to JSON data."""
    if isinstance(graph, dict):
        return graph
    if is_dataclass(graph):
        return _json_safe(asdict(graph))
    raise TypeError(f"Expected ProofGraph or dict, got {type(graph)!r}")


def _json_safe(value: Any) -> Any:
    """Convert dataclass output into JSON-safe primitives."""
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value
