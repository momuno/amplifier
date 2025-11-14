"""
Summaries cache management for doc-evergreen.

Handles versioned storage of file summaries with git commit tracking.
Each file's summary is stored individually with version information.
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


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


def get_git_commit_hash(file_path: str, repo_path: Path) -> str | None:
    """
    Get the current git commit hash for a specific file.

    Args:
        file_path: Path to file (relative to repo root)
        repo_path: Path to repository root

    Returns:
        Git commit hash (full SHA), or None if not in git or error
    """
    try:
        # Get the commit hash for the file
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", file_path],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

        # If no commit found, file might not be committed yet
        # Try to get current HEAD
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_path, capture_output=True, text=True, check=False
        )

        if result.returncode == 0 and result.stdout.strip():
            # File exists but not committed - return HEAD with marker
            return f"{result.stdout.strip()}-uncommitted"

        return None

    except Exception:
        # Not in a git repo or git not available
        return None


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
        - commit_hash: Git commit hash when summarized
        - prompt_version: Version of prompt used
        - summary: Summary text
        - timestamp: When summary was created
        Returns None if not cached
    """
    summary_path = get_versioned_summary_path(file_path, repo_path)

    if not summary_path.exists():
        return None

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
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
                    "commit_hash": most_recent.get("inputs", {}).get("commit_hash", "not-in-git"),
                    "prompt": most_recent.get("prompt", {"name": "unknown", "version": "unknown"}),
                    "prompt_version": most_recent.get("prompt", {}).get("version", "unknown"),  # For legacy compat
                    "summary": summary_text,
                    "timestamp": most_recent.get("version", ""),  # version IS the timestamp
                }
            else:
                # Old versioned format
                return {"file_path": file_path, **most_recent}

        # Legacy flat format - return as-is
        return data

    except (json.JSONDecodeError, IOError):
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

    # Get git commit hash for inputs
    commit_hash = get_git_commit_hash(file_path, repo_path)

    # Get sanitized name for this file summary with parent directory
    sanitized_filename = sanitize_filepath_to_filename(file_path).replace(".json", "")
    # Include parent directory so it's clear this is a step 2 file
    full_name = f"2_file_summaries/{sanitized_filename}"

    # Create new version entry with standardized structure
    now = datetime.now(timezone.utc).isoformat()
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
            "commit_hash": commit_hash if commit_hash else "not-in-git",
        },
    }

    # Load existing data or create new structure
    summary_path = get_versioned_summary_path(file_path, repo_path)

    if summary_path.exists():
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle legacy formats - convert to new standardized format
            if data and "versions" not in data:
                # Old flat format: convert to new standardized format
                legacy_timestamp = data.get("timestamp", now)
                legacy_version = {
                    "version": legacy_timestamp,  # Use legacy timestamp as version
                    "outputs": {
                        "file_summary": data.get("summary", ""),
                    },
                    "prompt": {
                        "name": f"prompts/{data.get('prompt', {}).get('name', 'unknown')}.json",
                        "version": data.get("prompt", {}).get("version", "unknown"),
                    },
                    "inputs": {
                        "file_path": file_path,
                        "commit_hash": data.get("commit_hash", "not-in-git"),
                    },
                }
                data = {"name": full_name, "versions": [legacy_version]}
            elif data and "versions" in data:
                # Update name field if it's still using old format
                if "file_path" in data and "name" not in data:
                    data["name"] = full_name
                    del data["file_path"]
                elif "name" in data and not data["name"].startswith("2_file_summaries/"):
                    # Update old name format to include parent directory
                    data["name"] = full_name

                # Check if versions are already in new format or need migration
                if data["versions"] and "outputs" not in data["versions"][0]:
                    # Old versioned format - migrate each version
                    migrated_versions = []
                    for old_ver in data["versions"]:
                        old_timestamp = old_ver.get("timestamp", now)
                        migrated = {
                            "version": old_timestamp,  # Use old timestamp as version
                            "outputs": {
                                "file_summary": old_ver.get("summary", ""),
                            },
                            "prompt": {
                                "name": f"prompts/{old_ver.get('prompt', {}).get('name', 'unknown')}.json",
                                "version": old_ver.get("prompt", {}).get("version", "unknown"),
                            },
                            "inputs": {
                                "file_path": file_path,
                                "commit_hash": old_ver.get("commit_hash", "not-in-git"),
                            },
                        }
                        migrated_versions.append(migrated)
                    data["versions"] = migrated_versions
            elif not data:
                # Empty file
                data = {"name": full_name, "versions": []}

        except (json.JSONDecodeError, IOError):
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
