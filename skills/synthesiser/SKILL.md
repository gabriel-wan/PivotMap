# PivotMap Synthesiser Skill

You assemble verified evidence into a PivotMap Career Proof Graph.

## Responsibilities

- Emit `Source`, `EvidenceNode`, `ClaimNode`, `SkillNode`, `GapNode`, and `TraceEvent` objects.
- Link claims to evidence and skills to claims using stable IDs.
- Classify each target-role requirement as a `GapNode` with `matched`, `weak`, or `missing` status.
- Cite every external source through `Source` IDs.
- Produce trace events for planner, research, verifier, proof mapping, and synthesis steps.
- Keep the output aligned with `schemas/roadmap-schema.json`.

## Output

Return a Career Proof Graph JSON payload with `sources`, `evidence_nodes`, `claim_nodes`, `skill_nodes`, `gap_nodes`, and `trace_events`.
