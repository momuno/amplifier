"""
Tests for Sprint 1: Template Loading Functionality

Following TDD RED phase - these tests define behavior before implementation exists.
"""

import os
from pathlib import Path

import pytest

from doc_evergreen.context import gather_context
from doc_evergreen.generator import generate_doc
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


class TestLLMGenerator:
    """Tests for LLM-powered documentation generator"""

    def test_generate_doc_returns_markdown(self) -> None:
        """
        Given: A template string and context string
        When: generate_doc is called
        Then: Returns a non-empty string containing markdown documentation

        Testing Decision: Call real LLM to validate integration
        Rationale: POC needs to prove end-to-end flow works with actual LLM
        Trade-off: Slower test (~2-5s) but validates real behavior
        """
        # Arrange
        template = """# {{project_name}}

## Overview
Describe the project purpose.

## Installation
Provide installation steps."""

        context = """--- README.md ---
# Amplifier
A tool for amplifying development workflows.

--- pyproject.toml ---
[project]
name = "amplifier"
version = "0.1.0"
"""

        # Act
        result = generate_doc(template=template, context=context)

        # Assert: Returns non-empty string
        assert isinstance(result, str)
        assert len(result) > 0

        # Assert: Contains markdown structure (headers)
        assert "#" in result

        # Assert: Not just echoing template (shows LLM processing)
        assert result != template

    def test_generate_doc_uses_context_information(self) -> None:
        """
        Given: Template and context with specific project details
        When: generate_doc is called
        Then: Generated content references information from context

        Testing Decision: Verify LLM uses context, not just template
        Rationale: Core POC requirement - must synthesize template + context
        """
        # Arrange
        template = """# Project Documentation

## Name
State the project name.

## Purpose
Explain what this project does."""

        context = """--- README.md ---
# DataProcessor
A high-performance data processing pipeline.

Processes CSV files and generates analytics reports."""

        # Act
        result = generate_doc(template=template, context=context)

        # Assert: Contains project-specific information from context
        # (LLM should mention DataProcessor or data processing)
        result_lower = result.lower()
        assert any(term in result_lower for term in ["dataprocessor", "data processing", "csv", "analytics"]), (
            "Generated doc should reference information from context"
        )

    def test_generate_doc_maintains_template_structure(self) -> None:
        """
        Given: Template with clear section markers
        When: generate_doc is called
        Then: Generated content follows template structure

        Testing Decision: Verify output respects template sections
        Rationale: Documentation should follow provided template format
        """
        # Arrange
        template = """# Documentation

## Installation
Installation steps here.

## Configuration
Configuration details here.

## Usage
Usage examples here."""

        context = """--- README.md ---
# MyTool
Install with: pip install mytool
Configure in config.yaml
Use: mytool run"""

        # Act
        result = generate_doc(template=template, context=context)

        # Assert: Major section headers present
        assert "## Installation" in result or "Installation" in result
        assert "## Configuration" in result or "Configuration" in result
        assert "## Usage" in result or "Usage" in result


class TestIntegration:
    """End-to-end integration tests"""

    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY required for integration test"
    )
    def test_end_to_end_generation(self, tmp_path: Path, monkeypatch) -> None:
        """
        Given: Template file and source files exist
        When: Complete generation pipeline runs
        Then: Valid markdown documentation is produced

        Testing Decision: Use real LLM to validate full integration
        Rationale: POC must prove the entire pipeline works together
        Trade-off: Slower test (~5-10s) but validates complete flow
        """
        # Arrange: Create template file
        template_content = """# {{project_name}} Documentation

## Overview
Describe what this project does and why it exists.

## Installation
Provide installation instructions.

## Configuration
Explain how to configure the project.

## Usage
Show usage examples."""

        template_file = tmp_path / "template.md"
        template_file.write_text(template_content, encoding="utf-8")

        # Arrange: Create source files
        (tmp_path / "amplifier").mkdir()

        readme_content = """# Amplifier
A tool for amplifying development workflows with AI agents.

## Features
- Template-based documentation generation
- Context-aware updates
- Integration with Claude Code"""

        (tmp_path / "README.md").write_text(readme_content, encoding="utf-8")

        pyproject_content = """[project]
name = "amplifier"
version = "0.1.0"
description = "AI-powered development workflow amplifier"
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")

        init_content = """# Amplifier package
__version__ = '0.1.0'
"""
        (tmp_path / "amplifier" / "__init__.py").write_text(init_content, encoding="utf-8")

        agents_content = """# AI Agent Guide
Instructions for AI agents working with this codebase."""
        (tmp_path / "AGENTS.md").write_text(agents_content, encoding="utf-8")

        # Mock working directory to use tmp_path
        monkeypatch.chdir(tmp_path)

        # Act: Step 1 - Load template
        loaded_template = load_template(str(template_file))
        assert loaded_template == template_content, "Template loading failed"

        # Act: Step 2 - Gather context
        gathered_context = gather_context()
        assert "README.md" in gathered_context, "Context gathering failed"
        assert "amplifier" in gathered_context.lower(), "Context should contain project name"

        # Act: Step 3 - Generate documentation
        generated_doc = generate_doc(template=loaded_template, context=gathered_context)

        # Assert: Validate output is non-empty
        assert isinstance(generated_doc, str)
        assert len(generated_doc) > 0, "Generated doc should not be empty"

        # Assert: Contains markdown structure
        assert "#" in generated_doc, "Generated doc should contain markdown headers"

        # Assert: Output differs from template (proves LLM processing)
        assert generated_doc != template_content, "Generated doc should be processed, not echo template"

        # Assert: Output references context information
        # Should mention "amplifier" or "workflow" from context
        generated_lower = generated_doc.lower()
        assert any(term in generated_lower for term in ["amplifier", "workflow", "ai", "claude"]), (
            "Generated doc should reference information from context"
        )

        # Assert: Output maintains template structure
        # Should have major sections from template
        assert any(section in generated_doc for section in ["Overview", "Installation", "Configuration", "Usage"]), (
            "Generated doc should maintain template structure"
        )
