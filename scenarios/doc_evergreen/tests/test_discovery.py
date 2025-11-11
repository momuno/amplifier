"""
Tests for file discovery and gathering.
"""

import tempfile
from pathlib import Path

import pytest

from doc_evergreen.core.discovery import (
    auto_discover_files,
    estimate_file_size,
    find_files,
    format_file_size,
    gather_files,
    load_gitignore,
    read_file,
    should_ignore,
    validate_utf8,
)


@pytest.fixture
def temp_repo():
    """Create a temporary repository with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create directory structure
        (repo / "src").mkdir()
        (repo / "src" / "core").mkdir()
        (repo / "tests").mkdir()
        (repo / "docs").mkdir()

        # Create Python files
        (repo / "src" / "__init__.py").write_text("# Init file\n")
        (repo / "src" / "main.py").write_text("def main():\n    pass\n")
        (repo / "src" / "core" / "utils.py").write_text("def util():\n    pass\n")

        # Create test files
        (repo / "tests" / "test_main.py").write_text("def test_main():\n    assert True\n")

        # Create docs
        (repo / "README.md").write_text("# Test Project\n")
        (repo / "docs" / "guide.md").write_text("# User Guide\n")

        # Create config file
        (repo / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        # Create .gitignore
        (repo / ".gitignore").write_text("__pycache__/\n*.pyc\n.venv/\n")

        yield repo


def test_find_files_single_pattern(temp_repo):
    """Test finding files with single glob pattern."""
    files = find_files(["*.md"], temp_repo)

    # Should find README.md
    assert len(files) == 1
    assert files[0].name == "README.md"


def test_find_files_recursive_pattern(temp_repo):
    """Test finding files with recursive pattern."""
    files = find_files(["src/**/*.py"], temp_repo)

    # Should find all Python files in src/
    file_names = [f.name for f in files]
    assert "__init__.py" in file_names
    assert "main.py" in file_names
    assert "utils.py" in file_names


def test_find_files_multiple_patterns(temp_repo):
    """Test finding files with multiple patterns."""
    files = find_files(["*.md", "*.toml"], temp_repo)

    file_names = [f.name for f in files]
    assert "README.md" in file_names
    assert "pyproject.toml" in file_names


def test_find_files_no_matches(temp_repo):
    """Test finding files with pattern that doesn't match."""
    files = find_files(["*.nonexistent"], temp_repo)
    assert len(files) == 0


def test_load_gitignore_exists(temp_repo):
    """Test loading .gitignore file."""
    gitignore = load_gitignore(temp_repo)

    assert gitignore is not None
    # Should have loaded patterns
    assert gitignore.match_file("__pycache__/file.py")
    assert gitignore.match_file("test.pyc")


def test_load_gitignore_not_exists():
    """Test loading .gitignore when it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        gitignore = load_gitignore(repo)
        assert gitignore is None


def test_should_ignore_with_gitignore(temp_repo):
    """Test checking if file should be ignored."""
    gitignore = load_gitignore(temp_repo)

    # Create a .pyc file path
    pyc_file = temp_repo / "test.pyc"

    assert should_ignore(pyc_file, temp_repo, gitignore) is True


def test_should_ignore_without_gitignore(temp_repo):
    """Test checking ignore when gitignore is None."""
    pyc_file = temp_repo / "test.pyc"

    assert should_ignore(pyc_file, temp_repo, None) is False


def test_should_ignore_not_in_gitignore(temp_repo):
    """Test file not in gitignore patterns."""
    gitignore = load_gitignore(temp_repo)
    py_file = temp_repo / "src" / "main.py"

    assert should_ignore(py_file, temp_repo, gitignore) is False


def test_validate_utf8_valid(temp_repo):
    """Test validating valid UTF-8 file."""
    py_file = temp_repo / "src" / "main.py"
    assert validate_utf8(py_file) is True


def test_validate_utf8_nonexistent():
    """Test validating non-existent file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_file = Path(tmpdir) / "nonexistent.txt"
        assert validate_utf8(fake_file) is False


