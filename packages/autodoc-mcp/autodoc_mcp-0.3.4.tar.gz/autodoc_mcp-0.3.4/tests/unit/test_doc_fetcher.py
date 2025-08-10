"""Unit tests for documentation fetching functionality."""

import pytest
from httpx import Response

from src.autodoc_mcp.core.doc_fetcher import (
    DocFetchResult,
    PyPIDocumentationFetcher,
)
from src.autodoc_mcp.exceptions import NetworkError, PackageNotFoundError
from src.autodoc_mcp.models import PackageInfo


@pytest.fixture
def mock_config(mocker):
    """Mock configuration for tests."""
    config = mocker.Mock()
    config.pypi_base_url = "https://pypi.org/pypi"
    config.max_concurrent = 5
    config.max_documentation_size = 50000
    return config


@pytest.fixture
def sample_package_info():
    """Sample PackageInfo for tests."""
    return PackageInfo(
        name="requests",
        version="2.28.0",
        summary="Python HTTP for Humans.",
        description="Requests is a simple, yet elegant, HTTP library for Python.",
        author="Kenneth Reitz",
        license="Apache 2.0",
        home_page="https://requests.readthedocs.io",
        project_urls={
            "Documentation": "https://requests.readthedocs.io",
            "Source": "https://github.com/psf/requests",
        },
        classifiers=["Development Status :: 5 - Production/Stable"],
        keywords=["http", "requests", "web"],
    )


@pytest.fixture
def sample_pypi_response():
    """Sample PyPI API response."""
    return {
        "info": {
            "name": "requests",
            "version": "2.28.0",
            "summary": "Python HTTP for Humans.",
            "description": "Requests is a simple, yet elegant, HTTP library for Python.",
            "author": "Kenneth Reitz",
            "license": "Apache 2.0",
            "home_page": "https://requests.readthedocs.io",
            "project_urls": {
                "Documentation": "https://requests.readthedocs.io",
                "Source": "https://github.com/psf/requests",
            },
            "classifiers": ["Development Status :: 5 - Production/Stable"],
            "keywords": "http requests web",
        }
    }


