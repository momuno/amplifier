"""
Tests for Sprint 4: Source Resolution

Tests the source_resolver module that handles:
- Parsing comma-separated source specifications
- Expanding glob patterns (*, **)
- Applying exclusion patterns
- Resolving final source lists with CLI/config priority
- Validating that sources exist

These tests follow TDD: they're written FIRST and will FAIL until
source_resolver.py is implemented.
"""

from pathlib import Path

from doc_evergreen.source_resolver import apply_exclusions
from doc_evergreen.source_resolver import expand_glob_patterns
from doc_evergreen.source_resolver import parse_source_spec
from doc_evergreen.source_resolver import resolve_sources
from doc_evergreen.source_resolver import validate_sources

# ============================================================================
# Test Class 1: Source Spec Parsing
# ============================================================================


class TestSourceSpecParsing:
    """Tests for parsing comma-separated source specifications."""

    def test_parse_single_source(self):
        """
        Given: A source spec with a single file
        When: parse_source_spec is called
        Then: Returns list with one file path
        """
        spec = "file.py"

        result = parse_source_spec(spec)

        assert result == ["file.py"]
        assert len(result) == 1

    def test_parse_multiple_sources(self):
        """
        Given: A source spec with multiple comma-separated files
        When: parse_source_spec is called
        Then: Returns list with all file paths
        """
        spec = "a.py,b.py,c.py"

        result = parse_source_spec(spec)

        assert result == ["a.py", "b.py", "c.py"]
        assert len(result) == 3

    def test_parse_with_spaces(self):
        """
        Given: A source spec with spaces around commas
        When: parse_source_spec is called
        Then: Returns list with trimmed file paths
        """
        spec = "a.py, b.py , c.py"

        result = parse_source_spec(spec)

        assert result == ["a.py", "b.py", "c.py"]
        assert all(" " not in path for path in result)

    def test_parse_empty_spec(self):
        """
        Given: An empty source spec
        When: parse_source_spec is called
        Then: Returns empty list
        """
        spec = ""

        result = parse_source_spec(spec)

        assert result == []
        assert len(result) == 0


# ============================================================================
# Test Class 2: Glob Expansion
# ============================================================================


class TestGlobExpansion:
    """Tests for expanding glob patterns to actual file paths."""

    def test_expand_literal_path(self, tmp_path):
        """
        Given: A literal file path (no glob characters)
        When: expand_glob_patterns is called
        Then: Returns the path as-is without expansion
        """
        test_file = tmp_path / "test.py"
        test_file.write_text("# test")
        patterns = [str(test_file)]

        result = expand_glob_patterns(patterns, base_dir=tmp_path)

        assert len(result) == 1
        assert Path(result[0]) == test_file

    def test_expand_single_dir_glob(self, tmp_path):
        """
        Given: A glob pattern matching files in a single directory
        When: expand_glob_patterns is called
        Then: Returns all matching files in that directory
        """
        # Create test files
        (tmp_path / "a.py").write_text("# a")
        (tmp_path / "b.py").write_text("# b")
        (tmp_path / "c.txt").write_text("text")
        patterns = ["*.py"]

        result = expand_glob_patterns(patterns, base_dir=tmp_path)

        assert len(result) == 2
        result_names = {Path(p).name for p in result}
        assert result_names == {"a.py", "b.py"}

    def test_expand_recursive_glob(self, tmp_path):
        """
        Given: A recursive glob pattern (**/*)
        When: expand_glob_patterns is called
        Then: Returns matching files in all subdirectories
        """
        # Create nested structure
        (tmp_path / "a.py").write_text("# a")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "b.py").write_text("# b")
        nested = subdir / "nested"
        nested.mkdir()
        (nested / "c.py").write_text("# c")
        patterns = ["**/*.py"]

        result = expand_glob_patterns(patterns, base_dir=tmp_path)

        assert len(result) == 3
        result_names = {Path(p).name for p in result}
        assert result_names == {"a.py", "b.py", "c.py"}

    def test_expand_mixed_patterns(self, tmp_path):
        """
        Given: A mix of literal paths and glob patterns
        When: expand_glob_patterns is called
        Then: Returns combination of literal and expanded paths
        """
        # Create test files
        (tmp_path / "specific.py").write_text("# specific")
        (tmp_path / "a.py").write_text("# a")
        (tmp_path / "b.py").write_text("# b")
        patterns = [str(tmp_path / "specific.py"), "*.py"]

        result = expand_glob_patterns(patterns, base_dir=tmp_path)

        assert len(result) >= 2  # At least specific.py + others
        result_names = {Path(p).name for p in result}
        assert "specific.py" in result_names
        assert "a.py" in result_names

    def test_expand_no_matches(self, tmp_path):
        """
        Given: A glob pattern that matches no files
        When: expand_glob_patterns is called
        Then: Returns empty list
        """
        patterns = ["*.nonexistent"]

        result = expand_glob_patterns(patterns, base_dir=tmp_path)

        assert result == []


# ============================================================================
# Test Class 3: Exclusion Patterns
# ============================================================================


