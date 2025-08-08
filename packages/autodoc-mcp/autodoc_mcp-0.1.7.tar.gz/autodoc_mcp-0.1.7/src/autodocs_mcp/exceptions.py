"""Custom exceptions for AutoDocs MCP Server."""

from pathlib import Path


class AutoDocsError(Exception):
    """Base exception for all AutoDocs errors."""

    pass


class ProjectParsingError(AutoDocsError):
    """Errors related to project file parsing."""

    def __init__(
        self,
        message: str,
        file_path: Path | None = None,
        line_number: int | None = None,
    ):
        super().__init__(message)
        self.file_path = file_path
        self.line_number = line_number


class NetworkError(AutoDocsError):
    """Network-related errors with retry information."""

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class PackageNotFoundError(AutoDocsError):
    """Package not found on PyPI."""

    pass


class CacheError(AutoDocsError):
    """Cache-related errors."""

    pass
