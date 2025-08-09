"""Unit tests for network client functionality."""

import httpx
import pytest

from src.autodoc_mcp.core.network_client import (
    BasicNetworkClient,
    NetworkResilientClient,
)
from src.autodoc_mcp.exceptions import NetworkError, PackageNotFoundError


class TestBasicNetworkClientInitialization:
    """Test network client initialization and lifecycle."""

    def test_init_creates_none_client(self):
        """Test that initialization sets client to None."""
        client = BasicNetworkClient()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_aenter_creates_client(self, mocker):
        """Test async context manager entry creates httpx client."""
        mock_httpx_client = mocker.patch("httpx.AsyncClient")
        mock_instance = mocker.AsyncMock()
        mock_httpx_client.return_value = mock_instance

        client = BasicNetworkClient()
        result = await client.__aenter__()

        assert result is client
        assert client._client is mock_instance
        mock_httpx_client.assert_called_once_with(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
            headers={"User-Agent": "AutoDocs-MCP/1.0"},
        )

    @pytest.mark.asyncio
    async def test_aexit_closes_client(self, mocker):
        """Test async context manager exit closes httpx client."""
        mock_client = mocker.AsyncMock()

        client = BasicNetworkClient()
        client._client = mock_client

        await client.__aexit__(None, None, None)

        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexit_with_none_client(self):
        """Test async context manager exit with None client."""
        client = BasicNetworkClient()
        client._client = None

        # Should not raise exception
        await client.__aexit__(None, None, None)

    @pytest.mark.asyncio
    async def test_aexit_handles_exception_context(self, mocker):
        """Test async context manager exit with exception context."""
        mock_client = mocker.AsyncMock()

        client = BasicNetworkClient()
        client._client = mock_client

        # Pass exception context
        await client.__aexit__(ValueError, ValueError("test"), None)

        mock_client.aclose.assert_called_once()


class TestNetworkResilientClientAlias:
    """Test NetworkResilientClient alias."""

    def test_alias_points_to_basic_client(self):
        """Test that NetworkResilientClient is an alias for BasicNetworkClient."""
        assert NetworkResilientClient is BasicNetworkClient

    def test_alias_creates_same_instance(self):
        """Test that alias creates the same type of instance."""
        client1 = BasicNetworkClient()
        client2 = NetworkResilientClient()

        assert type(client1) is type(client2)
        assert isinstance(client2, BasicNetworkClient)


class TestGetWithRetryClientValidation:
    """Test client validation in get_with_retry."""

    @pytest.mark.asyncio
    async def test_get_with_retry_no_client_raises_error(self):
        """Test get_with_retry raises NetworkError when client is None."""
        client = BasicNetworkClient()
        # Don't initialize client
        assert client._client is None

        with pytest.raises(NetworkError, match="HTTP client not initialized"):
            await client.get_with_retry("https://example.com")


