"""
Sprint 5 Deliverable 1: Extended Template Schema Tests (RED PHASE)

These tests define the expected behavior for the extended template schema
with section-level prompts for chunked generation mode.

Test Organization:
- TestSectionSchema: Basic section parsing with prompts
- TestTemplateSchemaValidation: Schema validation for chunked vs single-shot
- TestNestedSections: Nested section support with prompts
- TestBackwardCompatibility: Ensuring single-shot mode still works

These tests will FAIL until we implement:
1. Template schema dataclasses (Section, Document, Template)
2. JSON parsing for template files
3. Validation logic for chunked mode
"""

import json
from pathlib import Path

import pytest

from doc_evergreen.core.template_schema import Document

# These imports will fail initially - that's expected in RED phase
from doc_evergreen.core.template_schema import Section
from doc_evergreen.core.template_schema import Template
from doc_evergreen.core.template_schema import parse_template
from doc_evergreen.core.template_schema import validate_template


class TestSectionSchema:
    """Tests for basic Section schema with prompt field"""

    def test_section_with_prompt_parses(self) -> None:
        """
        Given: JSON with section containing prompt field
        When: Section is parsed
        Then: Section object has prompt attribute
        """
        section_data = {
            "heading": "Overview",
            "prompt": "High-level overview (2-3 paragraphs)",
            "sources": ["README.md"],
        }

        section = Section(**section_data)

        assert section.heading == "Overview"
        assert section.prompt == "High-level overview (2-3 paragraphs)"
        assert section.sources == ["README.md"]

    def test_section_without_prompt_defaults_none(self) -> None:
        """
        Given: JSON with section without prompt field
        When: Section is parsed
        Then: Section.prompt is None
        """
        section_data = {"heading": "Features", "sources": ["src/**/*.py"]}

        section = Section(**section_data)

        assert section.heading == "Features"
        assert section.prompt is None
        assert section.sources == ["src/**/*.py"]

    def test_section_with_empty_sources_list(self) -> None:
        """
        Given: JSON with section with empty sources
        When: Section is parsed
        Then: Section has empty sources list
        """
        section_data = {"heading": "Introduction", "prompt": "Brief intro paragraph"}

        section = Section(**section_data)  # type: ignore[arg-type]

        assert section.heading == "Introduction"
        assert section.prompt == "Brief intro paragraph"
        assert section.sources == []

    def test_section_minimal_only_heading(self) -> None:
        """
        Given: JSON with section containing only heading
        When: Section is parsed
        Then: Section has defaults for optional fields
        """
        section_data = {"heading": "Conclusion"}

        section = Section(**section_data)  # type: ignore[arg-type]

        assert section.heading == "Conclusion"
        assert section.prompt is None
        assert section.sources == []
        assert section.sections == []


class TestNestedSections:
    """Tests for nested sections with prompts"""

    def test_nested_sections_with_prompts(self) -> None:
        """
        Given: JSON with nested sections each having prompts
        When: Section tree is parsed
        Then: All sections have their prompts preserved
        """
        section_data = {
            "heading": "Features",
            "prompt": "List key features (bullet points)",
            "sources": ["src/**/*.py"],
            "sections": [
                {"heading": "Core Features", "prompt": "Describe core functionality", "sources": ["src/core/**/*.py"]},
                {
                    "heading": "Advanced Features",
                    "prompt": "Describe advanced capabilities",
                    "sources": ["src/advanced/**/*.py"],
                },
            ],
        }

        section = Section(**section_data)

        assert section.heading == "Features"
        assert section.prompt == "List key features (bullet points)"
        assert len(section.sections) == 2

        # Check first nested section
        assert section.sections[0].heading == "Core Features"
        assert section.sections[0].prompt == "Describe core functionality"
        assert section.sections[0].sources == ["src/core/**/*.py"]

        # Check second nested section
        assert section.sections[1].heading == "Advanced Features"
        assert section.sections[1].prompt == "Describe advanced capabilities"

    def test_deeply_nested_sections_three_levels(self) -> None:
        """
        Given: JSON with three levels of nested sections
        When: Section tree is parsed
        Then: All nesting levels preserved with prompts
        """
        section_data = {
            "heading": "API",
            "prompt": "API overview",
            "sections": [
                {
                    "heading": "REST API",
                    "prompt": "REST endpoints",
                    "sections": [{"heading": "Authentication", "prompt": "Auth endpoints details"}],
                }
            ],
        }

        section = Section(**section_data)

        assert section.sections[0].sections[0].heading == "Authentication"
        assert section.sections[0].sections[0].prompt == "Auth endpoints details"

    def test_mixed_nested_sections_some_with_prompts_some_without(self) -> None:
        """
        Given: Nested sections where some have prompts, others don't
        When: Section tree is parsed
        Then: Prompts preserved where present, None where absent
        """
        section_data = {
            "heading": "Documentation",
            "prompt": "Doc overview",
            "sections": [
                {"heading": "Getting Started", "prompt": "Quick start guide"},
                {
                    "heading": "Reference",
                    # No prompt for this section
                },
            ],
        }

        section = Section(**section_data)

        assert section.sections[0].prompt == "Quick start guide"
        assert section.sections[1].prompt is None


