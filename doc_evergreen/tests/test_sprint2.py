"""
Sprint 2 Tests: Preview File Generation

These tests define the behavior for generating preview files in the doc_evergreen system.
They are written in the RED phase (before implementation) to clarify requirements.

Test Philosophy:
- Each test validates one specific behavior
- Tests use real file I/O (no mocks) with tmp_path
- Given-When-Then pattern for clarity
- Tests should fail until preview.py is implemented
"""

from pathlib import Path

# This import will fail initially - that's expected in RED phase
from doc_evergreen.preview import generate_preview


class TestPreviewGeneration:
    """Tests for basic preview file generation"""

    def test_generate_preview_creates_file(self, tmp_path):
        """
        Given: A template, context, and target filename
        When: generate_preview() is called
        Then: A preview file is created on disk
        """
        # Arrange
        template = "# {{title}}\n\n{{content}}"
        context = "title: Test\ncontent: Body text"
        target = "README.md"

        # Act
        preview_path = generate_preview(template, context, target, output_dir=tmp_path)

        # Assert
        assert preview_path.exists()
        assert preview_path.is_file()

    def test_preview_naming_convention(self, tmp_path):
        """
        Given: A target filename "README.md"
        When: generate_preview() is called
        Then: Preview file is named "README.preview.md"
        """
        # Arrange
        template = "# {{title}}"
        context = "title: Test"
        target = "README.md"

        # Act
        preview_path = generate_preview(template, context, target, output_dir=tmp_path)

        # Assert
        assert preview_path.name == "README.preview.md"

    def test_preview_naming_for_different_targets(self, tmp_path):
        """
        Given: Various target filenames
        When: generate_preview() is called
        Then: Preview files follow {name}.preview{ext} pattern
        """
        test_cases = [
            ("README.md", "README.preview.md"),
            ("CONTRIBUTING.md", "CONTRIBUTING.preview.md"),
            ("docs/guide.md", "guide.preview.md"),
        ]

        for target, expected_name in test_cases:
            # Arrange
            template = "# Test"
            context = "title: Test"

            # Act
            preview_path = generate_preview(template, context, target, output_dir=tmp_path)

            # Assert
            assert preview_path.name == expected_name

    def test_preview_contains_generated_content(self, tmp_path):
        """
        Given: A template with placeholders and context data
        When: generate_preview() is called
        Then: Preview file contains fully rendered content
        """
        # Arrange
        template = "# {{title}}\n\n{{content}}"
        context = "title: Test Document\ncontent: This is the body"
        target = "README.md"

        # Act
        preview_path = generate_preview(template, context, target, output_dir=tmp_path)

        # Assert
        content = preview_path.read_text()
        assert "# Test Document" in content
        assert "This is the body" in content
        assert "{{" not in content  # No unrendered placeholders

    def test_generate_preview_returns_path(self, tmp_path):
        """
        Given: Valid inputs to generate_preview()
        When: Function completes successfully
        Then: Returns a Path object pointing to the preview file
        """
        # Arrange
        template = "# {{title}}"
        context = "title: Test"
        target = "README.md"

        # Act
        result = generate_preview(template, context, target, output_dir=tmp_path)

        # Assert
        assert isinstance(result, Path)
        assert result.parent == tmp_path
        assert result.name == "README.preview.md"


class TestPreviewCleanup:
    """Tests for cleaning up old preview files"""

    def test_preview_cleanup_removes_old_file(self, tmp_path):
        """
        Given: An existing preview file from a previous run
        When: generate_preview() is called again
        Then: Old preview file is replaced with new one
        """
        # Arrange
        template = "# {{title}}"
        context = "title: Test"
        target = "README.md"
        preview_path = tmp_path / "README.preview.md"

        # Create old preview with different content
        preview_path.write_text("# Old Content\n\nThis should be replaced")

        # Act
        new_preview = generate_preview(template, context, target, output_dir=tmp_path)

        # Assert
        content = new_preview.read_text()
        assert "Old Content" not in content
        assert "Test" in content

    def test_preview_cleanup_handles_no_existing_file(self, tmp_path):
        """
        Given: No existing preview file
        When: generate_preview() is called
        Then: Preview file is created without errors
        """
        # Arrange
        template = "# {{title}}"
        context = "title: Test"
        target = "README.md"
        preview_path = tmp_path / "README.preview.md"

        # Verify no preview exists
        assert not preview_path.exists()

        # Act
        result = generate_preview(template, context, target, output_dir=tmp_path)

        # Assert
        assert result.exists()
        assert "Test" in result.read_text()


class TestPreviewWithComplexContent:
    """Tests for preview generation with realistic content"""

    def test_preview_with_multiline_content(self, tmp_path):
        """
        Given: Template with multiple sections and formatting
        When: generate_preview() is called
        Then: Preview preserves all formatting and structure
        """
        # Arrange
        template = """# {{title}}

## Overview
{{overview}}

## Installation
{{install_steps}}

## Usage
{{usage}}"""
        context = """title: My Project
overview: A great tool
install_steps: |
    pip install mytool
    mytool init
usage: Run `mytool --help` for details"""
        target = "README.md"

        # Act
        preview_path = generate_preview(template, context, target, output_dir=tmp_path)

        # Assert
        content = preview_path.read_text()
        assert "# My Project" in content
        assert "## Overview" in content
        assert "pip install mytool" in content
        assert "Run `mytool --help`" in content

    def test_preview_with_empty_context_values(self, tmp_path):
        """
        Given: Context with some empty values
        When: generate_preview() is called
        Then: Preview handles empty values gracefully
        """
        # Arrange
        template = "# {{title}}\n\n{{content}}\n\n{{footer}}"
        context = "title: Test\ncontent: Body\nfooter: ''"
        target = "README.md"

        # Act
        preview_path = generate_preview(template, context, target, output_dir=tmp_path)

        # Assert
        content = preview_path.read_text()
        assert "# Test" in content
        assert "Body" in content
        # Empty footer should not cause issues


class TestPreviewEdgeCases:
    """Tests for edge cases and error conditions"""

    def test_preview_with_special_characters_in_content(self, tmp_path):
        """
        Given: Content with special markdown characters
        When: generate_preview() is called
        Then: Special characters are preserved correctly
        """
        # Arrange
        template = "# {{title}}\n\n{{code}}"
        context = "title: Code Example\ncode: '```python\\nprint(\"Hello\")\\n```'"
        target = "README.md"

        # Act
        preview_path = generate_preview(template, context, target, output_dir=tmp_path)

        # Assert
        content = preview_path.read_text()
        assert "```python" in content
        assert 'print("Hello")' in content

    def test_preview_preserves_file_encoding(self, tmp_path):
        """
        Given: Template with unicode characters
        When: generate_preview() is called
        Then: Preview file preserves UTF-8 encoding
        """
        # Arrange
        template = "# {{title}}\n\n{{content}}"
        context = "title: Unicode Test\ncontent: Emoji test 🚀 and unicode: café"
        target = "README.md"

        # Act
        preview_path = generate_preview(template, context, target, output_dir=tmp_path)

        # Assert
        content = preview_path.read_text(encoding="utf-8")
        assert "🚀" in content
        assert "café" in content
