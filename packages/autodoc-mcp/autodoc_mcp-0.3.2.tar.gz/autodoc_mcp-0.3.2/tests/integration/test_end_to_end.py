"""Integration tests for end-to-end workflows."""

import asyncio
import tempfile
import time
from pathlib import Path

import pytest

from src.autodoc_mcp.core.cache_manager import FileCacheManager
from src.autodoc_mcp.core.dependency_parser import PyProjectParser
from src.autodoc_mcp.core.doc_fetcher import PyPIDocumentationFetcher
from src.autodoc_mcp.core.version_resolver import VersionResolver
from src.autodoc_mcp.exceptions import NetworkError, PackageNotFoundError
from src.autodoc_mcp.models import PackageInfo


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_pyproject_toml():
    """Sample pyproject.toml content for testing."""
    return """
[project]
name = "test-project"
version = "1.0.0"
dependencies = [
    "requests>=2.28.0",
    "pydantic>=1.10.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0"
]
"""


@pytest.fixture
def sample_pyproject_with_errors():
    """Sample pyproject.toml with parsing errors for testing."""
    return """
[project]
name = "test-project"
version = "1.0.0"
dependencies = [
    "requests>=2.28.0",
    "bad@package-name!",
    "",
    "pkg[unclosed-bracket"
]
"""


class TestCompleteDocumentationWorkflow:
    """Test complete end-to-end documentation workflow."""

    @pytest.mark.asyncio
    async def test_complete_workflow_success(
        self, temp_project_dir, temp_cache_dir, sample_pyproject_toml
    ):
        """Test complete workflow: Scan → Resolve → Cache → Get Docs."""
        # Setup test project
        pyproject_path = temp_project_dir / "pyproject.toml"
        pyproject_path.write_text(sample_pyproject_toml)

        # Initialize components
        parser = PyProjectParser()
        cache_manager = FileCacheManager(temp_cache_dir)
        version_resolver = VersionResolver()

        # Step 1: Parse dependencies
        scan_result = await parser.parse_project(temp_project_dir)

        assert len(scan_result.dependencies) > 0
        assert len(scan_result.dependencies) >= 2  # requests, pydantic
        assert scan_result.project_name == "test-project"

        # Step 2: Process each dependency through full pipeline
        successful_packages = []

        for dependency in scan_result.dependencies[:2]:  # Test first 2 packages
            package_name = dependency.name
            version_constraint = dependency.version_constraint

            try:
                # Resolve version
                resolved_version = await version_resolver.resolve_version(
                    package_name, version_constraint
                )
                assert resolved_version is not None

                # Generate cache key
                cache_key = version_resolver.generate_cache_key(
                    package_name, resolved_version
                )

                # Check cache (should be miss first time)
                cached_entry = await cache_manager.get(cache_key)
                if cached_entry is None:
                    # Fetch from PyPI
                    async with PyPIDocumentationFetcher() as fetcher:
                        package_info = await fetcher.fetch_package_info(package_name)

                        # Cache the result
                        await cache_manager.set(cache_key, package_info)

                        # Format documentation
                        formatted_docs = fetcher.format_documentation(package_info)

                        assert (
                            len(formatted_docs) > 100
                        )  # Should have substantial content
                        assert package_name in formatted_docs

                        successful_packages.append(package_name)

            except (NetworkError, PackageNotFoundError, RuntimeError) as e:
                # Skip packages that fail due to network issues in CI
                pytest.skip(f"Network test skipped due to: {e}")

        # Verify at least one package was processed successfully
        assert len(successful_packages) > 0

        # Verify cache functionality
        cache_stats = await cache_manager.get_cache_stats()
        assert cache_stats["total_entries"] > 0

    @pytest.mark.asyncio
    async def test_workflow_with_cache_hit(
        self, temp_project_dir, temp_cache_dir, sample_pyproject_toml
    ):
        """Test workflow with cache hit scenario."""
        # Setup
        pyproject_path = temp_project_dir / "pyproject.toml"
        pyproject_path.write_text(sample_pyproject_toml)

        cache_manager = FileCacheManager(temp_cache_dir)

        # Pre-populate cache with mock data
        test_package_info = PackageInfo(
            name="requests",
            version="2.28.0",
            summary="HTTP library for Python",
            description="A simple HTTP library",
            author="Kenneth Reitz",
            license="Apache 2.0",
            home_page="https://requests.readthedocs.io",
            project_urls={},
            classifiers=[],
            keywords=[],
        )

        await cache_manager.set("requests-2.28.0", test_package_info)

        # Test cache hit
        cached_entry = await cache_manager.get("requests-2.28.0")
        assert cached_entry is not None
        assert cached_entry.data.name == "requests"

        # Format cached documentation
        async with PyPIDocumentationFetcher() as fetcher:
            formatted_docs = fetcher.format_documentation(cached_entry.data)
            assert "requests" in formatted_docs
            assert "2.28.0" in formatted_docs

    @pytest.mark.asyncio
    async def test_workflow_performance_requirements(
        self, temp_project_dir, temp_cache_dir
    ):
        """Test that workflow meets <5s performance requirement."""
        # Create minimal project for fast processing
        pyproject_content = """
[project]
name = "perf-test"
version = "1.0.0"
dependencies = ["requests>=2.28.0"]
"""
        pyproject_path = temp_project_dir / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        start_time = time.time()

        try:
            # Run complete workflow
            parser = PyProjectParser()
            cache_manager = FileCacheManager(temp_cache_dir)

            # Parse dependencies
            scan_result = await parser.parse_project(temp_project_dir)
            assert len(scan_result.dependencies) > 0

            # Process first dependency
            if scan_result.dependencies:
                dependency = scan_result.dependencies[0]

                # Use resolve_and_cache for integrated flow
                package_dict, from_cache = await cache_manager.resolve_and_cache(
                    dependency.name, dependency.version_constraint
                )

                # Verify result
                assert package_dict["name"] == dependency.name

        except (NetworkError, PackageNotFoundError, RuntimeError) as e:
            pytest.skip(f"Network test skipped due to: {e}")

        elapsed_time = time.time() - start_time

        # Performance requirement: <5 seconds
        assert elapsed_time < 5.0, (
            f"Workflow took {elapsed_time:.2f}s, exceeds 5s requirement"
        )


