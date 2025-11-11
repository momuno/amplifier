"""
Tests for history.yaml management.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from doc_evergreen.core.history import (
    add_doc_entry,
    add_version_entry,
    ensure_doc_evergreen_dir,
    get_doc_config,
    get_doc_evergreen_dir,
    get_history_path,
    list_all_docs,
    load_history,
    remove_doc_entry,
    save_history,
)


@pytest.fixture
def temp_repo():
    """Create a temporary repository directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_get_doc_evergreen_dir(temp_repo):
    """Test getting .doc-evergreen directory path."""
    doc_dir = get_doc_evergreen_dir(temp_repo)
    assert doc_dir == temp_repo / ".doc-evergreen"


def test_get_history_path(temp_repo):
    """Test getting history.yaml file path."""
    history_path = get_history_path(temp_repo)
    assert history_path == temp_repo / ".doc-evergreen" / "history.yaml"


def test_ensure_doc_evergreen_dir(temp_repo):
    """Test creating .doc-evergreen directory structure."""
    ensure_doc_evergreen_dir(temp_repo)

    doc_dir = temp_repo / ".doc-evergreen"
    assert doc_dir.exists()
    assert doc_dir.is_dir()
    assert (doc_dir / "templates").exists()
    assert (doc_dir / "versions").exists()


def test_load_history_creates_empty(temp_repo):
    """Test loading history when file doesn't exist creates empty structure."""
    history = load_history(temp_repo)

    assert isinstance(history, dict)
    assert "docs" in history
    assert history["docs"] == {}


def test_load_history_existing(temp_repo):
    """Test loading existing history file."""
    ensure_doc_evergreen_dir(temp_repo)
    history_path = get_history_path(temp_repo)

    # Create a history file
    test_data = {
        "docs": {
            "README.md": {
                "created": "2025-01-07T10:00:00+00:00",
                "last_generated": "2025-01-07T10:00:00+00:00",
                "path": "README.md",
                "template_used": {"name": "readme", "path": ".doc-evergreen/templates/readme.v1.md"},
                "previous_versions": [],
                "sources": ["src/**/*.py"],
                "about": "Main README",
            }
        }
    }

    with open(history_path, "w", encoding="utf-8") as f:
        yaml.dump(test_data, f)

    # Load and verify
    history = load_history(temp_repo)

    assert "docs" in history
    assert "README.md" in history["docs"]
    assert history["docs"]["README.md"]["about"] == "Main README"


