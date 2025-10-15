"""
Minimal implementation example for the Workspace Dashboard API.
This demonstrates the 'bricks and studs' approach - simple, focused, regeneratable.
"""

import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum

from fastapi import Depends
from fastapi import FastAPI
from fastapi import Header
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Simple in-memory storage for demonstration
# In production, use Redis or SQLite
sessions_db: dict[str, dict] = {}
layouts_db: dict[str, dict] = {}
sse_connections: dict[str, asyncio.Queue] = {}

app = FastAPI(title="Claude Code Workspace Dashboard API", version="1.0.0")

# === Models (The "Contract") ===


class SessionStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    ERROR = "error"


class CreateSessionRequest(BaseModel):
    workspace: str
    project_name: str | None = None
    initial_prompt: str | None = None


class UpdateSessionRequest(BaseModel):
    status: SessionStatus | None = None
    current_task: str | None = None
    next_task: str | None = None


class ErrorResponse(BaseModel):
    error: dict


# === Authentication ===


async def verify_api_key(x_api_key: str = Header(...)) -> str:
    """Simple API key verification - returns user_id"""
    if not x_api_key or not x_api_key.startswith("key_"):
        raise HTTPException(
            status_code=401, detail={"error": {"code": "UNAUTHORIZED", "message": "Invalid API key", "details": {}}}
        )
    # Extract user_id from key (in production, look up in database)
    return x_api_key.replace("key_", "user_")


# === Session Endpoints ===


@app.get("/api/v1/sessions")
async def list_sessions(user_id: str = Depends(verify_api_key)):
    """List all sessions for the authenticated user"""
    user_sessions = [s for s in sessions_db.values() if s.get("user_id") == user_id]
    return {"sessions": user_sessions}


@app.post("/api/v1/sessions", status_code=201)
async def create_session(request: CreateSessionRequest, user_id: str = Depends(verify_api_key)):
    """Create a new Claude session"""
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    session = {
        "id": session_id,
        "user_id": user_id,
        "workspace": request.workspace,
        "project_name": request.project_name or "Unnamed Project",
        "status": SessionStatus.ACTIVE,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_interaction": datetime.now(timezone.utc).isoformat(),
        "thread_id": f"thread_{uuid.uuid4().hex[:8]}",
    }

    sessions_db[session_id] = session

    # Emit event to dashboard subscribers
    await emit_dashboard_event(
        "dashboard.session.created",
        {
            "session_id": session_id,
            "workspace": request.workspace,
            "project_name": session["project_name"],
            "timestamp": session["created_at"],
        },
    )

    return session


