"""Unit tests for context fetcher functionality."""

import asyncio

import pytest

from src.autodoc_mcp.core.context_fetcher import (
    ConcurrentContextFetcher,
    create_context_fetcher,
)
from src.autodoc_mcp.core.context_formatter import (
    DocumentationContext,
    PackageDocumentation,
)
from src.autodoc_mcp.exceptions import NetworkError


@pytest.fixture
def mock_cache_manager(mocker):
    """Create mock cache manager for tests."""
    cache_manager = mocker.AsyncMock()
    return cache_manager


@pytest.fixture
def mock_dependency_resolver(mocker):
    """Create mock dependency resolver for tests."""
    resolver = mocker.AsyncMock()
    return resolver


@pytest.fixture
def mock_formatter(mocker):
    """Create mock context formatter for tests."""
    formatter = mocker.Mock()
    return formatter


@pytest.fixture
def mock_network_client(mocker):
    """Create mock network client for tests."""
    client = mocker.AsyncMock()
    return client


@pytest.fixture
def context_fetcher(
    mock_cache_manager, mock_dependency_resolver, mock_formatter, mock_network_client
):
    """Create ConcurrentContextFetcher instance with all dependencies mocked."""
    return ConcurrentContextFetcher(
        cache_manager=mock_cache_manager,
        dependency_resolver=mock_dependency_resolver,
        formatter=mock_formatter,
        network_client=mock_network_client,
    )


@pytest.fixture
def sample_package_info():
    """Sample package info for testing."""
    return {
        "name": "requests",
        "version": "2.28.0",
        "summary": "Python HTTP for Humans.",
        "description": "Requests is a simple HTTP library for Python.",
        "author": "Kenneth Reitz",
        "license": "Apache 2.0",
        "home_page": "https://requests.readthedocs.io",
        "project_urls": {
            "Documentation": "https://requests.readthedocs.io",
            "Source": "https://github.com/psf/requests",
        },
        "classifiers": ["Development Status :: 5 - Production/Stable"],
        "keywords": ["http", "requests", "web"],
    }


@pytest.fixture
def sample_primary_docs():
    """Sample primary package documentation."""
    return PackageDocumentation(
        name="requests",
        version="2.28.0",
        relationship="primary",
        summary="Python HTTP for Humans.",
        key_features=["HTTP/1.1", "Connection pooling", "SSL/TLS verification"],
        main_classes=["Session", "Request", "Response"],
        main_functions=["get", "post", "put", "delete"],
        usage_examples="requests.get('https://api.github.com')",
        why_included="Requested package",
        dependency_level=0,
    )


@pytest.fixture
def sample_dependency_docs():
    """Sample dependency package documentation."""
    return PackageDocumentation(
        name="urllib3",
        version="1.26.12",
        relationship="runtime_dependency",
        summary="HTTP library with thread-safe connection pooling.",
        key_features=["Connection pooling", "Thread-safe", "SSL/TLS"],
        main_classes=["PoolManager", "HTTPConnection"],
        main_functions=["request", "urlopen"],
        why_included="Required by requests",
        dependency_level=1,
    )


class TestConcurrentContextFetcherInitialization:
    """Test ConcurrentContextFetcher initialization."""

    def test_init_with_all_dependencies(
        self,
        mock_cache_manager,
        mock_dependency_resolver,
        mock_formatter,
        mock_network_client,
    ):
        """Test initialization with all required dependencies."""
        fetcher = ConcurrentContextFetcher(
            cache_manager=mock_cache_manager,
            dependency_resolver=mock_dependency_resolver,
            formatter=mock_formatter,
            network_client=mock_network_client,
        )

        assert fetcher.cache_manager == mock_cache_manager
        assert fetcher.dependency_resolver == mock_dependency_resolver
        assert fetcher.formatter == mock_formatter
        assert fetcher.network_client == mock_network_client
        assert fetcher.config is not None

    def test_init_without_network_client(
        self, mock_cache_manager, mock_dependency_resolver, mock_formatter
    ):
        """Test initialization without network client (allowed to be None)."""
        fetcher = ConcurrentContextFetcher(
            cache_manager=mock_cache_manager,
            dependency_resolver=mock_dependency_resolver,
            formatter=mock_formatter,
            network_client=None,
        )

        assert fetcher.network_client is None
        assert fetcher.cache_manager == mock_cache_manager
        assert fetcher.dependency_resolver == mock_dependency_resolver
        assert fetcher.formatter == mock_formatter

    def test_config_loading(self, context_fetcher, mocker):
        """Test that configuration is loaded during initialization."""
        mock_get_config = mocker.patch(
            "src.autodoc_mcp.core.context_fetcher.get_config"
        )
        mock_config = mocker.Mock()
        mock_get_config.return_value = mock_config

        # Create new fetcher to trigger config loading
        ConcurrentContextFetcher(
            cache_manager=mocker.AsyncMock(),
            dependency_resolver=mocker.AsyncMock(),
            formatter=mocker.Mock(),
        )

        mock_get_config.assert_called_once()


