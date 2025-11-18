"""
Sprint 3 Deliverable 1: Template Manager Tests (RED PHASE)

These tests define the expected behavior for template discovery, loading,
and auto-detection. They will FAIL until template_manager.py is implemented.

Test Organization:
- TestTemplateDiscovery: Finding available templates
- TestTemplateLoading: Loading template content
- TestTemplateDetection: Auto-detecting templates from filenames
- TestTemplateMetadata: Parsing template frontmatter (optional)
"""

from pathlib import Path

import pytest

from doc_evergreen.template_manager import detect_template
from doc_evergreen.template_manager import list_templates
from doc_evergreen.template_manager import load_template
from doc_evergreen.template_manager import parse_template_metadata


class TestTemplateDiscovery:
    """Tests for discovering available templates"""

    def test_list_templates_finds_markdown_files(self, tmp_path: Path) -> None:
        """
        Given: A templates directory with .md files
        When: list_templates is called
        Then: Returns list of template names without extensions
        """
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        (templates_dir / "readme.md").write_text("# README Template")
        (templates_dir / "contributing.md").write_text("# Contributing Template")
        (templates_dir / "api-reference.md").write_text("# API Template")

        result = list_templates(templates_dir)

        assert len(result) == 3
        assert "readme" in result
        assert "contributing" in result
        assert "api-reference" in result

    def test_list_templates_empty_directory(self, tmp_path: Path) -> None:
        """
        Given: An empty templates directory
        When: list_templates is called
        Then: Returns empty list without error
        """
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        result = list_templates(templates_dir)

        assert result == []

    def test_list_templates_ignores_non_markdown(self, tmp_path: Path) -> None:
        """
        Given: A templates directory with various file types
        When: list_templates is called
        Then: Returns only .md files, ignores others
        """
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        (templates_dir / "readme.md").write_text("# Template")
        (templates_dir / "notes.txt").write_text("Not a template")
        (templates_dir / "config.yaml").write_text("config: value")
        (templates_dir / ".hidden.md").write_text("# Hidden")

        result = list_templates(templates_dir)

        assert len(result) == 1
        assert "readme" in result

    def test_list_templates_missing_directory(self, tmp_path: Path) -> None:
        """
        Given: A non-existent templates directory
        When: list_templates is called
        Then: Returns empty list without error
        """
        templates_dir = tmp_path / "nonexistent"

        result = list_templates(templates_dir)

        assert result == []


class TestTemplateLoading:
    """Tests for loading template content"""

    def test_load_template_by_name(self, tmp_path: Path) -> None:
        """
        Given: A template file exists with name "readme"
        When: load_template("readme") is called
        Then: Returns template content as string
        """
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        template_content = "# {{project_name}}\n\nA great project."
        (templates_dir / "readme.md").write_text(template_content)

        result = load_template("readme", templates_dir)

        assert result == template_content

    def test_load_template_by_absolute_path(self, tmp_path: Path) -> None:
        """
        Given: A template file at an absolute path
        When: load_template(absolute_path) is called
        Then: Returns template content from that path
        """
        template_file = tmp_path / "custom_template.md"
        template_content = "# Custom Template\n\nContent here."
        template_file.write_text(template_content)

        result = load_template(str(template_file))

        assert result == template_content

    def test_load_template_by_relative_path(self, tmp_path: Path) -> None:
        """
        Given: A template file at a relative path
        When: load_template(relative_path) is called
        Then: Returns template content from that path
        """
        template_file = tmp_path / "my_template.md"
        template_content = "# Relative Template"
        template_file.write_text(template_content)

        result = load_template(f"./{template_file.name}", templates_dir=tmp_path)

        assert result == template_content

    def test_load_template_not_found_raises_error(self, tmp_path: Path) -> None:
        """
        Given: A non-existent template name
        When: load_template is called
        Then: Raises clear error with helpful message
        """
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        with pytest.raises(FileNotFoundError) as exc_info:
            load_template("nonexistent", templates_dir)

        assert "nonexistent" in str(exc_info.value).lower()
        assert "template" in str(exc_info.value).lower()

    def test_load_template_with_frontmatter(self, tmp_path: Path) -> None:
        """
        Given: A template with YAML frontmatter
        When: load_template is called
        Then: Returns full content including frontmatter
        """
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        template_content = """---
name: Test Template
description: A test
---

# {{project_name}}

Content here.
"""
        (templates_dir / "test.md").write_text(template_content)

        result = load_template("test", templates_dir)

        assert result == template_content
        assert "---" in result
        assert "name: Test Template" in result


