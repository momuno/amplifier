"""
Entity Models for Workspace Dashboard

Clean separation of Projects, Tasks, and Sessions with proper relationships.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enum"""

    IDLE = "idle"
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"


# Entity Models


class Project(BaseModel):
    """Project entity - top level organizational unit"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    position: int = 0  # For UI ordering


class Task(BaseModel):
    """Task entity - belongs to a project"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    status: TaskStatus = TaskStatus.IDLE
    last_accomplishment: Optional[str] = None
    next_action: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    position: int = 0  # Position within project


class Session(BaseModel):
    """Session entity - work session for a task"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    outputs: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Entity Stores


class ProjectStore:
    """Manages project entities"""

    def __init__(self, storage_path: Path = Path("./data/projects.json")):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.projects: Dict[str, Project] = {}
        self._load()

    def _load(self):
        """Load projects from storage"""
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                for proj_dict in data:
                    proj = Project(**proj_dict)
                    self.projects[proj.id] = proj

    def _save(self):
        """Save projects to storage"""
        with open(self.storage_path, "w") as f:
            data = [proj.model_dump(mode="json") for proj in self.projects.values()]
            json.dump(data, f, indent=2, default=str)

    def create(self, name: str, metadata: Dict[str, Any] = None) -> Project:
        """Create a new project"""
        # Find next position
        position = len(self.projects)
        project = Project(name=name, metadata=metadata or {}, position=position)
        self.projects[project.id] = project
        self._save()
        return project

    def get(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return self.projects.get(project_id)

    def get_by_name(self, name: str) -> Optional[Project]:
        """Get project by name"""
        for project in self.projects.values():
            if project.name == name:
                return project
        return None

    def list(self) -> List[Project]:
        """List all projects"""
        return sorted(self.projects.values(), key=lambda p: p.position)

    def update(self, project_id: str, updates: Dict[str, Any]) -> Optional[Project]:
        """Update a project"""
        project = self.projects.get(project_id)
        if not project:
            return None

        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)

        project.updated_at = datetime.utcnow()
        self._save()
        return project

    def delete(self, project_id: str) -> bool:
        """Delete a project"""
        if project_id in self.projects:
            del self.projects[project_id]
            self._save()
            return True
        return False


class TaskStore:
    """Manages task entities"""

    def __init__(self, storage_path: Path = Path("./data/tasks.json")):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: Dict[str, Task] = {}
        self._load()

    def _load(self):
        """Load tasks from storage"""
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                for task_dict in data:
                    task = Task(**task_dict)
                    self.tasks[task.id] = task

    def _save(self):
        """Save tasks to storage"""
        with open(self.storage_path, "w") as f:
            data = [task.model_dump(mode="json") for task in self.tasks.values()]
            json.dump(data, f, indent=2, default=str)

    def create(self, project_id: str, name: str, metadata: Dict[str, Any] = None) -> Task:
        """Create a new task"""
        # Find next position for this project
        project_tasks = self.get_by_project(project_id)
        position = len(project_tasks)

        task = Task(project_id=project_id, name=name, position=position)
        self.tasks[task.id] = task
        self._save()
        return task

    def get(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    def get_by_project(self, project_id: str) -> List[Task]:
        """Get all tasks for a project"""
        tasks = [t for t in self.tasks.values() if t.project_id == project_id]
        return sorted(tasks, key=lambda t: t.position)

    def list(self) -> List[Task]:
        """List all tasks"""
        return list(self.tasks.values())

    def update(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """Update a task"""
        task = self.tasks.get(task_id)
        if not task:
            return None

        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        self._save()
        return task

    def delete(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save()
            return True
        return False

    def delete_by_project(self, project_id: str) -> int:
        """Delete all tasks for a project"""
        to_delete = [tid for tid, task in self.tasks.items() if task.project_id == project_id]
        for task_id in to_delete:
            del self.tasks[task_id]

        if to_delete:
            self._save()
        return len(to_delete)


class SessionStore:
    """Manages session entities (work sessions)"""

    def __init__(self, storage_path: Path = Path("./data/sessions.json")):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, Session] = {}
        self._load()

    def _load(self):
        """Load sessions from storage"""
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                for session_dict in data:
                    session = Session(**session_dict)
                    self.sessions[session.id] = session

    def _save(self):
        """Save sessions to storage"""
        with open(self.storage_path, "w") as f:
            data = [session.model_dump(mode="json") for session in self.sessions.values()]
            json.dump(data, f, indent=2, default=str)

    def create(self, task_id: str, metadata: Dict[str, Any] = None) -> Session:
        """Create a new session"""
        session = Session(task_id=task_id, metadata=metadata or {})
        self.sessions[session.id] = session
        self._save()
        return session

    def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    def get_by_task(self, task_id: str) -> List[Session]:
        """Get all sessions for a task"""
        return [s for s in self.sessions.values() if s.task_id == task_id]

    def get_active(self) -> List[Session]:
        """Get all active sessions (not ended)"""
        return [s for s in self.sessions.values() if s.ended_at is None]

    def list(self) -> List[Session]:
        """List all sessions"""
        return list(self.sessions.values())

    def update(self, session_id: str, updates: Dict[str, Any]) -> Optional[Session]:
        """Update a session"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        self._save()
        return session

    def end(self, session_id: str) -> Optional[Session]:
        """End a session"""
        session = self.sessions.get(session_id)
        if session:
            session.ended_at = datetime.utcnow()
            self._save()
        return session

    def delete(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save()
            return True
        return False

    def delete_by_task(self, task_id: str) -> int:
        """Delete all sessions for a task"""
        to_delete = [sid for sid, session in self.sessions.items() if session.task_id == task_id]
        for session_id in to_delete:
            del self.sessions[session_id]

        if to_delete:
            self._save()
        return len(to_delete)


# Global instances
project_store = ProjectStore()
task_store = TaskStore()
session_store = SessionStore()
