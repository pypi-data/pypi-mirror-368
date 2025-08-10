"""Context documentation formatter for AI-optimized output."""

import re
from typing import Any

from pydantic import BaseModel, Field
from structlog import get_logger

logger = get_logger(__name__)


class PackageDocumentation(BaseModel):
    """Documentation for a single package optimized for AI context."""

    name: str
    version: str
    relationship: str  # "primary", "runtime_dependency", "dev_dependency"

    # Core documentation sections
    summary: str | None = None
    key_features: list[str] = Field(default_factory=list)
    main_classes: list[str] = Field(default_factory=list)
    main_functions: list[str] = Field(default_factory=list)
    usage_examples: str | None = None

    # Context metadata
    why_included: str = ""  # "Requested package", "Required by fastapi", etc.
    dependency_level: int = 0  # 0=primary, 1=direct dep, 2=transitive

    @property
    def token_estimate(self) -> int:
        """Rough token count estimate for this documentation."""
        content_parts = [
            self.summary or "",
            " ".join(self.key_features),
            " ".join(self.main_classes),
            " ".join(self.main_functions),
            self.usage_examples or "",
        ]

        total_content = " ".join(content_parts)
        # Rough estimate: 1.3 tokens per word
        return int(len(total_content.split()) * 1.3)


class DocumentationContext(BaseModel):
    """Complete documentation context for AI consumption."""

    # Primary package (the one explicitly requested)
    primary_package: PackageDocumentation

    # Direct dependencies (runtime dependencies)
    runtime_dependencies: list[PackageDocumentation] = Field(default_factory=list)

    # Development dependencies (if relevant)
    dev_dependencies: list[PackageDocumentation] = Field(default_factory=list)

    # Context metadata
    context_scope: str = "primary_only"  # "primary_only", "with_runtime", "with_dev"
    total_packages: int = 1
    truncated_packages: list[str] = Field(
        default_factory=list
    )  # Packages skipped due to limits

    @property
    def token_estimate(self) -> int:
        """Total token count estimate for complete context."""
        return sum(doc.token_estimate for doc in self.all_packages)

    @property
    def all_packages(self) -> list[PackageDocumentation]:
        """All packages in context."""
        return (
            [self.primary_package] + self.runtime_dependencies + self.dev_dependencies
        )


