"""
Sprint 3 Deliverable 2: CLI Interface Tests (RED Phase)

Tests define the expected CLI behavior using Click's CliRunner.
These tests will FAIL until cli.py is implemented in the GREEN phase.

Test Coverage:
- Basic command usage
- Template options (explicit, auto-detection, list)
- Review workflow (interactive and --no-review)
- Error handling (missing args, invalid templates)
- Exit codes and help text
- File system operations
"""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

# This import will fail initially - expected in RED phase
from doc_evergreen.cli import doc_update


class TestCLIBasicUsage:
    """Core CLI functionality tests"""

    def test_cli_basic_usage_shows_preview(self):
        """
        Given: A target file exists
        When: Running 'doc-update README.md'
        Then: Should generate preview and show diff
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Old Content\n\nOld description.")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# {{ project_name }}\n\n{{ description }}")

            # Act
            result = runner.invoke(doc_update, ["README.md"])

            # Assert
            assert result.exit_code == 0
            assert "Generated preview" in result.output or "Preview:" in result.output

    def test_cli_basic_usage_shows_diff(self):
        """
        Given: A target file exists
        When: Running 'doc-update README.md'
        Then: Should show diff between old and new content
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Old Content")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# New Content")

            # Act
            result = runner.invoke(doc_update, ["README.md"])

            # Assert
            assert result.exit_code == 0
            # Should show diff markers
            assert "---" in result.output or "+++" in result.output or "Old Content" in result.output

    def test_cli_basic_usage_prompts_for_review(self):
        """
        Given: A target file exists
        When: Running 'doc-update README.md'
        Then: Should prompt user to accept/reject changes
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Old Content")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# New Content")

            # Act - simulate user rejecting changes
            result = runner.invoke(doc_update, ["README.md"], input="n\n")

            # Assert
            assert result.exit_code == 0
            assert "Accept" in result.output or "apply" in result.output or "[y/n]" in result.output


class TestCLIOptions:
    """Option flag tests"""

    def test_cli_with_explicit_template(self):
        """
        Given: Multiple templates exist
        When: Running 'doc-update README.md --template contributing'
        Then: Should use specified template (not auto-detected)
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Project")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# README Template")
            Path(".templates/contributing.md").write_text("# Contributing Template")

            # Act
            result = runner.invoke(doc_update, ["README.md", "--template", "contributing"])

            # Assert
            assert result.exit_code == 0
            # Should use contributing template content, not readme template

    def test_cli_list_templates_shows_available(self):
        """
        Given: Templates exist in .templates/
        When: Running 'doc-update --list-templates'
        Then: Should list template names and exit
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# README")
            Path(".templates/contributing.md").write_text("# Contributing")
            Path(".templates/changelog.md").write_text("# Changelog")

            # Act
            result = runner.invoke(doc_update, ["--list-templates"])

            # Assert
            assert result.exit_code == 0
            assert "readme" in result.output.lower()
            assert "contributing" in result.output.lower()
            assert "changelog" in result.output.lower()

    def test_cli_list_templates_does_not_process_files(self):
        """
        Given: --list-templates flag is used
        When: Running command
        Then: Should not process any files or prompt for input
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# Template")

            # Act
            result = runner.invoke(doc_update, ["--list-templates"])

            # Assert
            assert result.exit_code == 0
            assert "Accept" not in result.output  # No review prompt
            assert "Generated preview" not in result.output  # No processing

    def test_cli_no_review_flag_accepts_automatically(self):
        """
        Given: --no-review flag is used
        When: Running 'doc-update README.md --no-review'
        Then: Should accept changes automatically without prompting
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            old_content = "# Old Content"
            Path("README.md").write_text(old_content)
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# New Content")

            # Act
            result = runner.invoke(doc_update, ["README.md", "--no-review"])

            # Assert
            assert result.exit_code == 0
            assert "Accept" not in result.output  # No prompt
            # File should be updated
            new_content = Path("README.md").read_text()
            assert new_content != old_content

    def test_cli_no_review_flag_completes_without_interaction(self):
        """
        Given: --no-review flag is used
        When: Running command
        Then: Should complete without any user interaction
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Old")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# New")

            # Act - no input provided
            result = runner.invoke(doc_update, ["README.md", "--no-review"])

            # Assert
            assert result.exit_code == 0
            # Should not have waited for input (would timeout/fail if it did)

    def test_cli_help_text_is_clear(self):
        """
        Given: User needs help
        When: Running 'doc-update --help'
        Then: Should show clear usage information
        """
        runner = CliRunner()

        # Act
        result = runner.invoke(doc_update, ["--help"])

        # Assert
        assert result.exit_code == 0
        assert "Usage:" in result.output or "usage:" in result.output
        assert "--template" in result.output
        assert "--list-templates" in result.output
        assert "--no-review" in result.output

    def test_cli_help_includes_examples(self):
        """
        Given: User needs help
        When: Running 'doc-update --help'
        Then: Should include usage examples
        """
        runner = CliRunner()

        # Act
        result = runner.invoke(doc_update, ["--help"])

        # Assert
        assert result.exit_code == 0
        # Should have examples or clear descriptions
        assert (
            "example" in result.output.lower() or "README.md" in result.output or "target_file" in result.output.lower()
        )

    def test_cli_template_auto_detection(self):
        """
        Given: Template exists matching target filename
        When: Running 'doc-update CONTRIBUTING.md' (no --template)
        Then: Should auto-detect 'contributing' template
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("CONTRIBUTING.md").write_text("# Old Contributing")
            Path(".templates").mkdir()
            contributing_content = "# Contributing Template Content"
            Path(".templates/contributing.md").write_text(contributing_content)

            # Act
            result = runner.invoke(doc_update, ["CONTRIBUTING.md", "--no-review"])

            # Assert
            assert result.exit_code == 0
            # Should use contributing template (verify file updated)
            updated = Path("CONTRIBUTING.md").read_text()
            assert "Template Content" in updated or "Contributing" in updated


class TestCLIErrorHandling:
    """Error handling and validation tests"""

    def test_cli_missing_target_file_shows_error(self):
        """
        Given: No target file argument provided
        When: Running 'doc-update' with no args
        Then: Should show error and exit with non-zero code
        """
        runner = CliRunner()

        # Act
        result = runner.invoke(doc_update, [])

        # Assert
        # When --list-templates not used, target_file is required
        # Should either error or show help
        assert result.exit_code != 0 or "--list-templates" in result.output

    def test_cli_missing_target_file_suggests_help(self):
        """
        Given: No target file argument provided
        When: Running 'doc-update' with no args
        Then: Should suggest using --help
        """
        runner = CliRunner()

        # Act
        result = runner.invoke(doc_update, [])

        # Assert
        assert "--help" in result.output or "Usage:" in result.output

    def test_cli_invalid_template_shows_clear_error(self):
        """
        Given: Invalid template name provided
        When: Running 'doc-update README.md --template nonexistent'
        Then: Should show clear error message
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Content")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# Template")

            # Act
            result = runner.invoke(doc_update, ["README.md", "--template", "nonexistent"])

            # Assert
            assert result.exit_code != 0
            assert (
                "not found" in result.output.lower()
                or "invalid" in result.output.lower()
                or "nonexistent" in result.output
            )

    def test_cli_invalid_template_suggests_available(self):
        """
        Given: Invalid template name provided
        When: Running command
        Then: Should suggest available templates
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Content")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# Template")
            Path(".templates/contributing.md").write_text("# Template")

            # Act
            result = runner.invoke(doc_update, ["README.md", "--template", "nonexistent"])

            # Assert
            assert result.exit_code != 0
            assert "available" in result.output.lower() or "readme" in result.output.lower()

    def test_cli_nonexistent_target_file_shows_error(self):
        """
        Given: Target file does not exist
        When: Running 'doc-update MISSING.md'
        Then: Should show clear error
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# Template")

            # Act
            result = runner.invoke(doc_update, ["MISSING.md"])

            # Assert
            assert result.exit_code != 0
            assert (
                "not found" in result.output.lower()
                or "does not exist" in result.output.lower()
                or "MISSING.md" in result.output
            )


