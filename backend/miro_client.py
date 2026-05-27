"""MiroMind API client for Career Proof Graph generation."""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

MODEL_NAME = "mirothinker-1-7-deepresearch-mini"
BASE_URL = "https://api.miromind.ai/v1"
logger = logging.getLogger("pivotmap.miromind")


class MiroMindClient:
    """Thin AsyncOpenAI wrapper configured for the MiroMind API."""

    def __init__(self, api_key: str | None = None) -> None:
        """Create a client from `MIROMIND_API_KEY` unless explicitly supplied."""
        self.api_key = api_key or os.getenv("MIROMIND_API_KEY")

    async def generate_graph(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Generate a Career Proof Graph payload for a backend task."""
        log_task = _log_task_name(task)
        logger.info("calling_miromind_%s payload_chars=%s", log_task, _payload_size(payload))

        if not self.api_key:
            logger.warning("miromind_%s_failed_fallback reason=missing_api_key", log_task)
            return _local_graph(task, payload)

        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            logger.warning("miromind_%s_failed_fallback reason=openai_import_error error=%s", log_task, type(exc).__name__)
            return _local_graph(task, payload)

        try:
            client = AsyncOpenAI(api_key=self.api_key, base_url=BASE_URL, timeout=60.0, max_retries=1)
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return only valid JSON shaped as a Career Proof Graph with keys "
                            "user_id, sources, evidence_nodes, claim_nodes, skill_nodes, "
                            "gap_nodes, and trace_events. Do not include markdown, prose, "
                            "comments, or code fences."
                        ),
                    },
                    {"role": "user", "content": json.dumps({"task": task, "payload": payload})},
                ],
                temperature=0.2,
            )
            content = _extract_response_content(response)
            graph = _parse_json_content(content)
            logger.info(
                "miromind_%s_success response_chars=%s source=%s",
                log_task,
                len(content),
                "sse" if isinstance(response, str) else "object",
            )
            return graph
        except Exception as exc:
            logger.warning("miromind_%s_failed_fallback error=%s", log_task, type(exc).__name__)
            return _local_graph(task, payload)


def _log_task_name(task: str) -> str:
    """Return a stable task label for safe logging."""
    return {
        "capture_voice": "capture_voice",
        "capture_resume": "capture_resume",
        "target_jd": "target_jd",
    }.get(task, "unknown")


def _payload_size(payload: dict[str, Any]) -> int:
    """Return payload size without logging the payload itself."""
    return len(json.dumps(payload, default=str))


def _extract_response_content(response: Any) -> str:
    """Extract assistant content from OpenAI objects or MiroMind SSE-style strings."""
    if isinstance(response, str):
        chunks: list[str] = []
        for raw_line in response.splitlines():
            line = raw_line.strip()
            if not line.startswith("data:"):
                continue
            data = line.removeprefix("data:").strip()
            if not data or data == "[DONE]":
                continue
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            for choice in event.get("choices", []):
                delta = choice.get("delta") or {}
                message = choice.get("message") or {}
                chunks.extend(_content_chunks(delta))
                chunks.extend(_content_chunks(message))
        return "".join(chunks).strip() or response.strip()

    choices = getattr(response, "choices", None)
    if choices:
        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content.strip()

    return str(response).strip()


def _parse_json_content(content: str) -> dict[str, Any]:
    """Parse JSON content, accepting fenced or prose-wrapped JSON."""
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(_first_json_object(text))


def _content_chunks(container: dict[str, Any]) -> list[str]:
    """Return assistant answer chunks from a MiroMind/OpenAI delta-like object."""
    chunks: list[str] = []
    for key in ("content", "text", "answer", "output"):
        value = container.get(key)
        if isinstance(value, str):
            chunks.append(value)
    return chunks


def _first_json_object(text: str) -> str:
    """Extract the first balanced JSON object from model text."""
    start = text.find("{")
    if start < 0:
        raise json.JSONDecodeError("No JSON object found", text, 0)

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise json.JSONDecodeError("Unterminated JSON object", text, start)


def _local_graph(task: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic graph data when live MiroMind access is unavailable."""
    user_id = str(payload.get("user_id", "demo-user"))
    run_id = f"run-{uuid4().hex[:8]}"
    now = datetime.now(UTC).isoformat()
    evidence_id = f"evidence-{uuid4().hex[:8]}"
    claim_id = f"claim-{uuid4().hex[:8]}"
    skill_id = f"skill-{uuid4().hex[:8]}"
    gap_id = f"gap-{uuid4().hex[:8]}"
    source_id = f"source-{uuid4().hex[:8]}"
    text = str(payload.get("transcript") or payload.get("resume_text") or payload.get("jd_text") or "")
    title = "Captured career evidence" if task != "target_jd" else "Target role requirement"
    return {
        "user_id": user_id,
        "sources": [
            {
                "id": source_id,
                "source_url": "https://pivotmap.local/demo",
                "source_type": "voice" if task == "capture_voice" else "resume",
                "title": title,
                "published_at": now,
                "retrieved_at": now,
                "metadata": {"task": task},
            }
        ],
        "evidence_nodes": [
            {
                "id": evidence_id,
                "user_id": user_id,
                "kind": "voice" if task == "capture_voice" else "resume",
                "title": title,
                "description": text[:240] or "No description supplied.",
                "source_ids": [source_id],
                "created_at": now,
                "metadata": {"task": task},
            }
        ],
        "claim_nodes": [
            {
                "id": claim_id,
                "evidence_id": evidence_id,
                "claim_text": "User supplied evidence that can be mapped into career proof.",
                "confidence_status": "user-attested",
                "confidence_score": 0.62,
                "source_ids": [source_id],
                "created_at": now,
            }
        ],
        "skill_nodes": [
            {
                "id": skill_id,
                "user_id": user_id,
                "skill": "career evidence articulation",
                "category": "communication",
                "confidence_score": 0.62,
                "evidence_ids": [evidence_id],
                "claim_ids": [claim_id],
                "created_at": now,
            }
        ],
        "gap_nodes": [
            {
                "id": gap_id,
                "user_id": user_id,
                "target_role": str(payload.get("company") or "Target role"),
                "requirement": "Add more source-backed evidence for the target JD.",
                "status": "weak",
                "recommended_action": "Attach a portfolio artifact or module source to strengthen this proof.",
                "linked_evidence_ids": [evidence_id],
                "source_ids": [source_id],
                "created_at": now,
            }
        ],
        "trace_events": [
            {
                "id": f"trace-{uuid4().hex[:8]}",
                "user_id": user_id,
                "run_id": run_id,
                "stage": "miromind_fallback",
                "message": f"Generated deterministic local graph for {task}.",
                "created_at": now,
                "metadata": {"model": MODEL_NAME},
            }
        ],
    }
