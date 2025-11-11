"""Template management service for doc-studio."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from doc_studio.models import Template
from doc_studio.models import TemplateSection


class TemplateService:
    """Service for managing documentation templates."""

    def __init__(self, workspace_path: str):
        """Initialize template service.

        Args:
            workspace_path: Path to workspace directory
        """
        self.workspace_path = Path(workspace_path)
        self.templates_dir = self.workspace_path / ".doc-evergreen" / "templates"

    def create_default_template(self) -> Template:
        """Create a default template for documentation.

        Returns:
            Template: Default template with common sections
        """
        sections = [
            TemplateSection(
                id=str(uuid.uuid4()),
                title="Introduction",
                content="# Introduction\n\nOverview of the project.",
                order=0,
            ),
            TemplateSection(
                id=str(uuid.uuid4()),
                title="Core Capabilities",
                content="# Core Capabilities\n\nKey features and functionality.",
                order=1,
            ),
            TemplateSection(
                id=str(uuid.uuid4()),
                title="Quick Start",
                content="# Quick Start\n\nGetting started guide.",
                order=2,
            ),
            TemplateSection(
                id=str(uuid.uuid4()),
                title="Architecture",
                content="# Architecture\n\nSystem design and structure.",
                order=3,
            ),
        ]

        return Template(
            name="default",
            description="Default documentation template",
            sections=sections,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def load_template(self, name: str) -> Template | None:
        """Load a template by name.

        Args:
            name: Template name

        Returns:
            Template if found, None otherwise
        """
        # Try to load from disk first
        template_path = self.templates_dir / f"{name}.json"
        if template_path.exists():
            import json

            with open(template_path, encoding="utf-8") as f:
                data = json.load(f)
                return Template.model_validate(data)

        # If not found and it's "default", create and save it
        if name == "default":
            template = self.create_default_template()
            self.save_template(template)
            return template

        return None

    def save_template(self, template: Template) -> None:
        """Save a template to disk.

        Args:
            template: Template to save
        """
        import json

        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Update timestamp
        template.updated_at = datetime.now()

        # Save as JSON
        template_path = self.templates_dir / f"{template.name}.json"
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(template.model_dump(mode="json"), f, indent=2, default=str)

    def add_source_to_section(self, template: Template, section_id: str, file_path: str) -> bool:
        """Add a source file to a template section.

        Args:
            template: Template to modify
            section_id: Section ID
            file_path: Path to source file

        Returns:
            True if added successfully, False if section not found
        """
        for section in template.sections:
            if section.id == section_id:
                if file_path not in section.source_files:
                    section.source_files.append(file_path)
                return True
        return False

    def remove_source_from_section(self, template: Template, section_id: str, file_path: str) -> bool:
        """Remove a source file from a template section.

        Args:
            template: Template to modify
            section_id: Section ID
            file_path: Path to source file

        Returns:
            True if removed successfully, False if section not found
        """
        for section in template.sections:
            if section.id == section_id:
                if file_path in section.source_files:
                    section.source_files.remove(file_path)
                return True
        return False

    def update_section_content(self, template: Template, section_id: str, content: str) -> bool:
        """Update the content of a template section.

        Args:
            template: Template to modify
            section_id: Section ID
            content: New content

        Returns:
            True if updated successfully, False if section not found
        """
        for section in template.sections:
            if section.id == section_id:
                section.content = content
                return True
        return False
