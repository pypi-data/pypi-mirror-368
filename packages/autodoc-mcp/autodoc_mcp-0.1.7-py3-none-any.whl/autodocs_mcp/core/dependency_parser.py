"""Dependency parsing implementation for pyproject.toml files."""

import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

import tomlkit
from structlog import get_logger
from tomlkit.exceptions import TOMLKitError

from ..exceptions import ProjectParsingError
from ..models import DependencySpec, ScanResult

logger = get_logger(__name__)


class DependencyParserInterface(ABC):
    """Interface for dependency parsing."""

    @abstractmethod
    async def parse_project(self, project_path: Path) -> ScanResult:
        """Parse project dependencies from configuration files."""

    @abstractmethod
    def validate_file(self, file_path: Path) -> bool:
        """Validate project configuration file."""


class PyProjectParser(DependencyParserInterface):
    """Parser for pyproject.toml files."""

    VERSION_PATTERN = re.compile(r"^([><=!~^]+)?([\d\w.-]+)$")

    async def parse_project(self, project_path: Path) -> ScanResult:
        """Parse pyproject.toml with graceful degradation."""
        pyproject_path = project_path / "pyproject.toml"

        if not pyproject_path.exists():
            raise ProjectParsingError(
                f"pyproject.toml not found in {project_path}", file_path=pyproject_path
            )

        dependencies = []
        failed_deps = []
        warnings = []
        errors: list[str] = []

        try:
            content = pyproject_path.read_text(encoding="utf-8")
            parsed = tomlkit.parse(content)
        except TOMLKitError as e:
            raise ProjectParsingError(
                f"Invalid TOML syntax: {e}", file_path=pyproject_path
            ) from e

        # Parse main dependencies with error handling
        project_section = parsed.get("project", {})
        project_name = project_section.get("name")

        if not project_section:
            warnings.append("No [project] section found in pyproject.toml")

        if "dependencies" in project_section:
            deps, failed = self._parse_dependency_list_safe(
                project_section["dependencies"], "project"
            )
            dependencies.extend(deps)
            failed_deps.extend(failed)

        # Parse optional dependencies with error handling (simplified for MVP)
        optional_deps = project_section.get("optional-dependencies", {})
        for group_name, dep_list in optional_deps.items():
            deps, failed = self._parse_dependency_list_safe(
                dep_list, f"optional-{group_name}"
            )
            dependencies.extend(deps)
            failed_deps.extend(failed)

        # Generate warnings for failed deps
        if failed_deps:
            warnings.extend(
                [
                    f"Skipped malformed dependency: {f['dependency_string']}"
                    for f in failed_deps
                ]
            )

        logger.info(
            "Parsed project dependencies",
            project_path=str(project_path),
            project_name=project_name,
            successful_deps=len(dependencies),
            failed_deps=len(failed_deps),
        )

        return ScanResult(
            project_path=project_path,
            dependencies=dependencies,
            project_name=project_name,
            successful_deps=len(dependencies),
            failed_deps=failed_deps,
            warnings=warnings,
            errors=errors,
            partial_success=len(failed_deps) > 0 or len(warnings) > 0,
            scan_timestamp=datetime.now(),
        )

    def validate_file(self, file_path: Path) -> bool:
        """Validate pyproject.toml structure."""
        try:
            if not file_path.exists():
                return False

            content = file_path.read_text(encoding="utf-8")
            parsed = tomlkit.parse(content)
            return "project" in parsed
        except (OSError, TOMLKitError):
            return False

    def _parse_dependency_list_safe(
        self, deps: list[str], source: str
    ) -> tuple[list[DependencySpec], list[dict[str, Any]]]:
        """Parse dependency list with error collection."""
        parsed_deps = []
        failed_deps = []

        for dep_str in deps:
            try:
                spec = self._parse_dependency_string(dep_str, source)
                parsed_deps.append(spec)
            except ValueError as e:
                failed_deps.append(
                    {"dependency_string": dep_str, "error": str(e), "source": source}
                )
                continue  # Keep processing other deps

        return parsed_deps, failed_deps

    def _parse_dependency_string(self, dep_str: str, source: str) -> DependencySpec:
        """Parse a single dependency string like 'requests>=2.0.0[security]'."""
        original_dep_str = dep_str
        dep_str = dep_str.strip()

        if not dep_str:
            raise ValueError("Empty dependency string")

        # Handle extras first
        extras = []
        if "[" in dep_str and "]" in dep_str:
            try:
                name_part, rest = dep_str.split("[", 1)
                if "]" not in rest:
                    raise ValueError(
                        f"Unclosed bracket in extras: '{original_dep_str}'"
                    )

                extra_part, version_part = rest.split("]", 1)
                extras = [e.strip() for e in extra_part.split(",") if e.strip()]

                # Reconstruct dep_str without extras
                dep_str = (name_part + version_part).strip()
            except ValueError as e:
                if "Unclosed bracket" in str(e):
                    raise e
                raise ValueError(f"Malformed extras in '{original_dep_str}'") from None

        # Handle version constraints
        version_constraint = None
        name = dep_str

        # Look for version operators
        for i, char in enumerate(dep_str):
            if char in ">=<!~":
                name = dep_str[:i].strip()
                version_constraint = dep_str[i:].strip()
                break

        if not name:
            raise ValueError(f"Invalid package name in '{original_dep_str}'")

        # Basic validation of package name
        if not re.match(r"^[A-Za-z0-9_.-]+$", name):
            raise ValueError(f"Invalid package name format: '{name}'")

        return DependencySpec(
            name=name,
            version_constraint=version_constraint,
            extras=extras,
            source=source,
        )
