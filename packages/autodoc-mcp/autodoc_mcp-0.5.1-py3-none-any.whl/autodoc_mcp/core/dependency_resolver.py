"""Dependency intelligence engine for context resolution."""

from dataclasses import dataclass, field

from packaging.requirements import Requirement
from structlog import get_logger

from ..config import get_config
from ..exceptions import AutoDocsError, NetworkError
from .network_client import NetworkResilientClient

logger = get_logger(__name__)


@dataclass
class DependencySpec:
    """Specification for a single dependency."""

    name: str
    version_constraint: str = ""
    extras: list[str] = field(default_factory=list)
    is_optional: bool = False
    environment_markers: str = ""

    @classmethod
    def from_requirement(cls, req: Requirement) -> "DependencySpec":
        """Create from packaging.requirements.Requirement."""
        return cls(
            name=req.name,
            version_constraint=str(req.specifier) if req.specifier else "",
            extras=list(req.extras) if req.extras else [],
            is_optional=False,  # Will be set by caller based on context
            environment_markers=str(req.marker) if req.marker else "",
        )


@dataclass
class PackageMetadata:
    """Metadata about a package from PyPI."""

    name: str
    version: str
    summary: str
    description: str
    runtime_requires: list[DependencySpec] = field(default_factory=list)
    dev_requires: list[DependencySpec] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    classifiers: list[str] = field(default_factory=list)
    download_count: int = 0  # For popularity scoring


# Pre-defined package categories for relevance scoring
CORE_FRAMEWORKS = {
    "pydantic",
    "fastapi",
    "django",
    "flask",
    "requests",
    "httpx",
    "sqlalchemy",
    "pandas",
    "numpy",
    "click",
    "typer",
    "pytest",
}

COMMON_UTILITIES = {
    "rich",
    "typer",
    "click",
    "jinja2",
    "pyyaml",
    "python-dotenv",
    "structlog",
    "loguru",
    "pytest",
    "black",
    "ruff",
    "mypy",
}

LOW_PRIORITY_DEPS = {
    "setuptools",
    "wheel",
    "pip",
    "build",
    "hatchling",
    "setuptools-scm",
    "tomli",
    "typing-extensions",
    "importlib-metadata",
    "packaging",
}

WELL_DOCUMENTED = {
    "requests",
    "pydantic",
    "fastapi",
    "click",
    "typer",
    "rich",
    "pandas",
    "numpy",
    "sqlalchemy",
    "jinja2",
    "pytest",
    "httpx",
}

# Package-specific relationship boosts
PACKAGE_RELATIONSHIP_BOOSTS = {
    "fastapi": {"pydantic": 8.0, "starlette": 8.0, "uvicorn": 6.0},
    "django": {"django-rest-framework": 7.0, "psycopg2": 6.0, "psycopg2-binary": 6.0},
    "flask": {"jinja2": 7.0, "werkzeug": 7.0, "flask-sqlalchemy": 6.0},
    "requests": {"urllib3": 8.0, "certifi": 6.0, "chardet": 5.0},
    "httpx": {"httpcore": 8.0, "certifi": 6.0, "h11": 6.0},
    "sqlalchemy": {"psycopg2": 7.0, "psycopg2-binary": 7.0, "pymysql": 6.0},
    "pytest": {"pytest-asyncio": 6.0, "pytest-cov": 6.0, "pytest-mock": 6.0},
}


