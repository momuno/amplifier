"""
Session State Management Module

Handles persistent storage of session data using JSON files.
Self-contained module with clear interfaces for session CRUD operations.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enumeration"""

    ACTIVE = "active"
    IDLE = "idle"
    COMPLETED = "completed"
    ERROR = "error"


class SessionData(BaseModel):
    """Session data model"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str
    task_name: str
    status: SessionStatus = SessionStatus.IDLE
    last_accomplishment: Optional[str] = None
    next_action: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_interaction: datetime = Field(default_factory=datetime.utcnow)
    outputs: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SessionStore:
    """Persistent session storage using JSON files"""

    def __init__(self, storage_dir: str = "./sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._sessions_file = self.storage_dir / "sessions.json"
        self._load_sessions()

    def _load_sessions(self) -> None:
        """Load sessions from disk"""
        if self._sessions_file.exists():
            try:
                with open(self._sessions_file, "r") as f:
                    data = json.load(f)
                    self.sessions = {sid: SessionData(**session_data) for sid, session_data in data.items()}
            except (json.JSONDecodeError, Exception):
                self.sessions = {}
        else:
            self.sessions = {}

    def _save_sessions(self) -> None:
        """Save sessions to disk"""
        data = {sid: session.dict() for sid, session in self.sessions.items()}
        with open(self._sessions_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def create_session(self, project_name: str, task_name: str, **kwargs) -> SessionData:
        """Create a new session"""
        session = SessionData(project_name=project_name, task_name=task_name, **kwargs)
        self.sessions[session.id] = session
        self._save_sessions()
        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get a session by ID"""
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[SessionData]:
        """Update a session"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.updated_at = datetime.utcnow()
        self._save_sessions()
        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
            return True
        return False

    def list_sessions(self) -> List[SessionData]:
        """List all sessions"""
        return list(self.sessions.values())

    def get_active_sessions(self) -> List[SessionData]:
        """Get all active sessions"""
        return [s for s in self.sessions.values() if s.status == SessionStatus.ACTIVE]
