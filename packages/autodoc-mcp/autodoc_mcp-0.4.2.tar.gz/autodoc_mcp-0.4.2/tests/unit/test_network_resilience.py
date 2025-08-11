"""Unit tests for network resilience functionality."""

import time

import httpx
import pytest

from src.autodoc_mcp.core.network_resilience import (
    CircuitBreaker,
    ConnectionPoolManager,
    NetworkResilientClient,
    RateLimiter,
    RetryConfig,
)
from src.autodoc_mcp.exceptions import NetworkError, PackageNotFoundError


class TestRetryConfig:
    """Test RetryConfig dataclass configuration."""

    def test_default_values(self):
        """Test RetryConfig default values."""
        config = RetryConfig()

        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True

    def test_custom_values(self):
        """Test RetryConfig with custom values."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.5,
            max_delay=30.0,
            exponential_base=1.5,
            jitter=False,
        )

        assert config.max_attempts == 5
        assert config.base_delay == 0.5
        assert config.max_delay == 30.0
        assert config.exponential_base == 1.5
        assert config.jitter is False

    def test_config_mutability(self):
        """Test that RetryConfig fields can be modified (not frozen)."""
        config = RetryConfig()

        # Test that we can modify fields after creation (dataclass is not frozen)
        config.max_attempts = 5
        assert config.max_attempts == 5


class TestConnectionPoolManager:
    """Test ConnectionPoolManager singleton behavior."""

    def test_singleton_pattern(self):
        """Test that ConnectionPoolManager follows singleton pattern."""
        manager1 = ConnectionPoolManager()
        manager2 = ConnectionPoolManager()

        assert manager1 is manager2
        assert id(manager1) == id(manager2)

    def test_initialization_once(self):
        """Test that initialization only happens once."""
        manager = ConnectionPoolManager()

        # Should have initialized attribute
        assert hasattr(manager, "initialized")
        assert manager.initialized is True
        assert hasattr(manager, "_clients")
        assert isinstance(manager._clients, dict)

    @pytest.mark.asyncio
    async def test_get_client_creates_new_client(self, mocker):
        """Test get_client creates new httpx client with proper config."""
        mock_config = mocker.Mock()
        mock_config.request_timeout = 45.0
        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )

        mock_httpx_client = mocker.patch("httpx.AsyncClient")
        mock_client_instance = mocker.AsyncMock()
        mock_httpx_client.return_value = mock_client_instance

        manager = ConnectionPoolManager()
        # Clear any existing clients
        manager._clients.clear()

        result = await manager.get_client("test")

        assert result is mock_client_instance
        mock_httpx_client.assert_called_once_with(
            timeout=httpx.Timeout(45.0),
            follow_redirects=True,
            headers={"User-Agent": "AutoDocs-MCP/1.0"},
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=30.0,
            ),
        )

    @pytest.mark.asyncio
    async def test_get_client_reuses_existing_client(self, mocker):
        """Test get_client reuses existing client for same config_key."""
        mock_config = mocker.Mock()
        mock_config.request_timeout = 30.0
        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )

        mock_httpx_client = mocker.patch("httpx.AsyncClient")
        mock_client_instance = mocker.AsyncMock()
        mock_httpx_client.return_value = mock_client_instance

        manager = ConnectionPoolManager()
        # Clear any existing clients
        manager._clients.clear()

        # Get client twice with same key
        result1 = await manager.get_client("test")
        result2 = await manager.get_client("test")

        assert result1 is result2
        assert result1 is mock_client_instance
        # Should only create once
        mock_httpx_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_different_keys_create_different_clients(self, mocker):
        """Test different config keys create different clients."""
        mock_config = mocker.Mock()
        mock_config.request_timeout = 30.0
        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )

        mock_httpx_client = mocker.patch("httpx.AsyncClient")
        mock_client1 = mocker.AsyncMock()
        mock_client2 = mocker.AsyncMock()
        mock_httpx_client.side_effect = [mock_client1, mock_client2]

        manager = ConnectionPoolManager()
        # Clear any existing clients
        manager._clients.clear()

        result1 = await manager.get_client("test1")
        result2 = await manager.get_client("test2")

        assert result1 is mock_client1
        assert result2 is mock_client2
        assert result1 is not result2
        # Should create twice for different keys
        assert mock_httpx_client.call_count == 2

    @pytest.mark.asyncio
    async def test_get_client_default_key(self, mocker):
        """Test get_client with default config key."""
        mock_config = mocker.Mock()
        mock_config.request_timeout = 30.0
        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )

        mock_httpx_client = mocker.patch("httpx.AsyncClient")
        mock_client_instance = mocker.AsyncMock()
        mock_httpx_client.return_value = mock_client_instance

        manager = ConnectionPoolManager()
        # Clear any existing clients
        manager._clients.clear()

        result = await manager.get_client()  # No key provided - should use "default"

        assert result is mock_client_instance
        assert "default" in manager._clients

    @pytest.mark.asyncio
    async def test_close_all_clients(self, mocker):
        """Test close_all closes all clients and clears the dict."""
        mock_client1 = mocker.AsyncMock()
        mock_client2 = mocker.AsyncMock()

        manager = ConnectionPoolManager()
        manager._clients = {
            "client1": mock_client1,
            "client2": mock_client2,
        }

        await manager.close_all()

        mock_client1.aclose.assert_called_once()
        mock_client2.aclose.assert_called_once()
        assert len(manager._clients) == 0

    @pytest.mark.asyncio
    async def test_close_all_empty_clients(self):
        """Test close_all with no clients doesn't raise errors."""
        manager = ConnectionPoolManager()
        manager._clients.clear()

        # Should not raise any exceptions
        await manager.close_all()

        assert len(manager._clients) == 0

    @pytest.mark.asyncio
    async def test_thread_safety_with_lock(self, mocker):
        """Test that get_client operations are thread-safe with async lock."""
        mock_config = mocker.Mock()
        mock_config.request_timeout = 30.0
        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )

        mock_httpx_client = mocker.patch("httpx.AsyncClient")
        mock_client_instance = mocker.AsyncMock()
        mock_httpx_client.return_value = mock_client_instance

        manager = ConnectionPoolManager()
        manager._clients.clear()

        # Replace the lock with a mock to verify it's used
        mock_lock = mocker.AsyncMock()
        manager._lock = mock_lock

        await manager.get_client("test")

        # Verify lock was acquired and released
        mock_lock.__aenter__.assert_called_once()
        mock_lock.__aexit__.assert_called_once()


