"""User-friendly error message formatting with actionable suggestions."""

import re
from dataclasses import dataclass
from enum import Enum
from re import Match
from typing import Any

from ..exceptions import (
    NetworkError,
    PackageNotFoundError,
    ProjectParsingError,
)


class ErrorSeverity(Enum):
    """Error severity levels for UI/UX purposes."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class FormattedError:
    """User-friendly error with context and suggestions."""

    message: str
    suggestion: str | None = None
    severity: ErrorSeverity = ErrorSeverity.ERROR
    error_code: str | None = None
    context: dict[str, Any] | None = None
    recoverable: bool = True


class ErrorFormatter:
    """Converts technical errors to user-friendly messages."""

    # Common dependency parsing error patterns
    DEPENDENCY_PATTERNS = [
        (r"Invalid package name format: '([^']+)'", "invalid_package_name"),
        (r"Unclosed bracket in extras: '([^']+)'", "malformed_extras"),
        (r"Empty dependency string", "empty_dependency"),
        (r"Malformed extras in '([^']+)'", "malformed_extras"),
        (r"Invalid version specifier.*'([^']+)'", "invalid_version"),
    ]

    @classmethod
    def format_dependency_parsing_errors(
        cls, failed_deps: list[dict[str, Any]]
    ) -> list[FormattedError]:
        """Format dependency parsing errors with suggestions."""
        formatted_errors = []

        for failure in failed_deps:
            dep_str = failure.get("dependency_string", "unknown")
            error_msg = failure.get("error", "")
            source = failure.get("source", "unknown")

            formatted = cls._format_single_dependency_error(dep_str, error_msg, source)
            formatted_errors.append(formatted)

        return formatted_errors

    @classmethod
    def _format_single_dependency_error(
        cls, dep_str: str, error_msg: str, source: str
    ) -> FormattedError:
        """Format a single dependency parsing error."""

        # Check against known patterns
        for pattern, error_type in cls.DEPENDENCY_PATTERNS:
            match = re.search(pattern, error_msg)
            if match:
                return cls._create_dependency_error_by_type(
                    error_type, dep_str, source, match
                )

        # Fallback for unknown errors
        return FormattedError(
            message=f"Could not parse dependency '{dep_str}' from {source} section",
            suggestion=f"Check the syntax of '{dep_str}'. Common formats: package>=1.0.0, package[extra1,extra2]>=1.0.0",
            severity=ErrorSeverity.WARNING,
            error_code="dependency_parse_unknown",
            recoverable=True,
        )

    @classmethod
    def _create_dependency_error_by_type(
        cls, error_type: str, dep_str: str, source: str, match: Match[str]
    ) -> FormattedError:
        """Create specific error messages based on error type."""

        if error_type == "invalid_package_name":
            package_name = match.group(1) if match.groups() else dep_str
            return FormattedError(
                message=f"Invalid package name '{package_name}' in {source} dependencies",
                suggestion=f"Package names can only contain letters, numbers, hyphens, periods, and underscores. Try: {cls._suggest_package_name_fix(package_name)}",
                severity=ErrorSeverity.WARNING,
                error_code="invalid_package_name",
                context={"original_name": package_name, "source": source},
            )

        elif error_type == "malformed_extras":
            return FormattedError(
                message=f"Malformed extras syntax in '{dep_str}' from {source} section",
                suggestion=f"Use square brackets for extras: {cls._suggest_extras_fix(dep_str)}",
                severity=ErrorSeverity.WARNING,
                error_code="malformed_extras",
                context={"original_dep": dep_str, "source": source},
            )

        elif error_type == "invalid_version":
            return FormattedError(
                message=f"Invalid version specifier in '{dep_str}' from {source} section",
                suggestion=f"Use valid version operators: {cls._suggest_version_fix(dep_str)}",
                severity=ErrorSeverity.WARNING,
                error_code="invalid_version",
                context={"original_dep": dep_str, "source": source},
            )

        elif error_type == "empty_dependency":
            return FormattedError(
                message=f"Empty dependency entry found in {source} section",
                suggestion="Remove empty strings from your dependencies list",
                severity=ErrorSeverity.WARNING,
                error_code="empty_dependency",
                context={"source": source},
            )

        # Fallback
        return FormattedError(
            message=f"Could not parse '{dep_str}' from {source} section",
            suggestion="Check dependency syntax and try again",
            severity=ErrorSeverity.WARNING,
            error_code="dependency_parse_unknown",
        )

    @classmethod
    def _suggest_package_name_fix(cls, name: str) -> str:
        """Suggest a fixed package name."""
        # Replace common problematic characters
        fixed = re.sub(r"[^A-Za-z0-9._-]", "-", name)
        fixed = re.sub(r"--+", "-", fixed)  # Replace multiple hyphens
        fixed = fixed.strip("-")  # Remove leading/trailing hyphens
        return fixed or "package-name"

    @classmethod
    def _suggest_extras_fix(cls, dep_str: str) -> str:
        """Suggest a fixed extras syntax."""
        # Extract package name before any brackets or version specs
        package_match = re.match(r"^([A-Za-z0-9._-]+)", dep_str)
        if package_match:
            return f"{package_match.group(1)}[extra1,extra2]>=1.0.0"
        return "package[extra1,extra2]>=1.0.0"

    @classmethod
    def _suggest_version_fix(cls, dep_str: str) -> str:
        """Suggest a fixed version syntax."""
        # Extract package name
        package_match = re.match(r"^([A-Za-z0-9._-]+)", dep_str)
        if package_match:
            return f"{package_match.group(1)}>=1.0.0"
        return "package>=1.0.0"

    @classmethod
    def format_network_errors(
        cls, errors: list[dict[str, Any]]
    ) -> list[FormattedError]:
        """Format network-related errors with suggestions."""
        formatted_errors = []

        for error in errors:
            error_type = error.get("type", "")
            package = error.get("package", "unknown")
            message = error.get("message", "")

            if error_type == "PackageNotFoundError":
                suggestions = error.get("suggestions", [])
                suggestion_text = ""
                if suggestions:
                    suggestion_text = f" Did you mean: {', '.join(suggestions[:3])}?"

                formatted_errors.append(
                    FormattedError(
                        message=f"Package '{package}' not found on PyPI",
                        suggestion=f"Check the package name spelling.{suggestion_text}",
                        severity=ErrorSeverity.ERROR,
                        error_code="package_not_found",
                        context={"package": package, "suggestions": suggestions},
                        recoverable=True,
                    )
                )

            elif error_type == "NetworkError":
                retry_suggested = error.get("retry_suggested", False)
                suggestion = "Check your internet connection and try again."
                if retry_suggested:
                    suggestion += " The request will be retried automatically."

                formatted_errors.append(
                    FormattedError(
                        message=f"Network error while fetching '{package}': {message}",
                        suggestion=suggestion,
                        severity=ErrorSeverity.ERROR,
                        error_code="network_error",
                        context={"package": package},
                        recoverable=True,
                    )
                )

            else:
                # Generic error formatting
                formatted_errors.append(
                    FormattedError(
                        message=f"Error processing '{package}': {message}",
                        suggestion="Review the error details and try again.",
                        severity=ErrorSeverity.ERROR,
                        error_code="generic_error",
                        context={"package": package, "type": error_type},
                    )
                )

        return formatted_errors

    @classmethod
    def format_exception(
        cls, exc: Exception, context: dict[str, Any] | None = None
    ) -> FormattedError:
        """Format any exception into a user-friendly error."""

        if isinstance(exc, ProjectParsingError):
            return FormattedError(
                message=f"Could not parse project file: {exc}",
                suggestion="Check your pyproject.toml file for syntax errors",
                severity=ErrorSeverity.CRITICAL,
                error_code="project_parse_error",
                context={"file_path": str(exc.file_path) if exc.file_path else None},
                recoverable=False,
            )

        elif isinstance(exc, PackageNotFoundError):
            package = context.get("package", "unknown") if context else "unknown"
            return FormattedError(
                message=f"Package '{package}' not found",
                suggestion="Verify the package name and check if it exists on PyPI",
                severity=ErrorSeverity.ERROR,
                error_code="package_not_found",
                context=context,
                recoverable=True,
            )

        elif isinstance(exc, NetworkError):
            return FormattedError(
                message=f"Network error: {exc}",
                suggestion="Check your internet connection. The operation will be retried automatically.",
                severity=ErrorSeverity.ERROR,
                error_code="network_error",
                context=context,
                recoverable=True,
            )

        else:
            return FormattedError(
                message=f"Unexpected error: {exc}",
                suggestion="This may be a system issue. Please try again or report if the problem persists.",
                severity=ErrorSeverity.CRITICAL,
                error_code="unexpected_error",
                context={"exception_type": type(exc).__name__},
                recoverable=False,
            )


class ResponseFormatter:
    """Format complete responses with errors, warnings, and suggestions."""

    @classmethod
    def format_scan_response(cls, result: Any) -> dict[str, Any]:
        """Format scan results with user-friendly error messages."""

        # Format dependency parsing errors
        formatted_dependency_errors = ErrorFormatter.format_dependency_parsing_errors(
            result.failed_deps
        )

        # Create suggestions summary
        suggestions = [
            err.suggestion for err in formatted_dependency_errors if err.suggestion
        ]

        return {
            "success": len(result.dependencies) > 0,
            "partial_success": result.partial_success,
            "project_name": result.project_name,
            "project_path": str(result.project_path),
            # Successful results
            "dependencies": [dep.model_dump() for dep in result.dependencies],
            "dependency_count": result.successful_deps,
            # Error information (user-friendly)
            "errors": [
                {
                    "message": err.message,
                    "suggestion": err.suggestion,
                    "severity": err.severity.value,
                    "code": err.error_code,
                    "recoverable": err.recoverable,
                }
                for err in formatted_dependency_errors
            ],
            # Legacy warning format (for backwards compatibility)
            "warnings": result.warnings,
            # Actionable suggestions summary
            "suggestions": suggestions,
            "scan_timestamp": result.scan_timestamp.isoformat(),
        }
