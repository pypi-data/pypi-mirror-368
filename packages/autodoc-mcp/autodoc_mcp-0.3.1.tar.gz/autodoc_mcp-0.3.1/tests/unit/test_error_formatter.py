"""Unit tests for error formatting functionality."""

import re
from datetime import datetime
from pathlib import Path

from src.autodocs_mcp.core.error_formatter import (
    ErrorFormatter,
    ErrorSeverity,
    FormattedError,
    ResponseFormatter,
)
from src.autodocs_mcp.exceptions import (
    NetworkError,
    PackageNotFoundError,
    ProjectParsingError,
)


class TestFormattedError:
    """Test FormattedError dataclass."""

    def test_formatted_error_creation(self):
        """Test basic FormattedError creation."""
        error = FormattedError(
            message="Test error message",
            suggestion="Test suggestion",
            severity=ErrorSeverity.ERROR,
            error_code="test_error",
            context={"key": "value"},
            recoverable=True,
        )

        assert error.message == "Test error message"
        assert error.suggestion == "Test suggestion"
        assert error.severity == ErrorSeverity.ERROR
        assert error.error_code == "test_error"
        assert error.context == {"key": "value"}
        assert error.recoverable is True

    def test_formatted_error_defaults(self):
        """Test FormattedError with default values."""
        error = FormattedError(message="Test message")

        assert error.message == "Test message"
        assert error.suggestion is None
        assert error.severity == ErrorSeverity.ERROR
        assert error.error_code is None
        assert error.context is None
        assert error.recoverable is True


class TestErrorSeverity:
    """Test ErrorSeverity enum."""

    def test_severity_values(self):
        """Test all severity level values."""
        assert ErrorSeverity.INFO.value == "info"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.CRITICAL.value == "critical"


class TestErrorFormatter:
    """Test ErrorFormatter functionality."""

    def test_dependency_patterns_defined(self):
        """Test that dependency patterns are properly defined."""
        patterns = ErrorFormatter.DEPENDENCY_PATTERNS

        assert len(patterns) > 0
        # Check pattern structure
        for pattern, error_type in patterns:
            assert isinstance(pattern, str)
            assert isinstance(error_type, str)
            # Ensure patterns compile
            re.compile(pattern)


