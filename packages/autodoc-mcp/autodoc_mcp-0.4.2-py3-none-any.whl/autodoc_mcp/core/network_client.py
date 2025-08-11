"""Basic network client for Phase 4 implementation."""

import asyncio
from typing import Any

import httpx
from structlog import get_logger

from ..exceptions import NetworkError, PackageNotFoundError

logger = get_logger(__name__)


class BasicNetworkClient:
    """Simple HTTP client for Phase 4 dependency resolution."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "BasicNetworkClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
            headers={"User-Agent": "AutoDocs-MCP/1.0"},
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    async def get_with_retry(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make GET request with basic retry logic."""

        if self._client is None:
            raise NetworkError("HTTP client not initialized")

        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                logger.debug("Making HTTP request", url=url, attempt=attempt)
                response = await self._client.get(url, **kwargs)

                # Handle 404 specifically
                if response.status_code == 404:
                    raise PackageNotFoundError(f"Resource not found: {url}")

                # Raise for other HTTP errors
                response.raise_for_status()
                return response

            except httpx.TimeoutException as e:
                logger.warning("Request timeout", url=url, attempt=attempt)

                if attempt == max_attempts:
                    raise NetworkError(
                        f"Request timeout after {attempt} attempts"
                    ) from e

                await asyncio.sleep(2 ** (attempt - 1))  # Simple backoff

            except httpx.HTTPStatusError as e:
                # Don't retry 4xx errors except 429 (rate limit) and 408 (timeout)
                if (
                    400 <= e.response.status_code < 500
                    and e.response.status_code not in [408, 429]
                ):
                    if e.response.status_code == 404:
                        raise PackageNotFoundError(f"Resource not found: {url}") from e
                    else:
                        raise NetworkError(
                            f"HTTP {e.response.status_code}: {e.response.text[:200]}"
                        ) from e

                logger.warning(
                    "HTTP error",
                    url=url,
                    status=e.response.status_code,
                    attempt=attempt,
                )

                if attempt == max_attempts:
                    raise NetworkError(f"HTTP error after {attempt} attempts") from e

                await asyncio.sleep(2 ** (attempt - 1))

            except httpx.RequestError as e:
                logger.warning("Network error", url=url, error=str(e), attempt=attempt)

                if attempt == max_attempts:
                    raise NetworkError(
                        f"Network error after {attempt} attempts: {e}"
                    ) from e

                await asyncio.sleep(2 ** (attempt - 1))

        # Should never reach here
        raise NetworkError("Retry logic failed unexpectedly")


# Alias for compatibility
NetworkResilientClient = BasicNetworkClient
