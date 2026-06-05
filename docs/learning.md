# Learning Skill

Use this playbook when a confusing, annoying, or "why did this break?" problem happens in PivotMap and the user wants to learn the workflow or concept behind the fix.

## Goal

Turn debugging moments into detailed, reusable learning notes in `docs/insights.md`.

The note should help the user understand:

- what failed
- why it failed
- how we diagnosed it
- what fixed it
- what concept or mental model explains it
- what pattern to remember next time

## When To Use

Use this when:

- CI, Docker, dev server, Git, dependency, branch, or deployment behavior is confusing
- an error message points to an environment or workflow issue
- the user says something like "why did this happen?", "what did we learn?", "add this to insights", or "dumb shit problem"
- a fix reveals a repeatable concept worth remembering

## Workflow

1. Capture the symptom in plain language.
2. Identify the actual root cause, not just the surface error.
3. Explain the workflow concept involved.
4. Record the exact diagnosis path: commands, files, logs, and observations.
5. Explain why the fix works, not only what changed.
6. Add or update an entry in `docs/insights.md`.
7. Keep the entry readable, but do not compress away the concept.

Good entries should answer: "If I see this class of problem again, what should I understand sooner?"

## How This Became A Local Codex Skill

There are two related things here:

- `docs/learning.md`: a project-local playbook that lives inside PivotMap.
- `C:\Users\kalen\.codex\skills\learning\SKILL.md`: a local Codex skill that can be reused across projects.

The project file is for humans and repo history. The local skill is for Codex discovery.

### 1. Find the local skills folder

Codex local skills live under:

```text
C:\Users\kalen\.codex\skills
```

Existing system skills live under:

```text
C:\Users\kalen\.codex\skills\.system
```

We checked that folder first to make sure a `learning` skill did not already exist.

### 2. Use the skill creator template

Instead of hand-making a random folder, use the skill creator script:

```powershell
C:\Users\kalen\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  C:\Users\kalen\.codex\skills\.system\skill-creator\scripts\init_skill.py `
  learning `
  --path C:\Users\kalen\.codex\skills `
  --interface display_name=Learning `
  --interface short_description="Capture debugging lessons into project insights" `
  --interface default_prompt="Distill this debugging/workflow issue into a concise learning note and append it to the project insights file."
```

This created:

```text
C:\Users\kalen\.codex\skills\learning\
|-- SKILL.md
`-- agents\openai.yaml
```

### 3. Write the required `SKILL.md`

Every skill needs a `SKILL.md` with YAML frontmatter:

```md
---
name: learning
description: Distill confusing debugging, CI, Docker, Git, dependency, environment, deployment, or workflow problems into concise learning notes. Use when the user asks to learn from an issue, add something to insights, capture a debugging lesson, explain a dumb/annoying problem, or preserve the workflow/concept behind a fix.
---
```

The important part is the `description`. Codex uses that metadata to decide when the skill should trigger.

Then the body explains the behavior:

- prefer the active project's `docs/insights.md`
- create `docs/` or `insights.md` if missing
- append a dated learning note
- explain the concept behind the fix
- keep notes detailed enough to be useful later

### 4. Validate the skill

After writing the skill, run:

```powershell
C:\Users\kalen\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  C:\Users\kalen\.codex\skills\.system\skill-creator\scripts\quick_validate.py `
  C:\Users\kalen\.codex\skills\learning
```

Expected output:

```text
Skill is valid!
```

### 5. The UTF-8 BOM gotcha

The first validation failed with:

```text
No YAML frontmatter found
```

The file visually started with `---`, but it actually had hidden UTF-8 BOM bytes before the frontmatter:

```text
b'\xef\xbb\xbf---\nname: lea'
```

That made the validator miss the YAML block. The fix was to rewrite the file as UTF-8 without BOM:

```powershell
C:\Users\kalen\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -c "from pathlib import Path; p=Path(r'C:\Users\kalen\.codex\skills\learning\SKILL.md'); text=p.read_text(encoding='utf-8-sig'); p.write_text(text, encoding='utf-8')"
```

After that, validation passed.

### 6. How To Use It Later

In a future Codex session, say:

- `use learning`
- `add this to insights`
- `distill this into a learning point`
- `capture what we learned from this CI issue`

Codex should then append a note to the current repo's `docs/insights.md`.

If the skill does not show up immediately, restart the Codex session. Newly added local skills may only be discovered on a fresh session.

## Insight Format

Append entries using this shape:

```md
## YYYY-MM-DD - Short Title

**Context:** What the user was trying to do.

**Surface Symptom:** What looked broken.

**Concept / Mental Model:** The underlying concept that explains the behavior.

**Root Cause:** What was actually wrong.

**Diagnosis Path:** The key checks that revealed the issue.

**Fix:** The concrete change or command.

**Why The Fix Works:** Why that change addresses the real cause.

**How To Verify:** The command, test, UI behavior, or log that proves it is fixed.

**Preventive Rule:** The reusable rule of thumb.

**Related Files / Commands:** Exact paths and commands worth remembering.
```

Use `Unknowns / Next Checks` if the issue is not fully diagnosed yet:

```md
**Unknowns / Next Checks:** What still needs to be inspected before calling this solved.
```

## Writing Style

- Be direct and non-judgmental.
- Prefer exact paths, commands, and filenames.
- Include the original error message if it is short and useful.
- Avoid dumping long logs.
- Break down the concept behind the error, especially for CI, Docker, databases, Git, dependency resolution, and dev-server caching.
- Distinguish local machine behavior from Docker/container behavior when relevant.
- Distinguish generated IDs from natural unique keys when explaining database bugs.
- Distinguish symptoms from causes. A failed pytest job may actually be a missing directory, not a test failure.
- Make the learning point portable to future projects.

## Example

```md
## 2026-05-27 - CI Working Directory Mismatch

**Context:** A GitHub Actions pytest job was added for PivotMap.

**Surface Symptom:** GitHub Actions failed before pytest started.

**Concept / Mental Model:** `actions/checkout` places the repository at `$GITHUB_WORKSPACE`. A workflow-level `defaults.run.working-directory` is prepended to every shell `run:` step. If that folder does not exist, the shell cannot start, so the command never runs.

**Root Cause:** The workflow set `working-directory: pivotmap`, but the repo checkout already landed at the project root.

**Diagnosis Path:** The error said the runner could not find `/home/runner/work/PivotMap/PivotMap/pivotmap`. The repo layout showed `tests/` at the root, not inside a nested `pivotmap/` folder.

**Fix:** Remove the invalid default working directory from `.github/workflows/ci.yml`.

**Why The Fix Works:** The install and pytest commands now start from the actual checkout root, where `tests/` exists.

**How To Verify:** Rerun the workflow and confirm it reaches the pytest command instead of failing while starting `/usr/bin/bash`.

**Preventive Rule:** In GitHub Actions, only set `working-directory` when your repo truly has a nested app folder.

**Related Files / Commands:** `.github/workflows/ci.yml`, `pytest tests/`.
```
