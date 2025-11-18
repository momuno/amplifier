"""
Integration tests for Sprint 4 CLI source control features.

Tests the CLI interface for:
- --sources/-s: Override default sources
- --exclude/-e: Exclude patterns
- --add-sources/-a: Add to defaults
- --show-sources: Preview without generating
"""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from doc_evergreen.cli import doc_update

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def runner():
    """Provide Click test runner."""
    return CliRunner()


@pytest.fixture
def test_files(tmp_path):
    """
    Create test file structure.

    Structure:
    tmp_path/
      src/
        core.py
        utils.py
      tests/
        test_core.py
      docs/
        guide.md
      README.md
      .env (should be excluded by default)
    """
    # Source files
    src = tmp_path / "src"
    src.mkdir()
    (src / "core.py").write_text("# Core implementation")
    (src / "utils.py").write_text("# Utilities")

    # Test files
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_core.py").write_text("# Tests")

    # Documentation
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# User Guide")

    # Root files
    (tmp_path / "README.md").write_text("# Project")
    (tmp_path / ".env").write_text("SECRET=value")

    return tmp_path


# ============================================================================
# Class 1: TestCLISourceOptions
# ============================================================================


class TestCLISourceOptions:
    """Test that CLI accepts all source control options."""

    def test_cli_accepts_sources_option(self, runner):
        """
        Given: CLI with --sources option
        When: User provides specific source files
        Then: CLI accepts the option without error
        """
        result = runner.invoke(doc_update, ["--sources", "README.md,src/core.py", "README.md"])

        # Should not fail with "no such option" error
        assert "no such option" not in result.output.lower()

    def test_cli_accepts_exclude_option(self, runner):
        """
        Given: CLI with --exclude option
        When: User provides exclusion patterns
        Then: CLI accepts the option without error
        """
        result = runner.invoke(doc_update, ["--exclude", "*.pyc,test_*", "README.md"])

        assert "no such option" not in result.output.lower()

    def test_cli_accepts_add_sources_option(self, runner):
        """
        Given: CLI with --add-sources option
        When: User provides additional sources
        Then: CLI accepts the option without error
        """
        result = runner.invoke(doc_update, ["--add-sources", "docs/*.md", "README.md"])

        assert "no such option" not in result.output.lower()

    def test_cli_accepts_show_sources_flag(self, runner):
        """
        Given: CLI with --show-sources flag
        When: User requests source preview
        Then: CLI accepts the flag without error
        """
        result = runner.invoke(doc_update, ["--show-sources"])

        assert "no such option" not in result.output.lower()


# ============================================================================
# Class 2: TestSourceResolutionIntegration
# ============================================================================


class TestSourceResolutionIntegration:
    """Test that CLI options integrate correctly with source resolution."""

    def test_sources_option_passed_to_resolver(self, runner, test_files, tmp_path):
        """
        Given: Project with default source structure
        When: User specifies --sources explicitly
        Then: Source resolver is called with CLI sources
        """
        target = test_files / "README.md"

        with (
            patch("doc_evergreen.cli.resolve_sources") as mock_resolve,
            patch("doc_evergreen.cli.generate_preview"),
        ):
            mock_resolve.return_value = [str(target)]

            runner.invoke(doc_update, ["--sources", "README.md,src/core.py", str(target)], obj={"cwd": str(test_files)})

            # Verify resolve_sources was called with cli_sources
            assert mock_resolve.called
            call_args = mock_resolve.call_args
            assert call_args[1].get("cli_sources") is not None

    def test_add_sources_option_passed_to_resolver(self, runner, test_files):
        """
        Given: Project with default sources
        When: User uses --add-sources
        Then: Source resolver is called with add_sources parameter
        """
        target = test_files / "README.md"

        with (
            patch("doc_evergreen.cli.resolve_sources") as mock_resolve,
            patch("doc_evergreen.cli.generate_preview"),
        ):
            mock_resolve.return_value = [str(target)]

            runner.invoke(doc_update, ["--add-sources", "docs/guide.md", str(target)])

            assert mock_resolve.called
            call_args = mock_resolve.call_args
            assert call_args[1].get("add_sources") is not None

    def test_sources_passed_to_context_gathering(self, runner, test_files):
        """
        Given: CLI with source options
        When: Documentation generation is triggered
        Then: Resolved sources are passed to context gathering
        """
        target = test_files / "README.md"

        with (
            patch("doc_evergreen.cli.gather_context") as mock_context,
            patch("doc_evergreen.cli.generate_preview"),
            patch("doc_evergreen.cli.resolve_sources") as mock_resolve,
        ):
            mock_resolve.return_value = [str(target)]
            mock_context.return_value = "# Context"

            runner.invoke(doc_update, ["--sources", "README.md", str(target), "--no-review"])

            # Verify gather_context was called with sources
            assert mock_context.called
            call_args = mock_context.call_args
            # Should have sources parameter
            assert len(call_args[0]) > 0 or "sources" in call_args[1]


