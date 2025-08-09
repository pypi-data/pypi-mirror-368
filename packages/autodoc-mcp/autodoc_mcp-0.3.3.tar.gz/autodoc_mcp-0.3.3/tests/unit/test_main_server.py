"""Comprehensive tests for main.py MCP server functionality."""

import asyncio
from datetime import datetime
from pathlib import Path

import pytest

from autodoc_mcp.exceptions import (
    PackageNotFoundError,
    ProjectParsingError,
)
from autodoc_mcp.models import CacheEntry, PackageInfo, ScanResult


class TestMCPTools:
    """Comprehensive MCP tool testing."""

    @pytest.mark.asyncio
    async def test_scan_dependencies_success(self, mocker):
        """Test successful dependency scanning."""
        # Setup mock parser response
        mock_result = ScanResult(
            project_path=Path("/test/project"),
            dependencies=[],
            project_name="test-project",
            scan_timestamp=datetime.now(),
            successful_deps=3,
            failed_deps=[],
        )

        # Use mocker instead of unittest.mock
        mock_parser = mocker.AsyncMock()
        mock_parser.parse_project = mocker.AsyncMock(return_value=mock_result)
        mock_formatter = mocker.patch("autodoc_mcp.main.ResponseFormatter")
        mock_validator = mocker.patch(
            "autodoc_mcp.main.InputValidator.validate_project_path"
        )

        mocker.patch("autodoc_mcp.main.parser", mock_parser)
        mock_formatter.format_scan_response.return_value = {
            "success": True,
            "dependency_count": 3,
        }
        mock_validator.return_value = Path("/test/project")

        # Import and call the function directly
        from autodoc_mcp.main import scan_dependencies

        result = await scan_dependencies.fn("/test/project")

        assert result["success"] is True
        assert result["dependency_count"] == 3
        mock_parser.parse_project.assert_called_once()

    @pytest.mark.asyncio
    async def test_scan_dependencies_parser_not_initialized(self, mocker):
        """Test scan_dependencies when parser is None."""
        from autodoc_mcp.main import scan_dependencies

        mocker.patch("autodoc_mcp.main.parser", None)
        result = await scan_dependencies.fn("/test/project")

        assert result["success"] is False
        assert result["error"]["code"] == "service_not_initialized"
        assert "Parser not initialized" in result["error"]["message"]
        assert result["error"]["recoverable"] is False

    @pytest.mark.asyncio
    async def test_scan_dependencies_project_parsing_error(self, mock_services, mocker):
        """Test scan_dependencies with ProjectParsingError."""
        from autodoc_mcp.main import scan_dependencies

        mock_services["parser"].parse_project.side_effect = ProjectParsingError(
            "Invalid project", Path("/test")
        )

        # Need to mock InputValidator as well
        mocker.patch(
            "autodoc_mcp.main.InputValidator.validate_project_path",
            return_value=Path("/test/project"),
        )

        mock_formatter = mocker.patch("autodoc_mcp.main.ErrorFormatter")
        mock_error = mocker.MagicMock()
        mock_error.message = "Invalid project structure"
        mock_error.suggestion = "Check pyproject.toml"
        mock_error.severity.value = "critical"
        mock_error.error_code = "project_parse_error"
        mock_error.recoverable = False
        mock_formatter.format_exception.return_value = mock_error

        result = await scan_dependencies.fn("/test/project")

        assert result["success"] is False
        assert "Invalid project structure" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_scan_dependencies_generic_error(self, mock_services, mocker):
        """Test scan_dependencies with generic exception."""
        from autodoc_mcp.main import scan_dependencies

        mock_services["parser"].parse_project.side_effect = ValueError("Generic error")

        mock_formatter = mocker.patch("autodoc_mcp.main.ErrorFormatter")
        mock_error = mocker.MagicMock()
        mock_error.message = "Unexpected error occurred"
        mock_error.suggestion = "Try again"
        mock_error.severity.value = "error"
        mock_error.error_code = "unexpected_error"
        mock_error.recoverable = True
        mock_formatter.format_exception.return_value = mock_error

        result = await scan_dependencies.fn("/test/project")

        assert result["success"] is False
        assert result["error"]["code"] == "unexpected_error"

    @pytest.mark.asyncio
    async def test_get_package_docs_success(self, mock_services, mocker):
        """Test successful package documentation retrieval."""
        from autodoc_mcp.main import get_package_docs

        # Mock services
        mock_services["version_resolver"].resolve_version = mocker.AsyncMock(
            return_value="2.28.2"
        )
        mock_services[
            "version_resolver"
        ].generate_cache_key.return_value = "requests-2.28.2"

        # Mock cache miss, fresh fetch
        mock_services["cache_manager"].get = mocker.AsyncMock(return_value=None)
        mock_services["cache_manager"].set = mocker.AsyncMock()

        # Mock package info
        mock_package_info = PackageInfo(
            name="requests",
            version="2.28.2",
            summary="HTTP library",
            description="Python HTTP library",
            author="Kenneth Reitz",
            author_email="me@kennethreitz.org",
            home_page="https://requests.readthedocs.io",
            package_url="https://pypi.org/project/requests/",
            project_urls={},
            classifiers=[],
            keywords=[],
            license="Apache 2.0",
        )

        mock_fetcher_class = mocker.patch("autodoc_mcp.main.PyPIDocumentationFetcher")
        mock_validator = mocker.patch("autodoc_mcp.main.InputValidator")

        mock_fetcher = mocker.AsyncMock()
        mock_fetcher.fetch_package_info = mocker.AsyncMock(
            return_value=mock_package_info
        )
        mock_fetcher.format_documentation.return_value = "# requests v2.28.2\n..."
        mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher
        mock_fetcher_class.return_value.__aexit__.return_value = None

        mock_validator.validate_package_name.return_value = "requests"
        mock_validator.validate_version_constraint.return_value = ">=2.0.0"

        result = await get_package_docs.fn("requests", ">=2.0.0", None)

        assert result["success"] is True
        assert result["package_name"] == "requests"
        assert result["version"] == "2.28.2"
        assert result["from_cache"] is False
        assert "documentation" in result

    @pytest.mark.asyncio
    async def test_get_package_docs_cache_hit(self, mock_services, mocker):
        """Test package docs retrieval with cache hit."""
        from autodoc_mcp.main import get_package_docs

        mock_services["version_resolver"].resolve_version = mocker.AsyncMock(
            return_value="2.28.2"
        )
        mock_services[
            "version_resolver"
        ].generate_cache_key.return_value = "requests-2.28.2"

        # Mock cache hit
        mock_package_info = PackageInfo(
            name="requests",
            version="2.28.2",
            summary="HTTP library",
            description="Python HTTP library",
            author="Kenneth Reitz",
            author_email="me@kennethreitz.org",
            home_page="https://requests.readthedocs.io",
            package_url="https://pypi.org/project/requests/",
            project_urls={},
            classifiers=[],
            keywords=[],
            license="Apache 2.0",
        )
        mock_cache_entry = CacheEntry(
            data=mock_package_info,
            timestamp=datetime.fromtimestamp(1234567890.0),
            version="2.28.2",
        )
        mock_services["cache_manager"].get = mocker.AsyncMock(
            return_value=mock_cache_entry
        )

        mock_fetcher_class = mocker.patch("autodoc_mcp.main.PyPIDocumentationFetcher")
        mock_validator = mocker.patch("autodoc_mcp.main.InputValidator")

        mock_fetcher = mocker.AsyncMock()
        mock_fetcher.format_documentation.return_value = "# requests v2.28.2\n..."
        mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher
        mock_fetcher_class.return_value.__aexit__.return_value = None

        mock_validator.validate_package_name.return_value = "requests"

        result = await get_package_docs.fn("requests", None, None)

        assert result["success"] is True
        assert result["from_cache"] is True
        # Should not call set when cache hit
        mock_services["cache_manager"].set.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_package_docs_services_not_initialized(self, mocker):
        """Test get_package_docs when services are None."""
        from autodoc_mcp.main import get_package_docs

        mocker.patch("autodoc_mcp.main.cache_manager", None)
        mocker.patch("autodoc_mcp.main.version_resolver", None)
        result = await get_package_docs.fn("requests")

        assert result["success"] is False
        assert result["error"]["code"] == "service_not_initialized"

    @pytest.mark.asyncio
    async def test_get_package_docs_package_not_found(self, mock_services, mocker):
        """Test get_package_docs with PackageNotFoundError."""
        from autodoc_mcp.main import get_package_docs

        mock_services["version_resolver"].resolve_version = mocker.AsyncMock(
            side_effect=PackageNotFoundError("Package not found")
        )

        mock_validator = mocker.patch("autodoc_mcp.main.InputValidator")
        mock_formatter = mocker.patch("autodoc_mcp.main.ErrorFormatter")
        mock_validator.validate_package_name.return_value = "nonexistent"
        mock_error = mocker.MagicMock()
        mock_error.message = "Package 'nonexistent' not found on PyPI"
        mock_error.suggestion = "Check package name spelling"
        mock_error.severity.value = "error"
        mock_error.error_code = "package_not_found"
        mock_error.recoverable = True
        mock_formatter.format_exception.return_value = mock_error

        result = await get_package_docs.fn("nonexistent")

        assert result["success"] is False
        assert result["error"]["code"] == "package_not_found"

    @pytest.mark.asyncio
    async def test_get_package_docs_with_context_success(self, mock_services, mocker):
        """Test successful context documentation retrieval."""
        from autodoc_mcp.main import get_package_docs_with_context

        # Mock context fetcher
        mock_context = mocker.MagicMock()
        mock_context.primary_package.model_dump.return_value = {
            "name": "requests",
            "version": "2.28.2",
        }
        mock_context.runtime_dependencies = []
        mock_context.dev_dependencies = []
        mock_context.context_scope = "smart"
        mock_context.total_packages = 1
        mock_context.truncated_packages = 0
        mock_context.token_estimate = 1000

        mock_performance = {"fetch_time": 1.5, "cache_hits": 0}

        mock_services["context_fetcher"].fetch_package_context = mocker.AsyncMock(
            return_value=(mock_context, mock_performance)
        )

        mock_validator = mocker.patch("autodoc_mcp.main.InputValidator")
        mock_validator.validate_package_name.return_value = "requests"

        result = await get_package_docs_with_context.fn("requests")

        assert result["success"] is True
        assert result["context"]["primary_package"]["name"] == "requests"
        assert result["performance"]["fetch_time"] == 1.5

    @pytest.mark.asyncio
    async def test_get_package_docs_with_context_not_initialized(self, mocker):
        """Test get_package_docs_with_context when context_fetcher is None."""
        from autodoc_mcp.main import get_package_docs_with_context

        mocker.patch("autodoc_mcp.main.context_fetcher", None)
        result = await get_package_docs_with_context.fn("requests")

        assert result["success"] is False
        assert "Context fetcher not initialized" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_refresh_cache_success(self, mock_services):
        """Test successful cache refresh."""
        from autodoc_mcp.main import refresh_cache

        # Mock cache stats
        initial_stats = {"total_entries": 5, "total_size_bytes": 50000}
        final_stats = {"total_entries": 0, "total_size_bytes": 0}

        mock_services["cache_manager"].get_cache_stats.side_effect = [
            initial_stats,
            final_stats,
        ]
        mock_services["cache_manager"].invalidate.return_value = None

        result = await refresh_cache.fn()

        assert result["success"] is True
        assert result["cleared_entries"] == 5
        assert result["freed_bytes"] == 50000
        assert result["final_entries"] == 0

    @pytest.mark.asyncio
    async def test_refresh_cache_not_initialized(self, mocker):
        """Test refresh_cache when cache_manager is None."""
        from autodoc_mcp.main import refresh_cache

        mocker.patch("autodoc_mcp.main.cache_manager", None)
        result = await refresh_cache.fn()

        assert result["success"] is False
        assert result["error"]["code"] == "service_not_initialized"

    @pytest.mark.asyncio
    async def test_get_cache_stats_success(self, mock_services):
        """Test successful cache statistics retrieval."""
        from autodoc_mcp.main import get_cache_stats

        mock_stats = {
            "total_entries": 10,
            "total_size_bytes": 100000,
            "cache_hit_rate": 85.5,
        }
        mock_packages = ["requests-2.28.2", "pydantic-1.10.0", "fastapi-0.95.0"]

        mock_services["cache_manager"].get_cache_stats.return_value = mock_stats
        mock_services["cache_manager"].list_cached_packages.return_value = mock_packages

        result = await get_cache_stats.fn()

        assert result["success"] is True
        assert result["cache_stats"] == mock_stats
        assert result["cached_packages"] == mock_packages
        assert result["total_packages"] == 3

    @pytest.mark.asyncio
    async def test_get_cache_stats_not_initialized(self, mocker):
        """Test get_cache_stats when cache_manager is None."""
        from autodoc_mcp.main import get_cache_stats

        mocker.patch("autodoc_mcp.main.cache_manager", None)
        result = await get_cache_stats.fn()

        assert result["success"] is False
        assert result["error"]["code"] == "service_not_initialized"

    @pytest.mark.asyncio
    async def test_get_cache_stats_error_handling(self, mock_services, mocker):
        """Test get_cache_stats with exception handling."""
        from autodoc_mcp.main import get_cache_stats

        mock_services["cache_manager"].get_cache_stats = mocker.AsyncMock(
            side_effect=Exception("Cache error")
        )

        mock_formatter = mocker.patch("autodoc_mcp.main.ErrorFormatter")
        mock_error = mocker.MagicMock()
        mock_error.message = "Failed to retrieve cache statistics"
        mock_error.suggestion = "Check cache directory permissions"
        mock_error.severity.value = "error"
        mock_error.error_code = "cache_stats_error"
        mock_error.recoverable = True
        mock_formatter.format_exception.return_value = mock_error

        result = await get_cache_stats.fn()

        assert result["success"] is False
        assert result["error"]["code"] == "cache_stats_error"


