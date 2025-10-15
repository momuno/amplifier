"""
Main FastAPI Application

Orchestrates all modules and provides REST/SSE endpoints.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from session_state import SessionStore, SessionStatus, SessionData
from sse_manager import SSEManager
from file_watcher import FileWatcher
from claude_integration import ClaudeIntegration


# Request/Response Models
class CreateSessionRequest(BaseModel):
    project_name: str
    task_name: str
    metadata: Optional[Dict[str, Any]] = None


class UpdateSessionRequest(BaseModel):
    status: Optional[SessionStatus] = None
    project_name: Optional[str] = None
    task_name: Optional[str] = None
    last_accomplishment: Optional[str] = None
    next_action: Optional[str] = None
    outputs: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class LayoutData(BaseModel):
    layouts: Dict[str, Any]
    timestamp: Optional[datetime] = None


# Global instances
session_store = SessionStore()
sse_manager = SSEManager()
file_watcher = FileWatcher()
claude_integration = ClaudeIntegration()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    await sse_manager.start()
    yield
    # Shutdown
    await sse_manager.stop()
    file_watcher.stop_all()


# Create FastAPI app
app = FastAPI(
    title="Workspace Dashboard API",
    description="Real-time dashboard for Claude Code sessions",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Session Management Endpoints


@app.post("/sessions", response_model=SessionData)
async def create_session(request: CreateSessionRequest) -> SessionData:
    """Create a new session"""
    # Create session in store
    session = session_store.create_session(
        project_name=request.project_name, task_name=request.task_name, metadata=request.metadata or {}
    )

    # Start file watcher for session
    async def on_file_change(event):
        """Handle file change events"""
        await sse_manager.session_outputs_created(session_id=session.id, outputs=[event.src_path])

    file_watcher.watch_session(session.id, on_file_change)

    # Create Claude integration session
    await claude_integration.create_session(session.id, request.project_name)

    # Broadcast session creation
    await sse_manager.session_status_changed(
        session_id=session.id,
        old_status=None,
        new_status=session.status,
        project_name=session.project_name,
        task_name=session.task_name,
    )

    return session


@app.get("/sessions/{session_id}", response_model=SessionData)
async def get_session(session_id: str) -> SessionData:
    """Get session by ID"""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/sessions", response_model=List[SessionData])
async def list_sessions() -> List[SessionData]:
    """List all sessions"""
    return session_store.list_sessions()


@app.get("/projects")
async def list_projects() -> List[str]:
    """List all unique project names"""
    sessions = session_store.list_sessions()
    projects = list(set(session.project_name for session in sessions))
    return sorted(projects)


@app.put("/sessions/{session_id}", response_model=SessionData)
async def update_session(session_id: str, request: UpdateSessionRequest) -> SessionData:
    """Update session"""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    old_status = session.status

    # Build update dict
    updates = {}
    if request.status is not None:
        updates["status"] = request.status
    if request.project_name is not None:
        updates["project_name"] = request.project_name
    if request.task_name is not None:
        updates["task_name"] = request.task_name
    if request.last_accomplishment is not None:
        updates["last_accomplishment"] = request.last_accomplishment
    if request.next_action is not None:
        updates["next_action"] = request.next_action
    if request.outputs is not None:
        updates["outputs"] = request.outputs
    if request.metadata is not None:
        updates["metadata"] = request.metadata

    # Update session
    updated_session = session_store.update_session(session_id, updates)

    # If project name changed, update all sessions with the same old project name
    if request.project_name and request.project_name != session.project_name:
        all_sessions = session_store.list_sessions()
        for other_session in all_sessions:
            if other_session.id != session_id and other_session.project_name == session.project_name:
                session_store.update_session(other_session.id, {"project_name": request.project_name})

    # Broadcast status change if needed
    if request.status and request.status != old_status:
        await sse_manager.session_status_changed(
            session_id=session_id,
            old_status=old_status,
            new_status=request.status,
            last_accomplishment=updated_session.last_accomplishment,
            next_action=updated_session.next_action,
        )

    # Broadcast task completion if accomplishment updated
    if request.last_accomplishment:
        await sse_manager.session_task_completed(
            session_id=session_id, task_name=updated_session.task_name, result=request.last_accomplishment
        )

    return updated_session


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, str]:
    """Close and delete a session"""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Stop file watcher
    file_watcher.stop_watching(session_id)

    # Close Claude session
    await claude_integration.close_session(session_id)

    # Delete from store
    session_store.delete_session(session_id)

    # Broadcast session closure
    await sse_manager.session_status_changed(session_id=session_id, old_status=session.status, new_status="closed")

    return {"message": f"Session {session_id} closed"}


@app.get("/sessions/{session_id}/outputs")
async def get_session_outputs(session_id: str) -> Dict[str, Any]:
    """Get generated files for a session"""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    outputs = file_watcher.get_session_outputs(session_id)

    return {"session_id": session_id, "outputs": outputs, "count": len(outputs)}


@app.get("/sessions/{session_id}/files")
async def get_session_file_tree(session_id: str) -> Dict[str, Any]:
    """Get file tree structure for a session"""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session_dir = file_watcher.base_dir / session_id

    def build_tree(path: Path) -> Dict[str, Any]:
        """Recursively build file tree structure"""
        if path.is_file():
            return {
                "name": path.name,
                "type": "file",
                "path": str(path.relative_to(session_dir)),
                "size": path.stat().st_size,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            }
        else:
            children = []
            for child in sorted(path.iterdir()):
                children.append(build_tree(child))
            return {
                "name": path.name,
                "type": "directory",
                "path": str(path.relative_to(session_dir)) if path != session_dir else "",
                "children": children,
            }

    if not session_dir.exists():
        return {"session_id": session_id, "tree": None}

    tree = build_tree(session_dir)
    tree["name"] = "/"

    return {"session_id": session_id, "tree": tree}


@app.get("/sessions/{session_id}/files/{file_path:path}")
async def get_file_content(session_id: str, file_path: str) -> Dict[str, Any]:
    """Get content of a specific file"""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    full_path = file_watcher.base_dir / session_id / file_path

    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not full_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    # Check if file is too large (> 1MB)
    if full_path.stat().st_size > 1_000_000:
        return {
            "path": file_path,
            "content": None,
            "error": "File too large to display",
            "size": full_path.stat().st_size,
        }

    try:
        # Try to read as text
        content = full_path.read_text(encoding="utf-8")
        return {
            "path": file_path,
            "content": content,
            "type": "text",
            "size": full_path.stat().st_size,
            "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat(),
        }
    except UnicodeDecodeError:
        # Binary file
        return {
            "path": file_path,
            "content": None,
            "type": "binary",
            "size": full_path.stat().st_size,
            "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat(),
        }


# Dashboard Layout Endpoints

LAYOUTS_FILE = "./layouts.json"


@app.get("/dashboard/layouts")
async def get_layouts() -> Dict[str, Any]:
    """Get saved dashboard layouts"""
    if os.path.exists(LAYOUTS_FILE):
        with open(LAYOUTS_FILE, "r") as f:
            return json.load(f)
    return {"layouts": {}}


@app.put("/dashboard/layouts")
async def save_layouts(layout_data: LayoutData) -> Dict[str, str]:
    """Save dashboard layout"""
    data = {"layouts": layout_data.layouts, "timestamp": datetime.utcnow().isoformat()}

    with open(LAYOUTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return {"message": "Layout saved successfully"}


# SSE Endpoint


@app.get("/events")
async def events(request: Request):
    """Server-sent events endpoint"""
    connection_id = sse_manager.create_connection()
    connection = sse_manager.get_connection(connection_id)

    async def event_generator():
        """Generate SSE events"""
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                # Get next event from connection queue
                event = await connection.receive()
                if event:
                    yield event.to_sse_format()

        finally:
            # Clean up connection
            sse_manager.remove_connection(connection_id)

    return EventSourceResponse(event_generator())


# Health Check


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": len(session_store.get_active_sessions()),
        "sse_connections": len(sse_manager.get_active_connections()),
    }


# Root endpoint


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {"name": "Workspace Dashboard API", "version": "0.1.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
