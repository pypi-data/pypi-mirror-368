"""Documentation fetching from PyPI API."""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from structlog import get_logger

from ..config import get_config
from ..exceptions import NetworkError, PackageNotFoundError
from ..models import PackageInfo
from .error_formatter import ErrorFormatter, FormattedError
from .network_resilience import NetworkResilientClient

logger = get_logger(__name__)


@dataclass
class DocFetchResult:
    """Result of documentation fetching with error tracking."""

    package_info: PackageInfo | None
    success: bool
    errors: list[FormattedError]
    warnings: list[str]
    from_cache: bool = False
    fetch_time: float = 0.0


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
    """Enhanced fetcher with graceful degradation and error collection."""

    def __init__(self, semaphore: asyncio.Semaphore | None = None):
        self.config = get_config()
        self.semaphore = semaphore or asyncio.Semaphore(self.config.max_concurrent)
        self._resilient_client: NetworkResilientClient | None = None
        self._error_formatter = ErrorFormatter()

    async def __aenter__(self) -> "PyPIDocumentationFetcher":
        self._resilient_client = NetworkResilientClient()
        await self._resilient_client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._resilient_client:
            await self._resilient_client.__aexit__(exc_type, exc_val, exc_tb)

    async def fetch_package_info_safe(self, package_name: str) -> DocFetchResult:
        """Fetch package info with comprehensive error handling."""
        start_time = time.time()
        errors: list[FormattedError] = []
        warnings: list[str] = []
        package_info = None

        async with self.semaphore:
            try:
                logger.debug("Fetching package documentation", package=package_name)

                if self._resilient_client is None:
                    raise RuntimeError(
                        "Client not initialized. Use 'async with' context manager."
                    )

                response = await self._resilient_client.get_with_retry(
                    f"{self.config.pypi_base_url}/{package_name}/json",
                    headers={"Accept": "application/json"},
                )

                data = response.json()
                package_info = self._parse_pypi_response(data, package_name)

                logger.info(
                    "Successfully fetched package info",
                    package=package_name,
                    version=package_info.version,
                )

            except PackageNotFoundError as e:
                formatted_error = self._error_formatter.format_exception(
                    e, {"package": package_name}
                )
                errors.append(formatted_error)
                logger.warning("Package not found", package=package_name)

            except NetworkError as e:
                formatted_error = self._error_formatter.format_exception(
                    e, {"package": package_name}
                )
                errors.append(formatted_error)
                logger.error(
                    "Network error fetching package", package=package_name, error=str(e)
                )

            except Exception as e:
                formatted_error = self._error_formatter.format_exception(
                    e, {"package": package_name, "operation": "documentation_fetch"}
                )
                errors.append(formatted_error)
                logger.error(
                    "Unexpected error fetching package",
                    package=package_name,
                    error=str(e),
                )

        fetch_time = time.time() - start_time

        return DocFetchResult(
            package_info=package_info,
            success=package_info is not None,
            errors=errors,
            warnings=warnings,
            fetch_time=fetch_time,
        )

    async def fetch_multiple_packages_safe(
        self, package_names: list[str]
    ) -> dict[str, DocFetchResult]:
        """Fetch multiple packages with individual error handling."""
        logger.info("Fetching multiple packages", count=len(package_names))

        # Create tasks for concurrent fetching
        tasks = [
            self.fetch_package_info_safe(package_name) for package_name in package_names
        ]

        # Wait for all tasks, collecting results regardless of individual failures
        results = await asyncio.gather(*tasks, return_exceptions=False)

        # Create result mapping
        fetch_results = {}
        for package_name, result in zip(package_names, results, strict=False):
            fetch_results[package_name] = result

        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        logger.info(
            "Completed batch documentation fetch",
            total=len(package_names),
            successful=successful,
            failed=failed,
        )

        return fetch_results

    async def fetch_package_info(self, package_name: str) -> PackageInfo:
        """Fetch package information from PyPI JSON API with network resilience."""
        async with self.semaphore:
            url = f"{self.config.pypi_base_url}/{package_name}/json"

            logger.info("Fetching package info", package=package_name, url=url)

            if self._resilient_client is None:
                raise RuntimeError(
                    "Client not initialized. Use 'async with' context manager."
                )

            try:
                response = await self._resilient_client.get_with_retry(
                    url, headers={"Accept": "application/json"}
                )
                data = response.json()

                return self._parse_pypi_response(data, package_name)

            except PackageNotFoundError:
                logger.error("Package not found on PyPI", package=package_name)
                raise
            except NetworkError as e:
                logger.error(
                    "Network error fetching package", package=package_name, error=str(e)
                )
                raise

    def format_documentation(
        self, package_info: PackageInfo, query: str | None = None
    ) -> str:
        """Format package info for AI consumption with optional query filtering."""
        config = get_config()
        sections = []

        # Basic info
        sections.append(f"# {package_info.name} v{package_info.version}")

        if package_info.summary:
            sections.append(f"**Summary**: {package_info.summary}")

        if package_info.author:
            sections.append(f"**Author**: {package_info.author}")

        # Description with intelligent truncation
        if package_info.description:
            desc = package_info.description
            max_desc_size = min(
                config.max_documentation_size // 2, 10000
            )  # Reserve space for other content
            if len(desc) > max_desc_size:
                desc = desc[:max_desc_size] + "\n\n... (truncated for performance)"
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

        # Final size check and truncation
        if len(formatted) > config.max_documentation_size:
            truncated = formatted[: config.max_documentation_size]
            # Try to truncate at a section boundary
            last_section = truncated.rfind("\n\n##")
            if last_section > config.max_documentation_size // 2:
                truncated = truncated[:last_section]
            formatted = truncated + "\n\n... (truncated for performance)"

        return formatted

    def _parse_pypi_response(
        self, data: dict[str, Any], package_name: str
    ) -> PackageInfo:
        """Parse PyPI response with validation."""
        try:
            info = data["info"]

            # Validate required fields
            if not info.get("name"):
                raise ValueError("Missing package name in PyPI response")
            if not info.get("version"):
                raise ValueError("Missing version in PyPI response")

            return PackageInfo(
                name=info["name"],
                version=info["version"],
                summary=info.get("summary") or "",
                description=info.get("description") or "",
                author=info.get("author"),
                license=info.get("license"),
                home_page=info.get("home_page"),
                project_urls=info.get("project_urls") or {},
                classifiers=info.get("classifiers") or [],
                keywords=info.get("keywords", "").split()
                if info.get("keywords")
                else [],
            )

        except KeyError as e:
            raise ValueError(f"Malformed PyPI response: missing key {e}") from e

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
