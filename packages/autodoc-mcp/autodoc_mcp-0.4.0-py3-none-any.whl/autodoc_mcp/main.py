"""FastMCP server entry point for AutoDocs MCP Server."""

import asyncio
import signal

# Configure structured logging to use stderr (required for MCP stdio protocol)
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import structlog
from fastmcp import FastMCP

from .config import get_config
from .core.cache_manager import FileCacheManager
from .core.context_fetcher import ConcurrentContextFetcher, create_context_fetcher
from .core.dependency_parser import PyProjectParser
from .core.doc_fetcher import PyPIDocumentationFetcher
from .core.error_formatter import ErrorFormatter, ResponseFormatter
from .core.version_resolver import VersionResolver
from .exceptions import AutoDocsError, ProjectParsingError
from .security import InputValidator

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.WriteLoggerFactory(file=sys.stderr),
    wrapper_class=structlog.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP("AutoDocs MCP Server 🚀")

# Global services (initialized in main)
parser: PyProjectParser | None = None
cache_manager: FileCacheManager | None = None
version_resolver: VersionResolver | None = None
context_fetcher: ConcurrentContextFetcher | None = None


class GracefulShutdown:
    """Handle graceful shutdown of the MCP server."""

    def __init__(self) -> None:
        self.shutdown_event = asyncio.Event()
        self.active_requests = 0
        self.max_shutdown_wait = 30.0  # seconds

    def register_signals(self) -> None:
        """Register signal handlers for graceful shutdown."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.shutdown_event.set()

    @asynccontextmanager
    async def request_context(self) -> Any:
        """Context manager to track active requests."""
        self.active_requests += 1
        try:
            yield
        finally:
            self.active_requests -= 1

    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal and cleanup."""
        await self.shutdown_event.wait()

        logger.info("Shutting down gracefully...")

        # Wait for active requests to complete
        start_time = asyncio.get_event_loop().time()
        while self.active_requests > 0:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.max_shutdown_wait:
                logger.warning(
                    f"Forcing shutdown after {elapsed}s with {self.active_requests} active requests"
                )
                break

            logger.info(
                f"Waiting for {self.active_requests} active requests to complete"
            )
            await asyncio.sleep(0.5)

        # Cleanup resources
        await self._cleanup_resources()

    async def _cleanup_resources(self) -> None:
        """Cleanup application resources."""
        from .core.network_resilience import ConnectionPoolManager

        # Close HTTP client connections
        pool_manager = ConnectionPoolManager()
        await pool_manager.close_all()

        # Flush any pending cache writes
        if cache_manager:
            # Add any pending cache operations cleanup if needed
            pass

        logger.info("Graceful shutdown completed")


@mcp.tool
async def scan_dependencies(project_path: str | None = None) -> dict[str, Any]:
    """
    Scan project dependencies from pyproject.toml

    Args:
        project_path: Path to project directory (defaults to current directory)

    Returns:
        JSON with dependency specifications and project metadata
    """
    from .observability import get_metrics_collector, track_request

    async with track_request("scan_dependencies") as metrics:
        if parser is None:
            get_metrics_collector().finish_request(
                metrics.request_id,
                success=False,
                error_type="ServiceNotInitialized",
            )
            return {
                "success": False,
                "error": {
                    "message": "Parser not initialized",
                    "suggestion": "Try again or restart the MCP server",
                    "severity": "critical",
                    "code": "service_not_initialized",
                    "recoverable": False,
                },
            }

        try:
            # Validate project path if provided
            if project_path is not None:
                path = InputValidator.validate_project_path(project_path)
            else:
                path = Path.cwd()
            logger.info("Scanning dependencies", project_path=str(path))

            result = await parser.parse_project(path)

            # Record successful metrics
            get_metrics_collector().finish_request(
                metrics.request_id,
                success=True,
                dependency_count=result.successful_deps,
            )

            # Use ResponseFormatter for consistent error formatting
            return ResponseFormatter.format_scan_response(result)

        except ProjectParsingError as e:
            formatted_error = ErrorFormatter.format_exception(e)
            get_metrics_collector().finish_request(
                metrics.request_id,
                success=False,
                error_type="ProjectParsingError",
            )
            return {
                "success": False,
                "error": {
                    "message": formatted_error.message,
                    "suggestion": formatted_error.suggestion,
                    "severity": formatted_error.severity.value,
                    "code": formatted_error.error_code,
                    "recoverable": formatted_error.recoverable,
                },
            }
        except Exception as e:
            formatted_error = ErrorFormatter.format_exception(e)
            get_metrics_collector().finish_request(
                metrics.request_id,
                success=False,
                error_type=type(e).__name__,
            )
            return {
                "success": False,
                "error": {
                    "message": formatted_error.message,
                    "suggestion": formatted_error.suggestion,
                    "severity": formatted_error.severity.value,
                    "code": formatted_error.error_code,
                    "recoverable": formatted_error.recoverable,
                },
            }


