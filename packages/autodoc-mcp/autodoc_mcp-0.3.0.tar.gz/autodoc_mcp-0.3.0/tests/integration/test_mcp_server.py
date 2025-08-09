"""Integration tests for the AutoDocs MCP server."""

import subprocess
import sys
import tempfile
from pathlib import Path


class TestMCPServerIntegration:
    """Integration tests for the MCP server functionality."""

    def test_server_help_command(self):
        """Test that the MCP server help doesn't crash."""
        # Basic smoke test - just ensure the module loads
        result = subprocess.run(
            [sys.executable, "-c", "import autodocs_mcp.main; print('OK')"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "OK" in result.stdout

    def test_basic_imports_work(self):
        """Test that core modules can be imported."""
        from autodocs_mcp.core.cache_manager import FileCacheManager
        from autodocs_mcp.core.dependency_parser import PyProjectParser
        from autodocs_mcp.core.version_resolver import VersionResolver

        # Just test instantiation doesn't crash
        parser = PyProjectParser()
        assert parser is not None

        with tempfile.TemporaryDirectory() as temp_dir:
            cache_manager = FileCacheManager(cache_dir=Path(temp_dir))
            assert cache_manager is not None

        resolver = VersionResolver()
        assert resolver is not None

    def test_toml_file_validation(self):
        """Test TOML file validation works."""
        from autodocs_mcp.core.dependency_parser import PyProjectParser

        parser = PyProjectParser()
        current_dir = Path(__file__).parent.parent.parent
        pyproject_file = current_dir / "pyproject.toml"

        # Test that file validation works
        is_valid = parser.validate_file(pyproject_file)
        assert is_valid is True
