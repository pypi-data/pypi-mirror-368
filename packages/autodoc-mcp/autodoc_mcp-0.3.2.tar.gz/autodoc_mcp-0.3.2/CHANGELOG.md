# Changelog

All notable changes to the AutoDocs MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.2] - 2025-08-09

### Changed
- **Package Name Standardization**
  - Standardized all package naming to `autodoc-mcp` (removing 's' from autodocs)
  - Renamed module directory: `src/autodocs_mcp/` → `src/autodoc_mcp/`
  - Updated script name: `autodocs-mcp` → `autodoc-mcp` in pyproject.toml
  - Updated cache directory paths: `~/.cache/autodocs-mcp/` → `~/.cache/autodoc-mcp/`
  - Fixed all import statements across codebase and tests (277 tests still pass)
  - Updated all configuration files (.mcp.json, pyproject.toml)
  - Updated all documentation (README.md, CLAUDE.md, CHANGELOG.md)
  - Updated development scripts and test references

### Technical
- Complete refactoring to ensure consistent naming throughout the entire codebase
- All pre-commit hooks pass and full test suite validated
- No functional changes - purely naming standardization

## [0.3.1] - 2025-08-09

### Fixed
- **README Documentation Accuracy**
  - Corrected development command paths (removed incorrect `src.` prefix)
  - Fixed MCP configuration examples with proper `autodoc-mcp` entry point
  - Updated manual server startup commands for accurate troubleshooting
  - Replaced outdated integration test examples with actual script commands

### Changed
- **Documentation Organization**
  - Documented all 8 MCP tools including `health_check`, `ready_check`, and `get_metrics`
  - Organized MCP tools into logical categories: Core Documentation, Cache Management, System Health & Monitoring
  - Updated testing examples to reference actual `scripts/dev.py` commands
  - Improved troubleshooting section with correct command examples

## [0.3.0] - 2025-08-09

### Added
- **Phase 3: Enhanced Network Resilience and Error Handling**
  - **Network Resilient Client**: Exponential backoff with jitter for HTTP requests
  - **Circuit Breaker Pattern**: Prevents cascade failures with configurable thresholds
  - **Rate Limiting**: Sliding window rate limiter to respect API limits with memory bounds
  - **Enhanced Error Messaging**: Structured error formatting with severity levels and suggestions
  - **Doc Fetching Resilience**: Safe batch document fetching with individual error handling
  - **MCP Response Standardization**: Consistent error responses across all MCP tools
  - **Performance Optimizations**:
    - Intelligent documentation truncation for performance
    - Configurable size limits and query filtering
    - Performance metrics tracking with correlation IDs
  - **Cache Improvements**: Safe cache entry retrieval with corruption handling

- **Production-Ready Infrastructure**
  - **Health Check System**: Comprehensive health monitoring with `health_check` and `ready_check` MCP tools
  - **Observability Framework**: Complete metrics collection, performance tracking, and monitoring integration
  - **Security Hardening**:
    - Input validation for package names, version constraints, and project paths
    - PyPI URL validation with trusted domain allowlist
    - Path traversal prevention with cache key sanitization
    - HTTPS enforcement for production environments
  - **Resource Management**:
    - Connection pooling with proper cleanup and limits
    - Graceful shutdown with signal handlers and active request tracking
    - Memory-bounded rate limiting with automatic cleanup
  - **Configuration Management**: Pydantic-based validation with production readiness checks

- **Comprehensive Testing and Quality Assurance**
  - **Enhanced Test Coverage**: Systematic improvement of unit and integration tests
  - **Test Infrastructure Modernization**: Complete migration to pytest-mock ecosystem
  - **Security Testing**: Full validation of input sanitization and attack prevention
  - **Production Validation**: Five-gate validation system for release readiness
  - **Performance Testing**: Response time validation and resource usage monitoring

- **Documentation and Developer Experience**
  - **Architecture Documentation**: Complete rewrite of CLAUDE.md with current system architecture
  - **Technical Debt Management**: Systematic tracking and prioritization of improvements
  - **Release Validation Framework**: Comprehensive validation gates for production deployment
  - **Development Workflow**: Enhanced GitFlow processes with release branch validation

