"""Pytest configuration and fixtures."""

from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_pyproject_content() -> str:
    """Sample pyproject.toml content for testing."""
    return """
[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "requests>=2.0.0",
    "pydantic[email]>=1.8.0",
    "click",
    "invalid package with spaces"
]

[project.optional-dependencies]
dev = ["pytest>=7.0.0", "ruff"]
"""


@pytest.fixture
def sample_pyproject_file(temp_dir: Path, sample_pyproject_content: str) -> Path:
    """Create a sample pyproject.toml file for testing."""
    pyproject_path = temp_dir / "pyproject.toml"
    pyproject_path.write_text(sample_pyproject_content)
    return temp_dir


@pytest.fixture
def mock_services(mocker):
    """Provide mocked services for testing MCP tools."""
    services = {
        "parser": mocker.AsyncMock(),
        "cache_manager": mocker.AsyncMock(),
        "version_resolver": mocker.AsyncMock(),
        "context_fetcher": mocker.AsyncMock(),
    }

    # Patch the global services in main module
    mocker.patch("autodoc_mcp.main.parser", services["parser"])
    mocker.patch("autodoc_mcp.main.cache_manager", services["cache_manager"])
    mocker.patch("autodoc_mcp.main.version_resolver", services["version_resolver"])
    mocker.patch("autodoc_mcp.main.context_fetcher", services["context_fetcher"])

    return services
