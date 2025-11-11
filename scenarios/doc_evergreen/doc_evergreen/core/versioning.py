"""
Document versioning and backup for doc-evergreen.

Handles backing up existing documents before regeneration.
"""

from datetime import datetime, timezone
from pathlib import Path


def get_versions_dir(repo_path: Path) -> Path:
    """
    Get the versions directory path.

    Args:
        repo_path: Repository root path

    Returns:
        Path to .doc-evergreen/versions/
    """
    return repo_path / ".doc-evergreen" / "versions"


def ensure_versions_dir(repo_path: Path) -> Path:
    """
    Ensure versions directory exists.

    Args:
        repo_path: Repository root path

    Returns:
        Path to versions directory
    """
    versions_dir = get_versions_dir(repo_path)
    versions_dir.mkdir(parents=True, exist_ok=True)
    return versions_dir


def create_backup_path(doc_path: Path, repo_path: Path) -> Path:
    """
    Create backup path for a document.

    Format: .doc-evergreen/versions/{filename}.{timestamp}.bak

    Args:
        doc_path: Path to document being backed up
        repo_path: Repository root path

    Returns:
        Path to backup file
    """
    # Get timestamp in ISO format (safe for filenames)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

    # Create backup filename
    backup_name = f"{doc_path.name}.{timestamp}.bak"

    # Full path
    versions_dir = get_versions_dir(repo_path)
    return versions_dir / backup_name


def backup_document(doc_path: Path, repo_path: Path) -> Path | None:
    """
    Backup an existing document before regeneration.

    Args:
        doc_path: Path to document to backup
        repo_path: Repository root path

    Returns:
        Path to backup file, or None if document doesn't exist
    """
    # Check if document exists
    if not doc_path.exists():
        return None

    # Ensure versions directory exists
    ensure_versions_dir(repo_path)

    # Create backup path
    backup_path = create_backup_path(doc_path, repo_path)

    # Copy file to backup location
    import shutil

    shutil.copy2(doc_path, backup_path)

    return backup_path