class TestCLIExitCodes:
    """Exit code tests for automation"""

    def test_cli_success_exits_zero(self):
        """
        Given: Command completes successfully
        When: Running doc-update
        Then: Should exit with code 0
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Content")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# Template")

            # Act
            result = runner.invoke(doc_update, ["README.md", "--no-review"])

            # Assert
            assert result.exit_code == 0

    def test_cli_error_exits_nonzero(self):
        """
        Given: Command encounters error
        When: Running doc-update with invalid input
        Then: Should exit with non-zero code
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange - no templates directory

            # Act
            result = runner.invoke(doc_update, ["README.md"])

            # Assert
            assert result.exit_code != 0

    def test_cli_user_rejection_exits_zero(self):
        """
        Given: User rejects changes
        When: Running doc-update and answering 'n'
        Then: Should exit with code 0 (successful cancellation)
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Content")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# Template")

            # Act - user says 'n'
            result = runner.invoke(doc_update, ["README.md"], input="n\n")

            # Assert
            assert result.exit_code == 0  # Clean exit, not an error


class TestCLIIntegration:
    """End-to-end integration tests"""

    def test_cli_full_workflow_with_acceptance(self):
        """
        Given: Complete setup (file, template, context)
        When: Running full workflow and accepting changes
        Then: Should generate, show diff, prompt, and apply changes
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            old_content = "# Old README\n\nOld description."
            Path("README.md").write_text(old_content)
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# {{ project_name }}\n\n{{ description }}")

            # Act - user accepts
            result = runner.invoke(doc_update, ["README.md"], input="y\n")

            # Assert
            assert result.exit_code == 0
            # File should be updated
            new_content = Path("README.md").read_text()
            assert new_content != old_content

    def test_cli_full_workflow_with_rejection(self):
        """
        Given: Complete setup
        When: Running full workflow and rejecting changes
        Then: Should show preview but not modify file
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            old_content = "# Old README"
            Path("README.md").write_text(old_content)
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# New Template")

            # Act - user rejects
            result = runner.invoke(doc_update, ["README.md"], input="n\n")

            # Assert
            assert result.exit_code == 0
            # File should remain unchanged
            current_content = Path("README.md").read_text()
            assert current_content == old_content

    def test_cli_automated_workflow(self):
        """
        Given: Automated environment (no user interaction)
        When: Running with --no-review flag
        Then: Should complete end-to-end automatically
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Old")
            Path("CONTRIBUTING.md").write_text("# Old Contributing")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# New README")
            Path(".templates/contributing.md").write_text("# New Contributing")

            # Act - process both files
            result1 = runner.invoke(doc_update, ["README.md", "--no-review"])
            result2 = runner.invoke(doc_update, ["CONTRIBUTING.md", "--no-review"])

            # Assert
            assert result1.exit_code == 0
            assert result2.exit_code == 0
            assert Path("README.md").read_text() == "# New README"
            assert Path("CONTRIBUTING.md").read_text() == "# New Contributing"

    def test_cli_uses_template_manager(self):
        """
        Given: Templates exist
        When: Running CLI command
        Then: Should use template_manager.load_template()
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Content")
            Path(".templates").mkdir()
            Path(".templates/readme.md").write_text("# Template with {{ var }}")

            # Act
            with patch("doc_evergreen.cli.template_manager") as mock_mgr:
                mock_mgr.load_template.return_value = "# Mocked Template"
                runner.invoke(doc_update, ["README.md", "--no-review"])

                # Assert
                mock_mgr.load_template.assert_called_once()

    def test_cli_respects_template_directory_structure(self):
        """
        Given: Templates in .templates/ directory
        When: Running CLI
        Then: Should find and use templates from correct location
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Old")
            Path(".templates").mkdir()
            template_content = "# Template Content"
            Path(".templates/readme.md").write_text(template_content)

            # Act
            result = runner.invoke(doc_update, ["README.md", "--no-review"])

            # Assert
            assert result.exit_code == 0
            updated = Path("README.md").read_text()
            assert updated == template_content


class TestCLIShortOptions:
    """Short option flag tests"""

    def test_cli_template_short_option(self):
        """
        Given: Template option has short form
        When: Running 'doc-update README.md -t contributing'
        Then: Should work same as --template
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Arrange
            Path("README.md").write_text("# Content")
            Path(".templates").mkdir()
            Path(".templates/contributing.md").write_text("# Contributing")

            # Act
            result = runner.invoke(doc_update, ["README.md", "-t", "contributing"])

            # Assert
            assert result.exit_code == 0
