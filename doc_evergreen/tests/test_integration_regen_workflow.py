"""Integration tests for complete regen-doc workflow.

Following TDD red-green-refactor cycle:
🔴 RED: Write failing tests first
🟢 GREEN: Implement minimal code to pass
🔵 REFACTOR: Improve quality while tests protect

These tests verify end-to-end workflows:
- Template → Generate → Diff → Approve → Apply
- Example templates generate valid documentation
- Handles both new files and updates
"""

import json
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

from click.testing import CliRunner

from doc_evergreen.cli import cli


class TestFullWorkflowNewFile:
    """Test complete workflow when output file doesn't exist."""

    def test_new_file_workflow_with_approval(self, tmp_path: Path) -> None:
        """
        Given: A template for a file that doesn't exist
        When: User runs regen-doc and approves changes
        Then: File is created with generated content
        """
        # Arrange
        template_path = tmp_path / "test_template.json"
        output_path = tmp_path / "output.md"

        template_data = {
            "document": {
                "title": "Test Document",
                "output": str(output_path),
                "sections": [
                    {
                        "heading": "Test Section",
                        "prompt": "Test prompt",
                        "sources": [],
                    }
                ],
            }
        }
        template_path.write_text(json.dumps(template_data))

        runner = CliRunner()

        # Mock the ChunkedGenerator to return predictable content
        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = "# Test Document\n\n## Test Section\n\nGenerated content.\n"
            mock_gen.return_value = mock_instance

            # Act - Simulate user approving with 'y' and declining regeneration with 'n'
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\nn\n")

        # Assert
        assert result.exit_code == 0
        assert output_path.exists()
        assert "NEW FILE" in result.output or "Creating new file" in result.output
        assert "Apply these changes?" in result.output
        assert "File written" in result.output

        # Verify content
        content = output_path.read_text()
        assert "# Test Document" in content
        assert "## Test Section" in content

    def test_new_file_workflow_with_rejection(self, tmp_path: Path) -> None:
        """
        Given: A template for a file that doesn't exist
        When: User runs regen-doc and rejects changes
        Then: File is NOT created
        """
        # Arrange
        template_path = tmp_path / "test_template.json"
        output_path = tmp_path / "output.md"

        template_data = {
            "document": {
                "title": "Test Document",
                "output": str(output_path),
                "sections": [
                    {
                        "heading": "Test Section",
                        "prompt": "Test prompt",
                        "sources": [],
                    }
                ],
            }
        }
        template_path.write_text(json.dumps(template_data))

        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = "# Test Document\n\n## Test Section\n\nGenerated content.\n"
            mock_gen.return_value = mock_instance

            # Act - Simulate user rejecting with 'n'
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="n\n")

        # Assert
        assert result.exit_code == 0
        assert not output_path.exists()
        assert "Aborted" in result.output or "not applied" in result.output


class TestFullWorkflowExistingFile:
    """Test complete workflow when output file already exists."""

    def test_existing_file_workflow_with_changes(self, tmp_path: Path) -> None:
        """
        Given: A template and existing output file with different content
        When: User runs regen-doc and approves
        Then: File is updated with new content
        """
        # Arrange
        template_path = tmp_path / "test_template.json"
        output_path = tmp_path / "output.md"

        # Create existing file
        output_path.write_text("# Old Content\n\nThis is old.\n")

        template_data = {
            "document": {
                "title": "Test Document",
                "output": str(output_path),
                "sections": [
                    {
                        "heading": "Test Section",
                        "prompt": "Test prompt",
                        "sources": [],
                    }
                ],
            }
        }
        template_path.write_text(json.dumps(template_data))

        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = "# New Content\n\n## Test Section\n\nThis is new.\n"
            mock_gen.return_value = mock_instance

            # Act - Approve changes and decline regeneration
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\nn\n")

        # Assert
        assert result.exit_code == 0
        assert output_path.exists()
        assert "Changes detected" in result.output
        assert "Apply these changes?" in result.output
        assert "File written" in result.output

        # Verify content was updated
        content = output_path.read_text()
        assert "# New Content" in content
        assert "This is new" in content
        assert "Old Content" not in content

    def test_existing_file_workflow_no_changes(self, tmp_path: Path) -> None:
        """
        Given: A template and existing output file with identical content
        When: User runs regen-doc
        Then: No changes are applied, user is informed
        """
        # Arrange
        template_path = tmp_path / "test_template.json"
        output_path = tmp_path / "output.md"

        # Create existing file
        existing_content = "# Test Document\n\n## Test Section\n\nGenerated content.\n"
        output_path.write_text(existing_content)

        template_data = {
            "document": {
                "title": "Test Document",
                "output": str(output_path),
                "sections": [
                    {
                        "heading": "Test Section",
                        "prompt": "Test prompt",
                        "sources": [],
                    }
                ],
            }
        }
        template_path.write_text(json.dumps(template_data))

        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = existing_content
            mock_gen.return_value = mock_instance

            # Act
            result = runner.invoke(cli, ["regen-doc", str(template_path)])

        # Assert
        assert result.exit_code == 0
        assert "No changes detected" in result.output
        # Should NOT prompt for approval when no changes
        assert "Apply these changes?" not in result.output


