"""
History management for doc-evergreen.

Handles reading, writing, and querying the .doc-evergreen/history.yaml file
which tracks all document configurations and version history.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def get_doc_evergreen_dir(repo_path: Path) -> Path:
    """
    Get the .doc-evergreen directory path.

    Args:
        repo_path: Path to repository root

    Returns:
        Path to .doc-evergreen directory
    """
    return repo_path / ".doc-evergreen"


def get_history_path(repo_path: Path) -> Path:
    """
    Get the history.yaml file path.

    Args:
        repo_path: Path to repository root

    Returns:
        Path to history.yaml file
    """
    return get_doc_evergreen_dir(repo_path) / "history.yaml"


def ensure_doc_evergreen_dir(repo_path: Path) -> None:
    """
    Ensure .doc-evergreen directory exists.

    Args:
        repo_path: Path to repository root
    """
    doc_dir = get_doc_evergreen_dir(repo_path)
    doc_dir.mkdir(parents=True, exist_ok=True)

    # Also create subdirectories
    (doc_dir / "templates").mkdir(exist_ok=True)
    (doc_dir / "versions").mkdir(exist_ok=True)
    (doc_dir / "source-maps").mkdir(exist_ok=True)


def load_history(repo_path: Path) -> dict[str, Any]:
    """
    Load history.yaml, create if doesn't exist.

    Args:
        repo_path: Path to repository root

    Returns:
        Dictionary containing history data
    """
    history_path = get_history_path(repo_path)

    if not history_path.exists():
        # Create empty history
        return {"docs": {}}

    try:
        with open(history_path, "r", encoding="utf-8") as f:
            history = yaml.safe_load(f)

        # Validate structure
        if history is None:
            return {"docs": {}}

        if not isinstance(history, dict):
            raise ValueError("History file must contain a dictionary")

        if "docs" not in history:
            history["docs"] = {}

        return history

    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse history.yaml: {e}")


def save_history(history: dict[str, Any], repo_path: Path) -> None:
    """
    Save history.yaml with validation.

    Args:
        history: Dictionary containing history data
        repo_path: Path to repository root
    """
    # Validate structure
    if not isinstance(history, dict):
        raise ValueError("History must be a dictionary")

    if "docs" not in history:
        raise ValueError("History must contain 'docs' key")

    if not isinstance(history["docs"], dict):
        raise ValueError("History['docs'] must be a dictionary")

    # Ensure directory exists
    ensure_doc_evergreen_dir(repo_path)

    # Write to file
    history_path = get_history_path(repo_path)

    with open(history_path, "w", encoding="utf-8") as f:
        yaml.dump(history, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def get_doc_config(doc_path: str, repo_path: Path) -> dict[str, Any] | None:
    """
    Get configuration for specific document.

    Args:
        doc_path: Path to document (relative to repo root)
        repo_path: Path to repository root

    Returns:
        Document configuration dictionary, or None if not found
    """
    history = load_history(repo_path)

    return history["docs"].get(doc_path)


def add_doc_entry(
    doc_path: str,
    about: str,
    template_name: str,
    template_path: str,
    sources: list[str],
    repo_path: Path,
    source_map_path: str = "",
) -> None:
    """
    Add or update document configuration.

    Args:
        doc_path: Path to document (relative to repo root)
        about: Description of what the document covers
        template_name: Name of the template used
        template_path: Path to the template file
        sources: List of source file glob patterns
        repo_path: Path to repository root
        source_map_path: Path to source mapping file (relative to repo root)
    """
    history = load_history(repo_path)

    now = datetime.now(timezone.utc).isoformat()

    # Check if this is an update or new entry
    if doc_path in history["docs"]:
        # Update existing entry
        history["docs"][doc_path]["last_generated"] = now
        history["docs"][doc_path]["template_used"] = {
            "name": template_name,
            "path": template_path,
        }
        history["docs"][doc_path]["sources"] = sources
        history["docs"][doc_path]["about"] = about
        if source_map_path:
            history["docs"][doc_path]["source_map_path"] = source_map_path
    else:
        # New entry
        entry = {
            "created": now,
            "last_generated": now,
            "path": doc_path,
            "template_used": {
                "name": template_name,
                "path": template_path,
            },
            "previous_versions": [],
            "sources": sources,
            "about": about,
        }
        if source_map_path:
            entry["source_map_path"] = source_map_path
        history["docs"][doc_path] = entry

    save_history(history, repo_path)


def add_version_entry(
    doc_path: str,
    backup_path: str,
    template_name: str,
    template_path: str,
    sources: list[str],
    repo_path: Path,
    source_map_path: str = "",
) -> None:
    """
    Add version entry to document history.

    Args:
        doc_path: Path to document (relative to repo root)
        backup_path: Path to backup file
        template_name: Name of template used for this version
        template_path: Path to template file
        sources: List of source file patterns or paths used for this version
        repo_path: Path to repository root
        source_map_path: Path to source mapping file (relative to repo root)
    """
    history = load_history(repo_path)

    if doc_path not in history["docs"]:
        raise ValueError(f"Document {doc_path} not found in history")

    now = datetime.now(timezone.utc).isoformat()

    version_entry = {
        "timestamp": now,
        "backup_path": backup_path,
        "template_used": {
            "name": template_name,
            "path": template_path,
        },
        "sources": sources,
    }
    if source_map_path:
        version_entry["source_map_path"] = source_map_path

    history["docs"][doc_path]["previous_versions"].append(version_entry)
    history["docs"][doc_path]["last_generated"] = now
    # Also update current sources to match this version
    history["docs"][doc_path]["sources"] = sources
    if source_map_path:
        history["docs"][doc_path]["source_map_path"] = source_map_path

    save_history(history, repo_path)


def list_all_docs(repo_path: Path) -> list[str]:
    """
    List all configured documents.

    Args:
        repo_path: Path to repository root

    Returns:
        List of document paths
    """
    history = load_history(repo_path)
    return list(history["docs"].keys())


def remove_doc_entry(doc_path: str, repo_path: Path) -> None:
    """
    Remove document from history.

    Args:
        doc_path: Path to document (relative to repo root)
        repo_path: Path to repository root
    """
    history = load_history(repo_path)

    if doc_path in history["docs"]:
        del history["docs"][doc_path]
        save_history(history, repo_path)
