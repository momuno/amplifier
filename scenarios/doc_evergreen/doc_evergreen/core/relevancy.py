"""
Relevancy scoring storage for doc-evergreen.

Stores versioned relevancy scores for source files relative to specific documents.
Each source file can have multiple relevancy assessments for different documents over time.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from doc_evergreen.core.summaries import sanitize_filepath_to_filename


def get_project_relevancy_dir(repo_path: Path, project_name: str) -> Path:
    """
    Get the directory for relevancy scores for a specific project.

    Args:
        repo_path: Path to repository root
        project_name: Name of the document project

    Returns:
        Path to project's 3_relevancy directory (step 3 in the workflow)
    """
    return repo_path / ".doc-evergreen" / "projects" / project_name / "3_relevancy"


def get_relevancy_path(file_path: str, repo_path: Path, project_name: str) -> Path:
    """
    Get the path to a relevancy score file for a source file in a project.

    Args:
        file_path: Path to source file (relative to repo root)
        repo_path: Path to repository root
        project_name: Name of the document project

    Returns:
        Path to the relevancy JSON file
    """
    relevancy_dir = get_project_relevancy_dir(repo_path, project_name)
    filename = sanitize_filepath_to_filename(file_path)
    return relevancy_dir / filename


def add_relevancy_score(
    file_path: str,
    doc_description: str,
    relevancy_explanation: str,
    relevancy_score: int,
    summary_text: str,
    summary_timestamp: str,
    repo_path: Path,
    project_name: str,
    prompt_name: str = "TBD",
    prompt_version: str = "TBD",
) -> str:
    """
    Add a new relevancy score for a source file.

    This appends a new version to the versions array in the JSON file.
    Each source file can have multiple relevancy scores over time.

    Returns:
        The timestamp (version) of the created relevancy score

    Args:
        file_path: Path to source file (relative to repo root)
        doc_description: Description of the document being generated
        relevancy_explanation: Explanation of why file is/isn't relevant
        relevancy_score: Score from 1-10 (10 = most relevant)
        summary_text: The summary text that was used
        summary_timestamp: Timestamp of the summary version used
        repo_path: Path to repository root
        project_name: Name of the document project
        prompt_name: Name of prompt used (e.g., "score_relevancy")
        prompt_version: Version of prompt used
    """
    # Ensure directory exists
    relevancy_dir = get_project_relevancy_dir(repo_path, project_name)
    relevancy_dir.mkdir(parents=True, exist_ok=True)

    # Get sanitized name for this file with parent directory
    sanitized_filename = sanitize_filepath_to_filename(file_path).replace(".json", "")
    # Include parent directory so it's clear this is a step 3 file
    full_name = f"3_relevancy/{sanitized_filename}"

    # Create new version entry with standardized structure
    now = datetime.now(timezone.utc).isoformat()
    new_version = {
        "version": now,  # Timestamp IS the version
        "outputs": {
            "relevancy": {
                "explanation": relevancy_explanation,
                "score": relevancy_score,
            }
        },
        "prompt": {
            "name": f"prompts/{prompt_name}.json",  # Full path to prompt file
            "version": prompt_version,
        },
        "inputs": {
            "doc_description": doc_description,
            "file_path": file_path,  # Direct value used in prompt
            "file_summary": {
                "name": f"2_file_summaries/{sanitized_filename}.json",  # Path to summary file
                "version": summary_timestamp,  # Version of summary used
            },
        },
    }

    # Load existing data or create new structure
    relevancy_path = get_relevancy_path(file_path, repo_path, project_name)

    if relevancy_path.exists():
        try:
            with open(relevancy_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle legacy format if needed
            if data and "versions" not in data:
                # Convert old format to new standardized format
                legacy_timestamp = data.get("timestamp", now)
                legacy_version = {
                    "version": legacy_timestamp,
                    "outputs": {
                        "relevancy": {
                            "explanation": data.get("relevancy_explanation", ""),
                            "score": data.get("relevancy_score", 0),
                        }
                    },
                    "prompt": {
                        "name": f"prompts/{data.get('prompt', {}).get('name', 'unknown')}.json",
                        "version": data.get("prompt", {}).get("version", "unknown"),
                    },
                    "inputs": {
                        "doc_description": data.get("doc_description", ""),
                        "file_path": file_path,  # Add file_path
                        "file_summary": {
                            "name": f"2_file_summaries/{sanitized_filename}.json",
                            "version": data.get("summary", {}).get("timestamp", "unknown"),
                        },
                    },
                }
                data = {"project_name": project_name, "name": full_name, "versions": [legacy_version]}
            elif data and "versions" in data:
                # Update to use 'name' with full path if needed
                if "file_path" in data and "name" not in data:
                    data["name"] = full_name
                    del data["file_path"]
                elif "name" in data and not data["name"].startswith("3_relevancy/"):
                    # Update old name format to include parent directory
                    data["name"] = full_name
                # Ensure project_name is at top level
                if "project_name" not in data:
                    data["project_name"] = project_name
            elif not data:
                # Empty file
                data = {"project_name": project_name, "name": full_name, "versions": []}

        except (json.JSONDecodeError, IOError):
            # Corrupted file - start fresh
            data = {"project_name": project_name, "name": full_name, "versions": []}
    else:
        # New file
        data = {"project_name": project_name, "name": full_name, "versions": []}

    # Append new version
    data["versions"].append(new_version)

    # Save updated data
    with open(relevancy_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return now  # Return the timestamp/version of this relevancy score


def get_relevancy_score(file_path: str, repo_path: Path, project_name: str) -> dict[str, str | int] | None:
    """
    Get the most recent relevancy score for a source file in a project.

    Args:
        file_path: Path to source file (relative to repo root)
        repo_path: Path to repository root
        project_name: Name of the document project

    Returns:
        Relevancy data dictionary with keys (flattened for backward compatibility):
        - file_path: Original file path
        - project_name: Project name
        - doc_description: Document description used
        - prompt: {name, version} of prompt used
        - file_summary: {name, version} of summary version used
        - relevancy_explanation: Explanation text
        - relevancy_score: Score 1-10
        - timestamp: When score was created (version)
        Returns None if not found
    """
    relevancy_path = get_relevancy_path(file_path, repo_path, project_name)

    if not relevancy_path.exists():
        return None

    try:
        with open(relevancy_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data is None or not isinstance(data, dict):
            return None

        # Check if this is the versioned format
        if "versions" in data:
            versions = data["versions"]
            if not versions:
                return None

            # Sort by version field to get most recent
            sorted_versions = sorted(versions, key=lambda v: v.get("version", ""), reverse=True)
            most_recent = sorted_versions[0]

            # Flatten new format for backward compatibility
            if "outputs" in most_recent:
                # New standardized format
                return {
                    "file_path": file_path,  # Original file path for compatibility
                    "project_name": data.get("project_name", project_name),
                    "doc_description": most_recent.get("inputs", {}).get("doc_description", ""),
                    "prompt": most_recent.get("prompt", {"name": "unknown", "version": "unknown"}),
                    "file_summary": most_recent.get("inputs", {}).get("file_summary", {}),
                    "relevancy_explanation": most_recent.get("outputs", {}).get("relevancy", {}).get("explanation", ""),
                    "relevancy_score": most_recent.get("outputs", {}).get("relevancy", {}).get("score", 0),
                    "timestamp": most_recent.get("version", ""),  # version IS the timestamp
                }
            else:
                # Old versioned format
                return {"file_path": file_path, "project_name": data.get("project_name", project_name), **most_recent}

        # Legacy format - return as-is
        return data

    except (json.JSONDecodeError, IOError):
        return None
