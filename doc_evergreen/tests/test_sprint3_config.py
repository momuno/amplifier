"""
Sprint 3 Deliverable 4: Configuration File Support Tests

RED PHASE - These tests WILL FAIL until config.py is implemented.

Tests for .doc-evergreen.yaml configuration file loading and usage.
"""

from pathlib import Path

from doc_evergreen.config import Config
from doc_evergreen.config import FileConfig
from doc_evergreen.config import LLMConfig
from doc_evergreen.config import default_config
from doc_evergreen.config import find_project_root
from doc_evergreen.config import load_config


class TestConfigLoading:
    """Tests for loading configuration from YAML files"""

    def test_load_config_from_file(self, tmp_path: Path) -> None:
        """
        Given: A .doc-evergreen.yaml file exists
        When: load_config is called
        Then: Should parse YAML correctly and return Config object with all fields
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
template_dir: ./custom-templates

files:
  README.md:
    template: readme
    sources:
      - README.md
      - pyproject.toml

  docs/API.md:
    template: api-reference
    sources:
      - src/api/
      - docs/api-spec.yaml

default_sources:
  - README.md
  - pyproject.toml

llm:
  provider: claude
  model: claude-3-5-sonnet-20241022
"""
        )

        config = load_config(tmp_path)

        assert config.template_dir == "./custom-templates"
        assert "README.md" in config.files
        assert config.files["README.md"].template == "readme"
        assert config.files["README.md"].sources == ["README.md", "pyproject.toml"]
        assert "docs/API.md" in config.files
        assert config.files["docs/API.md"].template == "api-reference"
        assert config.default_sources == ["README.md", "pyproject.toml"]
        assert config.llm.provider == "claude"
        assert config.llm.model == "claude-3-5-sonnet-20241022"

    def test_load_config_missing_file_returns_defaults(self, tmp_path: Path) -> None:
        """
        Given: No .doc-evergreen.yaml file exists
        When: load_config is called
        Then: Should return default config without raising error
        """
        config = load_config(tmp_path)

        assert config.template_dir is None
        assert config.files == {}
        assert config.default_sources == []
        assert config.llm.provider == "claude"
        assert config.llm.model == "claude-3-5-sonnet-20241022"

    def test_load_config_malformed_yaml_uses_defaults(self, tmp_path: Path) -> None:
        """
        Given: A malformed YAML file exists
        When: load_config is called
        Then: Should log warning and return default config (don't crash)
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
template_dir: ./templates
files:
  README.md:
    template: readme
    sources: [README.md
      - missing closing bracket
"""
        )

        config = load_config(tmp_path)

        # Should return defaults when YAML is malformed
        assert isinstance(config, Config)
        assert config.files == {}

    def test_load_config_partial_settings(self, tmp_path: Path) -> None:
        """
        Given: Config with only some fields defined
        When: load_config is called
        Then: Should merge with defaults, missing fields use default values
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
files:
  README.md:
    template: readme
"""
        )

        config = load_config(tmp_path)

        # Specified fields
        assert "README.md" in config.files
        assert config.files["README.md"].template == "readme"

        # Unspecified fields should use defaults
        assert config.template_dir is None
        assert config.default_sources == []
        assert config.llm.provider == "claude"
        assert config.llm.model == "claude-3-5-sonnet-20241022"


class TestConfigDefaults:
    """Tests for default configuration values"""

    def test_default_config_has_sensible_defaults(self) -> None:
        """
        Given: No configuration specified
        When: default_config is called
        Then: Should return Config with sensible default values
        """
        config = default_config()

        assert config.template_dir is None
        assert config.files == {}
        assert config.default_sources == []
        assert config.llm.provider == "claude"
        assert config.llm.model == "claude-3-5-sonnet-20241022"

    def test_llm_config_defaults(self) -> None:
        """
        Given: No LLM configuration specified
        When: LLMConfig is created
        Then: Should use default provider and model
        """
        llm_config = LLMConfig()

        assert llm_config.provider == "claude"
        assert llm_config.model == "claude-3-5-sonnet-20241022"

    def test_file_config_defaults(self) -> None:
        """
        Given: No file-specific configuration
        When: FileConfig is created
        Then: Should have None for optional fields
        """
        file_config = FileConfig()

        assert file_config.template is None
        assert file_config.sources is None


