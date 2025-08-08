"""Unit tests for dependency parser."""

import pytest

from autodocs_mcp.core.dependency_parser import PyProjectParser
from autodocs_mcp.exceptions import ProjectParsingError


class TestPyProjectParser:
    @pytest.fixture
    def parser(self):
        return PyProjectParser()

    async def test_parse_valid_project(self, parser, sample_pyproject_file):
        """Test parsing a valid pyproject.toml file."""
        result = await parser.parse_project(sample_pyproject_file)

        assert result.project_name == "test-project"
        # Expected: 3 valid main deps + 2 dev deps + malformed one fails = 5 successful
        assert result.successful_deps == 5
        assert len(result.dependencies) == 5
        assert len(result.failed_deps) == 1  # One malformed dependency
        assert result.partial_success is True
        assert len(result.warnings) == 1

        # Check main dependencies
        main_deps = [d for d in result.dependencies if d.source == "project"]
        assert len(main_deps) == 3  # Excluding the malformed one

        # Test specific dependency parsing
        requests_dep = next((d for d in main_deps if d.name == "requests"), None)
        assert requests_dep is not None
        assert requests_dep.version_constraint == ">=2.0.0"

        pydantic_dep = next((d for d in main_deps if d.name == "pydantic"), None)
        assert pydantic_dep is not None
        assert pydantic_dep.extras == ["email"]
        assert pydantic_dep.version_constraint == ">=1.8.0"

        click_dep = next((d for d in main_deps if d.name == "click"), None)
        assert click_dep is not None
        assert click_dep.version_constraint is None

        # Check dev dependencies
        dev_deps = [d for d in result.dependencies if d.source.startswith("optional-")]
        assert len(dev_deps) == 2

    async def test_parse_missing_file(self, parser, temp_dir):
        """Test parsing when pyproject.toml is missing."""
        with pytest.raises(ProjectParsingError, match="not found"):
            await parser.parse_project(temp_dir)

    async def test_parse_invalid_toml(self, parser, temp_dir):
        """Test parsing invalid TOML syntax."""
        invalid_path = temp_dir / "pyproject.toml"
        invalid_path.write_text("invalid toml [content")

        with pytest.raises(ProjectParsingError, match="Invalid TOML"):
            await parser.parse_project(temp_dir)

    async def test_parse_no_project_section(self, parser, temp_dir):
        """Test parsing TOML without [project] section."""
        no_project_path = temp_dir / "pyproject.toml"
        no_project_path.write_text("""
[build-system]
requires = ["setuptools", "wheel"]
""")

        result = await parser.parse_project(temp_dir)
        assert result.project_name is None
        assert len(result.dependencies) == 0
        assert len(result.warnings) >= 1
        assert "No [project] section found" in result.warnings[0]

    def test_validate_file_valid(self, parser, sample_pyproject_file):
        """Test file validation with valid file."""
        pyproject_path = sample_pyproject_file / "pyproject.toml"
        assert parser.validate_file(pyproject_path) is True

    def test_validate_file_missing(self, parser, temp_dir):
        """Test file validation with missing file."""
        missing_path = temp_dir / "nonexistent.toml"
        assert parser.validate_file(missing_path) is False

    def test_validate_file_no_project_section(self, parser, temp_dir):
        """Test file validation without [project] section."""
        no_project_path = temp_dir / "pyproject.toml"
        no_project_path.write_text("[build-system]\nrequires = ['setuptools']")
        assert parser.validate_file(no_project_path) is False

    def test_parse_dependency_string_simple(self, parser):
        """Test parsing simple dependency string."""
        spec = parser._parse_dependency_string("requests", "project")
        assert spec.name == "requests"
        assert spec.version_constraint is None
        assert spec.extras == []
        assert spec.source == "project"

    def test_parse_dependency_string_with_version(self, parser):
        """Test parsing dependency string with version constraint."""
        spec = parser._parse_dependency_string("requests>=2.0.0", "project")
        assert spec.name == "requests"
        assert spec.version_constraint == ">=2.0.0"
        assert spec.extras == []

    def test_parse_dependency_string_with_extras(self, parser):
        """Test parsing dependency string with extras."""
        spec = parser._parse_dependency_string("pydantic[email,validation]", "project")
        assert spec.name == "pydantic"
        assert spec.version_constraint is None
        assert spec.extras == ["email", "validation"]

    def test_parse_dependency_string_complex(self, parser):
        """Test parsing complex dependency string."""
        spec = parser._parse_dependency_string("fastapi[all]>=0.68.0", "project")
        assert spec.name == "fastapi"
        assert spec.version_constraint == ">=0.68.0"
        assert spec.extras == ["all"]

    def test_parse_dependency_string_invalid(self, parser):
        """Test parsing invalid dependency strings."""
        with pytest.raises(ValueError):
            parser._parse_dependency_string("", "project")

        with pytest.raises(ValueError):
            parser._parse_dependency_string("invalid name with spaces", "project")

        with pytest.raises(ValueError):
            parser._parse_dependency_string("package[unclosed", "project")