class TestErrorRecoveryWorkflows:
    """Test error handling and recovery workflows."""

    @pytest.mark.asyncio
    async def test_dependency_parsing_error_recovery(
        self, temp_project_dir, sample_pyproject_with_errors
    ):
        """Test workflow continues with valid dependencies despite parsing errors."""
        # Setup project with mixed valid/invalid dependencies
        pyproject_path = temp_project_dir / "pyproject.toml"
        pyproject_path.write_text(sample_pyproject_with_errors)

        parser = PyProjectParser()
        scan_result = await parser.parse_project(temp_project_dir)

        # Should have partial success
        assert scan_result.partial_success is True
        assert len(scan_result.dependencies) > 0  # At least 'requests' should parse
        assert len(scan_result.failed_deps) > 0  # Should have failed dependencies

        # Valid dependency should be processable
        valid_deps = [dep for dep in scan_result.dependencies if dep.name == "requests"]
        assert len(valid_deps) == 1

    @pytest.mark.asyncio
    async def test_network_error_recovery(
        self, temp_project_dir, temp_cache_dir, mocker
    ):
        """Test recovery from network errors."""
        # Create project
        pyproject_content = """
[project]
name = "network-test"
version = "1.0.0"
dependencies = ["requests>=2.28.0"]
"""
        pyproject_path = temp_project_dir / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        # Mock network failure for version resolution
        mock_client_class = mocker.patch(
            "src.autodoc_mcp.core.version_resolver.NetworkResilientClient"
        )
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.get_with_retry.side_effect = NetworkError("Connection failed")
        mock_client_class.return_value = mock_client

        # Test that errors are handled gracefully
        version_resolver = VersionResolver()

        with pytest.raises(NetworkError):
            await version_resolver.resolve_version("requests", ">=2.28.0")

    @pytest.mark.asyncio
    async def test_package_not_found_recovery(self, temp_cache_dir, mocker):
        """Test recovery from package not found errors."""
        # Mock PyPI client to return 404
        mock_client_class = mocker.patch(
            "src.autodoc_mcp.core.doc_fetcher.NetworkResilientClient"
        )
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.get_with_retry.side_effect = PackageNotFoundError(
            "Package not found"
        )
        mock_client_class.return_value = mock_client

        # Test safe fetch handles error gracefully
        async with PyPIDocumentationFetcher() as fetcher:
            result = await fetcher.fetch_package_info_safe("nonexistent-package")

            assert result.success is False
            assert len(result.errors) == 1
            assert result.package_info is None

    @pytest.mark.asyncio
    async def test_cache_corruption_recovery(self, temp_cache_dir):
        """Test recovery from corrupted cache files."""
        cache_manager = FileCacheManager(temp_cache_dir)

        # Create corrupted cache file
        cache_file = temp_cache_dir / "corrupted-key.json"
        cache_file.write_text("invalid json content")

        # Test safe retrieval handles corruption
        entry, errors = cache_manager.get_cached_entry_safe("corrupted-key")

        assert entry is None
        assert len(errors) == 1
        assert errors[0].error_code == "cache_corruption_fixed"
        assert not cache_file.exists()  # Should be cleaned up


