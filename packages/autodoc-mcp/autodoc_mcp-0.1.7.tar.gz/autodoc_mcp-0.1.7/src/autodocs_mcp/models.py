"""Data models for AutoDocs MCP Server."""

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DependencySpec(BaseModel):
    """Represents a single dependency specification."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1)
    version_constraint: str | None = None
    extras: list[str] = Field(default_factory=list)
    source: str = Field(default="project")  # project, dev, build


class ScanResult(BaseModel):
    """Enhanced result model supporting graceful degradation."""

    project_path: Path
    dependencies: list[DependencySpec]
    project_name: str | None = None
    scan_timestamp: datetime

    # Graceful degradation fields
    successful_deps: int = 0
    failed_deps: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    partial_success: bool = False

    def model_post_init(self, __context: Any) -> None:
        """Calculate successful_deps count automatically."""
        if self.successful_deps == 0:  # Only set if not already set
            self.successful_deps = len(self.dependencies)


class PackageInfo(BaseModel):
    """PyPI package information."""

    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    summary: str | None = None
    description: str | None = None
    home_page: str | None = None
    project_urls: dict[str, str] = Field(default_factory=dict)
    author: str | None = None
    license: str | None = None
    keywords: list[str] = Field(default_factory=list)
    classifiers: list[str] = Field(default_factory=list)


class CacheEntry(BaseModel):
    """Version-based cache entry (no time expiration)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: PackageInfo
    timestamp: datetime  # For metadata only, not expiration
    version: str  # Exact version for cache key

    # No is_expired property - version-based invalidation only