class DependencyResolver:
    """Intelligent dependency resolver for documentation context."""

    def __init__(self, network_client: NetworkResilientClient | None = None):
        self.config = get_config()
        self.network_client = network_client
        self._metadata_cache: dict[str, PackageMetadata] = {}

    async def resolve_context_dependencies(
        self,
        package_name: str,
        version: str,
        max_dependencies: int = 8,
        max_tokens: int = 30000,
    ) -> list[str]:
        """
        Resolve which dependencies to include in documentation context.

        Args:
            package_name: Primary package name
            version: Specific version of primary package
            max_dependencies: Maximum number of dependencies to include
            max_tokens: Token budget for dependency context

        Returns:
            List of dependency package names to fetch, ordered by relevance
        """
        try:
            logger.info(
                "Resolving context dependencies",
                package=package_name,
                version=version,
                max_deps=max_dependencies,
            )

            # Get dependency metadata from PyPI
            metadata = await self._get_package_metadata(package_name, version)

            if not metadata.runtime_requires:
                logger.info("No runtime dependencies found", package=package_name)
                return []

            # Score all dependencies by relevance
            scored_deps = []
            for dep in metadata.runtime_requires:
                # Skip optional dependencies and environment-specific ones
                if dep.is_optional or "extra ==" in dep.environment_markers.lower():
                    continue

                score = self._calculate_dependency_relevance(dep, package_name)
                if score > 0:  # Only include positively scored dependencies
                    scored_deps.append((score, dep))

            # Sort by relevance score (highest first)
            scored_deps.sort(key=lambda x: x[0], reverse=True)

            # Apply limits with token estimation
            selected_deps: list[str] = []
            estimated_tokens = 0

            for score, dep in scored_deps:
                if len(selected_deps) >= max_dependencies:
                    break

                # Rough token estimate for this dependency (conservative)
                dep_tokens = await self._estimate_dependency_tokens(dep.name)
                if estimated_tokens + dep_tokens > max_tokens:
                    logger.debug(
                        "Skipping dependency due to token limit",
                        dep=dep.name,
                        tokens=dep_tokens,
                        current_total=estimated_tokens,
                    )
                    break

                selected_deps.append(dep.name)
                estimated_tokens += dep_tokens

                logger.debug(
                    "Selected dependency", dep=dep.name, score=score, tokens=dep_tokens
                )

            logger.info(
                "Dependency resolution complete",
                selected=len(selected_deps),
                estimated_tokens=estimated_tokens,
                dependencies=selected_deps,
            )

            return selected_deps

        except Exception as e:
            logger.warning(
                "Dependency resolution failed", package=package_name, error=str(e)
            )
            return []  # Graceful degradation - return empty list

    async def _get_package_metadata(
        self, package_name: str, version: str
    ) -> PackageMetadata:
        """Fetch package metadata from PyPI API."""
        cache_key = f"{package_name}-{version}"

        if cache_key in self._metadata_cache:
            return self._metadata_cache[cache_key]

        if not self.network_client:
            raise AutoDocsError("Network client not initialized")

        url = f"https://pypi.org/pypi/{package_name}/{version}/json"

        try:
            response = await self.network_client.get_with_retry(url)
            data = response.json()

            # Parse package info
            info = data.get("info", {})

            # Parse dependencies from requires_dist
            runtime_requires = []
            requires_dist = info.get("requires_dist") or []

            for req_str in requires_dist:
                try:
                    req = Requirement(req_str)
                    dep_spec = DependencySpec.from_requirement(req)

                    # Classify as optional if it has extra requirements
                    if "extra ==" in dep_spec.environment_markers.lower():
                        dep_spec.is_optional = True

                    runtime_requires.append(dep_spec)

                except Exception as e:
                    logger.debug(
                        "Failed to parse requirement", requirement=req_str, error=str(e)
                    )
                    continue

            # Extract keywords and classifiers
            keywords = []
            if info.get("keywords"):
                keywords = [k.strip() for k in info["keywords"].split(",")]

            classifiers = info.get("classifiers") or []

            metadata = PackageMetadata(
                name=info.get("name", package_name),
                version=info.get("version", version),
                summary=info.get("summary", ""),
                description=info.get("description", ""),
                runtime_requires=runtime_requires,
                keywords=keywords,
                classifiers=classifiers,
            )

            self._metadata_cache[cache_key] = metadata
            return metadata

        except Exception as e:
            raise NetworkError(
                f"Failed to fetch metadata for {package_name}: {e}"
            ) from e

    def _calculate_dependency_relevance(
        self, dep: DependencySpec, primary_package: str
    ) -> float:
        """Calculate relevance score for a dependency."""
        score = 0.0
        dep_name = dep.name.lower()
        primary_name = primary_package.lower()

        # Core framework dependencies get high priority
        if dep_name in CORE_FRAMEWORKS:
            score += 10.0

        # Common utility libraries get medium priority
        if dep_name in COMMON_UTILITIES:
            score += 5.0

        # Package-specific relationship boosts
        if primary_name in PACKAGE_RELATIONSHIP_BOOSTS:
            boost = PACKAGE_RELATIONSHIP_BOOSTS[primary_name].get(dep_name, 0.0)
            score += boost

        # Well-documented packages get a small boost
        if dep_name in WELL_DOCUMENTED:
            score += 2.0

        # Penalty for low-priority/build dependencies
        if dep_name in LOW_PRIORITY_DEPS:
            score -= 5.0

        # Penalty for very version-constrained dependencies (likely internal/unstable)
        if dep.version_constraint and any(
            op in dep.version_constraint for op in ["==", "~="]
        ):
            score -= 1.0

        # Small boost for packages with similar names (likely related)
        if primary_name in dep_name or dep_name in primary_name:
            score += 1.0

        return max(0.0, score)  # Don't allow negative scores

    async def _estimate_dependency_tokens(self, dep_name: str) -> int:
        """Estimate token count for dependency documentation."""
        # Conservative estimates based on typical documentation sizes

        # Core frameworks tend to have more detailed docs
        if dep_name.lower() in CORE_FRAMEWORKS:
            return 2500

        # Common utilities have moderate documentation
        if dep_name.lower() in COMMON_UTILITIES:
            return 1500

        # Well-documented packages
        if dep_name.lower() in WELL_DOCUMENTED:
            return 2000

        # Default conservative estimate
        return 1000

    async def get_dependency_metadata(
        self, package_name: str, version: str
    ) -> PackageMetadata | None:
        """Get cached or fetch package metadata."""
        try:
            return await self._get_package_metadata(package_name, version)
        except Exception as e:
            logger.warning(
                "Failed to get dependency metadata", package=package_name, error=str(e)
            )
            return None


async def create_dependency_resolver() -> DependencyResolver:
    """Create a dependency resolver with network client."""
    network_client = NetworkResilientClient()
    await network_client.__aenter__()
    return DependencyResolver(network_client)
