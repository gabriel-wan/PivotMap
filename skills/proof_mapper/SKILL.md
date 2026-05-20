# PivotMap Proof Mapper Skill

You receive verified `VerifiedSkillClaim` objects and `StudentEvidence`, then map them into proof nodes.

## Responsibilities

- For each `JDRequirement`, inspect the corresponding verified skill claims and student evidence.
- Classify the proof state as `matched`, `weak`, or `missing`.
- Use `matched` when the student has strong, direct evidence for the requirement.
- Use `weak` when evidence exists but is indirect, old, underspecified, or low confidence.
- Use `missing` when no credible evidence proves the requirement.
- Add `gap_action` for weak or missing requirements, pointing to concrete modules, certifications, projects, or portfolio actions.
- Add `resume_bullet` when evidence can be translated into a truthful resume bullet.
- Preserve source provenance from `VerifiedSkillClaim.sources`.

## Input

Accept `list[VerifiedSkillClaim]`, `list[JDRequirement]`, and `list[StudentEvidence]`.

## Output

Return `ProofNode` objects with `requirement`, `status`, `evidence`, `gap_action`, `resume_bullet`, and `sources`.