class TestConfigFileSettings:
    """Tests for per-file configuration"""

    def test_config_file_specific_settings(self, tmp_path: Path) -> None:
        """
        Given: Config with file-specific settings
        When: Retrieving settings for specific file
        Then: Should return template and sources for that file
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
files:
  README.md:
    template: readme
    sources:
      - README.md
      - pyproject.toml

  docs/GUIDE.md:
    template: guide
    sources:
      - docs/
"""
        )

        config = load_config(tmp_path)

        # README.md settings
        readme_config = config.files.get("README.md")
        assert readme_config is not None
        assert readme_config.template == "readme"
        assert readme_config.sources == ["README.md", "pyproject.toml"]

        # docs/GUIDE.md settings
        guide_config = config.files.get("docs/GUIDE.md")
        assert guide_config is not None
        assert guide_config.template == "guide"
        assert guide_config.sources == ["docs/"]

    def test_config_default_sources(self, tmp_path: Path) -> None:
        """
        Given: Config with default_sources defined
        When: File not in files section
        Then: Should use default_sources as fallback
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
default_sources:
  - README.md
  - pyproject.toml
  - src/

files:
  docs/API.md:
    template: api
    sources:
      - src/api/
"""
        )

        config = load_config(tmp_path)

        # Default sources available
        assert config.default_sources == ["README.md", "pyproject.toml", "src/"]

        # File with specific sources uses those
        api_config = config.files.get("docs/API.md")
        assert api_config is not None
        assert api_config.sources == ["src/api/"]

    def test_config_sources_as_glob_patterns(self, tmp_path: Path) -> None:
        """
        Given: Sources with glob patterns like src/**/*.py
        When: Config is loaded
        Then: Should store patterns as-is (expansion happens later)
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
files:
  docs/CODE.md:
    template: code
    sources:
      - "src/**/*.py"
      - "tests/**/*.py"
      - "*.md"
"""
        )

        config = load_config(tmp_path)

        code_config = config.files.get("docs/CODE.md")
        assert code_config is not None
        assert code_config.sources == ["src/**/*.py", "tests/**/*.py", "*.md"]


class TestConfigTemplateDirectory:
    """Tests for custom template directory configuration"""

    def test_config_template_directory(self, tmp_path: Path) -> None:
        """
        Given: Config with custom template_dir
        When: Config is loaded
        Then: Should use custom directory for template discovery
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
template_dir: ./custom-templates
"""
        )

        config = load_config(tmp_path)

        assert config.template_dir == "./custom-templates"

    def test_config_template_directory_defaults_to_none(self, tmp_path: Path) -> None:
        """
        Given: Config without template_dir specified
        When: Config is loaded
        Then: Should default to None (use built-in templates)
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
files:
  README.md:
    template: readme
"""
        )

        config = load_config(tmp_path)

        assert config.template_dir is None


class TestConfigLLMSettings:
    """Tests for LLM configuration"""

    def test_config_llm_settings(self, tmp_path: Path) -> None:
        """
        Given: Config with llm settings
        When: Config is loaded
        Then: Should parse provider and model correctly
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
llm:
  provider: openai
  model: gpt-4
"""
        )

        config = load_config(tmp_path)

        assert config.llm.provider == "openai"
        assert config.llm.model == "gpt-4"

    def test_config_llm_defaults_when_not_specified(self, tmp_path: Path) -> None:
        """
        Given: Config without llm section
        When: Config is loaded
        Then: Should use default Claude settings
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
files:
  README.md:
    template: readme
"""
        )

        config = load_config(tmp_path)

        assert config.llm.provider == "claude"
        assert config.llm.model == "claude-3-5-sonnet-20241022"


