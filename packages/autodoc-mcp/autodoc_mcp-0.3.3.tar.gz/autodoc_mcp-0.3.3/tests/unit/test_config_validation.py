"""Tests for enhanced configuration validation."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from autodoc_mcp.config import AutoDocsConfig


class TestAutoDocsConfigValidation:
    """Test configuration validation."""

    def test_default_config_creation(self):
        """Test creating config with defaults."""
        config = AutoDocsConfig()

        assert config.max_concurrent == 10
        assert config.request_timeout == 30
        assert config.log_level == "INFO"
        assert config.pypi_base_url == "https://pypi.org/pypi"
        assert config.environment == "development"
        assert config.debug_mode is False

    def test_field_validation_constraints(self):
        """Test field validation constraints."""
        # Test max_concurrent constraints
        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(max_concurrent=0)  # Below minimum
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(max_concurrent=101)  # Above maximum
        assert "Input should be less than or equal to 100" in str(exc_info.value)

        # Test request_timeout constraints
        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(request_timeout=4)  # Below minimum
        assert "Input should be greater than or equal to 5" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(request_timeout=301)  # Above maximum
        assert "Input should be less than or equal to 300" in str(exc_info.value)

    def test_log_level_validation(self):
        """Test log level validation."""
        # Valid log levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = AutoDocsConfig(log_level=level)
            assert config.log_level == level

        # Case insensitive
        config = AutoDocsConfig(log_level="debug")
        assert config.log_level == "DEBUG"

        # Invalid log level
        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(log_level="INVALID")
        assert "Invalid log level: INVALID" in str(exc_info.value)

    def test_pypi_url_validation(self):
        """Test PyPI URL validation."""
        # Valid URLs
        valid_urls = [
            "https://pypi.org/pypi",
            "https://test.pypi.org/pypi",
            "http://localhost:8080/pypi",
        ]
        for url in valid_urls:
            config = AutoDocsConfig(pypi_base_url=url)
            assert config.pypi_base_url == url

        # Invalid URLs
        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(pypi_base_url="invalid-url")
        assert "Invalid PyPI URL" in str(exc_info.value)

        # Untrusted domain
        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(pypi_base_url="https://evil.com/pypi")
        assert "Untrusted PyPI domain" in str(exc_info.value)

    def test_environment_validation(self):
        """Test environment validation."""
        # Valid environments
        for env in ["development", "staging", "production"]:
            config = AutoDocsConfig(environment=env)
            assert config.environment == env

        # Invalid environment
        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(environment="invalid")
        assert "Invalid environment: invalid" in str(exc_info.value)

    def test_retry_delay_validation(self):
        """Test retry delay validation."""
        # Valid configuration
        config = AutoDocsConfig(base_retry_delay=1.0, max_retry_delay=30.0)
        assert config.base_retry_delay == 1.0
        assert config.max_retry_delay == 30.0

        # Invalid: max <= base
        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(base_retry_delay=5.0, max_retry_delay=5.0)
        assert "max_retry_delay must be greater than base_retry_delay" in str(
            exc_info.value
        )

        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(base_retry_delay=10.0, max_retry_delay=5.0)
        assert "max_retry_delay must be greater than base_retry_delay" in str(
            exc_info.value
        )

    def test_context_settings_validation(self):
        """Test context settings validation."""
        # Valid settings
        config = AutoDocsConfig(
            max_dependency_context=5,
            max_context_tokens=15000,
        )
        assert config.max_dependency_context == 5
        assert config.max_context_tokens == 15000

        # Invalid max_dependency_context
        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(max_dependency_context=0)
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(max_dependency_context=21)
        assert "Input should be less than or equal to 20" in str(exc_info.value)

        # Invalid max_context_tokens
        with pytest.raises(ValidationError) as exc_info:
            AutoDocsConfig(max_context_tokens=500)  # Below minimum
        assert "Input should be greater than or equal to 1000" in str(exc_info.value)

    def test_cache_dir_validation_and_creation(self):
        """Test cache directory validation and creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "test_cache"

            # Should create the directory
            config = AutoDocsConfig(cache_dir=cache_path)
            assert config.cache_dir == cache_path
            assert cache_path.exists()
            assert cache_path.is_dir()

    def test_cache_dir_write_permission_check(self):
        """Test cache directory write permission check."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "readonly_cache"
            cache_path.mkdir()

            # Make directory read-only (this might not work on all systems)
            try:
                cache_path.chmod(0o444)

                # This should fail due to write permission check
                with pytest.raises(ValidationError) as exc_info:
                    AutoDocsConfig(cache_dir=cache_path)
                assert "not writable" in str(exc_info.value)

            finally:
                # Restore permissions for cleanup
                cache_path.chmod(0o755)

    def test_from_env_basic(self):
        """Test loading configuration from environment."""
        env_vars = {
            "AUTODOCS_MAX_CONCURRENT": "20",
            "AUTODOCS_REQUEST_TIMEOUT": "45",
            "AUTODOCS_LOG_LEVEL": "DEBUG",
            "AUTODOCS_ENVIRONMENT": "staging",
            "AUTODOCS_DEBUG": "true",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = AutoDocsConfig.from_env()

            assert config.max_concurrent == 20
            assert config.request_timeout == 45
            assert config.log_level == "DEBUG"
            assert config.environment == "staging"
            assert config.debug_mode is True

    def test_from_env_with_cache_dir(self):
        """Test loading cache directory from environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_vars = {
                "AUTODOCS_CACHE_DIR": temp_dir,
            }

            with patch.dict(os.environ, env_vars, clear=False):
                config = AutoDocsConfig.from_env()
                assert config.cache_dir == Path(temp_dir)

    def test_from_env_invalid_values(self):
        """Test handling invalid environment variable values."""
        env_vars = {
            "AUTODOCS_MAX_CONCURRENT": "invalid",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with pytest.raises(ValueError) as exc_info:
                AutoDocsConfig.from_env()
            assert "Configuration validation failed" in str(exc_info.value)

    def test_from_env_boolean_conversion(self):
        """Test boolean conversion from environment."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("anything_else", False),
        ]

        for env_value, expected in test_cases:
            env_vars = {"AUTODOCS_DEBUG": env_value}

            with patch.dict(os.environ, env_vars, clear=False):
                config = AutoDocsConfig.from_env()
                assert config.debug_mode is expected

    def test_from_env_numeric_conversions(self):
        """Test numeric conversions from environment."""
        env_vars = {
            "AUTODOCS_MAX_RETRY_ATTEMPTS": "5",
            "AUTODOCS_BASE_RETRY_DELAY": "2.5",
            "AUTODOCS_CIRCUIT_BREAKER_TIMEOUT": "120.0",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = AutoDocsConfig.from_env()
            assert config.max_retry_attempts == 5
            assert config.base_retry_delay == 2.5
            assert config.circuit_breaker_timeout == 120.0

    def test_validate_production_readiness_development(self):
        """Test production readiness validation in development."""
        config = AutoDocsConfig(
            environment="development",
            debug_mode=True,
            log_level="DEBUG",
        )

        issues = config.validate_production_readiness()
        assert len(issues) == 0  # No issues in development

    def test_validate_production_readiness_production_good(self):
        """Test production readiness validation with good production config."""
        config = AutoDocsConfig(
            environment="production",
            debug_mode=False,
            log_level="INFO",
            pypi_base_url="https://pypi.org/pypi",
            max_concurrent=30,
        )

        issues = config.validate_production_readiness()
        assert len(issues) == 0

    def test_validate_production_readiness_production_issues(self):
        """Test production readiness validation with issues."""
        config = AutoDocsConfig(
            environment="production",
            debug_mode=True,  # Issue 1
            log_level="DEBUG",  # Issue 2
            pypi_base_url="http://localhost:8080/pypi",  # Issue 3 (not HTTPS)
            max_concurrent=75,  # Issue 4 (high concurrency)
        )

        issues = config.validate_production_readiness()
        assert len(issues) == 4

        issue_text = " ".join(issues)
        assert "debug mode" in issue_text.lower()
        assert "debug logging" in issue_text.lower()
        assert "https required" in issue_text.lower()
        assert "high concurrency" in issue_text.lower()

    def test_comprehensive_configuration_validation(self):
        """Test comprehensive configuration with all settings."""
        config_data = {
            "cache_dir": Path("/tmp/test_cache"),
            "max_concurrent": 15,
            "request_timeout": 60,
            "log_level": "WARNING",
            "pypi_base_url": "https://test.pypi.org/pypi",
            "max_cached_versions_per_package": 5,
            "cache_cleanup_days": 30,
            "max_dependency_context": 10,
            "max_context_tokens": 20000,
            "max_retry_attempts": 5,
            "base_retry_delay": 2.0,
            "max_retry_delay": 60.0,
            "circuit_breaker_threshold": 10,
            "circuit_breaker_timeout": 120.0,
            "rate_limit_requests_per_minute": 120,
            "max_documentation_size": 100000,
            "environment": "staging",
            "debug_mode": True,
        }

        # Should not raise any validation errors
        config = AutoDocsConfig(**config_data)

        # Verify all values are set correctly
        for key, value in config_data.items():
            assert getattr(config, key) == value
