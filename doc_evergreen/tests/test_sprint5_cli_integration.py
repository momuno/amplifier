"""
Sprint 5 Deliverable 5: CLI Integration Tests (RED Phase)

Tests for --mode flag to choose single-shot vs chunked generation.
These tests MUST fail initially until implementation in GREEN phase.

Test Coverage:
- CLI parsing (--mode flag exists and accepts values)
- Generator routing (single vs chunked)
- Validation (chunked mode requires prompts)
- Backward compatibility (single-shot default)
"""

from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import patch

from click.testing import CliRunner

from doc_evergreen.cli import doc_update


class TestCLIModeFlag:
    """Tests for --mode flag parsing"""

    def test_cli_has_mode_option(self):
        """
        Given: CLI interface exists
        When: Running 'doc-update --help'
        Then: Should show --mode option in help text
        """
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(doc_update, ["--help"])

        # Assert
        assert result.exit_code == 0
        assert "--mode" in result.output

    def test_cli_mode_accepts_single_value(self):
        """
        Given: CLI has --mode flag
        When: Running 'doc-update --mode single template.json'
        Then: Should accept 'single' as valid value
        """
        # Arrange
        runner = CliRunner()

        with runner.isolated_filesystem():
            Path("template.json").write_text('{"document": {"title": "Test", "output": "out.md", "sections": []}}')

            # Act
            result = runner.invoke(doc_update, ["--mode", "single", "template.json"])

            # Assert
            # Should not fail on parsing (may fail on other things, but not flag parsing)
            assert "--mode" not in result.output or "invalid" not in result.output.lower()

    def test_cli_mode_accepts_chunked_value(self):
        """
        Given: CLI has --mode flag
        When: Running 'doc-update --mode chunked template.json'
        Then: Should accept 'chunked' as valid value
        """
        # Arrange
        runner = CliRunner()

        with runner.isolated_filesystem():
            Path("template.json").write_text('{"document": {"title": "Test", "output": "out.md", "sections": []}}')

            # Act
            result = runner.invoke(doc_update, ["--mode", "chunked", "template.json"])

            # Assert
            # Should not fail on parsing
            assert "--mode" not in result.output or "invalid" not in result.output.lower()

    def test_cli_mode_rejects_invalid_value(self):
        """
        Given: CLI has --mode flag
        When: Running 'doc-update --mode invalid template.json'
        Then: Should reject invalid value
        """
        # Arrange
        runner = CliRunner()

        with runner.isolated_filesystem():
            Path("template.json").write_text('{"document": {"title": "Test", "output": "out.md", "sections": []}}')

            # Act
            result = runner.invoke(doc_update, ["--mode", "invalid", "template.json"])

            # Assert
            assert result.exit_code != 0
            assert "invalid" in result.output.lower() or "choice" in result.output.lower()

    def test_cli_mode_defaults_to_single(self):
        """
        Given: CLI has --mode flag with default
        When: Running 'doc-update template.json' (no --mode)
        Then: Should default to 'single' mode
        """
        # This test verifies behavior - we'll check by mocking generator calls
        # Arrange
        runner = CliRunner()

        with runner.isolated_filesystem():
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "out.md",
                    "sections": [
                        {"heading": "Section 1", "sources": []}
                    ]
                }
            }
            """
            Path("template.json").write_text(template_json)
            Path("out.md").write_text("# Old content")

            with patch("doc_evergreen.cli.Generator") as mock_single_gen:
                mock_single_gen.return_value.generate = AsyncMock(return_value="# Generated")

                # Act
                runner.invoke(doc_update, ["template.json"], input="n\n")

                # Assert
                # Single-shot generator should be used (not chunked)
                mock_single_gen.assert_called_once()


class TestGeneratorRouting:
    """Tests for routing to correct generator based on mode"""

    @patch("doc_evergreen.cli.Generator")
    def test_single_mode_uses_single_generator(self, mock_single_gen):
        """
        Given: --mode single specified
        When: CLI processes template
        Then: Should instantiate Generator (single-shot)
        """
        # Arrange
        runner = CliRunner()
        mock_single_gen.return_value.generate = AsyncMock(return_value="# Generated")

        with runner.isolated_filesystem():
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "out.md",
                    "sections": [
                        {"heading": "Section 1", "sources": []}
                    ]
                }
            }
            """
            Path("template.json").write_text(template_json)
            Path("out.md").write_text("# Old")

            # Act
            result = runner.invoke(doc_update, ["--mode", "single", "template.json"], input="n\n")

            # Assert
            assert result.exit_code == 0
            mock_single_gen.assert_called_once()

    @patch("doc_evergreen.cli.ChunkedGenerator")
    def test_chunked_mode_uses_chunked_generator(self, mock_chunked_gen):
        """
        Given: --mode chunked specified
        When: CLI processes template with prompts
        Then: Should instantiate ChunkedGenerator
        """
        # Arrange
        runner = CliRunner()
        mock_chunked_gen.return_value.generate = AsyncMock(return_value="# Generated")

        with runner.isolated_filesystem():
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "out.md",
                    "sections": [
                        {
                            "heading": "Section 1",
                            "prompt": "Write section 1",
                            "sources": []
                        }
                    ]
                }
            }
            """
            Path("template.json").write_text(template_json)
            Path("out.md").write_text("# Old")

            # Act
            result = runner.invoke(doc_update, ["--mode", "chunked", "template.json"], input="n\n")

            # Assert
            assert result.exit_code == 0
            mock_chunked_gen.assert_called_once()

    @patch("doc_evergreen.cli.Generator")
    @patch("doc_evergreen.cli.ChunkedGenerator")
    def test_mode_determines_generator_choice(self, mock_chunked_gen, mock_single_gen):
        """
        Given: Same template, different modes
        When: Running with --mode single vs --mode chunked
        Then: Should use different generators
        """
        # Arrange
        runner = CliRunner()
        mock_single_gen.return_value.generate = AsyncMock(return_value="# Generated")
        mock_chunked_gen.return_value.generate = AsyncMock(return_value="# Generated")

        template_json = """
        {
            "document": {
                "title": "Test",
                "output": "out.md",
                "sections": [
                    {
                        "heading": "Section 1",
                        "prompt": "Write section 1",
                        "sources": []
                    }
                ]
            }
        }
        """

        with runner.isolated_filesystem():
            Path("template.json").write_text(template_json)
            Path("out.md").write_text("# Old")

            # Act - single mode
            result1 = runner.invoke(doc_update, ["--mode", "single", "template.json"], input="n\n")

            # Assert single
            assert result1.exit_code == 0
            mock_single_gen.assert_called_once()
            mock_chunked_gen.assert_not_called()

            # Reset mocks
            mock_single_gen.reset_mock()
            mock_chunked_gen.reset_mock()

            # Act - chunked mode
            result2 = runner.invoke(doc_update, ["--mode", "chunked", "template.json"], input="n\n")

            # Assert chunked
            assert result2.exit_code == 0
            mock_chunked_gen.assert_called_once()
            mock_single_gen.assert_not_called()


class TestChunkedModeValidation:
    """Tests for validation when using chunked mode"""

    def test_chunked_mode_validates_prompts_exist(self):
        """
        Given: Template with sections
        When: Running with --mode chunked
        Then: Should validate that prompts exist in all sections
        """
        # Arrange
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Template with section missing prompt
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "out.md",
                    "sections": [
                        {
                            "heading": "Section 1",
                            "sources": []
                        }
                    ]
                }
            }
            """
            Path("template.json").write_text(template_json)

            # Act
            result = runner.invoke(doc_update, ["--mode", "chunked", "template.json"])

            # Assert
            assert result.exit_code != 0
            assert "prompt" in result.output.lower() or "missing" in result.output.lower()

    def test_chunked_mode_fails_without_prompts(self):
        """
        Given: Template without prompts
        When: Running with --mode chunked
        Then: Should fail with clear error message
        """
        # Arrange
        runner = CliRunner()

        with runner.isolated_filesystem():
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "out.md",
                    "sections": [
                        {
                            "heading": "Introduction",
                            "sources": []
                        },
                        {
                            "heading": "Details",
                            "sources": []
                        }
                    ]
                }
            }
            """
            Path("template.json").write_text(template_json)

            # Act
            result = runner.invoke(doc_update, ["--mode", "chunked", "template.json"])

            # Assert
            assert result.exit_code != 0
            # Should mention which section is missing prompts
            assert "Introduction" in result.output or "Details" in result.output

    @patch("doc_evergreen.cli.ChunkedGenerator")
    def test_chunked_mode_succeeds_with_all_prompts(self, mock_chunked_gen):
        """
        Given: Template with all sections having prompts
        When: Running with --mode chunked
        Then: Should pass validation and proceed to generation
        """
        # Arrange
        runner = CliRunner()
        mock_chunked_gen.return_value.generate = AsyncMock(return_value="# Generated")

        with runner.isolated_filesystem():
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "out.md",
                    "sections": [
                        {
                            "heading": "Introduction",
                            "prompt": "Write introduction",
                            "sources": []
                        },
                        {
                            "heading": "Details",
                            "prompt": "Write details",
                            "sources": []
                        }
                    ]
                }
            }
            """
            Path("template.json").write_text(template_json)
            Path("out.md").write_text("# Old")

            # Act
            result = runner.invoke(doc_update, ["--mode", "chunked", "template.json"], input="n\n")

            # Assert
            assert result.exit_code == 0
            mock_chunked_gen.assert_called_once()

    def test_chunked_mode_validates_nested_sections(self):
        """
        Given: Template with nested sections
        When: Running with --mode chunked
        Then: Should validate prompts in nested sections too
        """
        # Arrange
        runner = CliRunner()

        with runner.isolated_filesystem():
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "out.md",
                    "sections": [
                        {
                            "heading": "Parent",
                            "prompt": "Write parent",
                            "sources": [],
                            "sections": [
                                {
                                    "heading": "Child",
                                    "sources": []
                                }
                            ]
                        }
                    ]
                }
            }
            """
            Path("template.json").write_text(template_json)

            # Act
            result = runner.invoke(doc_update, ["--mode", "chunked", "template.json"])

            # Assert
            assert result.exit_code != 0
            assert "Child" in result.output or "prompt" in result.output.lower()


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing templates"""

    @patch("doc_evergreen.cli.Generator")
    def test_existing_templates_work_without_mode(self, mock_single_gen):
        """
        Given: Existing template without prompts
        When: Running without --mode flag
        Then: Should use single-shot generator (backward compatible)
        """
        # Arrange
        runner = CliRunner()
        mock_single_gen.return_value.generate = AsyncMock(return_value="# Generated")

        with runner.isolated_filesystem():
            # Old-style template (no prompts)
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "out.md",
                    "sections": [
                        {"heading": "Section 1", "sources": []},
                        {"heading": "Section 2", "sources": []}
                    ]
                }
            }
            """
            Path("template.json").write_text(template_json)
            Path("out.md").write_text("# Old")

            # Act
            result = runner.invoke(doc_update, ["template.json"], input="n\n")

            # Assert
            assert result.exit_code == 0
            mock_single_gen.assert_called_once()

    def test_mode_flag_optional(self):
        """
        Given: CLI with --mode flag
        When: Running without specifying --mode
        Then: Should not fail (flag is optional)
        """
        # Arrange
        runner = CliRunner()

        with runner.isolated_filesystem():
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "out.md",
                    "sections": []
                }
            }
            """
            Path("template.json").write_text(template_json)
            Path("out.md").write_text("# Old")

            with patch("doc_evergreen.cli.Generator") as mock_gen:
                mock_gen.return_value.generate = AsyncMock(return_value="# Generated")

                # Act
                result = runner.invoke(doc_update, ["template.json"], input="n\n")

                # Assert
                # Should work without --mode flag
                assert result.exit_code == 0

    @patch("doc_evergreen.cli.Generator")
    def test_single_mode_ignores_prompts(self, mock_single_gen):
        """
        Given: Template with prompts
        When: Running with --mode single
        Then: Should use single-shot generator (ignores prompts)
        """
        # Arrange
        runner = CliRunner()
        mock_single_gen.return_value.generate = AsyncMock(return_value="# Generated")

        with runner.isolated_filesystem():
            # Template with prompts (new-style)
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "out.md",
                    "sections": [
                        {
                            "heading": "Section 1",
                            "prompt": "Write section 1",
                            "sources": []
                        }
                    ]
                }
            }
            """
            Path("template.json").write_text(template_json)
            Path("out.md").write_text("# Old")

            # Act
            result = runner.invoke(doc_update, ["--mode", "single", "template.json"], input="n\n")

            # Assert
            assert result.exit_code == 0
            mock_single_gen.assert_called_once()

    def test_help_mentions_default_mode(self):
        """
        Given: CLI with --mode flag
        When: Running 'doc-update --help'
        Then: Should show that 'single' is the default
        """
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(doc_update, ["--help"])

        # Assert
        assert result.exit_code == 0
        # Should mention default in help text
        assert "default" in result.output.lower() or "single" in result.output.lower()


class TestCLIOutputPath:
    """Tests for --output flag (optional override)"""

    @patch("doc_evergreen.cli.ChunkedGenerator")
    def test_output_flag_overrides_template_path(self, mock_chunked_gen):
        """
        Given: Template specifies output path
        When: Running with --output override
        Then: Should write to override path instead
        """
        # Arrange
        runner = CliRunner()
        mock_chunked_gen.return_value.generate = AsyncMock(return_value="# Generated")

        with runner.isolated_filesystem():
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "default.md",
                    "sections": [
                        {
                            "heading": "Section 1",
                            "prompt": "Write section",
                            "sources": []
                        }
                    ]
                }
            }
            """
            Path("template.json").write_text(template_json)
            Path("custom.md").write_text("# Old")

            # Act
            result = runner.invoke(
                doc_update, ["--mode", "chunked", "--output", "custom.md", "template.json"], input="y\n"
            )

            # Assert
            assert result.exit_code == 0
            # Should update custom.md, not default.md
            assert Path("custom.md").read_text() == "# Generated"

    @patch("doc_evergreen.cli.Generator")
    def test_output_flag_works_with_single_mode(self, mock_single_gen):
        """
        Given: Single-shot mode
        When: Running with --output override
        Then: Should work in single mode too
        """
        # Arrange
        runner = CliRunner()
        mock_single_gen.return_value.generate = AsyncMock(return_value="# Generated")

        with runner.isolated_filesystem():
            template_json = """
            {
                "document": {
                    "title": "Test",
                    "output": "default.md",
                    "sections": []
                }
            }
            """
            Path("template.json").write_text(template_json)
            Path("override.md").write_text("# Old")

            # Act
            result = runner.invoke(
                doc_update, ["--mode", "single", "--output", "override.md", "template.json"], input="y\n"
            )

            # Assert
            assert result.exit_code == 0
