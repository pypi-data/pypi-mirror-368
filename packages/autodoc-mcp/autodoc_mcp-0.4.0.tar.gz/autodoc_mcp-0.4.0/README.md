# AutoDocs MCP Server

> **💡 Passion Project Note**: This is a personal passion project focused on exploring "intention-only programming" - the practice of describing what you want the code to do rather than how to implement it. The development process is completely transparent, and you can explore how this project evolved by examining the `.claude/` (Claude Code agent configurations) and `.specstory/` (session history) folders in this repository.

**Intelligent documentation context provider for AI assistants**

AutoDocs MCP Server automatically provides AI assistants with contextual, version-specific documentation for Python project dependencies. It uses intelligent dependency resolution to include both the requested package and its most relevant dependencies, giving AI assistants comprehensive context for accurate code assistance.

<a href="https://glama.ai/mcp/servers/@bradleyfay/autodoc-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@bradleyfay/autodoc-mcp/badge" alt="AutoDocs Server MCP server" />
</a>

## ✨ Features

### 🧠 **Phase 4: Dependency Context System** *(Complete)*
- **Smart dependency resolution** with relevance scoring for major frameworks
- **AI-optimized documentation** extraction with token management
- **Concurrent fetching** of dependency documentation (3-5 second response times)
- **Contextual intelligence** - includes 3-8 most relevant dependencies automatically

### 🛠️ **Production-Ready Core**
- **8 comprehensive MCP tools** including system health and monitoring
- **Network resilience** with circuit breakers and exponential backoff
- **Version-specific caching** with immutable cache keys for optimal performance
- **Graceful degradation** with partial results on failures
- **FastMCP integration** for seamless AI tool compatibility

### 🎯 **Intelligent Context**
- **Framework-aware**: Special handling for FastAPI, Django, Flask ecosystems
- **Token-aware**: Respects context window limits (30k tokens default)
- **Performance-optimized**: Concurrent requests with connection pooling
- **Configurable scope**: Primary-only, runtime deps, or smart context

### 🔍 **Development Transparency**
This project demonstrates transparent AI-assisted development:
- **`.claude/agents/`** - Claude Code agent configurations and specialized contexts
- **`.specstory/history/`** - Complete session history showing the development process
- **`planning/`** - Comprehensive planning documents and technical decisions

Explore these folders to see how this project evolved through intention-only programming!

## 🚀 Installation

### From PyPI (Recommended)
```bash
# Using uv (recommended)
uv tool install autodoc-mcp

# Using pip
pip install autodoc-mcp
```

### For Development
```bash
# Clone and install
git clone https://github.com/bradleyfay/autodoc-mcp.git
cd autodoc-mcp
uv sync --all-extras

# Run tests (277 tests)
uv run pytest

# Start development server
uv run python -m autodoc_mcp.main
```

## 🔌 Usage

### MCP Client Configuration

#### Claude Code Sessions
To use in Claude Code sessions:
```bash
# 1. Install the server in current session
uv tool install autodoc-mcp

# 2. Start the MCP server (the command is available globally)
autodoc-mcp

# 3. The server provides 8 MCP tools:
#    Core: scan_dependencies, get_package_docs, get_package_docs_with_context
#    Cache: refresh_cache, get_cache_stats
#    Health: health_check, ready_check, get_metrics
```

#### Cursor Desktop
Add to your Cursor settings (`Cmd+,` → Extensions → Rules for AI → MCP Servers):

