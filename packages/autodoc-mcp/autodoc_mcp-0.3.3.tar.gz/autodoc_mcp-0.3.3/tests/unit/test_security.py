"""Tests for security validation functions."""

import tempfile
from pathlib import Path

import pytest

from src.autodoc_mcp.security import (
    InputValidator,
    sanitize_cache_key,
    validate_pypi_url,
)


class TestValidatePyPIURL:
    """Test PyPI URL validation."""

    def test_valid_https_urls(self):
        """Test valid HTTPS URLs."""
        valid_urls = [
            "https://pypi.org/pypi",
            "https://test.pypi.org/pypi",
            "https://pypi.python.org/pypi",
        ]

        for url in valid_urls:
            result = validate_pypi_url(url)
            assert result == url

    def test_valid_localhost_urls(self):
        """Test localhost URLs are allowed."""
        localhost_urls = [
            "http://localhost:8000/pypi",
            "https://localhost/pypi",
            "http://localhost/test",
        ]

        for url in localhost_urls:
            result = validate_pypi_url(url)
            assert result == url

    def test_invalid_empty_url(self):
        """Test empty URLs are rejected."""
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            validate_pypi_url("")

        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            validate_pypi_url("   ")

    def test_invalid_none_url(self):
        """Test None URLs are rejected."""
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            validate_pypi_url(None)

    def test_invalid_scheme(self):
        """Test invalid URL schemes."""
        invalid_schemes = [
            "ftp://pypi.org/pypi",
            "file:///etc/passwd",
            "javascript:alert('xss')",
        ]

        for url in invalid_schemes:
            with pytest.raises(ValueError, match="Invalid URL scheme"):
                validate_pypi_url(url)

    def test_untrusted_domain(self):
        """Test untrusted domains are rejected."""
        untrusted_urls = [
            "https://evil.com/pypi",
            "https://malicious.org/pypi",
            "http://attacker.net/pypi",
        ]

        for url in untrusted_urls:
            with pytest.raises(ValueError, match="Untrusted PyPI domain"):
                validate_pypi_url(url)

    def test_http_production_domains_rejected(self):
        """Test HTTP URLs for production domains are rejected."""
        http_urls = ["http://pypi.org/pypi", "http://test.pypi.org/pypi"]

        for url in http_urls:
            with pytest.raises(
                ValueError, match="HTTP URLs not allowed for production"
            ):
                validate_pypi_url(url)

    def test_malformed_urls(self):
        """Test malformed URLs are rejected."""
        malformed_urls = [
            "not-a-url",
            "://missing-scheme",
            "https://",
            "https://pypi.org with spaces",
        ]

        for url in malformed_urls:
            with pytest.raises(ValueError):
                validate_pypi_url(url)

    def test_whitespace_trimming(self):
        """Test URLs with whitespace are trimmed."""
        url_with_whitespace = "  https://pypi.org/pypi  "
        result = validate_pypi_url(url_with_whitespace)
        assert result == "https://pypi.org/pypi"


class TestSanitizeCacheKey:
    """Test cache key sanitization."""

    def test_valid_cache_key(self):
        """Test valid cache keys pass through."""
        valid_keys = ["requests-2.28.2", "package_name-1.0.0", "my-package-v1.2.3"]

        for key in valid_keys:
            result = sanitize_cache_key(key)
            assert result == key

    def test_dangerous_characters_replaced(self):
        """Test dangerous characters are replaced."""
        dangerous_key = 'package<>:"/\\|?*\x01name'
        result = sanitize_cache_key(dangerous_key)
        assert (
            result == "package__________name"
        )  # 10 underscores for 10 dangerous chars

    def test_path_traversal_prevention(self):
        """Test path traversal attempts are prevented."""
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "package..name",
            "...///package",
        ]

        for key in traversal_attempts:
            result = sanitize_cache_key(key)
            assert ".." not in result

    def test_leading_trailing_dots_stripped(self):
        """Test leading/trailing dots are stripped."""
        dotted_keys = [".package", "package.", "..package..", "   .package.   "]

        expected = ["package", "package", "package", "package"]

        for key, expected_result in zip(dotted_keys, expected, strict=False):
            result = sanitize_cache_key(key)
            assert result == expected_result

    def test_long_keys_truncated(self):
        """Test long keys are truncated."""
        long_key = "a" * 300
        result = sanitize_cache_key(long_key)
        assert len(result) == 200

    def test_reserved_names_rejected(self):
        """Test Windows reserved names are rejected."""
        reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]

        for name in reserved_names:
            with pytest.raises(ValueError, match="reserved name"):
                sanitize_cache_key(name)

    def test_empty_keys_rejected(self):
        """Test empty keys are rejected."""
        empty_keys = ["", "   ", ".", "..", "..."]

        for key in empty_keys:
            with pytest.raises(ValueError, match="Invalid cache key"):
                sanitize_cache_key(key)

    def test_non_string_input_rejected(self):
        """Test non-string inputs are rejected."""
        with pytest.raises(ValueError, match="Cache key must be a string"):
            sanitize_cache_key(123)

        with pytest.raises(ValueError, match="Cache key must be a string"):
            sanitize_cache_key(None)


