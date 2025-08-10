# AutoDocs MCP Server

**Intelligent documentation context provider for AI assistants**

AutoDocs MCP Server automatically provides AI assistants with contextual, version-specific documentation for Python project dependencies. It uses intelligent dependency resolution to include both the requested package and its most relevant dependencies, giving AI assistants comprehensive context for accurate code assistance.

<a href="https://glama.ai/mcp/servers/@bradleyfay/autodoc-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@bradleyfay/autodoc-mcp/badge" alt="AutoDocs Server MCP server" />
</a>

## ✨ Features

### 🧠 **Phase 4: Dependency Context System**
- **Smart dependency resolution** with relevance scoring for major frameworks
- **AI-optimized documentation** extraction with token management
- **Concurrent fetching** of dependency documentation (3-5 second response times)
- **Contextual intelligence** - includes 3-8 most relevant dependencies automatically

### 🛠️ **Core Functionality**
- **Automatic dependency scanning** from pyproject.toml files
- **Version-specific caching** for optimal performance
- **Graceful degradation** with partial results on failures
- **FastMCP integration** for seamless AI tool compatibility

### 🎯 **Intelligent Context**
- **Framework-aware**: Special handling for FastAPI, Django, Flask ecosystems
- **Token-aware**: Respects context window limits (30k tokens default)
- **Performance-optimized**: Concurrent requests with caching
- **Configurable scope**: Primary-only, runtime deps, or smart context

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

# Run tests
uv run pytest

# Start development server
uv run python -m autodoc_mcp.main
```

## 🔌 Usage

### MCP Client Configuration

#### Cursor Desktop
Add to your Cursor settings (`Cmd+,` → Extensions → Rules for AI → MCP Servers):

```json
{
  "mcpServers": {
    "autodoc-mcp": {
      "command": "autodoc-mcp",
      "env": {
        "AUTODOCS_CACHE_DIR": "~/.autodocs/cache"
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
        "AUTODOCS_CACHE_DIR": "~/.autodocs/cache"
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
        "AUTODOCS_CACHE_DIR": "~/.autodocs/cache"
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
   # Or if installed via uv tool:
   uv tool run autodoc-mcp autodoc-mcp
   ```

2. **Test in your AI client:**
   - Ask: "What packages are available in this project?" (uses `scan_dependencies`)
   - Ask: "Tell me about the FastAPI package with its dependencies" (uses `get_package_docs_with_context`)

## 🛠️ Available MCP Tools

The server provides **8 MCP tools** organized into three categories:

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

### `get_package_docs_with_context` ⭐ **Main Feature**
Retrieves comprehensive documentation context including the requested package and its most relevant dependencies.

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
    "context_scope": "with_runtime (2 deps)",
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

### `get_package_docs` (Legacy)
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
Provides comprehensive system health status for monitoring and load balancer checks.

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
Provides system performance metrics for monitoring.

**Returns:**
- Performance statistics and metrics
- Health metrics
- Request/response statistics
- Cache performance data

## ⚙️ Configuration

### Environment Variables

- **`AUTODOCS_CACHE_DIR`**: Cache directory (default: `~/.autodocs/cache`)
- **`AUTODOCS_MAX_DEPENDENCY_CONTEXT`**: Max dependencies in context (default: 8)
- **`AUTODOCS_MAX_CONTEXT_TOKENS`**: Token budget for context (default: 30000)
- **`AUTODOCS_LOG_LEVEL`**: Logging level (default: INFO)

### Advanced Configuration

```bash
# Increase context size for complex projects
export AUTODOCS_MAX_DEPENDENCY_CONTEXT=12
export AUTODOCS_MAX_CONTEXT_TOKENS=50000

# Use custom cache location
export AUTODOCS_CACHE_DIR="/tmp/autodoc-cache"

# Enable debug logging
export AUTODOCS_LOG_LEVEL=DEBUG
```

## 🏗️ Architecture

### Intelligent Dependency Resolution
- **Relevance scoring**: Core frameworks (FastAPI, Django) get priority
- **Package relationships**: Framework-specific dependency boosts
- **Token awareness**: Respects context window limits
- **Graceful degradation**: Partial results when some deps fail

### Performance Optimizations
- **Version-based caching**: Immutable package versions cached indefinitely
- **Concurrent fetching**: Up to 5 simultaneous PyPI requests
- **Smart timeouts**: 15-second max for dependency fetching
- **Circuit breakers**: Prevents cascade failures

### AI-Optimized Output
- **Structured data**: Clean JSON with consistent formatting
- **Token estimation**: Helps AI clients manage context windows
- **Relevance filtering**: Only includes most important information
- **Context metadata**: Clear indication of what was included/excluded

## 🧪 Testing

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
```

## 🤔 Troubleshooting

### Common Issues

**"Context fetcher not initialized" error:**
- Ensure the MCP server started successfully
- Check logs for initialization errors
- Verify network connectivity to PyPI

**"No dependencies found" for known packages:**
- Check if the package has dependencies in its PyPI metadata
- Try with `context_scope="smart"` parameter
- Some packages have optional-only dependencies

**Slow response times:**
- Dependencies are fetched on first request (cache miss)
- Subsequent requests use cache (much faster)
- Network latency to PyPI affects first-time fetching

**MCP client can't connect:**
- Verify the command path in your MCP configuration
- Check if `autodoc-mcp` package is installed correctly
- Test manual server startup: `autodoc-mcp`
- If using uv tool install: `uv tool run autodoc-mcp autodoc-mcp`

### Debug Mode

```bash
# Enable debug logging
export AUTODOCS_LOG_LEVEL=DEBUG

# Run server manually to see debug output
autodoc-mcp

# Check cache contents
ls ~/.autodocs/cache/

# For development testing
uv run python scripts/dev.py --help
```

## 🔮 Roadmap

- **Multi-language support**: Expand beyond Python packages
- **Enhanced relevance scoring**: Machine learning-based dependency ranking
- **Semantic search**: Query-based documentation filtering
- **Performance monitoring**: Built-in metrics and alerting

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow conventional commits (`feat:`, `fix:`, `docs:`, etc.)
4. Run tests and linting (`uv run pytest && uv run ruff check`)
5. Create a Pull Request

---

**Built with ❤️ using [FastMCP](https://github.com/jlowin/fastmcp)**
