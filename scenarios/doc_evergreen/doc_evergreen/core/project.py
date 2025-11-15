"""
Project directory management for doc-evergreen.

Each document gets its own project directory under .doc-evergreen/projects/
containing metadata, content copies, templates, and history.
"""

import hashlib
import json
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any


def get_file_content_hash(file_path: str, repo_path: Path) -> str | None:
    """
    Get the SHA-256 hash of a file's content.

    Args:
        file_path: Path to file (relative to repo root)
        repo_path: Path to repository root

    Returns:
        SHA-256 hash string or None if file doesn't exist/error occurs
    """
    full_path = repo_path / file_path
    if not full_path.exists():
        return None

    try:
        with open(full_path, "rb") as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()
    except Exception:
        return None


def get_project_dir(doc_path: str, repo_path: Path) -> Path:
    """
    Get the project directory for a document.

    Args:
        doc_path: Path to document (relative to repo root)
        repo_path: Path to repository root

    Returns:
        Path to project directory
    """
    # Use the doc_path as the project directory name
    # Replace slashes with underscores to avoid nested directories
    project_name = doc_path.replace("/", "_").replace("\\", "_")
    return repo_path / ".doc-evergreen" / "projects" / project_name


def ensure_project_dir(doc_path: str, repo_path: Path) -> Path:
    """
    Ensure project directory exists for a document.

    Args:
        doc_path: Path to document (relative to repo root)
        repo_path: Path to repository root

    Returns:
        Path to project directory
    """
    project_dir = get_project_dir(doc_path, repo_path)
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def save_project_metadata(
    doc_path: str,
    about: str,
    source_patterns: list[str],
    source_files_with_commits: dict[str, str],
    template_version: str,
    repo_path: Path,
) -> None:
    """
    Save document metadata to project directory.

    Args:
        doc_path: Path to document (relative to repo root)
        about: Description of what the document covers
        source_patterns: List of source file patterns/paths provided by user
        source_files_with_commits: Dict mapping source file paths to their commit hashes
        template_version: Template version identifier used for generation
        repo_path: Path to repository root
    """
    project_dir = ensure_project_dir(doc_path, repo_path)
    metadata_path = project_dir / "metadata.json"

    now = datetime.now(UTC).isoformat()

    # Load existing metadata if it exists
    metadata: dict[str, Any]
    if metadata_path.exists():
        with open(metadata_path, encoding="utf-8") as f:
            metadata = json.load(f) or {}
    else:
        metadata = {
            "doc_path": doc_path,
            "created": now,
        }

    # Update core metadata
    metadata["last_generated"] = now

    # Create generation entry for this run
    generation_entry = {
        "timestamp": now,
        "about": about,
        "source_patterns": source_patterns,
        "source_files": source_files_with_commits,
        "template_version": template_version,
    }

    # Add to generations list
    if "generations" not in metadata:
        metadata["generations"] = []

    metadata["generations"].append(generation_entry)

    # Save metadata
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def backup_existing_document(doc_path: str, repo_path: Path) -> str | None:
    """
    Backup existing document before generating a new version.

    Args:
        doc_path: Path to document (relative to repo root)
        repo_path: Path to repository root

    Returns:
        Timestamp string used for backup file name, or None if no existing document
    """
    # Check if document exists
    existing_doc_path = repo_path / doc_path
    if not existing_doc_path.exists():
        return None

    # Read existing document content
    with open(existing_doc_path, encoding="utf-8") as f:
        existing_content = f.read()

    # Create backup with timestamp
    project_dir = ensure_project_dir(doc_path, repo_path)
    backups_dir = project_dir / "backups"
    backups_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{Path(doc_path).stem}-{timestamp}.md"
    backup_path = backups_dir / backup_filename

    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(existing_content)

    return timestamp