@mcp.tool
async def get_package_docs(
    package_name: str, version_constraint: str | None = None, query: str | None = None
) -> dict[str, Any]:
    """
    Retrieve formatted documentation for a package with version-based caching.

    This is the legacy single-package documentation tool. For rich context with
    dependencies, use get_package_docs_with_context instead.

    Args:
        package_name: Name of the package to fetch documentation for
        version_constraint: Version constraint from dependency scanning
        query: Optional query to filter documentation sections

    Returns:
        Formatted documentation with package metadata
    """
    from .observability import get_metrics_collector, track_request

    async with track_request("get_package_docs") as metrics:
        if cache_manager is None or version_resolver is None:
            get_metrics_collector().finish_request(
                metrics.request_id,
                success=False,
                error_type="ServiceNotInitialized",
                package_name=package_name,
            )
            return {
                "success": False,
                "error": {
                    "message": "Services not initialized",
                    "suggestion": "Try again or restart the MCP server",
                    "severity": "critical",
                    "code": "service_not_initialized",
                    "recoverable": False,
                },
            }

        try:
            # Validate inputs
            validated_package_name = InputValidator.validate_package_name(package_name)
            if version_constraint is not None:
                validated_constraint = InputValidator.validate_version_constraint(
                    version_constraint
                )
            else:
                validated_constraint = None

            logger.info(
                "Fetching package docs",
                package=validated_package_name,
                constraint=validated_constraint,
                query=query,
            )

            # Step 1: Resolve to specific version
            resolved_version = await version_resolver.resolve_version(
                validated_package_name, validated_constraint
            )

            # Step 2: Check version-specific cache
            cache_key = version_resolver.generate_cache_key(
                validated_package_name, resolved_version
            )
            cached_entry = await cache_manager.get(cache_key)

            if cached_entry:
                logger.info(
                    "Version-specific cache hit",
                    package=validated_package_name,
                    version=resolved_version,
                    constraint=version_constraint,
                )
                package_info = cached_entry.data
                from_cache = True
            else:
                logger.info(
                    "Fetching fresh package info",
                    package=validated_package_name,
                    version=resolved_version,
                )

                async with PyPIDocumentationFetcher() as fetcher:
                    package_info = await fetcher.fetch_package_info(
                        validated_package_name
                    )
                    await cache_manager.set(cache_key, package_info)
                from_cache = False

            # Step 3: Format documentation
            async with PyPIDocumentationFetcher() as fetcher:
                formatted_docs = fetcher.format_documentation(package_info, query)

            # Record successful metrics
            get_metrics_collector().finish_request(
                metrics.request_id,
                success=True,
                cache_hit=from_cache,
                package_name=validated_package_name,
            )

            return {
                "success": True,
                "package_name": package_info.name,
                "version": package_info.version,
                "resolved_version": resolved_version,
                "version_constraint": version_constraint,
                "documentation": formatted_docs,
                "from_cache": from_cache,
                "cache_key": cache_key,
                "query_applied": query is not None,
            }

        except AutoDocsError as e:
            formatted_error = ErrorFormatter.format_exception(
                e, {"package": validated_package_name}
            )
            logger.error(
                "Documentation fetch failed",
                package=validated_package_name,
                error=str(e),
                error_type=type(e).__name__,
            )
            get_metrics_collector().finish_request(
                metrics.request_id,
                success=False,
                error_type="AutoDocsError",
                package_name=package_name,
            )
            return {
                "success": False,
                "error": {
                    "message": formatted_error.message,
                    "suggestion": formatted_error.suggestion,
                    "severity": formatted_error.severity.value,
                    "code": formatted_error.error_code,
                    "recoverable": formatted_error.recoverable,
                },
            }
        except Exception as e:
            formatted_error = ErrorFormatter.format_exception(
                e, {"package": validated_package_name}
            )
            logger.error("Unexpected error during documentation fetch", error=str(e))
            get_metrics_collector().finish_request(
                metrics.request_id,
                success=False,
                error_type=type(e).__name__,
                package_name=package_name,
            )
            return {
                "success": False,
                "error": {
                    "message": formatted_error.message,
                    "suggestion": formatted_error.suggestion,
                    "severity": formatted_error.severity.value,
                    "code": formatted_error.error_code,
                    "recoverable": formatted_error.recoverable,
                },
            }


