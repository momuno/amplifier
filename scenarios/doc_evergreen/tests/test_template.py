"""
Tests for template management.
"""

import tempfile
from pathlib import Path

import pytest

from doc_evergreen.core.template import (
    create_template_metadata,
    find_latest_version,
    format_template_with_metadata,
    get_builtin_templates_dir,
    get_template_path,
    list_builtin_templates,
    load_builtin_template,
    load_template_from_path,
    parse_template_metadata,
    save_template,
    select_builtin_template,
)


def test_get_builtin_templates_dir():
    """Test getting built-in templates directory."""
    templates_dir = get_builtin_templates_dir()

    # Should be a Path
    assert isinstance(templates_dir, Path)

    # Should end with /templates
    assert templates_dir.name == "templates"


def test_list_builtin_templates():
    """Test listing built-in templates."""
    templates = list_builtin_templates()

    # Should return a list
    assert isinstance(templates, list)

    # Should include our templates
    assert "readme" in templates
    assert "api-reference" in templates
    assert "user-guide" in templates
    assert "developer-guide" in templates


def test_load_builtin_template_success():
    """Test loading an existing built-in template."""
    content = load_builtin_template("readme")

    # Should return content
    assert len(content) > 0
    assert "README" in content or "readme" in content.lower()


def test_load_builtin_template_not_found():
    """Test loading non-existent built-in template."""
    with pytest.raises(FileNotFoundError, match="not found"):
        load_builtin_template("nonexistent-template")


def test_parse_template_metadata_with_frontmatter():
    """Test parsing template with YAML frontmatter."""
    template = """---
name: test-template
version: 1
derived_from: readme
---

# Template Content

This is the template.
"""

    metadata, content = parse_template_metadata(template)

    assert metadata["name"] == "test-template"
    assert metadata["version"] == 1
    assert metadata["derived_from"] == "readme"
    assert content.startswith("# Template Content")


def test_parse_template_metadata_without_frontmatter():
    """Test parsing template without frontmatter."""
    template = "# Template\n\nNo metadata here."

    metadata, content = parse_template_metadata(template)

    assert metadata == {}
    assert content == template


def test_parse_template_metadata_invalid_yaml():
    """Test parsing template with invalid YAML."""
    template = """---
invalid: yaml: structure:
---

Content
"""

    metadata, content = parse_template_metadata(template)

    # Should return empty metadata and original content
    assert metadata == {}
    assert content == template


def test_create_template_metadata():
    """Test creating template metadata."""
    metadata = create_template_metadata(
        name="test-template",
        version=1,
        derived_from="readme",
        customizations=["Added custom section", "Modified tone"],
    )

    assert metadata["name"] == "test-template"
    assert metadata["version"] == 1
    assert metadata["derived_from"] == "readme"
    assert "created" in metadata
    assert len(metadata["customizations"]) == 2


def test_create_template_metadata_minimal():
    """Test creating minimal metadata."""
    metadata = create_template_metadata(name="simple", version=1)

    assert metadata["name"] == "simple"
    assert metadata["version"] == 1
    assert "created" in metadata
    assert "derived_from" not in metadata
    assert "customizations" not in metadata


def test_format_template_with_metadata():
    """Test formatting template with metadata."""
    metadata = {"name": "test", "version": 1}
    content = "# Template\n\nContent here."

    formatted = format_template_with_metadata(metadata, content)

    assert formatted.startswith("---\n")
    assert "name: test" in formatted
    assert "version: 1" in formatted
    assert "---\n\n# Template" in formatted


def test_find_latest_version_no_versions():
    """Test finding latest version when none exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        version = find_latest_version("test-template", repo)

        assert version == 0


def test_find_latest_version_with_versions():
    """Test finding latest version when versions exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        templates_dir = repo / ".doc-evergreen" / "templates"
        templates_dir.mkdir(parents=True)

        # Create some template versions
        (templates_dir / "test-template.v1.md").write_text("v1")
        (templates_dir / "test-template.v2.md").write_text("v2")
        (templates_dir / "test-template.v5.md").write_text("v5")

        version = find_latest_version("test-template", repo)

        assert version == 5