def test_validate_utf8_binary():
    """Test validating binary file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        binary_file = Path(tmpdir) / "binary.bin"
        # Write some binary data
        binary_file.write_bytes(b"\x80\x81\x82\x83")

        assert validate_utf8(binary_file) is False


def test_read_file_success(temp_repo):
    """Test reading file successfully."""
    content = read_file(temp_repo / "README.md")
    assert content == "# Test Project\n"


def test_read_file_not_found():
    """Test reading non-existent file raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_file = Path(tmpdir) / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            read_file(fake_file)


def test_gather_files_with_gitignore(temp_repo):
    """Test gathering files respecting gitignore."""
    # Create a .pyc file that should be ignored
    (temp_repo / "test.pyc").write_text("compiled")

    files = gather_files(["**/*.py", "*.pyc"], temp_repo, respect_gitignore=True)

    # Should include .py files but not .pyc
    assert "src/main.py" in files or "src\\main.py" in files  # Handle Windows paths
    assert "test.pyc" not in files


def test_gather_files_without_gitignore(temp_repo):
    """Test gathering files without respecting gitignore."""
    # Create a .pyc file
    (temp_repo / "test.pyc").write_text("compiled")

    files = gather_files(["**/*.py", "*.pyc"], temp_repo, respect_gitignore=False)

    # Should include both .py and .pyc files
    assert len(files) > 0
    # At minimum should have Python files
    python_files = [k for k in files.keys() if k.endswith(".py")]
    assert len(python_files) > 0


def test_gather_files_returns_contents(temp_repo):
    """Test that gathered files include contents."""
    files = gather_files(["README.md"], temp_repo)

    assert "README.md" in files
    assert files["README.md"] == "# Test Project\n"


def test_auto_discover_files_api_keyword():
    """Test auto-discovery with tree traversal."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create some test files
        (repo / "README.md").write_text("readme")
        src_dir = repo / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("code")

        files = auto_discover_files("API reference for user module", repo, max_depth=2)

        # Should discover files using tree traversal
        assert isinstance(files, list)
        assert any("README.md" in f for f in files)
        assert any("main.py" in f for f in files)


def test_auto_discover_files_cli_keyword():
    """Test auto-discovery finds CLI-related files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create CLI-related files
        (repo / "cli.py").write_text("cli code")
        src_dir = repo / "src"
        src_dir.mkdir()
        (src_dir / "commands.py").write_text("commands")

        files = auto_discover_files("CLI usage guide", repo, max_depth=2)

        assert isinstance(files, list)
        assert len(files) > 0


def test_auto_discover_files_readme():
    """Test auto-discovery for README."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create README and source files
        (repo / "README.md").write_text("readme")
        src_dir = repo / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("code")

        files = auto_discover_files("Main project README", repo, max_depth=2)

        # Should discover files with common extensions
        assert any("README.md" in f for f in files)


def test_auto_discover_files_no_keywords():
    """Test auto-discovery with tree traversal."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create various files
        (repo / "README.md").write_text("readme")
        (repo / "pyproject.toml").write_text("config")
        src_dir = repo / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("code")

        files = auto_discover_files("Some random documentation", repo, max_depth=2)

        # Should discover files using tree traversal
        assert isinstance(files, list)
        assert len(files) > 0


def test_auto_discover_files_no_duplicates():
    """Test that auto-discovery doesn't return duplicates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create test files
        (repo / "README.md").write_text("readme")
        src_dir = repo / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("code")

        files = auto_discover_files("Python API and CLI reference", repo, max_depth=2)

        # Should not have duplicates
        assert len(files) == len(set(files))


def test_estimate_file_size(temp_repo):
    """Test estimating total file size."""
    size = estimate_file_size(["**/*.py"], temp_repo)

    # Should be greater than 0
    assert size > 0


def test_estimate_file_size_empty_pattern(temp_repo):
    """Test estimating size with pattern that matches nothing."""
    size = estimate_file_size(["*.nonexistent"], temp_repo)
    assert size == 0


def test_format_file_size_bytes():
    """Test formatting bytes."""
    assert format_file_size(500) == "500 B"


def test_format_file_size_kilobytes():
    """Test formatting kilobytes."""
    assert format_file_size(1536) == "1.5 KB"


def test_format_file_size_megabytes():
    """Test formatting megabytes."""
    assert format_file_size(2 * 1024 * 1024) == "2.0 MB"