class TestCircuitBreaker:
    """Test CircuitBreaker functionality."""

    def test_init_default_values(self):
        """Test CircuitBreaker initialization with default values."""
        cb = CircuitBreaker()

        assert cb.failure_threshold == 5
        assert cb.reset_timeout == 60.0
        assert cb._failure_count == 0
        assert cb._last_failure_time == 0.0
        assert cb._state == "closed"

    def test_init_custom_values(self):
        """Test CircuitBreaker initialization with custom values."""
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=30.0)

        assert cb.failure_threshold == 3
        assert cb.reset_timeout == 30.0

    def test_is_open_closed_state(self):
        """Test is_open returns False when circuit is closed."""
        cb = CircuitBreaker()

        assert cb.is_open() is False
        assert cb._state == "closed"

    def test_is_open_half_open_state(self):
        """Test is_open returns False when circuit is half-open."""
        cb = CircuitBreaker()
        cb._state = "half_open"

        assert cb.is_open() is False

    def test_is_open_open_state_within_timeout(self):
        """Test is_open returns True when circuit is open and within timeout."""
        cb = CircuitBreaker(reset_timeout=60.0)
        cb._state = "open"
        cb._last_failure_time = time.time()  # Recent failure

        assert cb.is_open() is True

    def test_is_open_open_state_timeout_expired(self):
        """Test is_open transitions to half_open when timeout expires."""
        cb = CircuitBreaker(reset_timeout=1.0)
        cb._state = "open"
        cb._last_failure_time = time.time() - 2.0  # Failure more than timeout ago

        assert cb.is_open() is False
        assert cb._state == "half_open"

    def test_record_success_resets_state(self):
        """Test record_success resets failure count and state."""
        cb = CircuitBreaker()
        cb._failure_count = 3
        cb._state = "half_open"

        cb.record_success()

        assert cb._failure_count == 0
        assert cb._state == "closed"

    def test_record_failure_increments_count(self):
        """Test record_failure increments failure count and sets timestamp."""
        cb = CircuitBreaker()
        initial_time = cb._last_failure_time

        cb.record_failure()

        assert cb._failure_count == 1
        assert cb._last_failure_time > initial_time

    def test_record_failure_opens_circuit_at_threshold(self, mocker):
        """Test record_failure opens circuit when threshold is reached."""
        mock_logger = mocker.patch("src.autodoc_mcp.core.network_resilience.logger")

        cb = CircuitBreaker(failure_threshold=3)

        # Record failures up to threshold
        cb.record_failure()  # 1
        cb.record_failure()  # 2
        assert cb._state == "closed"

        cb.record_failure()  # 3 - should open
        assert cb._state == "open"
        assert cb._failure_count == 3

        mock_logger.warning.assert_called_once_with(
            "Circuit breaker opened", failure_count=3
        )

    def test_record_failure_doesnt_open_below_threshold(self):
        """Test record_failure doesn't open circuit below threshold."""
        cb = CircuitBreaker(failure_threshold=5)

        # Record failures below threshold
        cb.record_failure()  # 1
        cb.record_failure()  # 2
        cb.record_failure()  # 3
        cb.record_failure()  # 4

        assert cb._state == "closed"
        assert cb._failure_count == 4

    def test_state_transitions_full_cycle(self, mocker):
        """Test complete state transition cycle: closed -> open -> half_open -> closed."""
        mocker.patch("src.autodoc_mcp.core.network_resilience.logger")

        cb = CircuitBreaker(failure_threshold=2, reset_timeout=0.1)

        # Start in closed state
        assert cb._state == "closed"
        assert cb.is_open() is False

        # Record failures to open circuit
        cb.record_failure()
        cb.record_failure()  # Should open
        assert cb._state == "open"
        assert cb.is_open() is True

        # Mock time to simulate timeout expiration
        mocker.patch("time.time", return_value=cb._last_failure_time + 0.2)
        assert cb.is_open() is False
        assert cb._state == "half_open"

        # Record success to close
        cb.record_success()
        assert cb._state == "closed"
        assert cb._failure_count == 0