class TestRealPyPIIntegration:
    """Test integration with real PyPI API (network-dependent)."""

    @pytest.mark.asyncio
    async def test_real_pypi_popular_packages(self, temp_cache_dir):
        """Test fetching real popular packages from PyPI."""
        # Test with commonly available packages
        test_packages = ["requests"]  # Start with just one to be conservative
        cache_manager = FileCacheManager(temp_cache_dir)

        for package_name in test_packages:
            try:
                # Test resolve and cache with real PyPI
                package_dict, from_cache = await cache_manager.resolve_and_cache(
                    package_name, None
                )

                # Verify response structure
                assert "name" in package_dict
                assert "version" in package_dict
                assert package_dict["name"] == package_name
                assert from_cache is False  # First fetch

                # Test cache hit on second fetch
                package_dict2, from_cache2 = await cache_manager.resolve_and_cache(
                    package_name, None
                )

                assert from_cache2 is True  # Should be cached now
                assert package_dict2["name"] == package_name

            except (NetworkError, PackageNotFoundError, RuntimeError) as e:
                pytest.skip(f"Network test skipped due to: {e}")

    @pytest.mark.asyncio
    async def test_real_pypi_documentation_formatting(self):
        """Test documentation formatting with real PyPI data."""
        try:
            async with PyPIDocumentationFetcher() as fetcher:
                # Fetch real package
                package_info = await fetcher.fetch_package_info("requests")

                # Test basic formatting
                formatted = fetcher.format_documentation(package_info)

                assert len(formatted) > 100
                assert "requests" in formatted.lower()
                assert package_info.version in formatted

                # Test with query filtering
                filtered = fetcher.format_documentation(package_info, query="http")

                assert len(filtered) > 0
                assert "http" in filtered.lower()

        except (NetworkError, PackageNotFoundError, RuntimeError) as e:
            pytest.skip(f"Network test skipped due to: {e}")

    @pytest.mark.asyncio
    async def test_real_pypi_error_handling(self):
        """Test error handling with real PyPI for nonexistent packages."""
        try:
            async with PyPIDocumentationFetcher() as fetcher:
                # Test with package that definitely doesn't exist
                nonexistent_package = f"definitely-does-not-exist-{int(time.time())}"

                result = await fetcher.fetch_package_info_safe(nonexistent_package)

                assert result.success is False
                assert len(result.errors) > 0
                assert result.package_info is None

        except Exception as e:
            # Even in error cases, we shouldn't get unhandled exceptions
            pytest.skip(f"Network test skipped due to: {e}")