class TestConfigProjectRoot:
    """Tests for finding project root directory"""

    def test_config_finds_project_root(self, tmp_path: Path) -> None:
        """
        Given: .doc-evergreen.yaml in project root
        When: Called from subdirectory
        Then: Should find config by searching up directory tree
        """
        # Create project structure
        project_root = tmp_path / "project"
        project_root.mkdir()
        config_file = project_root / ".doc-evergreen.yaml"
        config_file.write_text("files: {}")

        # Create subdirectory
        subdir = project_root / "docs" / "guides"
        subdir.mkdir(parents=True)

        # Should find project root from subdirectory
        found_root = find_project_root(subdir)
        assert found_root == project_root

    def test_config_finds_git_root_as_fallback(self, tmp_path: Path) -> None:
        """
        Given: No .doc-evergreen.yaml but .git directory exists
        When: find_project_root is called
        Then: Should use .git directory as project root
        """
        # Create project with .git
        project_root = tmp_path / "project"
        project_root.mkdir()
        git_dir = project_root / ".git"
        git_dir.mkdir()

        # Create subdirectory
        subdir = project_root / "src"
        subdir.mkdir()

        # Should find git root from subdirectory
        found_root = find_project_root(subdir)
        assert found_root == project_root

    def test_config_returns_none_when_no_root_found(self, tmp_path: Path) -> None:
        """
        Given: No .doc-evergreen.yaml or .git directory
        When: find_project_root is called
        Then: Should return None
        """
        # Create directory without markers
        test_dir = tmp_path / "no-project"
        test_dir.mkdir()

        found_root = find_project_root(test_dir)
        assert found_root is None

    def test_config_uses_current_dir_when_no_start_specified(self) -> None:
        """
        Given: No start directory specified
        When: find_project_root is called
        Then: Should start search from current working directory
        """
        found_root = find_project_root()
        # Should return Path or None, not raise error
        assert found_root is None or isinstance(found_root, Path)


class TestConfigIntegration:
    """Integration tests for config with other components"""

    def test_config_with_all_settings(self, tmp_path: Path) -> None:
        """
        Given: Complete configuration file with all sections
        When: Config is loaded
        Then: All settings should be parsed correctly
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text(
            """
# Doc-Evergreen Configuration
template_dir: ./doc-templates

files:
  README.md:
    template: readme
    sources:
      - README.md
      - pyproject.toml
      - amplifier/cli.py

  docs/API.md:
    template: api-reference
    sources:
      - amplifier/api/
      - docs/api-spec.yaml

  docs/GUIDE.md:
    template: guide

default_sources:
  - README.md
  - pyproject.toml

llm:
  provider: claude
  model: claude-3-5-sonnet-20241022
"""
        )

        config = load_config(tmp_path)

        # Verify all sections parsed
        assert config.template_dir == "./doc-templates"
        assert len(config.files) == 3
        assert config.default_sources == ["README.md", "pyproject.toml"]
        assert config.llm.provider == "claude"
        assert config.llm.model == "claude-3-5-sonnet-20241022"

        # Verify README.md config
        readme = config.files["README.md"]
        assert readme.template == "readme"
        assert readme.sources is not None
        assert len(readme.sources) == 3

        # Verify docs/API.md config
        api = config.files["docs/API.md"]
        assert api.template == "api-reference"
        assert api.sources is not None
        assert len(api.sources) == 2

        # Verify docs/GUIDE.md config (no sources specified)
        guide = config.files["docs/GUIDE.md"]
        assert guide.template == "guide"
        assert guide.sources is None

    def test_config_empty_file_uses_all_defaults(self, tmp_path: Path) -> None:
        """
        Given: Empty .doc-evergreen.yaml file
        When: Config is loaded
        Then: Should use all default values
        """
        config_file = tmp_path / ".doc-evergreen.yaml"
        config_file.write_text("")

        config = load_config(tmp_path)

        # Should match default_config()
        default = default_config()
        assert config.template_dir == default.template_dir
        assert config.files == default.files
        assert config.default_sources == default.default_sources
        assert config.llm.provider == default.llm.provider
        assert config.llm.model == default.llm.model
