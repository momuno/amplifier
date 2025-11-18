"""
Sprint 3 Deliverable 1: Template Manager

Provides template discovery, loading, detection, and metadata parsing.
Implements the GREEN phase for passing TDD tests.
"""

from pathlib import Path
from typing import Any

import yaml

# Default template directory location
DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "templates"

# Filename-to-template mapping (case-insensitive)
FILENAME_TO_TEMPLATE = {
    "readme.md": "readme",
    "contributing.md": "contributing",
    "api.md": "api-reference",
    "changelog.md": "changelog",
}


def list_templates(template_dir: Path | None = None) -> list[str]:
    """List all available template names in directory.

    Args:
        template_dir: Directory containing templates (default: doc_evergreen/templates/)

    Returns:
        List of template names (without .md extension)
    """
    if template_dir is None:
        template_dir = DEFAULT_TEMPLATE_DIR

    # Handle missing directory
    if not template_dir.exists():
        return []

    # Find all .md files, excluding hidden files
    templates = []
    for md_file in template_dir.glob("*.md"):
        # Skip hidden files (starting with .)
        if md_file.name.startswith("."):
            continue
        # Add template name (without .md extension)
        templates.append(md_file.stem)

    return templates


def load_template(name_or_path: str, template_dir: Path | None = None, templates_dir: Path | None = None) -> str:
    """Load template content by name or path.

    Args:
        name_or_path: Template name (e.g., "readme") or file path
        template_dir: Directory containing templates (default: doc_evergreen/templates/)
        templates_dir: Alias for template_dir (for compatibility)

    Returns:
        Template content as string

    Raises:
        FileNotFoundError: If template not found
    """
    # Support both parameter names for compatibility
    if templates_dir is not None:
        template_dir = templates_dir

    path = Path(name_or_path)

    # If it's an absolute path, load it directly
    if path.is_absolute():
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {name_or_path}")
        return path.read_text(encoding="utf-8")

    # For relative paths, try resolving from template_dir first if provided
    if template_dir is not None:
        resolved_path = template_dir / name_or_path
        if resolved_path.exists():
            return resolved_path.read_text(encoding="utf-8")

    # Try as relative path from cwd
    if path.exists():
        return path.read_text(encoding="utf-8")

    # Otherwise, treat as template name
    if template_dir is None:
        template_dir = DEFAULT_TEMPLATE_DIR

    # Add .md extension if not present
    template_name = name_or_path if name_or_path.endswith(".md") else f"{name_or_path}.md"
    template_path = template_dir / template_name

    # Check if path exists
    if not template_path.exists():
        raise FileNotFoundError(f"Template '{name_or_path}' not found in {template_dir}")

    return template_path.read_text(encoding="utf-8")


def detect_template(target_file: str | Path) -> str:
    """Auto-detect appropriate template from target filename.

    Args:
        target_file: Target file path (str or Path)

    Returns:
        Template name (e.g., "readme", "contributing")
    """
    # Convert to Path and get filename only (ignore path components)
    if isinstance(target_file, str):
        target_file = Path(target_file)

    filename = target_file.name.lower()

    # Check against mapping
    template_name = FILENAME_TO_TEMPLATE.get(filename)

    # Default to readme if no match
    return template_name if template_name else "readme"


def parse_template_metadata(template_content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from template content.

    Args:
        template_content: Full template content as string

    Returns:
        Tuple of (metadata dict, content without frontmatter)
    """
    # Check if content starts with frontmatter delimiter
    if not template_content.startswith("---\n"):
        return {}, template_content

    # Find the closing delimiter
    lines = template_content.split("\n")
    closing_index = -1

    for i in range(1, len(lines)):
        if lines[i] == "---":
            closing_index = i
            break

    # No closing delimiter found
    if closing_index == -1:
        return {}, template_content

    # Extract frontmatter section (between delimiters)
    frontmatter_lines = lines[1:closing_index]
    frontmatter_text = "\n".join(frontmatter_lines)

    # Extract content (after closing delimiter)
    content_lines = lines[closing_index + 1 :]
    content = "\n".join(content_lines)

    # Parse YAML frontmatter
    try:
        metadata = yaml.safe_load(frontmatter_text)
        # Handle empty frontmatter (None result)
        if metadata is None:
            metadata = {}
    except yaml.YAMLError:
        # Malformed YAML - return empty metadata and full content
        return {}, template_content

    return metadata, content