class TestServiceInitialization:
    """Test service initialization and error handling."""

    @pytest.mark.asyncio
    async def test_initialize_services_success(self, mocker):
        """Test successful service initialization."""
        from autodoc_mcp.main import initialize_services

        mock_config = mocker.patch("autodoc_mcp.main.get_config")
        mocker.patch("autodoc_mcp.main.PyProjectParser")
        mock_cache_class = mocker.patch("autodoc_mcp.main.FileCacheManager")
        mocker.patch("autodoc_mcp.main.VersionResolver")
        mock_create_context = mocker.patch("autodoc_mcp.main.create_context_fetcher")

        mock_config.return_value.cache_dir = Path("/tmp/cache")

        mock_cache_manager = mocker.AsyncMock()
        mock_cache_manager.initialize = mocker.AsyncMock()
        mock_cache_class.return_value = mock_cache_manager

        mock_context_fetcher = mocker.AsyncMock()
        mock_create_context.return_value = mock_context_fetcher

        await initialize_services()

        mock_cache_manager.initialize.assert_called_once()
        mock_create_context.assert_called_once_with(mock_cache_manager)

    @pytest.mark.asyncio
    async def test_initialize_services_cache_failure(self, mocker):
        """Test service initialization with cache manager failure."""
        from autodoc_mcp.main import initialize_services

        mock_config = mocker.patch("autodoc_mcp.main.get_config")
        mocker.patch("autodoc_mcp.main.PyProjectParser")
        mock_cache_class = mocker.patch("autodoc_mcp.main.FileCacheManager")
        mocker.patch("autodoc_mcp.main.VersionResolver")

        mock_config.return_value.cache_dir = Path("/tmp/cache")

        mock_cache_manager = mocker.AsyncMock()
        mock_cache_manager.initialize = mocker.AsyncMock(
            side_effect=Exception("Cache init failed")
        )
        mock_cache_class.return_value = mock_cache_manager

        with pytest.raises(Exception, match="Cache init failed"):
            await initialize_services()


