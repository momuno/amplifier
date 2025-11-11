"""
Tests for regenerate command.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from doc_evergreen.commands.regenerate import execute_regenerate, regenerate_single_document
from doc_evergreen.core.history import add_doc_entry, load_history


@patch("doc_evergreen.commands.regenerate.map_sources_to_sections")
@patch("doc_evergreen.commands.regenerate.generate_document_with_mapping")
@patch("doc_evergreen.commands.regenerate.load_builtin_template")
def test_regenerate_single_document_success(mock_load_template, mock_generate, mock_map_sources):
    """Test regenerating a single document."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create source file
        source_file = repo / "src" / "test.py"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("def hello(): pass")

        # Create existing document
        doc_path = repo / "README.md"
        doc_path.write_text("# Old README")

        # Create history
        add_doc_entry(
            doc_path="README.md",
            about="Test README",
            template_name="readme",
            template_path="",
            sources=["src/**/*.py"],
            repo_path=repo,
        )

        # Mock LLM calls
        mock_load_template.return_value = "Template content"
        mock_map_sources.return_value = {"Introduction": ["src/test.py"]}
        mock_generate.return_value = "# New README\n\nGenerated content"

        # Load history to get document config
        history = load_history(repo)
        doc_config = history["docs"]["README.md"]

        # Regenerate
        regenerate_single_document("README.md", doc_config, repo, dry_run=False)

        # Verify document was updated
        assert doc_path.exists()
        content = doc_path.read_text()
        assert content == "# New README\n\nGenerated content"

        # Verify backup was created
        versions_dir = repo / ".doc-evergreen" / "versions"
        assert versions_dir.exists()
        backups = list(versions_dir.glob("README.md.*.bak"))
        assert len(backups) == 1

        # Verify history was updated
        updated_history = load_history(repo)
        assert len(updated_history["docs"]["README.md"]["previous_versions"]) == 1


@patch("doc_evergreen.commands.regenerate.click.echo")
def test_regenerate_single_document_dry_run(mock_echo):
    """Test dry run mode for single document."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create minimal config
        doc_config = {
            "path": "README.md",
            "sources": ["src/**/*.py"],
            "about": "Test",
            "template_used": {"name": "readme"},
        }

        # Dry run should not error and should just print
        regenerate_single_document("README.md", doc_config, repo, dry_run=True)

        # Verify echo was called with dry run message
        call_args = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("[DRY RUN]" in arg for arg in call_args)


@patch("doc_evergreen.commands.regenerate.click.echo")
def test_regenerate_single_document_no_template(mock_echo):
    """Test regeneration fails gracefully when no template info."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Config without template info
        doc_config = {
            "path": "README.md",
            "sources": ["src/**/*.py"],
            "about": "Test",
        }

        # Should handle gracefully
        regenerate_single_document("README.md", doc_config, repo, dry_run=False)

        # Verify error message was shown
        call_args = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("No template information" in arg for arg in call_args)


@patch("doc_evergreen.commands.regenerate.map_sources_to_sections")
@patch("doc_evergreen.commands.regenerate.generate_document_with_mapping")
@patch("doc_evergreen.commands.regenerate.load_builtin_template")
def test_regenerate_single_document_no_sources(mock_load_template, mock_generate, mock_map_sources):
    """Test regeneration handles missing source files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Config with patterns that don't match anything
        doc_config = {
            "path": "README.md",
            "sources": ["nonexistent/**/*.py"],
            "about": "Test",
            "template_used": {"name": "readme"},
        }

        mock_load_template.return_value = "Template"

        # Should handle gracefully and return early
        regenerate_single_document("README.md", doc_config, repo, dry_run=False)

        # Generate should not be called if no sources
        mock_generate.assert_not_called()
        # Map sources should also not be called
        mock_map_sources.assert_not_called()


@patch("doc_evergreen.commands.regenerate.regenerate_single_document")
def test_execute_regenerate_single_doc(mock_regenerate):
    """Test execute_regenerate for single document."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create document and history
        doc_path = repo / "README.md"
        doc_path.write_text("# README")

        add_doc_entry(
            doc_path="README.md",
            about="Test",
            template_name="readme",
            template_path="",
            sources=["src/**/*.py"],
            repo_path=repo,
        )

        # Change to temp directory
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(repo)

            # Execute regenerate
            execute_regenerate(doc_path=doc_path, regenerate_all=False, dry_run=False)

            # Verify regenerate_single_document was called
            mock_regenerate.assert_called_once()

        finally:
            os.chdir(original_cwd)


@patch("doc_evergreen.commands.regenerate.regenerate_single_document")
def test_execute_regenerate_all(mock_regenerate):
    """Test execute_regenerate for all documents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create multiple documents
        for name in ["README.md", "API.md", "GUIDE.md"]:
            doc_path = repo / name
            doc_path.write_text(f"# {name}")

            add_doc_entry(
                doc_path=name,
                about=f"Test {name}",
                template_name="readme",
                template_path="",
                sources=["src/**/*.py"],
                repo_path=repo,
            )

        # Change to temp directory
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(repo)

            # Execute regenerate all
            execute_regenerate(doc_path=None, regenerate_all=True, dry_run=False)

            # Verify regenerate_single_document was called 3 times
            assert mock_regenerate.call_count == 3

        finally:
            os.chdir(original_cwd)


def test_execute_regenerate_dry_run_all():
    """Test dry run mode for regenerate all."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create documents
        for name in ["README.md", "API.md"]:
            add_doc_entry(
                doc_path=name,
                about=f"Test {name}",
                template_name="readme",
                template_path="",
                sources=["src/**/*.py"],
                repo_path=repo,
            )

        # Change to temp directory
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(repo)

            # Dry run should not error
            execute_regenerate(doc_path=None, regenerate_all=True, dry_run=True)

        finally:
            os.chdir(original_cwd)


def test_execute_regenerate_no_history():
    """Test execute_regenerate handles missing history gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Change to temp directory (no history exists)
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(repo)

            # Should handle gracefully
            execute_regenerate(doc_path=None, regenerate_all=True, dry_run=False)

        finally:
            os.chdir(original_cwd)


def test_execute_regenerate_doc_not_found():
    """Test execute_regenerate handles unknown document."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create history with one document
        add_doc_entry(
            doc_path="README.md",
            about="Test",
            template_name="readme",
            template_path="",
            sources=["src/**/*.py"],
            repo_path=repo,
        )

        # Change to temp directory
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(repo)

            # Try to regenerate unknown document
            execute_regenerate(doc_path=Path("UNKNOWN.md"), regenerate_all=False, dry_run=False)

        finally:
            os.chdir(original_cwd)


def test_execute_regenerate_no_doc_path_or_all():
    """Test execute_regenerate requires doc_path or --all flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Add at least one document to history so it doesn't exit early
        add_doc_entry(
            doc_path="README.md",
            about="Test",
            template_name="readme",
            template_path="",
            sources=["src/**/*.py"],
            repo_path=repo,
        )

        # Change to temp directory
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(repo)

            # Should raise error
            with pytest.raises(ValueError, match="Must specify document path"):
                execute_regenerate(doc_path=None, regenerate_all=False, dry_run=False)

        finally:
            os.chdir(original_cwd)