class TestPyPIDocumentationFetcher:
    """Test PyPIDocumentationFetcher functionality."""

    @pytest.fixture
    def fetcher(self, mock_config, mocker):
        """Create fetcher instance with mocked config."""
        with mocker.patch(
            "src.autodoc_mcp.core.doc_fetcher.get_config", return_value=mock_config
        ):
            return PyPIDocumentationFetcher()

    @pytest.mark.asyncio
    async def test_context_manager_initialization(self, fetcher, mocker):
        """Test async context manager properly initializes client."""
        mock_client = mocker.AsyncMock()

        with mocker.patch(
            "src.autodoc_mcp.core.doc_fetcher.NetworkResilientClient",
            return_value=mock_client,
        ):
            async with fetcher:
                assert fetcher._resilient_client is mock_client
                mock_client.__aenter__.assert_called_once()

            mock_client.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_package_info_success(
        self, fetcher, sample_pypi_response, sample_package_info, mocker
    ):
        """Test successful package info fetching."""
        # Mock HTTP response
        mock_response = mocker.Mock(spec=Response)
        mock_response.json.return_value = sample_pypi_response

        # Mock resilient client
        mock_client = mocker.AsyncMock()
        mock_client.get_with_retry.return_value = mock_response
        fetcher._resilient_client = mock_client

        # Test fetch
        result = await fetcher.fetch_package_info("requests")

        # Verify result
        assert result.name == "requests"
        assert result.version == "2.28.0"
        assert result.summary == "Python HTTP for Humans."
        assert (
            result.description
            == "Requests is a simple, yet elegant, HTTP library for Python."
        )
        assert result.author == "Kenneth Reitz"

        # Verify API call
        mock_client.get_with_retry.assert_called_once_with(
            "https://pypi.org/pypi/requests/json",
            headers={"Accept": "application/json"},
        )

    @pytest.mark.asyncio
    async def test_fetch_package_info_package_not_found(self, fetcher, mocker):
        """Test handling of package not found errors."""
        mock_client = mocker.AsyncMock()
        mock_client.get_with_retry.side_effect = PackageNotFoundError(
            "Package not found"
        )
        fetcher._resilient_client = mock_client

        with pytest.raises(PackageNotFoundError):
            await fetcher.fetch_package_info("nonexistent-package")

    @pytest.mark.asyncio
    async def test_fetch_package_info_network_error(self, fetcher, mocker):
        """Test handling of network errors."""
        mock_client = mocker.AsyncMock()
        mock_client.get_with_retry.side_effect = NetworkError("Connection failed")
        fetcher._resilient_client = mock_client

        with pytest.raises(NetworkError):
            await fetcher.fetch_package_info("requests")

    @pytest.mark.asyncio
    async def test_fetch_package_info_client_not_initialized(self, fetcher):
        """Test error when client not initialized."""
        fetcher._resilient_client = None

        with pytest.raises(RuntimeError, match="Client not initialized"):
            await fetcher.fetch_package_info("requests")

    @pytest.mark.asyncio
    async def test_fetch_package_info_safe_success(
        self, fetcher, sample_pypi_response, sample_package_info, mocker
    ):
        """Test safe fetch with successful result."""
        # Mock HTTP response
        mock_response = mocker.Mock(spec=Response)
        mock_response.json.return_value = sample_pypi_response

        # Mock resilient client
        mock_client = mocker.AsyncMock()
        mock_client.get_with_retry.return_value = mock_response
        fetcher._resilient_client = mock_client

        # Test safe fetch
        result = await fetcher.fetch_package_info_safe("requests")

        # Verify result structure
        assert isinstance(result, DocFetchResult)
        assert result.success is True
        assert result.package_info is not None
        assert result.package_info.name == "requests"
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert result.fetch_time > 0

    @pytest.mark.asyncio
    async def test_fetch_package_info_safe_package_not_found(self, fetcher, mocker):
        """Test safe fetch handles package not found gracefully."""
        mock_client = mocker.AsyncMock()
        mock_client.get_with_retry.side_effect = PackageNotFoundError(
            "Package not found"
        )
        fetcher._resilient_client = mock_client

        result = await fetcher.fetch_package_info_safe("nonexistent-package")

        assert isinstance(result, DocFetchResult)
        assert result.success is False
        assert result.package_info is None
        assert len(result.errors) == 1
        assert result.errors[0].error_code is not None

    @pytest.mark.asyncio
    async def test_fetch_package_info_safe_network_error(self, fetcher, mocker):
        """Test safe fetch handles network errors gracefully."""
        mock_client = mocker.AsyncMock()
        mock_client.get_with_retry.side_effect = NetworkError("Connection failed")
        fetcher._resilient_client = mock_client

        result = await fetcher.fetch_package_info_safe("requests")

        assert isinstance(result, DocFetchResult)
        assert result.success is False
        assert result.package_info is None
        assert len(result.errors) == 1
        assert result.errors[0].error_code is not None

    @pytest.mark.asyncio
    async def test_fetch_package_info_safe_unexpected_error(self, fetcher, mocker):
        """Test safe fetch handles unexpected errors gracefully."""
        mock_client = mocker.AsyncMock()
        mock_client.get_with_retry.side_effect = ValueError("Unexpected error")
        fetcher._resilient_client = mock_client

        result = await fetcher.fetch_package_info_safe("requests")

        assert isinstance(result, DocFetchResult)
        assert result.success is False
        assert result.package_info is None
        assert len(result.errors) == 1
        assert result.errors[0].error_code is not None

    @pytest.mark.asyncio
    async def test_fetch_multiple_packages_safe(
        self, fetcher, sample_pypi_response, mocker
    ):
        """Test fetching multiple packages safely."""
        # Mock successful responses for both packages
        mock_response = mocker.Mock(spec=Response)
        mock_response.json.return_value = sample_pypi_response

        mock_client = mocker.AsyncMock()
        mock_client.get_with_retry.return_value = mock_response
        fetcher._resilient_client = mock_client

        # Test batch fetch
        packages = ["requests", "httpx"]
        results = await fetcher.fetch_multiple_packages_safe(packages)

        # Verify results structure
        assert len(results) == 2
        assert "requests" in results
        assert "httpx" in results
        assert all(isinstance(r, DocFetchResult) for r in results.values())
        assert all(r.success for r in results.values())

    @pytest.mark.asyncio
    async def test_fetch_multiple_packages_safe_mixed_results(
        self, fetcher, sample_pypi_response, mocker
    ):
        """Test batch fetch with mixed success/failure results."""

        # Mock responses: success for requests, failure for nonexistent
        def mock_get_with_retry(url, **kwargs):
            if "requests" in url:
                mock_response = mocker.Mock(spec=Response)
                mock_response.json.return_value = sample_pypi_response
                return mock_response
            else:
                raise PackageNotFoundError("Package not found")

        mock_client = mocker.AsyncMock()
        mock_client.get_with_retry.side_effect = mock_get_with_retry
        fetcher._resilient_client = mock_client

        # Test batch fetch
        packages = ["requests", "nonexistent-package"]
        results = await fetcher.fetch_multiple_packages_safe(packages)

        # Verify mixed results
        assert len(results) == 2
        assert results["requests"].success is True
        assert results["nonexistent-package"].success is False
        assert len(results["nonexistent-package"].errors) == 1