### Changed
- **Network Operations**: All HTTP requests now use resilient client with retry logic
- **Error Handling**: Standardized error responses with structured formatting and recovery suggestions
- **Documentation Formatting**: Added size limits and performance-aware truncation
- **Version Resolution**: Enhanced with network resilience and retry patterns
- **Cache Management**: Added safe retrieval methods with corruption handling and validation
- **Testing Standards**: Mandatory pytest-mock usage with comprehensive fixture patterns
- **Configuration Loading**: All 14 configuration parameters now properly validated and loaded

### Enhanced
- **Main MCP Server**: All 8 tools now return standardized error responses with graceful shutdown
- **PyPI Integration**: Improved reliability with circuit breaker, rate limiting, and connection pooling
- **Logging**: Enhanced structured logging with performance metrics and correlation IDs
- **Security Posture**: Production-ready security controls with comprehensive input validation
- **Operational Readiness**: Full health check, metrics, and monitoring integration for production deployment

### Fixed
- **Configuration Loading Issues**: All environment variables and parameters now loading correctly
- **HTTP Resource Leaks**: Connection pooling with proper lifecycle management implemented
- **Rate Limiter Memory Growth**: Memory bounds and cleanup mechanisms implemented
- **Test Infrastructure**: Complete resolution of import and mocking issues across test suite
- **Type Annotations**: Enhanced type safety across core modules for better reliability

### Security
- **CVE-Level Vulnerability Fixes**:
  - URL validation prevents malicious PyPI endpoint attacks
  - Path traversal prevention in cache operations
  - Comprehensive input sanitization for all user inputs
  - Production security controls with HTTPS enforcement

## [0.2.0] - 2025-08-07

### Added
- **Phase 4: Dependency Context System** - Major new feature providing rich AI context
  - **Dependency Intelligence Engine**: Smart dependency resolution with relevance scoring
  - **Context Documentation Formatter**: AI-optimized documentation extraction and token management
  - **Concurrent Context Fetcher**: High-performance parallel documentation fetching
  - **New MCP Tool**: `get_package_docs_with_context` for comprehensive documentation context
  - **Enhanced Cache Manager**: Added `resolve_and_cache` method for seamless integration
  - Configurable context scope (primary_only, runtime, smart)
  - Token budget management and performance tracking
  - Support for major frameworks (FastAPI, Django, Flask, etc.)
  - Graceful degradation on dependency fetch failures

### Changed
- **Legacy Tool Enhancement**: Updated `get_package_docs` with note about new context tool
- **Service Initialization**: Enhanced to include Phase 4 context fetcher
- **Documentation**: All new modules include comprehensive docstrings and type hints

## [0.1.4] - 2025-08-07

### Fixed
- **CI/CD Pipeline Issues**: Resolved ruff linting failures in GitHub Actions
  - Fixed import sorting issues in `src/autodocs_mcp/main.py`
  - Cleaned up unused imports and whitespace in test files
  - Added explicit `--no-fix` flag to GitHub Actions ruff check for consistency
  - All code quality checks now pass in both local pre-commit hooks and CI

### Changed
- **GitHub Actions Configuration**: Updated CI workflow to be more explicit about ruff behavior
  - CI now runs `ruff check --no-fix` to ensure it only validates without attempting fixes
  - Maintains separation between local development (with auto-fixing) and CI validation

## [0.1.3] - 2025-08-07

### Added
- **Pre-commit hooks configuration** with comprehensive code quality checks
  - Ruff linting and formatting for Python code quality
  - MyPy static type checking with proper dependencies
  - Basic file hygiene checks (trailing whitespace, end-of-file-fixer, YAML validation)
  - Excluded `.specstory/` directory from whitespace checks to avoid auto-generated file conflicts

- **Development workflow standards** in CLAUDE.md
  - GitHub Flow branching strategy with feature branches and squash merging
  - Conventional Commits specification requirement for all commit messages
  - Semantic Versioning (SemVer) 2.0.0 compliance with automatic version bumping rules
  - Comprehensive changelog management requirements using Keep a Changelog format

### Fixed
- **Code quality improvements** across the entire codebase:
  - Exception chaining: Added `from e` to all `raise` statements for proper error context
  - Context manager usage: Replaced `try/except/pass` patterns with `contextlib.suppress(OSError)`
  - Type annotations: Added missing `typing.Any` imports and fixed type hints
  - Async context managers: Fixed return type annotations for `__aenter__` methods
  - Unused variables: Removed unused imports and variables to satisfy linting
  - File formatting: Fixed trailing whitespace and missing end-of-file newlines

