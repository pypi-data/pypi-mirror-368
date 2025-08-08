# AutoDocs MCP Server

AutoDocs MCP Server automatically provides AI assistants with contextual, version-specific documentation for Python project dependencies, eliminating manual package lookup and providing more accurate coding assistance.

## Features

- **Automatic Dependency Scanning**: Parse pyproject.toml files and extract dependency information
- **Version-Specific Caching**: Cache documentation based on resolved package versions
- **Graceful Degradation**: Handle malformed dependencies and network issues gracefully
- **Rich Context**: Provide AI assistants with both primary package and dependency documentation
- **FastMCP Integration**: Built with FastMCP for seamless integration with AI tools like Cursor

## Installation

```bash
# Using uv (recommended)
uv tool install autodocs-mcp

# Using pip
pip install autodocs-mcp
```

## Usage

### As an MCP Server

Configure in your Cursor Desktop settings:

```json
{
  "mcpServers": {
    "autodocs-mcp": {
      "command": "uv",
      "args": ["run", "--from", "autodocs-mcp", "autodocs-mcp"],
      "env": {
        "AUTODOCS_CACHE_DIR": "/path/to/cache"
      }
    }
  }
}
```

### Development

```bash
# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linting
uv run ruff check

# Start development server
uv run hatch run dev
```

## MCP Tools

### `scan_dependencies`

Scans project dependencies from pyproject.toml files.

**Parameters:**
- `project_path` (optional): Path to project directory (defaults to current directory)

**Returns:**
- Project metadata and dependency specifications
- Graceful degradation information for malformed dependencies

### `get_package_docs` (Coming Soon)

Retrieves formatted documentation for Python packages.

## Configuration

Environment variables:

- `AUTODOCS_CACHE_DIR`: Cache directory location (default: ~/.autodocs/cache)
- `AUTODOCS_MAX_CONCURRENT`: Maximum concurrent PyPI requests (default: 10)
- `AUTODOCS_REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)
- `AUTODOCS_LOG_LEVEL`: Logging level (default: INFO)

## Architecture

- **FastMCP Server**: Handles MCP protocol communication
- **Dependency Parser**: Parses pyproject.toml with graceful error handling
- **Documentation Fetcher**: Retrieves package info from PyPI (coming soon)
- **Cache Manager**: Version-based caching system (coming soon)

## Development Status

This is currently in **Priority 1: Core Validation** phase:

- ✅ Basic project setup with hatch/uv
- ✅ Minimal viable dependency parser
- ✅ Basic FastMCP integration
- ✅ `scan_dependencies` MCP tool
- 🚧 Testing with real projects

Coming next: Documentation fetching, version-based caching, and rich dependency context.

## License

MIT