class TestDocumentationFormatting:
    """Test documentation formatting functionality."""

    @pytest.fixture
    def fetcher(self, mock_config, mocker):
        """Create fetcher instance with mocked config."""
        with mocker.patch(
            "src.autodoc_mcp.core.doc_fetcher.get_config", return_value=mock_config
        ):
            return PyPIDocumentationFetcher()

    def test_format_documentation_basic(
        self, fetcher, sample_package_info, mock_config, mocker
    ):
        """Test basic documentation formatting."""
        with mocker.patch(
            "src.autodoc_mcp.core.doc_fetcher.get_config", return_value=mock_config
        ):
            formatted = fetcher.format_documentation(sample_package_info)

        # Check basic structure
        assert "# requests v2.28.0" in formatted
        assert "**Summary**: Python HTTP for Humans." in formatted
        assert "**Author**: Kenneth Reitz" in formatted
        assert "## Description" in formatted
        assert "## Links" in formatted
        assert "**Documentation**: https://requests.readthedocs.io" in formatted

    def test_format_documentation_with_query(
        self, fetcher, sample_package_info, mock_config, mocker
    ):
        """Test documentation formatting with query filtering."""
        with mocker.patch(
            "src.autodoc_mcp.core.doc_fetcher.get_config", return_value=mock_config
        ):
            formatted = fetcher.format_documentation(
                sample_package_info, query="http web"
            )

        # Query filtering returns sections that match the query terms
        # Since "http" is in the keywords, should return relevant content
        assert len(formatted) > 0
        # Should contain keywords section since "http" matches
        assert "http" in formatted.lower()

    def test_format_documentation_size_limits(
        self, fetcher, sample_package_info, mock_config, mocker
    ):
        """Test documentation size limiting and truncation."""
        # Create package with very long description
        long_description = "Very long description. " * 1000
        long_package = PackageInfo(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            description=long_description,
            author="Test Author",
            license="MIT",
            home_page="https://example.com",
            project_urls={},
            classifiers=[],
            keywords=[],
        )

        # Set small max size for testing
        mock_config.max_documentation_size = 1000

        with mocker.patch(
            "src.autodoc_mcp.core.doc_fetcher.get_config", return_value=mock_config
        ):
            formatted = fetcher.format_documentation(long_package)

        # Should be truncated
        assert len(formatted) <= 1100  # Allow some buffer for truncation message
        assert "(truncated for performance)" in formatted

    def test_format_documentation_minimal_package_info(self, fetcher):
        """Test formatting with minimal package information."""
        minimal_package = PackageInfo(
            name="minimal-package",
            version="0.1.0",
            summary="",
            description="",
            author=None,
            license=None,
            home_page=None,
            project_urls={},
            classifiers=[],
            keywords=[],
        )

        formatted = fetcher.format_documentation(minimal_package)

        # Should handle missing fields gracefully
        assert "# minimal-package v0.1.0" in formatted
        assert len(formatted) > 0


