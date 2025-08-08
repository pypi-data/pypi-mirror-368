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
        cache_file = self.cache_dir / f"{cache_key}.json"

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
        cache_file = self.cache_dir / f"{cache_key}.json"

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
            cache_file = self.cache_dir / f"{cache_key}.json"
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