class TestRateLimiter:
    """Test RateLimiter functionality."""

    def test_init_default_values(self):
        """Test RateLimiter initialization with default values."""
        rl = RateLimiter()

        assert rl.requests_per_minute == 60
        assert len(rl.requests) == 0
        assert rl._max_entries == max(60 * 2, 1000)  # 1000
        assert isinstance(rl._last_cleanup, float)

    def test_init_custom_values(self):
        """Test RateLimiter initialization with custom values."""
        rl = RateLimiter(requests_per_minute=30)

        assert rl.requests_per_minute == 30
        assert rl._max_entries == max(30 * 2, 1000)  # 1000 (safety limit)

    def test_init_low_requests_per_minute(self):
        """Test RateLimiter with very low requests_per_minute uses safety limit."""
        rl = RateLimiter(requests_per_minute=10)

        assert rl.requests_per_minute == 10
        assert rl._max_entries == 1000  # Safety limit

    @pytest.mark.asyncio
    async def test_acquire_first_request(self):
        """Test acquire allows first request immediately."""
        rl = RateLimiter(requests_per_minute=60)

        start_time = time.time()
        await rl.acquire()
        end_time = time.time()

        # Should not have waited
        assert end_time - start_time < 0.1
        assert len(rl.requests) == 1

    @pytest.mark.asyncio
    async def test_acquire_within_limit(self):
        """Test acquire allows requests within rate limit."""
        rl = RateLimiter(requests_per_minute=60)

        # Make several requests within limit
        for _ in range(10):
            await rl.acquire()

        assert len(rl.requests) == 10

    @pytest.mark.asyncio
    async def test_acquire_cleanup_old_requests(self, mocker):
        """Test acquire cleans up old requests automatically."""
        rl = RateLimiter(requests_per_minute=60)

        # Add some old requests (more than 60 seconds ago)
        old_time = time.time() - 120
        for _ in range(5):
            rl.requests.append(old_time)

        # Add recent request
        await rl.acquire()

        # Old requests should be cleaned up, only recent one remains
        assert len(rl.requests) == 1
        assert all(req >= time.time() - 60 for req in rl.requests)

    @pytest.mark.asyncio
    async def test_acquire_rate_limiting_sleep(self, mocker):
        """Test acquire sleeps when rate limit is exceeded."""
        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        rl = RateLimiter(requests_per_minute=2)

        # Fill up the rate limit with recent requests
        current_time = time.time()
        rl.requests.append(current_time - 30)  # 30 seconds ago
        rl.requests.append(current_time - 20)  # 20 seconds ago

        await rl.acquire()

        # Should have slept to wait for the oldest request to expire
        mock_sleep.assert_called_once()
        # Sleep time should be roughly 60 - (current_time - oldest_request) + buffer
        sleep_time = mock_sleep.call_args[0][0]
        assert sleep_time > 29  # At least 30 seconds - some buffer
        assert sleep_time < 41  # Less than 40 seconds + buffer

    @pytest.mark.asyncio
    async def test_acquire_force_cleanup_every_60_seconds(self, mocker):
        """Test acquire performs force cleanup every 60 seconds."""
        mock_force_cleanup = mocker.patch.object(
            RateLimiter, "_force_cleanup", new_callable=mocker.AsyncMock
        )

        rl = RateLimiter()
        rl._last_cleanup = time.time() - 70  # 70 seconds ago

        await rl.acquire()

        mock_force_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_acquire_emergency_cleanup(self, mocker):
        """Test acquire performs emergency cleanup when deque is too large."""
        mock_logger = mocker.patch("src.autodoc_mcp.core.network_resilience.logger")
        mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        rl = RateLimiter(requests_per_minute=10)
        rl._max_entries = 20  # Small number for testing

        # Mock the cleanup methods to avoid actual processing and make them clear the deque
        async def mock_force_cleanup_impl(now):
            rl.requests.clear()  # Clear the deque to avoid rate limiting

        mock_force_cleanup = mocker.patch.object(
            rl, "_force_cleanup", side_effect=mock_force_cleanup_impl
        )
        mocker.patch.object(rl, "_cleanup_old_requests", new_callable=mocker.AsyncMock)

        # Fill deque beyond max_entries
        current_time = time.time()
        for _ in range(rl._max_entries + 5):  # 25 entries
            rl.requests.append(current_time)

        await rl.acquire()

        # Should have triggered emergency cleanup
        mock_force_cleanup.assert_called()
        mock_logger.warning.assert_called_with(
            "Rate limiter deque exceeded max size, forcing cleanup",
            current_size=rl._max_entries + 5,
            max_size=rl._max_entries,
        )

    @pytest.mark.asyncio
    async def test_cleanup_old_requests(self):
        """Test _cleanup_old_requests removes old entries."""
        rl = RateLimiter()

        # Add mix of old and recent requests
        current_time = time.time()
        rl.requests.append(current_time - 120)  # Old
        rl.requests.append(current_time - 90)  # Old
        rl.requests.append(current_time - 30)  # Recent
        rl.requests.append(current_time - 10)  # Recent

        await rl._cleanup_old_requests(current_time)

        # Should keep only recent requests (within last 60 seconds)
        assert len(rl.requests) == 2
        assert all(req >= current_time - 60 for req in rl.requests)

    @pytest.mark.asyncio
    async def test_force_cleanup_removes_old_entries(self):
        """Test _force_cleanup removes entries older than 60 seconds."""
        rl = RateLimiter()

        # Add mix of old and recent requests
        current_time = time.time()
        rl.requests.append(current_time - 120)  # Old
        rl.requests.append(current_time - 90)  # Old
        rl.requests.append(current_time - 30)  # Recent
        rl.requests.append(current_time - 10)  # Recent

        await rl._force_cleanup(current_time)

        # Should keep only recent requests
        assert len(rl.requests) == 2
        assert all(req >= current_time - 60 for req in rl.requests)

    @pytest.mark.asyncio
    async def test_force_cleanup_limits_recent_entries(self):
        """Test _force_cleanup limits even recent entries if too many."""
        rl = RateLimiter(requests_per_minute=10)

        # Add many recent requests (more than requests_per_minute)
        current_time = time.time()
        for i in range(20):
            rl.requests.append(current_time - (i * 2))  # All recent (within 60s)

        await rl._force_cleanup(current_time)

        # Should keep only requests_per_minute most recent entries
        assert len(rl.requests) == rl.requests_per_minute


