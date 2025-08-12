"""reqtracker - Intelligent Python dependency tracking and requirements generation.

This package provides automatic dependency detection and requirements.txt generation
for Python projects using static analysis, dynamic tracking, or hybrid approaches.

Basic Usage:
    import reqtracker

    # Simple dependency tracking
    packages = reqtracker.track()

    # Generate requirements.txt
    reqtracker.generate()

    # Complete workflow
    reqtracker.analyze()

Advanced Usage:
    # Custom paths and modes
    packages = reqtracker.track(['./src', './app'], mode='hybrid')

    # Custom configuration
    config = reqtracker.Config(mode='static')
    packages = reqtracker.track(config=config)

    # Custom requirements generation
    reqtracker.generate(packages, output='deps.txt', version_strategy='exact')
"""

__version__ = "1.0.7"
__author__ = "Oleksii Shcherbak"
__email__ = "oleksii_shcherbak@icloud.com"

from pathlib import Path
from typing import List, Optional, Set, Union

# Import core classes for advanced usage
from .config import Config, OutputConfig, TrackerMode
from .dynamic_tracker import DynamicTracker
from .generator import RequirementsGenerator, VersionStrategy

# Import mapping utilities
from .mappings import resolve_package_name
from .static_analyzer import StaticAnalyzer
from .tracker import Tracker, TrackingMode
from .utils import get_package_name, is_standard_library, normalize_package_name

__all__ = [
    # Main API functions
    "track",
    "generate",
    "analyze",
    "scan",
    "write_requirements",
    # Core classes
    "Config",
    "OutputConfig",
    "TrackerMode",
    "Tracker",
    "TrackingMode",
    "RequirementsGenerator",
    "VersionStrategy",
    "StaticAnalyzer",
    "DynamicTracker",
    # Utility functions
    "resolve_package_name",
    "get_package_name",
    "is_standard_library",
    "normalize_package_name",
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
]


def track(
    source_paths: Optional[List[Union[str, Path]]] = None,
    mode: Optional[str] = None,
    config: Optional[Config] = None,
) -> Set[str]:
    """Track dependencies in source files.

    This is the main entry point for dependency tracking. Analyzes source files
    to detect imported packages using static analysis, dynamic tracking, or both.

    Args:
        source_paths: List of paths to analyze. If None, analyzes current directory.
        mode: Analysis mode - .static., .dynamic., or .hybrid..
            If None, uses config.mode.
        config: Configuration object. If None, uses default configuration.

    Returns:
        Set of package names found in the analyzed code.

    Examples:
        # Simple usage - analyze current directory
        packages = reqtracker.track()

        # Analyze specific paths
        packages = reqtracker.track(['./src', './tests'])

        # Use static analysis only
        packages = reqtracker.track(mode='static')

        # Use custom configuration
        config = reqtracker.Config(exclude_patterns=['test_*'])
        packages = reqtracker.track(config=config)
    """
    import os

    # Use provided config or create default
    if config is None:
        config = Config()

    # Determine the mode to use: explicit parameter takes precedence over config
    if mode is not None:
        mode_to_use = mode
    else:
        # Use mode from config, converting TrackerMode enum to string
        if hasattr(config.mode, "value"):
            mode_to_use = config.mode.value
        else:
            mode_to_use = str(config.mode).lower()

    # Check if it is in dynamic analysis mode to prevent infinite recursion
    if mode_to_use in ("dynamic", "hybrid") and os.environ.get("REQTRACKER_ANALYZING"):
        # Return empty set to break the recursion
        return set()

    # Convert mode string to enum
    try:
        tracking_mode = TrackingMode(mode_to_use)
    except ValueError:
        raise ValueError(
            f"Invalid mode '{mode_to_use}'. Must be 'static', 'dynamic', or 'hybrid'"
        )

    # Create tracker and analyze
    tracker = Tracker(config)
    return tracker.track(source_paths, tracking_mode)


