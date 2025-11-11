"""Server-Sent Event models for doc-studio."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel
from pydantic import Field


class EventType(str, Enum):
    """SSE event types."""

    PROGRESS = "progress"
    DISCOVERY = "discovery"
    CHAT = "chat"
    ASSISTANT_ACTION = "assistant_action"
    ERROR = "error"


class ProgressEvent(BaseModel):
    """Progress event for generation jobs."""

    type: EventType = EventType.PROGRESS
    job_id: str
    progress: float  # 0-100
    stage: str
    message: str = ""


class DiscoveryEvent(BaseModel):
    """Discovery event for LLM file discovery reasoning."""

    type: EventType = EventType.DISCOVERY
    level: int
    reasoning: str
    files_found: list[str] = Field(default_factory=list)


class ChatEvent(BaseModel):
    """Chat event for AI assistant responses."""

    type: EventType = EventType.CHAT
    message: str
    is_complete: bool = False


class AssistantAction(str, Enum):
    """Actions the AI assistant can perform."""

    UPDATE_TEMPLATE = "update_template"
    ADD_SOURCE = "add_source"
    REMOVE_SOURCE = "remove_source"
    START_GENERATION = "start_generation"
    SEARCH_FILES = "search_files"


class AssistantActionEvent(BaseModel):
    """Event for AI assistant actions."""

    type: EventType = EventType.ASSISTANT_ACTION
    action: AssistantAction
    parameters: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)


class ErrorEvent(BaseModel):
    """Error event."""

    type: EventType = EventType.ERROR
    error: str
    details: dict[str, Any] = Field(default_factory=dict)
