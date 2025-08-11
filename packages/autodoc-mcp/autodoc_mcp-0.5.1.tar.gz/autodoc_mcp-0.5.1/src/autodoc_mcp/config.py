"""Configuration management for AutoDocs MCP Server."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

from .security import validate_pypi_url


class AutoDocsConfig(BaseModel):
    """Application configuration with comprehensive validation."""

    cache_dir: Path = Field(default_factory=lambda: Path.home() / ".autodocs" / "cache")
    max_concurrent: int = Field(default=10, ge=1, le=100)
    request_timeout: int = Field(default=30, ge=5, le=300)
    log_level: str = Field(default="INFO")
    pypi_base_url: str = Field(default="https://pypi.org/pypi")

    # Version-based caching settings
    max_cached_versions_per_package: int = Field(default=3, ge=1, le=10)
    cache_cleanup_days: int = Field(default=90, ge=1)

    # Context settings
    max_dependency_context: int = Field(default=8, ge=1, le=20)
    max_context_tokens: int = Field(default=30000, ge=1000, le=100000)

    # Performance and rate limiting settings
    max_retry_attempts: int = Field(default=3, ge=1, le=10)
    base_retry_delay: float = Field(default=1.0, ge=0.1, le=10.0)
    max_retry_delay: float = Field(default=30.0, ge=1.0, le=300.0)
    circuit_breaker_threshold: int = Field(default=5, ge=1, le=50)
    circuit_breaker_timeout: float = Field(default=60.0, ge=10.0, le=3600.0)
    rate_limit_requests_per_minute: int = Field(default=60, ge=1, le=1000)
    max_documentation_size: int = Field(default=50000, ge=1000, le=1000000)

    # Deployment settings
    environment: str = Field(default="development")
    debug_mode: bool = Field(default=False)

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()

    @field_validator("pypi_base_url")
    @classmethod
    def validate_pypi_url_enhanced(cls, v: str) -> str:
        """Enhanced PyPI URL validation."""
        try:
            # First use the security module validation
            validated_url = validate_pypi_url(v)

            # Additional security checks
            parsed = urlparse(validated_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("URL must have scheme and netloc")

            # Security check for trusted domains
            trusted_domains = {"pypi.org", "test.pypi.org", "localhost"}
            if parsed.netloc not in trusted_domains and not v.startswith(
                "http://localhost"
            ):
                raise ValueError(f"Untrusted PyPI domain: {parsed.netloc}")

            return validated_url
        except Exception as e:
            raise ValueError(f"Invalid PyPI URL '{v}': {e}") from e

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate deployment environment."""
        valid_envs = {"development", "staging", "production"}
        if v not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_envs}")
        return v

    @model_validator(mode="after")
    def validate_retry_delays(self) -> "AutoDocsConfig":
        """Ensure max_retry_delay > base_retry_delay."""
        if self.max_retry_delay <= self.base_retry_delay:
            raise ValueError("max_retry_delay must be greater than base_retry_delay")
        return self

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization validation and setup."""
        # Ensure cache directory exists and is writable
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            # Test write permissions
            test_file = self.cache_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            raise ValueError(
                f"Cache directory not writable: {self.cache_dir}. Error: {e}"
            ) from e

    @classmethod
    def from_env(cls) -> "AutoDocsConfig":
        """Load configuration from environment with enhanced validation."""
        try:
            config_data = {}

            # Map environment variables to config fields
            env_mappings = {
                "AUTODOCS_CACHE_DIR": "cache_dir",
                "AUTODOCS_MAX_CONCURRENT": ("max_concurrent", int),
                "AUTODOCS_REQUEST_TIMEOUT": ("request_timeout", int),
                "AUTODOCS_LOG_LEVEL": "log_level",
                "AUTODOCS_PYPI_URL": "pypi_base_url",
                "AUTODOCS_MAX_VERSIONS": ("max_cached_versions_per_package", int),
                "AUTODOCS_CLEANUP_DAYS": ("cache_cleanup_days", int),
                "AUTODOCS_MAX_DEPS": ("max_dependency_context", int),
                "AUTODOCS_MAX_TOKENS": ("max_context_tokens", int),
                "AUTODOCS_MAX_RETRY_ATTEMPTS": ("max_retry_attempts", int),
                "AUTODOCS_BASE_RETRY_DELAY": ("base_retry_delay", float),
                "AUTODOCS_MAX_RETRY_DELAY": ("max_retry_delay", float),
                "AUTODOCS_CIRCUIT_BREAKER_THRESHOLD": (
                    "circuit_breaker_threshold",
                    int,
                ),
                "AUTODOCS_CIRCUIT_BREAKER_TIMEOUT": ("circuit_breaker_timeout", float),
                "AUTODOCS_RATE_LIMIT_RPM": ("rate_limit_requests_per_minute", int),
                "AUTODOCS_MAX_DOC_SIZE": ("max_documentation_size", int),
                "AUTODOCS_ENVIRONMENT": "environment",
                "AUTODOCS_DEBUG": ("debug_mode", lambda x: x.lower() == "true"),
            }

            for env_var, config_key in env_mappings.items():
                value = os.getenv(env_var)
                if value is not None:
                    if isinstance(config_key, tuple):
                        key, converter = config_key
                        config_data[key] = converter(value)
                    else:
                        config_data[config_key] = value

            # Handle Path conversion for cache_dir
            if "cache_dir" in config_data:
                config_data["cache_dir"] = Path(config_data["cache_dir"])

            return cls(**config_data)

        except Exception as e:
            raise ValueError(f"Configuration validation failed: {e}") from e

    def validate_production_readiness(self) -> list[str]:
        """Validate configuration for production deployment."""
        issues = []

        if self.environment == "production":
            if self.debug_mode:
                issues.append("Debug mode should not be enabled in production")

            if not self.pypi_base_url.startswith("https://"):
                issues.append("HTTPS required for production PyPI URL")

            if self.log_level == "DEBUG":
                issues.append("Debug logging not recommended for production")

            if self.max_concurrent > 50:
                issues.append("High concurrency may overwhelm PyPI API")

        return issues


@lru_cache
def get_config() -> AutoDocsConfig:
    """Get cached configuration instance."""
    return AutoDocsConfig.from_env()