class TestFetchPackageContextPrimaryOnly:
    """Test fetch_package_context with primary package only."""

    @pytest.mark.asyncio
    async def test_fetch_primary_only_cache_hit(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test fetching primary package with cache hit."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )

        # Execute
        result, metrics = await context_fetcher.fetch_package_context(
            package_name="requests",
            version_constraint=">=2.0.0",
            include_dependencies=False,
        )

        # Verify result
        assert isinstance(result, DocumentationContext)
        assert result.primary_package == sample_primary_docs
        assert result.runtime_dependencies == []
        assert result.context_scope == "primary_only"
        assert result.total_packages == 1

        # Verify metrics
        assert metrics["cache_hits"] == 1
        assert metrics["cache_misses"] == 0
        assert metrics["concurrent_fetches"] == 0
        assert metrics["failed_fetches"] == 0
        assert metrics["total_time"] > 0

        # Verify mocks were called correctly
        context_fetcher.cache_manager.resolve_and_cache.assert_called_once_with(
            "requests", ">=2.0.0"
        )
        context_fetcher.formatter.format_primary_package.assert_called_once_with(
            sample_package_info, True
        )

    @pytest.mark.asyncio
    async def test_fetch_primary_only_cache_miss(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test fetching primary package with cache miss."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, False)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )

        # Execute
        result, metrics = await context_fetcher.fetch_package_context(
            package_name="requests", include_dependencies=False
        )

        # Verify metrics reflect cache miss
        assert metrics["cache_hits"] == 0
        assert metrics["cache_misses"] == 1
        assert result.primary_package == sample_primary_docs

    @pytest.mark.asyncio
    async def test_fetch_primary_with_version_constraint(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test fetching primary package with version constraint."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, False)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )

        # Execute
        await context_fetcher.fetch_package_context(
            package_name="requests",
            version_constraint="~=2.28.0",
            include_dependencies=False,
        )

        # Verify version constraint passed correctly
        context_fetcher.cache_manager.resolve_and_cache.assert_called_once_with(
            "requests", "~=2.28.0"
        )


class TestFetchPackageContextWithDependencies:
    """Test fetch_package_context with dependencies included."""

    @pytest.mark.asyncio
    async def test_fetch_with_runtime_dependencies_success(
        self,
        context_fetcher,
        sample_package_info,
        sample_primary_docs,
        sample_dependency_docs,
        mocker,
    ):
        """Test fetching package with runtime dependencies successfully."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )
        context_fetcher.dependency_resolver.resolve_context_dependencies = (
            mocker.AsyncMock(return_value=["urllib3", "charset-normalizer"])
        )

        # Mock concurrent dependency fetching
        mock_fetch_deps = mocker.patch.object(
            context_fetcher,
            "_fetch_dependencies_concurrently",
            return_value=[sample_dependency_docs],
        )

        # Mock config values
        context_fetcher.config.max_dependency_context = 10
        context_fetcher.config.max_context_tokens = 50000

        # Mock context window manager
        mock_context_manager = mocker.patch(
            "src.autodoc_mcp.core.context_fetcher.ContextWindowManager"
        )
        mock_context_manager.fit_to_window.return_value = mocker.Mock(
            primary_package=sample_primary_docs,
            runtime_dependencies=[sample_dependency_docs],
            context_scope="with_runtime (1 deps)",
            total_packages=2,
            token_estimate=1500,
            truncated_packages=[],
        )

        # Execute
        result, metrics = await context_fetcher.fetch_package_context(
            package_name="requests",
            include_dependencies=True,
            context_scope="smart",
        )

        # Verify dependency resolution was called
        context_fetcher.dependency_resolver.resolve_context_dependencies.assert_called_once_with(
            package_name="requests",
            version="2.28.0",
            max_dependencies=10,
            max_tokens=50000,
        )

        # Verify concurrent fetching was called
        mock_fetch_deps.assert_called_once_with(
            ["urllib3", "charset-normalizer"], "requests", metrics
        )

        # Verify result structure
        assert result.total_packages == 2
        assert len(result.runtime_dependencies) == 1
        assert metrics["concurrent_fetches"] == 2

    @pytest.mark.asyncio
    async def test_fetch_with_max_dependencies_limit(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test fetching with max_dependencies parameter."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )
        context_fetcher.dependency_resolver.resolve_context_dependencies = (
            mocker.AsyncMock(return_value=[])
        )

        # Execute with custom max_dependencies
        await context_fetcher.fetch_package_context(
            package_name="requests",
            include_dependencies=True,
            max_dependencies=3,
        )

        # Verify max_dependencies was used
        context_fetcher.dependency_resolver.resolve_context_dependencies.assert_called_once_with(
            package_name="requests",
            version="2.28.0",
            max_dependencies=3,
            max_tokens=50000,  # Default from config
        )

    @pytest.mark.asyncio
    async def test_fetch_with_max_tokens_limit(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test fetching with max_tokens parameter."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )
        context_fetcher.dependency_resolver.resolve_context_dependencies = (
            mocker.AsyncMock(return_value=[])
        )

        # Mock config to control max_dependency_context
        context_fetcher.config.max_dependency_context = 10

        # Execute with custom max_tokens and non-smart context scope to get fallback
        await context_fetcher.fetch_package_context(
            package_name="requests",
            include_dependencies=True,
            context_scope="runtime",  # Non-smart scope to get fallback of 5
            max_tokens=25000,
        )

        # Verify max_tokens was used and fallback max_dependencies
        context_fetcher.dependency_resolver.resolve_context_dependencies.assert_called_once_with(
            package_name="requests",
            version="2.28.0",
            max_dependencies=5,  # Fallback for non-smart scope
            max_tokens=25000,
        )

    @pytest.mark.asyncio
    async def test_fetch_with_no_dependencies_found(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test fetching when no dependencies are resolved."""
        # Setup mocks - empty dependency list
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )
        context_fetcher.dependency_resolver.resolve_context_dependencies = (
            mocker.AsyncMock(return_value=[])
        )

        # Execute
        result, metrics = await context_fetcher.fetch_package_context(
            package_name="requests", include_dependencies=True
        )

        # Verify result contains only primary package
        assert result.total_packages == 1
        assert result.runtime_dependencies == []
        assert result.context_scope == "primary_only"
        assert metrics["concurrent_fetches"] == 0


class TestFetchPackageContextScoping:
    """Test different context scoping options."""

    @pytest.mark.asyncio
    async def test_context_scope_primary_only(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test context_scope='primary_only' ignores dependencies."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )

        # Execute with primary_only scope
        result, metrics = await context_fetcher.fetch_package_context(
            package_name="requests",
            include_dependencies=True,
            context_scope="primary_only",
        )

        # Dependencies should still be resolved with primary_only scope
        # The behavior depends on the implementation of dependency resolver
        assert result.primary_package == sample_primary_docs

    @pytest.mark.asyncio
    async def test_context_scope_runtime(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test context_scope='runtime' includes runtime dependencies."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )
        context_fetcher.dependency_resolver.resolve_context_dependencies = (
            mocker.AsyncMock(return_value=[])
        )

        # Execute with runtime scope
        await context_fetcher.fetch_package_context(
            package_name="requests",
            include_dependencies=True,
            context_scope="runtime",
        )

        # Verify dependency resolution was called with runtime scope
        context_fetcher.dependency_resolver.resolve_context_dependencies.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_scope_smart_uses_config_limits(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test context_scope='smart' uses configuration limits."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )
        context_fetcher.dependency_resolver.resolve_context_dependencies = (
            mocker.AsyncMock(return_value=[])
        )

        # Mock config
        context_fetcher.config.max_dependency_context = 15
        context_fetcher.config.max_context_tokens = 75000

        # Execute with smart scope
        await context_fetcher.fetch_package_context(
            package_name="requests",
            include_dependencies=True,
            context_scope="smart",
        )

        # Verify config limits were used
        context_fetcher.dependency_resolver.resolve_context_dependencies.assert_called_once_with(
            package_name="requests",
            version="2.28.0",
            max_dependencies=15,
            max_tokens=75000,
        )


class TestConcurrentDependencyFetching:
    """Test concurrent dependency fetching functionality."""

    @pytest.mark.asyncio
    async def test_fetch_dependencies_concurrently_success(
        self, context_fetcher, sample_dependency_docs, mocker
    ):
        """Test successful concurrent dependency fetching."""
        # Mock single dependency fetch
        mock_fetch_single = mocker.patch.object(
            context_fetcher,
            "_fetch_single_dependency_with_semaphore",
            return_value=sample_dependency_docs,
        )

        dependency_names = ["urllib3", "charset-normalizer", "idna"]
        performance_metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "failed_fetches": 0,
        }

        # Execute
        results = await context_fetcher._fetch_dependencies_concurrently(
            dependency_names, "requests", performance_metrics
        )

        # Verify results
        assert len(results) == 3
        assert all(isinstance(result, PackageDocumentation) for result in results)
        assert mock_fetch_single.call_count == 3

    @pytest.mark.asyncio
    async def test_fetch_dependencies_concurrently_empty_list(self, context_fetcher):
        """Test concurrent fetching with empty dependency list."""
        results = await context_fetcher._fetch_dependencies_concurrently(
            [], "requests", {}
        )

        assert results == []

    @pytest.mark.asyncio
    async def test_fetch_dependencies_concurrently_timeout(
        self, context_fetcher, mocker
    ):
        """Test concurrent fetching with timeout."""

        # Mock fetch to simulate timeout by raising TimeoutError
        async def timeout_fetch(*args, **kwargs):
            raise TimeoutError("Simulated timeout")

        mocker.patch.object(
            context_fetcher,
            "_fetch_single_dependency_with_semaphore",
            side_effect=timeout_fetch,
        )

        dependency_names = ["slow-package"]
        performance_metrics = {"failed_fetches": 0}

        # Execute - should timeout
        results = await context_fetcher._fetch_dependencies_concurrently(
            dependency_names, "requests", performance_metrics
        )

        # Should return timeout exceptions
        assert len(results) == 1
        assert isinstance(results[0], Exception)
        assert "timeout" in str(results[0]).lower()

    @pytest.mark.asyncio
    async def test_fetch_single_dependency_with_semaphore(
        self, context_fetcher, sample_dependency_docs, mocker
    ):
        """Test semaphore-controlled single dependency fetching."""
        # Mock the actual fetch method
        mock_fetch = mocker.patch.object(
            context_fetcher,
            "_fetch_single_dependency",
            return_value=sample_dependency_docs,
        )

        semaphore = asyncio.Semaphore(1)
        performance_metrics = {}

        # Execute
        result = await context_fetcher._fetch_single_dependency_with_semaphore(
            semaphore, "urllib3", "requests", performance_metrics
        )

        assert result == sample_dependency_docs
        mock_fetch.assert_called_once_with("urllib3", "requests", performance_metrics)

    @pytest.mark.asyncio
    async def test_fetch_single_dependency_success(
        self, context_fetcher, sample_package_info, sample_dependency_docs, mocker
    ):
        """Test fetching single dependency successfully."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_dependency_package.return_value = (
            sample_dependency_docs
        )

        performance_metrics = {"cache_hits": 0, "cache_misses": 0}

        # Execute
        result = await context_fetcher._fetch_single_dependency(
            "urllib3", "requests", performance_metrics
        )

        # Verify result
        assert result == sample_dependency_docs
        assert performance_metrics["cache_hits"] == 1

        # Verify mocks called correctly
        context_fetcher.cache_manager.resolve_and_cache.assert_called_once_with(
            "urllib3"
        )
        context_fetcher.formatter.format_dependency_package.assert_called_once_with(
            sample_package_info, "requests"
        )

    @pytest.mark.asyncio
    async def test_fetch_single_dependency_failure(self, context_fetcher, mocker):
        """Test fetching single dependency with failure."""
        # Setup mocks to raise exception
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            side_effect=NetworkError("Network failed")
        )

        performance_metrics = {"cache_hits": 0, "cache_misses": 0}

        # Execute
        result = await context_fetcher._fetch_single_dependency(
            "bad-package", "requests", performance_metrics
        )

        # Should return minimal documentation for failed fetch
        assert isinstance(result, PackageDocumentation)
        assert result.name == "bad-package"
        assert result.version == "unknown"
        assert "fetch failed" in result.summary
        assert "Required by requests" in result.why_included


class TestErrorHandling:
    """Test error handling in context fetching."""

    @pytest.mark.asyncio
    async def test_fetch_package_context_primary_fetch_error(
        self, context_fetcher, mocker
    ):
        """Test error handling when primary package fetch fails."""
        # Setup mock to raise exception
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            side_effect=NetworkError("Package not found")
        )

        # Should re-raise the exception
        with pytest.raises(NetworkError, match="Package not found"):
            await context_fetcher.fetch_package_context("nonexistent-package")

    @pytest.mark.asyncio
    async def test_fetch_package_context_dependency_resolution_error(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test error handling when dependency resolution fails."""
        # Setup mocks - primary succeeds, dependency resolution fails
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )
        context_fetcher.dependency_resolver.resolve_context_dependencies = (
            mocker.AsyncMock(side_effect=Exception("Dependency resolution failed"))
        )

        # Mock context window manager
        mock_context_manager = mocker.patch(
            "src.autodoc_mcp.core.context_fetcher.ContextWindowManager"
        )
        mock_context_manager.fit_to_window.return_value = mocker.Mock(
            primary_package=sample_primary_docs,
            context_scope="primary_only (deps_failed)",
            token_estimate=500,
        )

        # Should return primary-only context with error indication
        result, metrics = await context_fetcher.fetch_package_context(
            "requests", include_dependencies=True
        )

        # Verify graceful degradation
        assert result.primary_package == sample_primary_docs
        assert "deps_failed" in result.context_scope
        assert metrics["total_time"] > 0

    @pytest.mark.asyncio
    async def test_fetch_package_context_mixed_dependency_results(
        self,
        context_fetcher,
        sample_package_info,
        sample_primary_docs,
        sample_dependency_docs,
        mocker,
    ):
        """Test handling mixed success/failure results in dependency fetching."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )
        context_fetcher.dependency_resolver.resolve_context_dependencies = (
            mocker.AsyncMock(return_value=["urllib3", "bad-package"])
        )

        # Mock concurrent fetching with mixed results
        mocker.patch.object(
            context_fetcher,
            "_fetch_dependencies_concurrently",
            return_value=[
                sample_dependency_docs,
                Exception("Failed to fetch bad-package"),
            ],
        )

        # Mock context window manager
        mock_context_manager = mocker.patch(
            "src.autodoc_mcp.core.context_fetcher.ContextWindowManager"
        )
        expected_context = mocker.Mock(
            primary_package=sample_primary_docs,
            runtime_dependencies=[sample_dependency_docs],
            context_scope="with_runtime (1 deps)",
            total_packages=2,
            truncated_packages=["Failed: Failed to fetch bad-package"],
            token_estimate=1200,
        )
        mock_context_manager.fit_to_window.return_value = expected_context

        # Execute
        result, metrics = await context_fetcher.fetch_package_context(
            "requests", include_dependencies=True
        )

        # Verify partial success handling
        assert result == expected_context
        assert metrics["failed_fetches"] == 1
        assert metrics["concurrent_fetches"] == 2

    @pytest.mark.asyncio
    async def test_fetch_package_context_early_primary_failure(
        self, context_fetcher, mocker
    ):
        """Test early failure before primary_docs is created."""
        # Setup mock to fail immediately
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            side_effect=Exception("Immediate failure")
        )

        # Should re-raise the exception since primary_docs doesn't exist
        with pytest.raises(Exception, match="Immediate failure"):
            await context_fetcher.fetch_package_context("bad-package")


class TestPerformanceMetrics:
    """Test performance metrics collection."""

    @pytest.mark.asyncio
    async def test_performance_metrics_structure(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test that all expected performance metrics are collected."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, False)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )

        # Execute
        result, metrics = await context_fetcher.fetch_package_context(
            "requests", include_dependencies=False
        )

        # Verify all expected metrics are present
        expected_keys = [
            "primary_fetch_time",
            "dependency_resolution_time",
            "dependency_fetch_time",
            "total_time",
            "cache_hits",
            "cache_misses",
            "concurrent_fetches",
            "failed_fetches",
        ]

        for key in expected_keys:
            assert key in metrics
            assert isinstance(metrics[key], int | float)

        # Verify time metrics are reasonable
        assert metrics["total_time"] > 0
        assert metrics["primary_fetch_time"] >= 0
        assert metrics["total_time"] >= metrics["primary_fetch_time"]

    @pytest.mark.asyncio
    async def test_timing_metrics_accuracy(
        self, context_fetcher, sample_package_info, sample_primary_docs, mocker
    ):
        """Test timing metrics accuracy by introducing controlled delays."""
        # Mock time.time to control timing
        # Need extra timestamps for all the time.time() calls in the method
        mock_times = [
            0.0,
            0.1,
            0.2,
            0.2,
            0.2,
            0.2,
        ]  # start, primary_start_end, total_end, extras for all time calls
        mock_time = mocker.patch("src.autodoc_mcp.core.context_fetcher.time.time")
        mock_time.side_effect = mock_times

        # Setup other mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )

        # Execute
        result, metrics = await context_fetcher.fetch_package_context(
            "requests", include_dependencies=False
        )

        # Verify timing calculations
        assert metrics["primary_fetch_time"] == 0.1  # 0.1 - 0.0
        assert metrics["total_time"] == 0.2  # 0.2 - 0.0


class TestContextWindowManagement:
    """Test context window management integration."""

    @pytest.mark.asyncio
    async def test_context_window_fitting(
        self,
        context_fetcher,
        sample_package_info,
        sample_primary_docs,
        sample_dependency_docs,
        mocker,
    ):
        """Test that context is fitted to token window."""
        # Setup mocks
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(sample_package_info, True)
        )
        context_fetcher.formatter.format_primary_package.return_value = (
            sample_primary_docs
        )
        context_fetcher.dependency_resolver.resolve_context_dependencies = (
            mocker.AsyncMock(return_value=["urllib3"])
        )

        # Mock concurrent dependency fetching
        mocker.patch.object(
            context_fetcher,
            "_fetch_dependencies_concurrently",
            return_value=[sample_dependency_docs],
        )

        # Mock context window manager
        mock_context_manager = mocker.patch(
            "src.autodoc_mcp.core.context_fetcher.ContextWindowManager"
        )
        fitted_context = mocker.Mock(
            primary_package=sample_primary_docs,
            runtime_dependencies=[sample_dependency_docs],
            truncated_packages=["some-large-package"],
            token_estimate=45000,
        )
        mock_context_manager.fit_to_window.return_value = fitted_context

        # Execute with token limit
        result, metrics = await context_fetcher.fetch_package_context(
            "requests", include_dependencies=True, max_tokens=50000
        )

        # Verify context window manager was called
        mock_context_manager.fit_to_window.assert_called_once()
        args, kwargs = mock_context_manager.fit_to_window.call_args
        assert args[1] == 50000  # max_tokens parameter

        # Verify fitted context is returned
        assert result == fitted_context


class TestCreateContextFetcher:
    """Test factory function for creating context fetcher."""

    @pytest.mark.asyncio
    async def test_create_context_fetcher_with_dependencies(self, mocker):
        """Test create_context_fetcher factory function."""
        # Mock all the components
        mock_cache_manager = mocker.AsyncMock()
        mock_network_client = mocker.AsyncMock()
        mock_network_client.__aenter__ = mocker.AsyncMock(
            return_value=mock_network_client
        )

        mock_network_client_class = mocker.patch(
            "src.autodoc_mcp.core.context_fetcher.NetworkResilientClient"
        )
        mock_network_client_class.return_value = mock_network_client

        mock_resolver_class = mocker.patch(
            "src.autodoc_mcp.core.context_fetcher.DependencyResolver"
        )
        mock_formatter_class = mocker.patch(
            "src.autodoc_mcp.core.context_fetcher.ContextDocumentationFormatter"
        )

        # Execute
        fetcher = await create_context_fetcher(mock_cache_manager)

        # Verify all components were created
        mock_network_client_class.assert_called_once()
        mock_network_client.__aenter__.assert_called_once()
        mock_resolver_class.assert_called_once_with(mock_network_client)
        mock_formatter_class.assert_called_once()

        # Verify fetcher was created properly
        assert isinstance(fetcher, ConcurrentContextFetcher)
        assert fetcher.cache_manager == mock_cache_manager
        assert fetcher.network_client == mock_network_client


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    @pytest.mark.asyncio
    async def test_real_world_package_with_many_dependencies(
        self, context_fetcher, mocker
    ):
        """Test realistic scenario with package having many dependencies."""
        # Mock primary package (fastapi)
        primary_info = {
            "name": "fastapi",
            "version": "0.104.1",
            "summary": "FastAPI framework, high performance web API framework",
            "description": "FastAPI is a modern web framework for Python",
        }
        primary_docs = PackageDocumentation(
            name="fastapi",
            version="0.104.1",
            relationship="primary",
            summary="FastAPI framework",
            why_included="Requested package",
            dependency_level=0,
        )

        # Setup mocks for realistic scenario
        context_fetcher.cache_manager.resolve_and_cache = mocker.AsyncMock(
            return_value=(primary_info, False)
        )
        context_fetcher.formatter.format_primary_package.return_value = primary_docs

        # Many dependencies
        dependencies = [
            "pydantic",
            "starlette",
            "typing-extensions",
            "uvicorn",
            "httpx",
        ]
        context_fetcher.dependency_resolver.resolve_context_dependencies = (
            mocker.AsyncMock(return_value=dependencies)
        )

        # Mock successful dependency fetches
        dependency_docs = [
            PackageDocumentation(
                name=dep,
                version="1.0.0",
                relationship="runtime_dependency",
                why_included="Required by fastapi",
                dependency_level=1,
            )
            for dep in dependencies
        ]

        mocker.patch.object(
            context_fetcher,
            "_fetch_dependencies_concurrently",
            return_value=dependency_docs,
        )

        # Mock context window manager
        mock_context_manager = mocker.patch(
            "src.autodoc_mcp.core.context_fetcher.ContextWindowManager"
        )
        fitted_context = mocker.Mock(
            primary_package=primary_docs,
            runtime_dependencies=dependency_docs,
            total_packages=6,
            context_scope="with_runtime (5 deps)",
            token_estimate=35000,
            truncated_packages=[],
        )
        mock_context_manager.fit_to_window.return_value = fitted_context

        # Execute
        result, metrics = await context_fetcher.fetch_package_context(
            "fastapi", include_dependencies=True, context_scope="smart"
        )

        # Verify realistic results
        assert result.total_packages == 6
        assert len(result.runtime_dependencies) == 5
        assert metrics["concurrent_fetches"] == 5
        assert metrics["cache_misses"] >= 1  # At least primary package
