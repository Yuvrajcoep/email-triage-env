"""
FastAPI server entry point for the Email Triage Environment.

Exposes the EmailTriageEnv via a REST API compatible with the OpenEnv spec.

Endpoints:
    POST /reset   — Start a new episode, returns session_id + initial observation
    POST /step    — Execute one action, returns observation + reward + done + info
    GET  /state   — Full environment state snapshot
    GET  /tasks   — List available tasks and metadata
    GET  /health  — Health check
    GET  /docs    — Swagger UI

Usage:
    # Via uv (after uv sync):
    uv run server

    # Direct:
    uvicorn server.app:app --host 0.0.0.0 --port 8000

    # Docker (port 7860 for HF Spaces):
    docker run -p 7860:7860 email-triage-env
"""

import os

import uvicorn

# Import the fully-featured FastAPI app from the environment package.
# This app manages multi-step stateful sessions (required for ticket queue).
from email_triage_env.server import app  # noqa: F401  (re-exported as 'app')


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Entry point for running the server.

    Enabled via pyproject.toml [project.scripts]:
        uv run server
        uv run server --port 8001
        python -m server.app

    For HF Spaces deployment port 7860 is used (set via PORT env var).
    """
    port = int(os.getenv("PORT", port))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
