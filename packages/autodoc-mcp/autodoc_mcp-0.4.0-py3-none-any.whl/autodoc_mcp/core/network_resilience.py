"""Network resilience implementation with retry patterns and circuit breakers."""

import asyncio
import random
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, TypeVar

import httpx
from structlog import get_logger

from ..config import get_config
from ..exceptions import NetworkError, PackageNotFoundError

logger = get_logger(__name__)
T = TypeVar("T")


class ConnectionPoolManager:
    """Singleton connection pool manager for HTTP clients."""

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls) -> "ConnectionPoolManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "initialized"):
            self._clients: dict[str, httpx.AsyncClient] = {}
            self._lock = asyncio.Lock()
            self.initialized = True

    async def get_client(self, config_key: str = "default") -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling."""
        async with self._lock:
            if config_key not in self._clients:
                config = get_config()
                self._clients[config_key] = httpx.AsyncClient(
                    timeout=httpx.Timeout(config.request_timeout),
                    follow_redirects=True,
                    headers={"User-Agent": "AutoDocs-MCP/1.0"},
                    limits=httpx.Limits(
                        max_connections=100,
                        max_keepalive_connections=20,
                        keepalive_expiry=30.0,
                    ),
                )
                logger.debug("Created new HTTP client", config_key=config_key)
            return self._clients[config_key]

    async def close_all(self) -> None:
        """Close all HTTP clients."""
        async with self._lock:
            for config_key, client in self._clients.items():
                await client.aclose()
                logger.debug("Closed HTTP client", config_key=config_key)
            self._clients.clear()


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


class CircuitBreaker:
    """Simple circuit breaker to prevent cascade failures."""

    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._state = "closed"  # closed, open, half_open

    def is_open(self) -> bool:
        """Check if circuit breaker is open (blocking requests)."""
        if self._state == "open":
            if time.time() - self._last_failure_time > self.reset_timeout:
                self._state = "half_open"
                return False
            return True
        return False

    def record_success(self) -> None:
        """Record a successful operation."""
        self._failure_count = 0
        self._state = "closed"

    def record_failure(self) -> None:
        """Record a failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self.failure_threshold:
            self._state = "open"
            logger.warning("Circuit breaker opened", failure_count=self._failure_count)


