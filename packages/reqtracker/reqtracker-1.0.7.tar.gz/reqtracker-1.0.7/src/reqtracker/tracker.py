"""Main tracker coordination for reqtracker.

This module provides the primary interface for dependency tracking,
coordinating between static and dynamic analysis modes.
"""

from enum import Enum
from pathlib import Path
from typing import List, Optional, Set, Union

from .config import Config
from .dynamic_tracker import DynamicTracker, TrackingSession
from .mappings import resolve_package_name
from .static_analyzer import StaticAnalyzer


class TrackingMode(Enum):
    """Available tracking modes."""

    STATIC = "static"
    DYNAMIC = "dynamic"
    HYBRID = "hybrid"


class Tracker:
    """Main dependency tracker coordinating static and dynamic analysis."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the tracker.

        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self.static_analyzer = StaticAnalyzer()
        self.dynamic_tracker = DynamicTracker()

    def track(
        self,
        source_paths: Optional[List[Union[str, Path]]] = None,
        mode: TrackingMode = TrackingMode.HYBRID,
    ) -> Set[str]:
        """Track dependencies in the specified paths.

        Args:
            source_paths: List of paths to analyze. If None, uses current directory.
            mode: Tracking mode to use.

        Returns:
            Set of package names found.
        """
        if source_paths is None:
            source_paths = [Path.cwd()]

        # Convert to Path objects
        paths = [Path(p) for p in source_paths]

        # Configure analyzers
        self._configure_analyzers(paths)

        # Run analysis based on mode
        if mode == TrackingMode.STATIC:
            return self._run_static_analysis(paths)
        elif mode == TrackingMode.DYNAMIC:
            return self._run_dynamic_analysis(paths)
        else:  # HYBRID
            return self._run_hybrid_analysis(paths)

    def _configure_analyzers(self, paths: List[Path]) -> None:
        """Configure analyzers with current settings."""
        # Configure static analyzer
        if paths:
            self.static_analyzer.configure(
                project_root=paths[0].parent if paths[0].is_file() else paths[0],
                include_patterns=self.config.include_patterns,
                exclude_patterns=self.config.exclude_patterns,
            )

    def _get_python_files(self, paths: List[Path]) -> List[Path]:  # noqa
        """Get all Python files from the given paths.

        Args:
            paths: List of file or directory paths.

        Returns:
            List of Python file paths.
        """
        python_files = []

        for path in paths:
            if path.is_file() and path.suffix == ".py":
                python_files.append(path)
            elif path.is_dir():
                # Find all Python files in directory recursively
                for py_file in path.rglob("*.py"):
                    # Apply basic filtering (could be enhanced with config patterns)
                    if not any(part.startswith(".") for part in py_file.parts):
                        python_files.append(py_file)

        return python_files

    def _run_static_analysis(self, paths: List[Path]) -> Set[str]:
        """Run static analysis only."""
        all_imports = set()

        for path in paths:
            if path.is_file():
                # Single file analysis
                imports = self.static_analyzer.analyze_file(path)
                # Extract just the module names
                module_names = {
                    imp.get("module", "").split(".")[0]
                    for imp in imports
                    if imp.get("module")
                }
                all_imports.update(module_names)
            else:
                # Directory analysis
                self.static_analyzer.project_root = path
                imports = self.static_analyzer.analyze()
                # Extract module names
                module_names = {
                    imp.get("module", "").split(".")[0]
                    for imp in imports
                    if imp.get("module")
                }
                all_imports.update(module_names)

        # noinspection PyUnreachableCode
        # Resolve package names
        return self._resolve_package_names(all_imports, paths)

    def _run_dynamic_analysis(self, paths: List[Path]) -> Set[str]:
        """Run dynamic analysis only."""
        import os

        # Check if we are already in a dynamic analysis session
        # to prevent infinite recursion
        if os.environ.get("REQTRACKER_ANALYZING"):
            # We are already analyzing, skip to prevent infinite loop
            return set()

        all_imports = set()

        # Get all Python files from paths (handles both files and directories)
        python_files = self._get_python_files(paths)

        # Set environment variable to indicate we are analyzing
        os.environ["REQTRACKER_ANALYZING"] = "1"

        try:
            # Create a tracking session and use it properly
            session = TrackingSession()
            for py_file in python_files:
                try:
                    # Skip the current file if it is the one being executed
                    import __main__

                    if (
                        hasattr(__main__, "__file__")
                        and Path(__main__.__file__).resolve() == py_file.resolve()
                    ):
                        continue

                    imports = session.track_file(py_file)
                    all_imports.update(imports)
                except Exception:  # noqa: BLE001
                    # Silently skip files that cannot be executed
                    pass
        finally:
            # Always clean up the environment variable
            os.environ.pop("REQTRACKER_ANALYZING", None)

        # noinspection PyUnreachableCode
        # Resolve package names
        return self._resolve_package_names(all_imports, paths)

    def _run_hybrid_analysis(self, paths: List[Path]) -> Set[str]:
        """Run both static and dynamic analysis, merging results."""
        static_imports = self._run_static_analysis(paths)
        dynamic_imports = self._run_dynamic_analysis(paths)

        # Merge results
        return static_imports.union(dynamic_imports)

    def _resolve_package_names(
        self, import_names: Set[str], source_paths: List[Path] = None
    ) -> Set[str]:  # noqa
        """Resolve import names to PyPI package names."""
        resolved = set()

        # Use provided source paths or current directory
        if source_paths is None:
            source_paths = [Path.cwd()]

        for import_name in import_names:
            if import_name:  # Skip empty strings
                # Skip local modules
                from .utils import is_local_module

                if is_local_module(import_name, source_paths):
                    continue

                package_name = resolve_package_name(import_name)
                if package_name:  # Skip None results (stdlib modules)
                    resolved.add(package_name)

        return resolved


def track(
    source_paths: Optional[List[Union[str, Path]]] = None,
    mode: str = "hybrid",
    config: Optional[Config] = None,
) -> Set[str]:
    """Simple interface for dependency tracking.

    Args:
        source_paths: List of paths to analyze. If None, uses current directory.
        mode: Tracking mode ('static', 'dynamic', or 'hybrid').
        config: Configuration object. If None, uses default config.

    Returns:
        Set of package names found.
    """
    tracker = Tracker(config)
    tracking_mode = TrackingMode(mode)
    return tracker.track(source_paths, tracking_mode)