def test_save_template_first_version():
    """Test saving first version of template."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        content = "# Template\n\nContent here."

        saved_path = save_template(
            template_content=content,
            template_name="test-template",
            repo_path=repo,
        )

        # Should create v1
        assert saved_path.name == "test-template.v1.md"
        assert saved_path.exists()

        # Check content
        saved_content = saved_path.read_text()
        assert "name: test-template" in saved_content
        assert "version: 1" in saved_content
        assert "# Template" in saved_content


def test_save_template_subsequent_version():
    """Test saving subsequent versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Save v1
        save_template("v1 content", "test", repo)

        # Save v2
        saved_path = save_template("v2 content", "test", repo)

        assert saved_path.name == "test.v2.md"


def test_save_template_with_metadata():
    """Test saving template with custom metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        content = "# Template"
        metadata = {
            "derived_from": "readme",
            "customizations": ["Custom change"],
        }

        saved_path = save_template(content, "test", repo, metadata=metadata)

        saved_content = saved_path.read_text()
        assert "derived_from: readme" in saved_content
        assert "Custom change" in saved_content


def test_save_template_preserves_existing_metadata():
    """Test that saving preserves metadata from content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        content = """---
derived_from: readme
custom_field: value
---

# Content
"""

        saved_path = save_template(content, "test", repo)

        saved_content = saved_path.read_text()
        assert "derived_from: readme" in saved_content
        assert "custom_field: value" in saved_content


def test_load_template_from_path_relative():
    """Test loading template from relative path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        templates_dir = repo / ".doc-evergreen" / "templates"
        templates_dir.mkdir(parents=True)

        template_file = templates_dir / "test.v1.md"
        template_file.write_text("Template content")

        content = load_template_from_path(".doc-evergreen/templates/test.v1.md", repo)

        assert content == "Template content"


def test_load_template_from_path_not_found():
    """Test loading non-existent template."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        with pytest.raises(FileNotFoundError):
            load_template_from_path("nonexistent.md", repo)


def test_get_template_path_specific_version():
    """Test getting path to specific version."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        templates_dir = repo / ".doc-evergreen" / "templates"
        templates_dir.mkdir(parents=True)

        (templates_dir / "test.v1.md").write_text("v1")
        (templates_dir / "test.v2.md").write_text("v2")

        path = get_template_path("test", version=1, repo_path=repo)

        assert path.name == "test.v1.md"


def test_get_template_path_latest_version():
    """Test getting latest version when version not specified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        templates_dir = repo / ".doc-evergreen" / "templates"
        templates_dir.mkdir(parents=True)

        (templates_dir / "test.v1.md").write_text("v1")
        (templates_dir / "test.v2.md").write_text("v2")

        path = get_template_path("test", version=None, repo_path=repo)

        assert path.name == "test.v2.md"


def test_get_template_path_not_found():
    """Test getting path when template doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        with pytest.raises(FileNotFoundError):
            get_template_path("nonexistent", version=1, repo_path=repo)


def test_get_template_path_no_versions():
    """Test getting path when no versions exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        with pytest.raises(FileNotFoundError, match="No versions"):
            get_template_path("test", version=None, repo_path=repo)


def test_select_builtin_template_readme():
    """Test selecting template for README."""
    template = select_builtin_template("Main project README")
    assert template == "readme"


def test_select_builtin_template_api():
    """Test selecting template for API docs."""
    template = select_builtin_template("API reference for module")
    assert template == "api-reference"


def test_select_builtin_template_user_guide():
    """Test selecting template for user guide."""
    template = select_builtin_template("User guide for CLI")
    assert template == "user-guide"


def test_select_builtin_template_developer():
    """Test selecting template for developer guide."""
    template = select_builtin_template("Contributing guidelines")
    assert template == "developer-guide"


def test_select_builtin_template_default():
    """Test selecting template with no keyword match."""
    template = select_builtin_template("Some random documentation")
    assert template == "readme"  # Default