@mcp.tool
async def get_package_docs_with_context(
    package_name: str,
    version_constraint: str | None = None,
    include_dependencies: bool = True,
    context_scope: str = "smart",
    max_dependencies: int | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """
    Retrieve comprehensive documentation context including dependencies.

    This is the main Phase 4 feature providing rich AI context with both the
    requested package and its most relevant dependencies.

    Args:
        package_name: Primary package name to document
        version_constraint: Version constraint for primary package
        include_dependencies: Whether to include dependency context (default: True)
        context_scope: Context scope - "primary_only", "runtime", or "smart" (default: "smart")
        max_dependencies: Maximum dependencies to include (default: from config)
        max_tokens: Maximum token budget for context (default: from config)

    Returns:
        Rich documentation context with primary package and dependencies
    """
    from .observability import get_metrics_collector, track_request

    async with track_request("get_package_docs_with_context") as metrics:
        if context_fetcher is None:
            get_metrics_collector().finish_request(
                metrics.request_id,
                success=False,
                error_type="InitializationError",
                package_name=package_name,
            )
            return {
                "success": False,
                "error": {
                    "type": "InitializationError",
                    "message": "Context fetcher not initialized",
                },
            }

    try:
        # Validate inputs
        validated_package_name = InputValidator.validate_package_name(package_name)
        if version_constraint is not None:
            validated_constraint = InputValidator.validate_version_constraint(
                version_constraint
            )
        else:
            validated_constraint = None

        logger.info(
            "Fetching package context",
            package=validated_package_name,
            constraint=validated_constraint,
            include_deps=include_dependencies,
            scope=context_scope,
        )

        # Fetch comprehensive context
        context, performance_metrics = await context_fetcher.fetch_package_context(
            package_name=validated_package_name,
            version_constraint=validated_constraint,
            include_dependencies=include_dependencies,
            context_scope=context_scope,
            max_dependencies=max_dependencies,
            max_tokens=max_tokens,
        )

        # Convert to serializable format
        context_data = {
            "primary_package": context.primary_package.model_dump(),
            "runtime_dependencies": [
                dep.model_dump() for dep in context.runtime_dependencies
            ],
            "dev_dependencies": [dep.model_dump() for dep in context.dev_dependencies],
            "context_scope": context.context_scope,
            "total_packages": context.total_packages,
            "truncated_packages": context.truncated_packages,
            "token_estimate": context.token_estimate,
        }

        # Record successful metrics
        cache_hit_rate = performance_metrics.get("cache_hits", 0) / max(
            1,
            performance_metrics.get("cache_hits", 0)
            + performance_metrics.get("cache_misses", 1),
        )
        get_metrics_collector().finish_request(
            metrics.request_id,
            success=True,
            cache_hit=(cache_hit_rate > 0.5),
            package_name=validated_package_name,
            dependency_count=context.total_packages - 1,  # Exclude primary package
        )

        return {
            "success": True,
            "context": context_data,
            "performance": performance_metrics,
        }

    except AutoDocsError as e:
        logger.error(
            "Context fetch failed",
            package=validated_package_name,
            error=str(e),
            error_type=type(e).__name__,
        )
        get_metrics_collector().finish_request(
            metrics.request_id,
            success=False,
            error_type="AutoDocsError",
            package_name=package_name,
        )
        return {
            "success": False,
            "error": {"type": type(e).__name__, "message": str(e)},
        }
    except Exception as e:
        formatted_error = ErrorFormatter.format_exception(
            e, {"package": validated_package_name}
        )
        logger.error("Unexpected error during context fetch", error=str(e))
        get_metrics_collector().finish_request(
            metrics.request_id,
            success=False,
            error_type=type(e).__name__,
            package_name=package_name,
        )
        return {
            "success": False,
            "error": {
                "message": formatted_error.message,
                "suggestion": formatted_error.suggestion,
                "severity": formatted_error.severity.value,
                "code": formatted_error.error_code,
                "recoverable": formatted_error.recoverable,
            },
        }


@mcp.tool
async def refresh_cache() -> dict[str, Any]:
    """
    Refresh the local documentation cache.

    Returns:
        Statistics about cache refresh operation
    """
    if cache_manager is None:
        return {
            "success": False,
            "error": {
                "message": "Cache manager not initialized",
                "suggestion": "Try again or restart the MCP server",
                "severity": "critical",
                "code": "service_not_initialized",
                "recoverable": False,
            },
        }

    try:
        logger.info("Starting cache refresh")

        # Get current cache stats
        initial_stats = await cache_manager.get_cache_stats()

        # Clear the entire cache
        await cache_manager.invalidate()

        # Get final stats
        final_stats = await cache_manager.get_cache_stats()

        logger.info(
            "Cache refresh completed",
            cleared_entries=initial_stats.get("total_entries", 0),
        )

        return {
            "success": True,
            "cleared_entries": initial_stats.get("total_entries", 0),
            "freed_bytes": initial_stats.get("total_size_bytes", 0),
            "final_entries": final_stats.get("total_entries", 0),
        }

    except AutoDocsError as e:
        formatted_error = ErrorFormatter.format_exception(e)
        logger.error("Cache refresh failed", error=str(e))
        return {
            "success": False,
            "error": {
                "message": formatted_error.message,
                "suggestion": formatted_error.suggestion,
                "severity": formatted_error.severity.value,
                "code": formatted_error.error_code,
                "recoverable": formatted_error.recoverable,
            },
        }


@mcp.tool
async def get_cache_stats() -> dict[str, Any]:
    """
    Get statistics about the documentation cache.

    Returns:
        Cache statistics and information
    """
    if cache_manager is None:
        return {
            "success": False,
            "error": {
                "message": "Cache manager not initialized",
                "suggestion": "Try again or restart the MCP server",
                "severity": "critical",
                "code": "service_not_initialized",
                "recoverable": False,
            },
        }

    try:
        stats = await cache_manager.get_cache_stats()
        cached_packages = await cache_manager.list_cached_packages()

        return {
            "success": True,
            "cache_stats": stats,
            "cached_packages": cached_packages,
            "total_packages": len(cached_packages),
        }

    except Exception as e:
        formatted_error = ErrorFormatter.format_exception(
            e, {"operation": "get_cache_stats"}
        )
        logger.error("Failed to get cache stats", error=str(e))
        return {
            "success": False,
            "error": {
                "message": formatted_error.message,
                "suggestion": formatted_error.suggestion,
                "severity": formatted_error.severity.value,
                "code": formatted_error.error_code,
                "recoverable": formatted_error.recoverable,
            },
        }


@mcp.tool
async def health_check() -> dict[str, Any]:
    """
    Get system health status for monitoring and load balancer checks.

    Returns:
        Comprehensive health status of all system components
    """
    from .health import HealthChecker

    health_checker = HealthChecker()
    return await health_checker.get_overall_health()


@mcp.tool
async def ready_check() -> dict[str, Any]:
    """
    Kubernetes-style readiness check for deployment orchestration.

    Returns:
        Simple ready/not-ready status
    """
    from .health import HealthChecker

    health_checker = HealthChecker()
    return await health_checker.get_readiness_status()


@mcp.tool
async def get_metrics() -> dict[str, Any]:
    """
    Get system performance metrics for monitoring.

    Returns:
        Performance statistics and metrics
    """
    from .observability import get_metrics_collector

    metrics_collector = get_metrics_collector()
    return {
        "success": True,
        "performance": metrics_collector.get_stats(),
        "health_metrics": metrics_collector.get_health_metrics(),
        "timestamp": time.time(),
    }


async def initialize_services() -> None:
    """Initialize global services with new components."""
    global parser, cache_manager, version_resolver, context_fetcher

    config = get_config()

    # Validate production readiness
    production_issues = config.validate_production_readiness()
    if production_issues:
        if config.environment == "production":
            # Fail startup in production if there are issues
            raise ValueError(
                f"Production configuration issues: {'; '.join(production_issues)}"
            )
        else:
            # Just warn in other environments
            logger.warning(
                "Configuration issues detected (non-production environment)",
                issues=production_issues,
                environment=config.environment,
            )

    logger.info(
        "Initializing services",
        cache_dir=str(config.cache_dir),
        environment=config.environment,
        debug_mode=config.debug_mode,
        max_concurrent=config.max_concurrent,
    )

    parser = PyProjectParser()
    cache_manager = FileCacheManager(config.cache_dir)
    version_resolver = VersionResolver()

    await cache_manager.initialize()

    # Initialize Phase 4 context fetcher
    context_fetcher = await create_context_fetcher(cache_manager)

    logger.info("Services initialized successfully", phase_4_enabled=True)


async def async_main() -> None:
    """Async main function with graceful shutdown."""
    shutdown_handler = GracefulShutdown()
    shutdown_handler.register_signals()

    try:
        await initialize_services()
        logger.info("Starting AutoDocs MCP Server")

        # Start server and wait for shutdown
        server_task = asyncio.create_task(run_mcp_server())
        shutdown_task = asyncio.create_task(shutdown_handler.wait_for_shutdown())

        await asyncio.wait(
            [server_task, shutdown_task], return_when=asyncio.FIRST_COMPLETED
        )

    except Exception as e:
        logger.error("Server startup failed", error=str(e))
        raise
    finally:
        await shutdown_handler._cleanup_resources()


async def run_mcp_server() -> None:
    """Run the MCP server in async mode."""
    # Since FastMCP doesn't have native async support, we need to run it in a thread
    import threading

    server_thread = threading.Thread(target=mcp.run, daemon=True)
    server_thread.start()

    # Keep the async task alive while server is running
    while server_thread.is_alive():
        await asyncio.sleep(1.0)


def main() -> None:
    """Entry point for the MCP server."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error("Server failed", error=str(e))
        raise


if __name__ == "__main__":
    main()