class TestGetWithRetrySuccessScenarios:
    """Test successful request scenarios."""

    @pytest.mark.asyncio
    async def test_get_with_retry_success_first_attempt(self, mocker):
        """Test successful request on first attempt."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(return_value=mock_response)

        client = BasicNetworkClient()
        client._client = mock_client

        result = await client.get_with_retry("https://example.com", param="value")

        assert result is mock_response
        mock_client.get.assert_called_once_with("https://example.com", param="value")
        mock_response.raise_for_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_with_retry_success_after_failures(self, mocker):
        """Test successful request after some failures."""
        # First two attempts fail, third succeeds
        mock_timeout_error = httpx.TimeoutException("Timeout")
        mock_success_response = mocker.Mock()
        mock_success_response.status_code = 200
        mock_success_response.raise_for_status = mocker.Mock()

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(
            side_effect=[mock_timeout_error, mock_timeout_error, mock_success_response]
        )

        client = BasicNetworkClient()
        client._client = mock_client

        # Mock asyncio.sleep to avoid actual delays in tests
        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        result = await client.get_with_retry("https://example.com")

        assert result is mock_success_response
        assert mock_client.get.call_count == 3
        # Should have slept twice (after first and second failures)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # 2^(1-1) = 1
        mock_sleep.assert_any_call(2)  # 2^(2-1) = 2


class TestGetWithRetry404Handling:
    """Test 404 handling scenarios."""

    @pytest.mark.asyncio
    async def test_get_with_retry_404_status_code(self, mocker):
        """Test 404 status code raises PackageNotFoundError."""
        mock_response = mocker.Mock()
        mock_response.status_code = 404

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(return_value=mock_response)

        client = BasicNetworkClient()
        client._client = mock_client

        with pytest.raises(
            PackageNotFoundError, match="Resource not found: https://example.com"
        ):
            await client.get_with_retry("https://example.com")

    @pytest.mark.asyncio
    async def test_get_with_retry_404_http_status_error(self, mocker):
        """Test 404 HTTPStatusError raises PackageNotFoundError."""
        mock_response = mocker.Mock()
        mock_response.status_code = 404

        mock_http_error = httpx.HTTPStatusError(
            message="Not Found", request=mocker.Mock(), response=mock_response
        )

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_http_error)

        client = BasicNetworkClient()
        client._client = mock_client

        with pytest.raises(
            PackageNotFoundError, match="Resource not found: https://example.com"
        ):
            await client.get_with_retry("https://example.com")


class TestGetWithRetryTimeoutHandling:
    """Test timeout handling and backoff logic."""

    @pytest.mark.asyncio
    async def test_get_with_retry_timeout_all_attempts_fail(self, mocker):
        """Test timeout on all attempts raises NetworkError."""
        mock_timeout_error = httpx.TimeoutException("Request timeout")

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_timeout_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError, match="Request timeout after 3 attempts"):
            await client.get_with_retry("https://example.com")

        # Should attempt 3 times
        assert mock_client.get.call_count == 3
        # Should sleep twice (after first two failures)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # 2^(1-1) = 1
        mock_sleep.assert_any_call(2)  # 2^(2-1) = 2

    @pytest.mark.asyncio
    async def test_get_with_retry_timeout_exponential_backoff(self, mocker):
        """Test timeout uses exponential backoff correctly."""
        mock_timeout_error = httpx.TimeoutException("Request timeout")

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_timeout_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError):
            await client.get_with_retry("https://example.com")

        # Verify exponential backoff: 2^0=1, 2^1=2
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls == [1, 2]


class TestGetWithRetryHTTPStatusErrorHandling:
    """Test HTTP status error handling for different status codes."""

    @pytest.mark.asyncio
    async def test_get_with_retry_4xx_client_error_no_retry(self, mocker):
        """Test 4xx client errors (except 408, 429) don't retry."""
        mock_response = mocker.Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request Error Message"

        mock_http_error = httpx.HTTPStatusError(
            message="Bad Request", request=mocker.Mock(), response=mock_response
        )

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_http_error)

        client = BasicNetworkClient()
        client._client = mock_client

        with pytest.raises(NetworkError, match="HTTP 400: Bad Request Error Message"):
            await client.get_with_retry("https://example.com")

        # Should only attempt once (no retry for 4xx except 408, 429)
        assert mock_client.get.call_count == 1

    @pytest.mark.asyncio
    async def test_get_with_retry_408_timeout_retries(self, mocker):
        """Test 408 Request Timeout retries with backoff."""
        mock_response = mocker.Mock()
        mock_response.status_code = 408
        mock_response.text = "Request Timeout"

        mock_http_error = httpx.HTTPStatusError(
            message="Request Timeout", request=mocker.Mock(), response=mock_response
        )

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_http_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError, match="HTTP error after 3 attempts"):
            await client.get_with_retry("https://example.com")

        # Should retry 3 times for 408
        assert mock_client.get.call_count == 3
        assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_get_with_retry_429_rate_limit_retries(self, mocker):
        """Test 429 Rate Limit retries with backoff."""
        mock_response = mocker.Mock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"

        mock_http_error = httpx.HTTPStatusError(
            message="Too Many Requests", request=mocker.Mock(), response=mock_response
        )

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_http_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError, match="HTTP error after 3 attempts"):
            await client.get_with_retry("https://example.com")

        # Should retry 3 times for 429
        assert mock_client.get.call_count == 3
        assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_get_with_retry_5xx_server_error_retries(self, mocker):
        """Test 5xx server errors retry with backoff."""
        mock_response = mocker.Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_http_error = httpx.HTTPStatusError(
            message="Internal Server Error",
            request=mocker.Mock(),
            response=mock_response,
        )

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_http_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError, match="HTTP error after 3 attempts"):
            await client.get_with_retry("https://example.com")

        # Should retry 3 times for 5xx errors
        assert mock_client.get.call_count == 3
        assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_get_with_retry_403_forbidden_no_retry(self, mocker):
        """Test 403 Forbidden doesn't retry."""
        mock_response = mocker.Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden Access"

        mock_http_error = httpx.HTTPStatusError(
            message="Forbidden", request=mocker.Mock(), response=mock_response
        )

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_http_error)

        client = BasicNetworkClient()
        client._client = mock_client

        with pytest.raises(NetworkError, match="HTTP 403: Forbidden Access"):
            await client.get_with_retry("https://example.com")

        # Should only attempt once
        assert mock_client.get.call_count == 1

    @pytest.mark.asyncio
    async def test_get_with_retry_response_text_truncation(self, mocker):
        """Test response text is truncated to 200 chars in error message."""
        long_text = "x" * 300  # 300 character error message

        mock_response = mocker.Mock()
        mock_response.status_code = 400
        mock_response.text = long_text

        mock_http_error = httpx.HTTPStatusError(
            message="Bad Request", request=mocker.Mock(), response=mock_response
        )

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_http_error)

        client = BasicNetworkClient()
        client._client = mock_client

        with pytest.raises(NetworkError) as exc_info:
            await client.get_with_retry("https://example.com")

        # Error message should contain only first 200 characters
        error_message = str(exc_info.value)
        assert "x" * 200 in error_message
        assert len([char for char in error_message if char == "x"]) == 200