@app.patch("/api/v1/sessions/{session_id}")
async def update_session(session_id: str, request: UpdateSessionRequest, user_id: str = Depends(verify_api_key)):
    """Update session state"""
    session = sessions_db.get(session_id)

    if not session or session["user_id"] != user_id:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Session {session_id} not found",
                    "details": {"resource_type": "session", "resource_id": session_id},
                }
            },
        )

    # Update fields
    if request.status:
        old_status = session["status"]
        session["status"] = request.status

        # Emit status change event
        await emit_session_event(
            session_id,
            "session.status",
            {
                "session_id": session_id,
                "status": request.status,
                "previous_status": old_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    if request.current_task is not None:
        session["current_task"] = request.current_task

    if request.next_task is not None:
        session["next_task"] = request.next_task

        # Emit task update event
        await emit_session_event(
            session_id,
            "session.task",
            {
                "session_id": session_id,
                "current_task": session.get("current_task"),
                "next_task": request.next_task,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    session["last_interaction"] = datetime.now(timezone.utc).isoformat()

    return session


# === SSE Implementation ===


async def emit_session_event(session_id: str, event_type: str, data: dict):
    """Emit event to session-specific subscribers"""
    key = f"session:{session_id}"
    if key in sse_connections:
        message = f"event: {event_type}\ndata: {json.dumps({'event': event_type, 'data': data})}\n\n"
        await sse_connections[key].put(message)


async def emit_dashboard_event(event_type: str, data: dict):
    """Emit event to dashboard subscribers"""
    key = "dashboard"
    if key in sse_connections:
        message = f"event: {event_type}\ndata: {json.dumps({'event': event_type, 'data': data})}\n\n"
        await sse_connections[key].put(message)


async def event_generator(queue: asyncio.Queue):
    """Generate SSE events from queue"""
    try:
        while True:
            message = await queue.get()
            yield message
    except asyncio.CancelledError:
        pass


@app.get("/api/v1/events/sessions/{session_id}")
async def session_events(session_id: str, user_id: str = Depends(verify_api_key)):
    """Subscribe to session-specific events"""
    # Verify session ownership
    session = sessions_db.get(session_id)
    if not session or session["user_id"] != user_id:
        raise HTTPException(status_code=404)

    # Create queue for this connection
    queue = asyncio.Queue()
    key = f"session:{session_id}"
    sse_connections[key] = queue

    # Send initial connection event
    await queue.put(f"event: connected\ndata: {json.dumps({'session_id': session_id})}\n\n")

    return StreamingResponse(
        event_generator(queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/v1/events/dashboard")
async def dashboard_events(user_id: str = Depends(verify_api_key)):
    """Subscribe to dashboard-wide events"""
    queue = asyncio.Queue()
    sse_connections["dashboard"] = queue

    # Send initial connection event
    await queue.put(f"event: connected\ndata: {json.dumps({'user_id': user_id})}\n\n")

    return StreamingResponse(
        event_generator(queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# === Layout Management ===


@app.get("/api/v1/layouts")
async def get_layout(user_id: str = Depends(verify_api_key)):
    """Get current dashboard layout for user"""
    layout = layouts_db.get(user_id, {"version": "1.0", "tiles": []})
    return layout


@app.put("/api/v1/layouts")
async def save_layout(layout: dict, user_id: str = Depends(verify_api_key)):
    """Save dashboard layout"""
    layouts_db[user_id] = layout

    # Emit layout change event
    await emit_dashboard_event(
        "dashboard.layout.changed", {"user_id": user_id, "timestamp": datetime.utcnow().isoformat()}
    )

    return layout


# === Workspace Management ===


@app.get("/api/v1/workspaces")
async def list_workspaces(user_id: str = Depends(verify_api_key)):
    """List available workspaces"""
    # In production, scan file system or read from config
    return {
        "workspaces": [
            {
                "path": "/home/user/amplifier-workspace",
                "name": "Amplifier Workspace",
                "last_accessed": datetime.utcnow().isoformat(),
                "git_branch": "main",
            }
        ]
    }


# === Meta Operations ===


@app.post("/api/v1/sessions/compare")
async def compare_sessions(session_ids: list[str], user_id: str = Depends(verify_api_key)):
    """Compare outputs from multiple sessions"""
    if len(session_ids) < 2 or len(session_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "Must compare between 2 and 10 sessions",
                    "details": {"provided": len(session_ids)},
                }
            },
        )

    # Verify all sessions belong to user
    sessions = []
    for sid in session_ids:
        session = sessions_db.get(sid)
        if not session or session["user_id"] != user_id:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Session {sid} not found",
                        "details": {"resource_type": "session", "resource_id": sid},
                    }
                },
            )
        sessions.append(session)

    # Simple comparison (in production, analyze actual outputs)
    return {
        "sessions": sessions,
        "differences": {"files_modified": {}, "outputs_generated": {}, "performance_metrics": {}},
    }


@app.get("/api/v1/sessions/stats")
async def get_session_stats(user_id: str = Depends(verify_api_key)):
    """Get aggregate session statistics"""
    user_sessions = [s for s in sessions_db.values() if s.get("user_id") == user_id]

    active = sum(1 for s in user_sessions if s["status"] == SessionStatus.ACTIVE)

    return {
        "total_sessions": len(user_sessions),
        "active_sessions": active,
        "tasks_completed_today": 0,  # Would track in production
        "files_modified_today": 0,  # Would track in production
        "average_session_duration": 1800,  # Would calculate in production
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