class TestInputValidator:
    """Test input validation."""

    def test_validate_package_name_valid(self):
        """Test valid package names."""
        valid_names = [
            "requests",
            "Django",
            "package-name",
            "package_name",
            "package.name",
            "a",
            "a1",
            "1a",
        ]

        for name in valid_names:
            result = InputValidator.validate_package_name(name)
            assert result == name.lower()

    def test_validate_package_name_invalid(self):
        """Test invalid package names."""
        invalid_names = [
            "",
            "-invalid",
            "invalid-",
            "_invalid",
            "invalid_",
            ".invalid",
            "invalid.",
            "invalid@name",
            "invalid name",
            "a" * 250,  # Too long
        ]

        for name in invalid_names:
            with pytest.raises(ValueError):
                InputValidator.validate_package_name(name)

    def test_validate_package_name_non_string(self):
        """Test non-string package names are rejected."""
        with pytest.raises(ValueError, match="Package name must be a non-empty string"):
            InputValidator.validate_package_name(None)

        with pytest.raises(ValueError, match="Package name must be a non-empty string"):
            InputValidator.validate_package_name(123)

    def test_validate_version_constraint_valid(self):
        """Test valid version constraints."""
        valid_constraints = [">=1.0.0", "~=2.1.0", ">=1.0,<2.0", "==1.2.3", "!=1.0.0"]

        for constraint in valid_constraints:
            result = InputValidator.validate_version_constraint(constraint)
            assert result == constraint

    def test_validate_version_constraint_invalid(self):
        """Test invalid version constraints."""
        invalid_constraints = [
            "",
            "   ",
            "invalid",
            ">==1.0.0",  # Invalid operator
            ">=1.0.0 invalid",
        ]

        for constraint in invalid_constraints:
            with pytest.raises(ValueError):
                InputValidator.validate_version_constraint(constraint)

    def test_validate_version_constraint_non_string(self):
        """Test non-string version constraints are rejected."""
        with pytest.raises(ValueError, match="Version constraint must be a string"):
            InputValidator.validate_version_constraint(None)

    def test_validate_project_path_valid(self):
        """Test valid project paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test file in the directory
            test_file = temp_path / "test.txt"
            test_file.write_text("test")

            result = InputValidator.validate_project_path(str(temp_path))
            assert result == temp_path.resolve()

    def test_validate_project_path_nonexistent(self):
        """Test nonexistent paths are rejected."""
        with pytest.raises(ValueError, match="Path does not exist"):
            InputValidator.validate_project_path("/nonexistent/path")

    def test_validate_project_path_not_directory(self):
        """Test file paths (not directories) are rejected."""
        with (
            tempfile.NamedTemporaryFile() as temp_file,
            pytest.raises(ValueError, match="Path is not a directory"),
        ):
            InputValidator.validate_project_path(temp_file.name)

    def test_validate_project_path_empty(self):
        """Test empty paths are rejected."""
        with pytest.raises(ValueError, match="Project path must be a non-empty string"):
            InputValidator.validate_project_path("")

        with pytest.raises(ValueError, match="Project path must be a non-empty string"):
            InputValidator.validate_project_path(None)