### Changed
- **Pre-commit integration**: All commits now automatically run code quality checks locally
- **CI/CD reliability**: Local pre-commit hooks prevent CI failures by catching issues before push
- **Type safety**: Stricter type checking with MyPy ensures better code reliability

## [0.1.2] - 2025-08-07

### Added
- GitHub Actions CI/CD pipeline with automated PyPI deployment
- Trusted publishing configuration using OpenID Connect (OIDC)
- Tag-based release workflow with automatic PyPI package publishing
- Integration tests for MCP server functionality
- Additional test coverage for error handling scenarios

### Fixed
- CI pipeline configuration and dependency management
- Test reliability improvements with proper async handling
- PyPI deployment authentication using trusted publishing tokens

## [0.1.1] - 2025-08-07

### Added
- Initial CI/CD pipeline setup
- Basic GitHub Actions workflow for testing and validation

### Fixed
- Project packaging and build configuration issues
- Missing README.md file for package distribution

## [0.1.0] - 2025-08-07

### Added
- **Core MCP Server Implementation**
  - FastMCP-based server with stdio transport for MCP protocol compliance
  - Four complete MCP tools: `scan_dependencies`, `get_package_docs`, `refresh_cache`, `get_cache_stats`
  - Structured logging with stderr output for proper MCP integration

- **Dependency Management System**
  - Complete pyproject.toml parsing with graceful degradation for malformed dependencies
  - Support for standard dependencies, optional dependencies, and complex version constraints
  - Robust error handling that continues processing even with parsing failures

- **Documentation Fetching & Caching**
  - PyPI JSON API integration for retrieving package documentation and metadata
  - Version resolution system that converts constraints to specific versions
  - Version-based caching system with `{package_name}-{version}` format
  - No time-based cache expiration (versions are immutable)
  - AI-optimized documentation formatting for better context

- **Project Architecture**
  - Modular SOLID design with clear separation of concerns:
    - `dependency_parser.py`: pyproject.toml parsing with error handling
    - `doc_fetcher.py`: PyPI API integration with concurrent requests
    - `cache_manager.py`: JSON-based version caching
    - `version_resolver.py`: Version constraint resolution
    - `main.py`: FastMCP server implementation
  - Comprehensive type hints with Pydantic models
  - Configuration management with environment variables

- **Development Infrastructure**
  - Complete test suite with pytest, asyncio, and mocking
  - Code quality tools: ruff (linting/formatting), mypy (type checking)
  - Pre-commit hooks configuration
  - Development scripts for testing individual components
  - uv-based dependency management and virtual environments

- **Documentation & Configuration**
  - Comprehensive README with installation and usage instructions
  - MCP integration examples for Claude Code and other AI clients
  - Project instructions in CLAUDE.md for AI assistant context
  - Environment variable configuration support
  - `.mcp.json` template for Claude Code integration

### Technical Features
- **Graceful Degradation**: Continues operation despite malformed dependencies or network failures
- **Concurrent Processing**: Optimized PyPI requests with httpx async client
- **Version Immutability**: Cache design assumes package versions never change
- **Transport Compliance**: Full stdio protocol implementation for MCP servers
- **Error Resilience**: Comprehensive exception handling at all levels

### Dependencies
- fastmcp >= 2.0.0 (MCP server framework)
- httpx >= 0.25.0 (async HTTP client)
- pydantic >= 2.0.0 (data validation)
- structlog >= 23.2.0 (structured logging)
- packaging >= 23.0 (version parsing)
- tomlkit >= 0.12.0 (TOML parsing)

### Development Dependencies
- pytest >= 7.4.0 with asyncio, mock, and coverage plugins
- ruff >= 0.1.0 (linting and formatting)
- mypy >= 1.6.0 (type checking)
- pre-commit >= 3.5.0 (git hooks)

### Notes
- This release represents a complete, production-ready MCP server
- Successfully tested with major packages: requests, pydantic, fastapi
- Ready for integration with AI coding assistants
- Cache directory defaults to `~/.cache/autodoc-mcp/`
- Supports Python 3.11+ as specified in pyproject.toml
