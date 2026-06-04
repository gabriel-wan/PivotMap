"""PivotMap MiroFlow agent-graph entry point.

This module hosts the `trace` smoke test for the MiroFlow agent-graph skeleton
(issue #1). `trace` loads the declarative agent graph in
``config/pivotmap_agent.yaml``, verifies every referenced ``SKILL.md`` is present
and parseable, then walks the nodes with a dummy task while emitting ordered
trace events. It performs no live LLM calls, so it is safe to run without any
API keys configured.

Usage:
    uv run main.py trace
    uv run main.py trace --config config/pivotmap_agent.yaml --task "map a JD"

Exit codes:
    0  graph loaded and all skills present/parseable
    1  config missing/invalid, or one or more SKILL.md files missing/unparseable
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config" / "pivotmap_agent.yaml"
DEFAULT_TASK = "dummy task: map a sample product-analyst JD against stored proof"


def _load_env() -> None:
    """Load a local ``.env`` file when python-dotenv is available (no-op otherwise)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(ROOT / ".env")


def _miroflow_available() -> bool:
    """Return whether the MiroFlow framework is installed in this environment.

    MiroFlow ships as the ``run-agent`` distribution, so we probe its package
    metadata rather than importing it (its top-level ``src`` module is heavy and
    not needed for this skeleton smoke test).
    """
    from importlib.metadata import PackageNotFoundError, version

    try:
        version("run-agent")
        return True
    except PackageNotFoundError:
        return False


def load_graph(config_path: Path) -> dict[str, Any]:
    """Parse and minimally validate the agent-graph YAML config."""
    if not config_path.exists():
        raise FileNotFoundError(f"agent graph config not found: {config_path}")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("agent_graph"), dict):
        raise ValueError(f"{config_path} is missing a valid 'agent_graph' section")
    if not isinstance(data["agent_graph"].get("nodes"), dict):
        raise ValueError(f"{config_path} 'agent_graph' has no 'nodes' mapping")
    return data


def _node_order(graph: dict[str, Any]) -> list[str]:
    """Return node names in pipeline order (YAML insertion order is the wired order)."""
    return list(graph["agent_graph"]["nodes"].keys())


def check_skills(graph: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Validate that every node's SKILL.md exists and is parseable.

    A skill file is considered parseable when it is non-empty and contains at
    least one Markdown heading. Returns ``(ok_skills, problems)``.
    """
    nodes: dict[str, Any] = graph["agent_graph"]["nodes"]
    ok_skills: list[str] = []
    problems: list[str] = []
    for name, node in nodes.items():
        skill_rel = (node or {}).get("skill")
        if not skill_rel:
            problems.append(f"{name}: node has no 'skill' path")
            continue
        skill_path = ROOT / skill_rel
        if not skill_path.exists():
            problems.append(f"{name}: missing skill file {skill_rel}")
            continue
        text = skill_path.read_text(encoding="utf-8").strip()
        if not text or not any(line.lstrip().startswith("#") for line in text.splitlines()):
            problems.append(f"{name}: {skill_rel} is empty or has no Markdown heading")
            continue
        ok_skills.append(skill_rel)
    return ok_skills, problems


def trace(config: str | None = None, task: str = DEFAULT_TASK) -> int:
    """Run the agent-graph smoke test and return a process exit code."""
    _load_env()
    config_path = Path(config) if config else DEFAULT_CONFIG

    print("PivotMap agent-graph trace")
    print("=" * 60)
    print(f"config:   {config_path}")
    print(f"task:     {task}")
    print(f"miroflow: {'available' if _miroflow_available() else 'not installed (skeleton mode)'}")
    print("-" * 60)

    try:
        graph = load_graph(config_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    agent_graph = graph["agent_graph"]
    root = agent_graph.get("root", "<unset>")
    order = _node_order(graph)
    print(f"root:     {root}")
    print(f"nodes:    {len(order)} ({' -> '.join(order)})")

    ok_skills, problems = check_skills(graph)
    print(f"skills:   {len(ok_skills)} present and parseable")
    print("-" * 60)

    # Walk the nodes with the dummy task, emitting ordered trace events.
    nodes: dict[str, Any] = agent_graph["nodes"]
    for index, name in enumerate(order, start=1):
        node = nodes[name] or {}
        detail = node.get("output") or node.get("classification") or node.get("tools") or "ok"
        print(f"[{index}/{len(order)}] {name:<16} -> {detail}")

    print("-" * 60)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        print(f"trace FAILED: {len(problems)} skill problem(s)", file=sys.stderr)
        return 1

    print(f"trace OK: dummy task walked {len(order)} nodes with all skills valid")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser for the agent-graph entry point."""
    parser = argparse.ArgumentParser(prog="main.py", description="PivotMap agent-graph CLI.")
    sub = parser.add_subparsers(dest="command", required=True)
    trace_cmd = sub.add_parser("trace", help="Smoke-test the agent graph with a dummy task.")
    trace_cmd.add_argument("--config", default=None, help="Path to the agent graph YAML config.")
    trace_cmd.add_argument("--task", default=DEFAULT_TASK, help="Dummy task description for the trace.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and dispatch to the requested command."""
    args = build_parser().parse_args(argv)
    if args.command == "trace":
        return trace(config=args.config, task=args.task)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
