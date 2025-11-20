"""Source validation for doc_evergreen templates.

Validates all source files upfront before generation starts (fail early).
"""

import logging
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from doc_evergreen.core.template_schema import Section
from doc_evergreen.core.template_schema import Template

logger = logging.getLogger(__name__)


class SourceValidationError(Exception):
    """Raised when source validation fails."""


@dataclass
class SourceValidationResult:
    """Result of source validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    section_sources: dict[str, list[Path]] = field(default_factory=dict)
    section_stats: dict[str, dict[str, int]] = field(default_factory=dict)


def validate_all_sources(template: Template, base_dir: Path) -> SourceValidationResult:
    """Validate all sources upfront (fail early).

    Args:
        template: Template to validate
        base_dir: Base directory to resolve sources relative to

    Returns:
        SourceValidationResult with resolved sources and statistics

    Raises:
        SourceValidationError: If any section has no sources
    """
    # Cache for resolved glob patterns
    glob_cache: dict[str, list[Path]] = {}

    section_sources: dict[str, list[Path]] = {}
    section_stats: dict[str, dict[str, int]] = {}
    errors: list[str] = []

    def resolve_source_pattern(pattern: str) -> list[Path]:
        """Resolve a single source pattern with caching."""
        if pattern in glob_cache:
            return glob_cache[pattern]

        # Try glob pattern first
        resolved = list(base_dir.glob(pattern))

        # If no match, try literal path
        if not resolved:
            literal_path = base_dir / pattern
            if literal_path.exists():
                resolved = [literal_path]

        # Cache the result
        glob_cache[pattern] = resolved
        return resolved

    def validate_section(section: Section, path: str = "") -> None:
        """Recursively validate a section and its children."""
        section_name = section.heading
        full_path = f"{path}/{section_name}" if path else section_name

        # Resolve all source patterns for this section
        all_sources: list[Path] = []
        for pattern in section.sources:
            resolved = resolve_source_pattern(pattern)
            all_sources.extend(resolved)

        # Remove duplicates (in case patterns overlap)
        all_sources = list(set(all_sources))

        # Check if section has any sources
        if not all_sources:
            patterns_str = ", ".join(f"'{p}'" for p in section.sources)
            error = (
                f"Section '{section_name}' has no sources - no files matched patterns: {patterns_str}\n"
                f"\n"
                f"Possible causes:\n"
                f"  1. Patterns are relative to template location (use '../' to go up)\n"
                f"  2. Files don't exist at specified paths\n"
                f"  3. Pattern syntax is incorrect\n"
                f"\n"
                f"Fix:\n"
                f"  - Check paths are relative to template: '../src/*.py'\n"
                f"  - Verify files exist: ls {base_dir}/your-pattern\n"
                f"  - See: TEMPLATES.md#source-resolution\n"
            )
            errors.append(error)
            raise SourceValidationError(error)

        # Store resolved sources
        section_sources[section_name] = all_sources

        # Calculate statistics
        file_count = len(all_sources)
        total_bytes = sum(s.stat().st_size for s in all_sources)
        section_stats[section_name] = {
            "file_count": file_count,
            "total_bytes": total_bytes,
        }

        # Recursively validate nested sections
        for child in section.sections:
            validate_section(child, full_path)

    # Validate all top-level sections
    for section in template.document.sections:
        validate_section(section)

    return SourceValidationResult(
        valid=True,
        errors=[],
        section_sources=section_sources,
        section_stats=section_stats,
    )


def display_validation_report(result: SourceValidationResult) -> None:
    """Display formatted validation report.

    Args:
        result: Validation result to display
    """
    logger.info("\n📋 Validating template sources...")
    logger.info("")

    if not result.valid:
        # Show errors
        logger.error("❌ Validation failed:\n")
        for error in result.errors:
            logger.error(f"  ERROR: {error}")
        logger.info("\n  Fix: Check that all source paths exist relative to base directory")
        return

    # Show successful validation
    for section_name, sources in result.section_sources.items():
        logger.info(f"Section: {section_name}")
        logger.info(f"  Sources: {[str(s.name) for s in sources]}")

        stats = result.section_stats.get(section_name, {})
        file_count = stats.get("file_count", 0)
        total_bytes = stats.get("total_bytes", 0)

        for source in sources:
            size_kb = source.stat().st_size / 1024
            logger.info(f"  ✅ Found: {source.name} ({size_kb:.1f} KB)")

        logger.info(f"  Total: {file_count} files, {total_bytes / 1024:.1f} KB")
        logger.info("")
