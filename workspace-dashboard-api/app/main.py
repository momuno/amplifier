"""
Workspace Dashboard API

FastAPI backend for managing Claude Code workspace sessions.
"""

import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Workspace Dashboard API", version="1.0.0")

# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage path
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
SESSIONS_FILE = DATA_DIR / "sessions.json"
LAYOUTS_FILE = DATA_DIR / "layouts.json"


# Pydantic models
class SessionCreate(BaseModel):
    project_name: str
    name: str
    notes: str = ""
    branch: str
    size: str = "medium"


class SessionUpdate(BaseModel):
    project_name: str | None = None
    name: str | None = None
    state: str | None = None
    notes: str | None = None
    branch: str | None = None
    files_changed: int | None = None
    commits: int | None = None
    todos_complete: int | None = None
    todos_total: int | None = None
    size: str | None = None


class Session(BaseModel):
    id: str
    project_name: str
    name: str
    state: str = "PLANNING"
    notes: str = ""
    branch: str
    last_activity: datetime
    files_changed: int = 0
    commits: int = 0
    todos_complete: int = 0
    todos_total: int = 0
    size: str = "medium"
    parent_id: str | None = None


class LayoutItem(BaseModel):
    i: str
    x: int
    y: int
    w: int
    h: int
    minW: int = 3
    minH: int = 3
    maxW: int = 8
    maxH: int = 8


# Storage utilities
def load_sessions() -> list[dict]:
    """Load sessions from JSON file"""
    if not SESSIONS_FILE.exists():
        return []
    with open(SESSIONS_FILE) as f:
        return json.load(f)


def save_sessions(sessions: list[dict]) -> None:
    """Save sessions to JSON file"""
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2, default=str)


def load_layouts() -> dict:
    """Load layouts from JSON file"""
    if not LAYOUTS_FILE.exists():
        return {}
    with open(LAYOUTS_FILE) as f:
        return json.load(f)


def save_layouts(layouts: dict) -> None:
    """Save layouts to JSON file"""
    with open(LAYOUTS_FILE, "w") as f:
        json.dump(layouts, f, indent=2)


# API endpoints
@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Workspace Dashboard API"}


@app.get("/api/sessions")
def get_sessions():
    """Get all sessions"""
    return load_sessions()


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    """Get a specific session"""
    sessions = load_sessions()
    session = next((s for s in sessions if s["id"] == session_id), None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/api/sessions")
def create_session(session_data: SessionCreate):
    """Create a new session"""
    sessions = load_sessions()

    # Generate new session ID
    import time

    session_id = f"sess-{int(time.time() * 1000)}"

    new_session = {
        "id": session_id,
        "project_name": session_data.project_name,
        "name": session_data.name,
        "state": "PLANNING",
        "notes": session_data.notes,
        "branch": session_data.branch,
        "last_activity": datetime.now().isoformat(),
        "files_changed": 0,
        "commits": 0,
        "todos_complete": 0,
        "todos_total": 0,
        "size": session_data.size,
        "parent_id": None,
    }

    sessions.append(new_session)
    save_sessions(sessions)

    return new_session


@app.put("/api/sessions/{session_id}")
def update_session(session_id: str, updates: SessionUpdate):
    """Update an existing session"""
    sessions = load_sessions()
    session_index = next((i for i, s in enumerate(sessions) if s["id"] == session_id), None)

    if session_index is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update fields
    session = sessions[session_index]
    update_data = updates.model_dump(exclude_unset=True)
    session.update(update_data)
    session["last_activity"] = datetime.now().isoformat()

    save_sessions(sessions)
    return session


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a session"""
    sessions = load_sessions()
    session_index = next((i for i, s in enumerate(sessions) if s["id"] == session_id), None)

    if session_index is None:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions.pop(session_index)
    save_sessions(sessions)

    return {"status": "deleted", "id": session_id}


@app.post("/api/sessions/{session_id}/fork")
def fork_session(session_id: str):
    """Fork an existing session"""
    sessions = load_sessions()
    parent_session = next((s for s in sessions if s["id"] == session_id), None)

    if not parent_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Count existing forks
    existing_forks = [s for s in sessions if s.get("parent_id") == session_id]
    fork_number = len(existing_forks) + 1

    # Create forked session
    import time

    new_session_id = f"sess-{int(time.time() * 1000)}"

    forked_session = {
        **parent_session,
        "id": new_session_id,
        "name": f"{parent_session['name']} (Fork {fork_number})",
        "state": "PLANNING",
        "branch": f"{parent_session['branch']}-fork-{fork_number}",
        "last_activity": datetime.now().isoformat(),
        "commits": 0,
        "files_changed": 0,
        "todos_complete": 0,
        "parent_id": session_id,
    }

    sessions.append(forked_session)
    save_sessions(sessions)

    return forked_session


@app.get("/api/projects")
def get_projects():
    """Get list of unique project names"""
    sessions = load_sessions()
    projects = sorted(list(set(s["project_name"] for s in sessions)))
    return projects


@app.get("/api/layouts")
def get_layouts():
    """Get all saved layouts"""
    return load_layouts()


@app.put("/api/layouts")
def save_layout(layouts: dict):
    """Save layout configuration"""
    save_layouts(layouts)
    return {"status": "saved"}
