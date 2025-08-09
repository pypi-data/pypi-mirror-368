"""Tests for context documentation formatter."""

from autodocs_mcp.core.context_formatter import (
    ContextDocumentationFormatter,
    ContextWindowManager,
    DocumentationContext,
    PackageDocumentation,
)


class TestContextDocumentationFormatter:
    """Test context documentation formatter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = ContextDocumentationFormatter()

    def test_format_primary_package(self):
        """Test formatting primary package documentation."""
        package_info = {
            "name": "test-package",
            "version": "1.0.0",
            "summary": "A test package for testing",
            "description": """
            This is a test package.

            Features:
            • Feature one
            • Feature two
            * Another feature
            - Yet another feature

            Main classes: TestClass, AnotherClass
            Main functions: test_function, another_function

            ```python
            from test_package import TestClass
            obj = TestClass()
            ```
            """,
        }

        docs = self.formatter.format_primary_package(package_info)

        assert docs.name == "test-package"
        assert docs.version == "1.0.0"
        assert docs.relationship == "primary"
        assert docs.why_included == "Requested package"
        assert docs.dependency_level == 0
        assert "A test package for testing" in docs.summary
        assert len(docs.key_features) > 0
        assert "Feature one" in docs.key_features
        assert "Feature two" in docs.key_features
        assert docs.usage_examples is not None

    def test_format_dependency_package(self):
        """Test formatting dependency package documentation."""
        package_info = {
            "name": "dep-package",
            "version": "2.0.0",
            "summary": "A dependency package for testing",
            "description": "Simple dependency with minimal features.",
        }

        docs = self.formatter.format_dependency_package(
            package_info, "primary-package", 1
        )

        assert docs.name == "dep-package"
        assert docs.version == "2.0.0"
        assert docs.relationship == "runtime_dependency"
        assert docs.why_included == "Required by primary-package"
        assert docs.dependency_level == 1

    def test_regex_patterns_dont_crash(self):
        """Test that regex patterns handle various inputs without crashing."""
        test_descriptions = [
            "Simple description with no special characters",
            "Description with • bullet points",
            "Description with * asterisk bullets",
            "Description with - dash bullets",
            "Description with [•*-] character classes that caused issues",
            "Mixed content:\n• Bullet one\n* Bullet two\n- Bullet three",
            "Numbered list:\n1. Item one\n2. Item two\n3. Item three",
            "Code blocks:\n```python\nprint('hello')\n```",
            "Class definitions: class MyClass, class AnotherClass",
            "Function calls: my_function(), another_function(args)",
        ]

        for description in test_descriptions:
            package_info = {
                "name": "test-pkg",
                "version": "1.0.0",
                "summary": "Test",
                "description": description,
            }

            # Should not raise any exceptions
            docs = self.formatter.format_primary_package(package_info)
            assert docs.name == "test-pkg"

    def test_extract_key_features(self):
        """Test key feature extraction from descriptions."""
        description = """
        This package provides:
        • Automatic documentation generation
        • Smart dependency resolution
        • Performance optimization
        * Concurrent processing
        - Error handling

        It supports advanced features like caching and validation.
        """

        features = self.formatter._extract_key_features(description)

        assert len(features) > 0
        assert "Automatic documentation generation" in features
        assert "Smart dependency resolution" in features
        assert "Performance optimization" in features

    def test_extract_main_classes(self):
        """Test class name extraction from descriptions."""
        description = """
        Main classes include:
        - `DocumentationContext` for context management
        - class PackageResolver for resolution
        - The `ContextFormatter` class handles formatting
        """

        classes = self.formatter._extract_main_classes(description)

        assert "DocumentationContext" in classes
        assert "PackageResolver" in classes
        assert "ContextFormatter" in classes

    def test_extract_main_functions(self):
        """Test function name extraction from descriptions."""
        description = """
        Key functions:
        - `format_documentation()` formats docs
        - def resolve_dependencies() resolves deps
        - Call `get_context()` to retrieve context
        - Use .fetch_package() for fetching
        """

        functions = self.formatter._extract_main_functions(description)

        assert "format_documentation" in functions
        assert "resolve_dependencies" in functions
        assert "get_context" in functions
        assert "fetch_package" in functions

    def test_token_estimate(self):
        """Test token estimation for documentation."""
        docs = PackageDocumentation(
            name="test-package",
            version="1.0.0",
            relationship="primary",
            summary="Short summary",
            key_features=["Feature one", "Feature two"],
            main_classes=["ClassOne", "ClassTwo"],
            main_functions=["func_one", "func_two"],
            usage_examples="Simple example code",
            why_included="Test",
            dependency_level=0,
        )

        tokens = docs.token_estimate
        assert tokens > 0
        assert isinstance(tokens, int)


class TestContextWindowManager:
    """Test context window management functionality."""

    def test_fit_to_window_no_truncation_needed(self):
        """Test when context fits within token limits."""
        primary = PackageDocumentation(
            name="primary",
            version="1.0.0",
            relationship="primary",
            summary="Short",
            why_included="Test",
        )

        dep1 = PackageDocumentation(
            name="dep1",
            version="1.0.0",
            relationship="runtime_dependency",
            summary="Short dep",
            why_included="Required",
        )

        context = DocumentationContext(
            primary_package=primary, runtime_dependencies=[dep1]
        )

        # Large token limit - should fit
        result = ContextWindowManager.fit_to_window(context, max_tokens=50000)

        assert len(result.runtime_dependencies) == 1
        assert len(result.truncated_packages) == 0

    def test_fit_to_window_with_truncation(self):
        """Test when context needs truncation to fit."""
        primary = PackageDocumentation(
            name="primary",
            version="1.0.0",
            relationship="primary",
            summary="Primary package summary",
            why_included="Test",
        )

        # Create dependencies with long content
        deps = []
        for i in range(3):
            dep = PackageDocumentation(
                name=f"dep{i}",
                version="1.0.0",
                relationship="runtime_dependency",
                summary="Very long dependency summary " * 50,  # Make it long
                why_included="Required",
            )
            deps.append(dep)

        context = DocumentationContext(
            primary_package=primary, runtime_dependencies=deps
        )

        # Small token limit - should truncate
        result = ContextWindowManager.fit_to_window(context, max_tokens=100)

        # Should keep primary but truncate some dependencies
        assert len(result.runtime_dependencies) < len(deps)
        assert len(result.truncated_packages) > 0
        assert result.token_estimate <= 100


class TestDocumentationContext:
    """Test documentation context model."""

    def test_token_estimate_property(self):
        """Test total token estimation."""
        primary = PackageDocumentation(
            name="primary",
            version="1.0.0",
            relationship="primary",
            summary="Primary summary",
            why_included="Test",
        )

        dep = PackageDocumentation(
            name="dep",
            version="1.0.0",
            relationship="runtime_dependency",
            summary="Dependency summary",
            why_included="Required",
        )

        context = DocumentationContext(
            primary_package=primary, runtime_dependencies=[dep]
        )

        total_tokens = context.token_estimate
        expected_tokens = primary.token_estimate + dep.token_estimate

        assert total_tokens == expected_tokens
        assert total_tokens > 0

    def test_all_packages_property(self):
        """Test all packages property includes all types."""
        primary = PackageDocumentation(
            name="primary",
            version="1.0.0",
            relationship="primary",
            summary="Primary",
            why_included="Test",
        )

        runtime_dep = PackageDocumentation(
            name="runtime",
            version="1.0.0",
            relationship="runtime_dependency",
            summary="Runtime dep",
            why_included="Required",
        )

        dev_dep = PackageDocumentation(
            name="dev",
            version="1.0.0",
            relationship="dev_dependency",
            summary="Dev dep",
            why_included="Development",
        )

        context = DocumentationContext(
            primary_package=primary,
            runtime_dependencies=[runtime_dep],
            dev_dependencies=[dev_dep],
        )

        all_packages = context.all_packages

        assert len(all_packages) == 3
        assert primary in all_packages
        assert runtime_dep in all_packages
        assert dev_dep in all_packages