def test_save_history(temp_repo):
    """Test saving history file."""
    test_history = {
        "docs": {
            "README.md": {
                "created": "2025-01-07T10:00:00+00:00",
                "last_generated": "2025-01-07T10:00:00+00:00",
                "path": "README.md",
                "template_used": {"name": "readme", "path": ".doc-evergreen/templates/readme.v1.md"},
                "previous_versions": [],
                "sources": ["src/**/*.py"],
                "about": "Main README",
            }
        }
    }

    save_history(test_history, temp_repo)

    # Verify file was created
    history_path = get_history_path(temp_repo)
    assert history_path.exists()

    # Verify contents
    with open(history_path, "r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)

    assert loaded["docs"]["README.md"]["about"] == "Main README"


def test_save_history_validation(temp_repo):
    """Test that save_history validates structure."""
    # Invalid: not a dict
    with pytest.raises(ValueError, match="must be a dictionary"):
        save_history("invalid", temp_repo)  # type: ignore[arg-type]

    # Invalid: missing 'docs' key
    with pytest.raises(ValueError, match="must contain 'docs' key"):
        save_history({}, temp_repo)

    # Invalid: 'docs' not a dict
    with pytest.raises(ValueError, match="must be a dictionary"):
        save_history({"docs": "invalid"}, temp_repo)


def test_get_doc_config_exists(temp_repo):
    """Test getting configuration for existing document."""
    # Create history
    test_history = {
        "docs": {
            "README.md": {
                "created": "2025-01-07T10:00:00+00:00",
                "last_generated": "2025-01-07T10:00:00+00:00",
                "path": "README.md",
                "template_used": {"name": "readme", "path": ".doc-evergreen/templates/readme.v1.md"},
                "previous_versions": [],
                "sources": ["src/**/*.py"],
                "about": "Main README",
            }
        }
    }
    save_history(test_history, temp_repo)

    # Get config
    config = get_doc_config("README.md", temp_repo)

    assert config is not None
    assert config["about"] == "Main README"
    assert config["sources"] == ["src/**/*.py"]


def test_get_doc_config_not_exists(temp_repo):
    """Test getting configuration for non-existent document."""
    config = get_doc_config("NONEXISTENT.md", temp_repo)
    assert config is None


def test_add_doc_entry_new(temp_repo):
    """Test adding new document entry."""
    add_doc_entry(
        doc_path="README.md",
        about="Main project README",
        template_name="readme-custom",
        template_path=".doc-evergreen/templates/readme-custom.v1.md",
        sources=["src/**/*.py", "pyproject.toml"],
        repo_path=temp_repo,
    )

    # Verify entry was added
    config = get_doc_config("README.md", temp_repo)

    assert config is not None
    assert config["about"] == "Main project README"
    assert config["path"] == "README.md"
    assert config["template_used"]["name"] == "readme-custom"
    assert config["template_used"]["path"] == ".doc-evergreen/templates/readme-custom.v1.md"
    assert config["sources"] == ["src/**/*.py", "pyproject.toml"]
    assert "created" in config
    assert "last_generated" in config
    assert config["previous_versions"] == []


def test_add_doc_entry_update(temp_repo):
    """Test updating existing document entry."""
    # Add initial entry
    add_doc_entry(
        doc_path="README.md",
        about="Initial description",
        template_name="readme",
        template_path=".doc-evergreen/templates/readme.v1.md",
        sources=["src/**/*.py"],
        repo_path=temp_repo,
    )

    initial_config = get_doc_config("README.md", temp_repo)
    assert initial_config is not None
    initial_created = initial_config["created"]

    # Update entry
    add_doc_entry(
        doc_path="README.md",
        about="Updated description",
        template_name="readme-v2",
        template_path=".doc-evergreen/templates/readme.v2.md",
        sources=["src/**/*.py", "docs/**/*.md"],
        repo_path=temp_repo,
    )

    # Verify update
    config = get_doc_config("README.md", temp_repo)
    assert config is not None

    assert config["about"] == "Updated description"
    assert config["template_used"]["name"] == "readme-v2"
    assert config["sources"] == ["src/**/*.py", "docs/**/*.md"]
    assert config["created"] == initial_created  # Created time shouldn't change
    assert config["last_generated"] != initial_created  # Last generated should update


def test_add_version_entry(temp_repo):
    """Test adding version entry to document."""
    # First add a document
    add_doc_entry(
        doc_path="README.md",
        about="Main README",
        template_name="readme",
        template_path=".doc-evergreen/templates/readme.v1.md",
        sources=["src/**/*.py"],
        repo_path=temp_repo,
    )

    # Add version entry
    add_version_entry(
        doc_path="README.md",
        backup_path=".doc-evergreen/versions/README.md.2025-01-07T10-00-00.bak",
        template_name="readme",
        template_path=".doc-evergreen/templates/readme.v1.md",
        sources=["src/**/*.py", "tests/**/*.py"],
        repo_path=temp_repo,
    )

    # Verify version was added
    config = get_doc_config("README.md", temp_repo)
    assert config is not None

    assert len(config["previous_versions"]) == 1
    version = config["previous_versions"][0]
    assert "timestamp" in version
    assert version["backup_path"] == ".doc-evergreen/versions/README.md.2025-01-07T10-00-00.bak"
    assert version["template_used"]["name"] == "readme"
    assert version["sources"] == ["src/**/*.py", "tests/**/*.py"]
    # Also verify current sources were updated
    assert config["sources"] == ["src/**/*.py", "tests/**/*.py"]


def test_add_version_entry_nonexistent_doc(temp_repo):
    """Test adding version entry for non-existent document fails."""
    with pytest.raises(ValueError, match="not found in history"):
        add_version_entry(
            doc_path="NONEXISTENT.md",
            backup_path=".doc-evergreen/versions/NONEXISTENT.md.2025-01-07T10-00-00.bak",
            template_name="test",
            template_path=".doc-evergreen/templates/test.v1.md",
            sources=["src/**/*.py"],
            repo_path=temp_repo,
        )


def test_list_all_docs_empty(temp_repo):
    """Test listing documents when history is empty."""
    docs = list_all_docs(temp_repo)
    assert docs == []


def test_list_all_docs(temp_repo):
    """Test listing all configured documents."""
    # Add multiple documents
    add_doc_entry(
        doc_path="README.md",
        about="Main README",
        template_name="readme",
        template_path=".doc-evergreen/templates/readme.v1.md",
        sources=["src/**/*.py"],
        repo_path=temp_repo,
    )

    add_doc_entry(
        doc_path="docs/API.md",
        about="API docs",
        template_name="api-reference",
        template_path=".doc-evergreen/templates/api-reference.v1.md",
        sources=["src/api/**/*.py"],
        repo_path=temp_repo,
    )

    # List all
    docs = list_all_docs(temp_repo)

    assert len(docs) == 2
    assert "README.md" in docs
    assert "docs/API.md" in docs


def test_remove_doc_entry(temp_repo):
    """Test removing document from history."""
    # Add document
    add_doc_entry(
        doc_path="README.md",
        about="Main README",
        template_name="readme",
        template_path=".doc-evergreen/templates/readme.v1.md",
        sources=["src/**/*.py"],
        repo_path=temp_repo,
    )

    # Verify it exists
    assert get_doc_config("README.md", temp_repo) is not None

    # Remove it
    remove_doc_entry("README.md", temp_repo)

    # Verify it's gone
    assert get_doc_config("README.md", temp_repo) is None


def test_remove_doc_entry_nonexistent(temp_repo):
    """Test removing non-existent document doesn't error."""
    # Should not raise an error
    remove_doc_entry("NONEXISTENT.md", temp_repo)