class TestGetWithRetryRequestErrorHandling:
    """Test request error handling scenarios."""

    @pytest.mark.asyncio
    async def test_get_with_retry_request_error_all_attempts_fail(self, mocker):
        """Test RequestError on all attempts raises NetworkError."""
        mock_request_error = httpx.RequestError("Connection failed")

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_request_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(
            NetworkError, match="Network error after 3 attempts: Connection failed"
        ):
            await client.get_with_retry("https://example.com")

        # Should attempt 3 times
        assert mock_client.get.call_count == 3
        # Should sleep twice (after first two failures)
        assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_get_with_retry_request_error_success_after_retry(self, mocker):
        """Test RequestError followed by success."""
        mock_request_error = httpx.RequestError("Connection failed")
        mock_success_response = mocker.Mock()
        mock_success_response.status_code = 200
        mock_success_response.raise_for_status = mocker.Mock()

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(
            side_effect=[mock_request_error, mock_success_response]
        )

        client = BasicNetworkClient()
        client._client = mock_client

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        result = await client.get_with_retry("https://example.com")

        assert result is mock_success_response
        assert mock_client.get.call_count == 2
        assert mock_sleep.call_count == 1  # One sleep after first failure
        mock_sleep.assert_called_with(1)  # 2^(1-1) = 1


class TestGetWithRetryMixedErrorScenarios:
    """Test mixed error scenarios and edge cases."""

    @pytest.mark.asyncio
    async def test_get_with_retry_mixed_errors_with_success(self, mocker):
        """Test mix of different error types followed by success."""
        mock_timeout_error = httpx.TimeoutException("Timeout")

        mock_response_429 = mocker.Mock()
        mock_response_429.status_code = 429
        mock_response_429.text = "Rate Limited"
        mock_http_error_429 = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=mocker.Mock(),
            response=mock_response_429,
        )

        mock_success_response = mocker.Mock()
        mock_success_response.status_code = 200
        mock_success_response.raise_for_status = mocker.Mock()

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(
            side_effect=[mock_timeout_error, mock_http_error_429, mock_success_response]
        )

        client = BasicNetworkClient()
        client._client = mock_client

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        result = await client.get_with_retry("https://example.com")

        assert result is mock_success_response
        assert mock_client.get.call_count == 3
        assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_get_with_retry_max_attempts_boundary(self, mocker):
        """Test that exactly 3 attempts are made before giving up."""
        mock_request_error = httpx.RequestError("Connection failed")

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_request_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError):
            await client.get_with_retry("https://example.com")

        # Verify exactly 3 attempts
        assert mock_client.get.call_count == 3
        # Verify exactly 2 sleep calls (between attempts)
        assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_get_with_retry_max_attempts_boundary_verification(self, mocker):
        """Test that exactly max_attempts are made before giving up."""
        # Test ensures the loop logic works correctly
        mock_request_error = httpx.RequestError("Connection failed")

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_request_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError, match="Network error after 3 attempts"):
            await client.get_with_retry("https://example.com")

        # Verify exactly 3 attempts as expected
        assert mock_client.get.call_count == 3
        # Verify exactly 2 sleep calls (between attempts)
        assert mock_sleep.call_count == 2