class TestDependencyParsingErrors:
    """Test dependency parsing error formatting."""

    def test_format_dependency_parsing_errors_empty_list(self):
        """Test formatting empty list of dependency errors."""
        result = ErrorFormatter.format_dependency_parsing_errors([])
        assert result == []

    def test_format_dependency_parsing_errors_single_failure(self):
        """Test formatting single dependency failure."""
        failed_deps = [
            {
                "dependency_string": "invalid-pkg-name!@#",
                "error": "Invalid package name format: 'invalid-pkg-name!@#'",
                "source": "dependencies",
            }
        ]

        result = ErrorFormatter.format_dependency_parsing_errors(failed_deps)

        assert len(result) == 1
        assert isinstance(result[0], FormattedError)
        assert result[0].error_code == "invalid_package_name"
        assert "invalid-pkg-name" in result[0].message

    def test_format_dependency_parsing_errors_multiple_failures(self):
        """Test formatting multiple dependency failures."""
        failed_deps = [
            {
                "dependency_string": "pkg[unclosed-bracket",
                "error": "Unclosed bracket in extras: 'pkg[unclosed-bracket'",
                "source": "dev-dependencies",
            },
            {
                "dependency_string": "",
                "error": "Empty dependency string",
                "source": "dependencies",
            },
        ]

        result = ErrorFormatter.format_dependency_parsing_errors(failed_deps)

        assert len(result) == 2
        assert result[0].error_code == "malformed_extras"
        assert result[1].error_code == "empty_dependency"

    def test_format_single_dependency_error_invalid_package_name(self):
        """Test formatting invalid package name error."""
        result = ErrorFormatter._format_single_dependency_error(
            "bad@pkg", "Invalid package name format: 'bad@pkg'", "dependencies"
        )

        assert result.error_code == "invalid_package_name"
        assert "bad@pkg" in result.message
        assert "dependencies" in result.message
        assert result.severity == ErrorSeverity.WARNING
        assert result.recoverable is True
        assert "bad-pkg" in result.suggestion  # Should suggest fix

    def test_format_single_dependency_error_malformed_extras(self):
        """Test formatting malformed extras error."""
        result = ErrorFormatter._format_single_dependency_error(
            "pkg[extra", "Unclosed bracket in extras: 'pkg[extra'", "dev-dependencies"
        )

        assert result.error_code == "malformed_extras"
        assert "pkg[extra" in result.message
        assert "dev-dependencies" in result.message
        assert result.severity == ErrorSeverity.WARNING
        assert "square brackets" in result.suggestion

    def test_format_single_dependency_error_invalid_version(self):
        """Test formatting invalid version error."""
        result = ErrorFormatter._format_single_dependency_error(
            "pkg>>1.0", "Invalid version specifier.*'pkg>>1.0'", "dependencies"
        )

        assert result.error_code == "invalid_version"
        assert "pkg>>1.0" in result.message
        assert result.severity == ErrorSeverity.WARNING
        assert "valid version operators" in result.suggestion

    def test_format_single_dependency_error_empty_dependency(self):
        """Test formatting empty dependency error."""
        result = ErrorFormatter._format_single_dependency_error(
            "", "Empty dependency string", "dependencies"
        )

        assert result.error_code == "empty_dependency"
        assert "Empty dependency" in result.message
        assert "dependencies" in result.message
        assert result.severity == ErrorSeverity.WARNING

    def test_format_single_dependency_error_unknown_pattern(self):
        """Test formatting unknown dependency error pattern."""
        result = ErrorFormatter._format_single_dependency_error(
            "unknown-issue", "Some unknown error message", "dependencies"
        )

        assert result.error_code == "dependency_parse_unknown"
        assert "unknown-issue" in result.message
        assert "dependencies" in result.message
        assert result.severity == ErrorSeverity.WARNING
        assert result.recoverable is True

    def test_create_dependency_error_by_type_invalid_package_name(self):
        """Test creating invalid package name error."""
        match = re.search(
            r"Invalid package name format: '([^']+)'",
            "Invalid package name format: 'bad@name'",
        )

        result = ErrorFormatter._create_dependency_error_by_type(
            "invalid_package_name", "bad@name", "dependencies", match
        )

        assert result.error_code == "invalid_package_name"
        assert result.context["original_name"] == "bad@name"
        assert result.context["source"] == "dependencies"

    def test_create_dependency_error_by_type_malformed_extras(self, mocker):
        """Test creating malformed extras error."""
        match = mocker.Mock()
        match.groups.return_value = ()

        result = ErrorFormatter._create_dependency_error_by_type(
            "malformed_extras", "pkg[extra", "dev-dependencies", match
        )

        assert result.error_code == "malformed_extras"
        assert result.context["original_dep"] == "pkg[extra"
        assert result.context["source"] == "dev-dependencies"

    def test_create_dependency_error_by_type_fallback(self, mocker):
        """Test creating error with unknown type falls back gracefully."""
        match = mocker.Mock()

        result = ErrorFormatter._create_dependency_error_by_type(
            "unknown_type", "test-dep", "dependencies", match
        )

        assert result.error_code == "dependency_parse_unknown"
        assert "test-dep" in result.message


class TestSuggestionGeneration:
    """Test suggestion generation methods."""

    def test_suggest_package_name_fix_basic(self):
        """Test basic package name fix suggestions."""
        result = ErrorFormatter._suggest_package_name_fix("bad@name!")
        assert result == "bad-name"

    def test_suggest_package_name_fix_multiple_hyphens(self):
        """Test package name fix with multiple consecutive special chars."""
        result = ErrorFormatter._suggest_package_name_fix("bad---name@@@")
        assert result == "bad-name"

    def test_suggest_package_name_fix_leading_trailing_hyphens(self):
        """Test package name fix removes leading/trailing hyphens."""
        result = ErrorFormatter._suggest_package_name_fix("-bad-name-")
        assert result == "bad-name"

    def test_suggest_package_name_fix_empty_result(self):
        """Test package name fix fallback for empty result."""
        result = ErrorFormatter._suggest_package_name_fix("@@@")
        assert result == "package-name"

    def test_suggest_extras_fix_valid_package(self):
        """Test extras fix suggestion with valid package name."""
        result = ErrorFormatter._suggest_extras_fix("requests[unclosed")
        assert result == "requests[extra1,extra2]>=1.0.0"

    def test_suggest_extras_fix_no_package_match(self):
        """Test extras fix suggestion with no package match."""
        result = ErrorFormatter._suggest_extras_fix("[@#$")
        assert result == "package[extra1,extra2]>=1.0.0"

    def test_suggest_version_fix_valid_package(self):
        """Test version fix suggestion with valid package name."""
        result = ErrorFormatter._suggest_version_fix("requests>>invalid")
        assert result == "requests>=1.0.0"

    def test_suggest_version_fix_no_package_match(self):
        """Test version fix suggestion with no package match."""
        result = ErrorFormatter._suggest_version_fix("@@invalid")
        assert result == "package>=1.0.0"


