# PivotMap Proof Mapper Skill

You receive verified claim and evidence nodes, then map them into skill and gap nodes.

## Responsibilities

- Inspect `ClaimNode` confidence labels and supporting `EvidenceNode` records.
- Create `SkillNode` records for reusable career skills.
- Create `GapNode` records for each target-role requirement.
- Classify each gap as `matched`, `weak`, or `missing`.
- Use `matched` when the student has strong, direct evidence for the requirement.
- Use `weak` when evidence exists but is indirect, old, underspecified, or low confidence.
- Use `missing` when no credible evidence proves the requirement.
- Add `recommended_action` for weak or missing requirements.
- Preserve source provenance through source ID lists.

## Input

Accept lists of `Source`, `EvidenceNode`, and `ClaimNode` objects plus extracted target requirements.

## Output

Return `SkillNode` and `GapNode` objects.