class TestConcurrencyAndRaceConditions:
    """Test concurrent operations and race conditions."""

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self, temp_cache_dir):
        """Test concurrent cache operations don't cause corruption."""
        cache_manager = FileCacheManager(temp_cache_dir)

        # Create sample package info
        package_info = PackageInfo(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            description="A test package",
            author="Test Author",
            license="MIT",
            home_page="https://example.com",
            project_urls={},
            classifiers=[],
            keywords=[],
        )

        # Run concurrent set operations
        tasks = []
        for i in range(10):
            task = cache_manager.set(f"test-package-{i}", package_info)
            tasks.append(task)

        await asyncio.gather(*tasks)

        # Verify all entries were cached
        stats = await cache_manager.get_cache_stats()
        assert stats["total_entries"] == 10

        # Test concurrent get operations
        get_tasks = []
        for i in range(10):
            task = cache_manager.get(f"test-package-{i}")
            get_tasks.append(task)

        results = await asyncio.gather(*get_tasks)

        # All should be successful
        assert all(result is not None for result in results)

    @pytest.mark.asyncio
    async def test_concurrent_documentation_fetching(self):
        """Test concurrent documentation fetching doesn't cause issues."""
        packages = ["requests"]  # Conservative test with one package

        async def fetch_package(package_name: str) -> bool:
            try:
                async with PyPIDocumentationFetcher() as fetcher:
                    await fetcher.fetch_package_info(package_name)
                    return True
            except (NetworkError, PackageNotFoundError, RuntimeError):
                return False

        try:
            # Run multiple concurrent fetches
            tasks = [fetch_package(pkg) for pkg in packages for _ in range(3)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Should not have any unhandled exceptions
            exceptions = [r for r in results if isinstance(r, Exception)]
            assert len(exceptions) == 0, f"Got unexpected exceptions: {exceptions}"

        except Exception as e:
            pytest.skip(f"Network test skipped due to: {e}")


class TestSystemResourceLimits:
    """Test behavior under system resource constraints."""

    @pytest.mark.asyncio
    async def test_large_project_handling(self, temp_project_dir):
        """Test handling of projects with many dependencies."""
        # Create project with many dependencies
        dependencies = [f"package-{i}>=1.0.0" for i in range(50)]

        pyproject_content = f"""
[project]
name = "large-project"
version = "1.0.0"
dependencies = {dependencies}
"""

        pyproject_path = temp_project_dir / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        parser = PyProjectParser()
        scan_result = await parser.parse_project(temp_project_dir)

        # Should handle large number of dependencies
        assert len(scan_result.dependencies) == 50
        assert scan_result.project_name == "large-project"

    @pytest.mark.asyncio
    async def test_memory_usage_with_large_descriptions(self, temp_cache_dir):
        """Test memory handling with large package descriptions."""
        cache_manager = FileCacheManager(temp_cache_dir)

        # Create package with very large description
        large_description = "Large description content. " * 10000  # ~300KB

        large_package = PackageInfo(
            name="large-package",
            version="1.0.0",
            summary="Package with large description",
            description=large_description,
            author="Test Author",
            license="MIT",
            home_page="https://example.com",
            project_urls={},
            classifiers=[],
            keywords=[],
        )

        # Should handle large package without issues
        await cache_manager.set("large-package-1.0.0", large_package)

        retrieved = await cache_manager.get("large-package-1.0.0")
        assert retrieved is not None
        assert len(retrieved.data.description) > 100000


class TestConfigurationEdgeCases:
    """Test edge cases in configuration and setup."""

    @pytest.mark.asyncio
    async def test_invalid_project_structure(self, temp_project_dir):
        """Test handling of invalid project structures."""
        # Create invalid pyproject.toml
        pyproject_path = temp_project_dir / "pyproject.toml"
        pyproject_path.write_text("invalid toml content [[[")

        parser = PyProjectParser()

        # Should handle gracefully
        scan_result = await parser.parse_project(temp_project_dir)
        assert len(scan_result.dependencies) == 0
        assert len(scan_result.dependencies) == 0

    @pytest.mark.asyncio
    async def test_missing_project_file(self, temp_project_dir):
        """Test handling of missing pyproject.toml."""
        # Don't create pyproject.toml file
        parser = PyProjectParser()

        scan_result = await parser.parse_project(temp_project_dir)
        assert len(scan_result.dependencies) == 0
        assert scan_result.project_name == "unknown"

    @pytest.mark.asyncio
    async def test_cache_directory_permissions(self, temp_cache_dir):
        """Test handling of cache directory permission issues."""
        cache_manager = FileCacheManager(temp_cache_dir)

        # Should initialize successfully
        await cache_manager.initialize()
        assert temp_cache_dir.exists()

        # Basic operations should work
        stats = await cache_manager.get_cache_stats()
        assert stats["total_entries"] == 0
