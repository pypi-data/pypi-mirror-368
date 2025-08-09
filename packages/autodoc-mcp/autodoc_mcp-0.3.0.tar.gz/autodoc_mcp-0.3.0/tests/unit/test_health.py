"""Tests for health check system."""

from autodocs_mcp.health import HealthCheck, HealthChecker, HealthStatus


class TestHealthCheck:
    """Test HealthCheck dataclass."""

    def test_health_check_creation(self):
        """Test creating a health check."""
        check = HealthCheck(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="All good",
            response_time_ms=150.0,
            timestamp=1234567890.0,
        )

        assert check.name == "test_check"
        assert check.status == HealthStatus.HEALTHY
        assert check.message == "All good"
        assert check.response_time_ms == 150.0
        assert check.timestamp == 1234567890.0


class TestHealthChecker:
    """Test HealthChecker functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.health_checker = HealthChecker()

    async def test_check_cache_manager_not_initialized(self, mocker):
        """Test cache manager health when not initialized."""
        mocker.patch("autodocs_mcp.main.cache_manager", None)
        result = await self.health_checker.check_cache_manager()

        assert result.name == "cache_manager"
        assert result.status == HealthStatus.UNHEALTHY
        assert "not initialized" in result.message.lower()

    async def test_check_cache_manager_healthy(self, mocker):
        """Test cache manager health when working."""
        mock_cache_manager = mocker.AsyncMock()
        mock_cache_manager.get_cache_stats.return_value = {"total_entries": 5}
        mock_cache_manager.invalidate.return_value = None

        mocker.patch("autodocs_mcp.main.cache_manager", mock_cache_manager)
        result = await self.health_checker.check_cache_manager()

        assert result.name == "cache_manager"
        assert result.status == HealthStatus.HEALTHY
        assert "working" in result.message.lower()
        assert result.response_time_ms > 0

    async def test_check_cache_manager_error(self, mocker):
        """Test cache manager health when erroring."""
        mock_cache_manager = mocker.AsyncMock()
        mock_cache_manager.get_cache_stats.side_effect = Exception("Cache error")

        mocker.patch("autodocs_mcp.main.cache_manager", mock_cache_manager)
        result = await self.health_checker.check_cache_manager()

        assert result.name == "cache_manager"
        assert result.status == HealthStatus.UNHEALTHY
        assert "Cache error" in result.message

    async def test_check_pypi_connectivity_healthy(self, mocker):
        """Test PyPI connectivity when working."""
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_with_retry.return_value = {}

        mock_class = mocker.patch(
            "autodocs_mcp.core.network_resilience.NetworkResilientClient"
        )
        mock_class.return_value = mock_client

        result = await self.health_checker.check_pypi_connectivity()

        assert result.name == "pypi_connectivity"
        assert result.status == HealthStatus.HEALTHY
        assert "accessible" in result.message.lower()

    async def test_check_pypi_connectivity_404_is_healthy(self, mocker):
        """Test that 404 from PyPI is considered healthy (PyPI is working)."""
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_with_retry.side_effect = Exception("404 not found")

        mock_class = mocker.patch(
            "autodocs_mcp.core.network_resilience.NetworkResilientClient"
        )
        mock_class.return_value = mock_client

        result = await self.health_checker.check_pypi_connectivity()

        assert result.name == "pypi_connectivity"
        assert result.status == HealthStatus.HEALTHY
        assert "expected error" in result.message

    async def test_check_pypi_connectivity_network_error(self, mocker):
        """Test PyPI connectivity with network error."""
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_with_retry.side_effect = Exception("Connection timeout")

        mock_class = mocker.patch(
            "autodocs_mcp.core.network_resilience.NetworkResilientClient"
        )
        mock_class.return_value = mock_client

        result = await self.health_checker.check_pypi_connectivity()

        assert result.name == "pypi_connectivity"
        assert result.status == HealthStatus.UNHEALTHY
        assert "Connection timeout" in result.message

    async def test_check_dependencies_not_initialized(self, mocker):
        """Test dependency parser when not initialized."""
        mocker.patch("autodocs_mcp.main.parser", None)
        result = await self.health_checker.check_dependencies()

        assert result.name == "dependency_parser"
        assert result.status == HealthStatus.UNHEALTHY
        assert "not initialized" in result.message.lower()

    async def test_check_dependencies_healthy(self, mocker):
        """Test dependency parser when working."""
        mock_parser = mocker.AsyncMock()
        mock_result = mocker.MagicMock()
        mock_result.successful_deps = 1
        mock_parser.parse_project.return_value = mock_result

        mocker.patch("autodocs_mcp.main.parser", mock_parser)
        result = await self.health_checker.check_dependencies()

        assert result.name == "dependency_parser"
        assert result.status == HealthStatus.HEALTHY
        assert "found 1 dependencies" in result.message

    async def test_check_dependencies_no_deps_found(self, mocker):
        """Test dependency parser when no dependencies found."""
        mock_parser = mocker.AsyncMock()
        mock_result = mocker.MagicMock()
        mock_result.successful_deps = 0
        mock_parser.parse_project.return_value = mock_result

        mocker.patch("autodocs_mcp.main.parser", mock_parser)
        result = await self.health_checker.check_dependencies()

        assert result.name == "dependency_parser"
        assert result.status == HealthStatus.DEGRADED
        assert "found no dependencies" in result.message

    async def test_check_dependencies_error(self, mocker):
        """Test dependency parser when erroring."""
        mock_parser = mocker.AsyncMock()
        mock_parser.parse_project.side_effect = Exception("Parse error")

        mocker.patch("autodocs_mcp.main.parser", mock_parser)
        result = await self.health_checker.check_dependencies()

        assert result.name == "dependency_parser"
        assert result.status == HealthStatus.UNHEALTHY
        assert "Parse error" in result.message

    async def test_check_context_fetcher_not_initialized(self, mocker):
        """Test context fetcher when not initialized."""
        mocker.patch("autodocs_mcp.main.context_fetcher", None)
        result = await self.health_checker.check_context_fetcher()

        assert result.name == "context_fetcher"
        assert result.status == HealthStatus.UNHEALTHY
        assert "not initialized" in result.message.lower()

    async def test_check_context_fetcher_healthy(self, mocker):
        """Test context fetcher when healthy."""
        mock_context_fetcher = mocker.MagicMock()
        mock_context_fetcher.cache_manager = mocker.MagicMock()
        mock_context_fetcher.dependency_resolver = mocker.MagicMock()
        mock_context_fetcher.formatter = mocker.MagicMock()

        mocker.patch("autodocs_mcp.main.context_fetcher", mock_context_fetcher)
        result = await self.health_checker.check_context_fetcher()

        assert result.name == "context_fetcher"
        assert result.status == HealthStatus.HEALTHY
        assert "all components" in result.message

    async def test_check_context_fetcher_partially_initialized(self, mocker):
        """Test context fetcher when partially initialized."""
        mock_context_fetcher = mocker.MagicMock()
        mock_context_fetcher.cache_manager = None
        mock_context_fetcher.dependency_resolver = mocker.MagicMock()
        mock_context_fetcher.formatter = mocker.MagicMock()

        mocker.patch("autodocs_mcp.main.context_fetcher", mock_context_fetcher)
        result = await self.health_checker.check_context_fetcher()

        assert result.name == "context_fetcher"
        assert result.status == HealthStatus.DEGRADED
        assert "partially initialized" in result.message

    async def test_get_overall_health_all_healthy(self, mocker):
        """Test overall health when all checks are healthy."""
        mock_cache = mocker.patch.object(self.health_checker, "check_cache_manager")
        mock_pypi = mocker.patch.object(self.health_checker, "check_pypi_connectivity")
        mock_deps = mocker.patch.object(self.health_checker, "check_dependencies")
        mock_context = mocker.patch.object(self.health_checker, "check_context_fetcher")

        mock_cache.return_value = HealthCheck(
            "cache", HealthStatus.HEALTHY, "ok", 10.0, 123.0
        )
        mock_pypi.return_value = HealthCheck(
            "pypi", HealthStatus.HEALTHY, "ok", 20.0, 124.0
        )
        mock_deps.return_value = HealthCheck(
            "deps", HealthStatus.HEALTHY, "ok", 15.0, 125.0
        )
        mock_context.return_value = HealthCheck(
            "context", HealthStatus.HEALTHY, "ok", 5.0, 126.0
        )

        result = await self.health_checker.get_overall_health()

        assert result["status"] == "healthy"
        assert result["summary"]["healthy"] == 4
        assert result["summary"]["degraded"] == 0
        assert result["summary"]["unhealthy"] == 0
        assert result["summary"]["total"] == 4

    async def test_get_overall_health_with_degraded(self, mocker):
        """Test overall health with degraded components."""
        mock_cache = mocker.patch.object(self.health_checker, "check_cache_manager")
        mock_pypi = mocker.patch.object(self.health_checker, "check_pypi_connectivity")
        mock_deps = mocker.patch.object(self.health_checker, "check_dependencies")
        mock_context = mocker.patch.object(self.health_checker, "check_context_fetcher")

        mock_cache.return_value = HealthCheck(
            "cache", HealthStatus.HEALTHY, "ok", 10.0, 123.0
        )
        mock_pypi.return_value = HealthCheck(
            "pypi", HealthStatus.DEGRADED, "slow", 100.0, 124.0
        )
        mock_deps.return_value = HealthCheck(
            "deps", HealthStatus.HEALTHY, "ok", 15.0, 125.0
        )
        mock_context.return_value = HealthCheck(
            "context", HealthStatus.HEALTHY, "ok", 5.0, 126.0
        )

        result = await self.health_checker.get_overall_health()

        assert result["status"] == "degraded"
        assert result["summary"]["healthy"] == 3
        assert result["summary"]["degraded"] == 1
        assert result["summary"]["unhealthy"] == 0

    async def test_get_overall_health_with_unhealthy(self, mocker):
        """Test overall health with unhealthy components."""
        mock_cache = mocker.patch.object(self.health_checker, "check_cache_manager")
        mock_pypi = mocker.patch.object(self.health_checker, "check_pypi_connectivity")
        mock_deps = mocker.patch.object(self.health_checker, "check_dependencies")
        mock_context = mocker.patch.object(self.health_checker, "check_context_fetcher")

        mock_cache.return_value = HealthCheck(
            "cache", HealthStatus.UNHEALTHY, "down", 0.0, 123.0
        )
        mock_pypi.return_value = HealthCheck(
            "pypi", HealthStatus.HEALTHY, "ok", 20.0, 124.0
        )
        mock_deps.return_value = HealthCheck(
            "deps", HealthStatus.HEALTHY, "ok", 15.0, 125.0
        )
        mock_context.return_value = HealthCheck(
            "context", HealthStatus.HEALTHY, "ok", 5.0, 126.0
        )

        result = await self.health_checker.get_overall_health()

        assert result["status"] == "unhealthy"
        assert result["summary"]["healthy"] == 3
        assert result["summary"]["degraded"] == 0
        assert result["summary"]["unhealthy"] == 1

    async def test_get_overall_health_with_exception(self, mocker):
        """Test overall health handling of exceptions."""
        mock_cache = mocker.patch.object(self.health_checker, "check_cache_manager")
        mock_pypi = mocker.patch.object(self.health_checker, "check_pypi_connectivity")
        mock_deps = mocker.patch.object(self.health_checker, "check_dependencies")
        mock_context = mocker.patch.object(self.health_checker, "check_context_fetcher")

        mock_cache.side_effect = Exception("Check failed")
        mock_pypi.return_value = HealthCheck(
            "pypi", HealthStatus.HEALTHY, "ok", 20.0, 124.0
        )
        mock_deps.return_value = HealthCheck(
            "deps", HealthStatus.HEALTHY, "ok", 15.0, 125.0
        )
        mock_context.return_value = HealthCheck(
            "context", HealthStatus.HEALTHY, "ok", 5.0, 126.0
        )

        result = await self.health_checker.get_overall_health()

        assert result["status"] == "unhealthy"
        assert result["summary"]["healthy"] == 3
        assert result["summary"]["unhealthy"] == 1
        assert "unknown_error" in result["checks"]

    async def test_get_readiness_status_ready(self, mocker):
        """Test readiness check when all services ready."""
        with (
            mocker.patch("autodocs_mcp.main.parser", mocker.MagicMock()),
            mocker.patch("autodocs_mcp.main.cache_manager", mocker.MagicMock()),
            mocker.patch("autodocs_mcp.main.version_resolver", mocker.MagicMock()),
            mocker.patch("autodocs_mcp.main.context_fetcher", mocker.MagicMock()),
        ):
            result = await self.health_checker.get_readiness_status()

        assert result["ready"] is True
        assert "timestamp" in result

    async def test_get_readiness_status_not_ready(self, mocker):
        """Test readiness check when services not ready."""
        mocker.patch("autodocs_mcp.main.parser", None)
        mocker.patch("autodocs_mcp.main.cache_manager", mocker.MagicMock())
        mocker.patch("autodocs_mcp.main.version_resolver", mocker.MagicMock())
        mocker.patch("autodocs_mcp.main.context_fetcher", mocker.MagicMock())

        result = await self.health_checker.get_readiness_status()

        assert result["ready"] is False
        assert "parser" in result["reason"]
        assert "timestamp" in result

    async def test_get_readiness_status_exception(self, mocker):
        """Test readiness check handling exceptions."""
        mocker.patch("autodocs_mcp.main.parser", None)
        result = await self.health_checker.get_readiness_status()

        assert result["ready"] is False
        assert "Services not initialized" in result["reason"]
        assert "parser" in result["reason"]
