"""Application state models for doc-studio."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import Field


class FileType(str, Enum):
    """File type enumeration."""

    FILE = "file"
    DIRECTORY = "directory"


class FileNode(BaseModel):
    """Represents a file or directory node in the repository tree."""

    path: str
    name: str
    type: FileType
    children: list[FileNode] = Field(default_factory=list)
    is_included: bool = False  # Whether this file is included in any template section


class TemplateSection(BaseModel):
    """Represents a section within a documentation template."""

    id: str
    title: str
    content: str = ""
    source_files: list[str] = Field(default_factory=list)  # Paths to source files
    order: int = 0


class Template(BaseModel):
    """Represents a documentation template."""

    name: str
    description: str = ""
    sections: list[TemplateSection] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class JobStatus(str, Enum):
    """Generation job status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationJob(BaseModel):
    """Represents a documentation generation job."""

    id: str
    template_name: str
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0  # 0-100
    current_stage: str = ""
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result_path: str | None = None


class AppState(BaseModel):
    """Global application state."""

    current_template: Template | None = None
    file_tree: FileNode | None = None
    active_job: GenerationJob | None = None
    workspace_path: str = "."

    def get_included_files(self) -> set[str]:
        """Get set of all files included in the current template."""
        if not self.current_template:
            return set()

        included = set()
        for section in self.current_template.sections:
            included.update(section.source_files)
        return included
