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
                        "content": _system_prompt(task),
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


def _system_prompt(task: str) -> str:
    """Return task-specific graph generation instructions."""
    base = (
        "Return only valid JSON shaped as a Career Proof Graph with keys "
        "user_id, sources, evidence_nodes, claim_nodes, skill_nodes, "
        "gap_nodes, and trace_events. Do not include markdown, prose, "
        "comments, or code fences."
    )
    if task != "target_jd":
        return base

    return (
        f"{base} For target_jd, use payload.existing_graph as the stored proof graph. "
        "Classify each JD requirement as matched, weak, or missing. Matched and weak "
        "gap_nodes must link to existing evidence_node.id values when stored proof "
        "supports the requirement. Missing gap_nodes must have empty linked_evidence_ids. "
        "Every weak or missing gap must include a concrete recommended_action."
    )


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
    if task == "target_jd":
        return _local_target_jd_graph(payload)

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


REQUIREMENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "python": ("python",),
    "sql": ("sql", "database", "query", "queries"),
    "dashboard": ("dashboard", "dashboards", "reporting"),
    "analytics": ("analytics", "analysis", "analytical", "metrics", "funnels"),
    "experiment": ("experiment", "experimentation", "a/b", "ab test", "test-and-learn"),
    "stakeholder": ("stakeholder", "stakeholders", "cross-functional", "presentation"),
    "visualization": ("visualization", "visualisation", "visualize", "visualise", "charts"),
    "product": ("product", "roadmap", "feature", "user problem"),
    "research": ("research", "user research", "market research", "interview"),
}


STRONG_CONFIDENCE = {"verified", "supported"}


def _local_target_jd_graph(payload: dict[str, Any]) -> dict[str, Any]:
    """Map a JD against stored proof graph context without live model access."""
    user_id = str(payload.get("user_id", "demo-user"))
    existing_graph = _normalise_existing_graph(user_id, payload.get("existing_graph"))
    run_id = f"run-{uuid4().hex[:8]}"
    now = datetime.now(UTC).isoformat()
    jd_text = str(payload.get("jd_text") or "")
    company = str(payload.get("company") or "Target role")
    job_source_id = f"source-jd-{uuid4().hex[:8]}"

    requirements = _extract_requirements(jd_text)
    gap_nodes = [
        _gap_for_requirement(
            user_id=user_id,
            target_role=company,
            requirement=requirement,
            existing_graph=existing_graph,
            job_source_id=job_source_id,
            now=now,
        )
        for requirement in requirements
    ]

    return {
        "user_id": user_id,
        "sources": [
            *existing_graph["sources"],
            {
                "id": job_source_id,
                "source_url": f"https://pivotmap.local/jd/{uuid4().hex[:12]}",
                "source_type": "job_post",
                "title": company,
                "published_at": None,
                "retrieved_at": now,
                "metadata": {"task": "target_jd", "source": "user_supplied_jd"},
            },
        ],
        "evidence_nodes": existing_graph["evidence_nodes"],
        "claim_nodes": existing_graph["claim_nodes"],
        "skill_nodes": existing_graph["skill_nodes"],
        "gap_nodes": gap_nodes,
        "trace_events": _target_jd_trace_events(user_id, run_id, now, requirements, gap_nodes),
    }


def _normalise_existing_graph(user_id: str, existing_graph: Any) -> dict[str, Any]:
    """Return a graph-shaped context object with expected collection keys."""
    graph = existing_graph if isinstance(existing_graph, dict) else {}
    return {
        "user_id": str(graph.get("user_id") or user_id),
        "sources": list(graph.get("sources") or []),
        "evidence_nodes": list(graph.get("evidence_nodes") or []),
        "claim_nodes": list(graph.get("claim_nodes") or []),
        "skill_nodes": list(graph.get("skill_nodes") or []),
        "gap_nodes": [],
        "trace_events": [],
    }


def _extract_requirements(jd_text: str) -> list[str]:
    """Extract deterministic requirement labels from a JD."""
    lowered = jd_text.casefold()
    requirements = [
        keyword
        for keyword, aliases in REQUIREMENT_KEYWORDS.items()
        if any(alias in lowered for alias in aliases)
    ]
    return requirements or ["target role evidence"]


