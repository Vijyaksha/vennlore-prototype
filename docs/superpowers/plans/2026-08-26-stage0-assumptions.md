# Stage-0 assumptions log

- Task 1: Added `pipeline/.gitignore` (excluding `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`) — not in the literal Task 1 file list, but `uv run` created a `.venv` and `.pytest_cache` in `pipeline/` and committing them would bloat the repo with generated/environment-specific artifacts. `uv.lock` (also uv-generated) was left tracked since lockfiles are meant to be committed for reproducible installs.
