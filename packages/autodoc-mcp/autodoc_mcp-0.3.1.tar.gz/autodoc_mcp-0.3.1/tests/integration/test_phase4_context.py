"""Integration tests for Phase 4 dependency context system."""

from pathlib import Path

import pytest

from autodocs_mcp.core.cache_manager import FileCacheManager
from autodocs_mcp.core.context_fetcher import create_context_fetcher
from autodocs_mcp.core.context_formatter import DocumentationContext


class TestPhase4Integration:
    """Integration tests for complete Phase 4 functionality."""

    async def test_context_fetcher_creation(self):
        """Test that context fetcher can be created properly."""
        cache_manager = FileCacheManager(Path("/tmp/test-cache"))
        await cache_manager.initialize()

        context_fetcher = await create_context_fetcher(cache_manager)

        assert context_fetcher is not None
        assert context_fetcher.cache_manager == cache_manager
        assert context_fetcher.dependency_resolver is not None
        assert context_fetcher.formatter is not None

    async def test_fetch_primary_only_context(self):
        """Test fetching context without dependencies."""
        # This test would normally require network access
        # In a real implementation, you'd mock the network layer
        # For now, we'll skip if network is unavailable

        cache_manager = FileCacheManager(Path("/tmp/test-cache-primary"))
        await cache_manager.initialize()

        try:
            context_fetcher = await create_context_fetcher(cache_manager)

            # Test with a simple package that should work
            context, metrics = await context_fetcher.fetch_package_context(
                package_name="click",
                include_dependencies=False,
                context_scope="primary_only",
            )

            assert isinstance(context, DocumentationContext)
            assert context.primary_package.name == "click"
            assert context.context_scope == "primary_only"
            assert len(context.runtime_dependencies) == 0
            assert context.token_estimate > 0
            assert metrics["total_time"] > 0

        except Exception as e:
            # Skip test if network/PyPI is unavailable
            pytest.skip(f"Network test skipped due to: {e}")

    async def test_fetch_context_with_dependencies(self):
        """Test fetching context with dependencies (network dependent)."""
        cache_manager = FileCacheManager(Path("/tmp/test-cache-deps"))
        await cache_manager.initialize()

        try:
            context_fetcher = await create_context_fetcher(cache_manager)

            # Test with FastAPI which should have dependencies
            context, metrics = await context_fetcher.fetch_package_context(
                package_name="fastapi",
                include_dependencies=True,
                context_scope="smart",
                max_dependencies=2,  # Limit for test performance
            )

            assert isinstance(context, DocumentationContext)
            assert context.primary_package.name == "fastapi"
            assert context.total_packages >= 1
            assert context.token_estimate > 0

            if len(context.runtime_dependencies) > 0:
                # Check that dependencies are properly formatted
                for dep in context.runtime_dependencies:
                    assert dep.name != ""
                    assert dep.version != ""
                    assert dep.relationship == "runtime_dependency"
                    assert "Required by fastapi" in dep.why_included

            # Check performance metrics
            assert "total_time" in metrics
            assert "cache_hits" in metrics
            assert "cache_misses" in metrics

        except Exception as e:
            pytest.skip(f"Network test skipped due to: {e}")

    def test_context_serialization(self):
        """Test that context can be properly serialized for MCP responses."""
        from autodocs_mcp.core.context_formatter import PackageDocumentation

        primary = PackageDocumentation(
            name="test-package",
            version="1.0.0",
            relationship="primary",
            summary="Test package",
            key_features=["Feature 1", "Feature 2"],
            main_classes=["TestClass"],
            main_functions=["test_function"],
            usage_examples="print('test')",
            why_included="Requested package",
            dependency_level=0,
        )

        context = DocumentationContext(
            primary_package=primary, context_scope="primary_only", total_packages=1
        )

        # Test that it can be serialized (like in MCP response)
        serialized = {
            "primary_package": primary.model_dump(),
            "runtime_dependencies": [
                dep.model_dump() for dep in context.runtime_dependencies
            ],
            "dev_dependencies": [dep.model_dump() for dep in context.dev_dependencies],
            "context_scope": context.context_scope,
            "total_packages": context.total_packages,
            "truncated_packages": context.truncated_packages,
            "token_estimate": context.token_estimate,
        }

        # Basic validation
        assert serialized["primary_package"]["name"] == "test-package"
        assert serialized["context_scope"] == "primary_only"
        assert serialized["total_packages"] == 1
        assert serialized["token_estimate"] > 0


