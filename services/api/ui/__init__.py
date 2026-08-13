"""HTMX workbench served from the orchestrator (same origin as /api)."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


def attach_ui(app: FastAPI) -> None:
    from services.api.ui.router import router

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.include_router(router)
