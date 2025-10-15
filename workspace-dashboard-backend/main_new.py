"""
Main FastAPI Application - Refactored for proper entity model

Uses Projects -> Tasks -> Sessions hierarchy with stable IDs.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from entities import Project, Task, Session, TaskStatus, project_store, task_store, session_store
from sse_manager import SSEManager
from file_watcher import FileWatcher
from claude_integration import ClaudeIntegration


# Request Models
class CreateProjectRequest(BaseModel):
    name: str
    metadata: Optional[Dict[str, Any]] = None


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class CreateTaskRequest(BaseModel):
    name: str
    metadata: Optional[Dict[str, Any]] = None


class UpdateTaskRequest(BaseModel):
    name: Optional[str] = None
    status: Optional[TaskStatus] = None
    last_accomplishment: Optional[str] = None
    next_action: Optional[str] = None
    position: Optional[int] = None
    project_id: Optional[str] = None  # Allow moving tasks between projects


class CreateSessionRequest(BaseModel):
    metadata: Optional[Dict[str, Any]] = None


# Response Models (for frontend compatibility)
class TaskWithProject(BaseModel):
    """Task with project info for frontend display"""

    id: str
    project_id: str
    project_name: str
    task_name: str
    status: TaskStatus
    last_accomplishment: Optional[str]
    next_action: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_interaction: datetime  # For compatibility
    outputs: List[str] = []
    metadata: Dict[str, Any] = {}


# Global instances
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
    description="Real-time dashboard with proper entity management",
    version="0.2.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Project Endpoints


@app.post("/api/projects", response_model=Project)
async def create_project(request: CreateProjectRequest) -> Project:
    """Create a new project"""
    project = project_store.create(name=request.name, metadata=request.metadata or {})
    return project


@app.get("/api/projects", response_model=List[Project])
async def list_projects() -> List[Project]:
    """List all projects"""
    return project_store.list()


@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(project_id: str) -> Project:
    """Get project by ID"""
    project = project_store.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.put("/api/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, request: UpdateProjectRequest) -> Project:
    """Update a project"""
    updates = request.dict(exclude_unset=True)
    project = project_store.update(project_id, updates)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str) -> Dict[str, str]:
    """Delete a project and all its tasks"""
    project = project_store.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete all tasks in project
    tasks_deleted = task_store.delete_by_project(project_id)

    # Delete project
    project_store.delete(project_id)

    return {"message": f"Project {project.name} deleted", "tasks_deleted": str(tasks_deleted)}


# Task Endpoints


@app.post("/api/projects/{project_id}/tasks", response_model=Task)
async def create_task(project_id: str, request: CreateTaskRequest) -> Task:
    """Create a new task in a project"""
    project = project_store.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task = task_store.create(project_id=project_id, name=request.name, metadata=request.metadata or {})

    # Create directory for task
    task_dir = file_watcher.base_dir / project_id / task.id
    task_dir.mkdir(parents=True, exist_ok=True)

    # Start file watcher
    async def on_file_change(event):
        await sse_manager.session_outputs_created(session_id=task.id, outputs=[event.src_path])

    file_watcher.watch_session(task.id, on_file_change)

    return task


@app.get("/api/projects/{project_id}/tasks", response_model=List[Task])
async def list_project_tasks(project_id: str) -> List[Task]:
    """List all tasks in a project"""
    project = project_store.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return task_store.get_by_project(project_id)


@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str) -> Task:
    """Get task by ID"""
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, request: UpdateTaskRequest) -> Task:
    """Update a task"""
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    old_status = task.status
    updates = request.dict(exclude_unset=True)

    task = task_store.update(task_id, updates)

    # Broadcast status change if needed
    if request.status and request.status != old_status:
        await sse_manager.session_status_changed(
            session_id=task_id,
            old_status=old_status,
            new_status=request.status,
            last_accomplishment=task.last_accomplishment,
            next_action=task.next_action,
        )

    return task


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str) -> Dict[str, str]:
    """Delete a task and all its sessions"""
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Delete all sessions in task
    sessions_deleted = session_store.delete_by_task(task_id)

    # Stop file watcher
    file_watcher.stop_watching(task_id)

    # Delete task
    task_store.delete(task_id)

    return {"message": f"Task {task.name} deleted", "sessions_deleted": str(sessions_deleted)}


# Session Endpoints (for work sessions)


@app.post("/api/tasks/{task_id}/sessions", response_model=Session)
async def create_session(task_id: str, request: CreateSessionRequest) -> Session:
    """Create a new work session for a task"""
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session = session_store.create(task_id=task_id, metadata=request.metadata or {})

    # Update task status
    task_store.update(task_id, {"status": TaskStatus.ACTIVE})

    return session


@app.get("/api/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str) -> Session:
    """Get session by ID"""
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.put("/api/sessions/{session_id}/end")
async def end_session(session_id: str) -> Session:
    """End a work session"""
    session = session_store.end(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update task status
    task = task_store.get(session.task_id)
    if task:
        task_store.update(task.id, {"status": TaskStatus.IDLE})

    return session


# Compatibility Endpoints (for frontend that expects old format)


@app.get("/sessions", response_model=List[TaskWithProject])
async def list_sessions_compat() -> List[TaskWithProject]:
    """List all tasks as sessions for compatibility"""
    tasks = task_store.list()
    projects_map = {p.id: p for p in project_store.list()}

    result = []
    for task in tasks:
        project = projects_map.get(task.project_id)
        if project:
            # Get latest session for this task
            sessions = session_store.get_by_task(task.id)
            outputs = []
            if sessions:
                for session in sessions:
                    outputs.extend(session.outputs)

            result.append(
                TaskWithProject(
                    id=task.id,
                    project_id=project.id,
                    project_name=project.name,
                    task_name=task.name,
                    status=task.status,
                    last_accomplishment=task.last_accomplishment,
                    next_action=task.next_action,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                    last_interaction=task.updated_at,
                    outputs=outputs,
                    metadata={},
                )
            )

    return result


class CreateSessionCompatRequest(BaseModel):
    project_name: str
    task_name: str
    metadata: Optional[Dict[str, Any]] = None


@app.post("/sessions", response_model=TaskWithProject)
async def create_session_compat(request: CreateSessionCompatRequest) -> TaskWithProject:
    """Create session compatibility endpoint"""
    data = request.model_dump()
    project_name = data.get("project_name", "Unnamed Project")
    task_name = data.get("task_name", "Unnamed Task")

    # Get or create project
    project = project_store.get_by_name(project_name)
    if not project:
        project = project_store.create(name=project_name)

    # Create task
    task = task_store.create(project_id=project.id, name=task_name)

    # Create directory
    task_dir = file_watcher.base_dir / project.id / task.id
    task_dir.mkdir(parents=True, exist_ok=True)

    return TaskWithProject(
        id=task.id,
        project_id=project.id,
        project_name=project.name,
        task_name=task.name,
        status=task.status,
        last_accomplishment=task.last_accomplishment,
        next_action=task.next_action,
        created_at=task.created_at,
        updated_at=task.updated_at,
        last_interaction=task.updated_at,
        outputs=[],
        metadata={},
    )


class UpdateSessionCompatRequest(BaseModel):
    project_name: Optional[str] = None
    task_name: Optional[str] = None
    status: Optional[TaskStatus] = None
    last_accomplishment: Optional[str] = None
    next_action: Optional[str] = None
    outputs: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@app.put("/sessions/{task_id}", response_model=TaskWithProject)
async def update_session_compat(task_id: str, request: UpdateSessionCompatRequest) -> TaskWithProject:
    """Update session compatibility endpoint"""
    data = request.model_dump(exclude_unset=True)
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = project_store.get(task.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Handle project name change
    if "project_name" in data and data["project_name"] != project.name:
        project_store.update(project.id, {"name": data["project_name"]})

    # Handle task updates
    updates = {}
    if "task_name" in data:
        updates["name"] = data["task_name"]
    if "status" in data:
        updates["status"] = data["status"]
    if "last_accomplishment" in data:
        updates["last_accomplishment"] = data["last_accomplishment"]
    if "next_action" in data:
        updates["next_action"] = data["next_action"]

    if updates:
        task = task_store.update(task_id, updates)

    # Reload project in case name changed
    project = project_store.get(task.project_id)

    return TaskWithProject(
        id=task.id,
        project_id=project.id,
        project_name=project.name,
        task_name=task.name,
        status=task.status,
        last_accomplishment=task.last_accomplishment,
        next_action=task.next_action,
        created_at=task.created_at,
        updated_at=task.updated_at,
        last_interaction=task.updated_at,
        outputs=[],
        metadata={},
    )


@app.delete("/sessions/{task_id}")
async def delete_session_compat(task_id: str) -> Dict[str, str]:
    """Delete session compatibility endpoint"""
    return await delete_task(task_id)


@app.get("/projects")
async def list_project_names() -> List[str]:
    """List all unique project names for dropdown"""
    projects = project_store.list()
    return sorted([p.name for p in projects])


# File Management Endpoints


@app.get("/sessions/{task_id}/files")
async def get_task_files(task_id: str) -> Dict[str, Any]:
    """Get file tree for a task"""
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = project_store.get(task.project_id)
    task_dir = file_watcher.base_dir / project.id / task.id

    def build_tree(path: Path) -> Dict[str, Any]:
        """Recursively build file tree structure"""
        if path.is_file():
            return {
                "name": path.name,
                "type": "file",
                "path": str(path.relative_to(task_dir)),
                "size": path.stat().st_size,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            }
        else:
            children = []
            if path.exists():
                for child in sorted(path.iterdir()):
                    children.append(build_tree(child))
            return {
                "name": path.name if path != task_dir else "/",
                "type": "directory",
                "path": str(path.relative_to(task_dir)) if path != task_dir else "",
                "children": children,
            }

    if not task_dir.exists():
        task_dir.mkdir(parents=True, exist_ok=True)

    tree = build_tree(task_dir)
    return {"session_id": task_id, "tree": tree}


@app.get("/sessions/{task_id}/files/{file_path:path}")
async def get_file_content(task_id: str, file_path: str) -> Dict[str, Any]:
    """Get content of a specific file"""
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = project_store.get(task.project_id)
    full_path = file_watcher.base_dir / project.id / task.id / file_path

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

import json

LAYOUTS_FILE = Path("./layouts.json")


class LayoutData(BaseModel):
    layouts: Dict[str, Any]
    timestamp: Optional[datetime] = None


@app.get("/dashboard/layouts")
async def get_layouts() -> Dict[str, Any]:
    """Get saved dashboard layouts"""
    if LAYOUTS_FILE.exists():
        with open(LAYOUTS_FILE, "r") as f:
            return json.load(f)
    return {"layouts": {}}


@app.put("/dashboard/layouts")
async def save_layouts(layout_data: LayoutData) -> Dict[str, str]:
    """Save dashboard layout"""
    data = {"layouts": layout_data.layouts, "timestamp": datetime.now(timezone.utc).isoformat()}

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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "projects": len(project_store.list()),
        "tasks": len(task_store.list()),
        "sessions": len(session_store.list()),
        "sse_connections": len(sse_manager.get_active_connections()),
    }


# Root endpoint


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {"name": "Workspace Dashboard API", "version": "0.2.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
