"""
Tests for Sprint 1: Template Loading Functionality

Following TDD RED phase - these tests define behavior before implementation exists.
"""

from pathlib import Path

import pytest
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