def save_generated_document(
    doc_path: str,
    content: str,
    repo_path: Path,
    project_name: str,
    doc_description: str,
    source_files_content: dict[str, str],
    customized_template_version: str | None = None,
    prompt_name: str | None = None,
    prompt_version: str | None = None,
) -> Path:
    """
    Save generated document with standardized versioning format.

    Uses the same versioned structure as steps 2-4.

    Args:
        doc_path: Path to document (relative to repo root)
        content: Generated document content
        repo_path: Path to repository root
        project_name: Name of the document project
        doc_description: Description of what the document covers (the "about" parameter)
        source_files_content: Dict mapping file paths to their full content (used to get commit hashes)
        customized_template_version: Version of customized template used (references step 4)
        prompt_name: Name of the LLM prompt used
        prompt_version: Version of the LLM prompt used

    Returns:
        Path to the saved metadata file
    """

    project_dir = ensure_project_dir(doc_path, repo_path)

    # Create 5_generated_doc subdirectory (step 5 in the workflow)
    generated_dir = project_dir / "5_generated_doc"
    generated_dir.mkdir(exist_ok=True)

    # Use metadata.json for step 5
    # Include parent directory so it's clear this is a step 5 file
    full_name = "5_generated_doc/metadata"
    metadata_path = generated_dir / "metadata.json"
    doc_md_path = generated_dir / "generated_doc.md"

    # Save the actual document content
    with open(doc_md_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Create timestamp for this version
    now = datetime.now(UTC).isoformat()

    # Get content hashes for source files
    source_files_with_hashes = []
    for file_path in source_files_content:
        content_hash = get_file_content_hash(file_path, repo_path)
        source_files_with_hashes.append(
            {
                "file_path": file_path,
                "content_hash": content_hash if content_hash else "no-hash",
            }
        )

    # Build new version entry with standardized structure
    new_version: dict[str, Any] = {
        "version": now,  # Timestamp IS the version
        "outputs": {
            "document": content,  # Full content of the generated document
        },
        "prompt": {
            "name": f"prompts/{prompt_name}.json" if prompt_name else "prompts/generate_document.json",
            "version": prompt_version if prompt_version else "unknown",
        },
        "inputs": {
            "doc_description": doc_description,  # The "about" parameter describing what to document
            "customized_template": {
                "name": "4_customized_template/metadata.json",
                "version": customized_template_version if customized_template_version else "unknown",
            },
            "selected_files_with_reasons": {
                "name": "4_customized_template/metadata.json",
                "version": customized_template_version if customized_template_version else "unknown",
            },
            "source_files_content": source_files_with_hashes,  # List of {file_path, content_hash}
        },
    }

    # Load existing data or create new structure
    if metadata_path.exists():
        try:
            with open(metadata_path, encoding="utf-8") as f:
                data = json.load(f)

            # Handle legacy format if needed
            if data and "versions" not in data:
                # Convert old format to new standardized format
                legacy_version = {
                    "version": data.get("last_generated", now),
                    "outputs": {"document": "generated_doc.md"},
                    "prompt": {"name": "unknown", "version": "unknown"},
                    "inputs": data.get("inputs", {}),
                }
                data = {"project_name": project_name, "name": full_name, "versions": [legacy_version]}
            elif data and "versions" in data:
                # Update to use 'name' with full path if needed
                if "name" not in data or not data["name"].startswith("5_generated_doc/"):
                    data["name"] = full_name
                # Ensure project_name is at top level
                if "project_name" not in data:
                    data["project_name"] = project_name
            elif not data:
                # Empty file
                data = {"project_name": project_name, "name": full_name, "versions": []}

        except (OSError, json.JSONDecodeError):
            # Corrupted file - start fresh
            data = {"project_name": project_name, "name": full_name, "versions": []}
    else:
        # New file
        data = {"project_name": project_name, "name": full_name, "versions": []}

    # Append new version
    data["versions"].append(new_version)

    # Save updated metadata
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return metadata_path


def save_customized_template(
    doc_path: str,
    template_content: str,
    repo_path: Path,
    template_version: str,
    project_name: str,
    selected_files: dict[str, str] | None = None,
    doc_description: str | None = None,
    template_guide_version: str | None = None,
    source_file_data: list[dict] | None = None,
    prompt_name: str | None = None,
    prompt_version: str | None = None,
) -> Path:
    """
    Save customized template to project directory with standardized versioning format.

    Uses the same versioned structure as file summaries and relevancy scores.

    Args:
        doc_path: Path to document (relative to repo root)
        template_content: Customized template content from LLM
        repo_path: Path to repository root
        template_version: Template version identifier
        project_name: Name of the document project
        selected_files: Dict mapping file paths to reasons for inclusion (from LLM)
        doc_description: Document description used as input
        template_guide_version: Version of template guide used as input
        source_file_data: List of source file data with summaries and relevancy used as input
        prompt_name: Name of the LLM prompt used
        prompt_version: Version of the LLM prompt used

    Returns:
        Path to the saved template file
    """
    from doc_evergreen.core.summaries import sanitize_filepath_to_filename

    project_dir = ensure_project_dir(doc_path, repo_path)

    # Create 4_customized_template subdirectory (step 4 in the workflow)
    templates_dir = project_dir / "4_customized_template"
    templates_dir.mkdir(exist_ok=True)

    # Use metadata.json for step 4
    # Include parent directory so it's clear this is a step 4 file
    full_name = "4_customized_template/metadata"
    file_path = templates_dir / "metadata.json"

    # Create timestamp for this version
    now = datetime.now(UTC).isoformat()

    # Build new version entry with standardized structure
    new_version: dict[str, Any] = {
        "version": now,  # Timestamp IS the version
        "outputs": {
            # Store LLM output AS IS (both fields from the LLM response)
            "customized_template": template_content,
            "selected_files_with_reasons": selected_files if selected_files is not None else {},
        },
        "prompt": {
            "name": f"prompts/{prompt_name}.json" if prompt_name else "prompts/create_customized_template.json",
            "version": prompt_version if prompt_version else "unknown",
        },
        "inputs": {
            "doc_description": doc_description if doc_description else "",
            "template_guide": {
                "name": "doc_evergreen/templates/template_guide.json",  # Full path to template guide
                "version": template_guide_version if template_guide_version else "unknown",
            },
            "formatted_source_data": [],  # Will be populated below with summary and relevancy refs
        },
    }

    # Build formatted_source_data array with both summary and relevancy references for each file
    if source_file_data:
        for file_data in source_file_data:
            file_path_str = file_data["file_path"]
            summary_timestamp = file_data["summary"].get("timestamp", "unknown")
            relevancy_timestamp = file_data["relevancy"].get("timestamp", "unknown")

            # Create sanitized name for both summary and relevancy files
            sanitized = sanitize_filepath_to_filename(file_path_str).replace(".json", "")

            new_version["inputs"]["formatted_source_data"].append(
                {
                    "file_path": file_path_str,  # Include file path for reference
                    "summary": {
                        "name": f"2_file_summaries/{sanitized}.json",
                        "version": summary_timestamp,
                    },
                    "relevancy_score": {
                        "name": f"3_relevancy/{sanitized}.json",
                        "version": relevancy_timestamp,
                    },
                    "relevancy_explanation": {
                        "name": f"3_relevancy/{sanitized}.json",
                        "version": relevancy_timestamp,
                    },
                }
            )

    # Load existing data or create new structure
    if file_path.exists():
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Handle legacy format if needed (though step 4 is new, so unlikely)
            if data and "versions" not in data:
                # Convert old format to new standardized format
                legacy_version = {
                    "version": data.get("version", now),
                    "outputs": data.get("outputs", {}),
                    "prompt": data.get("prompt", {"name": "unknown", "version": "unknown"}),
                    "inputs": data.get("inputs", {}),
                }
                data = {"project_name": project_name, "name": full_name, "versions": [legacy_version]}
            elif data and "versions" in data:
                # Update to use 'name' with full path if needed
                if "name" not in data or not data["name"].startswith("4_customized_template/"):
                    data["name"] = full_name
                # Ensure project_name is at top level
                if "project_name" not in data:
                    data["project_name"] = project_name
            elif not data:
                # Empty file
                data = {"project_name": project_name, "name": full_name, "versions": []}

        except (OSError, json.JSONDecodeError):
            # Corrupted file - start fresh
            data = {"project_name": project_name, "name": full_name, "versions": []}
    else:
        # New file
        data = {"project_name": project_name, "name": full_name, "versions": []}

    # Append new version
    data["versions"].append(new_version)

    # Save updated data
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Also save as markdown for convenience in the 4_customized_template directory
    current_template_path = templates_dir / "customized_template.md"
    with open(current_template_path, "w", encoding="utf-8") as f:
        f.write(template_content)

    return file_path


def save_template_index(
    doc_path: str,
    files_used: dict[str, str],
    repo_path: Path,
) -> None:
    """
    Save template index (files used and reasons) to project directory.

    Args:
        doc_path: Path to document (relative to repo root)
        files_used: Dictionary mapping file paths to reasons for inclusion
        repo_path: Path to repository root
    """
    project_dir = ensure_project_dir(doc_path, repo_path)
    index_path = project_dir / "template_index.json"

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(files_used, f, indent=2, ensure_ascii=False)


def load_template_index(doc_path: str, repo_path: Path) -> dict[str, str]:
    """
    Load template index from project directory.

    Args:
        doc_path: Path to document (relative to repo root)
        repo_path: Path to repository root

    Returns:
        Dictionary mapping file paths to reasons for inclusion
    """
    project_dir = get_project_dir(doc_path, repo_path)
    index_path = project_dir / "template_index.json"

    if not index_path.exists():
        return {}

    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)
        return index if index else {}


def load_customized_template(doc_path: str, repo_path: Path) -> str | None:
    """
    Load customized template from project directory.

    Args:
        doc_path: Path to document (relative to repo root)
        repo_path: Path to repository root

    Returns:
        Template content, or None if not found
    """
    project_dir = get_project_dir(doc_path, repo_path)
    template_path = project_dir / "template.md"

    if not template_path.exists():
        return None

    with open(template_path, encoding="utf-8") as f:
        return f.read()
