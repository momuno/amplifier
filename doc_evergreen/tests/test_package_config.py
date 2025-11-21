"""Test package configuration (pyproject.toml)."""

import tomllib
from pathlib import Path

import pytest


class TestPackageConfiguration:
    """Tests for pyproject.toml package configuration."""

    @pytest.fixture
    def doc_evergreen_root(self) -> Path:
        """Provide path to doc_evergreen package root."""
        # From tests/ directory, go up one level to doc_evergreen/
        return Path(__file__).parent.parent

    @pytest.fixture
    def pyproject_path(self, doc_evergreen_root: Path) -> Path:
        """Provide path to pyproject.toml."""
        return doc_evergreen_root / "pyproject.toml"

    @pytest.fixture
    def pyproject_config(self, pyproject_path: Path) -> dict:
        """
        Given: A pyproject.toml file exists
        When: We load it as TOML
        Then: Return the parsed configuration
        """
        if not pyproject_path.exists():
            pytest.fail(f"pyproject.toml not found at {pyproject_path}")

        with open(pyproject_path, "rb") as f:
            return tomllib.load(f)

    def test_pyproject_exists(self, pyproject_path: Path):
        """
        Given: The doc_evergreen package
        When: We check for pyproject.toml at package root
        Then: The file exists
        """
        assert pyproject_path.exists(), f"pyproject.toml must exist at {pyproject_path}"

    def test_package_name(self, pyproject_config: dict):
        """
        Given: A valid pyproject.toml
        When: We check the project name
        Then: It is "doc-evergreen"
        """
        assert "project" in pyproject_config, "pyproject.toml must have [project] section"
        assert pyproject_config["project"]["name"] == "doc-evergreen", "Package name must be 'doc-evergreen'"

    def test_package_version(self, pyproject_config: dict):
        """
        Given: A valid pyproject.toml
        When: We check the version field
        Then: It exists and matches v0.4.0
        """
        assert "project" in pyproject_config
        assert "version" in pyproject_config["project"], "Package must have version field"
        assert pyproject_config["project"]["version"] == "0.4.0", "Version must be '0.4.0' for this release"

    def test_python_version_requirement(self, pyproject_config: dict):
        """
        Given: A valid pyproject.toml
        When: We check the Python version requirement
        Then: It requires Python >= 3.11
        """
        assert "project" in pyproject_config
        assert "requires-python" in pyproject_config["project"], "Package must specify requires-python"

        requires_python = pyproject_config["project"]["requires-python"]
        # Accept variations: ">=3.11", ">=3.11.0", etc.
        assert requires_python.startswith(">=3.11"), f"Must require Python >= 3.11, got: {requires_python}"

    def test_cli_entry_point(self, pyproject_config: dict):
        """
        Given: A valid pyproject.toml
        When: We check the CLI entry points
        Then: "doc-evergreen" command points to "doc_evergreen.cli:cli"
        """
        assert "project" in pyproject_config
        assert "scripts" in pyproject_config["project"], "Package must define CLI entry points in [project.scripts]"

        scripts = pyproject_config["project"]["scripts"]
        assert "doc-evergreen" in scripts, "Must have 'doc-evergreen' CLI command in scripts"
        assert scripts["doc-evergreen"] == "doc_evergreen.cli:cli", (
            "doc-evergreen command must point to doc_evergreen.cli:cli"
        )

    def test_has_dependencies(self, pyproject_config: dict):
        """
        Given: A valid pyproject.toml
        When: We check for dependencies
        Then: A dependencies list exists
        """
        assert "project" in pyproject_config
        assert "dependencies" in pyproject_config["project"], "Package must declare dependencies"
        assert isinstance(pyproject_config["project"]["dependencies"], list), "dependencies must be a list"

    def test_build_system(self, pyproject_config: dict):
        """
        Given: A valid pyproject.toml
        When: We check the build system
        Then: It uses hatchling as the build backend
        """
        assert "build-system" in pyproject_config, "pyproject.toml must have [build-system] section"

        build_system = pyproject_config["build-system"]
        assert "requires" in build_system, "[build-system] must have 'requires' list"
        assert "build-backend" in build_system, "[build-system] must have 'build-backend'"

        # Check hatchling is the build backend
        assert build_system["build-backend"] == "hatchling.build", "Build backend must be 'hatchling.build'"

        # Check hatchling is in the requirements
        requires = build_system["requires"]
        assert any(req.startswith("hatchling") for req in requires), "hatchling must be in build-system.requires"