class TestGetWithRetryLoggingVerification:
    """Test that proper logging occurs during retry attempts."""

    @pytest.mark.asyncio
    async def test_get_with_retry_debug_logging_on_success(self, mocker):
        """Test debug logging occurs on successful requests."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(return_value=mock_response)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_logger = mocker.patch("src.autodoc_mcp.core.network_client.logger")

        await client.get_with_retry("https://example.com")

        mock_logger.debug.assert_called_with(
            "Making HTTP request", url="https://example.com", attempt=1
        )

    @pytest.mark.asyncio
    async def test_get_with_retry_warning_logging_on_timeout(self, mocker):
        """Test warning logging occurs on timeout."""
        mock_timeout_error = httpx.TimeoutException("Timeout")

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_timeout_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_logger = mocker.patch("src.autodoc_mcp.core.network_client.logger")
        mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError):
            await client.get_with_retry("https://example.com")

        # Should log warning for each timeout attempt
        assert mock_logger.warning.call_count == 3
        mock_logger.warning.assert_any_call(
            "Request timeout", url="https://example.com", attempt=1
        )
        mock_logger.warning.assert_any_call(
            "Request timeout", url="https://example.com", attempt=2
        )
        mock_logger.warning.assert_any_call(
            "Request timeout", url="https://example.com", attempt=3
        )

    @pytest.mark.asyncio
    async def test_get_with_retry_warning_logging_on_http_error(self, mocker):
        """Test warning logging occurs on retryable HTTP errors."""
        mock_response = mocker.Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"

        mock_http_error = httpx.HTTPStatusError(
            message="Server Error", request=mocker.Mock(), response=mock_response
        )

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_http_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_logger = mocker.patch("src.autodoc_mcp.core.network_client.logger")
        mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError):
            await client.get_with_retry("https://example.com")

        # Should log warning for each HTTP error attempt
        assert mock_logger.warning.call_count == 3
        mock_logger.warning.assert_any_call(
            "HTTP error",
            url="https://example.com",
            status=500,
            attempt=1,
        )

    @pytest.mark.asyncio
    async def test_get_with_retry_warning_logging_on_request_error(self, mocker):
        """Test warning logging occurs on request errors."""
        mock_request_error = httpx.RequestError("Connection failed")

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(side_effect=mock_request_error)

        client = BasicNetworkClient()
        client._client = mock_client

        mock_logger = mocker.patch("src.autodoc_mcp.core.network_client.logger")
        mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError):
            await client.get_with_retry("https://example.com")

        # Should log warning for each request error attempt
        assert mock_logger.warning.call_count == 3
        mock_logger.warning.assert_any_call(
            "Network error",
            url="https://example.com",
            error="Connection failed",
            attempt=1,
        )


class TestAsyncContextManagerIntegration:
    """Test full async context manager integration scenarios."""

    @pytest.mark.asyncio
    async def test_full_context_manager_workflow(self, mocker):
        """Test complete async context manager workflow."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()

        mock_httpx_client = mocker.patch("httpx.AsyncClient")
        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.get = mocker.AsyncMock(return_value=mock_response)
        mock_httpx_client.return_value = mock_client_instance

        async with BasicNetworkClient() as client:
            result = await client.get_with_retry("https://example.com")

        assert result is mock_response
        mock_client_instance.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_with_exception(self, mocker):
        """Test context manager cleanup when exception occurs."""
        mock_httpx_client = mocker.patch("httpx.AsyncClient")
        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.get = mocker.AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )
        mock_httpx_client.return_value = mock_client_instance

        mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        with pytest.raises(NetworkError, match="Network error after 3 attempts"):
            async with BasicNetworkClient() as client:
                await client.get_with_retry("https://example.com")

        # Should still close even when exception occurs
        mock_client_instance.aclose.assert_called_once()