# ============================================================================
# Class 3: TestShowSourcesPreview
# ============================================================================


class TestShowSourcesPreview:
    """Test --show-sources preview functionality."""

    def test_show_sources_displays_file_list(self, runner, test_files):
        """
        Given: Project with source files
        When: User runs --show-sources
        Then: List of resolved sources is displayed
        """
        with patch("doc_evergreen.cli.resolve_sources") as mock_resolve:
            mock_resolve.return_value = [str(test_files / "README.md"), str(test_files / "src" / "core.py")]

            result = runner.invoke(doc_update, ["--show-sources"])

            assert result.exit_code == 0

            # Should show source files
            assert "README.md" in result.output
            assert "core.py" in result.output

    def test_show_sources_does_not_generate_doc(self, runner, test_files):
        """
        Given: --show-sources flag
        When: Command is executed
        Then: No documentation is generated
        """
        with (
            patch("doc_evergreen.cli.resolve_sources") as mock_resolve,
            patch("doc_evergreen.cli.generate_preview") as mock_gen,
        ):
            mock_resolve.return_value = [str(test_files / "README.md")]

            result = runner.invoke(doc_update, ["--show-sources"])

            assert result.exit_code == 0

            # generate_preview should NOT be called
            assert not mock_gen.called

    def test_show_sources_shows_file_sizes(self, runner, test_files):
        """
        Given: --show-sources with resolved files
        When: Sources are displayed
        Then: File sizes or counts are shown
        """
        with patch("doc_evergreen.cli.resolve_sources") as mock_resolve:
            mock_resolve.return_value = [str(test_files / "README.md")]

            result = runner.invoke(doc_update, ["--show-sources"])

            assert result.exit_code == 0

            # Should show some kind of summary
            output_lower = result.output.lower()
            has_summary = any(word in output_lower for word in ["total", "files", "sources", "found"])
            assert has_summary


# ============================================================================
# Integration Test: Full Workflow
# ============================================================================


class TestFullSourceControlWorkflow:
    """Test complete workflows combining multiple options."""

    def test_exclude_with_add_sources(self, runner, test_files):
        """
        Given: User adds sources and excludes patterns
        When: Both options are combined
        Then: Both options are passed to resolver
        """
        target = test_files / "README.md"

        with (
            patch("doc_evergreen.cli.resolve_sources") as mock_resolve,
            patch("doc_evergreen.cli.generate_preview"),
        ):
            mock_resolve.return_value = [str(target)]

            runner.invoke(
                doc_update, ["--add-sources", "docs/guide.md", "--exclude", "*.py", str(target), "--no-review"]
            )

            assert mock_resolve.called
            call_args = mock_resolve.call_args[1]

            # Both options should be passed
            assert "add_sources" in call_args
            assert "exclusions" in call_args or "exclude" in call_args