class TestTemplateSchemaValidation:
    """Tests for template schema validation (chunked vs single-shot mode)"""

    def test_single_shot_mode_prompts_optional(self, tmp_path: Path) -> None:
        """
        Given: Template without prompts in sections
        When: Validated for single-shot mode
        Then: Validation passes (prompts not required)
        """
        template_data = {
            "document": {
                "title": "Test README",
                "output": "README.md",
                "sections": [{"heading": "Overview", "sources": ["README.md"]}],
            }
        }

        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps(template_data))

        template = parse_template(template_file)
        validation_result = validate_template(template, mode="single")

        assert validation_result.valid is True
        assert len(validation_result.errors) == 0

    def test_chunked_mode_requires_prompts(self, tmp_path: Path) -> None:
        """
        Given: Template without prompts in sections
        When: Validated for chunked mode
        Then: Validation fails with clear error
        """
        template_data = {
            "document": {
                "title": "Test README",
                "output": "README.md",
                "sections": [
                    {
                        "heading": "Overview",
                        "sources": ["README.md"],
                        # Missing prompt for chunked mode
                    }
                ],
            }
        }

        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps(template_data))

        template = parse_template(template_file)
        validation_result = validate_template(template, mode="chunked")

        assert validation_result.valid is False
        assert len(validation_result.errors) > 0
        assert "prompt" in validation_result.errors[0].lower()
        assert "Overview" in validation_result.errors[0]

    def test_chunked_mode_all_sections_need_prompts(self, tmp_path: Path) -> None:
        """
        Given: Template with some sections missing prompts
        When: Validated for chunked mode
        Then: Validation fails listing ALL sections without prompts
        """
        template_data = {
            "document": {
                "title": "Test README",
                "output": "README.md",
                "sections": [
                    {"heading": "Overview", "prompt": "Write overview", "sources": ["README.md"]},
                    {
                        "heading": "Features",
                        # Missing prompt
                        "sources": ["src/**/*.py"],
                    },
                    {
                        "heading": "Installation",
                        # Missing prompt
                        "sources": ["setup.py"],
                    },
                ],
            }
        }

        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps(template_data))

        template = parse_template(template_file)
        validation_result = validate_template(template, mode="chunked")

        assert validation_result.valid is False
        assert len(validation_result.errors) == 2  # Two sections missing prompts
        # Check both sections are reported
        error_text = " ".join(validation_result.errors)
        assert "Features" in error_text
        assert "Installation" in error_text

    def test_chunked_mode_nested_sections_need_prompts(self, tmp_path: Path) -> None:
        """
        Given: Template with nested sections, some missing prompts
        When: Validated for chunked mode
        Then: Validation fails for nested sections without prompts
        """
        template_data = {
            "document": {
                "title": "Test README",
                "output": "README.md",
                "sections": [
                    {
                        "heading": "Features",
                        "prompt": "List features",
                        "sections": [
                            {"heading": "Core", "prompt": "Core features"},
                            {
                                "heading": "Advanced",
                                # Missing prompt in nested section
                            },
                        ],
                    }
                ],
            }
        }

        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps(template_data))

        template = parse_template(template_file)
        validation_result = validate_template(template, mode="chunked")

        assert validation_result.valid is False
        assert "Advanced" in validation_result.errors[0]

    def test_chunked_mode_all_prompts_present_passes(self, tmp_path: Path) -> None:
        """
        Given: Template with ALL sections having prompts
        When: Validated for chunked mode
        Then: Validation passes
        """
        template_data = {
            "document": {
                "title": "Test README",
                "output": "README.md",
                "sections": [
                    {"heading": "Overview", "prompt": "Write overview", "sources": ["README.md"]},
                    {
                        "heading": "Features",
                        "prompt": "List features",
                        "sources": ["src/**/*.py"],
                        "sections": [{"heading": "Core", "prompt": "Core features"}],
                    },
                ],
            }
        }

        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps(template_data))

        template = parse_template(template_file)
        validation_result = validate_template(template, mode="chunked")

        assert validation_result.valid is True
        assert len(validation_result.errors) == 0


