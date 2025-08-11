"""Tests for dependency resolver functionality."""

import pytest

from autodoc_mcp.core.dependency_resolver import (
    CORE_FRAMEWORKS,
    LOW_PRIORITY_DEPS,
    WELL_DOCUMENTED,
    DependencyResolver,
    DependencySpec,
    PackageMetadata,
)
from autodoc_mcp.core.network_client import BasicNetworkClient


class TestDependencySpec:
    """Test dependency specification model."""

    def test_from_requirement(self):
        """Test creating DependencySpec from packaging.requirements.Requirement."""
        from packaging.requirements import Requirement

        req = Requirement("requests>=2.28.0")
        spec = DependencySpec.from_requirement(req)

        assert spec.name == "requests"
        assert spec.version_constraint == ">=2.28.0"
        assert spec.extras == []
        assert not spec.is_optional
        assert spec.environment_markers == ""

    def test_from_requirement_with_extras(self):
        """Test requirement with extras."""
        from packaging.requirements import Requirement

        req = Requirement("fastapi[all]>=0.100.0")
        spec = DependencySpec.from_requirement(req)

        assert spec.name == "fastapi"
        assert "all" in spec.extras
        assert ">=0.100.0" in spec.version_constraint


class TestPackageMetadata:
    """Test package metadata model."""

    def test_package_metadata_creation(self):
        """Test creating package metadata."""
        metadata = PackageMetadata(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            description="A test package for testing",
        )

        assert metadata.name == "test-package"
        assert metadata.version == "1.0.0"
        assert metadata.runtime_requires == []
        assert metadata.keywords == []


