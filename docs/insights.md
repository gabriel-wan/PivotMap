# PivotMap Insights

Short learning notes from real debugging and workflow problems.

## 2026-05-27 - CI Working Directory Mismatch

**Context:** A GitHub Actions pytest workflow was running after commits were cherry-picked into the frontend branch and pushed for PR merge checks.

**Surface Symptom:** The `pytest` job failed during `Install test dependencies` before pytest actually ran. The important log line was:

```text
Error: An error occurred trying to start process '/usr/bin/bash' with working directory '/home/runner/work/PivotMap/PivotMap/pivotmap'. No such file or directory
```

**Concept / Mental Model:** `actions/checkout` checks the repository into `$GITHUB_WORKSPACE`, which usually looks like `/home/runner/work/<repo>/<repo>`. That path is already the repository root. A workflow-level `defaults.run.working-directory` applies to every shell `run:` step, but not to `uses:` steps such as `actions/checkout` or `actions/setup-python`. If the configured working directory does not exist, GitHub Actions cannot even start the shell process.

**Root Cause:** `.github/workflows/ci.yml` set the default working directory to `pivotmap`, so each shell step tried to start inside `$GITHUB_WORKSPACE/pivotmap`. In CI, the repo files were already at `$GITHUB_WORKSPACE`; there was no nested `pivotmap/` directory. This was a path/bootstrap failure, not a pytest failure.

**Diagnosis Path:** The failure happened in `Install test dependencies`, where the command was only `python -m pip install --upgrade pip pytest`. Since that command does not depend on project files, the clue was the shell startup path, not Python packaging. The repo layout showed `tests/`, `schemas/`, `adapters/`, and `plugins/` at the repository root, confirming that the CI workflow was pointing one directory too deep.

**Fix:** Remove the invalid default working directory from `.github/workflows/ci.yml` so dependency installation and `pytest tests/` run from the checkout root.

**Why The Fix Works:** With no incorrect default working directory, GitHub Actions starts each shell step from `$GITHUB_WORKSPACE`, where the repository actually exists. The job can now install dependencies and reach the pytest command.

**How To Verify:** Rerun the GitHub Actions job. The failure should move past shell startup and either run `python -m pip install --upgrade pip pytest` successfully or reveal a real dependency/test problem. Locally, confirm the test folder is at the repo root with `Get-ChildItem` and run `pytest tests/` from the same level.

**Preventive Rule:** Only set `working-directory` in GitHub Actions when the application truly lives in a nested folder. If the repo root contains the test/config files, let the workflow run from the root.

**Related Files / Commands:** `.github/workflows/ci.yml`, `pytest tests/`, `python -m pip install --upgrade pip pytest`.

## 2026-05-28 - Idempotent Persistence For Unique URLs

**Context:** The backend was persisting proof graph data from `/capture/voice`. Because the MiroFlow API key was missing, the app used its local fallback graph generation path.

**Surface Symptom:** Repeated `/capture/voice` calls crashed with a 500 error. Postgres logged:

```text
duplicate key value violates unique constraint "sources_source_url_key"
DETAIL: Key (source_url)=(https://pivotmap.local/demo) already exists.
```

**Concept / Mental Model:** A database table can have a surrogate primary key and a natural unique key. In `sources`, `id` is the generated surrogate key, while `source_url` is the natural key that says "this URL should exist only once." SQLAlchemy `session.merge()` works by primary key identity. It does not automatically know that two rows with different generated IDs but the same `source_url` are the same logical source. Idempotent persistence means processing the same logical input repeatedly should reuse existing rows or update them, not crash or duplicate data.

**Root Cause:** The fallback graph produced a fresh source ID on each run, such as `source-b7d50862`, while reusing the same demo URL, `https://pivotmap.local/demo`. `store_graph()` merged by the new primary key, so SQLAlchemy attempted an insert. Postgres correctly rejected it because `sources.source_url` is unique and the URL already existed.

**Diagnosis Path:** The traceback pointed to `store_graph()` during `session.commit()`, specifically an `INSERT INTO sources`. The DB error named the unique constraint `sources_source_url_key`, so the conflict was on `source_url`, not `id`. The fallback log `reason=missing_api_key` explained why the same deterministic demo URL kept being generated. Reading the persistence path showed that source IDs are also stored in JSON `source_ids` arrays on evidence, claim, and gap nodes, which means reusing an existing source row also requires remapping references.