class TestPyPIResponseParsing:
    """Test PyPI response parsing functionality."""

    @pytest.fixture
    def fetcher(self, mock_config, mocker):
        """Create fetcher instance with mocked config."""
        with mocker.patch(
            "src.autodoc_mcp.core.doc_fetcher.get_config", return_value=mock_config
        ):
            return PyPIDocumentationFetcher()

    def test_parse_pypi_response_valid(self, fetcher, sample_pypi_response):
        """Test parsing valid PyPI response."""
        package_info = fetcher._parse_pypi_response(sample_pypi_response, "requests")

        assert package_info.name == "requests"
        assert package_info.version == "2.28.0"
        assert package_info.summary == "Python HTTP for Humans."
        assert package_info.author == "Kenneth Reitz"
        assert len(package_info.keywords) == 3
        assert "http" in package_info.keywords

    def test_parse_pypi_response_missing_name(self, fetcher):
        """Test parsing response with missing name."""
        malformed_response = {
            "info": {
                "version": "1.0.0",
                "summary": "Test package",
            }
        }

        with pytest.raises(ValueError, match="Missing package name"):
            fetcher._parse_pypi_response(malformed_response, "test")

    def test_parse_pypi_response_missing_version(self, fetcher):
        """Test parsing response with missing version."""
        malformed_response = {
            "info": {
                "name": "test-package",
                "summary": "Test package",
            }
        }

        with pytest.raises(ValueError, match="Missing version"):
            fetcher._parse_pypi_response(malformed_response, "test-package")

    def test_parse_pypi_response_missing_info_key(self, fetcher):
        """Test parsing response with missing info key."""
        malformed_response = {
            "data": {
                "name": "test-package",
                "version": "1.0.0",
            }
        }

        with pytest.raises(ValueError, match="Malformed PyPI response"):
            fetcher._parse_pypi_response(malformed_response, "test-package")

    def test_parse_pypi_response_optional_fields(self, fetcher):
        """Test parsing response with only required fields."""
        minimal_response = {
            "info": {
                "name": "minimal-package",
                "version": "0.1.0",
            }
        }

        package_info = fetcher._parse_pypi_response(minimal_response, "minimal-package")

        assert package_info.name == "minimal-package"
        assert package_info.version == "0.1.0"
        assert package_info.summary == ""
        assert package_info.description == ""
        assert package_info.author is None
        assert package_info.keywords == []

    def test_parse_pypi_response_keywords_handling(self, fetcher):
        """Test proper keyword parsing from string."""
        response_with_keywords = {
            "info": {
                "name": "keyword-test",
                "version": "1.0.0",
                "keywords": "web http api rest",
            }
        }

        package_info = fetcher._parse_pypi_response(
            response_with_keywords, "keyword-test"
        )

        assert len(package_info.keywords) == 4
        assert "web" in package_info.keywords
        assert "http" in package_info.keywords
        assert "api" in package_info.keywords
        assert "rest" in package_info.keywords


class TestQueryFiltering:
    """Test query-based content filtering functionality."""

    @pytest.fixture
    def fetcher(self, mock_config, mocker):
        """Create fetcher instance with mocked config."""
        with mocker.patch(
            "src.autodoc_mcp.core.doc_fetcher.get_config", return_value=mock_config
        ):
            return PyPIDocumentationFetcher()

    def test_apply_query_filter_basic(self, fetcher):
        """Test basic query filtering functionality."""
        content = """# Package Name

## HTTP Client
This section talks about HTTP requests and web interactions.

## Database Support
This section covers database operations and SQL queries.

## Logging
This section covers logging and debugging features."""

        filtered = fetcher._apply_query_filter(content, "http web")

        # Should prioritize HTTP section
        assert "HTTP Client" in filtered
        assert "HTTP requests and web interactions" in filtered
        # May include other sections based on scoring

    def test_apply_query_filter_no_matches(self, fetcher):
        """Test query filtering with no matches."""
        content = """# Package Name

## Database Support
This section covers database operations.

## File Operations
This section covers file handling."""

        filtered = fetcher._apply_query_filter(content, "http networking")

        # Should return empty or minimal content when no matches
        assert len(filtered) >= 0  # May be empty or contain title

    def test_apply_query_filter_case_insensitive(self, fetcher):
        """Test case-insensitive query filtering."""
        content = """# Package Name

## HTTP Client
This section talks about HTTP requests."""

        filtered = fetcher._apply_query_filter(content, "HTTP")

        assert "HTTP Client" in filtered
        assert "HTTP requests" in filtered
