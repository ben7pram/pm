# Backend AGENTS

This backend directory holds a minimal FastAPI application used for the project management MVP.

## Current state (scaffolding stage)

- `main.py` defines a FastAPI app with two routes:
  - `GET /api/hello` returns JSON confirming the backend is running.
  - `GET /` serves a static `hello.html` from `backend/static` if present, otherwise returns a default message.
- `backend/static/hello.html` is included as a basic static asset for testing.
- `pyproject.toml` declares dependencies (`fastapi`, `uvicorn`) and is used by the `uv` package manager.
- `tests/test_main.py` contains simple pytest cases to exercise the endpoints.

### Notes

- The project uses `uv` for package management; Dockerfile installs `uv` and runs `python -m uv install`.
- Dockerfile (in repository root) builds the environment, installs dependencies, copies code, and exposes port 8000.
- Start/stop scripts are provided in `scripts/` to build and manage the Docker container across platforms.

This file should grow as more backend components are added (database, API routes, AI integration, etc.).