**Fix:** Make `store_graph()` upsert sources by `source_url`. If a source URL already exists, reuse the persisted source row ID. Then remap incoming `source_ids` across evidence, claim, and gap nodes before saving them, and mutate the returned graph so API responses refer to the canonical source ID.

**Why The Fix Works:** The database now treats `source_url` as the identity for source reuse. Repeated fallback calls become idempotent: the same demo source URL maps to the same stored source row instead of trying to create a duplicate. Remapping keeps graph references coherent, so `load_graph_for_user()` can find source rows by the IDs stored inside node metadata.

**How To Verify:** Run the backend tests in Docker:

```powershell
docker exec pivotmap-backend-1 python -m pytest tests
```

The repository tests passed with `14 passed`, including the repeated-source case. Then restart the backend and check the health endpoint:

```powershell
docker restart pivotmap-backend-1
curl http://127.0.0.1:8000/health
```

The expected response is `{"status":"ok"}`.

**Preventive Rule:** When a table has a natural unique key such as `source_url`, write repository logic around that key. Generated IDs are good internal row handles, but they are not always the right identity for idempotent writes.

**Related Files / Commands:** `backend/repository.py`, `tests/test_repository.py`, `backend/miro_client.py`, `docker exec pivotmap-backend-1 python -m pytest tests`.

## 2026-05-28 - Docker Compose Env File Location

**Context:** The backend still logged `miromind_capture_voice_failed_fallback reason=missing_api_key` even after the MiroMind API key was added to an env file.

**Surface Symptom:** The user had already added the API key, but backend logs still showed:

```text
miromind_capture_voice_failed_fallback reason=missing_api_key
miromind_target_jd_failed_fallback reason=missing_api_key
```

**Concept / Mental Model:** Docker Compose automatically reads a file named `.env` from the same directory as `docker-compose.yml`. That file is used for variable substitution such as `${MIROMIND_API_KEY:-}`. A nested file like `tests/.env` is just an ordinary file unless something explicitly loads it. Also, environment variables are injected when the container is created; editing `.env` does not change the environment inside an already-running container.

**Root Cause:** The API key had been saved in `tests/.env`, but Compose was running from the project root where `docker-compose.yml` lives. There was no root `.env` at `C:\Users\kalen\projects\pivotmap\PivotMap\.env`, so Compose substituted an empty value for `MIROMIND_API_KEY`. The running backend container therefore still saw no key.

**Diagnosis Path:** Checking the root env file failed because it did not exist. Searching for env files showed only `.env.example` and `tests/.env`. The Compose file showed the backend expects:

```yaml
MIROMIND_API_KEY: ${MIROMIND_API_KEY:-}
```

That confirmed Compose was not reading the nested test env file. After copying `tests/.env` to the root `.env` and recreating the backend container, a safe in-container check showed the key was present without printing the secret:

```text
MIROMIND_API_KEY present: True
length: 47
prefix: sk-MiW
```

**Fix:** Copy the env values to the project-root `.env` beside `docker-compose.yml`, then recreate the backend container:

```powershell
Copy-Item -LiteralPath .\tests\.env -Destination .\.env -Force
docker compose up -d --force-recreate backend
```

**Why The Fix Works:** Compose now reads the correct root `.env` file and substitutes the real `MIROMIND_API_KEY` into the backend service definition. Recreating the backend container starts a new process with the updated environment.

**How To Verify:** Check the backend container environment without exposing the full secret:

```powershell
docker compose exec backend sh -c "python - <<'PY'
import os
v=os.getenv('MIROMIND_API_KEY') or ''
print('MIROMIND_API_KEY present:', bool(v))
print('length:', len(v))
print('prefix:', v[:6])
PY"
```

Then trigger `/capture/voice` or `/target/jd` again and confirm new logs no longer say `reason=missing_api_key`.

**Preventive Rule:** Put Docker Compose variables in the `.env` file next to `docker-compose.yml`, and recreate affected containers after changing env values. Use nested `.env` files only when a specific tool explicitly loads that path.

**Related Files / Commands:** `.env`, `.env.example`, `tests/.env`, `docker-compose.yml`, `docker compose up -d --force-recreate backend`, `docker compose exec backend`.
