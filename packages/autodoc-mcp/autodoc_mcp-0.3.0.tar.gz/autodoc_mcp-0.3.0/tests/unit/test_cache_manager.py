"""Unit tests for cache manager functionality."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.autodocs_mcp.core.cache_manager import FileCacheManager
from src.autodocs_mcp.exceptions import CacheError
from src.autodocs_mcp.models import CacheEntry, PackageInfo


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def cache_manager(temp_cache_dir):
    """Create cache manager instance with temp directory."""
    return FileCacheManager(temp_cache_dir)


@pytest.fixture
def sample_package_info():
    """Sample PackageInfo for tests."""
    return PackageInfo(
        name="requests",
        version="2.28.0",
        summary="Python HTTP for Humans.",
        description="Requests is a simple HTTP library.",
        author="Kenneth Reitz",
        license="Apache 2.0",
        home_page="https://requests.readthedocs.io",
        project_urls={
            "Documentation": "https://requests.readthedocs.io",
            "Source": "https://github.com/psf/requests",
        },
        classifiers=["Development Status :: 5 - Production/Stable"],
        keywords=["http", "requests", "web"],
    )


@pytest.fixture
def cache_entry(sample_package_info):
    """Sample CacheEntry for tests."""
    return CacheEntry(
        data=sample_package_info,
        timestamp=datetime.now(),
        version="2.28.0",
    )


class TestFileCacheManagerInitialization:
    """Test cache manager initialization."""

    def test_cache_dir_creation_on_init(self, temp_cache_dir):
        """Test cache directory is created during initialization."""
        cache_dir = temp_cache_dir / "new_cache"
        assert not cache_dir.exists()

        FileCacheManager(cache_dir)
        assert cache_dir.exists()

    @pytest.mark.asyncio
    async def test_initialize_creates_directory(self, temp_cache_dir):
        """Test initialize method creates cache directory."""
        cache_dir = temp_cache_dir / "init_test"
        cache_manager = FileCacheManager(cache_dir)

        # Remove directory to test initialization
        cache_dir.rmdir()
        assert not cache_dir.exists()

        await cache_manager.initialize()
        assert cache_dir.exists()

    @pytest.mark.asyncio
    async def test_initialize_existing_directory(self, cache_manager):
        """Test initialize method with existing directory."""
        # Should not raise error with existing directory
        await cache_manager.initialize()
        assert cache_manager.cache_dir.exists()


class TestCacheOperations:
    """Test basic cache operations."""

    @pytest.mark.asyncio
    async def test_get_cache_miss(self, cache_manager):
        """Test cache miss returns None."""
        result = await cache_manager.get("nonexistent-key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_cache_success(self, cache_manager, sample_package_info):
        """Test successful cache set and get operations."""
        cache_key = "requests-2.28.0"

        # Set cache entry
        await cache_manager.set(cache_key, sample_package_info)

        # Verify file was created
        cache_file = cache_manager.cache_dir / f"{cache_key}.json"
        assert cache_file.exists()

        # Get cache entry
        result = await cache_manager.get(cache_key)

        assert result is not None
        assert result.data.name == "requests"
        assert result.data.version == "2.28.0"
        assert result.version == "2.28.0"

    @pytest.mark.asyncio
    async def test_get_corrupted_cache_file_json_error(self, cache_manager):
        """Test handling of corrupted JSON cache files."""
        cache_key = "corrupted-key"
        cache_file = cache_manager.cache_dir / f"{cache_key}.json"

        # Create corrupted JSON file
        cache_file.write_text("invalid json content")

        # Should return None and remove corrupted file
        result = await cache_manager.get(cache_key)
        assert result is None
        assert not cache_file.exists()

    @pytest.mark.asyncio
    async def test_get_corrupted_cache_file_key_error(self, cache_manager):
        """Test handling of cache files with missing keys."""
        cache_key = "missing-keys"
        cache_file = cache_manager.cache_dir / f"{cache_key}.json"

        # Create JSON with missing required keys
        cache_file.write_text(json.dumps({"invalid": "structure"}))

        # Should return None and remove corrupted file
        result = await cache_manager.get(cache_key)
        assert result is None
        assert not cache_file.exists()

    @pytest.mark.asyncio
    async def test_set_cache_io_error(self, cache_manager, sample_package_info):
        """Test cache set with I/O error."""
        # Mock cache directory to be a file (causing OSError)
        cache_manager.cache_dir = Path("/dev/null/invalid")

        with pytest.raises(CacheError, match="Failed to cache"):
            await cache_manager.set("test-key", sample_package_info)

    @pytest.mark.asyncio
    async def test_set_cache_type_error(self, cache_manager, mocker):
        """Test cache set with serialization error."""
        # Create a package info that can't be serialized
        bad_package = mocker.Mock(spec=PackageInfo)
        bad_package.model_dump.side_effect = TypeError("Cannot serialize")
        bad_package.name = "test"
        bad_package.version = "1.0.0"

        with pytest.raises(CacheError, match="Failed to cache"):
            await cache_manager.set("test-key", bad_package)


class TestCacheManagement:
    """Test cache management operations."""

    @pytest.mark.asyncio
    async def test_invalidate_specific_key_existing(
        self, cache_manager, sample_package_info
    ):
        """Test invalidating specific existing cache key."""
        cache_key = "requests-2.28.0"

        # Set cache entry
        await cache_manager.set(cache_key, sample_package_info)
        cache_file = cache_manager.cache_dir / f"{cache_key}.json"
        assert cache_file.exists()

        # Invalidate specific key
        await cache_manager.invalidate(cache_key)

        # File should be removed
        assert not cache_file.exists()

    @pytest.mark.asyncio
    async def test_invalidate_specific_key_nonexistent(self, cache_manager):
        """Test invalidating non-existent cache key."""
        # Should not raise error
        await cache_manager.invalidate("nonexistent-key")

    @pytest.mark.asyncio
    async def test_invalidate_specific_key_os_error(
        self, cache_manager, sample_package_info, mocker
    ):
        """Test invalidating with OS error during deletion."""
        cache_key = "requests-2.28.0"

        # Set cache entry
        await cache_manager.set(cache_key, sample_package_info)

        # Mock unlink to raise OSError
        mocker.patch.object(Path, "unlink", side_effect=OSError("Permission denied"))
        # Should not raise error, just log warning
        await cache_manager.invalidate(cache_key)

    @pytest.mark.asyncio
    async def test_invalidate_entire_cache(self, cache_manager, sample_package_info):
        """Test invalidating entire cache."""
        # Set multiple cache entries
        await cache_manager.set("requests-2.28.0", sample_package_info)
        await cache_manager.set("httpx-0.24.0", sample_package_info)

        # Verify files exist
        assert len(list(cache_manager.cache_dir.glob("*.json"))) == 2

        # Clear entire cache
        await cache_manager.invalidate()

        # All files should be removed
        assert len(list(cache_manager.cache_dir.glob("*.json"))) == 0

    @pytest.mark.asyncio
    async def test_invalidate_entire_cache_os_error(
        self, cache_manager, sample_package_info, mocker
    ):
        """Test clearing entire cache with OS error."""
        await cache_manager.set("test-key", sample_package_info)

        # Mock glob to raise OSError
        mocker.patch.object(Path, "glob", side_effect=OSError("Permission denied"))
        with pytest.raises(CacheError, match="Failed to clear cache"):
            await cache_manager.invalidate()

    @pytest.mark.asyncio
    async def test_list_cached_packages_success(
        self, cache_manager, sample_package_info
    ):
        """Test listing cached packages successfully."""
        # Add some cache entries
        await cache_manager.set("requests-2.28.0", sample_package_info)
        await cache_manager.set("httpx-0.24.0", sample_package_info)

        # List cached packages
        packages = await cache_manager.list_cached_packages()

        assert len(packages) == 2
        assert "requests-2.28.0" in packages
        assert "httpx-0.24.0" in packages

    @pytest.mark.asyncio
    async def test_list_cached_packages_empty_cache(self, cache_manager):
        """Test listing cached packages with empty cache."""
        packages = await cache_manager.list_cached_packages()
        assert packages == []

    @pytest.mark.asyncio
    async def test_list_cached_packages_os_error(self, cache_manager, mocker):
        """Test listing cached packages with OS error."""
        # Mock glob to raise OSError
        with mocker.patch.object(
            Path, "glob", side_effect=OSError("Permission denied")
        ):
            packages = await cache_manager.list_cached_packages()
            assert packages == []

    @pytest.mark.asyncio
    async def test_get_cache_stats_success(self, cache_manager, sample_package_info):
        """Test getting cache statistics successfully."""
        # Add some cache entries
        await cache_manager.set("requests-2.28.0", sample_package_info)
        await cache_manager.set("httpx-0.24.0", sample_package_info)

        stats = await cache_manager.get_cache_stats()

        assert stats["total_entries"] == 2
        assert stats["total_size_bytes"] > 0
        assert stats["cache_dir"] == str(cache_manager.cache_dir)

    @pytest.mark.asyncio
    async def test_get_cache_stats_empty_cache(self, cache_manager):
        """Test getting cache statistics with empty cache."""
        stats = await cache_manager.get_cache_stats()

        assert stats["total_entries"] == 0
        assert stats["total_size_bytes"] == 0
        assert stats["cache_dir"] == str(cache_manager.cache_dir)

    @pytest.mark.asyncio
    async def test_get_cache_stats_os_error(self, cache_manager, mocker):
        """Test getting cache statistics with OS error."""
        # Mock glob to raise OSError
        with mocker.patch.object(
            Path, "glob", side_effect=OSError("Permission denied")
        ):
            stats = await cache_manager.get_cache_stats()
            assert "error" in stats


class TestSafeCacheOperations:
    """Test safe cache operations with error handling."""

    def test_get_cached_entry_safe_cache_miss(self, cache_manager):
        """Test safe cache retrieval with cache miss."""
        entry, errors = cache_manager.get_cached_entry_safe("nonexistent-key")

        assert entry is None
        assert len(errors) == 0

    def test_get_cached_entry_safe_success(self, cache_manager, sample_package_info):
        """Test safe cache retrieval with successful hit."""
        cache_key = "requests-2.28.0"
        cache_file = cache_manager.cache_dir / f"{cache_key}.json"

        # Create valid cache file
        cache_data = {
            "data": sample_package_info.model_dump(),
            "timestamp": datetime.now().isoformat(),
            "version": "2.28.0",
        }
        cache_file.write_text(json.dumps(cache_data))

        entry, errors = cache_manager.get_cached_entry_safe(cache_key)

        assert entry is not None
        assert entry.data.name == "requests"
        assert len(errors) == 0

    def test_get_cached_entry_safe_empty_file(self, cache_manager):
        """Test safe cache retrieval with empty cache file."""
        cache_key = "empty-file"
        cache_file = cache_manager.cache_dir / f"{cache_key}.json"

        # Create empty cache file
        cache_file.write_text("")

        entry, errors = cache_manager.get_cached_entry_safe(cache_key)

        assert entry is None
        assert len(errors) == 1
        assert errors[0].error_code == "cache_corruption_fixed"
        assert not cache_file.exists()  # File should be removed

    def test_get_cached_entry_safe_json_decode_error(self, cache_manager):
        """Test safe cache retrieval with JSON decode error."""
        cache_key = "corrupted-json"
        cache_file = cache_manager.cache_dir / f"{cache_key}.json"

        # Create corrupted JSON file
        cache_file.write_text("invalid json content")

        entry, errors = cache_manager.get_cached_entry_safe(cache_key)

        assert entry is None
        assert len(errors) == 1
        assert errors[0].error_code == "cache_corruption_fixed"
        assert not cache_file.exists()  # File should be removed

    def test_get_cached_entry_safe_generic_exception(self, cache_manager, mocker):
        """Test safe cache retrieval with generic exception."""
        cache_key = "error-key"

        # Mock sanitize_cache_key to raise exception
        with mocker.patch(
            "src.autodocs_mcp.core.cache_manager.sanitize_cache_key",
            side_effect=ValueError("Test error"),
        ):
            entry, errors = cache_manager.get_cached_entry_safe(cache_key)

        assert entry is None
        assert len(errors) == 1
        assert errors[0].error_code is not None


class TestResolveAndCache:
    """Test resolve and cache functionality."""

    @pytest.mark.asyncio
    async def test_resolve_and_cache_cache_hit(
        self, cache_manager, sample_package_info, mocker
    ):
        """Test resolve and cache with cache hit."""
        # Pre-populate cache
        cache_key = "requests-2.28.0"
        await cache_manager.set(cache_key, sample_package_info)

        mock_resolver_class = mocker.patch(
            "src.autodocs_mcp.core.version_resolver.VersionResolver"
        )
        mock_resolver = mocker.Mock()
        mock_resolver.resolve_version = mocker.AsyncMock(return_value="2.28.0")
        mock_resolver.generate_cache_key.return_value = cache_key
        mock_resolver_class.return_value = mock_resolver

        result, from_cache = await cache_manager.resolve_and_cache(
            "requests", ">=2.0.0"
        )

        assert from_cache is True
        assert result["name"] == "requests"
        assert result["version"] == "2.28.0"

    @pytest.mark.asyncio
    async def test_resolve_and_cache_cache_miss(
        self, cache_manager, sample_package_info, mocker
    ):
        """Test resolve and cache with cache miss and fresh fetch."""
        cache_key = "requests-2.28.0"

        # Mock version resolver
        mock_resolver_class = mocker.patch(
            "src.autodocs_mcp.core.version_resolver.VersionResolver"
        )
        mock_resolver = mocker.Mock()
        mock_resolver.resolve_version = mocker.AsyncMock(return_value="2.28.0")
        mock_resolver.generate_cache_key.return_value = cache_key
        mock_resolver_class.return_value = mock_resolver

        # Mock fetcher
        mock_fetcher_class = mocker.patch(
            "src.autodocs_mcp.core.doc_fetcher.PyPIDocumentationFetcher"
        )
        mock_fetcher = mocker.AsyncMock()
        mock_fetcher.fetch_package_info = mocker.AsyncMock(
            return_value=sample_package_info
        )
        mock_fetcher.__aenter__ = mocker.AsyncMock(return_value=mock_fetcher)
        mock_fetcher.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_fetcher_class.return_value = mock_fetcher

        result, from_cache = await cache_manager.resolve_and_cache(
            "requests", ">=2.0.0"
        )

        assert from_cache is False
        assert result["name"] == "requests"
        assert result["version"] == "2.28.0"

        # Verify entry was cached
        cached_entry = await cache_manager.get(cache_key)
        assert cached_entry is not None

    @pytest.mark.asyncio
    async def test_resolve_and_cache_version_resolution_error(
        self, cache_manager, mocker
    ):
        """Test resolve and cache with version resolution error."""
        mock_resolver_class = mocker.patch(
            "src.autodocs_mcp.core.version_resolver.VersionResolver"
        )
        mock_resolver = mocker.Mock()
        mock_resolver.resolve_version = mocker.AsyncMock(
            side_effect=ValueError("Version resolution failed")
        )
        mock_resolver_class.return_value = mock_resolver

        with pytest.raises(ValueError, match="Version resolution failed"):
            await cache_manager.resolve_and_cache("nonexistent-package", ">=1.0.0")

    @pytest.mark.asyncio
    async def test_resolve_and_cache_fetch_error(self, cache_manager, mocker):
        """Test resolve and cache with fetch error."""
        cache_key = "requests-2.28.0"

        # Mock version resolver
        mock_resolver_class = mocker.patch(
            "src.autodocs_mcp.core.version_resolver.VersionResolver"
        )
        mock_resolver = mocker.Mock()
        mock_resolver.resolve_version = mocker.AsyncMock(return_value="2.28.0")
        mock_resolver.generate_cache_key.return_value = cache_key
        mock_resolver_class.return_value = mock_resolver

        # Mock fetcher to raise error
        mock_fetcher_class = mocker.patch(
            "src.autodocs_mcp.core.doc_fetcher.PyPIDocumentationFetcher"
        )
        mock_fetcher = mocker.AsyncMock()
        mock_fetcher.fetch_package_info = mocker.AsyncMock(
            side_effect=ValueError("Fetch failed")
        )
        mock_fetcher.__aenter__ = mocker.AsyncMock(return_value=mock_fetcher)
        mock_fetcher.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_fetcher_class.return_value = mock_fetcher

        with pytest.raises(ValueError, match="Fetch failed"):
            await cache_manager.resolve_and_cache("requests", ">=2.0.0")


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_cache_key_sanitization(self, cache_manager, sample_package_info, mocker):
        """Test that cache keys are properly sanitized."""
        # This test verifies that sanitize_cache_key is called
        mock_sanitize = mocker.patch(
            "src.autodocs_mcp.core.cache_manager.sanitize_cache_key",
            return_value="sanitized-key",
        )
        cache_manager.cache_dir / "sanitized-key.json"

        # The function should be called during cache operations
        cache_manager.get_cached_entry_safe("unsafe/key\\with:special*chars")
        mock_sanitize.assert_called_with("unsafe/key\\with:special*chars")

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(
        self, cache_manager, sample_package_info
    ):
        """Test handling of concurrent cache operations."""
        import asyncio

        # Test concurrent set operations
        tasks = [
            cache_manager.set(f"package-{i}", sample_package_info) for i in range(5)
        ]

        await asyncio.gather(*tasks)

        # All entries should be cached
        stats = await cache_manager.get_cache_stats()
        assert stats["total_entries"] == 5

    @pytest.mark.asyncio
    async def test_large_cache_data(self, cache_manager):
        """Test handling of large cache data."""
        # Create package with large description
        large_package = PackageInfo(
            name="large-package",
            version="1.0.0",
            summary="Test package",
            description="Large description. " * 10000,  # ~200KB description
            author="Test Author",
            license="MIT",
            home_page="https://example.com",
            project_urls={},
            classifiers=[],
            keywords=[],
        )

        # Should handle large data without issues
        await cache_manager.set("large-package-1.0.0", large_package)

        result = await cache_manager.get("large-package-1.0.0")
        assert result is not None
        assert result.data.name == "large-package"
        assert len(result.data.description) > 100000
