"""FastAPI server for doc-studio."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from doc_studio.api import routes
from doc_studio.models import AppState

# Global app state
app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: Initialize app state
    # Allow workspace to be configured via environment variable
    workspace_path = os.getenv("DOC_STUDIO_WORKSPACE", str(Path.cwd()))
    workspace = Path(workspace_path).resolve()

    # Ensure workspace exists and is a directory
    if not workspace.exists():
        raise ValueError(f"Workspace directory does not exist: {workspace}")
    if not workspace.is_dir():
        raise ValueError(f"Workspace path is not a directory: {workspace}")

    app_state.workspace_path = str(workspace)
    print(f"📁 doc-studio workspace: {workspace}")

    yield

    # Shutdown: No cleanup needed currently


# Create FastAPI app
app = FastAPI(
    title="doc-studio",
    description="AI-amplified interactive workspace for documentation generation",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and typical React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, prefix="/api")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "workspace": app_state.workspace_path,
        "has_template": app_state.current_template is not None,
    }


# Serve frontend static files in production
# This will be used after `npm run build` is executed
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