class TestDependencyResolver:
    """Test dependency resolver functionality."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mocker):
        """Set up test fixtures."""
        # Mock network client
        self.mock_client = mocker.AsyncMock(spec=BasicNetworkClient)
        self.resolver = DependencyResolver(self.mock_client)

    async def test_resolve_context_dependencies_no_deps(self, mocker):
        """Test resolving dependencies when package has none."""
        # Mock response for package with no dependencies
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {
            "info": {
                "name": "simple-package",
                "version": "1.0.0",
                "summary": "Simple package",
                "description": "No dependencies",
                "requires_dist": None,
            }
        }
        self.mock_client.get_with_retry.return_value = mock_response

        deps = await self.resolver.resolve_context_dependencies(
            "simple-package", "1.0.0"
        )

        assert deps == []

    async def test_resolve_context_dependencies_with_deps(self, mocker):
        """Test resolving dependencies with actual dependencies."""
        # Mock response for fastapi-like package
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {
            "info": {
                "name": "fastapi",
                "version": "0.104.1",
                "summary": "FastAPI framework",
                "description": "Modern web framework",
                "requires_dist": [
                    "pydantic>=2.0.0",
                    "starlette>=0.27.0",
                    "typing-extensions>=4.0.0",
                ],
            }
        }
        self.mock_client.get_with_retry.return_value = mock_response

        deps = await self.resolver.resolve_context_dependencies(
            "fastapi", "0.104.1", max_dependencies=3
        )

        # Should prioritize pydantic (core framework) and starlette
        assert len(deps) > 0
        assert "pydantic" in deps
        assert "starlette" in deps
        # typing-extensions is low priority, might be excluded

    async def test_resolve_context_dependencies_with_token_limit(self, mocker):
        """Test token-aware dependency selection."""
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {
            "info": {
                "name": "test-package",
                "version": "1.0.0",
                "summary": "Test",
                "description": "Test",
                "requires_dist": [
                    "requests>=2.28.0",
                    "pydantic>=2.0.0",
                    "click>=8.0.0",
                ],
            }
        }
        self.mock_client.get_with_retry.return_value = mock_response

        # Very low token limit - should limit dependencies
        deps = await self.resolver.resolve_context_dependencies(
            "test-package", "1.0.0", max_tokens=1000
        )

        # Should only include highest priority dep due to token limit
        assert len(deps) <= 2  # Limited by token budget

    def test_calculate_dependency_relevance_core_framework(self):
        """Test relevance scoring for core frameworks."""
        spec = DependencySpec(name="fastapi", version_constraint=">=0.100.0")

        score = self.resolver._calculate_dependency_relevance(spec, "myapp")

        # Core frameworks get 10.0 base score
        assert score >= 10.0

    def test_calculate_dependency_relevance_relationship_boost(self):
        """Test package-specific relationship boosts."""
        spec = DependencySpec(name="pydantic", version_constraint=">=2.0.0")

        # Should get relationship boost when used with fastapi
        score = self.resolver._calculate_dependency_relevance(spec, "fastapi")

        # Should get core framework (10.0) + relationship boost (8.0)
        assert score >= 18.0

    def test_calculate_dependency_relevance_low_priority(self):
        """Test penalty for low-priority dependencies."""
        spec = DependencySpec(name="setuptools", version_constraint=">=60.0.0")

        score = self.resolver._calculate_dependency_relevance(spec, "myapp")

        # Low priority deps get negative score, but minimum is 0
        assert score == 0.0

    def test_calculate_dependency_relevance_well_documented(self):
        """Test boost for well-documented packages."""
        spec = DependencySpec(name="requests", version_constraint=">=2.28.0")

        score = self.resolver._calculate_dependency_relevance(spec, "myapp")

        # requests is both core framework (10.0) and well documented (+2.0)
        assert score >= 12.0

    async def test_estimate_dependency_tokens(self):
        """Test token estimation for different types of packages."""
        # Core framework - should have high token estimate
        core_tokens = await self.resolver._estimate_dependency_tokens("fastapi")
        assert core_tokens == 2500

        # Package in CORE_FRAMEWORKS gets 2500 (first match wins)
        requests_tokens = await self.resolver._estimate_dependency_tokens("requests")
        assert requests_tokens == 2500

        # Package in CORE_FRAMEWORKS gets 2500 (first match wins)
        click_tokens = await self.resolver._estimate_dependency_tokens("click")
        assert click_tokens == 2500

        # Unknown package - default estimate
        default_tokens = await self.resolver._estimate_dependency_tokens("unknown-pkg")
        assert default_tokens == 1000

    async def test_graceful_degradation_on_network_error(self):
        """Test graceful handling of network errors."""
        # Mock network error
        self.mock_client.get_with_retry.side_effect = Exception("Network error")

        deps = await self.resolver.resolve_context_dependencies("test-package", "1.0.0")

        # Should return empty list gracefully
        assert deps == []

    async def test_get_dependency_metadata_caching(self, mocker):
        """Test that metadata is cached properly."""
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {
            "info": {
                "name": "cached-package",
                "version": "1.0.0",
                "summary": "Cached",
                "description": "Test caching",
            }
        }
        self.mock_client.get_with_retry.return_value = mock_response

        # First call should hit network
        metadata1 = await self.resolver._get_package_metadata("cached-package", "1.0.0")
        assert metadata1.name == "cached-package"

        # Second call should use cache
        metadata2 = await self.resolver._get_package_metadata("cached-package", "1.0.0")
        assert metadata2.name == "cached-package"

        # Should only have called network once
        assert self.mock_client.get_with_retry.call_count == 1


class TestDependencyConstants:
    """Test dependency categorization constants."""

    def test_core_frameworks_contains_expected(self):
        """Test that core frameworks includes expected packages."""
        assert "fastapi" in CORE_FRAMEWORKS
        assert "django" in CORE_FRAMEWORKS
        assert "flask" in CORE_FRAMEWORKS
        assert "requests" in CORE_FRAMEWORKS
        assert "pydantic" in CORE_FRAMEWORKS

    def test_well_documented_contains_expected(self):
        """Test that well documented includes expected packages."""
        assert "requests" in WELL_DOCUMENTED
        assert "fastapi" in WELL_DOCUMENTED
        assert "pydantic" in WELL_DOCUMENTED
        assert "click" in WELL_DOCUMENTED

    def test_low_priority_contains_build_tools(self):
        """Test that low priority includes build tools."""
        assert "setuptools" in LOW_PRIORITY_DEPS
        assert "wheel" in LOW_PRIORITY_DEPS
        assert "pip" in LOW_PRIORITY_DEPS
        assert "hatchling" in LOW_PRIORITY_DEPS
