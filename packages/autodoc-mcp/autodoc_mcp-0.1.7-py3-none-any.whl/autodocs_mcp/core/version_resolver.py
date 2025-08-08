"""Version resolution for converting constraints to specific versions."""

import httpx
from packaging.specifiers import SpecifierSet
from structlog import get_logger

from ..config import get_config
from ..exceptions import NetworkError, PackageNotFoundError

logger = get_logger(__name__)


class VersionResolver:
    """Resolve version constraints to specific versions."""

    @staticmethod
    async def resolve_version(package_name: str, constraint: str | None = None) -> str:
        """
        Resolve version constraint to specific version.

        Args:
            package_name: Package to resolve
            constraint: Version constraint like ">=2.0.0" or None for latest

        Returns:
            Specific version string like "2.28.2"
        """
        config = get_config()

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(config.request_timeout)
        ) as client:
            try:
                response = await client.get(
                    f"{config.pypi_base_url}/{package_name}/json"
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise PackageNotFoundError(
                        f"Package '{package_name}' not found on PyPI"
                    ) from e
                raise NetworkError(f"PyPI API error: {e.response.status_code}") from e
            except httpx.RequestError as e:
                raise NetworkError(
                    f"Network error resolving {package_name}: {e}"
                ) from e

        latest_version: str = data["info"]["version"]

        if constraint is None:
            logger.info(
                "Resolved version without constraint",
                package=package_name,
                resolved_version=latest_version,
            )
            return latest_version

        # Parse and validate constraint
        try:
            specifier = SpecifierSet(constraint)
            if latest_version in specifier:
                logger.info(
                    "Resolved version with constraint",
                    package=package_name,
                    constraint=constraint,
                    resolved_version=latest_version,
                )
                return latest_version
            else:
                # For MVP, raise error if latest doesn't match
                # Future: implement full version resolution from all releases
                msg = f"Latest version {latest_version} doesn't satisfy constraint {constraint}"
                raise ValueError(msg)
        except Exception as e:
            logger.warning(
                "Version constraint parsing failed",
                package=package_name,
                constraint=constraint,
                error=str(e),
            )
            return latest_version  # Fallback to latest

    @staticmethod
    def generate_cache_key(package_name: str, version: str) -> str:
        """Generate cache key for specific version."""
        return f"{package_name}-{version}"
