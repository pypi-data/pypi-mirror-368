"""Version resolution for converting constraints to specific versions."""

from packaging.specifiers import SpecifierSet
from structlog import get_logger

from ..config import get_config
from ..exceptions import NetworkError, PackageNotFoundError
from .network_resilience import NetworkResilientClient

logger = get_logger(__name__)


class VersionResolver:
    """Resolve version constraints to specific versions."""

    @staticmethod
    async def resolve_version(package_name: str, constraint: str | None = None) -> str:
        """
        Resolve version constraint to specific version with network resilience.

        Args:
            package_name: Package to resolve
            constraint: Version constraint like ">=2.0.0" or None for latest

        Returns:
            Specific version string like "2.28.2"
        """
        config = get_config()

        async with NetworkResilientClient() as client:
            try:
                response = await client.get_with_retry(
                    f"{config.pypi_base_url}/{package_name}/json",
                    headers={"Accept": "application/json"},
                )
                data = response.json()
            except PackageNotFoundError:
                logger.error("Package not found", package=package_name)
                raise
            except NetworkError as e:
                logger.error(
                    "Failed to resolve version", package=package_name, error=str(e)
                )
                raise

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
