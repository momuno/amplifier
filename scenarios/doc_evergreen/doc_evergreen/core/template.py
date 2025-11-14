"""
Template management for doc-evergreen.

Handles loading built-in templates, saving customized templates,
and automatic versioning.
"""

import re
from datetime import UTC
from datetime import datetime
from pathlib import Path

import yaml


def get_builtin_templates_dir() -> Path:
    """
    Get the built-in templates directory.

    Returns:
        Path to templates directory in package
    """
    # Get path relative to this file
    return Path(__file__).parent.parent / "templates"


def list_builtin_templates() -> list[str]:
    """
    List available built-in templates.

    Returns:
        List of template names (without .md extension)
    """
    templates_dir = get_builtin_templates_dir()

    if not templates_dir.exists():
        return []

    templates = []
    for file in templates_dir.glob("*.md"):
        templates.append(file.stem)

    return sorted(templates)


def load_template_guide() -> tuple[str, str]:
    """
    Load the template guide (versioned).

    Returns:
        Tuple of (guide content, version timestamp)

    Raises:
        FileNotFoundError: If template guide doesn't exist
        ValueError: If JSON format is invalid
    """
    import json

    templates_dir = get_builtin_templates_dir()
    template_path = templates_dir / "template_guide.json"

    if not template_path.exists():
        raise FileNotFoundError(f"Template guide not found: {template_path}")

    with open(template_path, encoding="utf-8") as f:
        data = json.load(f)

    if "versions" not in data or not data["versions"]:
        raise ValueError("Template guide has no versions")

    # Sort by version (timestamp) and get most recent
    versions = sorted(data["versions"], key=lambda v: v["version"], reverse=True)
    latest = versions[0]

    return latest["guide"], latest["version"]


def parse_template_metadata(template_content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from template.

    Template format:
    ---
    name: template-name
    version: 1
    ---
    # Template content

    Args:
        template_content: Full template content

    Returns:
        Tuple of (metadata dict, content without frontmatter)
    """
    # Check if template starts with YAML frontmatter
    if not template_content.startswith("---"):
        return {}, template_content

    # Find the closing ---
    parts = template_content.split("---", 2)

    if len(parts) < 3:
        # No valid frontmatter
        return {}, template_content

    # Parse YAML
    try:
        metadata = yaml.safe_load(parts[1])
        if metadata is None:
            metadata = {}
        content = parts[2].lstrip("\n")
        return metadata, content
    except yaml.YAMLError:
        # Invalid YAML, treat as no metadata
        return {}, template_content


def create_template_metadata(
    name: str,
    version: int,
    derived_from: str | None = None,
    customizations: list[str] | None = None,
) -> dict:
    """
    Create template metadata dictionary.

    Args:
        name: Template name
        version: Version number
        derived_from: Source template name
        customizations: List of customization descriptions

    Returns:
        Metadata dictionary
    """
    metadata = {
        "name": name,
        "version": version,
        "created": datetime.now(UTC).isoformat(),
    }

    if derived_from:
        metadata["derived_from"] = derived_from

    if customizations:
        metadata["customizations"] = customizations

    return metadata


def format_template_with_metadata(metadata: dict, content: str) -> str:
    """
    Format template with YAML frontmatter.

    Args:
        metadata: Metadata dictionary
        content: Template content

    Returns:
        Full template with frontmatter
    """
    yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)

    return f"---\n{yaml_str}---\n\n{content}"


def find_latest_version(template_name: str, repo_path: Path) -> int:
    """
    Find the latest version number for a template.

    Args:
        template_name: Base template name
        repo_path: Repository root path

    Returns:
        Latest version number (0 if no versions exist)
    """
    templates_dir = repo_path / ".doc-evergreen" / "templates"

    if not templates_dir.exists():
        return 0

    # Find all files matching pattern: {name}.v{N}.md
    pattern = re.compile(rf"^{re.escape(template_name)}\.v(\d+)\.md$")

    max_version = 0
    for file in templates_dir.glob(f"{template_name}.v*.md"):
        match = pattern.match(file.name)
        if match:
            version = int(match.group(1))
            max_version = max(max_version, version)

    return max_version


def save_template(
    template_content: str,
    template_name: str,
    repo_path: Path,
    metadata: dict | None = None,
) -> Path:
    """
    Save template with automatic versioning.

    Args:
        template_content: Template content (can include frontmatter or not)
        template_name: Base template name
        repo_path: Repository root path
        metadata: Optional metadata to add/override

    Returns:
        Path to saved template file
    """
    # Ensure templates directory exists
    templates_dir = repo_path / ".doc-evergreen" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Parse existing metadata
    existing_metadata, content = parse_template_metadata(template_content)

    # Determine next version
    next_version = find_latest_version(template_name, repo_path) + 1

    # Create or update metadata
    if metadata:
        existing_metadata.update(metadata)

    existing_metadata["name"] = template_name
    existing_metadata["version"] = next_version

    if "created" not in existing_metadata:
        existing_metadata["created"] = datetime.now(UTC).isoformat()

    # Format with metadata
    full_template = format_template_with_metadata(existing_metadata, content)

    # Save to file
    filename = f"{template_name}.v{next_version}.md"
    template_path = templates_dir / filename

    with open(template_path, "w", encoding="utf-8") as f:
        f.write(full_template)

    return template_path


def load_template_from_path(template_path: str, repo_path: Path) -> str:
    """
    Load template from a specific path.

    Args:
        template_path: Path to template (relative to repo root or absolute)
        repo_path: Repository root path

    Returns:
        Template content

    Raises:
        FileNotFoundError: If template doesn't exist
    """
    # Try as relative path first
    full_path = repo_path / template_path

    if not full_path.exists():
        # Try as absolute path
        full_path = Path(template_path)

    if not full_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(full_path, encoding="utf-8") as f:
        return f.read()


def get_template_path(template_name: str, version: int | None, repo_path: Path) -> Path:
    """
    Get path to a specific template version.

    Args:
        template_name: Base template name
        version: Version number (None for latest)
        repo_path: Repository root path

    Returns:
        Path to template file

    Raises:
        FileNotFoundError: If template doesn't exist
    """
    templates_dir = repo_path / ".doc-evergreen" / "templates"

    if version is None:
        # Get latest version
        version = find_latest_version(template_name, repo_path)

        if version == 0:
            raise FileNotFoundError(f"No versions of template '{template_name}' found")

    filename = f"{template_name}.v{version}.md"
    template_path = templates_dir / filename

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {filename}")

    return template_path
