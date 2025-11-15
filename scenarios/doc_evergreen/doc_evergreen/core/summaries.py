"""
Summaries cache management for doc-evergreen.

Handles versioned storage of file summaries with content hash tracking.
Each file's summary is stored individually with version information.
"""

import hashlib
import json
from datetime import UTC
from datetime import datetime
from pathlib import Path


def get_file_content_hash(file_path: str, repo_path: Path) -> str | None:
    """
    Get the SHA-256 hash of a file's content.

    Args:
        file_path: Path to file (relative to repo root)
        repo_path: Path to repository root

    Returns:
        SHA-256 hash string or None if file doesn't exist
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


def get_file_summaries_dir(repo_path: Path) -> Path:
    """
    Get the directory for versioned file summaries.

    Args:
        repo_path: Path to repository root

    Returns:
        Path to 2_file_summaries directory (step 2 in the workflow)
    """
    return repo_path / ".doc-evergreen" / "2_file_summaries"


def sanitize_filepath_to_filename(file_path: str) -> str:
    """
    Convert a file path to a safe filename for storage.

    Args:
        file_path: Original file path (e.g., "src/auth/user.py")

    Returns:
        Sanitized filename (e.g., "src__auth__user__py.json")

    Examples:
        "src/auth.py" -> "src__auth__py.json"
        "README.md" -> "README__md.json"
        "docs/api/endpoints.md" -> "docs__api__endpoints__md.json"
    """
    # Replace path separators and dots with double underscores
    sanitized = file_path.replace("/", "__").replace(".", "__")
    return f"{sanitized}.json"


def get_versioned_summary_path(file_path: str, repo_path: Path) -> Path:
    """
    Get the path to a versioned summary file.

    Args:
        file_path: Path to source file (relative to repo root)
        repo_path: Path to repository root

    Returns:
        Path to the versioned summary JSON file
    """
    summaries_dir = get_file_summaries_dir(repo_path)
    filename = sanitize_filepath_to_filename(file_path)
    return summaries_dir / filename


def get_summary(file_path: str, repo_path: Path) -> dict[str, str] | None:
    """
    Get the most recent cached versioned summary for a specific file.

    Args:
        file_path: Path to file (relative to repo root)
        repo_path: Path to repository root

    Returns:
        Summary data dictionary with keys (flattened for backward compatibility):
        - file_path: Original file path
        - content_hash: SHA-256 hash of file content when summarized
        - prompt_version: Version of prompt used
        - summary: Summary text
        - timestamp: When summary was created
        Returns None if not cached
    """
    summary_path = get_versioned_summary_path(file_path, repo_path)

    if not summary_path.exists():
        return None

    try:
        with open(summary_path, encoding="utf-8") as f:
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
                # Try file_summary first (new format), fall back to summary (old format)
                outputs = most_recent.get("outputs", {})
                summary_text = outputs.get("file_summary", outputs.get("summary", ""))

                return {
                    "file_path": file_path,  # Return original file_path for backward compatibility
                    "content_hash": most_recent.get("inputs", {}).get("content_hash", "no-hash"),
                    "prompt": most_recent.get("prompt", {"name": "unknown", "version": "unknown"}),
                    "prompt_version": most_recent.get("prompt", {}).get("version", "unknown"),  # For legacy compat
                    "summary": summary_text,
                    "timestamp": most_recent.get("version", ""),  # version IS the timestamp
                }
            # Old versioned format
            return {"file_path": file_path, **most_recent}

        # Legacy flat format - return as-is
        return data

    except (OSError, json.JSONDecodeError):
        return None


def add_summary(
    file_path: str, summary: str, repo_path: Path, prompt_name: str = "TBD", prompt_version: str = "TBD"
) -> None:
    """
    Add a new versioned summary for a file.

    This appends a new version to the versions array in the JSON file.
    Each file can have multiple summary versions over time.

    Args:
        file_path: Path to file (relative to repo root)
        summary: Summary text
        repo_path: Path to repository root
        prompt_name: Name of prompt used (e.g., "summarize_file")
        prompt_version: Version of prompt used (e.g., "2025-01-13T19:00:00Z")
    """
    # Ensure directory exists
    summaries_dir = get_file_summaries_dir(repo_path)
    summaries_dir.mkdir(parents=True, exist_ok=True)

    # Get content hash for inputs
    content_hash = get_file_content_hash(file_path, repo_path)

    # Get sanitized name for this file summary with parent directory
    sanitized_filename = sanitize_filepath_to_filename(file_path).replace(".json", "")
    # Include parent directory so it's clear this is a step 2 file
    full_name = f"2_file_summaries/{sanitized_filename}"

    # Create new version entry with standardized structure
    now = datetime.now(UTC).isoformat()
    new_version = {
        "version": now,  # Timestamp IS the version
        "outputs": {
            "file_summary": summary,
        },
        "prompt": {
            "name": f"prompts/{prompt_name}.json",  # Full path to prompt file
            "version": prompt_version,
        },
        "inputs": {
            "file_path": file_path,
            "content_hash": content_hash if content_hash else "no-hash",
        },
    }

    # Load existing data or create new structure
    summary_path = get_versioned_summary_path(file_path, repo_path)

    if summary_path.exists():
        try:
            with open(summary_path, encoding="utf-8") as f:
                data = json.load(f)

            # Ensure proper structure
            if not data or "versions" not in data:
                data = {"name": full_name, "versions": []}

        except (OSError, json.JSONDecodeError):
            # Corrupted file - start fresh
            data = {"name": full_name, "versions": []}
    else:
        # New file
        data = {"name": full_name, "versions": []}

    # Append new version
    data["versions"].append(new_version)

    # Save updated data
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