class TestNetworkErrorFormatting:
    """Test network error formatting."""

    def test_format_network_errors_empty_list(self):
        """Test formatting empty list of network errors."""
        result = ErrorFormatter.format_network_errors([])
        assert result == []

    def test_format_network_errors_package_not_found(self):
        """Test formatting PackageNotFoundError."""
        errors = [
            {
                "type": "PackageNotFoundError",
                "package": "nonexistent-pkg",
                "message": "Package not found",
                "suggestions": ["requests", "httpx"],
            }
        ]

        result = ErrorFormatter.format_network_errors(errors)

        assert len(result) == 1
        assert result[0].error_code == "package_not_found"
        assert "nonexistent-pkg" in result[0].message
        assert "requests" in result[0].suggestion
        assert result[0].severity == ErrorSeverity.ERROR
        assert result[0].recoverable is True

    def test_format_network_errors_package_not_found_no_suggestions(self):
        """Test formatting PackageNotFoundError without suggestions."""
        errors = [
            {
                "type": "PackageNotFoundError",
                "package": "nonexistent-pkg",
                "message": "Package not found",
                "suggestions": [],
            }
        ]

        result = ErrorFormatter.format_network_errors(errors)

        assert len(result) == 1
        assert "Did you mean:" not in result[0].suggestion
        assert "Check the package name" in result[0].suggestion

    def test_format_network_errors_network_error(self):
        """Test formatting NetworkError."""
        errors = [
            {
                "type": "NetworkError",
                "package": "requests",
                "message": "Connection timeout",
                "retry_suggested": True,
            }
        ]

        result = ErrorFormatter.format_network_errors(errors)

        assert len(result) == 1
        assert result[0].error_code == "network_error"
        assert "requests" in result[0].message
        assert "Connection timeout" in result[0].message
        assert "retried automatically" in result[0].suggestion
        assert result[0].severity == ErrorSeverity.ERROR

    def test_format_network_errors_network_error_no_retry(self):
        """Test formatting NetworkError without retry suggestion."""
        errors = [
            {
                "type": "NetworkError",
                "package": "requests",
                "message": "Connection failed",
                "retry_suggested": False,
            }
        ]

        result = ErrorFormatter.format_network_errors(errors)

        assert len(result) == 1
        assert "retried automatically" not in result[0].suggestion
        assert "internet connection" in result[0].suggestion

    def test_format_network_errors_generic_error(self):
        """Test formatting generic error type."""
        errors = [
            {
                "type": "UnknownError",
                "package": "test-pkg",
                "message": "Something went wrong",
            }
        ]

        result = ErrorFormatter.format_network_errors(errors)

        assert len(result) == 1
        assert result[0].error_code == "generic_error"
        assert "test-pkg" in result[0].message
        assert "Something went wrong" in result[0].message
        assert result[0].context["type"] == "UnknownError"