class TestTemplateStructure:
    """Tests for complete template structure (Document and Template)"""

    def test_parse_complete_template(self, tmp_path: Path) -> None:
        """
        Given: Complete JSON template file
        When: parse_template is called
        Then: Returns Template object with Document and Sections
        """
        template_data = {
            "document": {
                "title": "Project README",
                "output": "README.md",
                "sections": [{"heading": "Overview", "prompt": "Write overview", "sources": ["README.md"]}],
            }
        }

        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps(template_data))

        template = parse_template(template_file)

        assert isinstance(template, Template)
        assert isinstance(template.document, Document)
        assert template.document.title == "Project README"
        assert template.document.output == "README.md"
        assert len(template.document.sections) == 1
        assert template.document.sections[0].heading == "Overview"

    def test_parse_template_invalid_json_raises_error(self, tmp_path: Path) -> None:
        """
        Given: File with invalid JSON
        When: parse_template is called
        Then: Raises clear error about JSON parsing
        """
        template_file = tmp_path / "bad_template.json"
        template_file.write_text("{ invalid json }")

        with pytest.raises(ValueError) as exc_info:
            parse_template(template_file)

        assert "json" in str(exc_info.value).lower()

    def test_parse_template_missing_document_raises_error(self, tmp_path: Path) -> None:
        """
        Given: JSON without 'document' key
        When: parse_template is called
        Then: Raises clear error about missing document
        """
        template_data = {"wrong_key": {}}

        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps(template_data))

        with pytest.raises(ValueError) as exc_info:
            parse_template(template_file)

        assert "document" in str(exc_info.value).lower()

    def test_parse_template_missing_required_fields_raises_error(self, tmp_path: Path) -> None:
        """
        Given: JSON with document but missing required fields (title, output)
        When: parse_template is called
        Then: Raises clear error about missing fields
        """
        template_data = {
            "document": {
                # Missing title and output
                "sections": []
            }
        }

        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps(template_data))

        with pytest.raises(ValueError) as exc_info:
            parse_template(template_file)

        error_msg = str(exc_info.value).lower()
        assert "title" in error_msg or "output" in error_msg


class TestBackwardCompatibility:
    """Tests ensuring single-shot mode works without section prompts"""

    def test_existing_templates_without_prompts_still_work(self, tmp_path: Path) -> None:
        """
        Given: Existing template from v0.1.0 (no prompts)
        When: Parsed and validated for single-shot
        Then: Works without modification
        """
        # This is what v0.1.0 templates look like
        template_data = {
            "document": {
                "title": "Legacy README",
                "output": "README.md",
                "sections": [
                    {"heading": "Overview", "sources": ["README.md", "src/**/*.py"]},
                    {"heading": "Installation", "sources": ["setup.py", "pyproject.toml"]},
                ],
            }
        }

        template_file = tmp_path / "legacy_template.json"
        template_file.write_text(json.dumps(template_data))

        template = parse_template(template_file)
        validation_result = validate_template(template, mode="single")

        assert validation_result.valid is True
        # Sections should parse with prompt=None
        assert template.document.sections[0].prompt is None
        assert template.document.sections[1].prompt is None

    def test_mode_defaults_to_single_if_not_specified(self, tmp_path: Path) -> None:
        """
        Given: Template validated without mode specified
        When: validate_template called with no mode argument
        Then: Defaults to single-shot (backward compatible)
        """
        template_data = {
            "document": {
                "title": "Test README",
                "output": "README.md",
                "sections": [{"heading": "Overview", "sources": ["README.md"]}],
            }
        }

        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps(template_data))

        template = parse_template(template_file)
        validation_result = validate_template(template)  # No mode argument

        assert validation_result.valid is True