class TestGracefulShutdown:
    """Test graceful shutdown functionality."""

    @pytest.mark.asyncio
    async def test_graceful_shutdown_no_active_requests(self, mocker):
        """Test graceful shutdown with no active requests."""
        from autodoc_mcp.main import GracefulShutdown

        shutdown_handler = GracefulShutdown()
        shutdown_handler.active_requests = 0

        mock_cleanup = mocker.patch.object(shutdown_handler, "_cleanup_resources")
        mock_cleanup.return_value = None
        shutdown_handler.shutdown_event.set()

        await shutdown_handler.wait_for_shutdown()

        mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_graceful_shutdown_with_active_requests(self, mocker):
        """Test graceful shutdown waits for active requests."""
        from autodoc_mcp.main import GracefulShutdown

        shutdown_handler = GracefulShutdown()
        shutdown_handler.active_requests = 2

        async def mock_requests_complete():
            await asyncio.sleep(0.1)  # Simulate request completion
            shutdown_handler.active_requests = 0

        mock_cleanup = mocker.patch.object(shutdown_handler, "_cleanup_resources")
        mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        mock_cleanup.return_value = None
        shutdown_handler.shutdown_event.set()

        # Start background task to simulate requests completing
        asyncio.create_task(mock_requests_complete())

        await shutdown_handler.wait_for_shutdown()

        mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_graceful_shutdown_timeout(self, mocker):
        """Test graceful shutdown with timeout."""
        from autodoc_mcp.main import GracefulShutdown

        shutdown_handler = GracefulShutdown()
        shutdown_handler.active_requests = 5
        shutdown_handler.max_shutdown_wait = 0.1  # Very short timeout

        mock_cleanup = mocker.patch.object(shutdown_handler, "_cleanup_resources")
        mock_cleanup.return_value = None
        shutdown_handler.shutdown_event.set()

        await shutdown_handler.wait_for_shutdown()

        # Should force shutdown after timeout
        mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_resources(self, mocker):
        """Test resource cleanup functionality."""
        from autodoc_mcp.main import GracefulShutdown

        shutdown_handler = GracefulShutdown()

        mock_pool_class = mocker.patch(
            "autodoc_mcp.core.network_resilience.ConnectionPoolManager"
        )
        mocker.patch("autodoc_mcp.main.cache_manager")

        mock_pool_manager = mocker.AsyncMock()
        mock_pool_manager.close_all = mocker.AsyncMock()
        mock_pool_class.return_value = mock_pool_manager

        await shutdown_handler._cleanup_resources()

        mock_pool_manager.close_all.assert_called_once()

    def test_signal_handler(self):
        """Test signal handler registration and handling."""
        from autodoc_mcp.main import GracefulShutdown

        shutdown_handler = GracefulShutdown()

        # Test signal handler
        shutdown_handler._signal_handler(15, None)  # SIGTERM

        assert shutdown_handler.shutdown_event.is_set()

    @pytest.mark.asyncio
    async def test_request_context_manager(self):
        """Test request context manager tracking."""
        from autodoc_mcp.main import GracefulShutdown

        shutdown_handler = GracefulShutdown()
        assert shutdown_handler.active_requests == 0

        async with shutdown_handler.request_context():
            assert shutdown_handler.active_requests == 1

        assert shutdown_handler.active_requests == 0

    @pytest.mark.asyncio
    async def test_request_context_manager_with_exception(self):
        """Test request context manager with exception."""
        from autodoc_mcp.main import GracefulShutdown

        shutdown_handler = GracefulShutdown()
        assert shutdown_handler.active_requests == 0

        with pytest.raises(ValueError):
            async with shutdown_handler.request_context():
                assert shutdown_handler.active_requests == 1
                raise ValueError("Test exception")

        # Should decrement even with exception
        assert shutdown_handler.active_requests == 0


