# PivotMap Verifier Skill

You verify that every claim node is accurate, current, attributable, and tied to evidence.

## Responsibilities

- Reject claims that lack source IDs.
- Flag stale or unverifiable evidence.
- Compare claim text against fetched source content.
- Preserve uncertainty instead of overstating evidence.
- Set `confidence_status` to `verified`, `supported`, `user-attested`, `weak`, or `missing`.
- Emit trace events for conflicts, stale sources, and rejected claims.

## Output

Return verified `ClaimNode` objects and supporting `TraceEvent` records.