class ContextDocumentationFormatter:
    """Formats package information into AI-optimized documentation context."""

    def __init__(self) -> None:
        self.max_summary_length = 300
        self.max_examples_length = 800
        self.max_features_count = 8
        self.max_classes_count = 10
        self.max_functions_count = 10

    def format_primary_package(
        self, package_info: dict[str, Any], from_cache: bool = False
    ) -> PackageDocumentation:
        """Format primary package documentation with full detail."""

        return PackageDocumentation(
            name=package_info.get("name", ""),
            version=package_info.get("version", ""),
            relationship="primary",
            summary=self._clean_summary(package_info.get("summary", "")),
            key_features=self._extract_key_features(
                package_info.get("description", ""),
                max_features=self.max_features_count,
            ),
            main_classes=self._extract_main_classes(
                package_info.get("description", ""), max_classes=self.max_classes_count
            ),
            main_functions=self._extract_main_functions(
                package_info.get("description", ""),
                max_functions=self.max_functions_count,
            ),
            usage_examples=self._extract_concise_examples(
                package_info.get("description", ""), max_length=self.max_examples_length
            ),
            why_included="Requested package",
            dependency_level=0,
        )

    def format_dependency_package(
        self,
        package_info: dict[str, Any],
        primary_package_name: str,
        dependency_level: int = 1,
    ) -> PackageDocumentation:
        """Format dependency package documentation with concise detail."""

        # For dependencies, use more conservative limits to save tokens
        return PackageDocumentation(
            name=package_info.get("name", ""),
            version=package_info.get("version", ""),
            relationship="runtime_dependency",
            summary=self._clean_summary(
                package_info.get("summary", ""),
                max_length=200,  # Shorter for dependencies
            ),
            key_features=self._extract_key_features(
                package_info.get("description", ""),
                max_features=5,  # Fewer features for dependencies
            ),
            main_classes=self._extract_main_classes(
                package_info.get("description", ""),
                max_classes=6,  # Fewer classes for dependencies
            ),
            main_functions=self._extract_main_functions(
                package_info.get("description", ""),
                max_functions=6,  # Fewer functions for dependencies
            ),
            usage_examples=self._extract_concise_examples(
                package_info.get("description", ""),
                max_length=400,  # Shorter examples for dependencies
            ),
            why_included=f"Required by {primary_package_name}",
            dependency_level=dependency_level,
        )

    def _clean_summary(self, summary: str, max_length: int | None = None) -> str:
        """Clean and truncate package summary."""
        if not summary:
            return ""

        # Clean up common summary issues
        summary = summary.strip()
        summary = re.sub(r"\s+", " ", summary)  # Normalize whitespace

        # Remove common prefixes
        prefixes_to_remove = [
            "A Python library for ",
            "Python library for ",
            "A library for ",
            "Library for ",
            "A Python package for ",
            "Python package for ",
            "A package for ",
            "Package for ",
        ]

        for prefix in prefixes_to_remove:
            if summary.startswith(prefix):
                summary = summary[len(prefix) :]
                break

        # Capitalize first letter
        if summary:
            summary = summary[0].upper() + summary[1:]

        # Truncate if needed
        max_len = max_length or self.max_summary_length
        if len(summary) > max_len:
            summary = summary[:max_len].rsplit(" ", 1)[0] + "..."

        return summary

    def _extract_key_features(
        self, description: str, max_features: int = 8
    ) -> list[str]:
        """Extract key features from package description."""
        if not description:
            return []

        features = []

        # Look for bullet points or numbered lists
        bullet_patterns = [
            r"[•*\-]\s*([^•*\-\n]+)",  # Bullet points (escape the hyphen)
            r"\d+\.\s*([^\n]+)",  # Numbered lists
        ]

        for pattern in bullet_patterns:
            matches = re.findall(pattern, description, re.MULTILINE)
            for match in matches:
                feature = match.strip().rstrip(".")
                if 10 < len(feature) < 100:  # Reasonable length
                    features.append(feature)

        # Look for common feature indicators
        feature_indicators = [
            r"supports?\s+([^.]{10,80})",
            r"provides?\s+([^.]{10,80})",
            r"includes?\s+([^.]{10,80})",
            r"features?\s+([^.]{10,80})",
        ]

        for pattern in feature_indicators:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                feature = match.strip().rstrip(".")
                if feature not in features and len(feature) > 10:
                    features.append(feature)

        # Deduplicate and limit
        unique_features = []
        for feature in features:
            if feature not in unique_features:
                unique_features.append(feature)

        return unique_features[:max_features]

    def _extract_main_classes(
        self, description: str, max_classes: int = 10
    ) -> list[str]:
        """Extract main class names from description."""
        if not description:
            return []

        # Look for class patterns
        class_patterns = [
            r"class\s+([A-Z][a-zA-Z0-9_]+)",  # Python class definitions
            r"`([A-Z][a-zA-Z0-9_]+)`",  # Backtick-quoted class names
            r"``([A-Z][a-zA-Z0-9_]+)``",  # Double backtick-quoted
            r"([A-Z][a-zA-Z0-9_]+)\s+class",  # "SomeClass class"
        ]

        classes = set()
        for pattern in class_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                # Filter out common non-class words
                if match not in {
                    "HTTP",
                    "API",
                    "URL",
                    "JSON",
                    "XML",
                    "HTML",
                    "CSS",
                    "SQL",
                }:
                    classes.add(match)

        return sorted(classes)[:max_classes]

    def _extract_main_functions(
        self, description: str, max_functions: int = 10
    ) -> list[str]:
        """Extract main function names from description."""
        if not description:
            return []

        # Look for function patterns
        function_patterns = [
            r"def\s+([a-z_][a-zA-Z0-9_]*)",  # Python function definitions
            r"`([a-z_][a-zA-Z0-9_]*)\(",  # Backtick-quoted function calls
            r"``([a-z_][a-zA-Z0-9_]*)\(``",  # Double backtick-quoted
            r"\.([a-z_][a-zA-Z0-9_]*)\(",  # Method calls
        ]

        functions = set()
        for pattern in function_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                # Filter out common non-function words and very short names
                if len(match) > 2 and match not in {
                    "get",
                    "set",
                    "run",
                    "new",
                    "add",
                    "del",
                }:
                    functions.add(match)

        return sorted(functions)[:max_functions]

    def _extract_concise_examples(
        self, description: str, max_length: int = 800
    ) -> str | None:
        """Extract concise usage examples from description."""
        if not description:
            return None

        # Look for code blocks
        code_patterns = [
            r"```python\n(.*?)\n```",  # Python code blocks
            r"```\n(.*?)\n```",  # Generic code blocks
            r":::\n\n(.*?)\n\n",  # RST code blocks
        ]

        examples = []
        for pattern in code_patterns:
            matches = re.findall(pattern, description, re.DOTALL)
            for match in matches:
                code = match.strip()
                if 20 < len(code) < 500:  # Reasonable length
                    examples.append(code)

        if not examples:
            # Look for inline code examples
            inline_patterns = [
                r"`([^`]{20,200})`",  # Inline code
                r">>> ([^>\n]{10,100})",  # Python REPL examples
            ]

            for pattern in inline_patterns:
                matches = re.findall(pattern, description)
                for match in matches:
                    if "import" in match or "(" in match:  # Looks like code
                        examples.append(match.strip())

        if examples:
            # Take the best example (longest, up to limit)
            best_example = max(examples, key=len)
            if len(best_example) > max_length:
                best_example = best_example[:max_length] + "..."
            return str(best_example)

        return None


class ContextWindowManager:
    """Manage AI context window efficiently."""

    @staticmethod
    def fit_to_window(
        context: DocumentationContext, max_tokens: int = 30000
    ) -> DocumentationContext:
        """Trim context to fit within token limits."""

        if context.token_estimate <= max_tokens:
            return context

        logger.info(
            "Trimming context to fit token window",
            current_tokens=context.token_estimate,
            max_tokens=max_tokens,
        )

        # Start by truncating dependency documentation
        truncated_deps = []
        remaining_tokens = max_tokens - context.primary_package.token_estimate

        # Sort dependencies by relevance (assume they're already sorted)
        for dep in context.runtime_dependencies:
            if remaining_tokens >= dep.token_estimate:
                truncated_deps.append(dep)
                remaining_tokens -= dep.token_estimate
            else:
                context.truncated_packages.append(dep.name)
                logger.debug(
                    "Truncated dependency due to token limit",
                    package=dep.name,
                    tokens=dep.token_estimate,
                )

        context.runtime_dependencies = truncated_deps

        # Update context scope if we had to truncate
        if context.truncated_packages:
            original_scope = context.context_scope
            truncated_count = len(context.truncated_packages)
            context.context_scope = (
                f"{original_scope} (truncated {truncated_count} deps)"
            )

        logger.info(
            "Context trimmed successfully",
            final_tokens=context.token_estimate,
            kept_deps=len(truncated_deps),
            truncated_deps=len(context.truncated_packages),
        )

        return context


def create_context_formatter() -> ContextDocumentationFormatter:
    """Create a context documentation formatter."""
    return ContextDocumentationFormatter()