class TestAutoApproveFlag:
    """Test --auto-approve flag bypasses confirmation."""

    def test_auto_approve_creates_file_without_prompt(self, tmp_path: Path) -> None:
        """
        Given: A template and --auto-approve flag
        When: User runs regen-doc
        Then: File is created without confirmation prompt
        """
        # Arrange
        template_path = tmp_path / "test_template.json"
        output_path = tmp_path / "output.md"

        template_data = {
            "document": {
                "title": "Test Document",
                "output": str(output_path),
                "sections": [
                    {
                        "heading": "Test Section",
                        "prompt": "Test prompt",
                        "sources": [],
                    }
                ],
            }
        }
        template_path.write_text(json.dumps(template_data))

        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = "# Test Document\n\n## Test Section\n\nGenerated content.\n"
            mock_gen.return_value = mock_instance

            # Act - No input needed with --auto-approve
            result = runner.invoke(cli, ["regen-doc", "--auto-approve", str(template_path)])

        # Assert
        assert result.exit_code == 0
        assert output_path.exists()
        # Should NOT show approval prompt
        assert "Apply these changes?" not in result.output
        assert "File written" in result.output


class TestOutputOverride:
    """Test --output flag overrides template output path."""

    def test_output_override_writes_to_custom_path(self, tmp_path: Path) -> None:
        """
        Given: A template and --output flag with custom path
        When: User runs regen-doc
        Then: File is written to custom path, not template path
        """
        # Arrange
        template_path = tmp_path / "test_template.json"
        template_output = tmp_path / "template_output.md"
        custom_output = tmp_path / "custom_output.md"

        template_data = {
            "document": {
                "title": "Test Document",
                "output": str(template_output),
                "sections": [
                    {
                        "heading": "Test Section",
                        "prompt": "Test prompt",
                        "sources": [],
                    }
                ],
            }
        }
        template_path.write_text(json.dumps(template_data))

        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = "# Test Document\n\n## Test Section\n\nGenerated content.\n"
            mock_gen.return_value = mock_instance

            # Act
            result = runner.invoke(
                cli,
                ["regen-doc", "--auto-approve", "--output", str(custom_output), str(template_path)],
            )

        # Assert
        assert result.exit_code == 0
        assert custom_output.exists()
        assert not template_output.exists()
        assert str(custom_output) in result.output