class TestTemplateDetection:
    """Tests for auto-detecting templates from filenames"""

    def test_detect_template_from_readme(self) -> None:
        """
        Given: Target file is "README.md"
        When: detect_template is called
        Then: Returns "readme" template name
        """
        result = detect_template("README.md")

        assert result == "readme"

    def test_detect_template_from_lowercase_readme(self) -> None:
        """
        Given: Target file is "readme.md"
        When: detect_template is called
        Then: Returns "readme" template name (case-insensitive)
        """
        result = detect_template("readme.md")

        assert result == "readme"

    def test_detect_template_from_contributing(self) -> None:
        """
        Given: Target file is "CONTRIBUTING.md"
        When: detect_template is called
        Then: Returns "contributing" template name
        """
        result = detect_template("CONTRIBUTING.md")

        assert result == "contributing"

    def test_detect_template_from_api_reference(self) -> None:
        """
        Given: Target file is "API.md" or "docs/API.md"
        When: detect_template is called
        Then: Returns "api-reference" template name
        """
        assert detect_template("API.md") == "api-reference"
        assert detect_template("docs/API.md") == "api-reference"

    def test_detect_template_from_changelog(self) -> None:
        """
        Given: Target file is "CHANGELOG.md"
        When: detect_template is called
        Then: Returns "changelog" template name
        """
        result = detect_template("CHANGELOG.md")

        assert result == "changelog"

    def test_detect_template_from_path_object(self) -> None:
        """
        Given: Target file is a Path object
        When: detect_template is called
        Then: Returns appropriate template name
        """
        result = detect_template(Path("docs/README.md"))

        assert result == "readme"

    def test_detect_template_default_for_unknown(self) -> None:
        """
        Given: Target file doesn't match known patterns
        When: detect_template is called
        Then: Returns "readme" as default template
        """
        result = detect_template("RANDOM_FILE.md")

        assert result == "readme"

    def test_detect_template_ignores_path_components(self) -> None:
        """
        Given: Target file has path components
        When: detect_template is called
        Then: Detects based on filename only, not path
        """
        assert detect_template("docs/subdir/CONTRIBUTING.md") == "contributing"
        assert detect_template("/absolute/path/to/README.md") == "readme"


class TestTemplateMetadata:
    """Tests for parsing template frontmatter metadata (optional feature)"""

    def test_parse_template_metadata_with_frontmatter(self) -> None:
        """
        Given: Template content with YAML frontmatter
        When: parse_template_metadata is called
        Then: Returns metadata dict and content separately
        """
        template_content = """---
name: Test Template
description: A test template
suggested_sources:
  - README.md
  - CONTRIBUTING.md
---

# {{project_name}}

Content here.
"""
        metadata, content = parse_template_metadata(template_content)

        assert metadata["name"] == "Test Template"
        assert metadata["description"] == "A test template"
        assert "README.md" in metadata["suggested_sources"]
        assert "# {{project_name}}" in content
        assert "---" not in content

    def test_parse_template_metadata_without_frontmatter(self) -> None:
        """
        Given: Template content without YAML frontmatter
        When: parse_template_metadata is called
        Then: Returns empty metadata dict and full content
        """
        template_content = "# {{project_name}}\n\nNo frontmatter here."

        metadata, content = parse_template_metadata(template_content)

        assert metadata == {}
        assert content == template_content

    def test_parse_template_metadata_malformed_frontmatter(self) -> None:
        """
        Given: Template with malformed YAML frontmatter
        When: parse_template_metadata is called
        Then: Returns empty metadata and treats as plain content
        """
        template_content = """---
name: Test
invalid yaml: [unclosed
---

# Content
"""
        metadata, content = parse_template_metadata(template_content)

        assert metadata == {}
        assert "name: Test" in content

    def test_parse_template_metadata_empty_frontmatter(self) -> None:
        """
        Given: Template with empty frontmatter
        When: parse_template_metadata is called
        Then: Returns empty metadata dict
        """
        template_content = """---
---

# {{project_name}}
"""
        metadata, content = parse_template_metadata(template_content)

        assert metadata == {}
        assert "# {{project_name}}" in content
