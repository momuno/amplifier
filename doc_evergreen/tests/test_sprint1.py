"""
Tests for Sprint 1: Template Loading Functionality

Following TDD RED phase - these tests define behavior before implementation exists.
"""

from pathlib import Path

import pytest

from doc_evergreen.context import gather_context
from doc_evergreen.template import load_template


class TestTemplateLoading:
    """Tests for template file loading functionality"""

    def test_load_template_success(self, tmp_path: Path) -> None:
        """
        Given: A template file exists with content
        When: load_template is called with the file path
        Then: The template content is returned as a string
        """
        # Arrange
        template_content = "# Project: {{project_name}}\n\nVersion: {{version}}"
        template_file = tmp_path / "test-template.md"
        template_file.write_text(template_content, encoding="utf-8")

        # Act
        result = load_template(str(template_file))

        # Assert
        assert result == template_content
        assert isinstance(result, str)
        assert "{{project_name}}" in result

    def test_load_template_preserves_formatting(self, tmp_path: Path) -> None:
        """
        Given: A template with multiple lines and whitespace
        When: load_template is called
        Then: All formatting including newlines and spacing is preserved
        """
        # Arrange
        template_content = """# Header

Paragraph with content.

- List item 1
- List item 2

## Section

More content here."""
        template_file = tmp_path / "formatted-template.md"
        template_file.write_text(template_content, encoding="utf-8")

        # Act
        result = load_template(str(template_file))

        # Assert
        assert result == template_content
        assert result.count("\n") == template_content.count("\n")

    def test_load_template_missing_file(self, tmp_path: Path) -> None:
        """
        Given: A template file path that doesn't exist
        When: load_template is called
        Then: A FileNotFoundError is raised with a clear message
        """
        # Arrange
        nonexistent_path = tmp_path / "does-not-exist.md"

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            load_template(str(nonexistent_path))

        # Verify error message is helpful
        assert "does-not-exist.md" in str(exc_info.value)

    def test_load_template_empty_file(self, tmp_path: Path) -> None:
        """
        Given: A template file that is empty
        When: load_template is called
        Then: An empty string is returned (valid use case)
        """
        # Arrange
        empty_file = tmp_path / "empty-template.md"
        empty_file.write_text("", encoding="utf-8")

        # Act
        result = load_template(str(empty_file))

        # Assert
        assert result == ""
        assert isinstance(result, str)

    def test_load_template_with_utf8_content(self, tmp_path: Path) -> None:
        """
        Given: A template with UTF-8 special characters
        When: load_template is called
        Then: UTF-8 content is correctly loaded
        """
        # Arrange
        template_content = "# Prøject: {{name}}\n\n使用者指南\n\nCafé ☕"
        template_file = tmp_path / "utf8-template.md"
        template_file.write_text(template_content, encoding="utf-8")

        # Act
        result = load_template(str(template_file))

        # Assert
        assert result == template_content
        assert "☕" in result
        assert "使用者" in result


class TestContextGathering:
    """Tests for context gathering functionality"""

    def test_gather_context_includes_all_sources(self, tmp_path: Path, monkeypatch) -> None:
        """
        Given: All hardcoded source files exist with content
        When: gather_context is called
        Then: All source files are included in the returned context
        """
        # Arrange: Create test files matching SOURCES
        sources = {
            "README.md": "# Project README\n\nThis is the readme.",
            "amplifier/__init__.py": "# Amplifier package\n__version__ = '0.1.0'",
            "pyproject.toml": "[tool.poetry]\nname = 'amplifier'",
            "AGENTS.md": "# AI Agent Guide\n\nAgent instructions here.",
        }

        # Create directory structure
        (tmp_path / "amplifier").mkdir()
        for filename, content in sources.items():
            filepath = tmp_path / filename
            filepath.write_text(content, encoding="utf-8")

        # Mock the base directory to use tmp_path
        monkeypatch.chdir(tmp_path)

        # Act
        result = gather_context()

        # Assert: All filenames appear in result
        for filename in sources:
            assert filename in result, f"Expected {filename} to be in gathered context"

        # Assert: All content appears in result
        for content in sources.values():
            assert content in result, "Expected content to be in gathered context"

    def test_gather_context_format(self, tmp_path: Path, monkeypatch) -> None:
        """
        Given: Multiple source files exist
        When: gather_context is called
        Then: Content is formatted with clear file separators
        """
        # Arrange
        sources = {"README.md": "# README content", "AGENTS.md": "# AGENTS content"}

        for filename, content in sources.items():
            filepath = tmp_path / filename
            filepath.write_text(content, encoding="utf-8")

        monkeypatch.chdir(tmp_path)

        # Act
        result = gather_context()

        # Assert: File separators present
        # Expected format: --- filename ---
        assert "--- README.md ---" in result
        assert "--- AGENTS.md ---" in result

        # Assert: Separators come before content
        readme_sep_pos = result.find("--- README.md ---")
        readme_content_pos = result.find("# README content")
        assert readme_sep_pos < readme_content_pos, "Separator should come before content"

    def test_gather_context_content_preservation(self, tmp_path: Path, monkeypatch) -> None:
        """
        Given: Source files with various formatting (multiline, special chars)
        When: gather_context is called
        Then: All content is preserved exactly including whitespace and UTF-8
        """
        # Arrange
        complex_content = """# Header

Paragraph with content.

- List item 1
- List item 2

Special chars: ☕ 使用者"""

        readme_file = tmp_path / "README.md"
        readme_file.write_text(complex_content, encoding="utf-8")

        # Create minimal other files to satisfy SOURCES
        (tmp_path / "amplifier").mkdir()
        (tmp_path / "amplifier" / "__init__.py").write_text("pass", encoding="utf-8")
        (tmp_path / "pyproject.toml").write_text("name='test'", encoding="utf-8")
        (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")

        monkeypatch.chdir(tmp_path)

        # Act
        result = gather_context()

        # Assert: Exact content preserved
        assert complex_content in result
        assert result.count("\n") >= complex_content.count("\n")
        assert "☕" in result
        assert "使用者" in result

    def test_gather_context_handles_missing_files(self, tmp_path: Path, monkeypatch) -> None:
        """
        Given: Some hardcoded source files are missing
        When: gather_context is called
        Then: Available files are included, missing files are skipped gracefully

        Testing Decision: Skip missing files rather than fail.
        Rationale: In real usage, some context files might be optional.
        """
        # Arrange: Create only some of the expected files
        readme_file = tmp_path / "README.md"
        readme_file.write_text("# README exists", encoding="utf-8")

        # Don't create amplifier/__init__.py, pyproject.toml, AGENTS.md

        monkeypatch.chdir(tmp_path)

        # Act
        result = gather_context()

        # Assert: Available file is included
        assert "README.md" in result
        assert "# README exists" in result

        # Assert: Result is still valid (non-empty string)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_gather_context_returns_single_string(self, tmp_path: Path, monkeypatch) -> None:
        """
        Given: Multiple source files exist
        When: gather_context is called
        Then: A single concatenated string is returned
        """
        # Arrange
        (tmp_path / "amplifier").mkdir()
        (tmp_path / "README.md").write_text("readme", encoding="utf-8")
        (tmp_path / "amplifier" / "__init__.py").write_text("init", encoding="utf-8")
        (tmp_path / "pyproject.toml").write_text("toml", encoding="utf-8")
        (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")

        monkeypatch.chdir(tmp_path)

        # Act
        result = gather_context()

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain all content in one string
        assert "readme" in result and "init" in result and "toml" in result and "agents" in result
