"""Documentation fetching from PyPI API."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any

import httpx
from structlog import get_logger

from ..config import get_config
from ..exceptions import NetworkError, PackageNotFoundError
from ..models import PackageInfo

logger = get_logger(__name__)


class DocumentationFetcherInterface(ABC):
    """Interface for documentation fetching."""

    @abstractmethod
    async def fetch_package_info(self, package_name: str) -> PackageInfo:
        """Fetch package information from external source."""

    @abstractmethod
    def format_documentation(
        self, package_info: PackageInfo, query: str | None = None
    ) -> str:
        """Format package info for AI consumption."""


class PyPIDocumentationFetcher(DocumentationFetcherInterface):
    """Fetches documentation from PyPI JSON API."""

    def __init__(self, semaphore: asyncio.Semaphore | None = None):
        self.config = get_config()
        self.semaphore = semaphore or asyncio.Semaphore(self.config.max_concurrent)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "PyPIDocumentationFetcher":
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.request_timeout), follow_redirects=True
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def fetch_package_info(self, package_name: str) -> PackageInfo:
        """Fetch package information from PyPI JSON API."""
        async with self.semaphore:
            url = f"{self.config.pypi_base_url}/{package_name}/json"

            logger.info("Fetching package info", package=package_name, url=url)

            if self._client is None:
                raise RuntimeError(
                    "Client not initialized. Use 'async with' context manager."
                )

            try:
                response = await self._client.get(url)
                response.raise_for_status()
                data = response.json()

                return self._parse_pypi_response(data)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise PackageNotFoundError(
                        f"Package '{package_name}' not found on PyPI"
                    ) from e
                raise NetworkError(f"PyPI API error: {e.response.status_code}") from e

            except httpx.RequestError as e:
                raise NetworkError(f"Network error fetching {package_name}: {e}") from e

    def format_documentation(
        self, package_info: PackageInfo, query: str | None = None
    ) -> str:
        """Format package info for AI consumption with optional query filtering."""
        sections = []

        # Basic info
        sections.append(f"# {package_info.name} v{package_info.version}")

        if package_info.summary:
            sections.append(f"**Summary**: {package_info.summary}")

        if package_info.author:
            sections.append(f"**Author**: {package_info.author}")

        # Description (truncated if too long)
        if package_info.description:
            desc = package_info.description
            if len(desc) > 2000:  # Truncate very long descriptions
                desc = desc[:2000] + "..."
            sections.append(f"## Description\n{desc}")

        # Project URLs
        if package_info.project_urls:
            sections.append("## Links")
            for label, url in package_info.project_urls.items():
                sections.append(f"- **{label}**: {url}")

        if package_info.home_page:
            sections.append(f"- **Homepage**: {package_info.home_page}")

        # Keywords (if relevant to query)
        if package_info.keywords and (
            not query or any(kw in query.lower() for kw in package_info.keywords)
        ):
            sections.append(f"**Keywords**: {', '.join(package_info.keywords)}")

        formatted = "\n\n".join(sections)

        # Apply query filtering if provided
        if query:
            formatted = self._apply_query_filter(formatted, query)

        return formatted

    def _parse_pypi_response(self, data: dict[str, Any]) -> PackageInfo:
        """Parse PyPI JSON response into PackageInfo model."""
        info = data.get("info", {})

        return PackageInfo(
            name=info.get("name", ""),
            version=info.get("version", ""),
            summary=info.get("summary"),
            description=info.get("description"),
            home_page=info.get("home_page"),
            project_urls=info.get("project_urls", {}),
            author=info.get("author"),
            license=info.get("license"),
            keywords=info.get("keywords", "").split() if info.get("keywords") else [],
            classifiers=info.get("classifiers", []),
        )

    def _apply_query_filter(self, content: str, query: str) -> str:
        """Apply simple query-based filtering to content."""
        query_terms = query.lower().split()

        # Split content into sections and score by relevance
        sections = content.split("\n\n")
        relevant_sections = []

        for section in sections:
            section_lower = section.lower()
            score = sum(1 for term in query_terms if term in section_lower)

            if score > 0:
                relevant_sections.append((score, section))

        # Sort by relevance and return top sections
        relevant_sections.sort(key=lambda x: x[0], reverse=True)

        return "\n\n".join([section for _, section in relevant_sections[:5]])