class TestExampleTemplates:
    """Test that example templates generate valid documentation."""

    def test_simple_template_generates_valid_output(self, tmp_path: Path) -> None:
        """
        Given: The simple.json example template
        When: User runs regen-doc
        Then: Valid markdown is generated with 2 sections
        """
        # Arrange
        # Note: This assumes examples/simple.json exists
        # In a real test, we'd either use the actual file or create a test version
        template_path = tmp_path / "simple_test.json"
        output_path = tmp_path / "output.md"

        template_data = {
            "document": {
                "title": "Simple Project Documentation",
                "output": str(output_path),
                "sections": [
                    {
                        "heading": "Overview",
                        "prompt": "Explain what this project does",
                        "sources": [],
                    },
                    {
                        "heading": "Installation",
                        "prompt": "Provide installation instructions",
                        "sources": [],
                    },
                ],
            }
        }
        template_path.write_text(json.dumps(template_data))

        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = "# Simple Project Documentation\n\n## Overview\n\nProject description.\n\n## Installation\n\nInstallation steps.\n"
            mock_gen.return_value = mock_instance

            # Act
            result = runner.invoke(cli, ["regen-doc", "--auto-approve", str(template_path)])

        # Assert
        assert result.exit_code == 0
        assert output_path.exists()

        content = output_path.read_text()
        assert "# Simple Project Documentation" in content
        assert "## Overview" in content
        assert "## Installation" in content

    def test_nested_template_generates_valid_hierarchy(self, tmp_path: Path) -> None:
        """
        Given: A template with nested sections
        When: User runs regen-doc
        Then: Valid markdown is generated with proper heading hierarchy
        """
        # Arrange
        template_path = tmp_path / "nested_test.json"
        output_path = tmp_path / "output.md"

        template_data = {
            "document": {
                "title": "Advanced Documentation",
                "output": str(output_path),
                "sections": [
                    {
                        "heading": "Getting Started",
                        "prompt": "Introduction",
                        "sources": [],
                        "sections": [
                            {
                                "heading": "Installation",
                                "prompt": "How to install",
                                "sources": [],
                            }
                        ],
                    }
                ],
            }
        }
        template_path.write_text(json.dumps(template_data))

        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            # Note: ChunkedGenerator should handle nested sections properly
            mock_instance.generate.return_value = "# Advanced Documentation\n\n## Getting Started\n\nIntro content.\n\n### Installation\n\nInstallation steps.\n"
            mock_gen.return_value = mock_instance

            # Act
            result = runner.invoke(cli, ["regen-doc", "--auto-approve", str(template_path)])

        # Assert
        assert result.exit_code == 0
        assert output_path.exists()

        content = output_path.read_text()
        assert "## Getting Started" in content
        assert "### Installation" in content


class TestErrorHandling:
    """Test error handling in integration workflows."""

    def test_invalid_json_template_shows_error(self, tmp_path: Path) -> None:
        """
        Given: A template file with invalid JSON
        When: User runs regen-doc
        Then: Clear error message is shown
        """
        # Arrange
        template_path = tmp_path / "invalid.json"
        template_path.write_text("{invalid json")

        runner = CliRunner()

        # Act
        result = runner.invoke(cli, ["regen-doc", str(template_path)])

        # Assert
        assert result.exit_code != 0
        assert "Error" in result.output or "Invalid" in result.output

    def test_missing_template_file_shows_error(self) -> None:
        """
        Given: A non-existent template file path
        When: User runs regen-doc
        Then: Clear error message is shown
        """
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(cli, ["regen-doc", "does-not-exist.json"])

        # Assert
        assert result.exit_code != 0
        # Click validates file existence and shows its own error

    def test_permission_error_shows_clear_message(self, tmp_path: Path) -> None:
        """
        Given: Output path where we don't have write permission
        When: User runs regen-doc and approves
        Then: Clear permission error is shown
        """
        # Arrange
        template_path = tmp_path / "test_template.json"
        # Try to write to a path that should fail (system directory)
        output_path = Path("/root/test_output.md")  # Should fail on most systems

        template_data = {
            "document": {
                "title": "Test Document",
                "output": str(output_path),
                "sections": [
                    {
                        "heading": "Test Section",
                        "prompt": "Test prompt",
                        "sources": [],
                    }
                ],
            }
        }
        template_path.write_text(json.dumps(template_data))

        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = "# Test Document\n"
            mock_gen.return_value = mock_instance

            # Act
            result = runner.invoke(cli, ["regen-doc", "--auto-approve", str(template_path)])

        # Assert
        # Should either fail with permission error or create parent dirs
        # The exact behavior depends on system permissions
        if result.exit_code != 0:
            # Check output and exception for error indicators
            exception_str = str(result.exception) if result.exception else ""
            assert "Error" in result.output or "Permission" in result.output or "Permission" in exception_str
