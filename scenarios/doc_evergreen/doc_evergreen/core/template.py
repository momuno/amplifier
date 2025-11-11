"""
Template management for doc-evergreen.

Handles loading built-in templates, saving customized templates,
and automatic versioning.
"""

import re
from datetime import datetime, timezone
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


def load_builtin_template(template_name: str) -> str:
    """
    Load a built-in template by name.

    Args:
        template_name: Name of template (without .md extension)

    Returns:
        Template content as string

    Raises:
        FileNotFoundError: If template doesn't exist
    """
    templates_dir = get_builtin_templates_dir()
    template_path = templates_dir / f"{template_name}.md"

    if not template_path.exists():
        available = list_builtin_templates()
        raise FileNotFoundError(
            f"Built-in template '{template_name}' not found. "
            f"Available templates: {', '.join(available) if available else 'none'}"
        )

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


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
        "created": datetime.now(timezone.utc).isoformat(),
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
        existing_metadata["created"] = datetime.now(timezone.utc).isoformat()

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

    with open(full_path, "r", encoding="utf-8") as f:
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


def select_builtin_template(about: str) -> str:
    """
    Select appropriate built-in template based on topic.

    This is a simple keyword-based fallback. For more intelligent selection,
    use select_template_with_llm() instead.

    Args:
        about: Description of what documentation is about

    Returns:
        Name of built-in template to use
    """
    about_lower = about.lower()

    # Keyword to template mapping (check more specific keywords first)
    keywords = {
        "readme": "readme",
        "api": "api-reference",
        "reference": "api-reference",
        "contributing": "developer-guide",
        "developer": "developer-guide",
        "development": "developer-guide",
        "user guide": "user-guide",
        "tutorial": "user-guide",
        "guide": "user-guide",  # Check generic "guide" last
    }

    # Find matching keyword
    for keyword, template in keywords.items():
        if keyword in about_lower:
            # Check if template exists
            try:
                load_builtin_template(template)
                return template
            except FileNotFoundError:
                continue

    # Default to readme if no match
    return "readme"


def get_template_descriptions() -> dict[str, str]:
    """
    Get brief descriptions of built-in templates by reading their content.

    Returns:
        Dictionary mapping template names to brief descriptions
    """
    descriptions = {}

    for template_name in list_builtin_templates():
        try:
            content = load_builtin_template(template_name)
            # Extract first few lines as description (skip frontmatter)
            _, content_only = parse_template_metadata(content)
            lines = content_only.strip().split("\n")

            # Get first substantial line (skip empty lines and short headings)
            description = ""
            for line in lines[:10]:
                line = line.strip()
                if len(line) > 20 and not line.startswith("#"):
                    description = line[:150]
                    break

            if not description:
                # Fallback to first line
                description = lines[0][:150] if lines else "No description"

            descriptions[template_name] = description

        except Exception:
            descriptions[template_name] = "No description available"

    return descriptions


def select_template_with_llm(about: str, repo_path: Path) -> str:
    """
    Use LLM to intelligently select or create an appropriate template.

    This function:
    1. Lists available built-in templates
    2. Asks LLM to either select an existing template OR indicate a new one is needed
    3. If creating new, generates the template content via LLM
    4. Saves newly created templates
    5. Returns the template name to use

    Args:
        about: User's description of what documentation is about
        repo_path: Repository root path (for saving new templates)

    Returns:
        Name of template to use (either existing or newly created)
    """
    # Import here to avoid circular dependency
    from doc_evergreen.core.generator import call_llm

    # Get available templates and their descriptions
    available_templates = list_builtin_templates()
    template_descriptions = get_template_descriptions()

    # Format template list for LLM
    templates_list = "\n".join(
        [f"- {name}: {template_descriptions.get(name, 'No description')}" for name in available_templates]
    )

    # Ask LLM to select or indicate new template needed
    selection_prompt = f"""You are helping select an appropriate documentation template.

User's Request: {about}

Available Templates:
{templates_list}

Task: Determine if one of the existing templates is appropriate, or if a new template should be created.

Respond in ONE of these two formats:

Format 1 - Use Existing Template:
USE: <template-name>
REASON: <brief explanation>

Format 2 - Create New Template:
CREATE: <suggested-template-name>
PURPOSE: <brief description of what this new template should cover>
REASON: <why existing templates don't fit>

Be decisive. Choose CREATE only if truly none of the existing templates are appropriate."""

    llm_response = call_llm(selection_prompt, max_tokens=500, temperature=0.3)

    # Parse LLM response
    if "USE:" in llm_response:
        # Extract template name
        for line in llm_response.split("\n"):
            if line.startswith("USE:"):
                template_name = line.replace("USE:", "").strip()
                # Validate it exists
                if template_name in available_templates:
                    return template_name
                # Fallback to readme if invalid
                return "readme"

    elif "CREATE:" in llm_response:
        # Extract new template details
        new_template_name = None
        purpose = ""

        for line in llm_response.split("\n"):
            if line.startswith("CREATE:"):
                new_template_name = line.replace("CREATE:", "").strip()
            elif line.startswith("PURPOSE:"):
                purpose = line.replace("PURPOSE:", "").strip()

        if not new_template_name:
            # Fallback to generating name from about text
            new_template_name = about.lower().replace(" ", "-")[:30]

        # Generate the new template
        generation_prompt = f"""You are creating a new documentation template.

Purpose: {purpose if purpose else about}

Task: Create a documentation template that will be used by an LLM to generate documentation.

Requirements:
1. The template should contain clear instructions for the LLM on what to generate
2. Include section headings and structure
3. Use {{{{SOURCE_FILES}}}} placeholder where source code content should be extracted
4. Provide guidance on tone, style, and what to include
5. Keep it focused and specific to the purpose

Example template structure:
# {{{{Document Title}}}}

## Overview
[Instructions: Provide a brief overview of...]

## {{{{Section Name}}}}
[Instructions: Analyze the source files and extract...]

{{{{SOURCE_FILES}}}}

Generate the complete template in markdown format:"""

        template_content = call_llm(generation_prompt, max_tokens=2000, temperature=0.4)

        # Save the new template
        metadata = {
            "derived_from": None,
            "customizations": [f"Generated for: {about}"],
        }

        save_template(template_content, new_template_name, repo_path, metadata)

        return new_template_name

    # Fallback: use readme if response format unexpected
    return "readme"