def _gap_for_requirement(
    user_id: str,
    target_role: str,
    requirement: str,
    existing_graph: dict[str, Any],
    job_source_id: str,
    now: str,
) -> dict[str, Any]:
    """Create one deterministic gap node from stored proof matches."""
    strong_evidence_ids, weak_evidence_ids, matched_source_ids = _match_requirement(requirement, existing_graph)
    if strong_evidence_ids:
        status = "matched"
        linked_evidence_ids = strong_evidence_ids
        action = f"Use the stored {requirement} proof directly in the tailored resume bullet."
    elif weak_evidence_ids:
        status = "weak"
        linked_evidence_ids = weak_evidence_ids
        action = f"Strengthen {requirement} with a source-backed artifact, metric, or portfolio note."
    else:
        status = "missing"
        linked_evidence_ids = []
        action = f"Create or attach evidence that demonstrates {requirement} for this role."

    return {
        "id": f"gap-{uuid4().hex[:8]}",
        "user_id": user_id,
        "target_role": target_role,
        "requirement": requirement,
        "status": status,
        "recommended_action": action,
        "linked_evidence_ids": linked_evidence_ids,
        "source_ids": list(dict.fromkeys([job_source_id, *matched_source_ids])),
        "created_at": now,
    }


def _match_requirement(requirement: str, existing_graph: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    """Return strong/weak evidence IDs and supporting source IDs for a requirement."""
    aliases = REQUIREMENT_KEYWORDS.get(requirement, (requirement,))
    evidence_by_id = {node["id"]: node for node in existing_graph["evidence_nodes"] if "id" in node}
    strong: set[str] = set()
    weak: set[str] = set()
    source_ids: list[str] = []

    for claim in existing_graph["claim_nodes"]:
        evidence_id = claim.get("evidence_id")
        if not evidence_id or not _text_matches(claim.get("claim_text"), aliases):
            continue
        if claim.get("confidence_status") in STRONG_CONFIDENCE and float(claim.get("confidence_score", 0)) >= 0.7:
            strong.add(str(evidence_id))
        else:
            weak.add(str(evidence_id))
        source_ids.extend(str(source_id) for source_id in claim.get("source_ids", []))

    for evidence in existing_graph["evidence_nodes"]:
        evidence_id = evidence.get("id")
        if not evidence_id or not _text_matches(_node_text(evidence), aliases):
            continue
        weak.add(str(evidence_id))
        source_ids.extend(str(source_id) for source_id in evidence.get("source_ids", []))

    for skill in existing_graph["skill_nodes"]:
        if not _text_matches(skill.get("skill"), aliases):
            continue
        evidence_ids = [str(evidence_id) for evidence_id in skill.get("evidence_ids", [])]
        if float(skill.get("confidence_score", 0)) >= 0.7:
            strong.update(evidence_ids)
        else:
            weak.update(evidence_ids)
        for evidence_id in evidence_ids:
            source_ids.extend(str(source_id) for source_id in evidence_by_id.get(evidence_id, {}).get("source_ids", []))

    weak.difference_update(strong)
    return sorted(strong), sorted(weak), list(dict.fromkeys(source_ids))


def _text_matches(value: Any, aliases: tuple[str, ...]) -> bool:
    """Return whether any alias is present in a text value."""
    text = str(value or "").casefold()
    return any(alias in text for alias in aliases)


def _node_text(node: dict[str, Any]) -> str:
    """Return searchable text for an evidence-like node."""
    return " ".join(str(part) for part in [node.get("title"), node.get("description")] if part)


def _target_jd_trace_events(
    user_id: str,
    run_id: str,
    now: str,
    requirements: list[str],
    gap_nodes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return staged fallback trace events for JD targeting."""
    statuses = {status: sum(1 for gap in gap_nodes if gap["status"] == status) for status in ("matched", "weak", "missing")}
    return [
        _trace_event(user_id, run_id, "planner", f"Extracted {len(requirements)} JD requirement(s).", now),
        _trace_event(user_id, run_id, "proof_mapper", "Mapped requirements against stored evidence, claims, and skills.", now),
        _trace_event(
            user_id,
            run_id,
            "verifier",
            f"Classified gaps: {statuses['matched']} matched, {statuses['weak']} weak, {statuses['missing']} missing.",
            now,
        ),
        _trace_event(user_id, run_id, "synthesiser", "Returned JD gaps with evidence links and roadmap actions.", now),
    ]


def _trace_event(user_id: str, run_id: str, stage: str, message: str, now: str) -> dict[str, Any]:
    """Build a trace event."""
    return {
        "id": f"trace-{uuid4().hex[:8]}",
        "user_id": user_id,
        "run_id": run_id,
        "stage": stage,
        "message": message,
        "created_at": now,
        "metadata": {"model": MODEL_NAME, "mode": "local_fallback"},
    }
