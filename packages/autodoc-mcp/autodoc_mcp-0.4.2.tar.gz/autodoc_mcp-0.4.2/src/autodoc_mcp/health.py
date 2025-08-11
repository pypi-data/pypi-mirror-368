"""Health check and monitoring system for AutoDocs MCP Server."""

import asyncio
import contextlib
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from structlog import get_logger

from .config import get_config

logger = get_logger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """Individual health check result."""

    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: float


class HealthChecker:
    """Comprehensive health checking for all system components."""

    def __init__(self) -> None:
        self.checks: dict[str, HealthCheck] = {}

    async def check_cache_manager(self) -> HealthCheck:
        """Check cache manager health."""
        start_time = time.time()

        try:
            # Import here to avoid circular imports
            from . import main

            if main.cache_manager is None:
                return HealthCheck(
                    name="cache_manager",
                    status=HealthStatus.UNHEALTHY,
                    message="Cache manager not initialized",
                    response_time_ms=0,
                    timestamp=time.time(),
                )

            # Test basic cache operations
            test_key = "_health_check_test"

            # Try to clean up any existing test entry
            with contextlib.suppress(Exception):
                await main.cache_manager.invalidate(test_key)

            # Test cache directory access
            cache_stats = await main.cache_manager.get_cache_stats()

            response_time = (time.time() - start_time) * 1000

            return HealthCheck(
                name="cache_manager",
                status=HealthStatus.HEALTHY,
                message=f"Cache operations working ({cache_stats.get('total_entries', 0)} entries)",
                response_time_ms=response_time,
                timestamp=time.time(),
            )

        except Exception as e:
            return HealthCheck(
                name="cache_manager",
                status=HealthStatus.UNHEALTHY,
                message=f"Cache error: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=time.time(),
            )

    async def check_pypi_connectivity(self) -> HealthCheck:
        """Check PyPI API connectivity."""
        start_time = time.time()

        try:
            from .core.network_resilience import NetworkResilientClient

            async with NetworkResilientClient() as client:
                # Test lightweight PyPI endpoint
                config = get_config()
                test_url = f"{config.pypi_base_url}/requests/json"
                await client.get_with_retry(test_url)

            response_time = (time.time() - start_time) * 1000

            return HealthCheck(
                name="pypi_connectivity",
                status=HealthStatus.HEALTHY,
                message="PyPI API accessible",
                response_time_ms=response_time,
                timestamp=time.time(),
            )

        except Exception as e:
            error_msg = str(e).lower()
            # 404 for 'requests' package would actually indicate PyPI is working
            if "not found" in error_msg or "404" in error_msg:
                status = HealthStatus.HEALTHY
                message = "PyPI API accessible (test endpoint returned expected error)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"PyPI connectivity: {str(e)}"

            return HealthCheck(
                name="pypi_connectivity",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=time.time(),
            )

    async def check_dependencies(self) -> HealthCheck:
        """Check dependency parser health."""
        start_time = time.time()

        try:
            # Import here to avoid circular imports
            from . import main

            if main.parser is None:
                return HealthCheck(
                    name="dependency_parser",
                    status=HealthStatus.UNHEALTHY,
                    message="Dependency parser not initialized",
                    response_time_ms=0,
                    timestamp=time.time(),
                )

            # Test parser with minimal valid project
            with tempfile.TemporaryDirectory() as temp_dir:
                test_project = Path(temp_dir) / "pyproject.toml"
                test_project.write_text("""
[project]
name = "health-test"
version = "1.0.0"
dependencies = ["requests>=2.0.0"]
                """)

                result = await main.parser.parse_project(Path(temp_dir))

                if result.successful_deps > 0:
                    status = HealthStatus.HEALTHY
                    message = (
                        f"Parser working, found {result.successful_deps} dependencies"
                    )
                else:
                    status = HealthStatus.DEGRADED
                    message = "Parser running but found no dependencies"

            response_time = (time.time() - start_time) * 1000

            return HealthCheck(
                name="dependency_parser",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=time.time(),
            )

        except Exception as e:
            return HealthCheck(
                name="dependency_parser",
                status=HealthStatus.UNHEALTHY,
                message=f"Parser error: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=time.time(),
            )

    async def check_context_fetcher(self) -> HealthCheck:
        """Check Phase 4 context fetcher health."""
        start_time = time.time()

        try:
            # Import here to avoid circular imports
            from . import main

            if main.context_fetcher is None:
                return HealthCheck(
                    name="context_fetcher",
                    status=HealthStatus.UNHEALTHY,
                    message="Context fetcher not initialized",
                    response_time_ms=0,
                    timestamp=time.time(),
                )

            # Basic validation that components exist
            if (
                main.context_fetcher.cache_manager is None
                or main.context_fetcher.dependency_resolver is None
                or main.context_fetcher.formatter is None
            ):
                return HealthCheck(
                    name="context_fetcher",
                    status=HealthStatus.DEGRADED,
                    message="Context fetcher partially initialized",
                    response_time_ms=(time.time() - start_time) * 1000,
                    timestamp=time.time(),
                )

            response_time = (time.time() - start_time) * 1000

            return HealthCheck(
                name="context_fetcher",
                status=HealthStatus.HEALTHY,
                message="Context fetcher initialized with all components",
                response_time_ms=response_time,
                timestamp=time.time(),
            )

        except Exception as e:
            return HealthCheck(
                name="context_fetcher",
                status=HealthStatus.UNHEALTHY,
                message=f"Context fetcher error: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=time.time(),
            )

    async def get_overall_health(self) -> dict[str, Any]:
        """Get comprehensive health status."""
        checks = await asyncio.gather(
            self.check_cache_manager(),
            self.check_pypi_connectivity(),
            self.check_dependencies(),
            self.check_context_fetcher(),
            return_exceptions=True,
        )

        health_data: dict[str, Any] = {
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {},
            "summary": {
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "total": len(checks),
            },
        }

        overall_status = HealthStatus.HEALTHY

        for check in checks:
            if isinstance(check, Exception):
                health_data["checks"]["unknown_error"] = {
                    "status": "unhealthy",
                    "message": f"Health check failed: {str(check)}",
                    "response_time_ms": 0,
                }
                overall_status = HealthStatus.UNHEALTHY
                health_data["summary"]["unhealthy"] += 1
                continue

            # At this point, check must be a HealthCheck (not Exception)
            assert isinstance(check, HealthCheck)
            health_data["checks"][check.name] = {
                "status": check.status.value,
                "message": check.message,
                "response_time_ms": check.response_time_ms,
                "timestamp": check.timestamp,
            }

            if check.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                health_data["summary"]["unhealthy"] += 1
            elif check.status == HealthStatus.DEGRADED:
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                health_data["summary"]["degraded"] += 1
            else:
                health_data["summary"]["healthy"] += 1

        health_data["status"] = overall_status.value
        return health_data

    async def get_readiness_status(self) -> dict[str, Any]:
        """Get Kubernetes-style readiness check."""
        try:
            # Import here to avoid circular imports
            from . import main

            # Quick checks for readiness
            if (
                main.parser is None
                or main.cache_manager is None
                or main.version_resolver is None
                or main.context_fetcher is None
            ):
                missing_services = []
                if main.parser is None:
                    missing_services.append("parser")
                if main.cache_manager is None:
                    missing_services.append("cache_manager")
                if main.version_resolver is None:
                    missing_services.append("version_resolver")
                if main.context_fetcher is None:
                    missing_services.append("context_fetcher")

                return {
                    "ready": False,
                    "reason": f"Services not initialized: {', '.join(missing_services)}",
                    "timestamp": time.time(),
                }

            return {"ready": True, "timestamp": time.time()}

        except Exception as e:
            return {
                "ready": False,
                "reason": f"Readiness check failed: {str(e)}",
                "timestamp": time.time(),
            }
