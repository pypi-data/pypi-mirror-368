"""FastMCP server entry point for AutoDocs MCP Server."""

import asyncio

# Configure structured logging to use stderr (required for MCP stdio protocol)
import sys
from pathlib import Path
from typing import Any

import structlog
from fastmcp import FastMCP

from .config import get_config
from .core.cache_manager import FileCacheManager
from .core.dependency_parser import PyProjectParser
from .core.doc_fetcher import PyPIDocumentationFetcher
from .core.version_resolver import VersionResolver
from .exceptions import AutoDocsError

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


@mcp.tool
async def scan_dependencies(project_path: str | None = None) -> dict[str, Any]:
    """
    Scan project dependencies from pyproject.toml

    Args:
        project_path: Path to project directory (defaults to current directory)

    Returns:
        JSON with dependency specifications and project metadata
    """
    if parser is None:
        return {
            "success": False,
            "error": {
                "type": "InitializationError",
                "message": "Parser not initialized",
            },
        }

    try:
        path = Path(project_path) if project_path else Path.cwd()
        logger.info("Scanning dependencies", project_path=str(path))

        result = await parser.parse_project(path)

        return {
            "success": True,
            "partial_success": result.partial_success,
            "project_path": str(result.project_path),
            "project_name": result.project_name,
            "dependencies": [
                {
                    "name": dep.name,
                    "version_constraint": dep.version_constraint,
                    "extras": dep.extras,
                    "source": dep.source,
                }
                for dep in result.dependencies
            ],
            "scan_timestamp": result.scan_timestamp.isoformat(),
            "successful_deps": result.successful_deps,
            "total_dependencies": len(result.dependencies),
            "failed_deps": result.failed_deps,
            "warnings": result.warnings,
            "errors": result.errors,
        }

    except AutoDocsError as e:
        logger.error(
            "Dependency scanning failed", error=str(e), error_type=type(e).__name__
        )
        return {
            "success": False,
            "error": {"type": type(e).__name__, "message": str(e)},
        }
    except Exception as e:
        logger.error("Unexpected error during dependency scanning", error=str(e))
        return {
            "success": False,
            "error": {
                "type": "UnexpectedError",
                "message": f"An unexpected error occurred: {str(e)}",
            },
        }


@mcp.tool
async def get_package_docs(
    package_name: str, version_constraint: str | None = None, query: str | None = None
) -> dict[str, Any]:
    """
    Retrieve formatted documentation for a package with version-based caching.

    Args:
        package_name: Name of the package to fetch documentation for
        version_constraint: Version constraint from dependency scanning
        query: Optional query to filter documentation sections

    Returns:
        Formatted documentation with package metadata
    """
    if cache_manager is None or version_resolver is None:
        return {
            "success": False,
            "error": {
                "type": "InitializationError",
                "message": "Services not initialized",
            },
        }

    try:
        logger.info(
            "Fetching package docs",
            package=package_name,
            constraint=version_constraint,
            query=query,
        )

        # Step 1: Resolve to specific version
        resolved_version = await version_resolver.resolve_version(
            package_name, version_constraint
        )

        # Step 2: Check version-specific cache
        cache_key = version_resolver.generate_cache_key(package_name, resolved_version)
        cached_entry = await cache_manager.get(cache_key)

        if cached_entry:
            logger.info(
                "Version-specific cache hit",
                package=package_name,
                version=resolved_version,
                constraint=version_constraint,
            )
            package_info = cached_entry.data
            from_cache = True
        else:
            logger.info(
                "Fetching fresh package info",
                package=package_name,
                version=resolved_version,
            )

            async with PyPIDocumentationFetcher() as fetcher:
                package_info = await fetcher.fetch_package_info(package_name)
                await cache_manager.set(cache_key, package_info)
            from_cache = False

        # Step 3: Format documentation
        async with PyPIDocumentationFetcher() as fetcher:
            formatted_docs = fetcher.format_documentation(package_info, query)

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
        logger.error(
            "Documentation fetch failed",
            package=package_name,
            error=str(e),
            error_type=type(e).__name__,
        )
        return {
            "success": False,
            "error": {"type": type(e).__name__, "message": str(e)},
        }
    except Exception as e:
        logger.error("Unexpected error during documentation fetch", error=str(e))
        return {
            "success": False,
            "error": {
                "type": "UnexpectedError",
                "message": f"An unexpected error occurred: {str(e)}",
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
                "type": "InitializationError",
                "message": "Cache manager not initialized",
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
        logger.error("Cache refresh failed", error=str(e))
        return {
            "success": False,
            "error": {"type": type(e).__name__, "message": str(e)},
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
                "type": "InitializationError",
                "message": "Cache manager not initialized",
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
        logger.error("Failed to get cache stats", error=str(e))
        return {
            "success": False,
            "error": {
                "type": "CacheError",
                "message": f"Failed to get cache stats: {str(e)}",
            },
        }


async def initialize_services() -> None:
    """Initialize global services with new components."""
    global parser, cache_manager, version_resolver

    config = get_config()
    logger.info("Initializing services", cache_dir=str(config.cache_dir))

    parser = PyProjectParser()
    cache_manager = FileCacheManager(config.cache_dir)
    version_resolver = VersionResolver()

    await cache_manager.initialize()

    logger.info("Services initialized successfully")


def main() -> None:
    """Entry point for the MCP server."""
    try:
        # Initialize services
        asyncio.run(initialize_services())

        logger.info("Starting AutoDocs MCP Server")

        # Run the server
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error("Server startup failed", error=str(e))
        raise


if __name__ == "__main__":
    main()
