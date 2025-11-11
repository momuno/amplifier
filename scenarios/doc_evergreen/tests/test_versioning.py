"""
Tests for document versioning and backup.
"""

import tempfile
from pathlib import Path

from doc_evergreen.core.versioning import (
    backup_document,
    create_backup_path,
    ensure_versions_dir,
    get_versions_dir,
)


def test_get_versions_dir():
    """Test getting versions directory path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        versions_dir = get_versions_dir(repo)

        # Should be .doc-evergreen/versions/
        assert versions_dir == repo / ".doc-evergreen" / "versions"


def test_ensure_versions_dir():
    """Test creating versions directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Directory shouldn't exist yet
        versions_dir = get_versions_dir(repo)
        assert not versions_dir.exists()

        # Ensure directory exists
        result = ensure_versions_dir(repo)

        # Should create directory
        assert result.exists()
        assert result.is_dir()
        assert result == versions_dir


def test_ensure_versions_dir_idempotent():
    """Test that ensure_versions_dir can be called multiple times."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Call twice
        result1 = ensure_versions_dir(repo)
        result2 = ensure_versions_dir(repo)

        # Should return same path
        assert result1 == result2
        assert result1.exists()


def test_create_backup_path():
    """Test creating backup path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        doc_path = repo / "README.md"

        backup_path = create_backup_path(doc_path, repo)

        # Should be in versions directory
        assert backup_path.parent == get_versions_dir(repo)

        # Should start with original filename
        assert backup_path.name.startswith("README.md.")

        # Should end with .bak
        assert backup_path.name.endswith(".bak")

        # Should contain timestamp
        assert "T" in backup_path.name  # ISO format has T


def test_create_backup_path_timestamp_format():
    """Test backup path timestamp format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        doc_path = repo / "test.md"

        backup_path = create_backup_path(doc_path, repo)

        # Extract timestamp part
        # Format: test.md.{timestamp}.bak
        parts = backup_path.name.split(".")
        # Should be: ['test', 'md', '{timestamp}', 'bak']
        assert len(parts) == 4
        timestamp = parts[2]

        # Should match format: YYYY-MM-DDTHH-MM-SS
        assert len(timestamp) == 19
        assert timestamp[4] == "-"  # Year-month separator
        assert timestamp[7] == "-"  # Month-day separator
        assert timestamp[10] == "T"  # Date-time separator
        assert timestamp[13] == "-"  # Hour-minute separator
        assert timestamp[16] == "-"  # Minute-second separator


def test_backup_document_success():
    """Test backing up an existing document."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create a document to backup
        doc_path = repo / "test.md"
        doc_content = "# Test Document\n\nSome content here."
        doc_path.write_text(doc_content)

        # Backup the document
        backup_path = backup_document(doc_path, repo)

        # Should return a path
        assert backup_path is not None

        # Backup file should exist
        assert backup_path.exists()

        # Backup should contain same content
        assert backup_path.read_text() == doc_content

        # Original should still exist
        assert doc_path.exists()
        assert doc_path.read_text() == doc_content


def test_backup_document_nonexistent():
    """Test backing up non-existent document."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Try to backup non-existent file
        doc_path = repo / "nonexistent.md"
        backup_path = backup_document(doc_path, repo)

        # Should return None
        assert backup_path is None


def test_backup_document_creates_versions_dir():
    """Test that backup creates versions directory if needed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create document
        doc_path = repo / "test.md"
        doc_path.write_text("Content")

        # Versions dir shouldn't exist yet
        versions_dir = get_versions_dir(repo)
        assert not versions_dir.exists()

        # Backup document
        backup_path = backup_document(doc_path, repo)

        # Versions dir should now exist
        assert versions_dir.exists()
        assert backup_path is not None
        assert backup_path.exists()


def test_backup_document_preserves_metadata():
    """Test that backup preserves file metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create document
        doc_path = repo / "test.md"
        doc_path.write_text("Content")

        # Get original modification time
        original_mtime = doc_path.stat().st_mtime

        # Backup document
        backup_path = backup_document(doc_path, repo)

        # Backup should have same modification time
        assert backup_path is not None
        backup_mtime = backup_path.stat().st_mtime

        # shutil.copy2 preserves metadata
        assert backup_mtime == original_mtime


def test_backup_document_nested_path():
    """Test backing up document in nested directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create nested directory structure
        nested_dir = repo / "docs" / "api"
        nested_dir.mkdir(parents=True)

        # Create document
        doc_path = nested_dir / "endpoints.md"
        doc_path.write_text("API endpoints")

        # Backup document
        backup_path = backup_document(doc_path, repo)

        # Should succeed
        assert backup_path is not None
        assert backup_path.exists()

        # Backup should be in versions dir (not nested)
        assert backup_path.parent == get_versions_dir(repo)

        # Filename should be preserved
        assert backup_path.name.startswith("endpoints.md.")


def test_multiple_backups_unique_names():
    """Test that multiple backups get unique filenames."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create document
        doc_path = repo / "test.md"
        doc_path.write_text("Version 1")

        # Create first backup
        backup1 = backup_document(doc_path, repo)

        # Modify document
        doc_path.write_text("Version 2")

        # Create second backup (delay to ensure different timestamp)
        import time

        time.sleep(1.1)  # Need >1 second for timestamp to differ
        backup2 = backup_document(doc_path, repo)

        # Both should exist
        assert backup1 is not None
        assert backup2 is not None
        assert backup1.exists()
        assert backup2.exists()

        # Should have different names (different timestamps)
        assert backup1.name != backup2.name

        # Should have different content
        assert backup1.read_text() == "Version 1"
        assert backup2.read_text() == "Version 2"
