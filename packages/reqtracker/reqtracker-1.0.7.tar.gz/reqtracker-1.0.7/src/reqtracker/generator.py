"""Requirements.txt generation engine.

This module provides functionality to generate clean, well-formatted
requirements.txt files from tracked dependencies.
"""

import subprocess
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Set, Union


class VersionStrategy(Enum):
    """Version pinning strategies for requirements generation."""

    EXACT = "exact"  # ==1.2.3
    COMPATIBLE = "compatible"  # ~=1.2.3
    MINIMUM = "minimum"  # >=1.2.3
    NONE = "none"  # package-name (no version)


class RequirementsGenerator:
    """Generator for requirements.txt files from tracked dependencies."""

    def __init__(self, version_strategy: VersionStrategy = VersionStrategy.COMPATIBLE):
        """Initialize the requirements generator.

        Args:
            version_strategy: Strategy for version pinning.
        """
        self.version_strategy = version_strategy
        self._package_versions: Dict[str, str] = {}

    def generate(
        self,
        packages: Set[str],
        output_file: Union[str, Path] = "requirements.txt",
        include_header: bool = True,
        sort_packages: bool = True,
    ) -> str:
        """Generate requirements.txt content from package names.

        Args:
            packages: Set of package names to include.
            output_file: Output file path (for header generation).
            include_header: Whether to include generation header.
            sort_packages: Whether to sort packages alphabetically.

        Returns:
            Generated requirements.txt content as string.
        """
        if not packages:
            return self._generate_empty_requirements(include_header)

        # Get current versions for packages
        self._fetch_package_versions(packages)

        # Generate requirement lines
        requirement_lines = []
        for package in sorted(packages) if sort_packages else packages:
            req_line = self._format_requirement(package)
            if req_line:  # Skip if we couldn't format the requirement
                requirement_lines.append(req_line)

        # Build complete content
        content_parts = []

        if include_header:
            content_parts.append(self._generate_header(output_file, len(packages)))

        content_parts.extend(requirement_lines)

        return "\n".join(content_parts) + "\n"

    def write_requirements(
        self,
        packages: Set[str],
        output_file: Union[str, Path] = "requirements.txt",
        include_header: bool = True,
        sort_packages: bool = True,
    ) -> None:
        """Write requirements.txt file to disk.

        Args:
            packages: Set of package names to include.
            output_file: Output file path.
            include_header: Whether to include generation header.
            sort_packages: Whether to sort packages alphabetically.
        """
        content = self.generate(packages, output_file, include_header, sort_packages)

        output_path = Path(output_file)
        output_path.write_text(content, encoding="utf-8")

    def _fetch_package_versions(self, packages: Set[str]) -> None:
        """Fetch current versions of installed packages.

        Args:
            packages: Set of package names to get versions for.
        """
        self._package_versions.clear()

        if self.version_strategy == VersionStrategy.NONE:
            return  # No versions needed

        try:
            # Use pip show to get package versions
            for package in packages:
                version = self._get_package_version(package)
                if version:
                    self._package_versions[package] = version
        except Exception:
            # If it can't get versions, falls back to no versions
            pass

    def _get_package_version(self, package_name: str) -> Optional[str]:
        """Get version of a specific package.

        Args:
            package_name: Name of the package.

        Returns:
            Version string or None if not found.
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

        return None

    def _format_requirement(self, package_name: str) -> Optional[str]:
        """Format a single requirement line.

        Args:
            package_name: Name of the package.

        Returns:
            Formatted requirement string or None if invalid.
        """
        if not package_name or not package_name.strip():
            return None

        package_name = package_name.strip()

        if self.version_strategy == VersionStrategy.NONE:
            return package_name

        version = self._package_versions.get(package_name)
        if not version:
            return package_name  # No version available

        if self.version_strategy == VersionStrategy.EXACT:
            return f"{package_name}=={version}"
        elif self.version_strategy == VersionStrategy.COMPATIBLE:
            return f"{package_name}~={version}"
        elif self.version_strategy == VersionStrategy.MINIMUM:
            return f"{package_name}>={version}"
        else:
            return package_name

    def _generate_header(
        self, output_file: Union[str, Path], package_count: int
    ) -> str:
        """Generate header comment for requirements file.

        Args:
            output_file: Output file path.
            package_count: Number of packages in requirements.

        Returns:
            Header comment string.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        strategy_desc = {
            VersionStrategy.EXACT: "exact versions (==)",
            VersionStrategy.COMPATIBLE: "compatible versions (~=)",
            VersionStrategy.MINIMUM: "minimum versions (>=)",
            VersionStrategy.NONE: "no version constraints",
        }

        return f"""# Requirements generated by reqtracker
# Generated on: {timestamp}
# Strategy: {strategy_desc[self.version_strategy]}
# Packages: {package_count}
#
# This file was automatically generated from your project's imports.
# To regenerate: reqtracker generate
"""

    def _generate_empty_requirements(self, include_header: bool) -> str:
        """Generate content for empty requirements file.

        Args:
            include_header: Whether to include header.

        Returns:
            Empty requirements content.
        """
        if include_header:
            return (
                self._generate_header("requirements.txt", 0)
                + "\n# No dependencies found\n"
            )
        else:
            return "# No dependencies found\n"


def generate_requirements(
    packages: Set[str],
    output_file: Union[str, Path] = "requirements.txt",
    version_strategy: str = "compatible",
    include_header: bool = True,
    sort_packages: bool = True,
) -> str:
    """Generate requirements.txt content from package names.

    Args:
        packages: Set of package names to include.
        output_file: Output file path.
        version_strategy: Version pinning strategy ('exact', 'compatible', 'minimum',
            'none').
        include_header: Whether to include generation header.
        sort_packages: Whether to sort packages alphabetically.

    Returns:
        Generated requirements.txt content.
    """
    strategy = VersionStrategy(version_strategy)
    generator = RequirementsGenerator(strategy)
    return generator.generate(packages, output_file, include_header, sort_packages)


def write_requirements(
    packages: Set[str],
    output_file: Union[str, Path] = "requirements.txt",
    version_strategy: str = "compatible",
    include_header: bool = True,
    sort_packages: bool = True,
) -> None:
    """Write requirements.txt file to disk.

    Args:
        packages: Set of package names to include.
        output_file: Output file path.
        version_strategy: Version pinning strategy ('exact', 'compatible', 'minimum',
            'none').
        include_header: Whether to include generation header.
        sort_packages: Whether to sort packages alphabetically.
    """
    strategy = VersionStrategy(version_strategy)
    generator = RequirementsGenerator(strategy)
    generator.write_requirements(packages, output_file, include_header, sort_packages)
