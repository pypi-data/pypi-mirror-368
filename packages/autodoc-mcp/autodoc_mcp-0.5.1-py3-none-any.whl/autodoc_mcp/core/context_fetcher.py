"""Concurrent context fetcher for high-performance dependency documentation."""

import asyncio
import time
from typing import Any

from structlog import get_logger

from ..config import get_config
from .cache_manager import CacheManagerInterface
from .context_formatter import (
    ContextDocumentationFormatter,
    ContextWindowManager,
    DocumentationContext,
    PackageDocumentation,
)
from .dependency_resolver import DependencyResolver
from .network_client import NetworkResilientClient

logger = get_logger(__name__)


class ConcurrentContextFetcher:
    """High-performance concurrent fetcher for documentation context."""

    def __init__(
        self,
        cache_manager: CacheManagerInterface,
        dependency_resolver: DependencyResolver,
        formatter: ContextDocumentationFormatter,
        network_client: NetworkResilientClient | None = None,
    ):
        self.cache_manager = cache_manager
        self.dependency_resolver = dependency_resolver
        self.formatter = formatter
        self.network_client = network_client
        self.config = get_config()

    async def fetch_package_context(
        self,
        package_name: str,
        version_constraint: str | None = None,
        include_dependencies: bool = True,
        context_scope: str = "smart",
        max_dependencies: int | None = None,
        max_tokens: int | None = None,
    ) -> tuple[DocumentationContext, dict[str, Any]]:
        """
        Fetch comprehensive documentation context for a package.

        Args:
            package_name: Primary package name
            version_constraint: Version constraint for primary package
            include_dependencies: Whether to include dependency context
            context_scope: Scope of context ("primary_only", "runtime", "smart")
            max_dependencies: Maximum dependencies to include
            max_tokens: Maximum token budget for context

        Returns:
            Tuple of (DocumentationContext, performance_metrics)
        """
        start_time = time.time()
        performance_metrics = {
            "primary_fetch_time": 0.0,
            "dependency_resolution_time": 0.0,
            "dependency_fetch_time": 0.0,
            "total_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "concurrent_fetches": 0,
            "failed_fetches": 0,
        }

        try:
            logger.info(
                "Starting context fetch",
                package=package_name,
                include_deps=include_dependencies,
                scope=context_scope,
            )

            # Step 1: Fetch primary package documentation
            primary_start = time.time()
            primary_info, from_cache = await self.cache_manager.resolve_and_cache(
                package_name, version_constraint
            )

            if from_cache:
                performance_metrics["cache_hits"] += 1
            else:
                performance_metrics["cache_misses"] += 1

            primary_docs = self.formatter.format_primary_package(
                primary_info, from_cache
            )
            performance_metrics["primary_fetch_time"] = time.time() - primary_start

            # Initialize context with primary package
            context = DocumentationContext(
                primary_package=primary_docs, context_scope="primary_only"
            )

            # If dependencies not requested, return early
            if not include_dependencies:
                performance_metrics["total_time"] = time.time() - start_time
                return context, performance_metrics

            # Step 2: Resolve dependency context
            resolution_start = time.time()
            max_deps = max_dependencies or (
                self.config.max_dependency_context if context_scope == "smart" else 5
            )
            max_context_tokens = max_tokens or self.config.max_context_tokens

            dependency_names = (
                await self.dependency_resolver.resolve_context_dependencies(
                    package_name=primary_info["name"],
                    version=primary_info["version"],
                    max_dependencies=max_deps,
                    max_tokens=max_context_tokens,
                )
            )

            performance_metrics["dependency_resolution_time"] = (
                time.time() - resolution_start
            )

            if not dependency_names:
                logger.info("No dependencies to fetch", package=package_name)
                performance_metrics["total_time"] = time.time() - start_time
                return context, performance_metrics

            # Step 3: Fetch dependency documentation concurrently
            dep_fetch_start = time.time()
            dependency_results = await self._fetch_dependencies_concurrently(
                dependency_names, primary_info["name"], performance_metrics
            )

            performance_metrics["dependency_fetch_time"] = time.time() - dep_fetch_start
            performance_metrics["concurrent_fetches"] = len(dependency_names)

            # Step 4: Process successful results
            successful_deps = []
            failed_deps = []

            for result in dependency_results:
                if isinstance(result, Exception):
                    failed_deps.append(str(result))
                    performance_metrics["failed_fetches"] += 1
                else:
                    successful_deps.append(result)

            # Update context with dependencies
            context.runtime_dependencies = successful_deps
            context.total_packages = 1 + len(successful_deps)

            if successful_deps:
                context.context_scope = f"with_runtime ({len(successful_deps)} deps)"

            if failed_deps:
                context.truncated_packages.extend(
                    [f"Failed: {dep}" for dep in failed_deps]
                )

            # Step 5: Apply token window management
            context = ContextWindowManager.fit_to_window(context, max_context_tokens)

            performance_metrics["total_time"] = time.time() - start_time

            logger.info(
                "Context fetch complete",
                package=package_name,
                total_packages=context.total_packages,
                total_time=performance_metrics["total_time"],
                tokens=context.token_estimate,
            )

            return context, performance_metrics

        except Exception as e:
            performance_metrics["total_time"] = time.time() - start_time
            logger.error(
                "Context fetch failed",
                package=package_name,
                error=str(e),
                total_time=performance_metrics["total_time"],
            )

            # Return minimal context with primary package only
            if "primary_docs" in locals():
                context = DocumentationContext(
                    primary_package=primary_docs,
                    context_scope="primary_only (deps_failed)",
                )
                return context, performance_metrics

            raise

    async def _fetch_dependencies_concurrently(
        self,
        dependency_names: list[str],
        primary_package_name: str,
        performance_metrics: dict[str, Any],
    ) -> list[Any]:
        """Fetch multiple dependencies concurrently with proper error handling."""

        if not dependency_names:
            return []

        # Create concurrent tasks
        tasks = []
        semaphore = asyncio.Semaphore(5)  # Limit concurrent requests

        for dep_name in dependency_names:
            task = asyncio.create_task(
                self._fetch_single_dependency_with_semaphore(
                    semaphore, dep_name, primary_package_name, performance_metrics
                )
            )
            tasks.append(task)

        # Wait for all tasks with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=15.0,  # Don't wait too long for dependencies
            )
            return results

        except TimeoutError:
            logger.warning(
                "Dependency fetching timed out",
                dependencies=dependency_names,
                timeout=15.0,
            )

            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()

            # Return whatever we got before timeout
            completed_results: list[Any] = []
            for task in tasks:
                if task.done() and not task.cancelled():
                    try:
                        result = task.result()
                        completed_results.append(result)
                    except Exception as e:
                        completed_results.append(e)
                else:
                    completed_results.append(Exception("Timeout fetching dependency"))

            return completed_results

    async def _fetch_single_dependency_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        dep_name: str,
        primary_package_name: str,
        performance_metrics: dict[str, Any],
    ) -> PackageDocumentation:
        """Fetch a single dependency with semaphore control."""

        async with semaphore:
            return await self._fetch_single_dependency(
                dep_name, primary_package_name, performance_metrics
            )

    async def _fetch_single_dependency(
        self,
        dep_name: str,
        primary_package_name: str,
        performance_metrics: dict[str, Any],
    ) -> PackageDocumentation:
        """Fetch documentation for a single dependency."""

        try:
            logger.debug("Fetching dependency", dependency=dep_name)

            # Try to resolve and cache the dependency
            dep_info, from_cache = await self.cache_manager.resolve_and_cache(dep_name)

            if from_cache:
                performance_metrics["cache_hits"] += 1
            else:
                performance_metrics["cache_misses"] += 1

            # Format as dependency documentation
            dep_docs = self.formatter.format_dependency_package(
                dep_info, primary_package_name
            )

            logger.debug(
                "Successfully fetched dependency",
                dependency=dep_name,
                from_cache=from_cache,
            )

            return dep_docs

        except Exception as e:
            logger.warning(
                "Failed to fetch dependency", dependency=dep_name, error=str(e)
            )

            # Return minimal documentation for failed fetches
            return PackageDocumentation(
                name=dep_name,
                version="unknown",
                relationship="runtime_dependency",
                why_included=f"Required by {primary_package_name} (fetch failed)",
                dependency_level=1,
                summary=f"Documentation fetch failed: {str(e)[:100]}...",
            )


async def create_context_fetcher(
    cache_manager: CacheManagerInterface,
) -> ConcurrentContextFetcher:
    """Create a concurrent context fetcher with all dependencies."""

    # Initialize network client
    network_client = NetworkResilientClient()
    await network_client.__aenter__()

    # Initialize dependency resolver
    dependency_resolver = DependencyResolver(network_client)

    # Initialize formatter
    formatter = ContextDocumentationFormatter()

    return ConcurrentContextFetcher(
        cache_manager=cache_manager,
        dependency_resolver=dependency_resolver,
        formatter=formatter,
        network_client=network_client,
    )