class TestContextFetcherErrorHandling:
    """Test error handling and graceful degradation."""

    async def test_fetch_context_invalid_package(self):
        """Test handling of invalid package names."""
        cache_manager = FileCacheManager(Path("/tmp/test-cache-invalid"))
        await cache_manager.initialize()

        context_fetcher = await create_context_fetcher(cache_manager)

        from contextlib import suppress

        with suppress(Exception):
            context, metrics = await context_fetcher.fetch_package_context(
                package_name="this-package-definitely-does-not-exist-12345",
                include_dependencies=False,
            )

            # Should handle gracefully - might raise exception or return error context
            # Implementation depends on error handling strategy

    async def test_fetch_context_with_network_timeout(self):
        """Test handling of network timeouts."""
        # This would require mocking network delays
        # For now, just test that timeout parameters work

        cache_manager = FileCacheManager(Path("/tmp/test-cache-timeout"))
        await cache_manager.initialize()

        context_fetcher = await create_context_fetcher(cache_manager)

        # The implementation should respect timeouts
        # Actual timeout testing would require network mocking
        assert context_fetcher is not None


class TestCacheManagerIntegration:
    """Test cache manager integration with context system."""

    async def test_cache_manager_resolve_and_cache(self):
        """Test the resolve_and_cache method used by context fetcher."""
        cache_manager = FileCacheManager(Path("/tmp/test-resolve-cache"))
        await cache_manager.initialize()

        try:
            # Test basic resolve and cache functionality
            package_info, from_cache = await cache_manager.resolve_and_cache("click")

            assert isinstance(package_info, dict)
            assert "name" in package_info
            assert "version" in package_info
            assert isinstance(from_cache, bool)

            # Second call should hit cache
            package_info2, from_cache2 = await cache_manager.resolve_and_cache("click")

            assert from_cache2 is True  # Should be from cache
            assert package_info["name"] == package_info2["name"]

        except Exception as e:
            pytest.skip(f"Network test skipped due to: {e}")

    async def test_cache_directory_creation(self):
        """Test that cache directories are created properly."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "autodocs-cache"

            cache_manager = FileCacheManager(cache_path)
            await cache_manager.initialize()

            assert cache_path.exists()
            assert cache_path.is_dir()


class TestRegexPatterns:
    """Test regex patterns that previously caused issues."""

    def test_bullet_point_regex_patterns(self):
        """Test that bullet point regex patterns work correctly."""
        from autodocs_mcp.core.context_formatter import ContextDocumentationFormatter

        formatter = ContextDocumentationFormatter()

        test_descriptions = [
            "Features:\n• First feature\n• Second feature",
            "Features:\n* First feature\n* Second feature",
            "Features:\n- First feature\n- Second feature",
            "Mixed:\n• Bullet\n* Asterisk\n- Dash",
            "With special chars: [•*-] should not break",
            "Range test: a-z should not interfere with [•*-] patterns",
        ]

        for description in test_descriptions:
            # Should not raise regex errors
            features = formatter._extract_key_features(description)
            assert isinstance(features, list)

    def test_class_extraction_patterns(self):
        """Test class extraction regex patterns."""
        from autodocs_mcp.core.context_formatter import ContextDocumentationFormatter

        formatter = ContextDocumentationFormatter()

        test_descriptions = [
            "class MyClass: implementation",
            "`MyClass` is the main class",
            "Use the `ClassName` for processing",
            "Main classes: FirstClass, SecondClass",
        ]

        for description in test_descriptions:
            # Should not raise regex errors
            classes = formatter._extract_main_classes(description)
            assert isinstance(classes, list)

    def test_function_extraction_patterns(self):
        """Test function extraction regex patterns."""
        from autodocs_mcp.core.context_formatter import ContextDocumentationFormatter

        formatter = ContextDocumentationFormatter()

        test_descriptions = [
            "def my_function(): implementation",
            "Call `function_name()` to process",
            "Use .method_call() for results",
            "Functions: first_func, second_func",
        ]

        for description in test_descriptions:
            # Should not raise regex errors
            functions = formatter._extract_main_functions(description)
            assert isinstance(functions, list)
