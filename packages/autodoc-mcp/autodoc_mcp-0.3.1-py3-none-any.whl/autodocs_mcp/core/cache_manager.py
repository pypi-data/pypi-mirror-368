"""File-based cache manager for package documentation."""

import contextlib
import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from structlog import get_logger

from ..exceptions import CacheError
from ..models import CacheEntry, PackageInfo
from ..security import sanitize_cache_key
from .error_formatter import ErrorFormatter, ErrorSeverity, FormattedError

logger = get_logger(__name__)


class CacheManagerInterface(ABC):
    """Interface for cache management."""

    @abstractmethod
    async def get(self, cache_key: str) -> CacheEntry | None:
        """Retrieve cached entry if exists."""

    @abstractmethod
    async def set(self, cache_key: str, package_info: PackageInfo) -> None:
        """Store entry in cache."""

    @abstractmethod
    async def invalidate(self, cache_key: str | None = None) -> None:
        """Invalidate specific key or entire cache."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize cache storage."""

    @abstractmethod
    async def resolve_and_cache(
        self, package_name: str, version_constraint: str | None = None
    ) -> tuple[dict[str, Any], bool]:
        """Resolve package version and retrieve from cache or fetch fresh."""


class FileCacheManager(CacheManagerInterface):
    """JSON file-based cache implementation."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def initialize(self) -> None:
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Cache manager initialized", cache_dir=str(self.cache_dir))

    async def get(self, cache_key: str) -> CacheEntry | None:
        """Retrieve cached entry by version-based key."""
        sanitized_key = sanitize_cache_key(cache_key)
        cache_file = self.cache_dir / f"{sanitized_key}.json"

        if not cache_file.exists():
            logger.debug("Cache miss", cache_key=cache_key)
            return None

        try:
            data = json.loads(cache_file.read_text())

            # Parse the cached data back to models
            package_info = PackageInfo(**data["data"])
            cache_entry = CacheEntry(
                data=package_info,
                timestamp=datetime.fromisoformat(data["timestamp"]),
                version=data["version"],
            )

            logger.debug("Cache hit", cache_key=cache_key, version=cache_entry.version)
            return cache_entry

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Corrupted cache entry", cache_key=cache_key, error=str(e))
            # Remove corrupted cache file
            with contextlib.suppress(OSError):
                cache_file.unlink()
            return None

    async def set(self, cache_key: str, package_info: PackageInfo) -> None:
        """Store package info in cache with version-based key."""
        sanitized_key = sanitize_cache_key(cache_key)
        cache_file = self.cache_dir / f"{sanitized_key}.json"

        cache_entry = CacheEntry(
            data=package_info,
            timestamp=datetime.now(),
            version=package_info.version,
        )

        try:
            # Serialize for JSON storage
            cache_data = {
                "data": package_info.model_dump(),
                "timestamp": cache_entry.timestamp.isoformat(),
                "version": cache_entry.version,
            }

            cache_file.write_text(json.dumps(cache_data, indent=2))
            logger.info(
                "Cached package info",
                cache_key=cache_key,
                package=package_info.name,
                version=package_info.version,
            )

        except (OSError, TypeError) as e:
            raise CacheError(f"Failed to cache {cache_key}: {e}") from e

    async def invalidate(self, cache_key: str | None = None) -> None:
        """Invalidate specific cache entry or entire cache."""
        if cache_key:
            sanitized_key = sanitize_cache_key(cache_key)
            cache_file = self.cache_dir / f"{sanitized_key}.json"
            try:
                if cache_file.exists():
                    cache_file.unlink()
                    logger.info("Invalidated cache entry", cache_key=cache_key)
            except OSError as e:
                logger.warning(
                    "Failed to invalidate cache entry",
                    cache_key=cache_key,
                    error=str(e),
                )
        else:
            # Clear entire cache
            try:
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
                logger.info("Cleared entire cache", cache_dir=str(self.cache_dir))
            except OSError as e:
                logger.error("Failed to clear cache", error=str(e))
                raise CacheError(f"Failed to clear cache: {e}") from e

    async def list_cached_packages(self) -> list[str]:
        """List all cached package keys."""
        try:
            return [f.stem for f in self.cache_dir.glob("*.json")]
        except OSError as e:
            logger.error("Failed to list cached packages", error=str(e))
            return []

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)

            return {
                "total_entries": len(cache_files),
                "total_size_bytes": total_size,
                "cache_dir": str(self.cache_dir),
            }
        except OSError as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {"error": str(e)}

    def get_cached_entry_safe(
        self, cache_key: str
    ) -> tuple[CacheEntry | None, list[FormattedError]]:
        """Get cached entry with error handling."""
        errors: list[FormattedError] = []

        try:
            sanitized_key = sanitize_cache_key(cache_key)
            cache_file = self.cache_dir / f"{sanitized_key}.json"

            if not cache_file.exists():
                return None, errors

            # Check if cache file is corrupted
            try:
                with cache_file.open("r", encoding="utf-8") as f:
                    content = f.read().strip()

                if not content:
                    # Empty cache file
                    cache_file.unlink()  # Remove corrupted file
                    errors.append(
                        FormattedError(
                            message=f"Corrupted cache file removed: {cache_key}",
                            suggestion="The cache file was empty and has been cleaned up automatically.",
                            severity=ErrorSeverity.INFO,
                            error_code="cache_corruption_fixed",
                        )
                    )
                    return None, errors

                data = json.loads(content)

                # Parse the cached data back to models
                package_info = PackageInfo(**data["data"])
                cache_entry = CacheEntry(
                    data=package_info,
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    version=data["version"],
                )
                return cache_entry, errors

            except json.JSONDecodeError:
                # Corrupted JSON file
                cache_file.unlink()
                errors.append(
                    FormattedError(
                        message=f"Corrupted cache file removed: {cache_key}",
                        suggestion="The cache file was corrupted and has been cleaned up automatically.",
                        severity=ErrorSeverity.WARNING,
                        error_code="cache_corruption_fixed",
                    )
                )
                return None, errors

        except Exception as e:
            formatted_error = ErrorFormatter.format_exception(
                e, {"cache_key": cache_key, "operation": "cache_retrieval"}
            )
            errors.append(formatted_error)
            return None, errors

    async def resolve_and_cache(
        self, package_name: str, version_constraint: str | None = None
    ) -> tuple[dict[str, Any], bool]:
        """
        Resolve package version and retrieve from cache or fetch fresh.

        Args:
            package_name: Name of the package
            version_constraint: Optional version constraint

        Returns:
            Tuple of (package_info_dict, from_cache_bool)
        """
        from .doc_fetcher import PyPIDocumentationFetcher
        from .version_resolver import VersionResolver

        # Initialize resolvers
        version_resolver = VersionResolver()

        try:
            # Step 1: Resolve to specific version
            resolved_version = await version_resolver.resolve_version(
                package_name, version_constraint
            )

            # Step 2: Check version-specific cache
            cache_key = version_resolver.generate_cache_key(
                package_name, resolved_version
            )
            cached_entry = await self.get(cache_key)

            if cached_entry:
                logger.debug(
                    "Cache hit for resolve_and_cache",
                    package=package_name,
                    version=resolved_version,
                )
                # Return as dictionary for compatibility
                return cached_entry.data.model_dump(), True
            else:
                logger.debug(
                    "Cache miss, fetching fresh",
                    package=package_name,
                    version=resolved_version,
                )

                # Step 3: Fetch fresh from PyPI
                async with PyPIDocumentationFetcher() as fetcher:
                    package_info = await fetcher.fetch_package_info(package_name)
                    await self.set(cache_key, package_info)

                # Return as dictionary for compatibility
                return package_info.model_dump(), False

        except Exception as e:
            logger.error(
                "Failed to resolve and cache package",
                package=package_name,
                constraint=version_constraint,
                error=str(e),
            )
            raise