class TestNetworkResilientClient:
    """Test NetworkResilientClient integration."""

    def test_init_with_default_config(self, mocker):
        """Test NetworkResilientClient initialization with default config."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        client = NetworkResilientClient()

        assert client.retry_config.max_attempts == 3
        assert client.retry_config.base_delay == 1.0
        assert client.retry_config.max_delay == 60.0
        assert client._client is None
        assert isinstance(client._circuit_breaker, CircuitBreaker)
        assert isinstance(client._rate_limiter, RateLimiter)

    def test_init_with_custom_retry_config(self, mocker):
        """Test NetworkResilientClient initialization with custom retry config."""
        mock_config = mocker.Mock()
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        custom_config = RetryConfig(max_attempts=5, base_delay=0.5)
        client = NetworkResilientClient(retry_config=custom_config)

        assert client.retry_config is custom_config
        assert client.retry_config.max_attempts == 5
        assert client.retry_config.base_delay == 0.5

    @pytest.mark.asyncio
    async def test_aenter_gets_client_from_pool(self, mocker):
        """Test async context manager entry gets client from pool."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )

        mock_pool_manager = mocker.Mock()
        mock_client = mocker.AsyncMock()
        mock_pool_manager.get_client = mocker.AsyncMock(return_value=mock_client)

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.ConnectionPoolManager",
            return_value=mock_pool_manager,
        )

        client = NetworkResilientClient()
        result = await client.__aenter__()

        assert result is client
        assert client._client is mock_client
        mock_pool_manager.get_client.assert_called_once_with("default")

    @pytest.mark.asyncio
    async def test_aexit_clears_client_reference(self, mocker):
        """Test async context manager exit clears client reference."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        client = NetworkResilientClient()
        client._client = mocker.AsyncMock()  # Set a mock client

        await client.__aexit__(None, None, None)

        assert client._client is None

    @pytest.mark.asyncio
    async def test_get_with_retry_no_client_raises_error(self, mocker):
        """Test get_with_retry raises NetworkError when client is None."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        client = NetworkResilientClient()
        # Don't set _client

        with pytest.raises(NetworkError, match="HTTP client not initialized"):
            await client.get_with_retry("https://example.com")

    @pytest.mark.asyncio
    async def test_get_with_retry_circuit_breaker_open(self, mocker):
        """Test get_with_retry raises error when circuit breaker is open."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        client = NetworkResilientClient()
        client._client = mocker.AsyncMock()

        # Mock circuit breaker to be open
        client._circuit_breaker.is_open = mocker.Mock(return_value=True)

        with pytest.raises(
            NetworkError, match="Circuit breaker is open - too many failures"
        ):
            await client.get_with_retry("https://example.com")

    @pytest.mark.asyncio
    async def test_get_with_retry_success_resets_circuit_breaker(self, mocker):
        """Test successful request resets circuit breaker."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()

        client = NetworkResilientClient()
        client._client = mocker.AsyncMock()
        client._client.get = mocker.AsyncMock(return_value=mock_response)

        # Mock rate limiter acquire
        client._rate_limiter.acquire = mocker.AsyncMock()

        # Spy on circuit breaker methods
        cb_success_spy = mocker.spy(client._circuit_breaker, "record_success")

        result = await client.get_with_retry("https://example.com")

        assert result is mock_response
        cb_success_spy.assert_called_once()
        client._rate_limiter.acquire.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_with_retry_404_status_code_raises_package_not_found(
        self, mocker
    ):
        """Test 404 status code raises PackageNotFoundError."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_response = mocker.Mock()
        mock_response.status_code = 404

        client = NetworkResilientClient()
        client._client = mocker.AsyncMock()
        client._client.get = mocker.AsyncMock(return_value=mock_response)
        client._rate_limiter.acquire = mocker.AsyncMock()

        with pytest.raises(
            PackageNotFoundError, match="Resource not found: https://example.com"
        ):
            await client.get_with_retry("https://example.com")

    @pytest.mark.asyncio
    async def test_get_with_retry_timeout_retries_with_backoff(self, mocker):
        """Test timeout errors retry with exponential backoff."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)
        mock_timeout_error = httpx.TimeoutException("Request timeout")

        client = NetworkResilientClient()
        client._client = mocker.AsyncMock()
        client._client.get = mocker.AsyncMock(side_effect=mock_timeout_error)
        client._rate_limiter.acquire = mocker.AsyncMock()

        # Spy on circuit breaker failure recording
        cb_failure_spy = mocker.spy(client._circuit_breaker, "record_failure")

        with pytest.raises(NetworkError, match="Request timeout after 3 attempts"):
            await client.get_with_retry("https://example.com")

        # Should have tried 3 times
        assert client._client.get.call_count == 3
        # Should have slept twice (between attempts)
        assert mock_sleep.call_count == 2
        # Should have recorded failures
        assert cb_failure_spy.call_count == 3

    @pytest.mark.asyncio
    async def test_get_with_retry_http_404_error_raises_package_not_found(self, mocker):
        """Test HTTPStatusError 404 raises PackageNotFoundError."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_response = mocker.Mock()
        mock_response.status_code = 404

        mock_http_error = httpx.HTTPStatusError(
            message="Not Found", request=mocker.Mock(), response=mock_response
        )

        client = NetworkResilientClient()
        client._client = mocker.AsyncMock()
        client._client.get = mocker.AsyncMock(side_effect=mock_http_error)
        client._rate_limiter.acquire = mocker.AsyncMock()

        with pytest.raises(
            PackageNotFoundError, match="Resource not found: https://example.com"
        ):
            await client.get_with_retry("https://example.com")

    @pytest.mark.asyncio
    async def test_get_with_retry_4xx_no_retry_except_408_429(self, mocker):
        """Test 4xx errors don't retry except 408 and 429."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_response = mocker.Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_response.headers = {}

        mock_http_error = httpx.HTTPStatusError(
            message="Forbidden", request=mocker.Mock(), response=mock_response
        )

        client = NetworkResilientClient()
        client._client = mocker.AsyncMock()
        client._client.get = mocker.AsyncMock(side_effect=mock_http_error)
        client._rate_limiter.acquire = mocker.AsyncMock()

        with pytest.raises(NetworkError, match="HTTP 403: Forbidden"):
            await client.get_with_retry("https://example.com")

        # Should only attempt once (no retry for 403)
        assert client._client.get.call_count == 1

    @pytest.mark.asyncio
    async def test_get_with_retry_429_retries(self, mocker):
        """Test 429 Rate Limit errors retry."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        mock_response = mocker.Mock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        mock_response.headers = {}

        mock_http_error = httpx.HTTPStatusError(
            message="Too Many Requests", request=mocker.Mock(), response=mock_response
        )

        client = NetworkResilientClient()
        client._client = mocker.AsyncMock()
        client._client.get = mocker.AsyncMock(side_effect=mock_http_error)
        client._rate_limiter.acquire = mocker.AsyncMock()

        with pytest.raises(NetworkError, match="HTTP error after 3 attempts"):
            await client.get_with_retry("https://example.com")

        # Should retry 3 times
        assert client._client.get.call_count == 3
        assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_get_with_retry_request_error_retries(self, mocker):
        """Test RequestError retries with backoff."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)
        mock_request_error = httpx.RequestError("Connection failed")

        client = NetworkResilientClient()
        client._client = mocker.AsyncMock()
        client._client.get = mocker.AsyncMock(side_effect=mock_request_error)
        client._rate_limiter.acquire = mocker.AsyncMock()

        with pytest.raises(
            NetworkError, match="Network error after 3 attempts: Connection failed"
        ):
            await client.get_with_retry("https://example.com")

        # Should retry 3 times
        assert client._client.get.call_count == 3
        assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_wait_for_retry_exponential_backoff(self, mocker):
        """Test _wait_for_retry implements exponential backoff correctly."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 2.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        client = NetworkResilientClient()
        client.retry_config.jitter = False  # Disable jitter for predictable testing

        # Test different attempts
        await client._wait_for_retry(1)  # 2^(1-1) = 1 * 2.0 = 2.0
        await client._wait_for_retry(2)  # 2^(2-1) = 2 * 2.0 = 4.0
        await client._wait_for_retry(3)  # 2^(3-1) = 4 * 2.0 = 8.0

        expected_delays = [2.0, 4.0, 8.0]
        actual_delays = [call[0][0] for call in mock_sleep.call_args_list]

        assert actual_delays == expected_delays

    @pytest.mark.asyncio
    async def test_wait_for_retry_max_delay_limit(self, mocker):
        """Test _wait_for_retry respects max_delay limit."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 10.0
        mock_config.max_retry_delay = 20.0  # Low max delay
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        client = NetworkResilientClient()
        client.retry_config.jitter = False

        # This would normally be 10 * 2^(5-1) = 160, but should be capped at 20
        await client._wait_for_retry(5)

        mock_sleep.assert_called_once_with(20.0)

    @pytest.mark.asyncio
    async def test_wait_for_retry_with_jitter(self, mocker):
        """Test _wait_for_retry applies jitter correctly."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 2.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)
        # Mock random to return predictable value
        mocker.patch("random.random", return_value=0.5)

        client = NetworkResilientClient()
        client.retry_config.jitter = True

        await client._wait_for_retry(
            1
        )  # base_delay = 2.0, jitter should make it 2.0 * (0.5 + 0.5 * 0.5) = 1.5

        expected_delay = 2.0 * (0.5 + 0.5 * 0.5)  # 1.5
        mock_sleep.assert_called_once_with(expected_delay)

    def test_get_error_text_json_response(self, mocker):
        """Test _get_error_text extracts JSON error message."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_response = mocker.Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"message": "Custom error message"}

        client = NetworkResilientClient()

        result = client._get_error_text(mock_response)

        assert result == "Custom error message"

    def test_get_error_text_fallback_to_text(self, mocker):
        """Test _get_error_text falls back to response text."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_response = mocker.Mock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = "HTML error page content"

        client = NetworkResilientClient()

        result = client._get_error_text(mock_response)

        assert result == "HTML error page content"

    def test_get_error_text_truncates_long_text(self, mocker):
        """Test _get_error_text truncates long response text."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        long_text = "x" * 300  # 300 character text
        mock_response = mocker.Mock()
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = long_text

        client = NetworkResilientClient()

        result = client._get_error_text(mock_response)

        assert len(result) == 200
        assert result == "x" * 200

    def test_get_error_text_exception_fallback(self, mocker):
        """Test _get_error_text handles exceptions gracefully."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )
        mocker.patch("src.autodoc_mcp.core.network_resilience.ConnectionPoolManager")

        mock_response = mocker.Mock()
        mock_response.status_code = 500
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.side_effect = Exception("JSON parsing failed")
        mock_response.text = None

        client = NetworkResilientClient()

        result = client._get_error_text(mock_response)

        assert result == "Status 500"


class TestNetworkResilientClientFullIntegration:
    """Test full integration scenarios with NetworkResilientClient."""

    @pytest.mark.asyncio
    async def test_full_context_manager_success_workflow(self, mocker):
        """Test complete workflow with context manager and successful request."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 3
        mock_config.base_retry_delay = 1.0
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 5
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = 60

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(return_value=mock_response)

        mock_pool_manager = mocker.Mock()
        mock_pool_manager.get_client = mocker.AsyncMock(return_value=mock_client)

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.ConnectionPoolManager",
            return_value=mock_pool_manager,
        )

        async with NetworkResilientClient() as client:
            result = await client.get_with_retry("https://example.com", param="value")

        assert result is mock_response
        mock_client.get.assert_called_once_with("https://example.com", param="value")
        mock_response.raise_for_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_with_mixed_failures_then_success(self, mocker):
        """Test retry logic with mixed failure types followed by success."""
        mock_config = mocker.Mock()
        mock_config.max_retry_attempts = 4
        mock_config.base_retry_delay = 0.1  # Fast for testing
        mock_config.max_retry_delay = 60.0
        mock_config.circuit_breaker_threshold = 10  # High threshold to avoid opening
        mock_config.circuit_breaker_timeout = 60.0
        mock_config.rate_limit_requests_per_minute = (
            1000  # High limit to avoid rate limiting
        )

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.get_config",
            return_value=mock_config,
        )

        # Mock different types of failures followed by success
        mock_timeout = httpx.TimeoutException("Timeout")

        mock_429_response = mocker.Mock()
        mock_429_response.status_code = 429
        mock_429_response.text = "Rate limited"
        mock_429_response.headers = {}
        mock_429_error = httpx.HTTPStatusError(
            "Rate limited", request=mocker.Mock(), response=mock_429_response
        )

        mock_request_error = httpx.RequestError("Connection failed")

        mock_success_response = mocker.Mock()
        mock_success_response.status_code = 200
        mock_success_response.raise_for_status = mocker.Mock()

        mock_client = mocker.AsyncMock()
        mock_client.get = mocker.AsyncMock(
            side_effect=[
                mock_timeout,
                mock_429_error,
                mock_request_error,
                mock_success_response,
            ]
        )

        mock_pool_manager = mocker.Mock()
        mock_pool_manager.get_client = mocker.AsyncMock(return_value=mock_client)

        mocker.patch(
            "src.autodoc_mcp.core.network_resilience.ConnectionPoolManager",
            return_value=mock_pool_manager,
        )
        mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        async with NetworkResilientClient() as client:
            result = await client.get_with_retry("https://example.com")

        assert result is mock_success_response
        assert mock_client.get.call_count == 4  # 3 failures + 1 success
        mock_success_response.raise_for_status.assert_called_once()
