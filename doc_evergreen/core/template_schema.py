"""Template schema for doc_evergreen with section-level prompts."""

import json
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


@dataclass
class Section:
    """Section within a document template."""

    heading: str
    prompt: str | None = None
    sources: list[str] = field(default_factory=list)
    sections: list["Section"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Convert dict sections to Section objects."""
        self.sections = [Section(**s) if isinstance(s, dict) else s for s in self.sections]


@dataclass
class Document:
    """Document structure with sections."""

    title: str
    output: str
    sections: list[Section]


@dataclass
class Template:
    """Complete template containing document definition."""

    document: Document


@dataclass
class ValidationResult:
    """Result of template validation."""

    valid: bool
    errors: list[str]


def parse_template(path: Path) -> Template:
    """Parse a JSON template file into a Template object.

    Args:
        path: Path to JSON template file

    Returns:
        Template object

    Raises:
        ValueError: If JSON is invalid or required fields are missing
    """
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    if "document" not in data:
        raise ValueError("Template missing required 'document' key")

    doc_data = data["document"]

    if "title" not in doc_data or "output" not in doc_data:
        raise ValueError("Document missing required fields: 'title' and 'output'")

    sections = [_parse_section(s) for s in doc_data.get("sections", [])]

    document = Document(title=doc_data["title"], output=doc_data["output"], sections=sections)

    return Template(document=document)


def _parse_section(data: dict) -> Section:
    """Parse section data recursively."""
    nested_sections = [_parse_section(s) for s in data.get("sections", [])]

    return Section(
        heading=data["heading"],
        prompt=data.get("prompt"),
        sources=data.get("sources", []),
        sections=nested_sections,
    )


def validate_template(template: Template, mode: str = "single") -> ValidationResult:
    """Validate template based on generation mode.

    Args:
        template: Template to validate
        mode: Generation mode - "single" or "chunked"

    Returns:
        ValidationResult with validation status and errors
    """
    errors: list[str] = []

    if mode == "chunked":
        # In chunked mode, all sections must have prompts
        _check_prompts_recursive(template.document.sections, errors)

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def _check_prompts_recursive(sections: list[Section], errors: list[str]) -> None:
    """Recursively check that all sections have prompts."""
    for section in sections:
        if section.prompt is None:
            errors.append(f"Section '{section.heading}' missing required prompt for chunked mode")

        # Check nested sections
        if section.sections:
            _check_prompts_recursive(section.sections, errors)