class TestMainFunctions:
    """Test main function and server startup."""

    @pytest.mark.asyncio
    async def test_async_main_success(self, mocker):
        """Test successful async_main execution."""
        from autodoc_mcp.main import async_main

        mock_init = mocker.patch("autodoc_mcp.main.initialize_services")
        mocker.patch("autodoc_mcp.main.run_mcp_server")
        mock_shutdown_class = mocker.patch("autodoc_mcp.main.GracefulShutdown")

        mock_init.return_value = None
        mock_server_task = mocker.AsyncMock()
        mock_shutdown_task = mocker.AsyncMock()

        mock_shutdown_handler = mocker.AsyncMock()
        mock_shutdown_handler.register_signals.return_value = None
        mock_shutdown_handler.wait_for_shutdown.return_value = None
        mock_shutdown_handler._cleanup_resources.return_value = None
        mock_shutdown_class.return_value = mock_shutdown_handler

        mocker.patch(
            "asyncio.create_task",
            side_effect=[mock_server_task, mock_shutdown_task],
        )
        mocker.patch(
            "asyncio.wait",
            return_value=({mock_shutdown_task}, {mock_server_task}),
        )

        await async_main()

        mock_init.assert_called_once()
        mock_shutdown_handler.register_signals.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_main_initialization_failure(self, mocker):
        """Test async_main with service initialization failure."""
        from autodoc_mcp.main import async_main

        mock_init = mocker.patch("autodoc_mcp.main.initialize_services")
        mock_shutdown_class = mocker.patch("autodoc_mcp.main.GracefulShutdown")

        mock_init.side_effect = Exception("Initialization failed")

        mock_shutdown_handler = mocker.AsyncMock()
        mock_shutdown_handler.register_signals.return_value = None
        mock_shutdown_handler._cleanup_resources.return_value = None
        mock_shutdown_class.return_value = mock_shutdown_handler

        with pytest.raises(Exception, match="Initialization failed"):
            await async_main()

        # Should still cleanup resources
        mock_shutdown_handler._cleanup_resources.assert_called_once()

    def test_main_function_keyboard_interrupt(self, mocker):
        """Test main function handling KeyboardInterrupt."""
        from autodoc_mcp.main import main

        mock_run = mocker.patch("autodoc_mcp.main.asyncio.run")
        mock_logger = mocker.patch("autodoc_mcp.main.logger")

        mock_run.side_effect = KeyboardInterrupt()

        main()  # Should not raise

        mock_logger.info.assert_called_with("Server shutdown requested")

    def test_main_function_generic_exception(self, mocker):
        """Test main function handling generic exception."""
        from autodoc_mcp.main import main

        mock_run = mocker.patch("autodoc_mcp.main.asyncio.run")
        mock_logger = mocker.patch("autodoc_mcp.main.logger")

        mock_run.side_effect = Exception("Server error")

        with pytest.raises(Exception, match="Server error"):
            main()

        mock_logger.error.assert_called_with("Server failed", error="Server error")