```json
{
  "mcpServers": {
    "autodoc-mcp": {
      "command": "autodoc-mcp",
      "env": {
        "CACHE_DIR": "~/.cache/autodoc-mcp",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Claude Desktop
Add to your claude_desktop_config.json:

```json
{
  "mcpServers": {
    "autodoc-mcp": {
      "command": "autodoc-mcp",
      "env": {
        "CACHE_DIR": "~/.cache/autodoc-mcp",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Other MCP Clients
```json
{
  "mcpServers": {
    "autodoc-mcp": {
      "command": "python",
      "args": ["-m", "autodoc_mcp.main"],
      "cwd": "/path/to/autodoc-mcp",
      "env": {
        "CACHE_DIR": "~/.cache/autodoc-mcp",
        "LOG_LEVEL": "INFO",
        "MAX_CONCURRENT": "10"
      }
    }
  }
}
```

### Testing Your Setup

1. **Start the MCP server manually to test:**
   ```bash
   # Should show FastMCP startup screen
   autodoc-mcp
   ```

2. **Test in your AI client:**
   - Ask: "What packages are available in this project?" (uses `scan_dependencies`)
   - Ask: "Tell me about the FastAPI package with its dependencies" (uses `get_package_docs_with_context`)

## 🛠️ Available MCP Tools

The server provides **8 production-ready MCP tools** organized into three categories:

### Core Documentation Tools

#### `scan_dependencies`
Scans project dependencies from pyproject.toml files with graceful error handling.

**Parameters:**
- `project_path` (optional): Path to project directory (defaults to current directory)

**Returns:**
- Project metadata and dependency specifications
- Graceful degradation info for malformed dependencies
- Success/failure counts and error details

**Example:**
```python
# AI Assistant can call this to understand your project
{
  "success": true,
  "project_name": "my-fastapi-app",
  "total_dependencies": 12,
  "dependencies": [
    {"name": "fastapi", "version_constraint": ">=0.100.0"},
    {"name": "pydantic", "version_constraint": "^2.0.0"}
  ]
}
```

#### `get_package_docs_with_context` ⭐ **Primary Phase 4 Tool**
Retrieves comprehensive documentation context including the requested package and its most relevant dependencies with smart scoping.

**Parameters:**
- `package_name` (required): Primary package to document
- `version_constraint` (optional): Version constraint for primary package
- `include_dependencies` (optional): Include dependency context (default: true)
- `context_scope` (optional): "primary_only", "runtime", or "smart" (default: "smart")
- `max_dependencies` (optional): Maximum dependencies to include (default: 8)
- `max_tokens` (optional): Token budget for context (default: 30000)

**Returns:**
- Rich documentation context with primary package + key dependencies
- Performance metrics (response times, cache hits)
- Token estimates and context scope information

**Example:**
```python
# AI Assistant gets comprehensive context
{
  "success": true,
  "context": {
    "primary_package": {
      "name": "fastapi",
      "version": "0.104.1",
      "summary": "FastAPI framework, high performance...",
      "key_features": ["Automatic API docs", "Type hints", "Async support"],
      "main_classes": ["FastAPI", "APIRouter", "Depends"],
      "usage_examples": "from fastapi import FastAPI\napp = FastAPI()..."
    },
    "runtime_dependencies": [
      {
        "name": "pydantic",
        "version": "2.5.1",
        "why_included": "Required by fastapi",
        "summary": "Data validation using Python type hints",
        "key_features": ["Data validation", "Serialization"]
      },
      {
        "name": "starlette",
        "version": "0.27.0",
        "why_included": "Required by fastapi",
        "summary": "Lightweight ASGI framework/toolkit"
      }
    ],
    "context_scope": "smart (2 deps)",
    "total_packages": 3,
    "token_estimate": 15420
  },
  "performance": {
    "total_time": 0.89,
    "cache_hits": 1,
    "cache_misses": 2
  }
}
```

#### `get_package_docs` (Legacy)
Retrieves basic documentation for a single package without dependency context.

**Parameters:**
- `package_name` (required): Package to document
- `version_constraint` (optional): Version constraint
- `query` (optional): Filter documentation sections

**Note:** For rich context with dependencies, use `get_package_docs_with_context` instead.

### Cache Management Tools

#### `refresh_cache`
Clears the local documentation cache.

**Returns:**
- Statistics about cleared entries and freed space

#### `get_cache_stats`
Gets statistics about the documentation cache.

**Returns:**
- Cache statistics (total entries, size, hit rates)
- List of cached packages

### System Health & Monitoring Tools

#### `health_check`
Comprehensive health status for monitoring and load balancer checks.

**Returns:**
- Overall health status of all system components
- Component-level health information
- System diagnostics

#### `ready_check`
Kubernetes-style readiness check for deployment orchestration.

**Returns:**
- Simple ready/not-ready status
- Readiness for handling requests

#### `get_metrics`
System performance metrics for monitoring.

**Returns:**
- Performance statistics and metrics
- Health metrics
- Request/response statistics
- Cache performance data

## ⚙️ Configuration

### Environment Variables

- **`CACHE_DIR`**: Cache directory (default: `~/.cache/autodoc-mcp`)
- **`MAX_DEPENDENCY_CONTEXT`**: Max dependencies in context (default: 8)
- **`MAX_CONTEXT_TOKENS`**: Token budget for context (default: 30000)
- **`LOG_LEVEL`**: Logging level (default: INFO)
- **`MAX_CONCURRENT`**: Maximum concurrent PyPI requests (default: 10)

### Advanced Configuration

```bash
# Increase context size for complex projects
export MAX_DEPENDENCY_CONTEXT=12
export MAX_CONTEXT_TOKENS=50000

# Use custom cache location
export CACHE_DIR="/tmp/autodoc-cache"

# Enable debug logging
export LOG_LEVEL=DEBUG

# Adjust concurrency for network conditions
export MAX_CONCURRENT=5
```

## 🏗️ Architecture

### Layered Architecture (Phase 4 Complete)
- **Core Services Layer** (`src/autodoc_mcp/core/`): 10 specialized modules for dependency parsing, resolution, fetching, caching, and context management
- **Infrastructure Layer** (`src/autodoc_mcp/`): MCP server, configuration, security, observability, health checks
- **Network Resilience**: Circuit breakers, exponential backoff, connection pooling
- **Production Ready**: Graceful shutdown, comprehensive error handling, structured logging

### Intelligent Dependency Resolution
- **Relevance scoring**: Core frameworks (FastAPI, Django, Flask) get priority
- **Package relationships**: Framework-specific dependency boosts
- **Token awareness**: Respects context window limits with automatic truncation
- **Smart scoping**: Runtime vs development dependency classification
- **Graceful degradation**: Partial results when some dependencies fail

### Performance Optimizations
- **Version-based caching**: Immutable package versions cached indefinitely with `{package}-{version}.json` keys
- **Concurrent fetching**: Up to 10 simultaneous PyPI requests with connection pooling
- **Smart timeouts**: 15-second max for dependency fetching with exponential backoff
- **Circuit breakers**: Prevents cascade failures with automatic recovery

### AI-Optimized Output
- **Structured data**: Clean JSON with consistent formatting and metadata
- **Token estimation**: Helps AI clients manage context windows effectively
- **Relevance filtering**: Only includes most important information based on scoring
- **Context metadata**: Clear indication of what was included/excluded and why

## 🧪 Testing

### Comprehensive Test Suite (277 Tests)
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run linting
uv run ruff check

# Type checking
uv run mypy src

# Development testing with scripts
uv run python scripts/dev.py test-scan
uv run python scripts/dev.py test-docs fastapi ">=0.100.0"
uv run python scripts/dev.py cache-stats
uv run python scripts/dev.py clear-cache
```

### Development Standards
- **Conventional Commits**: All commits follow conventional commit standards
- **Pre-commit Hooks**: Automated linting, formatting, and type checking
- **pytest Ecosystem**: pytest-mock, pytest-asyncio, pytest-cov, pytest-xdist
- **Security Focused**: Input validation and security controls throughout

## 🤔 Troubleshooting

### Common Issues

**"Context fetcher not initialized" error:**
- Ensure the MCP server started successfully
- Check logs for initialization errors with `LOG_LEVEL=DEBUG`
- Verify network connectivity to PyPI

**"No dependencies found" for known packages:**
- Check if the package has dependencies in its PyPI metadata
- Try with `context_scope="smart"` parameter
- Some packages have optional-only dependencies

**Slow response times:**
- Dependencies are fetched on first request (cache miss)
- Subsequent requests use cache (much faster)
- Network latency to PyPI affects first-time fetching
- Adjust `MAX_CONCURRENT` for network conditions

**MCP client can't connect:**
- Verify the command path in your MCP configuration
- Check if `autodoc-mcp` package is installed correctly: `autodoc-mcp --version`
- Test manual server startup: `autodoc-mcp`
- Check server logs with `LOG_LEVEL=DEBUG`

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run server manually to see debug output
autodoc-mcp

# Check cache contents
ls ~/.cache/autodoc-mcp/

# View cache statistics
uv run python scripts/dev.py cache-stats

# Test specific functionality
uv run python scripts/dev.py --help
```

### Health Monitoring

```bash
# Check system health (using the MCP tools)
# Ask your AI assistant: "Check the health status of AutoDocs"
# This uses the health_check MCP tool

# View performance metrics
# Ask your AI assistant: "Show me AutoDocs performance metrics"
# This uses the get_metrics MCP tool
```

## 🔮 Future Enhancements

### Immediate Robustness (Technical Debt)
- Enhanced input validation for edge cases
- Memory pressure monitoring for long-running instances
- Cache corruption recovery mechanisms
- Dependency graph analysis with circular dependency detection

### Performance & Scalability
- Streaming context delivery for large dependency trees
- Predictive caching based on usage patterns
- Delta documentation (changes between versions)
- Distributed caching with Redis support

### AI Integration
- Semantic documentation filtering with embedding models
- ML-based relevance scoring for dependency prioritization
- Documentation quality assessment
- Custom context templates for different AI use cases

### Enterprise Features
- Authentication & authorization (API keys, JWT)
- Rate limiting and quota management
- Multi-tenant support with isolated caching
- OpenTelemetry integration for distributed tracing

## 📊 Project Statistics

- **Version**: 0.3.4 (Phase 4 Complete)
- **Architecture**: Layered with 10 core service modules
- **Test Coverage**: 277 comprehensive tests
- **MCP Tools**: 8 production-ready tools
- **Dependencies**: Minimal, production-focused
- **Language Support**: Python (with plans for multi-language)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow conventional commits (`feat:`, `fix:`, `docs:`, etc.)
4. Run tests and linting (`uv run pytest && uv run ruff check`)
5. Create a Pull Request

### Development Workflow
- **Work on `develop` branch** for most changes
- **Use `feature/*` branches** for larger features
- **Create `release/v0.x.x` branches** for version releases
- **All commits must pass pre-commit hooks** (never use `--no-verify`)

---

**Built with ❤️ using [FastMCP](https://github.com/jlowin/fastmcp) and intention-only programming**
