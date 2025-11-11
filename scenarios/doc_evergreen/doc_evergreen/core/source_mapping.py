"""
Source mapping functionality for doc-evergreen.

Maps which source files are relevant for each section of a documentation template.
"""

import json
import re
from datetime import datetime
from pathlib import Path

import yaml

from doc_evergreen.core.generator import call_llm


def extract_template_sections(template: str) -> list[str]:
    """
    Extract section names from a markdown template.

    Looks for markdown headers (# Header, ## Header, etc.) and extracts their text.

    Args:
        template: Template content as markdown

    Returns:
        List of section names (header text without the # symbols)
    """
    sections = []
    # Match markdown headers: one or more #, followed by space, then text
    pattern = r"^#+\s+(.+)$"

    for line in template.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            section_name = match.group(1).strip()
            # Skip common meta sections that aren't content sections
            if section_name.lower() not in ["instructions", "notes", "todo", "example"]:
                sections.append(section_name)

    return sections


def map_sources_to_sections(template: str, sources: dict[str, str], about: str) -> dict[str, list[str]]:
    """
    Use LLM to map which sources are relevant for each section of the template.

    Args:
        template: Template content
        sources: Dictionary of source file paths to contents
        about: Description of what documentation is about

    Returns:
        Dictionary mapping section names to list of relevant source file paths
    """
    # Extract sections from template
    sections = extract_template_sections(template)

    if not sections:
        # If no sections found, return empty mapping
        return {}

    # Format sources for prompt (limit size)
    from doc_evergreen.core.generator import format_sources

    formatted_sources = format_sources(sources, max_total_length=15000)

    # List available source paths
    source_paths = list(sources.keys())

    prompt = f"""You are mapping source files to documentation sections to guide intelligent document generation.

Topic: {about}

Template Sections Identified:
{chr(10).join(f"- {section}" for section in sections)}

Available Source Files:
{chr(10).join(f"- {path}" for path in source_paths)}

Source File Contents (preview):
{formatted_sources}

Task: For each section, identify which source files are most relevant for generating that section's content.

Guidelines:
- A source can be mapped to 0, 1, or multiple sections
- Only include sources that are directly relevant to the section
- Consider file names, paths, and content
- Be specific - map to actual file paths from the available list

Respond with ONLY a JSON object in this exact format:
{{
  "Section Name 1": ["path/to/file1.py", "path/to/file2.md"],
  "Section Name 2": ["path/to/file3.py"],
  "Section Name 3": []
}}

JSON Response:"""

    response = call_llm(prompt, max_tokens=2000)

    # Parse JSON response
    try:
        # Try to extract JSON from response (in case LLM adds explanation)
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            mapping = json.loads(json_match.group(0))
        else:
            mapping = json.loads(response)

        # Validate that all sections are present
        result = {}
        for section in sections:
            if section in mapping:
                result[section] = mapping[section]
            else:
                result[section] = []

        return result
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Failed to parse source mapping from LLM response: {e}\nResponse: {response}")


def save_source_map(
    mapping: dict[str, list[str]], template_name: str, repo_path: Path, metadata: dict | None = None
) -> Path:
    """
    Save source mapping to versioned YAML file.

    Args:
        mapping: Dictionary mapping section names to source file paths
        template_name: Name of the template this mapping is for
        repo_path: Repository root path
        metadata: Optional metadata to include (template_version, description, etc.)

    Returns:
        Path to saved source map file
    """
    # Create source-maps directory
    maps_dir = repo_path / ".doc-evergreen" / "source-maps"
    maps_dir.mkdir(parents=True, exist_ok=True)

    # Find next version number
    base_name = f"{template_name}-map"
    existing_maps = list(maps_dir.glob(f"{base_name}.v*.yaml"))
    if existing_maps:
        # Extract version numbers
        versions = []
        for path in existing_maps:
            match = re.search(r"\.v(\d+)\.yaml$", path.name)
            if match:
                versions.append(int(match.group(1)))
        next_version = max(versions) + 1 if versions else 1
    else:
        next_version = 1

    # Create file path
    map_file = maps_dir / f"{base_name}.v{next_version}.yaml"

    # Build content
    content = {
        "metadata": {
            "template_name": template_name,
            "version": next_version,
            "created_at": datetime.now().isoformat(),
            **(metadata or {}),
        },
        "sections": {section: {"sources": sources} for section, sources in mapping.items()},
    }

    # Save to YAML
    with open(map_file, "w", encoding="utf-8") as f:
        yaml.dump(content, f, default_flow_style=False, sort_keys=False)

    return map_file


def load_source_map(map_path: Path) -> dict[str, list[str]]:
    """
    Load source mapping from YAML file.

    Args:
        map_path: Path to source map YAML file

    Returns:
        Dictionary mapping section names to source file paths
    """
    with open(map_path, "r", encoding="utf-8") as f:
        content = yaml.safe_load(f)

    # Extract mapping from YAML structure
    sections = content.get("sections", {})
    mapping = {}
    for section, data in sections.items():
        mapping[section] = data.get("sources", [])

    return mapping