class TestExceptionFormatting:
    """Test exception formatting."""

    def test_format_exception_project_parsing_error(self):
        """Test formatting ProjectParsingError."""
        exc = ProjectParsingError("Invalid TOML", Path("/test/pyproject.toml"))

        result = ErrorFormatter.format_exception(exc)

        assert result.error_code == "project_parse_error"
        assert "Invalid TOML" in result.message
        assert result.severity == ErrorSeverity.CRITICAL
        assert result.recoverable is False
        assert result.context["file_path"] == "/test/pyproject.toml"

    def test_format_exception_project_parsing_error_no_path(self):
        """Test formatting ProjectParsingError without file path."""
        exc = ProjectParsingError("Invalid TOML", None)

        result = ErrorFormatter.format_exception(exc)

        assert result.context["file_path"] is None

    def test_format_exception_package_not_found_error(self):
        """Test formatting PackageNotFoundError."""
        exc = PackageNotFoundError("Package not found")
        context = {"package": "requests"}

        result = ErrorFormatter.format_exception(exc, context)

        assert result.error_code == "package_not_found"
        assert "requests" in result.message
        assert result.severity == ErrorSeverity.ERROR
        assert result.recoverable is True
        assert result.context == context

    def test_format_exception_package_not_found_error_no_context(self):
        """Test formatting PackageNotFoundError without context."""
        exc = PackageNotFoundError("Package not found")

        result = ErrorFormatter.format_exception(exc)

        assert "unknown" in result.message

    def test_format_exception_network_error(self):
        """Test formatting NetworkError."""
        exc = NetworkError("Connection failed")
        context = {"package": "httpx"}

        result = ErrorFormatter.format_exception(exc, context)

        assert result.error_code == "network_error"
        assert "Connection failed" in result.message
        assert result.severity == ErrorSeverity.ERROR
        assert result.recoverable is True
        assert "retried automatically" in result.suggestion

    def test_format_exception_generic_exception(self):
        """Test formatting generic exception."""
        exc = ValueError("Something went wrong")
        context = {"operation": "test"}

        result = ErrorFormatter.format_exception(exc, context)

        assert result.error_code == "unexpected_error"
        assert "Something went wrong" in result.message
        assert result.severity == ErrorSeverity.CRITICAL
        assert result.recoverable is False
        assert result.context["exception_type"] == "ValueError"

    def test_format_exception_no_context(self):
        """Test formatting exception without context."""
        exc = RuntimeError("Runtime issue")

        result = ErrorFormatter.format_exception(exc)

        assert result.error_code == "unexpected_error"
        assert "Runtime issue" in result.message
        assert result.context["exception_type"] == "RuntimeError"