class RateLimiter:
    """Simple rate limiter with sliding window and memory bounds."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: deque[float] = deque()
        self._max_entries = max(requests_per_minute * 2, 1000)  # Safety limit
        self._last_cleanup = time.time()

    async def acquire(self) -> None:
        """Wait if necessary to respect rate limits."""
        now = time.time()

        # Force cleanup every 60 seconds to prevent memory leaks
        if now - self._last_cleanup > 60:
            await self._force_cleanup(now)
            self._last_cleanup = now

        # Remove requests older than 1 minute
        await self._cleanup_old_requests(now)

        # Emergency cleanup if deque grows too large
        if len(self.requests) > self._max_entries:
            logger.warning(
                "Rate limiter deque exceeded max size, forcing cleanup",
                current_size=len(self.requests),
                max_size=self._max_entries,
            )
            await self._force_cleanup(now)

        # If we're at the limit, wait until we can make another request
        if len(self.requests) >= self.requests_per_minute and self.requests:
            sleep_time = 60 - (now - self.requests[0]) + 0.1  # Small buffer
            if sleep_time > 0:
                logger.debug("Rate limiting: sleeping", sleep_time=sleep_time)
                await asyncio.sleep(sleep_time)

        # Record this request
        self.requests.append(now)

    async def _cleanup_old_requests(self, now: float) -> None:
        """Remove requests older than 1 minute."""
        cutoff = now - 60
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()

    async def _force_cleanup(self, now: float) -> None:
        """Force cleanup of old entries to prevent memory leaks."""
        cutoff = now - 60
        # Keep only recent requests
        self.requests = deque(t for t in self.requests if t >= cutoff)

        # If still too large, keep only the most recent entries
        if len(self.requests) > self.requests_per_minute:
            self.requests = deque(sorted(self.requests)[-self.requests_per_minute :])


class NetworkResilientClient:
    """HTTP client with built-in retry logic, circuit breaker, and rate limiting."""

    def __init__(self, retry_config: RetryConfig | None = None):
        config = get_config()
        self.retry_config = retry_config or RetryConfig(
            max_attempts=config.max_retry_attempts,
            base_delay=config.base_retry_delay,
            max_delay=config.max_retry_delay,
        )
        self._client: httpx.AsyncClient | None = None
        self._pool_manager = ConnectionPoolManager()
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold,
            reset_timeout=config.circuit_breaker_timeout,
        )
        self._rate_limiter = RateLimiter(config.rate_limit_requests_per_minute)

    async def __aenter__(self) -> "NetworkResilientClient":
        """Enter async context manager."""
        # Get shared client from pool instead of creating new one
        self._client = await self._pool_manager.get_client("default")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        # Don't close the client - it's managed by the pool
        self._client = None

    async def get_with_retry(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make GET request with retry logic and circuit breaker."""

        for attempt in range(1, self.retry_config.max_attempts + 1):
            try:
                # Check circuit breaker
                if self._circuit_breaker.is_open():
                    raise NetworkError("Circuit breaker is open - too many failures")

                # Apply rate limiting
                await self._rate_limiter.acquire()

                logger.debug("Making HTTP request", url=url, attempt=attempt)
                if self._client is None:
                    raise NetworkError("HTTP client not initialized")
                response = await self._client.get(url, **kwargs)

                # Success - reset circuit breaker
                self._circuit_breaker.record_success()

                # Handle 404 specifically
                if response.status_code == 404:
                    raise PackageNotFoundError(f"Resource not found: {url}")

                # Raise for other HTTP errors
                response.raise_for_status()
                return response

            except httpx.TimeoutException as e:
                self._circuit_breaker.record_failure()
                logger.warning("Request timeout", url=url, attempt=attempt)

                if attempt == self.retry_config.max_attempts:
                    raise NetworkError(
                        f"Request timeout after {attempt} attempts"
                    ) from e

                await self._wait_for_retry(attempt)

            except httpx.HTTPStatusError as e:
                self._circuit_breaker.record_failure()

                # Don't retry 4xx errors except 429 (rate limit) and 408 (timeout)
                if (
                    400 <= e.response.status_code < 500
                    and e.response.status_code not in [408, 429]
                ):
                    if e.response.status_code == 404:
                        raise PackageNotFoundError(f"Resource not found: {url}") from e
                    else:
                        raise NetworkError(
                            f"HTTP {e.response.status_code}: {self._get_error_text(e.response)}"
                        ) from e

                logger.warning(
                    "HTTP error",
                    url=url,
                    status=e.response.status_code,
                    attempt=attempt,
                )

                if attempt == self.retry_config.max_attempts:
                    raise NetworkError(f"HTTP error after {attempt} attempts") from e

                await self._wait_for_retry(attempt)

            except httpx.RequestError as e:
                self._circuit_breaker.record_failure()
                logger.warning("Network error", url=url, error=str(e), attempt=attempt)

                if attempt == self.retry_config.max_attempts:
                    raise NetworkError(
                        f"Network error after {attempt} attempts: {e}"
                    ) from e

                await self._wait_for_retry(attempt)

        # Should never reach here
        raise NetworkError("Retry logic failed unexpectedly")

    def _get_error_text(self, response: httpx.Response) -> str:
        """Extract error message from HTTP response."""
        try:
            # Try to get JSON error if available
            if "application/json" in response.headers.get("content-type", ""):
                data = response.json()
                if isinstance(data, dict) and "message" in data:
                    return str(data["message"])

            # Fallback to response text
            return response.text[:200] if response.text else "Unknown error"
        except Exception:
            return f"Status {response.status_code}"

    async def _wait_for_retry(self, attempt: int) -> None:
        """Calculate and wait for retry delay with exponential backoff."""
        delay = min(
            self.retry_config.base_delay
            * (self.retry_config.exponential_base ** (attempt - 1)),
            self.retry_config.max_delay,
        )

        if self.retry_config.jitter:
            # Add ±50% jitter to prevent thundering herd
            delay *= 0.5 + random.random() * 0.5

        logger.debug("Waiting before retry", delay=delay, attempt=attempt)
        await asyncio.sleep(delay)