def generate(
    packages: Optional[Set[str]] = None,
    output: Union[str, Path] = "requirements.txt",
    version_strategy: str = "compatible",
    include_header: bool = True,
    sort_packages: bool = True,
    config: Optional[Config] = None,
) -> str:
    """Generate requirements.txt content from packages.

    Creates a properly formatted requirements.txt file from a set of package names.
    If no packages provided, automatically tracks dependencies in current directory.

    Args:
        packages: Set of package names. If None, auto-detects from current directory.
        output: Output file path (default: requirements.txt).
        version_strategy: Version pinning strategy - 'exact', 'compatible',
            'minimum', or 'none'.
        include_header: Whether to include generation header in output.
        sort_packages: Whether to sort packages alphabetically.
        config: Configuration object for dependency tracking (if packages is None).

    Returns:
        Generated requirements.txt content as string.

    Examples:
        # Generate from current directory
        content = reqtracker.generate()

        # Generate from specific packages
        packages = {'requests', 'numpy'}
        content = reqtracker.generate(packages)

        # Generate with exact versions
        content = reqtracker.generate(version_strategy='exact')

        # Generate to custom file
        content = reqtracker.generate(output='deps.txt')
    """
    # Auto-detect packages if not provided
    if packages is None:
        packages = track(config=config)

    # Convert version strategy string to enum
    try:
        strategy = VersionStrategy(version_strategy)
    except ValueError:
        raise ValueError(
            f"Invalid version_strategy '{version_strategy}'. "
            f"Must be 'exact', 'compatible', 'minimum', or 'none'"
        )

    # Generate requirements
    generator = RequirementsGenerator(strategy)
    content = generator.generate(packages, output, include_header, sort_packages)

    # Write to file
    Path(output).write_text(content, encoding="utf-8")

    return content


def analyze(
    source_paths: Optional[List[Union[str, Path]]] = None,
    output: Union[str, Path] = "requirements.txt",
    mode: str = "hybrid",
    version_strategy: str = "compatible",
    include_header: bool = True,
    sort_packages: bool = True,
    config: Optional[Config] = None,
) -> Set[str]:
    """Complete workflow: track dependencies and generate requirements.txt.

    Combines dependency tracking and requirements generation in a single call.
    This is the most convenient function for complete dependency management.

    Args:
        source_paths: List of paths to analyze. If None, analyzes current directory.
        output: Output file path for requirements.txt.
        mode: Analysis mode - .static., .dynamic., or .hybrid..
            If None, uses config.mode.
        version_strategy: Version pinning strategy.
        include_header: Whether to include generation header.
        sort_packages: Whether to sort packages alphabetically.
        config: Configuration object. If None, uses default configuration.

    Returns:
        Set of package names that were found and included in requirements.txt.

    Examples:
        # Complete workflow with defaults
        packages = reqtracker.analyze()

        # Analyze specific paths with custom output
        packages = reqtracker.analyze(['./src'], output='deps.txt')

        # Use exact versioning
        packages = reqtracker.analyze(version_strategy='exact')

        # Custom configuration
        config = reqtracker.Config(mode='static')
        packages = reqtracker.analyze(config=config)
    """
    # Track dependencies
    packages = track(source_paths, mode, config)

    # Generate requirements
    generate(packages, output, version_strategy, include_header, sort_packages)

    return packages


# Convenience function aliases for common usage patterns
def scan(source_paths: Optional[List[Union[str, Path]]] = None, **kwargs) -> Set[str]:
    """Alias for track() - scan for dependencies."""
    return track(source_paths, **kwargs)


def write_requirements(
    packages: Optional[Set[str]] = None,
    output: Union[str, Path] = "requirements.txt",
    **kwargs,
) -> None:
    """Generate and write requirements.txt file (no return value)."""
    generate(packages, output, **kwargs)


# Make the package easily importable
def __getattr__(name: str):
    """Support for dynamic imports of submodules."""
    if name in __all__:
        return globals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