class TestResponseFormatter:
    """Test ResponseFormatter functionality."""

    def test_format_scan_response_success(self, mocker):
        """Test formatting successful scan response."""
        # Mock scan result
        mock_result = mocker.Mock()
        mock_result.dependencies = [mocker.Mock(), mocker.Mock()]  # 2 dependencies
        mock_result.dependencies[0].model_dump.return_value = {
            "name": "requests",
            "version": ">=2.0.0",
        }
        mock_result.dependencies[1].model_dump.return_value = {
            "name": "httpx",
            "version": ">=0.24.0",
        }
        mock_result.failed_deps = []
        mock_result.successful_deps = 2
        mock_result.partial_success = False
        mock_result.project_name = "test-project"
        mock_result.project_path = Path("/test/project")
        mock_result.warnings = []
        mock_result.scan_timestamp = datetime(2025, 1, 8, 12, 0, 0)

        result = ResponseFormatter.format_scan_response(mock_result)

        assert result["success"] is True
        assert result["partial_success"] is False
        assert result["project_name"] == "test-project"
        assert result["project_path"] == "/test/project"
        assert len(result["dependencies"]) == 2
        assert result["dependency_count"] == 2
        assert len(result["errors"]) == 0
        assert result["scan_timestamp"] == "2025-01-08T12:00:00"

    def test_format_scan_response_with_errors(self, mocker):
        """Test formatting scan response with dependency errors."""
        # Mock scan result with failures
        mock_result = mocker.Mock()
        mock_result.dependencies = [mocker.Mock()]  # 1 successful dependency
        mock_result.dependencies[0].model_dump.return_value = {
            "name": "requests",
            "version": ">=2.0.0",
        }
        mock_result.failed_deps = [
            {
                "dependency_string": "bad@pkg",
                "error": "Invalid package name format: 'bad@pkg'",
                "source": "dependencies",
            }
        ]
        mock_result.successful_deps = 1
        mock_result.partial_success = True
        mock_result.project_name = "test-project"
        mock_result.project_path = Path("/test/project")
        mock_result.warnings = ["Some warning"]
        mock_result.scan_timestamp = datetime(2025, 1, 8, 12, 0, 0)

        result = ResponseFormatter.format_scan_response(mock_result)

        assert result["success"] is True  # Has some dependencies
        assert result["partial_success"] is True
        assert len(result["dependencies"]) == 1
        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "invalid_package_name"
        assert result["errors"][0]["severity"] == "warning"
        assert len(result["suggestions"]) == 1

    def test_format_scan_response_no_dependencies(self, mocker):
        """Test formatting scan response with no successful dependencies."""
        # Mock scan result with no successful dependencies
        mock_result = mocker.Mock()
        mock_result.dependencies = []
        mock_result.failed_deps = [
            {
                "dependency_string": "",
                "error": "Empty dependency string",
                "source": "dependencies",
            }
        ]
        mock_result.successful_deps = 0
        mock_result.partial_success = False
        mock_result.project_name = "test-project"
        mock_result.project_path = Path("/test/project")
        mock_result.warnings = []
        mock_result.scan_timestamp = datetime(2025, 1, 8, 12, 0, 0)

        result = ResponseFormatter.format_scan_response(mock_result)

        assert result["success"] is False
        assert result["dependency_count"] == 0
        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "empty_dependency"

    def test_format_scan_response_error_structure(self, mocker):
        """Test the structure of formatted errors in scan response."""
        # Mock scan result with multiple error types
        mock_result = mocker.Mock()
        mock_result.dependencies = []
        mock_result.failed_deps = [
            {
                "dependency_string": "bad@pkg",
                "error": "Invalid package name format: 'bad@pkg'",
                "source": "dependencies",
            },
            {
                "dependency_string": "pkg[unclosed",
                "error": "Unclosed bracket in extras: 'pkg[unclosed'",
                "source": "dev-dependencies",
            },
        ]
        mock_result.successful_deps = 0
        mock_result.partial_success = False
        mock_result.project_name = "test-project"
        mock_result.project_path = Path("/test/project")
        mock_result.warnings = []
        mock_result.scan_timestamp = datetime(2025, 1, 8, 12, 0, 0)

        result = ResponseFormatter.format_scan_response(mock_result)

        # Check error structure
        assert len(result["errors"]) == 2

        error1 = result["errors"][0]
        assert "message" in error1
        assert "suggestion" in error1
        assert "severity" in error1
        assert "code" in error1
        assert "recoverable" in error1

        # Check suggestions are collected
        assert len(result["suggestions"]) == 2
        assert all(suggestion for suggestion in result["suggestions"])


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_format_dependency_parsing_errors_missing_keys(self):
        """Test handling of malformed failure dictionaries."""
        failed_deps = [
            {
                # Missing some keys
                "dependency_string": "test-pkg",
                # "error" key missing
                "source": "dependencies",
            }
        ]

        result = ErrorFormatter.format_dependency_parsing_errors(failed_deps)

        assert len(result) == 1
        # Should handle gracefully with defaults
        assert result[0].error_code == "dependency_parse_unknown"

    def test_format_network_errors_missing_keys(self):
        """Test handling of malformed network error dictionaries."""
        errors = [
            {
                "type": "NetworkError",
                # Missing "package" and "message" keys
            }
        ]

        result = ErrorFormatter.format_network_errors(errors)

        assert len(result) == 1
        assert "unknown" in result[0].message
        assert result[0].error_code == "network_error"

    def test_pattern_matching_edge_cases(self):
        """Test regex pattern matching with edge cases."""
        # Test with pattern that might not match
        result = ErrorFormatter._format_single_dependency_error(
            "test", "Some completely different error message", "dependencies"
        )

        assert result.error_code == "dependency_parse_unknown"
        assert result.recoverable is True

    def test_suggestion_generation_edge_cases(self):
        """Test suggestion generation with edge cases."""
        # Empty string
        result = ErrorFormatter._suggest_package_name_fix("")
        assert result == "package-name"

        # Only special characters
        result = ErrorFormatter._suggest_package_name_fix("@#$%")
        assert result == "package-name"

        # Very long string
        long_name = "a" * 200 + "@" + "b" * 200
        result = ErrorFormatter._suggest_package_name_fix(long_name)
        assert "@" not in result
        assert "-" in result