class TestExclusionPatterns:
    """Tests for applying exclusion patterns to filter out unwanted files."""

    def test_exclude_single_pattern(self, tmp_path):
        """
        Given: A list of files and a single exclusion pattern
        When: apply_exclusions is called
        Then: Files matching the pattern are removed
        """
        files = [
            str(tmp_path / "keep.py"),
            str(tmp_path / "test_remove.py"),
            str(tmp_path / "also_keep.py"),
        ]
        exclusions = ["test_*.py"]

        result = apply_exclusions(files, exclusions)

        assert len(result) == 2
        result_names = {Path(p).name for p in result}
        assert result_names == {"keep.py", "also_keep.py"}

    def test_exclude_multiple_patterns(self, tmp_path):
        """
        Given: A list of files and multiple exclusion patterns
        When: apply_exclusions is called
        Then: Files matching any pattern are removed
        """
        files = [
            str(tmp_path / "keep.py"),
            str(tmp_path / "test_remove.py"),
            str(tmp_path / "temp_file.py"),
            str(tmp_path / "also_keep.py"),
        ]
        exclusions = ["test_*.py", "temp_*.py"]

        result = apply_exclusions(files, exclusions)

        assert len(result) == 2
        result_names = {Path(p).name for p in result}
        assert result_names == {"keep.py", "also_keep.py"}

    def test_exclude_none(self, tmp_path):
        """
        Given: A list of files and no exclusion patterns
        When: apply_exclusions is called
        Then: All files remain in the result
        """
        files = [
            str(tmp_path / "a.py"),
            str(tmp_path / "b.py"),
            str(tmp_path / "c.py"),
        ]
        exclusions = []

        result = apply_exclusions(files, exclusions)

        assert len(result) == 3
        assert set(result) == set(files)

    def test_exclude_all(self, tmp_path):
        """
        Given: A list of files and a pattern that matches everything
        When: apply_exclusions is called
        Then: Empty list is returned
        """
        files = [
            str(tmp_path / "a.py"),
            str(tmp_path / "b.py"),
            str(tmp_path / "c.py"),
        ]
        exclusions = ["*.py"]

        result = apply_exclusions(files, exclusions)

        assert result == []


# ============================================================================
# Test Class 4: Source Resolution (Integration)
# ============================================================================


class TestSourceResolution:
    """Tests for resolving final source list from CLI + config + defaults."""

    def test_cli_sources_override_config(self, tmp_path):
        """
        Given: Both CLI sources and config sources are specified
        When: resolve_sources is called
        Then: CLI sources take priority, config is ignored
        """
        cli_sources = "cli.py"
        config_sources = ["config.py"]
        base_dir = tmp_path

        result = resolve_sources(
            cli_sources=cli_sources,
            config_sources=config_sources,
            base_dir=base_dir,
        )

        assert "cli.py" in [Path(p).name for p in result]
        assert "config.py" not in [Path(p).name for p in result]

    def test_add_sources_merges_with_config(self, tmp_path):
        """
        Given: Both add_sources and config sources are specified
        When: resolve_sources is called
        Then: Both sets of sources are included (merged)
        """
        add_sources = "added.py"
        config_sources = ["config.py"]
        base_dir = tmp_path

        result = resolve_sources(
            add_sources=add_sources,
            config_sources=config_sources,
            base_dir=base_dir,
        )

        result_names = {Path(p).name for p in result}
        assert "added.py" in result_names
        assert "config.py" in result_names

    def test_config_defaults_used(self, tmp_path):
        """
        Given: No CLI sources specified, only config sources
        When: resolve_sources is called
        Then: Config sources are used
        """
        config_sources = ["config.py"]
        base_dir = tmp_path

        result = resolve_sources(
            cli_sources=None,
            config_sources=config_sources,
            base_dir=base_dir,
        )

        assert "config.py" in [Path(p).name for p in result]

    def test_built_in_defaults(self, tmp_path):
        """
        Given: No CLI sources and no config sources
        When: resolve_sources is called
        Then: Built-in defaults are used (*.py, *.md, etc.)
        """
        base_dir = tmp_path
        (tmp_path / "test.py").write_text("# test")
        (tmp_path / "readme.md").write_text("# readme")

        result = resolve_sources(
            cli_sources=None,
            config_sources=None,
            base_dir=base_dir,
        )

        result_names = {Path(p).name for p in result}
        # Should include at least .py and .md files from built-in defaults
        assert any(name.endswith(".py") for name in result_names)

    def test_validate_missing_files(self, tmp_path, caplog):
        """
        Given: A list of source paths including non-existent files
        When: validate_sources is called
        Then: Warnings are logged for missing files, existing files returned
        """
        existing = tmp_path / "exists.py"
        existing.write_text("# exists")
        sources = [
            str(existing),
            str(tmp_path / "missing.py"),
            str(tmp_path / "also_missing.py"),
        ]

        result = validate_sources(sources)

        # Should return only existing files
        assert len(result) == 1
        assert Path(result[0]) == existing

        # Should log warnings about missing files
        assert "missing.py" in caplog.text
        assert "also_missing.py" in caplog.text
