"""Security validation and sanitization functions."""

import re
from pathlib import Path
from urllib.parse import urlparse

# Trusted PyPI domains for URL validation
TRUSTED_PYPI_DOMAINS: set[str] = {
    "pypi.org",
    "test.pypi.org",
    "pypi.python.org",  # Legacy support
}


def validate_pypi_url(url: str) -> str:
    """Validate PyPI URL against allowlist of trusted domains.

    Args:
        url: The PyPI URL to validate

    Returns:
        The validated URL

    Raises:
        ValueError: If URL is invalid or uses untrusted domain
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string")

    try:
        parsed = urlparse(url.strip())

        if not parsed.scheme or parsed.scheme not in ("http", "https"):
            raise ValueError(
                f"Invalid URL scheme: {parsed.scheme}. Must be http or https"
            )

        if not parsed.netloc:
            raise ValueError("URL must have a valid domain")

        # Check against trusted domains
        domain = parsed.netloc.lower()
        if domain not in TRUSTED_PYPI_DOMAINS and not domain.startswith("localhost"):
            raise ValueError(
                f"Untrusted PyPI domain: {domain}. Allowed domains: {TRUSTED_PYPI_DOMAINS}"
            )

        # Ensure HTTPS for production (except localhost)
        if parsed.scheme == "http" and not domain.startswith("localhost"):
            raise ValueError(
                "HTTP URLs not allowed for production PyPI domains. Use HTTPS"
            )

        return url.strip()

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid PyPI URL '{url}': {e}") from e


def sanitize_cache_key(cache_key: str) -> str:
    """Sanitize cache key to prevent path traversal attacks.

    Args:
        cache_key: The cache key to sanitize

    Returns:
        The sanitized cache key

    Raises:
        ValueError: If cache key is invalid after sanitization
    """
    if not isinstance(cache_key, str):
        raise ValueError("Cache key must be a string")

    # Remove dangerous characters and path components
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", cache_key)

    # Collapse multiple dots to prevent ../ traversal
    sanitized = re.sub(r"\.\.+", ".", sanitized)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Ensure reasonable length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]

    # Validate final result
    if not sanitized or sanitized in {"", ".", ".."}:
        raise ValueError(f"Invalid cache key after sanitization: '{cache_key}'")

    # Check for reserved Windows filenames
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
    if sanitized.upper() in reserved_names:
        raise ValueError(
            f"Invalid cache key after sanitization (reserved name): '{cache_key}'"
        )

    return sanitized


class InputValidator:
    """Centralized input validation for all user inputs."""

    @staticmethod
    def validate_package_name(name: str) -> str:
        """Validate PyPI package name format.

        Args:
            name: Package name to validate

        Returns:
            Normalized package name (lowercase)

        Raises:
            ValueError: If package name is invalid
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Package name must be a non-empty string")

        # PyPI naming rules: https://packaging.python.org/en/latest/specifications/name-normalization/
        if not re.match(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$", name):
            raise ValueError(
                f"Invalid package name format: '{name}'. Must start and end with alphanumeric characters"
            )

        if len(name) > 214:  # PyPI limit
            raise ValueError(f"Package name too long: {len(name)} > 214 characters")

        return name.lower()  # Normalize case

    @staticmethod
    def validate_version_constraint(constraint: str) -> str:
        """Validate version constraint syntax.

        Args:
            constraint: Version constraint to validate

        Returns:
            The validated constraint

        Raises:
            ValueError: If version constraint is invalid
        """
        if not isinstance(constraint, str):
            raise ValueError("Version constraint must be a string")

        if not constraint.strip():
            raise ValueError("Version constraint cannot be empty")

        try:
            from packaging.specifiers import SpecifierSet

            SpecifierSet(constraint)
            return constraint.strip()
        except Exception as e:
            raise ValueError(f"Invalid version constraint '{constraint}': {e}") from e

    @staticmethod
    def validate_project_path(path: str) -> Path:
        """Validate and resolve project path.

        Args:
            path: Project path to validate

        Returns:
            Resolved Path object

        Raises:
            ValueError: If path is invalid
        """
        if not isinstance(path, str) or not path.strip():
            raise ValueError("Project path must be a non-empty string")

        try:
            resolved = Path(path).resolve()
            if not resolved.exists():
                raise ValueError(f"Path does not exist: {path}")
            if not resolved.is_dir():
                raise ValueError(f"Path is not a directory: {path}")
            return resolved
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid project path '{path}': {e}") from e
